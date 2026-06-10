#!/usr/bin/env python3
"""Audit content, assets, and schedule for an ISO week.

Usage:
  python3 scripts/list_week_content.py 2026-W22           # content audit
  python3 scripts/list_week_content.py 2026-W22 --plan    # Mon-Fri production plan
  python3 scripts/list_week_content.py 2026-W22 --json    # machine-readable JSON
"""

import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).parent.parent

KNOWN_NICHES = ["data_science_tech", "life_self_dev", "poetry_quotes"]

NICHE_LABEL = {
    "data_science_tech": "DS",
    "life_self_dev": "Life",
    "poetry_quotes": "Poetry",
}

# (display_time, week_note) — inferred from niche+platform
TIMINGS: dict[tuple[str, str], tuple[str, str]] = {
    ("data_science_tech", "blog"):           ("Wed 2:00 PM IST",  "same wk"),
    ("data_science_tech", "youtube"):        ("Thu upload",        "same wk"),
    ("data_science_tech", "youtube_shorts"): ("Thu upload",        "same wk"),
    ("data_science_tech", "instagram"):      ("Wed 8:00 AM IST",   "+1 wk"),
    ("data_science_tech", "threads"):        ("Wed 8:00 PM IST",   "+1 wk"),
    ("data_science_tech", "linkedin"):       ("Tue 8:00 AM IST",   "+1 wk"),
    ("data_science_tech", "twitter"):        ("—",                 ""),
    ("life_self_dev",     "blog"):           ("Wed 2:00 PM IST",  "same wk"),
    ("life_self_dev",     "youtube"):        ("Thu upload",        "same wk"),
    ("life_self_dev",     "youtube_shorts"): ("Thu upload",        "same wk"),
    ("life_self_dev",     "instagram"):      ("Tue 8:00 AM IST",   "+1 wk"),
    ("life_self_dev",     "threads"):        ("Tue 8:00 PM IST",   "+1 wk"),
    ("life_self_dev",     "linkedin"):       ("Tue 8:00 AM IST",   "+1 wk"),
    ("life_self_dev",     "twitter"):        ("Mon 1:00 PM IST",   "+1 wk"),
    ("poetry_quotes",     "blog"):           ("Wed 2:00 PM IST",  "same wk"),
    ("poetry_quotes",     "youtube"):        ("Thu upload",        "same wk"),
    ("poetry_quotes",     "youtube_shorts"): ("Thu upload",        "same wk"),
    ("poetry_quotes",     "instagram"):      ("Fri 10:00 AM IST",  "+1 wk"),
    ("poetry_quotes",     "threads"):        ("Fri 12:00 PM IST",  "+1 wk"),
    ("poetry_quotes",     "linkedin"):       ("Tue 8:00 AM IST",   "+1 wk"),
    ("poetry_quotes",     "twitter"):        ("Fri 12:00 PM IST",  "+1 wk"),
}

# (label, timing_key_or_None, filename_or_None)
# filename=None → blog special case: content/blogs/{week}/{slug}.md
CONTENT_ROWS: list[tuple[str, str | None, str | None]] = [
    ("Blog",          "blog",           None),
    ("YouTube",       "youtube",        "youtube_metadata.json"),
    ("YT Shorts",     "youtube_shorts", "youtube_shorts_metadata.json"),
    ("Instagram/FB",  "instagram",      "instagram_caption.txt"),
    ("Threads",       "threads",        "threads_post.txt"),
    ("LinkedIn",      "linkedin",       "linkedin_post.txt"),
    ("Twitter/X",     "twitter",        "twitter_thread.txt"),
    ("Newsletter",    None,             "newsletter.txt"),
    ("Slide Outline", None,             "slide_outline.json"),
    ("Schedule",      None,             "schedule.json"),
]

IMAGE_KEYS = ["instagram", "linkedin", "threads", "twitter"]


