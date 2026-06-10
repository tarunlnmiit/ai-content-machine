#!/usr/bin/env python3
"""
sync_tracker.py — build/update data/content_tracker.csv from derivatives/ + output/.

Usage:
  python3 scripts/sync_tracker.py                    # scan all derivatives/
  python3 scripts/sync_tracker.py --week 2026-W24    # single week
  python3 scripts/sync_tracker.py --dry-run          # print rows, no write
"""

import argparse
import csv
import glob
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRACKER_PATH = REPO_ROOT / "data" / "content_tracker.csv"
MEDIUM_POSTS_PATH = REPO_ROOT / "output" / "published" / "medium_posts.json"

FIELDNAMES = [
    "Week", "Date", "Niche", "Title", "Slug",
    "Status", "Substack URL", "Medium URL", "YouTube URL",
    "Shorts Count", "Social Scheduled", "Buffer Slot", "Notes",
]

NICHE_MAP = {
    "data_science_tech": "DS",
    "data-science-tech": "DS",
    "life_self_dev": "Life",
    "life-self-dev": "Life",
    "poetry_quotes": "Poetry",
    "poetry-quotes": "Poetry",
}

STATUS_ORDER = ["Idea", "Draft", "Script", "Shot", "Rendered", "Uploaded", "Published", "Archived"]


def detect_niche(dirname: str) -> str:
    for key, label in NICHE_MAP.items():
        if key in dirname:
            return label
    return "Unknown"


def detect_date(dirname: str) -> str:
    match = re.search(r"(\d{4}-\d{2}-\d{2})", dirname)
    return match.group(1) if match else ""


def detect_week(date_str: str) -> str:
    if not date_str:
        return ""
    try:
        from datetime import date
        parts = date_str.split("-")
        d = date(int(parts[0]), int(parts[1]), int(parts[2]))
        iso = d.isocalendar()
        return f"{iso[0]}-W{iso[1]:02d}"
    except Exception:
        return ""


def load_medium_posts() -> dict:
    if not MEDIUM_POSTS_PATH.exists():
        return {}
    with open(MEDIUM_POSTS_PATH) as f:
        posts = json.load(f)
    # medium_posts.json is a list of {slug, url} or {title, url} entries
    index = {}
    if isinstance(posts, list):
        for p in posts:
            if isinstance(p, dict):
                key = p.get("slug") or p.get("title") or ""
                url = p.get("url") or p.get("medium_url") or ""
                if key and url:
                    index[key.lower()] = url
    elif isinstance(posts, dict):
        for k, v in posts.items():
            index[k.lower()] = v if isinstance(v, str) else v.get("url", "")
    return index


def count_shorts(week: str, slug_dir: str) -> int:
    # slug_dir is the full derivative dirname (e.g. 2026-06-08_data_science_tech_python-...)
    # shorts are at output/animations/{week}/{slug_dir}_s*.mp4
    # try exact match first, then fuzzy
    anim_dir = REPO_ROOT / "output" / "animations" / week
    if not anim_dir.exists():
        return 0
    base = slug_dir
    exact = list(anim_dir.glob(f"{base}_s*.mp4"))
    if exact:
        return len(exact)
    # fuzzy: match any file that starts with slug_dir[:30]
    fuzzy = list(anim_dir.glob(f"{base[:30]}*_s*.mp4"))
    return len(set(f.stem for f in fuzzy))


def check_social_scheduled(slug_dir: str) -> str:
    csv_dir = REPO_ROOT / "output" / "scheduled"
    found_in = []
    for csv_path in csv_dir.glob("metricool_*.csv"):
        try:
            with open(csv_path) as f:
                content = f.read()
            if slug_dir[:30].lower() in content.lower():
                found_in.append(csv_path.stem.replace("metricool_", ""))
        except Exception:
            pass
    if not found_in:
        return "No"
    return "Yes"


def derive_status(schedule: dict, slug_dir: str, week: str) -> str:
    if schedule.get("youtube_url"):
        return "Uploaded"
    if schedule.get("substack_url"):
        return "Published"
    # check if video rendered
    anim_dir = REPO_ROOT / "output" / "animations" / week
    if anim_dir.exists():
        renders = list(anim_dir.glob(f"{slug_dir[:40]}*.mp4"))
        if renders:
            return "Rendered"
    # check if raw footage exists
    raw_dir = REPO_ROOT / "assets" / "raw" / week
    if raw_dir.exists():
        raws = list(raw_dir.glob(f"{slug_dir[:30]}*.*"))
        if raws:
            return "Shot"
    # check if script exists
    script_dir = REPO_ROOT / "content" / "scripts" / week
    if script_dir.exists():
        scripts = list(script_dir.glob(f"{slug_dir[:30]}*_yt.md"))
        if scripts:
            return "Script"
    return "Draft"


