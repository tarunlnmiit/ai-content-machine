#!/usr/bin/env python3
"""
Read slide_outline.json from content/derivatives/{slug}/ and output
a Canva Bulk Create-compatible CSV to output/scheduled/{slug}_slides.csv

CSV columns: slide_number, title, bullet1, bullet2, bullet3
"""

import argparse
import csv
import json
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent


from lib.slug import slugify


def process_slug(slug: str) -> Path:
    src = REPO / "content" / "derivatives" / slug / "slide_outline.json"
    if not src.exists():
        sys.exit(f"slide_outline.json not found: {src}")

    data = json.loads(src.read_text(encoding="utf-8"))

    # slide_outline may be the full repurpose JSON key or a standalone file
    slides = data if isinstance(data, list) else data.get("slides", [])
    if not slides:
        sys.exit(f"No slides found in {src}")

    out_dir = REPO / "output" / "scheduled"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{slug}_slides.csv"

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["slide_number", "title", "bullet1", "bullet2", "bullet3"])
        writer.writeheader()
        for slide in slides:
            bullets = slide.get("bullet_points", [])
            writer.writerow({
                "slide_number": slide.get("slide_number", ""),
                "title": slide.get("heading", ""),
                "bullet1": bullets[0] if len(bullets) > 0 else "",
                "bullet2": bullets[1] if len(bullets) > 1 else "",
                "bullet3": bullets[2] if len(bullets) > 2 else "",
            })

    return out_path


def find_all_slugs() -> list[str]:
    deriv_dir = REPO / "content" / "derivatives"
    if not deriv_dir.exists():
        return []
    return [
        d.name for d in deriv_dir.iterdir()
        if d.is_dir() and (d / "slide_outline.json").exists()
    ]


def main():
    parser = argparse.ArgumentParser(description="Generate Canva slides CSV from slide_outline.json.")
    parser.add_argument("--slug", help="Specific blog slug. Omit to process all slugs with slide_outline.json.")
    args = parser.parse_args()

    slugs = [args.slug] if args.slug else find_all_slugs()

    if not slugs:
        sys.exit("No slide_outline.json files found in content/derivatives/")

    for slug in slugs:
        out_path = process_slug(slug)
        print(f"Saved: {out_path.relative_to(REPO)}")

    print(f"\nDone — {len(slugs)} CSV(s) written.")
    print("Next: Canva → your Slide Deck template → Apps → Bulk Create → upload CSV")


if __name__ == "__main__":
    main()