def parse_week(week_str: str) -> tuple[int, int]:
    m = re.fullmatch(r"(\d{4})-W(\d{2})", week_str)
    if not m:
        print(f"Error: invalid week format '{week_str}' — expected YYYY-Wnn", file=sys.stderr)
        sys.exit(1)
    return int(m.group(1)), int(m.group(2))


def prev_week(year: int, week: int) -> tuple[int, int]:
    mon = date.fromisocalendar(year, week, 1) - timedelta(weeks=1)
    cal = mon.isocalendar()
    return cal[0], cal[1]


def parse_slug(slug: str) -> tuple[str, str, str]:
    """Return (date_str, niche, title) from slug dirname."""
    for niche in KNOWN_NICHES:
        marker = f"_{niche}_"
        if marker in slug:
            idx = slug.index(marker)
            return slug[:idx], niche, slug[idx + len(marker):]
    # fallback
    parts = slug.split("_", 1)
    return parts[0], "", parts[1] if len(parts) > 1 else slug


def load_schedule(slug_dir: Path) -> dict:
    p = slug_dir / "schedule.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def fmt_schedule_dt(dt_str: str) -> str:
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%a %b %d %I:%M %p IST")
    except Exception:
        return dt_str


def inferred_timing(niche: str, key: str) -> str:
    entry = TIMINGS.get((niche, key))
    if not entry:
        return "—"
    time_str, week_note = entry
    if not week_note:
        return time_str
    return f"{time_str}  ({week_note})"


def resolve_timing(niche: str, key: str | None, schedule: dict) -> str:
    if key is None:
        return "—"
    if key == "instagram":
        t = schedule.get("social", {}).get("ig_fb_publish_at", "")
        if t:
            return fmt_schedule_dt(t) + "  (from schedule.json)"
    if key == "threads":
        t = schedule.get("social", {}).get("threads_publish_at", "")
        if t:
            return fmt_schedule_dt(t) + "  (from schedule.json)"
    return inferred_timing(niche, key)


def glob_assets(dir_path: Path, slug: str) -> list[Path]:
    if not dir_path.exists():
        return []
    return sorted(p for p in dir_path.iterdir() if p.name.startswith(slug))


def audit_slug(slug_dir: Path, week: str) -> dict:
    slug = slug_dir.name
    date_str, niche, title = parse_slug(slug)
    schedule = load_schedule(slug_dir)

    blog_path = REPO / "content" / "blogs" / week / f"{slug}.md"

    content = []
    for label, timing_key, filename in CONTENT_ROWS:
        if filename is None:
            path = blog_path
        else:
            path = slug_dir / filename
        content.append({
            "label": label,
            "path": str(path.relative_to(REPO)),
            "exists": path.exists(),
            "timing": resolve_timing(niche, timing_key, schedule),
        })

    social_dir = REPO / "assets" / "social_posts" / week
    images = []
    drive_urls: dict = schedule.get("image_urls", {})
    for key in IMAGE_KEYS:
        img_path = social_dir / f"{slug}_{key}.png"
        images.append({
            "platform": key,
            "path": str(img_path.relative_to(REPO)),
            "exists": img_path.exists(),
            "drive_url": drive_urls.get(key, ""),
        })
    html_path = social_dir / f"{slug}_social.html"
    images.append({
        "platform": "social.html",
        "path": str(html_path.relative_to(REPO)),
        "exists": html_path.exists(),
        "drive_url": "",
    })

    slides_dir = REPO / "assets" / "slides" / week
    carousel_dir = REPO / "assets" / "carousels" / week
    slides = [
        {"label": "slides.html", "path": f"assets/slides/{week}/{slug}_slides.html",      "exists": (slides_dir / f"{slug}_slides.html").exists()},
        {"label": "slides.pdf",  "path": f"assets/slides/{week}/{slug}_slides.pdf",       "exists": (slides_dir / f"{slug}_slides.pdf").exists()},
        {"label": "carousel",    "path": f"assets/carousels/{week}/{slug}_carousel.html", "exists": (carousel_dir / f"{slug}_carousel.html").exists()},
        {"label": "export.py",   "path": f"assets/carousels/{week}/{slug}_export.py",     "exists": (carousel_dir / f"{slug}_export.py").exists()},
    ]

    video: dict[str, dict] = {}
    for key, rel_dir in [
        ("raw",     f"assets/raw/{week}"),
        ("edited",  "assets/video/edited"),
        ("stories", "assets/stories"),
    ]:
        files = glob_assets(REPO / rel_dir, slug)
        video[key] = {
            "dir": rel_dir,
            "files": [str(p.relative_to(REPO)) for p in files],
        }

    # Hyperframes use render-date prefix (not slug prefix); match on content date + niche
    hf_rel = f"assets/hyperframes/{week}"
    hf_dir = REPO / hf_rel
    niche_norm = niche.replace("_", "-")
    hf_files = sorted(
        p for p in (hf_dir.iterdir() if hf_dir.exists() else [])
        if date_str in p.name and niche_norm in p.name.replace("_", "-")
    )
    video["hyperframes"] = {
        "dir": hf_rel,
        "files": [str(p.relative_to(REPO)) for p in hf_files],
    }

    return {
        "slug": slug,
        "date": date_str,
        "niche": niche,
        "title": title,
        "content": content,
        "images": images,
        "slides": slides,
        "video": video,
    }


