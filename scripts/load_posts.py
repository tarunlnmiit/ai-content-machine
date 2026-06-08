#!/usr/bin/env python3
"""
Read all derivative files from content/derivatives/*/
Insert scheduled posts into data/scheduling.db.
Generate output/scheduled/publer_import.csv for Instagram + Facebook + Threads (via Publer).

Schedule logic:
  LinkedIn posts   — Tuesday 8am IST, Thursday 12pm IST  (direct API via scheduler.py)
  Twitter threads  — manual for now (copy content/derivatives/{slug}/twitter_thread.txt)
  Instagram        — Wednesday 6pm IST, Friday 10am IST  (via Publer CSV)
  Facebook         — Wednesday 7pm IST, Friday 11am IST  (via Publer CSV)
  Threads          — Wednesday 8pm IST, Friday 12pm IST  (via Publer CSV)

Run after repurpose_blog.py has produced derivatives for the week.
Safe to re-run — skips slugs already in DB with status='pending' or 'posted'.
"""

import csv
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

from lib.schedule_calc import next_weekday, get_iso_week

REPO = Path(__file__).parent.parent
DB_PATH = REPO / "data" / "scheduling.db"
load_dotenv(REPO / ".env")

# IST = UTC+5:30
IST = timezone(timedelta(hours=5, minutes=30))


# LinkedIn slots — direct API via scheduler.py (Tue 8am, Thu 12pm IST)
LINKEDIN_SLOTS = [(1, 8, 0), (3, 12, 0)]


def slug_already_loaded(conn: sqlite3.Connection, slug: str, platform: str) -> bool:
    row = conn.execute(
        "SELECT id FROM posts WHERE slug=? AND platform=? AND status IN ('pending','posted')",
        (slug, platform),
    ).fetchone()
    return row is not None


def parse_twitter_thread(txt_path: Path) -> list[str]:
    """Split on blank lines — each block = one tweet."""
    text = txt_path.read_text(encoding="utf-8").strip()
    return [b.strip() for b in text.split("\n\n") if b.strip()]


def insert_twitter(conn: sqlite3.Connection, slug: str, txt_path: Path, slot_index: int):
    if slug_already_loaded(conn, slug, "twitter"):
        print(f"  [skip] twitter/{slug} already in DB")
        return

    tweets = parse_twitter_thread(txt_path)
    if not tweets:
        print(f"  [skip] twitter/{slug} — empty thread file")
        return

    weekday, hour, minute = SCHEDULE["twitter"][slot_index % len(SCHEDULE["twitter"])]
    scheduled_at = next_weekday(weekday, hour, minute).isoformat()

    # Insert hook tweet as main row; rest as thread children
    parent_id = None
    for i, tweet in enumerate(tweets):
        row = conn.execute(
            """INSERT INTO posts (platform, content_text, scheduled_at, status, thread_parent_id,
               metadata_json, slug)
               VALUES (?,?,?,'pending',?,?,?)""",
            (
                "twitter",
                tweet,
                scheduled_at,
                parent_id,
                json.dumps({"tweet_index": i, "total_tweets": len(tweets)}),
                slug,
            ),
        )
        if i == 0:
            parent_id = row.lastrowid

    print(f"  [queued] twitter/{slug} — {len(tweets)} tweets at {scheduled_at}")


def insert_linkedin(conn: sqlite3.Connection, slug: str, txt_path: Path, slot_index: int):
    if slug_already_loaded(conn, slug, "linkedin"):
        print(f"  [skip] linkedin/{slug} already in DB")
        return

    text = txt_path.read_text(encoding="utf-8").strip()
    if not text:
        return

    # Check for matching thumbnail
    thumb = REPO / "assets" / "thumbnails" / f"{slug}_thumb.png"
    media_path = str(thumb.relative_to(REPO)) if thumb.exists() else None

    weekday, hour, minute = LINKEDIN_SLOTS[slot_index % len(LINKEDIN_SLOTS)]
    scheduled_at = next_weekday(weekday, hour, minute).isoformat()

    conn.execute(
        """INSERT INTO posts (platform, content_text, media_path, scheduled_at, status,
           metadata_json, slug)
           VALUES (?,?,?,?,?,?,?)""",
        ("linkedin", text, media_path, scheduled_at, "pending", json.dumps({}), slug),
    )
    print(f"  [queued] linkedin/{slug} — at {scheduled_at}" + (f" + image" if media_path else ""))


