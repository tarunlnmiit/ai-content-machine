#!/usr/bin/env python3
"""Render all edit plans for a given ISO week.

Usage:
    python3 scripts/render_week.py --week 2026-W24
    python3 scripts/render_week.py --week 2026-W24 --dry-run
    python3 scripts/render_week.py --week 2026-W24 --concurrency 2
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

REPO_ROOT = Path(__file__).parent.parent
REMOTION_DIR = REPO_ROOT / "remotion"
EDIT_PLANS_DIR = REMOTION_DIR / "public" / "edit-plans"


def load_plan(plan_file: Path) -> dict:
    return json.loads(plan_file.read_text())


def output_dir(week: str) -> Path:
    d = REPO_ROOT / "output" / "animations" / week
    d.mkdir(parents=True, exist_ok=True)
    return d


def render_plan(plan_file: Path, week: str, dry_run: bool) -> tuple[str, bool, float]:
    plan = load_plan(plan_file)
    slug = plan.get("slug", plan_file.stem)
    output_size = plan.get("outputSize", "16x9")

    if output_size == "9x16":
        composition = "ShortClip"
        extra_props = {
            "editPlanFile": f"edit-plans/{week}/{plan_file.name}",
            "clipStartSec": 0,
            "clipEndSec": plan.get("durationSec", 60),
        }
    else:
        composition = "CourseLesson"
        extra_props = {"editPlanFile": f"edit-plans/{week}/{plan_file.name}"}

    out_file = output_dir(week) / f"{slug}.mp4"
    props_json = json.dumps({**extra_props})

    cmd = [
        "npx", "remotion", "render", composition, str(out_file),
        "--props", props_json,
        "--log", "verbose",
    ]

    print(f"  {'[DRY-RUN] ' if dry_run else ''}render {composition} → {out_file.name}")
    if dry_run:
        return slug, True, 0.0

    t0 = time.time()
    result = subprocess.run(cmd, cwd=str(REMOTION_DIR), capture_output=True, text=True)
    elapsed = time.time() - t0

    if result.returncode != 0:
        print(f"  [FAIL] {slug}: {result.stderr[-500:]}")
        return slug, False, elapsed

    size_mb = out_file.stat().st_size / 1_048_576 if out_file.exists() else 0
    print(f"  [OK] {slug} — {elapsed:.1f}s — {size_mb:.1f} MB")
    return slug, True, elapsed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--week", required=True, help="ISO week, e.g. 2026-W24")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--concurrency", type=int, default=1)
    args = parser.parse_args()

    week_dir = EDIT_PLANS_DIR / args.week
    if not week_dir.exists():
        sys.exit(f"No edit plans found at {week_dir}")

    plans = sorted(week_dir.glob("*.json"))
    if not plans:
        sys.exit(f"No *.json files in {week_dir}")

    print(f"\n── Remotion render_week {args.week} ──────────────────────────")
    print(f"   {len(plans)} plan(s) found  concurrency={args.concurrency}")

    results: list[tuple[str, bool, float]] = []

    if args.concurrency > 1:
        with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            futures = {
                pool.submit(render_plan, p, args.week, args.dry_run): p for p in plans
            }
            for fut in as_completed(futures):
                results.append(fut.result())
    else:
        for plan in plans:
            results.append(render_plan(plan, args.week, args.dry_run))

    ok = [r for r in results if r[1]]
    fail = [r for r in results if not r[1]]
    total_time = sum(r[2] for r in results)

    print(f"\n── Summary ────────────────────────────────────────────────")
    print(f"   OK:   {len(ok)}/{len(results)}")
    if fail:
        print(f"   FAIL: {', '.join(r[0] for r in fail)}")
    if not args.dry_run:
        print(f"   Time: {total_time:.1f}s total")


if __name__ == "__main__":
    main()
