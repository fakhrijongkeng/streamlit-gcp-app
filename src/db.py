from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import streamlit as st


DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "app.db"


def _get_db_path() -> Path:
    """
    Database path resolution:
    - Streamlit secrets: DB_PATH
    - Fallback: data/app.db
    """
    try:
        v = st.secrets.get("DB_PATH")
        if v:
            return Path(str(v))
    except Exception:
        pass
    return DEFAULT_DB_PATH


@st.cache_resource(show_spinner=False)
def get_connection() -> sqlite3.Connection:
    path = _get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path.as_posix(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    _init_schema(conn)
    return conn


def _init_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS etl_metadata (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          created_at_utc TEXT NOT NULL,
          last_sync_utc TEXT,
          rows_processed INTEGER NOT NULL,
          status TEXT NOT NULL,
          sources_json TEXT NOT NULL
        );
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tiktok_clips (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          created_at_utc TEXT NOT NULL,
          clip_date TEXT,
          creator TEXT,
          topic TEXT,
          caption TEXT,
          url TEXT,
          views INTEGER NOT NULL,
          likes INTEGER NOT NULL,
          comments INTEGER NOT NULL,
          shares INTEGER NOT NULL,
          saves INTEGER NOT NULL
        );
        """
    )
    conn.commit()


@dataclass(frozen=True)
class EtlMetadata:
    last_sync_utc: str | None
    rows_processed: int
    status: str
    sources: list[dict[str, Any]]


def upsert_latest_etl_metadata(meta: EtlMetadata) -> None:
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO etl_metadata (created_at_utc, last_sync_utc, rows_processed, status, sources_json)
        VALUES (?, ?, ?, ?, ?);
        """,
        (
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            meta.last_sync_utc,
            int(meta.rows_processed),
            str(meta.status),
            json.dumps(meta.sources),
        ),
    )
    conn.commit()


def get_latest_etl_metadata() -> EtlMetadata | None:
    conn = get_connection()
    row = conn.execute(
        """
        SELECT last_sync_utc, rows_processed, status, sources_json
        FROM etl_metadata
        ORDER BY id DESC
        LIMIT 1;
        """
    ).fetchone()
    if not row:
        return None
    sources = []
    try:
        sources = json.loads(row["sources_json"] or "[]")
        if not isinstance(sources, list):
            sources = []
    except Exception:
        sources = []

    return EtlMetadata(
        last_sync_utc=row["last_sync_utc"],
        rows_processed=int(row["rows_processed"] or 0),
        status=str(row["status"] or "unknown"),
        sources=sources,
    )


@dataclass(frozen=True)
class TikTokClip:
    clip_date: str | None
    creator: str | None
    topic: str | None
    caption: str | None
    url: str | None
    views: int
    likes: int
    comments: int
    shares: int
    saves: int


def replace_all_tiktok_clips(clips: list[TikTokClip]) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM tiktok_clips;")
    conn.executemany(
        """
        INSERT INTO tiktok_clips (
          created_at_utc, clip_date, creator, topic, caption, url,
          views, likes, comments, shares, saves
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        [
            (
                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                c.clip_date,
                c.creator,
                c.topic,
                c.caption,
                c.url,
                int(c.views),
                int(c.likes),
                int(c.comments),
                int(c.shares),
                int(c.saves),
            )
            for c in clips
        ],
    )
    conn.commit()


def list_tiktok_clips() -> list[dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT
          clip_date, creator, topic, caption, url,
          views, likes, comments, shares, saves
        FROM tiktok_clips
        ORDER BY clip_date DESC, views DESC;
        """
    ).fetchall()
    return [dict(r) for r in rows]

