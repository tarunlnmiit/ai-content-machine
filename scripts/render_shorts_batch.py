#!/usr/bin/env python3
"""Render all shorts for a given week + niche.

Each slug directory under content/derivatives/{week}/ may contain a
shorts_manifest.json that lists clip-based and motion-graphic short slots.

Usage:
    python3 scripts/render_shorts_batch.py --week 2026-W24 --niche ds
    python3 scripts/render_shorts_batch.py --week 2026-W24 --niche life --dry-run

shorts_manifest.json schema:
    [
      {"slot": 0, "type": "clip",   "editPlanFile": "edit-plans/2026-W24/slug.json",
       "clipStartSec": 10, "clipEndSec": 70},
      {"slot": 1, "type": "motion", "scenePlanFile": "scene-plans/slug_s01.json",
       "audioFile": "audio/slug_s01.mp3"},
      ...
    ]
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO_ROOT = Path(__file__).parent.parent
REMOTION_DIR = REPO_ROOT / "remotion"
DERIVATIVES_DIR = REPO_ROOT / "content" / "derivatives"

NICHE_MOTION_COMP = {
    "ds": "DSMotionShort",
    "life": "LifeMotionShort",
    "poetry": "PoetryMotionShort",
}


def output_dir(week: str) -> Path:
    d = REPO_ROOT / "output" / "animations" / week
    d.mkdir(parents=True, exist_ok=True)
    return d


def render_slot(
    slot: dict,
    slug: str,
    week: str,
    niche: str,
    dry_run: bool,
) -> tuple[str, bool, float]:
    slot_id = f"{slug}_s{slot['slot']:02d}"
    out_file = output_dir(week) / f"{slot_id}.mp4"

    if slot["type"] == "clip":
        composition = "ShortClip"
        props = {
            "editPlanFile": slot["editPlanFile"],
            "clipStartSec": slot["clipStartSec"],
            "clipEndSec": slot["clipEndSec"],
        }
    else:
        composition = NICHE_MOTION_COMP.get(niche, "DSMotionShort")
        props = {"scenePlanFile": slot["scenePlanFile"]}
        if "audioFile" in slot:
            props["audioFile"] = slot["audioFile"]

    cmd = [
        "npx", "remotion", "render", composition, str(out_file),
        "--props", json.dumps(props),
    ]

    print(f"  {'[DRY-RUN] ' if dry_run else ''}render {composition} slot {slot['slot']} → {out_file.name}")
    if dry_run:
        return slot_id, True, 0.0

    t0 = time.time()
    result = subprocess.run(cmd, cwd=str(REMOTION_DIR), capture_output=True, text=True)
    elapsed = time.time() - t0

    if result.returncode != 0:
        print(f"  [FAIL] {slot_id}: {result.stderr[-400:]}")
        return slot_id, False, elapsed

    size_mb = out_file.stat().st_size / 1_048_576 if out_file.exists() else 0
    print(f"  [OK] {slot_id} — {elapsed:.1f}s — {size_mb:.1f} MB")
    return slot_id, True, elapsed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--week", required=True, help="ISO week, e.g. 2026-W24")
    parser.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--concurrency", type=int, default=3)
    args = parser.parse_args()

    week_dir = DERIVATIVES_DIR / args.week
    if not week_dir.exists():
        sys.exit(f"No derivatives found at {week_dir}")

    # Collect all slug dirs for this niche that have a shorts_manifest.json
    manifests: list[tuple[str, list[dict]]] = []
    for slug_dir in sorted(week_dir.iterdir()):
        if not slug_dir.is_dir():
            continue
        manifest_file = slug_dir / "shorts_manifest.json"
        if not manifest_file.exists():
            continue
        slots: list[dict] = json.loads(manifest_file.read_text())
        # Filter to slots matching the niche (if manifest has niche field per slot)
        # Or just use all slots in the directory since we're already filtering by niche via args
        manifests.append((slug_dir.name, slots))

    if not manifests:
        print(f"No shorts_manifest.json found in {week_dir}")
        print(f"Create content/derivatives/{args.week}/{{slug}}/shorts_manifest.json to schedule shorts.")
        sys.exit(0)

    all_slots = [(slug, slot) for slug, slots in manifests for slot in slots]

    print(f"\n── Remotion render_shorts_batch {args.week} niche={args.niche} ──")
    print(f"   {len(all_slots)} slot(s) across {len(manifests)} slug(s)  concurrency={args.concurrency}")

    results: list[tuple[str, bool, float]] = []

    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {
            pool.submit(render_slot, slot, slug, args.week, args.niche, args.dry_run): (slug, slot)
            for slug, slot in all_slots
        }
        for fut in as_completed(futures):
            results.append(fut.result())

    ok = [r for r in results if r[1]]
    fail = [r for r in results if not r[1]]
    total_time = sum(r[2] for r in results)

    print(f"\n── Summary ─────────────────────────────────────────────")
    print(f"   OK:   {len(ok)}/{len(results)}")
    if fail:
        print(f"   FAIL: {', '.join(r[0] for r in fail)}")
    if not args.dry_run:
        print(f"   Time: {total_time:.1f}s total (wall clock faster with concurrency)")


if __name__ == "__main__":
    main()
