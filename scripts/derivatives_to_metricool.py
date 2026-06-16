#!/usr/bin/env python3
"""
Turn a derivatives folder into a Metricool-importable scheduling CSV.

One reel/blog → one CSV with a row per platform (Instagram Reel, Twitter/X,
TikTok, YouTube Short, Threads, and optionally LinkedIn). Metricool is the
posting bridge, so no per-platform API is needed here.

Reads the per-platform derivative files produced by `prompts/repurposing_agent.md`:
  instagram_caption.txt, twitter_thread.txt, threads_post.txt, linkedin_post.txt,
  youtube_shorts_metadata.json

Channel reality (see plan): HN/Reddit excluded. LinkedIn is written as a DRAFT row
(Draft=true) unless --linkedin-live is passed, because posting there needs employer
clearance first.

Usage:
    # From an explicit derivatives dir, scheduled from next Monday
    python3 scripts/derivatives_to_metricool.py \
        --dir content/derivatives/2026-W23/2026-06-01_poetry_quotes_... \
        --video-url https://cdn.example.com/reel.mp4

    # By date + slug (resolves dir via content_paths), with a known niche's slots
    python3 scripts/derivatives_to_metricool.py \
        --date 2026-06-01 --slug 2026-06-01_poetry_quotes_... --niche poetry

    # Pin the schedule start and include LinkedIn as a live (non-draft) row
    python3 scripts/derivatives_to_metricool.py --dir ... --start-date 2026-06-16 --linkedin-live
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import content_paths  # noqa: E402
from lib import schedule_calc  # noqa: E402

# Exact Metricool import header (order matters — matches Mtr_calendar_template.csv).
METRICOOL_COLUMNS = [
    "Text", "Date", "Time", "Draft", "Facebook", "Twitter/X", "LinkedIn", "GBP",
    "Instagram", "Pinterest", "TikTok", "Youtube", "Threads", "Bluesky",
    "Picture Url 1", "Picture Url 2", "Picture Url 3", "Picture Url 4", "Picture Url 5",
    "Picture Url 6", "Picture Url 7", "Picture Url 8", "Picture Url 9", "Picture Url 10",
    "Alt text picture 1", "Alt text picture 2", "Alt text picture 3", "Alt text picture 4",
    "Alt text picture 5", "Alt text picture 6", "Alt text picture 7", "Alt text picture 8",
    "Alt text picture 9", "Alt text picture 10", "Document title", "Shortener",
    "Video Thumbnail Url", "Video Cover Frame", "Twitter/X Can reply", "Twitter/X Type",
    "Twitter/X Poll Duration minutes", "Twitter/X Poll Option 1", "Twitter/X Poll Option 2",
    "Twitter/X Poll Option 3", "Twitter/X Poll Option 4", "Pinterest Board",
    "Pinterest Pin Title", "Pinterest Pin Link", "Pinterest Pin New Format",
    "Instagram Post Type", "Instagram Show Reel On Feed", "Youtube Video Title",
    "Youtube Video Type", "Youtube Video Privacy", "Youtube video for kids",
    "Youtube Video Category", "Youtube Video Tags", "Youtube playlist", "GBP Post Type",
    "Facebook Post Type", "Facebook Title", "First Comment Text", "TikTok Title",
    "TikTok disable comments", "TikTok disable duet", "TikTok disable stitch",
    "TikTok Post Privacy", "TikTok Branded Content", "TikTok Your Brand",
    "TikTok Auto Add Music", "TikTok Photo Cover Index", "TikTok musicId",
    "TikTok music title", "TikTok music author", "TikTok music previewUrl",
    "TikTok music thumbnailUrl", "TikTok music soundVolume", "TikTok music originalVolume",
    "TikTok music startMillis", "TikTok music endMillis", "TikTok Ai generated content",
    "LinkedIn Type", "LinkedIn Poll Question", "LinkedIn Poll Option 1",
    "LinkedIn Poll Option 2", "LinkedIn Poll Option 3", "LinkedIn Poll Option 4",
    "LinkedIn Poll Duration", "LinkedIn Show link preview", "LinkedIn Images as Carousel",
    "Threads Reply Control", "Threads Is Spoiler", "Threads Post Type", "Brand name",
]

# Fallback slots when no niche schedule is used: (day_offset_from_start, "HH:MM:SS").
# Spread across the week so one piece doesn't blast every platform at once.
DEFAULT_SLOTS = {
    "instagram": (0, "08:00:00"),
    "twitter": (0, "13:00:00"),
    "threads": (0, "20:00:00"),
    "tiktok": (1, "10:00:00"),
    "youtube": (1, "18:00:00"),
    "linkedin": (2, "12:00:00"),
}


def _read_text(deriv_dir: Path, name: str) -> str:
    path = deriv_dir / name
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


def _read_json(deriv_dir: Path, name: str) -> dict:
    path = deriv_dir / name
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _blank_row() -> dict:
    return {col: "" for col in METRICOOL_COLUMNS}


def _next_monday(today: datetime | None = None) -> datetime:
    today = today or datetime.now()
    return today + timedelta(days=(7 - today.weekday()) % 7 or 7)


def _slot_datetime(start: datetime, day_offset: int, time_str: str) -> tuple[str, str]:
    d = (start + timedelta(days=day_offset)).strftime("%Y-%m-%d")
    return d, time_str


def _niche_slots(niche: str) -> dict | None:
    """Pull IST publish times from schedule_calc for a known niche, else None."""
    if niche not in schedule_calc.NICHE_TIMES:
        return None
    sched = schedule_calc.compute("bridge", niche).to_dict()
    social = sched["social"]

    def split(iso: str) -> tuple[str, str]:
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")

    return {
        "instagram": split(social["ig_fb_publish_at"]),
        "twitter": split(social["twitter_publish_at"]),
        "threads": split(social["threads_publish_at"]),
        "linkedin": split(social["linkedin_publish_at"]),
        "youtube": split(sched["long_form"]["publish_at"]),
        "tiktok": split(social["ig_fb_publish_at"]),  # mirror IG timing
    }


def _when(platform: str, start: datetime, niche_slots: dict | None) -> tuple[str, str]:
    if niche_slots and platform in niche_slots:
        return niche_slots[platform]
    day_offset, time_str = DEFAULT_SLOTS[platform]
    return _slot_datetime(start, day_offset, time_str)


def build_rows(
    deriv_dir: Path,
    start: datetime,
    *,
    video_url: str = "",
    thumb_url: str = "",
    niche: str = "",
    linkedin_live: bool = False,
) -> list[dict]:
    niche_slots = _niche_slots(niche)
    ig_caption = _read_text(deriv_dir, "instagram_caption.txt")
    yt_short = _read_json(deriv_dir, "youtube_shorts_metadata.json")
    rows: list[dict] = []

    # Instagram Reel
    if ig_caption:
        r = _blank_row()
        date, time = _when("instagram", start, niche_slots)
        r.update({
            "Text": ig_caption, "Date": date, "Time": time, "Draft": "false",
            "Instagram": "true", "Instagram Post Type": "REEL",
            "Instagram Show Reel On Feed": "true",
            "Video Thumbnail Url": thumb_url, "Picture Url 1": video_url,
        })
        rows.append(r)

    # Twitter/X
    tw = _read_text(deriv_dir, "twitter_thread.txt")
    if tw:
        r = _blank_row()
        date, time = _when("twitter", start, niche_slots)
        r.update({
            "Text": tw, "Date": date, "Time": time, "Draft": "false",
            "Twitter/X": "true", "Twitter/X Type": "POST",
        })
        rows.append(r)

    # TikTok (reuse IG caption as the description)
    if ig_caption:
        r = _blank_row()
        date, time = _when("tiktok", start, niche_slots)
        r.update({
            "Text": ig_caption, "Date": date, "Time": time, "Draft": "false",
            "TikTok": "true", "TikTok Post Privacy": "PUBLIC_TO_EVERYONE",
            "TikTok Auto Add Music": "true", "Picture Url 1": video_url,
        })
        rows.append(r)

    # YouTube Short
    if yt_short:
        r = _blank_row()
        date, time = _when("youtube", start, niche_slots)
        tags = ",".join(yt_short.get("tags", []))
        r.update({
            "Text": yt_short.get("description", ""), "Date": date, "Time": time,
            "Draft": "false", "Youtube": "true",
            "Youtube Video Title": yt_short.get("title", ""),
            "Youtube Video Type": "SHORT", "Youtube Video Privacy": "PUBLIC",
            "Youtube video for kids": "false",
            "Youtube Video Category": "SCIENCE_TECHNOLOGY",
            "Youtube Video Tags": tags, "Picture Url 1": video_url,
        })
        rows.append(r)

    # Threads
    th = _read_text(deriv_dir, "threads_post.txt")
    if th:
        r = _blank_row()
        date, time = _when("threads", start, niche_slots)
        r.update({
            "Text": th, "Date": date, "Time": time, "Draft": "false",
            "Threads": "true", "Threads Post Type": "POST",
        })
        rows.append(r)

    # LinkedIn — DRAFT unless explicitly cleared (employer constraint)
    li = _read_text(deriv_dir, "linkedin_post.txt")
    if li:
        r = _blank_row()
        date, time = _when("linkedin", start, niche_slots)
        r.update({
            "Text": li, "Date": date, "Time": time,
            "Draft": "false" if linkedin_live else "true",
            "LinkedIn": "true", "LinkedIn Type": "POST",
            "LinkedIn Show link preview": "true",
        })
        rows.append(r)

    return rows


def write_csv(rows: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=METRICOOL_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def resolve_dir(args: argparse.Namespace) -> Path:
    if args.dir:
        return Path(args.dir)
    if args.date and args.slug:
        return content_paths.derivatives_dir(args.date, args.slug)
    raise SystemExit("Provide --dir, or both --date and --slug.")


def main() -> None:
    p = argparse.ArgumentParser(description="Derivatives → Metricool CSV bridge")
    p.add_argument("--dir", help="Path to a derivatives directory")
    p.add_argument("--date", help="Content date YYYY-MM-DD (with --slug)")
    p.add_argument("--slug", help="Content slug (with --date)")
    p.add_argument("--niche", default="", help="ds|life|poetry to use that niche's slots")
    p.add_argument("--start-date", help="Schedule start YYYY-MM-DD (default: next Monday)")
    p.add_argument("--video-url", default="", help="Public URL of the reel/short video")
    p.add_argument("--thumb-url", default="", help="Public URL of the video thumbnail")
    p.add_argument("--linkedin-live", action="store_true",
                   help="Write LinkedIn as a live row (default: draft, needs employer OK)")
    p.add_argument("--out", help="Output CSV path (default: <dir>/metricool.csv)")
    args = p.parse_args()

    deriv_dir = resolve_dir(args)
    if not deriv_dir.exists():
        raise SystemExit(f"Derivatives dir not found: {deriv_dir}")

    start = (datetime.strptime(args.start_date, "%Y-%m-%d")
             if args.start_date else _next_monday())

    rows = build_rows(
        deriv_dir, start,
        video_url=args.video_url, thumb_url=args.thumb_url,
        niche=args.niche, linkedin_live=args.linkedin_live,
    )
    if not rows:
        raise SystemExit(f"No derivative files found in {deriv_dir}")

    # Convention: scheduled CSVs live in output/scheduled/<ISO-week>/ (see Folder Map).
    if args.out:
        out_path = Path(args.out)
    else:
        week = schedule_calc.get_iso_week(start.strftime("%Y-%m-%d"))
        out_path = content_paths.REPO / "output" / "scheduled" / week / f"{deriv_dir.name}_metricool.csv"
    write_csv(rows, out_path)
    platforms = [c for r in rows for c in
                 ("Instagram", "Twitter/X", "TikTok", "Youtube", "Threads", "LinkedIn")
                 if r.get(c) == "true"]
    print(f"Wrote {len(rows)} rows → {out_path}")
    print(f"Platforms: {', '.join(dict.fromkeys(platforms))}")
    if any(r.get('LinkedIn') == 'true' and r.get('Draft') == 'true' for r in rows):
        print("LinkedIn row is a DRAFT — clear with employer, then re-run with --linkedin-live.")


if __name__ == "__main__":
    main()
