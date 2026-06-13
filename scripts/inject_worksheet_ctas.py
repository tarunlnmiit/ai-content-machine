#!/usr/bin/env python3
"""Inject worksheet CTAs into derivatives retroactively (W22 onwards) or as needed."""

import argparse
import sys
from pathlib import Path

from lib.worksheet_cta import (
    inject_worksheet_ctas_to_dir,
    extract_worksheet_slug_from_dir,
    worksheet_exists,
)

REPO = Path(__file__).parent.parent
DERIVATIVES = REPO / "content" / "derivatives"


def niche_from_slug(slug: str) -> str:
    """Map a derivative slug to a niche key (ds / life / poetry)."""
    if "data_science_tech" in slug:
        return "ds"
    if "poetry_quotes" in slug:
        return "poetry"
    return "life"


def week_to_number(week_str: str) -> int:
    """Parse 'W22' to 22, 'W01' to 1. Returns -1 if invalid."""
    try:
        return int(week_str.lstrip("W"))
    except ValueError:
        return -1


def week_number_from_dir(dir_name: str) -> int | None:
    """Extract week number from '2026-W22' format. Returns None if not a week dir."""
    parts = dir_name.split("-")
    if len(parts) == 2 and parts[1].startswith("W"):
        return week_to_number(parts[1])
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Inject worksheet CTAs into derivative files retroactively."
    )
    parser.add_argument(
        "--week-from",
        default="W22",
        help="Start week (e.g., W22, W21). Default: W22",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )
    args = parser.parse_args()

    min_week = week_to_number(args.week_from)
    if min_week < 0:
        sys.exit(f"Invalid week format: {args.week_from}")

    if not DERIVATIVES.exists():
        sys.exit(f"Derivatives directory not found: {DERIVATIVES}")

    modified_files = []
    skipped = []

    # Walk week directories
    for week_dir in sorted(DERIVATIVES.iterdir()):
        if not week_dir.is_dir():
            continue

        week_num = week_number_from_dir(week_dir.name)
        if week_num is None or week_num < min_week:
            continue

        print(f"\n[{week_dir.name}]")

        # Walk slug directories within week
        for slug_dir in sorted(week_dir.iterdir()):
            if not slug_dir.is_dir():
                continue

            dir_name = slug_dir.name
            niche = niche_from_slug(dir_name)

            # Skip poetry
            if niche == "poetry":
                skipped.append((dir_name, "poetry niche"))
                continue

            # Extract worksheet slug
            ws_slug = extract_worksheet_slug_from_dir(dir_name)
            if not ws_slug:
                skipped.append((dir_name, "invalid dir name format"))
                continue

            # Check if worksheet exists
            if not worksheet_exists(ws_slug):
                skipped.append((dir_name, f"no worksheet for '{ws_slug}'"))
                continue

            # Inject CTAs
            if args.dry_run:
                print(f"  [DRY-RUN] Would inject CTA into {dir_name}")
            else:
                modified = inject_worksheet_ctas_to_dir(slug_dir, ws_slug, niche)
                if modified:
                    print(f"  ✓ {dir_name}")
                    for f in modified:
                        print(f"    └ {f}")
                    modified_files.extend(modified)
                else:
                    print(f"  → {dir_name} (already present or no files modified)")

    # Summary
    print("\n" + "=" * 60)
    print(f"Processed: {len(modified_files) if not args.dry_run else '(dry-run)'} files modified")
    if skipped:
        print(f"Skipped: {len(skipped)}")
        for dir_name, reason in skipped[:10]:  # Show first 10
            print(f"  • {dir_name}: {reason}")
        if len(skipped) > 10:
            print(f"  ... and {len(skipped) - 10} more")


if __name__ == "__main__":
    main()