# Metricool CSV — exact column order from official template (do not reorder/add/remove)
METRICOOL_FIELDS = [
    "Text", "Date", "Time", "Draft",
    "Facebook", "Twitter/X", "LinkedIn", "GBP", "Instagram", "Pinterest",
    "TikTok", "Youtube", "Threads", "Bluesky",
    "Picture Url 1", "Picture Url 2", "Picture Url 3", "Picture Url 4", "Picture Url 5",
    "Picture Url 6", "Picture Url 7", "Picture Url 8", "Picture Url 9", "Picture Url 10",
    "Alt text picture 1", "Alt text picture 2", "Alt text picture 3", "Alt text picture 4",
    "Alt text picture 5", "Alt text picture 6", "Alt text picture 7", "Alt text picture 8",
    "Alt text picture 9", "Alt text picture 10",
    "Document title", "Shortener", "Video Thumbnail Url", "Video Cover Frame",
    "Twitter/X Can reply", "Twitter/X Type", "Twitter/X Poll Duration minutes",
    "Twitter/X Poll Option 1", "Twitter/X Poll Option 2", "Twitter/X Poll Option 3", "Twitter/X Poll Option 4",
    "Pinterest Board", "Pinterest Pin Title", "Pinterest Pin Link", "Pinterest Pin New Format",
    "Instagram Post Type", "Instagram Show Reel On Feed",
    "Youtube Video Title", "Youtube Video Type", "Youtube Video Privacy",
    "Youtube video for kids", "Youtube Video Category", "Youtube Video Tags", "Youtube playlist",
    "GBP Post Type", "Facebook Post Type", "Facebook Title", "First Comment Text",
    "TikTok Title", "TikTok disable comments", "TikTok disable duet", "TikTok disable stitch",
    "TikTok Post Privacy", "TikTok Branded Content", "TikTok Your Brand", "TikTok Auto Add Music",
    "TikTok Photo Cover Index", "TikTok musicId", "TikTok music title", "TikTok music author",
    "TikTok music previewUrl", "TikTok music thumbnailUrl", "TikTok music soundVolume",
    "TikTok music originalVolume", "TikTok music startMillis", "TikTok music endMillis",
    "TikTok Ai generated content",
    "LinkedIn Type", "LinkedIn Poll Question",
    "LinkedIn Poll Option 1", "LinkedIn Poll Option 2", "LinkedIn Poll Option 3", "LinkedIn Poll Option 4",
    "LinkedIn Poll Duration", "LinkedIn Show link preview", "LinkedIn Images as Carousel",
    "Threads Reply Control", "Threads Is Spoiler", "Threads Post Type",
    "Brand name",
]

# Per-niche canonical schedule (weekday 0=Mon, times IST)
NICHE_SCHEDULE = {
    "life":   {"ig_fb": (1,  8, 0), "threads": (1, 20, 0)},   # Tue 8 AM / 8 PM
    "ds":     {"ig_fb": (2,  8, 0), "threads": (2, 20, 0)},   # Wed 8 AM / 8 PM
    "poetry": {"ig_fb": (4, 10, 0), "threads": (4, 12, 0)},   # Fri 10 AM / 12 PM
}

# Metricool brand names (must match exactly what's in Metricool)
BRAND_NAMES = {
    "mistakenlyhuman": "mistakenlyhuman",    # Life + Poetry
    "breathofds":      "Breath of Data Science",
}


def _metricool_row(
    text: str,
    scheduled_dt: datetime,
    instagram: bool = False,
    facebook: bool = False,
    threads: bool = False,
    ig_post_type: str = "POST",
    picture_url: str = "",
    brand: str = "",
) -> dict:
    row = {f: "" for f in METRICOOL_FIELDS}
    row["Text"] = text
    row["Date"] = scheduled_dt.strftime("%Y-%m-%d")
    row["Time"] = scheduled_dt.strftime("%H:%M:%S")
    row["Draft"] = "FALSE"
    row["Facebook"]  = "TRUE" if facebook  else "FALSE"
    row["Instagram"] = "TRUE" if instagram else "FALSE"
    row["Threads"]   = "TRUE" if threads   else "FALSE"
    row["Twitter/X"] = "FALSE"
    row["LinkedIn"]  = "FALSE"
    row["GBP"] = "FALSE"
    row["Pinterest"] = "FALSE"
    row["TikTok"]    = "FALSE"
    row["Youtube"]   = "FALSE"
    row["Bluesky"]   = "FALSE"
    if picture_url:
        row["Picture Url 1"] = picture_url
    if instagram or facebook:
        row["Instagram Post Type"] = ig_post_type
    row["Brand name"] = brand
    return row


