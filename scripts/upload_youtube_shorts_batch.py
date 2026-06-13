#!/usr/bin/env python3
"""
upload_youtube_shorts_batch.py — Batch upload YouTube Shorts for a slug.

Discovers all clip shorts (_short_NN / _yt_short_NN) and Remotion reels (_sNN)
for a given slug, maps them to scheduled publish times, and uploads via the
YouTube Data API using shared auth from upload_youtube.py.

USAGE:
    python3 scripts/upload_youtube_shorts_batch.py \\
        --slug 2026-05-21_life_self_dev_how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals \\
        --publish-week 2026-W25 \\
        [--dry-run] [--pin-comment] [--slots 0,1,5]

OPTIONS:
    --slug SLUG             Required. Derivatives slug (date_niche_title format).
    --publish-week YYYY-Wnn Override schedule.json timestamps with computed times
                            for the given ISO week (Mon–Sun, 10 AM + 8 PM IST).
    --dry-run               Print upload plan without uploading anything.
    --pin-comment           Post long-form URL as first comment after each upload.
                            Pin manually in YouTube Studio (API cannot pin).
    --slots N,N,...         Upload only specific slot numbers (default: all found).

FIRST-TIME SETUP:
    Run once per channel to register OAuth tokens:
        python3 scripts/upload_youtube.py --register
"""

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib.schedule_calc import get_iso_week
from upload_youtube import get_credentials, post_comment, resolve_channel, upload_video

# ── Niche config ──────────────────────────────────────────────────────────────
NICHE_MARKERS = {
    "DS": ["data_science_tech", "data-science-tech"],
    "Life": ["life_self_dev", "life-self-dev"],
    "Poetry": ["poetry_quotes", "poetry-quotes"],
}

NICHE_CHANNEL = {
    "DS": "Breath of Data Science",
    "Life": "Breath of Life",
    "Poetry": "Breath of Poetry",
}

NICHE_CATEGORY = {
    "DS": "28",   # Science & Technology
    "Life": "22", # People & Blogs
    "Poetry": "22",
}

SHORTS_DIR = BASE_DIR / "assets" / "video" / "edited" / "shorts"


# ── Niche detection ───────────────────────────────────────────────────────────
def detect_niche(slug: str) -> str:
    for niche, markers in NICHE_MARKERS.items():
        if any(m in slug for m in markers):
            return niche
    sys.exit(
        f"ERROR: Cannot detect niche from slug '{slug}'.\n"
        "Expected one of: data_science_tech, life_self_dev, poetry_quotes"
    )


# ── Slot time calculation ─────────────────────────────────────────────────────
def slot_publish_times(year: int, week: int) -> dict[int, str]:
    """Return {slot: ISO8601_string} for 14 slots, Mon–Sun, 10 AM + 8 PM IST."""
    times = {}
    for day_offset in range(7):
        d = datetime.date.fromisocalendar(year, week, day_offset + 1)
        for hour, slot_in_day in [(10, 0), (20, 1)]:
            slot = day_offset * 2 + slot_in_day
            times[slot] = f"{d}T{hour:02d}:00:00+05:30"
    return times


def parse_publish_week(value: str) -> tuple[int, int]:
    """Parse '2026-W25' → (2026, 25)."""
    m = re.fullmatch(r"(\d{4})-W(\d{1,2})", value)
    if not m:
        sys.exit(f"ERROR: --publish-week must be YYYY-Wnn format, got '{value}'")
    return int(m.group(1)), int(m.group(2))


