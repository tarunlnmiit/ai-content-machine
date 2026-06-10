#!/usr/bin/env python3
"""
Map Google Drive file IDs to platform-specific image URLs.
Create schedule.json files in derivatives/ with image_urls + publish dates.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).parent.parent

# IST = UTC+5:30
IST = timezone(timedelta(hours=5, minutes=30))

# Per-niche canonical schedule (weekday 0=Mon, times IST)
NICHE_SCHEDULE = {
    "life":   {"ig_fb": (1,  8, 0), "threads": (1, 20, 0)},   # Tue 8 AM / 8 PM
    "ds":     {"ig_fb": (2,  8, 0), "threads": (2, 20, 0)},   # Wed 8 AM / 8 PM
    "poetry": {"ig_fb": (4, 10, 0), "threads": (4, 12, 0)},   # Fri 10 AM / 12 PM
}


def drive_id_to_url(file_id: str) -> str:
    """Convert Drive file ID to public viewing URL."""
    return f"https://drive.google.com/uc?id={file_id}&export=download"


def platform_from_filename(filename: str) -> str | None:
    """Extract platform from filename (instagram, threads, twitter, linkedin)."""
    lower = filename.lower()
    for platform in ["instagram", "threads", "twitter", "linkedin"]:
        if f"_{platform}" in lower:
            return platform
    return None


def slug_from_filename(filename: str) -> str:
    """Extract slug from filename."""
    name = filename.rsplit(".", 1)[0]
    for platform in ["instagram", "threads", "twitter", "linkedin"]:
        if f"_{platform}" == name[-len(platform)-1:]:
            name = name[:-len(platform)-1]
            break
    return name


def _niche_from_slug(slug: str) -> str:
    """Returns 'ds', 'life', or 'poetry' based on slug contents."""
    s = slug.lower()
    if "_data_science_tech_" in s:
        return "ds"
    if "_poetry_quotes_" in s:
        return "poetry"
    return "life"


def next_weekday(weekday: int, hour: int, minute: int, week_offset: int = 1) -> datetime:
    """Compute next occurrence of weekday at time, offset by weeks."""
    now = datetime.now(IST)
    current_weekday = now.weekday()
    days_ahead = weekday - current_weekday
    if days_ahead <= 0:
        days_ahead += 7
    target_date = now + timedelta(days=days_ahead + 7 * week_offset)
    return target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)


def main():
    """Load w21/w22 Drive files, map to slugs, create schedule.json."""
    files_to_process = [
        Path("/tmp/w21_files.json"),
        Path("/tmp/w22_files.json"),
    ]

    all_files = {}
    for json_file in files_to_process:
        if not json_file.exists():
            print(f"⚠️  {json_file} not found, skipping")
            continue
        data = json.loads(json_file.read_text(encoding="utf-8"))
        for file_entry in data.get("files", []):
            filename = file_entry.get("name", "")
            file_id = file_entry.get("id", "")
            if filename and file_id:
                all_files[filename] = file_id

    print(f"📂 Found {len(all_files)} Drive files")

    # Group files by slug
    slug_files = {}
    for filename, file_id in all_files.items():
        slug = slug_from_filename(filename)
        platform = platform_from_filename(filename)
        if not slug or not platform:
            continue
        if slug not in slug_files:
            slug_files[slug] = {}
        slug_files[slug][platform] = (filename, file_id)

    print(f"🏷️  Mapped {len(slug_files)} unique slugs")

    # Create schedule.json for each slug
    derivatives_dir = REPO / "content" / "derivatives"
    updated_count = 0

    for slug, platforms in slug_files.items():
        date_str = slug[:10]
        from lib.schedule_calc import get_iso_week
        week = get_iso_week(date_str)

        slug_dir = derivatives_dir / week / slug
        slug_dir.mkdir(parents=True, exist_ok=True)

        schedule_file = slug_dir / "schedule.json"

        # Determine niche and compute publish times
        niche = _niche_from_slug(slug)
        sched = NICHE_SCHEDULE.get(niche, NICHE_SCHEDULE["life"])
        
        weekday, hour, minute = sched["ig_fb"]
        ig_dt = next_weekday(weekday, hour, minute, week_offset=1)
        
        weekday, hour, minute = sched["threads"]
        thr_dt = next_weekday(weekday, hour, minute, week_offset=1)

        # Build image_urls dict
        image_urls = {}
        for platform, (filename, file_id) in platforms.items():
            image_urls[platform] = drive_id_to_url(file_id)

        # Create schedule.json structure
        sched_data = {
            "social": {
                "ig_fb_publish_at": ig_dt.isoformat(),
                "threads_publish_at": thr_dt.isoformat(),
            },
            "image_urls": image_urls,
        }

        schedule_file.write_text(json.dumps(sched_data, indent=2), encoding="utf-8")
        print(f"✅ {slug}: {', '.join(platforms.keys())}")
        updated_count += 1

    print(f"\n✅ Created {updated_count} schedule.json files")


if __name__ == "__main__":
    main()