def _write_metricool_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=METRICOOL_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _niche_from_slug(slug: str) -> str:
    """Returns 'ds', 'life', or 'poetry' based on slug contents."""
    s = slug.lower()
    if "_data_science_tech_" in s:
        return "ds"
    if "_poetry_quotes_" in s:
        return "poetry"
    return "life"


def _ig_post_type_from_caption(caption_text: str) -> str:
    first = caption_text.splitlines()[0].lower() if caption_text else ""
    if "reel" in first:
        return "REEL"
    if "story" in first:
        return "STORY"
    return "POST"


def build_metricool_csvs(slugs_data: list[str]) -> tuple[Path, Path]:
    """
    Generate two Metricool bulk import CSVs, one per brand/account.

    Account 1 — mistakenlyhuman (Life + Poetry): IG + FB + Threads
    Account 2 — Breath of Data Science (DS only): IG + FB + Threads

    LinkedIn is handled by scheduler.py direct API — not in Metricool CSV.
    Rows use Brand name column so both can be imported from a single Metricool workspace
    if the user upgrades; until then import each CSV in the matching brand workspace.

    Images require a publicly accessible URL. Local thumbnail paths are skipped —
    add image URLs manually in Metricool after import, or host via Google Drive/Dropbox.

    Schedule times are read from schedule.json if present, otherwise computed via next_weekday().
    """
    out_dir = REPO / "output" / "scheduled"
    out_dir.mkdir(parents=True, exist_ok=True)

    mh_rows: list[dict] = []   # mistakenlyhuman: Life + Poetry
    ds_rows: list[dict] = []   # breathofds: DS

    for slug in slugs_data:
        niche = _niche_from_slug(slug)
        # Find slug_dir under the correct week folder
        date_str = slug[:10]  # Extract YYYY-MM-DD from slug
        week = get_iso_week(date_str)
        slug_dir = REPO / "content" / "derivatives" / week / slug
        brand = BRAND_NAMES["breathofds"] if niche == "ds" else BRAND_NAMES["mistakenlyhuman"]
        target = ds_rows if niche == "ds" else mh_rows

        # Try to read schedule.json; fall back to next_weekday()
        schedule_file = slug_dir / "schedule.json"
        if schedule_file.exists():
            try:
                sched_data = json.loads(schedule_file.read_text(encoding="utf-8"))
                ig_publish_at = sched_data.get("social", {}).get("ig_fb_publish_at")
                thr_publish_at = sched_data.get("social", {}).get("threads_publish_at")
                ig_dt = datetime.fromisoformat(ig_publish_at) if ig_publish_at else None
                thr_dt = datetime.fromisoformat(thr_publish_at) if thr_publish_at else None
            except (json.JSONDecodeError, ValueError):
                sched_data = None
                ig_dt = None
                thr_dt = None
        else:
            sched_data = None
            ig_dt = None
            thr_dt = None

        # Fallback: compute via next_weekday() if schedule.json not available
        if not sched_data:
            sched = NICHE_SCHEDULE.get(niche, NICHE_SCHEDULE["life"])
            weekday, hour, minute = sched["ig_fb"]
            ig_dt = next_weekday(weekday, hour, minute, week_offset=1)
            weekday, hour, minute = sched["threads"]
            thr_dt = next_weekday(weekday, hour, minute, week_offset=1)

        # Social posts publish ONE WEEK after the long-form (week_offset=1)
        # ── IG + FB row
        ig_path = slug_dir / "instagram_caption.txt"
        if ig_path.exists() and ig_dt:
            caption = ig_path.read_text(encoding="utf-8").strip()
            clean = "\n".join(
                l for l in caption.splitlines()
                if not l.startswith("Format:") and not l.startswith("Why:")
            ).strip()
            target.append(_metricool_row(
                text=clean,
                scheduled_dt=ig_dt,
                instagram=True,
                facebook=True,
                ig_post_type=_ig_post_type_from_caption(caption),
                brand=brand,
            ))

        # ── Threads row
        thr_path = slug_dir / "threads_post.txt"
        if thr_path.exists() and thr_dt:
            thr_text = thr_path.read_text(encoding="utf-8").strip()
            target.append(_metricool_row(
                text=thr_text,
                scheduled_dt=thr_dt,
                threads=True,
                brand=brand,
            ))

    mh_path = out_dir / "metricool_mistakenlyhuman.csv"
    ds_path = out_dir / "metricool_breathofds.csv"
    _write_metricool_csv(mh_path, mh_rows)
    _write_metricool_csv(ds_path, ds_rows)
    return mh_path, ds_path


