#!/usr/bin/env python3
"""Muapi.ai Python client — mirrors the JS MuapiClient from open-generative-ai.

API pattern (2-step polling):
  POST https://api.muapi.ai/api/v1/{model-endpoint}  → {request_id}
  GET  https://api.muapi.ai/api/v1/predictions/{request_id}/result → poll until completed

Auth: x-api-key header (MUAPI_KEY env var).
"""

import os
import time
import requests
from pathlib import Path

BASE_URL = "https://api.muapi.ai"
POLL_INTERVAL = 3       # seconds between polls
POLL_MAX_ATTEMPTS = 180  # 9 min max


def _get_key() -> str:
    key = os.getenv("MUAPI_KEY", "")
    if not key:
        raise RuntimeError("MUAPI_KEY not set in environment")
    return key


def _poll(request_id: str, key: str, max_attempts: int = POLL_MAX_ATTEMPTS) -> dict:
    url = f"{BASE_URL}/api/v1/predictions/{request_id}/result"
    headers = {"x-api-key": key, "Content-Type": "application/json"}

    for attempt in range(1, max_attempts + 1):
        time.sleep(POLL_INTERVAL)
        resp = requests.get(url, headers=headers, timeout=30)

        if not resp.ok:
            if resp.status_code >= 500 and attempt < max_attempts:
                continue
            raise RuntimeError(f"Poll {resp.status_code}: {resp.text[:200]}")

        data = resp.json()
        status = (data.get("status") or "").lower()

        if status in ("completed", "succeeded", "success"):
            return data
        if status in ("failed", "error"):
            raise RuntimeError(f"Generation failed: {data.get('error', 'unknown')}")
        # still processing — keep polling

    raise TimeoutError(f"Timed out after {max_attempts * POLL_INTERVAL}s")


def _extract_url(result: dict) -> str:
    url = (result.get("outputs") or [None])[0] or result.get("url") or (result.get("output") or {}).get("url")
    if not url:
        raise RuntimeError(f"No output URL in result: {result}")
    return url


def generate_video(
    prompt: str,
    model: str = "seedance-lite-t2v",
    aspect_ratio: str = "16:9",
    duration: int = 5,
    resolution: str = "720p",
) -> str:
    """Submit text-to-video job. Returns output video URL."""
    key = _get_key()
    url = f"{BASE_URL}/api/v1/{model}"
    payload = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "duration": duration,
        "resolution": resolution,
    }
    resp = requests.post(url, json=payload, headers={"x-api-key": key}, timeout=30)
    if not resp.ok:
        raise RuntimeError(f"Submit failed {resp.status_code}: {resp.text[:200]}")

    data = resp.json()
    request_id = data.get("request_id") or data.get("id")
    if not request_id:
        return _extract_url(data)  # some models return sync

    result = _poll(request_id, key)
    return _extract_url(result)


def download_video(video_url: str, dest_path: Path) -> Path:
    """Download video from URL to dest_path. Returns path."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(video_url, stream=True, timeout=120)
    resp.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return dest_path
