#!/usr/bin/env python3
"""Publish to a Facebook Page (text, photo, or video) via the Graph API.

Note: in most setups FB simply mirrors from Instagram (cross-post on publish), so
direct FB publishing is optional. Use this only if you want FB to carry content IG
doesn't, or you are not cross-posting from IG.

Env: META_ACCESS_TOKEN, META_PAGE_ID (see docs/one-time-platform-setup.md).

CLI:
    python3 scripts/post_facebook.py --text "..."
    python3 scripts/post_facebook.py --photo <public_jpg_url> --text "..."
"""

from __future__ import annotations

import argparse
import sys

from lib.meta_graph import MetaGraphError, graph_post, require_env


def _creds() -> tuple[str, str]:
    env = require_env("META_ACCESS_TOKEN", "META_PAGE_ID")
    return env["META_ACCESS_TOKEN"], env["META_PAGE_ID"]


def post_text(message: str, link: str | None = None) -> str:
    """Publish a text (optionally link) post to the Page feed. Returns post id."""
    token, page_id = _creds()
    params = {"message": message, "access_token": token}
    if link:
        params["link"] = link
    result = graph_post(f"{page_id}/feed", params)
    return result["id"]


def post_photo(image_url: str, message: str = "") -> str:
    """Publish a photo (public image URL) to the Page. Returns post/photo id."""
    token, page_id = _creds()
    result = graph_post(
        f"{page_id}/photos",
        {"url": image_url, "caption": message, "access_token": token},
    )
    return result.get("post_id") or result["id"]


def post_video(video_url: str, message: str = "") -> str:
    """Publish a video (public URL) to the Page. Returns video id."""
    token, page_id = _creds()
    result = graph_post(
        f"{page_id}/videos",
        {"file_url": video_url, "description": message, "access_token": token},
    )
    return result["id"]


def main() -> None:
    ap = argparse.ArgumentParser(description="Publish to a Facebook Page via Graph API")
    ap.add_argument("--text", default="")
    ap.add_argument("--photo", help="Public https image URL")
    ap.add_argument("--video", help="Public https video URL")
    ap.add_argument("--link", help="Optional link for a text post")
    args = ap.parse_args()

    try:
        if args.photo:
            print(post_photo(args.photo, args.text))
        elif args.video:
            print(post_video(args.video, args.text))
        elif args.text:
            print(post_text(args.text, args.link))
        else:
            ap.error("one of --text / --photo / --video is required")
    except MetaGraphError as e:
        sys.exit(f"Facebook publish failed: {e}")


if __name__ == "__main__":
    main()
