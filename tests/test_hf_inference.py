from __future__ import annotations

import unittest
from unittest.mock import patch

from src.hf_inference import HFInferenceError, generate_image_via_hf


class TestGenerateImageViaHF(unittest.TestCase):
    @patch("src.hf_inference.requests.post")
    def test_request_exception_message_is_clearly_explained(self, mock_post):
        mock_post.side_effect = ConnectionError("Name resolution failed")

        with self.assertRaises(HFInferenceError) as cm:
            generate_image_via_hf(token="hf_test", prompt="a cat")

        self.assertIn("Network error contacting Hugging Face", str(cm.exception))
        self.assertIn("Name resolution failed", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
