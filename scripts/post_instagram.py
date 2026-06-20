#!/usr/bin/env python3
"""Publish to Instagram (Reels / single image / carousel) via the Instagram Graph API.

Constraint (by design of the IG API): the API ingests media from a PUBLIC https
URL — it cannot upload local bytes. The pipeline already hosts images (Google
Drive via populate_image_urls_from_gdrive.py); Reels need a public video URL too.
So callers pass media_url(s), not local paths.

Honesty guardrail: Reels, single image, and carousel only (Business/Creator
account). IG Stories are not API-publishable here — keep those manual.

Env: META_ACCESS_TOKEN, IG_USER_ID (see docs/one-time-platform-setup.md).

CLI (manual test):
    python3 scripts/post_instagram.py --reel <public_mp4_url> --caption "..."
    python3 scripts/post_instagram.py --image <public_jpg_url> --caption "..."
"""

from __future__ import annotations

import argparse
import sys

from lib.meta_graph import (
    MetaGraphError,
    graph_post,
    require_env,
    wait_for_container,
)


def _creds() -> tuple[str, str]:
    env = require_env("META_ACCESS_TOKEN", "IG_USER_ID")
    return env["META_ACCESS_TOKEN"], env["IG_USER_ID"]


def post_reel(media_url: str, caption: str, *, share_to_feed: bool = True) -> str:
    """Publish a Reel from a public video URL. Returns the published media id."""
    token, ig_id = _creds()
    container = graph_post(
        f"{ig_id}/media",
        {
            "media_type": "REELS",
            "video_url": media_url,
            "caption": caption,
            "share_to_feed": "true" if share_to_feed else "false",
            "access_token": token,
        },
    )
    container_id = container["id"]
    wait_for_container(container_id, token)
    published = graph_post(
        f"{ig_id}/media_publish",
        {"creation_id": container_id, "access_token": token},
    )
    return published["id"]


def post_image(media_url: str, caption: str) -> str:
    """Publish a single image from a public image URL. Returns the published media id."""
    token, ig_id = _creds()
    container = graph_post(
        f"{ig_id}/media",
        {"image_url": media_url, "caption": caption, "access_token": token},
    )
    container_id = container["id"]
    wait_for_container(container_id, token)
    published = graph_post(
        f"{ig_id}/media_publish",
        {"creation_id": container_id, "access_token": token},
    )
    return published["id"]


def post_carousel(media_urls: list[str], caption: str) -> str:
    """Publish a carousel (2–10 public image URLs). Returns the published media id."""
    if not 2 <= len(media_urls) <= 10:
        raise MetaGraphError(f"Carousel needs 2–10 images, got {len(media_urls)}")
    token, ig_id = _creds()
    child_ids = []
    for url in media_urls:
        child = graph_post(
            f"{ig_id}/media",
            {"image_url": url, "is_carousel_item": "true", "access_token": token},
        )
        wait_for_container(child["id"], token)
        child_ids.append(child["id"])
    parent = graph_post(
        f"{ig_id}/media",
        {
            "media_type": "CAROUSEL",
            "children": ",".join(child_ids),
            "caption": caption,
            "access_token": token,
        },
    )
    wait_for_container(parent["id"], token)
    published = graph_post(
        f"{ig_id}/media_publish",
        {"creation_id": parent["id"], "access_token": token},
    )
    return published["id"]


def main() -> None:
    ap = argparse.ArgumentParser(description="Publish to Instagram via Graph API")
    ap.add_argument("--reel", help="Public https URL of the Reel video")
    ap.add_argument("--image", help="Public https URL of the image")
    ap.add_argument("--carousel", nargs="+", help="2–10 public image URLs")
    ap.add_argument("--caption", default="")
    args = ap.parse_args()

    try:
        if args.reel:
            print(post_reel(args.reel, args.caption))
        elif args.image:
            print(post_image(args.image, args.caption))
        elif args.carousel:
            print(post_carousel(args.carousel, args.caption))
        else:
            ap.error("one of --reel / --image / --carousel is required")
    except MetaGraphError as e:
        sys.exit(f"Instagram publish failed: {e}")


if __name__ == "__main__":
    main()
