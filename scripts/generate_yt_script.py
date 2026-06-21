#!/usr/bin/env python3
"""
generate_yt_script.py — Turn a recorded VOICEOVER transcript into a YouTube long-form
script (a deliverable doc). Voiceover-first lane only.

This is a DELIVERABLE, not a B-roll source — B-roll keywords come from the transcript
directly (see fetch_videos.py --captions). The script gives you a clean reference doc
(title, hook, sections, suggested on-screen beats) for the YouTube description/structure.

Usage:
  python3 scripts/generate_yt_script.py \\
    --captions remotion/public/captions/2026-W26/2026-06-22_ds_slug.captions.json \\
    --niche ds --week 2026-W26 --slug 2026-06-22_ds_slug

Output: content/scripts/{week}/{slug}_yt.md
"""

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.claude_cli import call_claude
from lib.niche_config import model_for

SCRIPTS_ROOT = REPO / "content" / "scripts"
CAPTIONS_ROOT = REPO / "remotion" / "public" / "captions"

NICHE_LABELS = {
    "ds": "Data Science / Python / Tech",
    "life": "Life & Self-Development / Habits / Mindset",
    "poetry": "Poetry / Quotes / Reflection",
}

BANNED_WORDS = ["In conclusion", "Dive into", "Leverage", "Game-changer", "Synergy"]


def transcript_text(captions_path: Path) -> str:
    data = json.loads(captions_path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return " ".join(str(c.get("text", "")).strip() for c in data if isinstance(c, dict))
    return ""


def resolve_captions(args) -> Path:
    if args.captions:
        p = Path(args.captions)
        return p if p.is_absolute() else REPO / p
    # auto-detect by week + slug
    return CAPTIONS_ROOT / args.week / f"{args.slug}.captions.json"


def build_prompt(transcript: str, niche: str) -> str:
    label = NICHE_LABELS.get(niche, niche)
    banned = ", ".join(f'"{w}"' for w in BANNED_WORDS)
    return f"""You are a YouTube scriptwriter for a creator in the niche: {label}.

The creator already RECORDED a voiceover (audio-only — no face on camera). Below is the
verbatim transcript. Reverse-engineer a clean YouTube long-form SCRIPT document from it so it
can serve as the canonical reference (and feed the YouTube description/structure).

Rules:
- Faithful to the transcript — do NOT invent claims, stats, or anecdotes not present in it.
- Voice: analytical but warm, personal, no jargon without context.
- NEVER use these banned words/phrases: {banned}.
- Mark suggested on-screen beats with [BROLL: ...] cues where a visual would help — but keep
  them light; the actual B-roll is fetched separately.
- Include a strong title, a 1–2 sentence hook, then sections with short headers, then a closing
  line / call to action.

Return Markdown only, in this shape:

# <title>

**Hook:** <1–2 sentence hook>

## <section header>
<script prose, with [BROLL: ...] cues inline>

## <section header>
...

**Close:** <closing line / CTA>

TRANSCRIPT:
{transcript[:8000]}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Voiceover transcript → YouTube long-form script deliverable")
    parser.add_argument("--captions", default=None, help="Captions JSON path (auto-detected from --week/--slug if omitted)")
    parser.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    parser.add_argument("--week", required=True, help="ISO week e.g. 2026-W26")
    parser.add_argument("--slug", required=True, help="Full slug e.g. 2026-06-22_ds_slug")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--force", action="store_true", help="Overwrite existing script")
    args = parser.parse_args()

    cap_path = resolve_captions(args)
    if not cap_path.exists():
        sys.exit(f"ERROR: captions not found: {cap_path}")

    out_path = SCRIPTS_ROOT / args.week / f"{args.slug}_yt.md"
    if out_path.exists() and not args.force and not args.dry_run:
        print(f"[skip] {out_path.relative_to(REPO)} already exists (--force to overwrite)")
        return

    transcript = transcript_text(cap_path)
    if not transcript:
        sys.exit(f"ERROR: empty transcript in {cap_path}")

    print(f"Generating YouTube script for {args.slug} ({args.niche})...", file=sys.stderr)
    script_md = call_claude(
        build_prompt(transcript, args.niche),
        cache=not args.no_cache,
        model=model_for("buffer"),
        timeout=300,
    ).strip()

    if args.dry_run:
        print(script_md)
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(script_md + "\n", encoding="utf-8")
    print(f"✓ Written: {out_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
