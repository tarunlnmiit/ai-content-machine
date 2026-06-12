#!/usr/bin/env python3
"""Render each overlay scene as a standalone MP4 and write a manifest CSV.

Usage:
    python3 scripts/render_overlay_scenes.py --week 2026-W24
    python3 scripts/render_overlay_scenes.py --week 2026-W24 --dry-run
    python3 scripts/render_overlay_scenes.py --week 2026-W24 --niche ds
"""
import argparse
import csv
import json
import subprocess
import sys
import time
import threading
from pathlib import Path
from typing import Optional

_print_lock = threading.Lock()

REPO_ROOT = Path(__file__).parent.parent
REMOTION_DIR = REPO_ROOT / "remotion"
SCENE_PLANS_DIR = REMOTION_DIR / "public" / "scene-plans"
PREVIEW_DIR = REMOTION_DIR / "public" / "scene-plans" / "preview"
FPS = 30

OVERLAY_PLAN_SUFFIXES = {
    "ds":      lambda week: f"2026-06-10_2026-06-10-data-science-tech-python-for-data-science-tutoria_overlay.json",
    "life":    lambda week: f"2026-06-10_2026-06-08-life-self-dev-the-simple-habit-that-changed-my-pr_overlay.json",
    "poetry":  lambda week: f"2026-06-08_2026-06-08-poetry-quotes-poetry-dips-its-fingers-in-every-co_overlay.json",
}


def find_overlay_plan(week: str, niche: str) -> Optional[Path]:
    week_dir = SCENE_PLANS_DIR / week
    if not week_dir.exists():
        return None
    suffix_fn = OVERLAY_PLAN_SUFFIXES.get(niche)
    if suffix_fn:
        candidate = week_dir / suffix_fn(week)
        if candidate.exists():
            return candidate
    # Fallback: glob for any overlay file containing the niche keyword
    niche_map = {"ds": "data-science", "life": "life-self-dev", "poetry": "poetry"}
    keyword = niche_map.get(niche, niche)
    matches = list(week_dir.glob(f"*{keyword}*_overlay.json"))
    return matches[0] if matches else None


def output_dir(week: str) -> Path:
    d = REPO_ROOT / "output" / "animations" / week / "overlay-scenes"
    d.mkdir(parents=True, exist_ok=True)
    return d


def render_scene(scene: dict, niche: str, week: str, dry_run: bool) -> tuple[str, bool, float, str]:
    scene_id = scene.get("sceneId", "unknown")
    component = scene.get("componentName", "Unknown")
    duration_sec = scene.get("durationSec", 6)
    script = scene.get("script", "")

    # Write temp scene plan JSON (single-scene array)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    preview_filename = f"{niche}_{scene_id}.json"
    preview_path = PREVIEW_DIR / preview_filename
    preview_path.write_text(json.dumps([scene], ensure_ascii=False, indent=2))

    out_filename = f"{niche}_{scene_id}_{component}.mp4"
    out_file = output_dir(week) / out_filename

    props = {"scenePlanFile": f"scene-plans/preview/{preview_filename}"}

    cmd = [
        "npx", "remotion", "render", "ScenePreview", str(out_file),
        "--props", json.dumps(props),
        "--log", "verbose",
    ]

    label = f"{niche}/{scene_id} ({component})"
    with _print_lock:
        print(f"  {'[DRY-RUN] ' if dry_run else ''}render {label} → {out_filename}")

    if dry_run:
        return scene_id, True, 0.0, out_filename

    t0 = time.time()
    proc = subprocess.Popen(
        cmd, cwd=str(REMOTION_DIR),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    for line in proc.stdout:
        with _print_lock:
            print(f"    [{label}] {line}", end="")
    proc.wait()
    elapsed = time.time() - t0

    if proc.returncode != 0:
        with _print_lock:
            print(f"  [FAIL] {label} ({elapsed:.1f}s)")
        return scene_id, False, elapsed, out_filename

    with _print_lock:
        print(f"  [OK]   {label} ({elapsed:.1f}s)")
    return scene_id, True, elapsed, out_filename


def write_manifest(rows: list[dict], week: str) -> Path:
    out = output_dir(week) / "manifest.csv"
    fieldnames = ["niche", "scene_id", "component_name", "duration_sec", "output_file", "script"]
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Render overlay scenes as standalone MP4s")
    parser.add_argument("--week", required=True, help="ISO week, e.g. 2026-W24")
    parser.add_argument("--niche", choices=["ds", "life", "poetry"], help="Only render one niche")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without rendering")
    args = parser.parse_args()

    niches = [args.niche] if args.niche else ["ds", "life", "poetry"]

    all_scenes: list[tuple[str, dict]] = []  # (niche, scene)
    for niche in niches:
        plan_path = find_overlay_plan(args.week, niche)
        if not plan_path:
            print(f"  [WARN] No overlay plan found for {niche} in {args.week}")
            continue
        scenes = json.loads(plan_path.read_text())
        print(f"  {niche}: {len(scenes)} scenes from {plan_path.name}")
        for scene in scenes:
            all_scenes.append((niche, scene))

    if not all_scenes:
        print("No scenes found. Exiting.")
        sys.exit(1)

    print(f"\n── Rendering {len(all_scenes)} scenes ──")
    manifest_rows: list[dict] = []
    ok = fail = 0

    for niche, scene in all_scenes:
        scene_id, success, elapsed, out_filename = render_scene(scene, niche, args.week, args.dry_run)
        if success:
            ok += 1
            manifest_rows.append({
                "niche": niche,
                "scene_id": scene_id,
                "component_name": scene.get("componentName", ""),
                "duration_sec": scene.get("durationSec", 6),
                "output_file": out_filename,
                "script": scene.get("script", ""),
            })
        else:
            fail += 1

    manifest_path = write_manifest(manifest_rows, args.week)
    print(f"\n── Summary ──")
    print(f"   OK:      {ok}/{len(all_scenes)}")
    if fail:
        print(f"   FAIL:    {fail}")
    print(f"   Manifest: {manifest_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
