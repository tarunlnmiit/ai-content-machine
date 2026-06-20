#!/usr/bin/env python3
"""Host rendered reels at a public URL (Vercel Blob) and write the reel manifest.

This is the missing link that lets Instagram Reels auto-publish: the IG Graph API
ingests a reel from a PUBLIC https video URL, not local bytes. This uploads each
`assets/video/edited/shorts/{week}/{slug}_short_NN.mp4` to Vercel Blob and writes
`data/reel_media_urls.json` (the manifest `load_posts.py` reads to stage IG reels).

Requires: BLOB_READ_WRITE_TOKEN in .env (Vercel → Storage → Blob → token).
⚠️ Verify with one upload before relying on it — the Blob API version header may
need bumping. Until a token is set + smoke-tested, IG reels stay manual.

Usage:
    python3 scripts/upload_reels_blob.py --week 2026-W22
    python3 scripts/upload_reels_blob.py --week 2026-W22 --slug 2026-05-25-data_science_tech-...
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO = Path(__file__).resolve().parent.parent
load_dotenv(REPO / ".env")

BLOB_API = "https://blob.vercel-storage.com"
BLOB_API_VERSION = os.environ.get("VERCEL_BLOB_API_VERSION", "7")
MANIFEST = REPO / "data" / "reel_media_urls.json"
SHORT_RE = re.compile(r"_short_(\d+)\.mp4$")


def upload_blob(path: Path, token: str) -> str:
    """Upload a file to Vercel Blob (public). Returns the public URL."""
    pathname = f"reels/{path.name}"
    headers = {
        "authorization": f"Bearer {token}",
        "x-content-type": "video/mp4",
        "x-api-version": BLOB_API_VERSION,
        "x-add-random-suffix": "1",
    }
    with open(path, "rb") as f:
        resp = requests.put(f"{BLOB_API}/{pathname}", headers=headers, data=f, timeout=300)
    if resp.status_code >= 400:
        raise RuntimeError(f"Blob upload failed ({resp.status_code}): {resp.text[:300]}")
    url = resp.json().get("url")
    if not url:
        raise RuntimeError(f"Blob response had no url: {resp.text[:300]}")
    return url


def main() -> int:
    ap = argparse.ArgumentParser(description="Upload reels to Vercel Blob + write manifest")
    ap.add_argument("--week", required=True, help="ISO week, e.g. 2026-W22")
    ap.add_argument("--slug", help="Limit to one slug (default: all in the week)")
    args = ap.parse_args()

    token = os.environ.get("BLOB_READ_WRITE_TOKEN")
    if not token:
        sys.exit("BLOB_READ_WRITE_TOKEN not set in .env — see Vercel → Storage → Blob.")

    shorts_dir = REPO / "assets" / "video" / "edited" / "shorts" / args.week
    if not shorts_dir.exists():
        sys.exit(f"No shorts dir for week: {shorts_dir}")

    reels = sorted(p for p in shorts_dir.glob("*_short_*.mp4")
                   if not args.slug or p.name.startswith(args.slug))
    if not reels:
        sys.exit(f"No reels found in {shorts_dir}" + (f" for slug {args.slug}" if args.slug else ""))

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}

    for path in reels:
        m = SHORT_RE.search(path.name)
        idx = int(m.group(1)) if m else 0
        slug = SHORT_RE.sub("", path.name)
        print(f"Uploading {path.name} …", end=" ", flush=True)
        url = upload_blob(path, token)
        print("OK")
        entries = [e for e in manifest.get(slug, []) if e.get("index") != idx]
        entries.append({"index": idx, "url": url})
        manifest[slug] = sorted(entries, key=lambda e: e["index"])

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\n✓ Manifest → {MANIFEST.relative_to(REPO)} ({sum(len(v) for v in manifest.values())} reels)")
    print("Next: python3 scripts/load_posts.py --week " + args.week + "  (stages IG reels)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