def read_existing_tracker() -> dict:
    rows = {}
    if not TRACKER_PATH.exists():
        return rows
    with open(TRACKER_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows[row["Slug"]] = row
    return rows


def build_row(slug_dir: str, schedule_path: Path, medium_index: dict) -> dict:
    with open(schedule_path) as f:
        try:
            schedule = json.load(f)
        except json.JSONDecodeError:
            schedule = {}

    date_str = detect_date(slug_dir)
    week = schedule.get("week") or detect_week(date_str)
    niche = detect_niche(slug_dir)
    title = (
        schedule.get("title")
        or schedule.get("youtube_metadata", {}).get("title")
        or slug_dir
    )

    substack_url = schedule.get("substack_url", "")
    medium_url = schedule.get("medium_url", "")
    youtube_url = schedule.get("youtube_url", "")

    # fallback: check medium_posts.json
    if not medium_url:
        slug_key = slug_dir.lower()
        for key, url in medium_index.items():
            if key in slug_key or slug_key[:30] in key:
                medium_url = url
                break

    status = derive_status(schedule, slug_dir, week)
    shorts_count = count_shorts(week, slug_dir)
    social_scheduled = check_social_scheduled(slug_dir)

    notes_parts = []
    if medium_url and not schedule.get("medium_url"):
        notes_parts.append("Medium URL from medium_posts.json")

    return {
        "Week": week,
        "Date": date_str,
        "Niche": niche,
        "Title": title,
        "Slug": slug_dir,
        "Status": status,
        "Substack URL": substack_url,
        "Medium URL": medium_url,
        "YouTube URL": youtube_url,
        "Shorts Count": str(shorts_count),
        "Social Scheduled": social_scheduled,
        "Buffer Slot": schedule.get("buffer_slot", "Live"),
        "Notes": "; ".join(notes_parts),
    }


def main():
    parser = argparse.ArgumentParser(description="Sync content tracker CSV from derivatives/")
    parser.add_argument("--week", help="Only process this ISO week (e.g. 2026-W24)")
    parser.add_argument("--dry-run", action="store_true", help="Print rows, don't write")
    args = parser.parse_args()

    medium_index = load_medium_posts()
    existing = read_existing_tracker()

    derivatives_root = REPO_ROOT / "content" / "derivatives"

    if args.week:
        pattern = str(derivatives_root / args.week / "*" / "schedule.json")
    else:
        pattern = str(derivatives_root / "*" / "*" / "schedule.json")

    schedule_files = sorted(glob.glob(pattern))

    if not schedule_files:
        print(f"No schedule.json files found matching: {pattern}")
        sys.exit(0)

    rows = dict(existing)
    new_count = 0
    updated_count = 0

    for schedule_path in schedule_files:
        slug_dir = Path(schedule_path).parent.name
        row = build_row(slug_dir, Path(schedule_path), medium_index)
        slug = row["Slug"]

        if slug in rows:
            # preserve manually-edited fields: Notes, Buffer Slot
            old = rows[slug]
            if old.get("Notes") and not row["Notes"]:
                row["Notes"] = old["Notes"]
            if old.get("Buffer Slot") and old["Buffer Slot"] != "Live":
                row["Buffer Slot"] = old["Buffer Slot"]
            # preserve higher status if manually set
            if old.get("Status") in STATUS_ORDER and row["Status"] in STATUS_ORDER:
                if STATUS_ORDER.index(old["Status"]) > STATUS_ORDER.index(row["Status"]):
                    row["Status"] = old["Status"]
            updated_count += 1
        else:
            new_count += 1

        rows[slug] = row

    sorted_rows = sorted(rows.values(), key=lambda r: (r.get("Week", ""), r.get("Date", ""), r.get("Niche", "")))

    if args.dry_run:
        print(f"\n{'Week':<10} {'Date':<12} {'Niche':<8} {'Status':<12} {'Title':<50}")
        print("-" * 100)
        for r in sorted_rows:
            print(f"{r['Week']:<10} {r['Date']:<12} {r['Niche']:<8} {r['Status']:<12} {r['Title'][:49]:<50}")
        print(f"\n{len(sorted_rows)} total rows ({new_count} new, {updated_count} updated) — dry run, not written")
        return

    TRACKER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(TRACKER_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(sorted_rows)

    print(f"✓ {TRACKER_PATH.relative_to(REPO_ROOT)}: {len(sorted_rows)} rows ({new_count} new, {updated_count} updated)")


if __name__ == "__main__":
    main()
