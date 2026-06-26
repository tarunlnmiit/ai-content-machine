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
LINKEDIN_DOC_SLOTS = [(2, 10, 0), (4, 10, 0)] # Wed 10am, Fri 10am (slide deck posts)
THREADS_SLOTS = [(0, 19, 0), (3, 19, 0)]      # Mon/Thu 7pm
INSTAGRAM_SLOTS = [(0, 16, 0), (3, 10, 0)]    # Mon 4pm, Thu 10am
# Reel slots — spread the ~2-3 reels/niche across the week (Mon/Tue/Wed mornings).
REEL_SLOTS = [(0, 7, 0), (1, 11, 0), (2, 9, 0)]

# Public video-URL manifest the IG reel publisher reads. IG Graph API ingests reels
# from a public https URL (not local bytes), so an uploader (scripts/upload_reels_blob.py)
# must host each reel and write its URL here before reels can auto-publish.
REEL_MANIFEST = REPO / "data" / "reel_media_urls.json"


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

    # Comments posted by daemon immediately after the post goes live.
    meta = {"kind": "image" if media_path else "text"}
    comment_file = txt_path.with_name("linkedin_first_comment.txt")
    if comment_file.exists():
        comment = comment_file.read_text(encoding="utf-8").strip()
        if comment:
            meta["first_comment"] = comment
    second_comment_file = txt_path.with_name("linkedin_second_comment.txt")
    if second_comment_file.exists():
        second = second_comment_file.read_text(encoding="utf-8").strip()
        if second:
            meta["second_comment"] = second

    conn.execute(
        """INSERT INTO posts (platform, content_text, media_path, scheduled_at, status,
           metadata_json, slug)
           VALUES (?,?,?,?,?,?,?)""",
        ("linkedin", text, media_path, scheduled_at, "pending", json.dumps(meta), slug),
    )
    n_comments = sum(1 for k in ("first_comment", "second_comment") if meta.get(k))
    extras = "".join([
        " + image" if media_path else "",
        f" + {n_comments} comment(s)" if n_comments else "",
    ])
    print(f"  [queued] linkedin/{slug} — at {scheduled_at}{extras}")


def insert_linkedin_document(conn: sqlite3.Connection, slug: str, slot_index: int):
    """Stage a LinkedIn document post for the slide deck PDF, if one exists."""
    date_str = slug[:10]
    week = get_iso_week(date_str)
    pdf_path = REPO / "assets" / "slides" / week / f"{slug}_slides.pdf"
    if not pdf_path.exists():
        return

    doc_slug = f"{slug}#slides"
    if slug_already_loaded(conn, doc_slug, "linkedin"):
        print(f"  [skip] linkedin-doc/{doc_slug} already in DB")
        return

    # Caption: optional override file, else auto-generate.
    slug_dir = REPO / "content" / "derivatives" / week / slug
    cap_file = slug_dir / "linkedin_document_caption.txt"
    if cap_file.exists():
        caption = cap_file.read_text(encoding="utf-8").strip()
    else:
        # Humanize slug: strip date + niche segment, title-case the rest.
        parts = slug.split("_")
        # slug format: YYYY-MM-DD_niche1_niche2_title-words
        title_parts = parts[3:] if len(parts) > 3 else parts[1:]
        title = " ".join(title_parts).replace("-", " ").title()
        caption = f"Slides from this week's post.\n\n{title} — swipe through for the key ideas 👆"

    # Document title for the card.
    try:
        yt_meta = json.loads((slug_dir / "youtube_metadata.json").read_text(encoding="utf-8"))
        doc_title = yt_meta.get("title", slug)[:100]
    except (OSError, ValueError):
        doc_title = slug

    weekday, hour, minute = LINKEDIN_DOC_SLOTS[slot_index % len(LINKEDIN_DOC_SLOTS)]
    scheduled_at = next_weekday(weekday, hour, minute).isoformat()

    meta = {
        "kind": "document",
        "doc_path": str(pdf_path.relative_to(REPO)),
        "doc_title": doc_title,
    }
    # Comments: 1st = Worksheet link, 2nd = YT link (strategy: same as regular LI post order)
    doc1_file = slug_dir / "linkedin_document_first_comment.txt"
    if doc1_file.exists():
        c = doc1_file.read_text(encoding="utf-8").strip()
        if c:
            meta["first_comment"] = c
    doc2_file = slug_dir / "linkedin_document_second_comment.txt"
    if doc2_file.exists():
        c = doc2_file.read_text(encoding="utf-8").strip()
        if c:
            meta["second_comment"] = c

    conn.execute(
        """INSERT INTO posts (platform, content_text, scheduled_at, status,
           metadata_json, slug)
           VALUES (?,?,?,?,?,?)""",
        ("linkedin", caption, scheduled_at, "pending", json.dumps(meta), doc_slug),
    )
    n_comments = sum(1 for k in ("first_comment", "second_comment") if meta.get(k))
    extras = f" + {n_comments} comment(s)" if n_comments else ""
    print(f"  [queued] linkedin-doc/{doc_slug} — at {scheduled_at} ({pdf_path.name}){extras}")


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


