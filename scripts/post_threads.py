#!/usr/bin/env python3
"""Publish to Threads (text or text+media) via the Threads Graph API.

Two-step like IG: create a media container, then publish it. Text-only posts
publish immediately; media posts ingest from a public URL.

Env: THREADS_ACCESS_TOKEN, THREADS_USER_ID (see docs/one-time-platform-setup.md).

CLI:
    python3 scripts/post_threads.py --text "..."
    python3 scripts/post_threads.py --text "..." --image <public_jpg_url>
"""

from __future__ import annotations

import argparse
import sys

from lib.meta_graph import (
    THREADS_ROOT,
    MetaGraphError,
    graph_post,
    require_env,
    wait_for_container,
)


def _creds() -> tuple[str, str]:
    env = require_env("THREADS_ACCESS_TOKEN", "THREADS_USER_ID")
    return env["THREADS_ACCESS_TOKEN"], env["THREADS_USER_ID"]


def post_thread(text: str, image_url: str | None = None,
                video_url: str | None = None) -> str:
    """Publish one Threads post. Returns the published thread id."""
    token, user_id = _creds()
    params = {"text": text, "access_token": token}
    if video_url:
        params["media_type"] = "VIDEO"
        params["video_url"] = video_url
    elif image_url:
        params["media_type"] = "IMAGE"
        params["image_url"] = image_url
    else:
        params["media_type"] = "TEXT"

    container = graph_post(f"{user_id}/threads", params, root=THREADS_ROOT)
    container_id = container["id"]
    if image_url or video_url:
        wait_for_container(container_id, token, root=THREADS_ROOT)
    published = graph_post(
        f"{user_id}/threads_publish",
        {"creation_id": container_id, "access_token": token},
        root=THREADS_ROOT,
    )
    return published["id"]


def main() -> None:
    ap = argparse.ArgumentParser(description="Publish to Threads via Graph API")
    ap.add_argument("--text", required=True)
    ap.add_argument("--image", help="Public https image URL")
    ap.add_argument("--video", help="Public https video URL")
    args = ap.parse_args()

    try:
        print(post_thread(args.text, image_url=args.image, video_url=args.video))
    except MetaGraphError as e:
        sys.exit(f"Threads publish failed: {e}")


if __name__ == "__main__":
    main()
