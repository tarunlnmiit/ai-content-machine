#!/usr/bin/env python3
"""
Read all derivative files from content/derivatives/*/ and stage every postable
platform into data/scheduling.db for the scheduler.py daemon (direct API).

Auto-published by the daemon (one stage step → daemon fires everything):
  LinkedIn  — text post, Tue 8am / Thu 12pm IST (employer cleared)
  Threads   — native text post, engagement window (no media needed)
  Instagram — image/carousel/reel; requires a PUBLIC media_url (Graph API ingests
              from a URL, not local bytes). Staged only when a media_url is known;
              otherwise skipped with a warning (host the asset first).
  Facebook  — usually mirrors from IG; direct FB staging optional.

Twitter was dropped from the pipeline. No Metricool/Publer CSV.

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


# Per-platform engagement-window slots (weekday 0=Mon, hour, minute IST).
# The scheduler daemon fires each row at its scheduled_at.
LINKEDIN_SLOTS = [(1, 8, 0), (3, 12, 0)]      # Tue 8am, Thu 12pm
THREADS_SLOTS = [(0, 19, 0), (3, 19, 0)]      # Mon/Thu 7pm
INSTAGRAM_SLOTS = [(0, 16, 0), (3, 10, 0)]    # Mon 4pm, Thu 10am


def slug_already_loaded(conn: sqlite3.Connection, slug: str, platform: str) -> bool:
    row = conn.execute(
        "SELECT id FROM posts WHERE slug=? AND platform=? AND status IN ('pending','posted')",
        (slug, platform),
    ).fetchone()
    return row is not None


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
        ("linkedin", text, media_path, scheduled_at, "pending",
         json.dumps({"kind": "image" if media_path else "text"}), slug),
    )
    print(f"  [queued] linkedin/{slug} — at {scheduled_at}" + (f" + image" if media_path else ""))


def insert_threads(conn: sqlite3.Connection, slug: str, txt_path: Path, slot_index: int):
    """Stage a Threads native text post (no media needed — publishes immediately)."""
    if slug_already_loaded(conn, slug, "threads"):
        print(f"  [skip] threads/{slug} already in DB")
        return
    text = txt_path.read_text(encoding="utf-8").strip()
    if not text:
        return
    weekday, hour, minute = THREADS_SLOTS[slot_index % len(THREADS_SLOTS)]
    scheduled_at = next_weekday(weekday, hour, minute).isoformat()
    conn.execute(
        """INSERT INTO posts (platform, content_text, scheduled_at, status,
           metadata_json, slug) VALUES (?,?,?,?,?,?)""",
        ("threads", text, scheduled_at, "pending", json.dumps({"kind": "text"}), slug),
    )
    print(f"  [queued] threads/{slug} — at {scheduled_at}")


def _instagram_media_url(slug: str) -> tuple[str, str] | None:
    """Return (kind, media_url) for an IG static post if a public URL is known.

    Reads schedule.json's social.ig_media_url / ig_media_urls (populated by
    populate_image_urls_from_gdrive.py). Returns None when no public URL exists —
    the IG Graph API ingests from a URL, so we cannot stage IG without one.
    """
    date_str = slug[:10]
    week = get_iso_week(date_str)
    sched = REPO / "content" / "derivatives" / week / slug / "schedule.json"
    if not sched.exists():
        return None
    try:
        social = json.loads(sched.read_text(encoding="utf-8")).get("social", {})
    except (ValueError, OSError):
        return None
    urls = social.get("ig_media_urls")
    if isinstance(urls, list) and len(urls) >= 2:
        return ("carousel", urls)
    single = social.get("ig_media_url")
    if single:
        return ("image", single)
    return None


def insert_instagram(conn: sqlite3.Connection, slug: str, txt_path: Path, slot_index: int):
    """Stage an Instagram static post — only if a public media_url is available."""
    if slug_already_loaded(conn, slug, "instagram"):
        print(f"  [skip] instagram/{slug} already in DB")
        return
    caption = txt_path.read_text(encoding="utf-8").strip()
    if not caption:
        return
    media = _instagram_media_url(slug)
    if not media:
        print(f"  [skip] instagram/{slug} — no public media_url "
              "(run populate_image_urls_from_gdrive.py; IG API needs a hosted URL)")
        return
    kind, url = media
    meta = {"kind": kind}
    meta["media_urls" if kind == "carousel" else "media_url"] = url
    weekday, hour, minute = INSTAGRAM_SLOTS[slot_index % len(INSTAGRAM_SLOTS)]
    scheduled_at = next_weekday(weekday, hour, minute).isoformat()
    conn.execute(
        """INSERT INTO posts (platform, content_text, scheduled_at, status,
           metadata_json, slug) VALUES (?,?,?,?,?,?)""",
        ("instagram", caption, scheduled_at, "pending", json.dumps(meta), slug),
    )
    print(f"  [queued] instagram/{slug} ({kind}) — at {scheduled_at}")


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

        threads_file = slug_dir / "threads_post.txt"
        if threads_file.exists():
            insert_threads(conn, slug, threads_file, i)

        instagram_file = slug_dir / "instagram_caption.txt"
        if instagram_file.exists():
            insert_instagram(conn, slug, instagram_file, i)

    conn.commit()

    # Summary
    total = conn.execute("SELECT COUNT(*) FROM posts WHERE status='pending'").fetchone()[0]
    by_platform = conn.execute(
        "SELECT platform, COUNT(*) FROM posts WHERE status='pending' GROUP BY platform"
    ).fetchall()
    conn.close()

    print(f"\nDB: {total} pending post(s) in scheduling.db")
    for platform, n in by_platform:
        print(f"  {platform}: {n}")
    print("  Facebook → mirrors from Instagram on publish (no separate staging).")

    # YouTube Shorts upload script
    shorts_script = build_shorts_upload_script(slugs)
    if shorts_script:
        print(f"YT Shorts script  : {shorts_script.relative_to(REPO)}")
        print("  → Run on Friday after recording: bash output/scheduled/upload_shorts.sh")
        print("  → Ensure reel video files exist at assets/video/edited/{slug}_reel.mp4")
    else:
        print("YT Shorts script  : skipped (no youtube_shorts_metadata.json found)")

    print("\nNext: start APScheduler daemon (LinkedIn + Instagram + Threads):")
    print("  nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &")
    print("  (IG needs Meta tokens — see docs/one-time-platform-setup.md)")


if __name__ == "__main__":
    main()