def _reel_manifest() -> dict:
    """Load the slug → [{index, url, caption?}] public-URL manifest, or {} if absent."""
    if not REEL_MANIFEST.exists():
        return {}
    try:
        return json.loads(REEL_MANIFEST.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return {}


def insert_instagram_reels(conn: sqlite3.Connection, slug: str, clean_caption: str | None,
                           manifest: dict):
    """Stage Instagram Reels for a slug from public URLs in the reel manifest.

    Each manifest entry is {"index": int, "url": str, "caption": optional str}. Falls
    back to the slug's clean IG caption when an entry has no caption. No-op (with a
    note) when the slug has no hosted reels yet — IG reels stay manual until then.
    """
    entries = manifest.get(slug) or []
    if not entries:
        return 0
    staged = 0
    for entry in entries:
        url = entry.get("url")
        idx = entry.get("index", 0)
        if not url:
            continue
        reel_slug = f"{slug}#reel{idx}"
        if slug_already_loaded(conn, reel_slug, "instagram"):
            continue
        caption = entry.get("caption") or clean_caption or ""
        weekday, hour, minute = REEL_SLOTS[idx % len(REEL_SLOTS)]
        scheduled_at = next_weekday(weekday, hour, minute).isoformat()
        meta = {"kind": "reel", "media_url": url}
        conn.execute(
            """INSERT INTO posts (platform, content_text, scheduled_at, status,
               metadata_json, slug) VALUES (?,?,?,?,?,?)""",
            ("instagram", caption, scheduled_at, "pending", json.dumps(meta), reel_slug),
        )
        staged += 1
        print(f"  [queued] instagram-reel/{reel_slug} — at {scheduled_at}")
    return staged


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
    reel_manifest = _reel_manifest()

    for i, slug in enumerate(slugs):
        # Find slug_dir under the correct week folder
        date_str = slug[:10]  # Extract YYYY-MM-DD from slug
        week = get_iso_week(date_str)
        slug_dir = deriv_dir / week / slug
        print(f"[{i+1}/{len(slugs)}] {slug}")

        linkedin_file = slug_dir / "linkedin_post.txt"
        if linkedin_file.exists():
            insert_linkedin(conn, slug, linkedin_file, i)

        insert_linkedin_document(conn, slug, i)

        # Mark this slug as "Scheduled" in the annual tracker (staged → will publish).
        # The scheduler daemon flips it to "Published" after the post goes live via
        # mark_published() called in scheduler.py. If tracker integration is unavailable,
        # this is a silent no-op.
        try:
            from lib.tracker import mark_published as _mark_tracker
            _mark_tracker(slug, status="Scheduled")
        except Exception:
            pass

        threads_file = slug_dir / "threads_post.txt"
        if threads_file.exists():
            insert_threads(conn, slug, threads_file, i)

        # Prefer the post-ready clean caption; fall back to the brief file.
        clean_file = slug_dir / "instagram_caption_clean.txt"
        instagram_file = clean_file if clean_file.exists() else slug_dir / "instagram_caption.txt"
        if instagram_file.exists():
            insert_instagram(conn, slug, instagram_file, i)

        # Instagram Reels — staged only for slugs whose reels are hosted (manifest).
        clean_caption = clean_file.read_text(encoding="utf-8").strip() if clean_file.exists() else None
        insert_instagram_reels(conn, slug, clean_caption, reel_manifest)

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
