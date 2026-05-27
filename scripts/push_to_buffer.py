#!/usr/bin/env python3
"""
Push produced content into the buffer — or confirm it stays as live content.

Run after any production day. Script checks current buffer depth per niche and
decides automatically where content goes:

  - Buffer < 4 weeks  → copies into the next empty week slot (buffers it)
  - Buffer already 4  → prints "buffer full — content stays live this week"

Usage:
    # Auto-decide for all 3 niches (most common — run after Wed production)
    python3 scripts/push_to_buffer.py --auto

    # Auto-decide for one niche
    python3 scripts/push_to_buffer.py --auto --niche ds

    # Force into a specific week slot (override auto)
    python3 scripts/push_to_buffer.py --niche ds --week 3

    # Target a specific production date (default: latest file by mtime)
    python3 scripts/push_to_buffer.py --auto --date 2026-05-21

    # Preview without writing
    python3 scripts/push_to_buffer.py --auto --dry-run
"""

import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).parent.parent

NICHE_MAP = {
    "ds": "data_science_tech",
    "life": "life_self_dev",
    "poetry": "poetry_quotes",
    "data_science_tech": "data_science_tech",
    "life_self_dev": "life_self_dev",
    "poetry_quotes": "poetry_quotes",
}

ALL_NICHES = ["data_science_tech", "life_self_dev", "poetry_quotes"]

BLOGS_DIR = REPO / "content" / "blogs"
SCRIPTS_DIR = REPO / "content" / "scripts"
DERIVATIVES_DIR = REPO / "content" / "derivatives"
BUFFER_DIR = REPO / "content" / "buffer"
BUFFER_TARGET = 4


def buffer_depth(niche: str) -> int:
    return len(list(BUFFER_DIR.glob(f"week-*/{niche}/*_meta.md")))


def next_empty_week(niche: str) -> int | None:
    """Return lowest week number (1-4) that has no content for this niche."""
    for w in range(1, BUFFER_TARGET + 1):
        meta_files = list((BUFFER_DIR / f"week-{w}" / niche).glob("*_meta.md"))
        if not meta_files:
            return w
    return None


def latest_blog(niche: str, date_filter: str | None) -> Path | None:
    candidates = [
        p for p in BLOGS_DIR.glob(f"*_{niche}_*.md")
        if "_images" not in p.name
    ]
    if date_filter:
        candidates = [p for p in candidates if p.name.startswith(date_filter)]
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None


def latest_yt_script(niche: str, date_filter: str | None) -> Path | None:
    niche_slug = niche.replace("_", "-")
    candidates = [
        p for p in SCRIPTS_DIR.glob(f"*{niche_slug}*_yt.md")
        if "_PRODUCTION_GUIDE" not in p.name
    ]
    if date_filter:
        candidates = [p for p in candidates if date_filter.replace("-", "") in p.name.replace("-", "")
                      or date_filter in p.name]
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None


def latest_derivatives_dir(niche: str, date_filter: str | None) -> Path | None:
    niche_slug = niche.replace("_", "-")
    candidates = [p for p in DERIVATIVES_DIR.iterdir() if p.is_dir() and niche_slug in p.name]
    if date_filter:
        candidates = [p for p in candidates if p.name.startswith(date_filter)]
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None


def build_social_copy(deriv_dir: Path) -> str:
    parts = []
    for fname, label in [
        ("twitter_thread.txt", "Twitter/X"),
        ("linkedin_post.txt", "LinkedIn"),
        ("instagram_caption.txt", "Instagram"),
        ("threads_post.txt", "Threads"),
    ]:
        f = deriv_dir / fname
        if f.exists():
            parts.append(f"## {label}\n\n{f.read_text().strip()}")
    return "\n\n---\n\n".join(parts)


def slug_from_path(p: Path) -> str:
    name = p.stem
    name = re.sub(r"^\d{4}-\d{2}-\d{2}[_-]", "", name)
    for niche_key in ["data_science_tech", "life_self_dev", "poetry_quotes",
                       "data-science-tech", "life-self-dev", "poetry-quotes"]:
        name = re.sub(rf"^{re.escape(niche_key)}[_-]?", "", name, flags=re.IGNORECASE)
    name = re.sub(r"_yt$", "", name)
    return name.strip("-_") or p.stem


def slug_already_buffered(niche: str, slug: str) -> int | None:
    """Return week number if this slug is already in any buffer week, else None."""
    for w in range(1, BUFFER_TARGET + 1):
        if (BUFFER_DIR / f"week-{w}" / niche / f"{slug}_meta.md").exists():
            return w
    return None


