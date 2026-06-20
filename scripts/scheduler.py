#!/usr/bin/env python3
"""
APScheduler daemon — polls scheduling.db every 60 seconds.
Fires pending posts when scheduled_at <= now.
Dispatches to post_linkedin.py, post_instagram.py, post_facebook.py, post_threads.py.
Updates DB status to 'posted' or 'failed'.

Twitter was dropped from the pipeline. LinkedIn is active (employer cleared).
IG / FB / Threads publish via the Meta Graph API (see scripts/lib/meta_graph.py and
docs/one-time-platform-setup.md). Only platforms with valid credentials fire — the
rest are logged and skipped. Recording, the content-approval gate, and replies stay
manual (honesty guardrail: this is "minimal manual", not "zero manual").

Run as background daemon:
    nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &

Check it's running:
    ps aux | grep scheduler.py

Stop it:
    pkill -f scheduler.py
"""

import json
import logging
import signal
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

REPO = Path(__file__).parent.parent
DB_PATH = REPO / "data" / "scheduling.db"
load_dotenv(REPO / ".env")

IST = timezone(timedelta(hours=5, minutes=30))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("scheduler")


# ── Dispatch functions ────────────────────────────────────────────────────

def _post_meta(post: dict) -> dict:
    """Parse metadata_json for a post row (carries media_url(s) + kind for Meta)."""
    raw = post.get("metadata_json")
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return {}


def dispatch_instagram(post: dict):
    sys.path.insert(0, str(REPO / "scripts"))
    from post_instagram import post_reel, post_image, post_carousel

    post_id = post["id"]
    slug = post["slug"]
    caption = post["content_text"]
    meta = _post_meta(post)
    kind = meta.get("kind", "reel")

    log.info(f"Posting Instagram ({kind}): slug={slug}")
    try:
        if kind == "reel":
            media_id = post_reel(meta["media_url"], caption)
        elif kind == "carousel":
            media_id = post_carousel(meta["media_urls"], caption)
        else:  # single image
            media_id = post_image(meta["media_url"], caption)
        _mark_posted(post_id, {"media_id": media_id, "slug": slug})
        log.info(f"Instagram posted: {media_id}")
    except KeyError:
        _mark_failed(post_id, "missing media_url/media_urls in metadata_json")
        log.error(f"Instagram skip {slug}: no public media URL staged")
    except Exception as e:
        _mark_failed(post_id, str(e))
        log.error(f"Instagram post failed: {e}")


def dispatch_facebook(post: dict):
    sys.path.insert(0, str(REPO / "scripts"))
    from post_facebook import post_text, post_photo, post_video

    post_id = post["id"]
    slug = post["slug"]
    message = post["content_text"]
    meta = _post_meta(post)
    kind = meta.get("kind", "text")

    log.info(f"Posting Facebook ({kind}): slug={slug}")
    try:
        if kind == "video":
            post_obj = post_video(meta["media_url"], message)
        elif kind in ("image", "photo"):
            post_obj = post_photo(meta["media_url"], message)
        else:
            post_obj = post_text(message, meta.get("link"))
        _mark_posted(post_id, {"fb_id": post_obj, "slug": slug})
        log.info(f"Facebook posted: {post_obj}")
    except KeyError:
        _mark_failed(post_id, "missing media_url in metadata_json")
        log.error(f"Facebook skip {slug}: no public media URL staged")
    except Exception as e:
        _mark_failed(post_id, str(e))
        log.error(f"Facebook post failed: {e}")


def dispatch_threads(post: dict):
    sys.path.insert(0, str(REPO / "scripts"))
    from post_threads import post_thread

    post_id = post["id"]
    slug = post["slug"]
    text = post["content_text"]
    meta = _post_meta(post)

    log.info(f"Posting Threads: slug={slug}")
    try:
        thread_id = post_thread(
            text, image_url=meta.get("media_url"), video_url=meta.get("video_url")
        )
        _mark_posted(post_id, {"thread_id": thread_id, "slug": slug})
        log.info(f"Threads posted: {thread_id}")
    except Exception as e:
        _mark_failed(post_id, str(e))
        log.error(f"Threads post failed: {e}")


