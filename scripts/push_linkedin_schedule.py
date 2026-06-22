#!/usr/bin/env python3
"""
Push pending LinkedIn posts from scheduling.db to LinkedIn's native scheduler.

LinkedIn holds and fires each post at the exact scheduled_at time — visible
immediately in LinkedIn Creator Studio. Our daemon only needs to fire comments
after the post goes live.

Status flow:
  pending → (this script) → li_native_scheduled  [post visible in LinkedIn]
  li_native_scheduled → (scheduler.py at scheduled_at + 5 min) → posted  [comments fired]

Usage:
    python3 scripts/push_linkedin_schedule.py              # all pending LinkedIn posts
    python3 scripts/push_linkedin_schedule.py --week 2026-W22
    python3 scripts/push_linkedin_schedule.py --dry-run
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO = Path(__file__).parent.parent
DB_PATH = REPO / "data" / "scheduling.db"
load_dotenv(REPO / ".env")

MIN_SCHEDULE_OFFSET_MS = 10 * 60 * 1000  # LinkedIn requires >= 10 min from now


def _iso_to_unix_ms(iso: str) -> int:
    dt = datetime.fromisoformat(iso)
    return int(dt.timestamp() * 1000)


def _now_unix_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def push_post(row: dict, token: str, urn: str, dry_run: bool) -> bool:
    """Push one pending LinkedIn row to LinkedIn native scheduling. Returns True on success."""
    sys.path.insert(0, str(REPO / "scripts"))
    from post_linkedin import post_text, post_document, upload_image, get_credentials

    post_id = row["id"]
    slug = row["slug"]
    text = row["content_text"]
    media_path = row["media_path"]
    scheduled_at = row["scheduled_at"]
    meta = json.loads(row["metadata_json"] or "{}")
    kind = meta.get("kind", "text")

    scheduled_unix_ms = _iso_to_unix_ms(scheduled_at)
    now_ms = _now_unix_ms()

    # LinkedIn requires >= 10 min in the future.
    if scheduled_unix_ms < now_ms + MIN_SCHEDULE_OFFSET_MS:
        scheduled_unix_ms = now_ms + MIN_SCHEDULE_OFFSET_MS
        print(f"  [warn] {slug}: scheduled_at in past — bumped to +10 min from now")

    print(f"  [{kind}] {slug}")
    print(f"    scheduled: {scheduled_at}")

    if dry_run:
        print("    → dry-run, skipping API call")
        return True

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    try:
        if kind == "document":
            doc_rel = meta.get("doc_path")
            doc_title = meta.get("doc_title", "")
            if not doc_rel:
                print(f"    [error] no doc_path in metadata — skipping")
                return False
            pdf_path = REPO / doc_rel
            if not pdf_path.exists():
                print(f"    [error] PDF not found: {pdf_path} — skipping")
                return False
            post_urn = post_document(token, urn, text, pdf_path, doc_title, scheduled_unix_ms)
        else:
            image_path = (REPO / media_path) if media_path else None
            post_urn = post_text(token, urn, text, image_path, scheduled_unix_ms)

        # Update DB: li_native_scheduled + store post_urn for comment phase.
        meta["post_urn"] = post_urn
        meta["scheduled_unix_ms"] = scheduled_unix_ms
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "UPDATE posts SET status='li_native_scheduled', metadata_json=? WHERE id=?",
            (json.dumps(meta), post_id),
        )
        conn.commit()
        conn.close()

        print(f"    → LinkedIn scheduled: {post_urn}")
        return True

    except requests.HTTPError as e:
        print(f"    [error] {e.response.status_code} — {e.response.text[:300]}")
        return False
    except Exception as e:
        print(f"    [error] {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Push LinkedIn posts to LinkedIn native scheduling.")
    parser.add_argument("--week", help="Filter by week slug prefix, e.g. 2026-W22")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be pushed without calling API")
    args = parser.parse_args()

    if not DB_PATH.exists():
        sys.exit(f"DB not found: {DB_PATH}\nRun: python3 scripts/db_setup.py first")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    query = "SELECT * FROM posts WHERE platform='linkedin' AND status='pending'"
    params: list = []
    if args.week:
        query += " AND (slug LIKE ? OR slug LIKE ?)"
        date_prefix = args.week.replace("W", "")  # rough filter by slug date
        query += ""  # rely on week param below
        # Filter by slugs whose date falls in the week — use slug prefix approach.
        # Slugs start with YYYY-MM-DD; filter by checking week tag in metadata or just load all and filter.
        # Simplest: load all pending and filter by scheduled_at year-week if needed.
        params = []
        query = "SELECT * FROM posts WHERE platform='linkedin' AND status='pending'"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    if args.week:
        # Filter: slug must contain a date that falls in the given week.
        from lib.schedule_calc import get_iso_week
        rows = [r for r in rows if get_iso_week(dict(r)["slug"][:10]) == args.week
                or dict(r)["slug"].endswith(f"#{args.week}")]

    if not rows:
        print("No pending LinkedIn posts found.")
        return

    print(f"Pushing {len(rows)} LinkedIn post(s) to native scheduling"
          + (f" (week {args.week})" if args.week else "")
          + (" [DRY RUN]" if args.dry_run else "") + " ...\n")

    sys.path.insert(0, str(REPO / "scripts"))
    from post_linkedin import get_credentials
    token, urn = get_credentials()

    ok = fail = 0
    for row in rows:
        success = push_post(dict(row), token, urn, args.dry_run)
        if success:
            ok += 1
        else:
            fail += 1

    print(f"\nDone: {ok} scheduled, {fail} failed.")
    if not args.dry_run and ok:
        print("Posts now visible in LinkedIn Creator Studio → Scheduled.")
        print("Daemon fires comments at scheduled_at + 5 min:")
        print("  nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &")


if __name__ == "__main__":
    main()