# ── File discovery ────────────────────────────────────────────────────────────
def discover_shorts(slug: str, week: str, niche: str) -> dict[int, dict]:
    """
    Scan shorts dir and animations dir for clip files belonging to this slug.
    Returns {slot: {path, source}} with no conflicts.
    """
    content_date = slug[:10]
    markers = NICHE_MARKERS[niche]
    found: dict[int, dict] = {}

    # Clip shorts: assets/video/edited/shorts/
    if SHORTS_DIR.exists():
        for f in sorted(SHORTS_DIR.iterdir()):
            if f.suffix != ".mp4":
                continue
            name = f.name
            if content_date not in name:
                continue
            if not any(m in name for m in markers):
                continue
            m = re.search(r"_(?:yt_)?short_(\d+)\.mp4$", name)
            if not m:
                continue
            slot = int(m.group(1))
            if slot in found:
                sys.exit(
                    f"ERROR: Slot {slot} conflict — "
                    f"'{found[slot]['path'].name}' and '{f.name}' both match. Resolve manually."
                )
            found[slot] = {"path": f, "source": "clip"}

    # Remotion reels: output/animations/{week}/
    anim_dir = BASE_DIR / "output" / "animations" / week
    if anim_dir.exists():
        for f in sorted(anim_dir.iterdir()):
            if f.suffix != ".mp4":
                continue
            name = f.name
            if content_date not in name:
                continue
            if not any(m in name for m in markers):
                continue
            m = re.search(r"_s(\d+)\.mp4$", name)
            if not m:
                continue
            slot = int(m.group(1))
            if slot in found:
                sys.exit(
                    f"ERROR: Slot {slot} conflict — "
                    f"clip '{found[slot]['path'].name}' and remotion '{f.name}' both claim it."
                )
            found[slot] = {"path": f, "source": "remotion"}

    return found


# ── Metadata ──────────────────────────────────────────────────────────────────
def load_shorts_metadata(slug: str, week: str) -> dict | list:
    path = BASE_DIR / "content" / "derivatives" / week / slug / "youtube_shorts_metadata.json"
    if not path.exists():
        sys.exit(f"ERROR: No shorts metadata at {path.relative_to(BASE_DIR)}")
    return json.loads(path.read_text())


def load_schedule(slug: str, week: str) -> dict:
    path = BASE_DIR / "content" / "derivatives" / week / slug / "schedule.json"
    return json.loads(path.read_text()) if path.exists() else {}


def get_slot_meta(meta: dict | list, slot: int) -> dict:
    if isinstance(meta, dict) and "shorts" in meta:
        shorts = meta["shorts"]
        if slot >= len(shorts):
            sys.exit(
                f"ERROR: No metadata for slot {slot} — "
                f"shorts array has {len(shorts)} entries (0–{len(shorts) - 1})."
            )
        return shorts[slot]
    if isinstance(meta, list):
        if slot >= len(meta):
            sys.exit(f"ERROR: No metadata for slot {slot} — array has {len(meta)} entries.")
        return meta[slot]
    # Legacy single-object
    if slot > 0:
        sys.exit(
            f"ERROR: Legacy single-object metadata only covers slot 0, not slot {slot}. "
            "Convert to wrapper format {\"long_form_url\": \"\", \"shorts\": [...]}."
        )
    return meta