def mark(exists: bool) -> str:
    return "✓" if exists else "✗"


def print_audit(data: list[dict], week: str) -> None:
    print(f"\nWeek: {week}  ({len(data)} slug{'s' if len(data) != 1 else ''})\n")
    for s in data:
        bar = "━" * 64
        niche_display = s["niche"].replace("_", " ")
        print(bar)
        print(f"{s['date']} · {niche_display} · {s['title']}")
        print(bar)

        print("\n  CONTENT")
        for row in s["content"]:
            label = row["label"].ljust(15)
            path = row["path"].ljust(52)
            print(f"  {mark(row['exists'])}  {label}  {path}  {row['timing']}")

        print("\n  IMAGES  (assets/social_posts/{week}/)".replace("{week}", week))
        for img in s["images"]:
            plat = img["platform"].ljust(12)
            url_part = f"  → {img['drive_url']}" if img["drive_url"] else ""
            print(f"  {mark(img['exists'])}  {plat}  {img['path']}{url_part}")

        print("\n  SLIDES & CAROUSELS")
        for sl in s["slides"]:
            print(f"  {mark(sl['exists'])}  {sl['label'].ljust(12)}  {sl['path']}")

        print("\n  VIDEO & MEDIA")
        for key, info in s["video"].items():
            if info["files"]:
                print(f"  ✓  {key.ljust(12)}  {info['dir']}/")
                for f in info["files"]:
                    print(f"              {f}")
            else:
                print(f"  ✗  {key.ljust(12)}  {info['dir']}/ — empty")

        print()


def _content_ready(s: dict, labels: set[str]) -> bool:
    return all(r["exists"] for r in s["content"] if r["label"] in labels)


