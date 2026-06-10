#!/usr/bin/env python3
"""
generate_shorts_manifest.py — Auto-create shorts_manifest.json for each slug in a week.

Scans content/derivatives/{week}/ and matches each slug to its scene plan in
remotion/public/scene-plans/{week}/. Writes a 3-slot motion-only manifest.

On Wednesday, swap motion slots for clip slots once edit plans exist.

Usage:
  python3 scripts/generate_shorts_manifest.py --week 2026-W24
  python3 scripts/generate_shorts_manifest.py --week 2026-W24 --niche ds
  python3 scripts/generate_shorts_manifest.py --week 2026-W24 --dry-run
"""

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DERIVATIVES_ROOT = REPO / "content" / "derivatives"
SCENE_PLANS_ROOT = REPO / "remotion" / "public" / "scene-plans"

NICHE_KEYWORDS = {
    "ds": ["data-science", "data_science"],
    "life": ["life-self", "life_self"],
    "poetry": ["poetry-quotes", "poetry_quotes"],
}

NICHE_FROM_SLUG = {
    "data_science_tech": "ds",
    "life_self_dev": "life",
    "poetry_quotes": "poetry",
}


def detect_niche(slug: str) -> str | None:
    for marker, niche in NICHE_FROM_SLUG.items():
        if marker in slug:
            return niche
    return None


def find_scene_plan(week: str, date_prefix: str, niche: str) -> str | None:
    """
    Find non-overlay scene plan file for (week, date, niche).
    Returns path relative to remotion/public/ or None.
    """
    scene_dir = SCENE_PLANS_ROOT / week
    if not scene_dir.exists():
        return None

    keywords = NICHE_KEYWORDS.get(niche, [])
    candidates = []
    for f in scene_dir.iterdir():
        if not f.name.endswith(".json"):
            continue
        if "_overlay" in f.name:
            continue
        if not f.name.startswith(date_prefix):
            continue
        fname_lower = f.name.lower()
        if any(kw in fname_lower for kw in keywords):
            candidates.append(f)

    if not candidates:
        return None
    # Pick shortest name (most specific match over overlap variants)
    best = min(candidates, key=lambda f: len(f.name))
    # Return relative to remotion/public/
    return str(best.relative_to(REPO / "remotion" / "public"))


def build_manifest(scene_plan_file: str) -> list[dict]:
    return [
        {"slot": 0, "type": "motion", "scenePlanFile": scene_plan_file},
        {"slot": 1, "type": "motion", "scenePlanFile": scene_plan_file},
        {"slot": 2, "type": "motion", "scenePlanFile": scene_plan_file},
    ]


def process_week(week: str, niche_filter: str | None, dry_run: bool) -> int:
    week_dir = DERIVATIVES_ROOT / week
    if not week_dir.exists():
        print(f"ERROR: {week_dir} does not exist", file=sys.stderr)
        return 1

    slugs = sorted(d.name for d in week_dir.iterdir() if d.is_dir())
    if not slugs:
        print(f"No slugs found in {week_dir}")
        return 0

    errors = 0
    written = 0

    for slug in slugs:
        niche = detect_niche(slug)
        if niche is None:
            print(f"  SKIP {slug} (niche unknown)")
            continue
        if niche_filter and niche != niche_filter:
            continue

        date_prefix = slug[:10]  # YYYY-MM-DD
        scene_plan = find_scene_plan(week, date_prefix, niche)

        if scene_plan is None:
            print(f"  WARN {slug}: no scene plan found — skipping")
            errors += 1
            continue

        manifest = build_manifest(scene_plan)
        out_path = week_dir / slug / "shorts_manifest.json"

        if dry_run:
            print(f"  DRY  {slug}")
            print(f"       → {out_path.relative_to(REPO)}")
            print(f"       scene plan: {scene_plan}")
        else:
            out_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            print(f"  OK   {slug}")
            print(f"       → {out_path.relative_to(REPO)}")
            written += 1

    if not dry_run:
        print(f"\nWrote {written} manifest(s). Errors: {errors}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate shorts_manifest.json for a week")
    parser.add_argument("--week", required=True, help="ISO week, e.g. 2026-W24")
    parser.add_argument("--niche", choices=["ds", "life", "poetry"], help="Filter to one niche")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing")
    args = parser.parse_args()

    rc = process_week(args.week, args.niche, args.dry_run)
    sys.exit(rc)


if __name__ == "__main__":
    main()