def schedule_publish_at(schedule: dict, slot: int) -> str | None:
    for entry in schedule.get("shorts", []):
        if entry.get("slot") == slot:
            return entry.get("publish_at")
    return None


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch-upload YouTube Shorts for a content slug.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--slug", required=True,
                        help="Derivatives slug (date_niche_title format)")
    parser.add_argument("--publish-week", default=None, metavar="YYYY-Wnn",
                        help="Override publish times with computed week times (Mon–Sun, 10AM+8PM IST)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print plan, upload nothing")
    parser.add_argument("--pin-comment", action="store_true",
                        help="Post long-form URL as comment after each upload")
    parser.add_argument("--slots", default=None,
                        help="Comma-separated slot numbers (default: all found)")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Skip confirmation prompt")
    args = parser.parse_args()

    load_dotenv(BASE_DIR / ".env")

    slug = args.slug
    week = get_iso_week(slug[:10])
    niche = detect_niche(slug)

    # Discover files
    all_found = discover_shorts(slug, week, niche)
    if not all_found:
        sys.exit(
            f"ERROR: No short clips found for slug '{slug}'\n"
            f"  Content date: {slug[:10]}, Niche: {niche}\n"
            f"  Searched: {SHORTS_DIR}\n"
            f"  Expected filename containing '{slug[:10]}' and niche marker."
        )

    # Filter by --slots
    if args.slots:
        requested = {int(s.strip()) for s in args.slots.split(",") if s.strip()}
        missing = requested - set(all_found.keys())
        if missing:
            sys.exit(f"ERROR: Requested slots {sorted(missing)} not found. Found slots: {sorted(all_found.keys())}")
        found = {k: v for k, v in all_found.items() if k in requested}
    else:
        found = all_found

    # Load metadata and schedule
    meta = load_shorts_metadata(slug, week)
    long_form_url = meta.get("long_form_url", "") if isinstance(meta, dict) else ""
    schedule = load_schedule(slug, week)

    # Build publish time map
    pub_times: dict[int, str] = {}
    if args.publish_week:
        year, wnum = parse_publish_week(args.publish_week)
        pub_times = slot_publish_times(year, wnum)

    channel_name = NICHE_CHANNEL[niche]
    category_id = NICHE_CATEGORY[niche]

    # Build upload plan
    plan = []
    for slot in sorted(found.keys()):
        file_info = found[slot]
        s_meta = get_slot_meta(meta, slot)

        title = s_meta.get("title", f"{slug} #{slot}")
        description = s_meta.get("description", "")
        tags = s_meta.get("tags", [])

        if long_form_url:
            description = description.rstrip() + f"\n\nFull video: {long_form_url}"
        if "#Shorts" not in description and "#shorts" not in description:
            description = description.rstrip() + "\n#Shorts"

        if args.publish_week:
            if slot not in pub_times:
                sys.exit(f"ERROR: Slot {slot} exceeds max slot 13 for 7-day schedule.")
            publish_at = pub_times[slot]
        else:
            publish_at = schedule_publish_at(schedule, slot)
            if not publish_at:
                sys.exit(
                    f"ERROR: No publish_at for slot {slot} in schedule.json.\n"
                    "Use --publish-week YYYY-Wnn to override with computed times."
                )

        plan.append({
            "slot": slot,
            "file": file_info["path"],
            "source": file_info["source"],
            "title": title,
            "description": description,
            "tags": tags,
            "publish_at": publish_at,
        })

    # Print plan header
    print(f"\nSlug:     {slug}")
    print(f"Niche:    {niche} → {channel_name}")
    print(f"Week:     {week}")
    print(f"Uploads:  {len(plan)} shorts")
    print(f"LF URL:   {long_form_url or '[empty — fill in youtube_shorts_metadata.json]'}")
    print()

    for item in plan:
        prefix = "[DRY RUN] " if args.dry_run else ""
        print(f"  {prefix}Slot {item['slot']:02d}  {item['publish_at']}  [{item['source']:8s}]  {item['file'].name}")
        print(f"           {item['title'][:90]}")
    print()

    if args.dry_run:
        print("Dry run complete. Re-run without --dry-run to upload.")
        return

    if not args.yes:
        confirm = input(f"Upload {len(plan)} shorts to '{channel_name}'? [y/N] ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            return

    channel = resolve_channel(channel_name)
    creds = get_credentials(channel["id"])
    youtube = build("youtube", "v3", credentials=creds)

    for item in plan:
        print(f"\n── Slot {item['slot']:02d} {'─' * 50}")
        try:
            url = upload_video(
                youtube=youtube,
                video_path=item["file"],
                title=item["title"],
                description=item["description"],
                tags=item["tags"],
                category_id=category_id,
                privacy="public",
                publish_at=item["publish_at"],
            )
        except HttpError as e:
            sys.exit(f"ERROR: YouTube API error on slot {item['slot']}: {e}")

        print(f"URL:       {url}")
        print(f"Scheduled: {item['publish_at']}")

        if args.pin_comment and long_form_url:
            vid_m = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
            if vid_m:
                video_id = vid_m.group(1)
                comment_id = post_comment(youtube, video_id, f"Watch the full video: {long_form_url}")
                if comment_id:
                    print(f"[comment] posted: Watch the full video: {long_form_url}")
                    print(f"[comment] PIN manually → https://studio.youtube.com/video/{video_id}/comments")

    print(f"\nDone. {len(plan)} shorts uploaded to '{channel_name}'.")


if __name__ == "__main__":
    main()
