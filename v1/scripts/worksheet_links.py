#!/usr/bin/env python3
"""Emit copy-paste worksheet download links from worksheets-manifest.json.

Phase 1: links for W21 blogs already drafted on Medium (paste into the draft
+ social posts).  Phase 2: run unfiltered to cover all past worksheets.

Usage:
    python scripts/worksheet_links.py                 # all worksheets
    python scripts/worksheet_links.py --week 2026-W21 # one ISO week
    python scripts/worksheet_links.py --niche life_self_dev
    python scripts/worksheet_links.py --json          # machine-readable

The manifest must exist first:
    node scripts/build-worksheets-manifest.mjs
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.worksheet_cta import (  # noqa: E402
    base_url,
    worksheet_url,
    worksheet_blog_snippet,
    worksheet_yt_description_snippet,
)

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "worksheets-manifest.json"


def iso_week_of(date_str: str) -> str:
    """YYYY-MM-DD -> YYYY-Wnn (matches the worksheet folder grouping)."""
    from datetime import date

    y, m, d = (int(p) for p in date_str.split("-"))
    iso = date(y, m, d).isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def load_manifest() -> dict:
    if not MANIFEST.exists():
        sys.exit(
            "worksheets-manifest.json not found. "
            "Run: node scripts/build-worksheets-manifest.mjs"
        )
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--week", help="Filter by ISO week, e.g. 2026-W21")
    ap.add_argument("--niche", help="Filter by niche segment, e.g. life_self_dev")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of a table")
    args = ap.parse_args()

    worksheets = load_manifest().get("worksheets", {})
    rows = []
    for slug, e in sorted(worksheets.items(), key=lambda kv: kv[1]["date"]):
        if args.week and iso_week_of(e["date"]) != args.week:
            continue
        if args.niche and e["niche"] != args.niche:
            continue
        rows.append(
            {
                "date": e["date"],
                "week": iso_week_of(e["date"]),
                "niche": e["niche"],
                "title": e["title"],
                "slug": slug,
                "url": worksheet_url(slug),
            }
        )

    if not rows:
        sys.exit("No worksheets matched the filters.")

    if args.json:
        print(json.dumps(rows, indent=2))
        return

    print(f"\nWorksheet links  (BASE_URL = {base_url()})\n")
    for r in rows:
        print(f"{'─' * 72}")
        print(f"{r['title']}  ·  {r['date']} · {r['week']} · {r['niche']}")
        print(f"\nURL:\n  {r['url']}")
        print("\nBlog (paste into Medium/Substack body):")
        print(f"  {worksheet_blog_snippet(r['slug'], r['title'])}")
        print("\nYouTube description (paste into the video description):")
        for line in worksheet_yt_description_snippet(r["slug"], r["title"]).splitlines():
            print(f"  {line}")
        print()
    print(f"{'─' * 72}\n{len(rows)} worksheet(s).\n")


if __name__ == "__main__":
    main()
