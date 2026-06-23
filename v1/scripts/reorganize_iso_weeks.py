#!/usr/bin/env python3
"""
Reorganize assets/, content/, output/ into ISO week subfolders.

Usage:
  python3 scripts/reorganize_iso_weeks.py          # dry run (safe)
  python3 scripts/reorganize_iso_weeks.py --execute # apply moves
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
from schedule_calc import get_iso_week

DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
WEEK_RE = re.compile(r"^\d{4}-W\d{2}$")

# Files with no date in name but known content dates
FORCED_DATES: dict[str, str] = {
    "ds_complete_python_course.mp4": "2026-05-21",
    "life_habits.mp4": "2026-05-21",
    "poetry_when_dreams_speak.mp4": "2026-05-21",
    "pandas-for-data-analysis-load-filter-clean-aggregate-4-essen_carousel.html": "2026-06-10",
    "pandas-for-data-analysis-load-filter-clean-aggregate-4-essen_export.py": "2026-06-10",
}


def extract_week(name: str) -> str | None:
    if name in FORCED_DATES:
        return get_iso_week(FORCED_DATES[name])
    m = DATE_RE.search(name)
    return get_iso_week(m.group()) if m else None


def move_item(src: Path, dst_dir: Path, dry_run: bool) -> None:
    dst = dst_dir / src.name
    print(f"  {'[DRY] ' if dry_run else ''}mv  {src.relative_to(ROOT)}")
    print(f"       → {dst.relative_to(ROOT)}")
    if not dry_run:
        dst_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))


def reorganize(
    folder: Path,
    dry_run: bool,
    files_only: bool = False,
    dirs_only: bool = False,
    skip: set[str] | None = None,
    dated_only: bool = False,
) -> int:
    """Move direct children of folder into ISO week subdirs. Returns count moved."""
    skip = skip or set()
    count = 0
    for item in sorted(folder.iterdir()):
        if item.name.startswith("."):
            continue
        if item.name in skip:
            continue
        if WEEK_RE.match(item.name):
            continue  # already in a week folder
        if files_only and not item.is_file():
            continue
        if dirs_only and not item.is_dir():
            continue
        week = extract_week(item.name)
        if week:
            move_item(item, folder / week, dry_run)
            count += 1
        elif not dated_only:
            print(f"  [SKIP] {item.relative_to(ROOT)}  (no date)")
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Apply moves (default: dry run)")
    args = parser.parse_args()
    dry_run = not args.execute

    if dry_run:
        print("=== DRY RUN — pass --execute to apply ===\n")

    total = 0

    sections: list[tuple[str, dict]] = [
        ("assets/stories",            {"files_only": True}),
        ("assets/teleprompter",        {"files_only": True}),
        ("assets/thumbnails",          {"files_only": True}),
        ("assets/carousels",           {"files_only": True}),
        ("assets/carousels/slides",    {"dirs_only": True}),
        ("assets/video/edited",        {"files_only": True, "skip": {"shorts"}}),
        ("assets/video/edited/shorts", {"files_only": True}),
        ("assets/video/_work",         {"dirs_only": True}),
        ("assets/videos",              {"dirs_only": True, "skip": {"test_script"}}),
        ("assets/reels_video",         {"dirs_only": True}),
        ("assets/stories_video",       {"dirs_only": True}),
        ("content/prompts",            {"files_only": True}),
        ("content/archive",            {"files_only": True, "dated_only": True}),
        ("output/scheduled",           {"files_only": True, "dated_only": True}),
    ]

    for rel_path, kwargs in sections:
        folder = ROOT / rel_path
        if not folder.exists():
            print(f"[MISSING] {rel_path}")
            continue
        print(f"\n--- {rel_path} ---")
        n = reorganize(folder, dry_run, **kwargs)
        total += n

    print(f"\n{'Would move' if dry_run else 'Moved'} {total} items total.")


if __name__ == "__main__":
    main()
