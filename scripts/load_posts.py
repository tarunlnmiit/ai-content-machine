#!/usr/bin/env python3
"""
Read all derivative files from content/derivatives/*/
Insert LinkedIn posts into data/scheduling.db for the scheduler daemon (direct API).

No Metricool, no Publer, no aggregator CSV — Instagram / Facebook / Threads are posted
MANUALLY (see docs/weekly-runner.md Step 22). This script only stages LinkedIn for the
scheduler/API path, which itself stays dormant until employer clearance.

Schedule logic:
  LinkedIn posts   — Tuesday 8am IST, Thursday 12pm IST  (direct API via scheduler.py)
  Twitter threads  — manual (post content/derivatives/{slug}/twitter_thread.md)
  Instagram / FB / Threads — manual, in-app, in the niche's engagement window

Also emits output/scheduled/upload_shorts.sh — pre-filled YouTube Shorts upload commands.

Run after repurpose_blog.py has produced derivatives for the week.
Safe to re-run — skips slugs already in DB with status='pending' or 'posted'.
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

from lib.schedule_calc import next_weekday, get_iso_week

def _prompt_user(prompt_text: str) -> str:
    """Prompt user interactively if stdin is a TTY, otherwise return empty string."""
    if not sys.stdin.isatty():
        return ""
    try:
        return input(prompt_text).strip()
    except EOFError:
        return ""

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

    # Check for LinkedIn image in social_posts
    date_str = slug[:10]
    week = get_iso_week(date_str)
    li_img = REPO / "assets" / "social_posts" / week / f"{slug}_linkedin.png"
    media_path = str(li_img.relative_to(REPO)) if li_img.exists() else None

    weekday, hour, minute = LINKEDIN_SLOTS[slot_index % len(LINKEDIN_SLOTS)]
    scheduled_at = next_weekday(weekday, hour, minute).isoformat()

    conn.execute(
        """INSERT INTO posts (platform, content_text, media_path, scheduled_at, status,
           metadata_json, slug)
           VALUES (?,?,?,?,?,?,?)""",
        ("linkedin", text, media_path, scheduled_at, "pending", json.dumps({}), slug),
    )
    print(f"  [queued] linkedin/{slug} — at {scheduled_at}" + (f" + image" if media_path else ""))


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
    parser = argparse.ArgumentParser(description="Load social posts from derivatives into scheduling.db")
    parser.add_argument(
        "--week",
        type=str,
        default=None,
        help="Week(s) to load (e.g., '2026-W23' or '2026-W22,2026-W23'). Omit to load all weeks.",
    )
    args = parser.parse_args()

    if not DB_PATH.exists():
        sys.exit(f"DB not found: {DB_PATH}\nRun: python3 scripts/db_setup.py first")

    deriv_dir = REPO / "content" / "derivatives"
    if not deriv_dir.exists():
        sys.exit("content/derivatives/ not found — run repurpose_blog.py first")

    # Parse target weeks if specified
    target_weeks = set()
    if args.week:
        target_weeks = set(w.strip() for w in args.week.split(","))

    # Collect slugs from week-organized subfolders (2026-Wnn/slug/)
    slugs = []
    for week_folder in sorted(deriv_dir.iterdir()):
        if week_folder.is_dir() and week_folder.name[0].isdigit():  # Week folders like 2026-W21
            if target_weeks and week_folder.name not in target_weeks:
                continue
            for slug_folder in sorted(week_folder.iterdir()):
                if slug_folder.is_dir():
                    slugs.append(slug_folder.name)

    if not slugs:
        sys.exit("No derivative folders found.")

    week_label = f"week(s) {args.week}" if args.week else "all weeks"
    print(f"Loading {len(slugs)} slug(s) from {week_label} into scheduling.db ...\n")

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
    print("  Instagram / Facebook / Threads → post manually (no Metricool/Publer CSV).")

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
