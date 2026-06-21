#!/usr/bin/env python3
"""
detect_short_sections.py — From a VOICEOVER transcript, auto-detect a small set of
SELF-COMPLETE sections that stand alone as Shorts/Reels. Voiceover-first lane only.

Each section is a {startSec, endSec, angle}. The LLM picks the strongest standalone
segments; we then snap start/end to caption boundaries and enforce duration bounds.

Usage:
  python3 scripts/detect_short_sections.py \\
    --captions remotion/public/captions/2026-W26/2026-06-22_ds_slug.captions.json \\
    --niche ds --week 2026-W26 --slug 2026-06-22_ds_slug

Output: content/derivatives/{week}/{slug}/short_sections.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.claude_cli import call_claude
from lib.niche_config import model_for

CAPTIONS_ROOT = REPO / "remotion" / "public" / "captions"
DERIVATIVES_ROOT = REPO / "content" / "derivatives"

DEFAULT_MIN_SEC = 15.0
DEFAULT_MAX_SEC = 90.0
DEFAULT_MAX_COUNT = 5

NICHE_LABELS = {
    "ds": "Data Science / Python / Tech",
    "life": "Life & Self-Development / Habits / Mindset",
    "poetry": "Poetry / Quotes / Reflection",
}


def load_captions(captions_path: Path) -> list[dict]:
    data = json.loads(captions_path.read_text(encoding="utf-8"))
    return [c for c in data if isinstance(c, dict)] if isinstance(data, list) else []


def format_for_prompt(captions: list[dict]) -> str:
    lines = []
    for c in captions:
        start = c.get("startMs", 0) / 1000
        end = c.get("endMs", 0) / 1000
        lines.append(f"[{start:.1f}s-{end:.1f}s] {c.get('text', '')}")
    return "\n".join(lines)


def resolve_captions(args) -> Path:
    if args.captions:
        p = Path(args.captions)
        return p if p.is_absolute() else REPO / p
    return CAPTIONS_ROOT / args.week / f"{args.slug}.captions.json"


def build_prompt(captions_text: str, niche: str, min_sec: float, max_sec: float, max_count: int) -> str:
    label = NICHE_LABELS.get(niche, niche)
    return f"""You are a short-form video editor for the niche: {label}.

Below is a timestamped voiceover transcript ([startSec-endSec] text). Pick the FEW strongest
SELF-COMPLETE sections that work as standalone Shorts/Reels.

Hard rules:
- A section MUST make full sense cold, to a viewer who saw nothing else. No "as I said", "earlier",
  "part 2", "in this video". Self-contained hook + payoff.
- Each section duration MUST be between {min_sec:.0f} and {max_sec:.0f} seconds.
- Return AT MOST {max_count} sections — only the strongest. Fewer is fine. Quality over count.
- startSec/endSec must align to the transcript timestamps (use real segment boundaries).
- Sections must NOT overlap.

Return ONLY a JSON array, each object:
{{
  "startSec": 0.0,
  "endSec": 42.0,
  "angle": "one-line hook describing what makes this clip stand alone"
}}

No prose, no markdown fences.

TRANSCRIPT:
{captions_text[:9000]}
"""


def extract_json(raw: str) -> list:
    raw = re.sub(r"```(?:json)?", "", raw)
    i = raw.find("[")
    if i < 0:
        raise json.JSONDecodeError("No JSON array found", raw, 0)
    result, _ = json.JSONDecoder().raw_decode(raw, i)
    return result


def snap_to_boundaries(start: float, end: float, captions: list[dict]) -> tuple[float, float]:
    """Snap start to the nearest caption start and end to the nearest caption end."""
    starts = [c.get("startMs", 0) / 1000 for c in captions]
    ends = [c.get("endMs", 0) / 1000 for c in captions]
    if not starts:
        return start, end
    snapped_start = min(starts, key=lambda s: abs(s - start))
    snapped_end = min(ends, key=lambda e: abs(e - end))
    return snapped_start, snapped_end


def main() -> None:
    parser = argparse.ArgumentParser(description="Voiceover transcript → self-complete Short sections")
    parser.add_argument("--captions", default=None, help="Captions JSON (auto-detected from --week/--slug if omitted)")
    parser.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    parser.add_argument("--week", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--min-sec", type=float, default=DEFAULT_MIN_SEC)
    parser.add_argument("--max-sec", type=float, default=DEFAULT_MAX_SEC)
    parser.add_argument("--max-count", type=int, default=DEFAULT_MAX_COUNT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    cap_path = resolve_captions(args)
    if not cap_path.exists():
        sys.exit(f"ERROR: captions not found: {cap_path}")

    out_path = DERIVATIVES_ROOT / args.week / args.slug / "short_sections.json"
    if out_path.exists() and not args.force and not args.dry_run:
        print(f"[skip] {out_path.relative_to(REPO)} already exists (--force to overwrite)")
        return

    captions = load_captions(cap_path)
    if not captions:
        sys.exit(f"ERROR: empty captions in {cap_path}")

    print(f"Detecting short sections for {args.slug} ({args.niche})...", file=sys.stderr)
    raw = call_claude(
        build_prompt(format_for_prompt(captions), args.niche, args.min_sec, args.max_sec, args.max_count),
        cache=not args.no_cache,
        model=model_for("scene_plan"),
        timeout=180,
    )
    sections = extract_json(raw)
    if not isinstance(sections, list):
        sys.exit("ERROR: expected a JSON array of sections")

    # Snap + enforce bounds + drop overlaps.
    clean: list[dict] = []
    last_end = -1.0
    for s in sections:
        try:
            start = float(s["startSec"])
            end = float(s["endSec"])
        except (KeyError, TypeError, ValueError):
            continue
        start, end = snap_to_boundaries(start, end, captions)
        dur = end - start
        if dur < args.min_sec or dur > args.max_sec:
            print(f"  [drop] section {start:.1f}-{end:.1f}s ({dur:.1f}s) out of bounds", file=sys.stderr)
            continue
        if start < last_end:
            print(f"  [drop] section {start:.1f}-{end:.1f}s overlaps previous", file=sys.stderr)
            continue
        clean.append({"startSec": round(start, 2), "endSec": round(end, 2), "angle": str(s.get("angle", "")).strip()})
        last_end = end
        if len(clean) >= args.max_count:
            break

    print(f"\n{len(clean)} self-complete section(s):")
    for i, s in enumerate(clean):
        print(f"  {i+1}. {s['startSec']:.1f}-{s['endSec']:.1f}s ({s['endSec']-s['startSec']:.0f}s) — \"{s['angle'][:60]}\"")

    if args.dry_run:
        print("\n[dry-run] not writing.")
        print(json.dumps(clean, indent=2))
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(clean, indent=2), encoding="utf-8")
    print(f"\n✓ Written: {out_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