def push_niche(niche: str, week: int, date_filter: str | None,
               dry: bool, force: bool) -> bool:
    blog = latest_blog(niche, date_filter)
    script = latest_yt_script(niche, date_filter)
    deriv = latest_derivatives_dir(niche, date_filter)

    if not any([blog, script, deriv]):
        print(f"  [{niche}] ERROR: no produced content found — run production first")
        return False

    source = blog or script or Path(deriv.name)
    slug = slug_from_path(source)

    existing_week = slug_already_buffered(niche, slug)
    if existing_week is not None and not force:
        print(f"  [{niche}] SKIP: '{slug}' already in week-{existing_week} — use --force to overwrite")
        return False
    topic = slug.replace("-", " ").title()
    out_dir = BUFFER_DIR / f"week-{week}" / niche

    print(f"  [{niche}] → week-{week}/{niche}/  (slug: {slug})")

    if not dry:
        out_dir.mkdir(parents=True, exist_ok=True)

    def copy(src: Path, dest_name: str) -> None:
        dest = out_dir / dest_name
        if dest.exists() and not force:
            print(f"    SKIP (exists): {dest_name}  — use --force to overwrite")
            return
        print(f"    {'[dry] ' if dry else ''}COPY {src.name} → {dest_name}")
        if not dry:
            shutil.copy2(src, dest)

    def write(dest_name: str, content: str) -> None:
        dest = out_dir / dest_name
        if dest.exists() and not force:
            print(f"    SKIP (exists): {dest_name}  — use --force to overwrite")
            return
        print(f"    {'[dry] ' if dry else ''}WRITE {dest_name}")
        if not dry:
            dest.write_text(content)

    meta = (
        f"# {topic}\n\n"
        f"**Niche:** {niche}\n"
        f"**Week:** {week}\n"
        f"**Angle:** (pushed from production — edit if needed)\n"
        f"**Status:** Buffer\n"
        f"**Source date:** {date_filter or date.today().isoformat()}\n"
    )
    write(f"{slug}_meta.md", meta)

    if blog:
        copy(blog, f"{slug}_substack_post.md")
    else:
        print(f"    WARN: no blog — substack_post skipped")

    if script:
        copy(script, f"{slug}_youtube_script.md")
    else:
        print(f"    WARN: no YT script — youtube_script skipped")

    if deriv:
        social_text = build_social_copy(deriv)
        if social_text:
            write(f"{slug}_social_copy.md", social_text)
        else:
            print(f"    WARN: derivatives empty — social_copy skipped")
    else:
        print(f"    WARN: no derivatives dir — social_copy skipped")

    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Push produced content to buffer, or confirm it stays live."
    )
    parser.add_argument("--niche", default=None, choices=list(NICHE_MAP.keys()),
                        help="Single niche (omit for all 3 when using --auto)")
    parser.add_argument("--week", default=None, type=int, choices=[1, 2, 3, 4],
                        help="Force a specific week slot (skips auto-decide)")
    parser.add_argument("--auto", action="store_true",
                        help="Auto-decide: buffer if < 4 weeks, else stay live")
    parser.add_argument("--date", default=None, help="Production date YYYY-MM-DD (default: latest)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Overwrite existing buffer files")
    args = parser.parse_args()

    if not args.auto and args.week is None:
        parser.error("Provide --auto OR --week N")

    niches = [NICHE_MAP[args.niche]] if args.niche else ALL_NICHES
    dry = args.dry_run

    print(f"{'[DRY RUN] ' if dry else ''}Buffer check")
    print()

    buffered, live = [], []

    for niche in niches:
        depth = buffer_depth(niche)
        print(f"  {niche}: {depth}/{BUFFER_TARGET} weeks buffered")

        if args.week:
            week = args.week
            print(f"  → forcing week-{week}")
            push_niche(niche, week, args.date, dry, args.force)
            buffered.append(niche)
        else:
            # auto-decide
            if depth >= BUFFER_TARGET:
                print(f"  → buffer FULL — content stays live this week (no copy needed)")
                live.append(niche)
            else:
                week = next_empty_week(niche)
                if week is None:
                    print(f"  → ERROR: buffer shows {depth} but no empty week slot found")
                    continue
                print(f"  → buffer needs filling — pushing to week-{week}")
                if push_niche(niche, week, args.date, dry, args.force):
                    buffered.append(niche)
        print()

    print("─" * 50)
    if buffered:
        print(f"Buffered: {', '.join(buffered)}")
        if not dry:
            print("Next: Notion → Status = Script, note 'pushed to buffer [date]'")
    if live:
        print(f"Live (buffer full): {', '.join(live)} — use as this week's content")
    if dry:
        print("\nDry run — no files written.")


if __name__ == "__main__":
    main()
