"""Unit tests for fetch_tiktok_content and fetch_tiktok_profile (mocked HTTP)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.tt_oop import fetch_tiktok_content, fetch_tiktok_profile


def _feed_api_payload():
    """Minimal RapidAPI-style JSON for user/posts (two videos for APIDataToDataFrame)."""
    return {
        "msg": "success",
        "data": {
            "cursor": "next-cursor",
            "hasMore": False,
            "videos": [
                {
                    "video_id": "v1",
                    "title": "Hello #python @someone",
                    "create_time": 1609459200,
                    "duration": 12,
                    "digg_count": 100,
                    "share_count": 5,
                    "comment_count": 3,
                    "download_count": 1,
                    "collect_count": 7,
                    "play_count": 1000,
                    "is_ad": False,
                    "music_info": {"title": "Track A"},
                    "author": {
                        "id": "u1",
                        "nickname": "Nick1",
                        "unique_id": "creator1",
                    },
                    "cover": "https://example.com/c1.jpg",
                },
                {
                    "video_id": "v2",
                    "title": "Second clip",
                    "create_time": 1609545600,
                    "duration": 20,
                    "digg_count": 50,
                    "share_count": 2,
                    "comment_count": 1,
                    "download_count": 0,
                    "collect_count": 4,
                    "play_count": 500,
                    "is_ad": False,
                    "music_info": {"title": "Track B"},
                    "author": {
                        "id": "u1",
                        "nickname": "Nick1",
                        "unique_id": "creator1",
                    },
                    "cover": "https://example.com/c2.jpg",
                },
            ],
        },
    }


def _profile_api_payload():
    """Minimal RapidAPI-style JSON for user/info."""
    return {
        "msg": "success",
        "data": {
            "user": {
                "id": "123",
                "uniqueId": "tiktokuser",
                "nickname": "Display Name",
                "avatarThumb": "https://example.com/a.jpg",
                "signature": "Bio here",
                "verified": True,
                "secUid": "sec-uid-value",
                "ftc": False,
                "relation": 0,
                "openFavorite": True,
                "privateAccount": False,
                "secret": False,
                "isADVirtual": False,
            },
            "stats": {
                "followerCount": 10_000,
                "followingCount": 200,
                "heart": 50_000,
                "heartCount": 50_000,
                "videoCount": 42,
                "diggCount": 100,
            },
        },
    }


def _mock_request_json(payload):
    mock_resp = MagicMock()
    mock_resp.json.return_value = payload
    return mock_resp


class TestFetchTiktokContent(unittest.TestCase):
    @patch("src.tt_oop.requests.request")
    def test_returns_dataframe_with_expected_columns(self, mock_request):
        mock_request.return_value = _mock_request_json(_feed_api_payload())

        df = fetch_tiktok_content("creator1", count=20)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        expected_cols = {
            "content_id",
            "description",
            "username",
            "digg",
            "play",
        }
        self.assertTrue(expected_cols.issubset(set(df.columns)))
        mock_request.assert_called()
        call_kw = mock_request.call_args
        self.assertEqual(call_kw[0][0], "GET")
        self.assertIn("user/posts", call_kw[0][1])

    @patch("src.tt_oop.requests.request")
    def test_api_not_success_returns_none_from_print(self, mock_request):
        mock_request.return_value = _mock_request_json({"msg": "error", "data": {}})

        out = fetch_tiktok_content("anyuser", count=5)

        self.assertIsNone(out)


class TestFetchTiktokProfile(unittest.TestCase):
    @patch("src.tt_oop.requests.request")
    def test_returns_dataframe_with_profile_fields(self, mock_request):
        mock_request.return_value = _mock_request_json(_profile_api_payload())

        df = fetch_tiktok_profile("tiktokuser")

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["unique_id"], "tiktokuser")
        self.assertEqual(df.iloc[0]["followers"], 10_000)
        self.assertEqual(df.iloc[0]["video_count"], 42)
        mock_request.assert_called()
        self.assertIn("user/info", mock_request.call_args[0][1])

    @patch("src.tt_oop.requests.request")
    def test_api_not_success_returns_none(self, mock_request):
        mock_request.return_value = _mock_request_json({"msg": "failed", "data": {}})

        out = fetch_tiktok_profile("x")

        self.assertIsNone(out)


if __name__ == "__main__":
    unittest.main()