def print_plan(data: list[dict], week: str) -> None:
    year, wnum = parse_week(week)
    mon = date.fromisocalendar(year, wnum, 1)
    py_wk, prev_wnum = prev_week(year, wnum)
    prev_week_str = f"{py_wk}-W{prev_wnum:02d}"

    print(f"\nWeek: {week}  ({len(data)} slug{'s' if len(data) != 1 else ''})")
    print(f"Calendar: Mon {mon.strftime('%b %d')} – Fri {(mon + timedelta(days=4)).strftime('%b %d, %Y')}\n")

    days = [mon + timedelta(days=i) for i in range(5)]
    bar = "─" * 64

    # MON
    print(f"MON {days[0].strftime('%b %d')}   Generate blogs + repurpose all niches")
    print(bar)
    for s in data:
        blog = next((r for r in s["content"] if r["label"] == "Blog"), None)
        label = NICHE_LABEL.get(s["niche"], s["niche"])
        print(f"  {mark(blog['exists'] if blog else False)}  {label:8}  {blog['path'] if blog else '—'}")
    deriv_labels = {"YouTube", "Instagram/FB", "Threads", "LinkedIn", "Twitter/X"}
    deriv_ok = sum(1 for s in data if _content_ready(s, deriv_labels))
    print(f"  {mark(deriv_ok == len(data))}  Derivatives   content/derivatives/{week}/  ({deriv_ok}/{len(data)} slugs fully populated)")

    # TUE
    print(f"\nTUE {days[1].strftime('%b %d')}   Video scripts + social visual assets")
    print(bar)
    yt_ok = sum(1 for s in data if any(r["label"] == "YouTube" and r["exists"] for r in s["content"]))
    print(f"  {mark(yt_ok == len(data))}  YouTube metadata     {yt_ok}/{len(data)} slugs")
    img_ok = sum(1 for s in data if any(img["exists"] for img in s["images"] if img["platform"] == "instagram"))
    hint = "  ← run image generation" if img_ok < len(data) else ""
    print(f"  {mark(img_ok == len(data))}  Social images        {img_ok}/{len(data)} slugs{hint}")

    # WED
    print(f"\nWED {days[2].strftime('%b %d')}   Upload blogs to Medium/Substack + shoot videos")
    print(bar)
    ready_blogs = [s for s in data if any(r["label"] == "Blog" and r["exists"] for r in s["content"])]
    missing_blogs = [s for s in data if not any(r["label"] == "Blog" and r["exists"] for r in s["content"])]
    if ready_blogs:
        print(f"  → Upload to Medium/Substack ({len(ready_blogs)} ready):")
        for s in ready_blogs:
            blog = next((r for r in s["content"] if r["label"] == "Blog"), None)
            if blog:
                print(f"       {blog['path']}")
    if missing_blogs:
        for s in missing_blogs:
            label = NICHE_LABEL.get(s["niche"], s["niche"])
            print(f"  ✗  {label} blog missing — generate on Monday first")
    raw_any = any(s["video"]["raw"]["files"] for s in data)
    print(f"  {mark(raw_any)}  Raw video            assets/raw/{week}/{'  ← shoot needed' if not raw_any else ''}")

    # THU
    print(f"\nTHU {days[3].strftime('%b %d')}   Upload videos + create/upload shorts/reels")
    print(bar)
    hf_any = any(s["video"]["hyperframes"]["files"] for s in data)
    edited_any = any(s["video"]["edited"]["files"] for s in data)
    print(f"  {mark(hf_any)}  Hyperframes / shorts  assets/hyperframes/{week}/{'  ← empty' if not hf_any else ''}")
    print(f"  {mark(edited_any)}  Edited long-form      assets/video/edited/{'  ← empty' if not edited_any else ''}")

    # FRI
    print(f"\nFRI {days[4].strftime('%b %d')}   Schedule social media for {prev_week_str}")
    print(bar)
    print(f"  → python3 scripts/load_posts.py --week {prev_week_str}")
    print(f"  → CSVs: output/scheduled/metricool_breathofds.csv")
    print(f"          output/scheduled/metricool_mistakenlyhuman.csv")
    print(f"  → Import both CSVs into Metricool dashboard")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit content for an ISO week.")
    parser.add_argument("week", help="ISO week, e.g. 2026-W22")
    parser.add_argument("--plan", action="store_true", help="Show Mon-Fri production plan")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output JSON")
    args = parser.parse_args()

    parse_week(args.week)

    deriv_root = REPO / "content" / "derivatives" / args.week
    if not deriv_root.exists():
        print(f"No content found for {args.week} — {deriv_root} does not exist")
        sys.exit(0)

    slug_dirs = sorted(p for p in deriv_root.iterdir() if p.is_dir())
    if not slug_dirs:
        print(f"No slugs found for {args.week}")
        sys.exit(0)

    data = [audit_slug(d, args.week) for d in slug_dirs]

    if args.as_json:
        print(json.dumps(data, indent=2))
    elif args.plan:
        print_plan(data, args.week)
    else:
        print_audit(data, args.week)


if __name__ == "__main__":
    main()