def dispatch_linkedin(post: dict):
    sys.path.insert(0, str(REPO / "scripts"))
    from post_linkedin import post_text, get_credentials

    post_id = post["id"]
    slug = post["slug"]
    text = post["content_text"]
    media_path = post["media_path"]

    image_path = (REPO / media_path) if media_path else None

    log.info(f"Posting LinkedIn: slug={slug}")
    try:
        token, urn = get_credentials()
        post_urn = post_text(token, urn, text, image_path)
        _mark_posted(post_id, {"post_urn": post_urn, "slug": slug})
        log.info(f"LinkedIn posted: {post_urn}")
    except Exception as e:
        _mark_failed(post_id, str(e))
        log.error(f"LinkedIn post failed: {e}")


DISPATCHERS = {
    "linkedin": dispatch_linkedin,
    "instagram": dispatch_instagram,
    "facebook": dispatch_facebook,
    "threads": dispatch_threads,
}


# ── DB helpers ────────────────────────────────────────────────────────────

def _mark_posted(post_id: int, meta: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE posts SET status='posted', posted_at=?, metadata_json=? WHERE id=?",
        (datetime.now(timezone.utc).isoformat(), json.dumps(meta), post_id),
    )
    conn.commit()
    conn.close()


def _mark_failed(post_id: int, error: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE posts SET status='failed', posted_at=?, metadata_json=? WHERE id=?",
        (datetime.now(timezone.utc).isoformat(), json.dumps({"error": error}), post_id),
    )
    conn.commit()
    conn.close()


# ── Poll function ─────────────────────────────────────────────────────────

def poll_and_fire():
    if not DB_PATH.exists():
        log.warning("scheduling.db not found — skipping poll")
        return

    now = datetime.now(IST).isoformat()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Only fire parent posts (thread_parent_id IS NULL) to avoid double-posting thread children
    due = conn.execute(
        """SELECT * FROM posts
           WHERE status='pending'
             AND scheduled_at <= ?
             AND (thread_parent_id IS NULL)
           ORDER BY scheduled_at ASC""",
        (now,),
    ).fetchall()
    conn.close()

    if not due:
        return

    log.info(f"Found {len(due)} due post(s)")

    for row in due:
        post = dict(row)
        platform = post["platform"]

        if platform not in DISPATCHERS:
            log.warning(f"No dispatcher for platform '{platform}' — marking cancelled")
            _mark_failed(post["id"], f"No dispatcher for platform: {platform}")
            continue

        try:
            DISPATCHERS[platform](post)
        except Exception as e:
            log.error(f"Dispatcher error for post {post['id']}: {e}")
            _mark_failed(post["id"], str(e))


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    if not DB_PATH.exists():
        log.error(f"DB not found: {DB_PATH}")
        log.error("Run: python3 scripts/db_setup.py first")
        sys.exit(1)

    log.info("Starting APScheduler daemon (IST timezone)")
    log.info(f"DB: {DB_PATH}")
    log.info("Polling every 60 seconds. Stop with: pkill -f scheduler.py")

    # Fail-soft credential check — log which Meta platforms can publish. LinkedIn
    # validates lazily on first post via post_linkedin.get_credentials().
    try:
        sys.path.insert(0, str(REPO / "scripts"))
        from lib.meta_graph import validate_credentials

        creds = validate_credentials()
        log.info(
            "Meta credential check — "
            + ", ".join(f"{k}={'ok' if v else 'MISSING'}" for k, v in creds.items())
        )
        if not any(creds.values()):
            log.warning(
                "No Meta credentials valid — IG/FB/Threads posts will fail until "
                "tokens are set (see docs/one-time-platform-setup.md). LinkedIn unaffected."
            )
    except Exception as e:
        log.warning(f"Meta credential check skipped: {e}")

    scheduler = BackgroundScheduler(timezone=IST)
    scheduler.add_job(poll_and_fire, "interval", seconds=60, id="poll_and_fire")
    scheduler.start()

    # Run once immediately on startup
    poll_and_fire()

    def handle_shutdown(sig, frame):
        log.info("Shutting down scheduler ...")
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    while True:
        time.sleep(30)


if __name__ == "__main__":
    main()
