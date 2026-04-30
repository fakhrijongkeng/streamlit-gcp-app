from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


DEFAULT_MODEL = "runwayml/stable-diffusion-v1-5"


@dataclass(frozen=True)
class HFImageResponse:
    image_bytes: bytes
    content_type: str | None


class HFInferenceError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def generate_image_via_hf(
    *,
    token: str,
    prompt: str,
    model: str = DEFAULT_MODEL,
    timeout_s: int = 60,
    extra_payload: dict[str, Any] | None = None,
) -> HFImageResponse:
    if not token:
        raise HFInferenceError("HF token is missing.", status_code=401)
    if not prompt.strip():
        raise HFInferenceError("Prompt cannot be empty.")

    api_url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {token}"}
    payload: dict[str, Any] = {"inputs": prompt}
    if extra_payload:
        payload.update(extra_payload)

    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=timeout_s)
    except requests.Timeout as e:
        raise HFInferenceError("Request timed out. Try again.", status_code=408) from e
    except requests.RequestException as e:
        raise HFInferenceError("Network error contacting Hugging Face.") from e

    if resp.status_code == 200:
        return HFImageResponse(
            image_bytes=resp.content,
            content_type=resp.headers.get("content-type"),
        )

    detail = ""
    try:
        data = resp.json()
        if isinstance(data, dict):
            detail = str(data.get("error") or data.get("message") or "")
    except Exception:
        detail = resp.text[:300].strip()

    if resp.status_code == 503 and ("loading" in detail.lower() or "currently loading" in detail.lower()):
        raise HFInferenceError(
            "Model is loading on Hugging Face. Wait ~10–30s and retry.",
            status_code=503,
        )

    msg = f"Hugging Face API error ({resp.status_code})."
    if detail:
        msg += f" Details: {detail}"
    raise HFInferenceError(msg, status_code=resp.status_code)