def build_shorts_upload_script(slugs: list[str]) -> Path | None:
    """
    Generate output/scheduled/upload_shorts.sh with pre-filled upload_youtube.py --shorts
    commands for each slug that has youtube_shorts_metadata.json.

    Niche is inferred from slug prefix (ds|life|poetry) → channel name.
    """
    NICHE_TO_CHANNEL = {
        "ds":     "Breath of Data Science",
        "life":   "Breath of Life",
        "poetry": "Breath of Poetry",
    }
    DEFAULT_CHANNEL = "Breath of Data Science"

    lines = ["#!/bin/bash", "# YouTube Shorts upload commands — generated by load_posts.py", "# Run on Friday after recording.", ""]

    found = []
    for slug in slugs:
        meta_path = REPO / "content" / "derivatives" / slug / "youtube_shorts_metadata.json"
        if not meta_path.exists():
            continue

        # Infer channel from slug
        channel = DEFAULT_CHANNEL
        for prefix, ch in NICHE_TO_CHANNEL.items():
            if f"-{prefix}-" in slug or slug.startswith(f"{prefix}-"):
                channel = ch
                break

        # Infer reel video path — same file used for IG reel
        reel_path = f"assets/video/edited/{slug}_reel.mp4"

        lines.append(f"# {slug}")
        lines.append(
            f'python3 scripts/upload_youtube.py --shorts --slug "{slug}" '
            f'--channel "{channel}" '
            f'--video "{reel_path}" '
            f'--category 22'
        )
        lines.append("")
        found.append(slug)

    if not found:
        return None

    out_path = REPO / "output" / "scheduled" / "upload_shorts.sh"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    out_path.chmod(0o755)
    return out_path


def main():
    if not DB_PATH.exists():
        sys.exit(f"DB not found: {DB_PATH}\nRun: python3 scripts/db_setup.py first")

    deriv_dir = REPO / "content" / "derivatives"
    if not deriv_dir.exists():
        sys.exit("content/derivatives/ not found — run repurpose_blog.py first")

    # Collect slugs from week-organized subfolders (2026-Wnn/slug/)
    slugs = []
    for week_folder in sorted(deriv_dir.iterdir()):
        if week_folder.is_dir() and week_folder.name[0].isdigit():  # Week folders like 2026-W21
            for slug_folder in sorted(week_folder.iterdir()):
                if slug_folder.is_dir():
                    slugs.append(slug_folder.name)

    if not slugs:
        sys.exit("No derivative folders found.")

    print(f"Loading {len(slugs)} slug(s) into scheduling.db ...\n")

    conn = sqlite3.connect(DB_PATH)

    for i, slug in enumerate(slugs):
        # Find slug_dir under the correct week folder
        date_str = slug[:10]  # Extract YYYY-MM-DD from slug
        week = get_iso_week(date_str)
        slug_dir = deriv_dir / week / slug
        print(f"[{i+1}/{len(slugs)}] {slug}")

        linkedin_file = slug_dir / "linkedin_post.txt"
        if linkedin_file.exists():
            insert_linkedin(conn, slug, linkedin_file, i)

    conn.commit()

    # Summary
    total = conn.execute("SELECT COUNT(*) FROM posts WHERE status='pending'").fetchone()[0]
    conn.close()

    print(f"\nDB: {total} pending LinkedIn post(s) in scheduling.db")

    # Metricool CSVs — one per brand/account
    mh_csv, ds_csv = build_metricool_csvs(slugs)
    print(f"Metricool [mistakenlyhuman — Life + Poetry] : {mh_csv.relative_to(REPO)}")
    print(f"Metricool [Breath of Data Science — DS]    : {ds_csv.relative_to(REPO)}")
    print("  → Import each CSV in the matching brand workspace in Metricool")
    print("  ⚠ Images: add public URLs manually (Google Drive/Dropbox) — local paths not supported")

    # YouTube Shorts upload script
    shorts_script = build_shorts_upload_script(slugs)
    if shorts_script:
        print(f"YT Shorts script  : {shorts_script.relative_to(REPO)}")
        print("  → Run on Friday after recording: bash output/scheduled/upload_shorts.sh")
        print("  → Ensure reel video files exist at assets/video/edited/{slug}_reel.mp4")
    else:
        print("YT Shorts script  : skipped (no youtube_shorts_metadata.json found)")

    print("\nNext: start APScheduler daemon (LinkedIn only):")
    print("  nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &")


if __name__ == "__main__":
    main()
