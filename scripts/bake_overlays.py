#!/usr/bin/env python3
"""Bake rendered overlay scenes onto a long-form video using ffmpeg.

Reads the overlay scene plan for a given week + niche, finds the pre-rendered
overlay clips from render_overlay_scenes.py, and composites each one onto the
base long-form video at the correct timestamp.

Layout mapping:
  fullscreen  → 1920×1080 at (0, 0) — covers full frame
  panel-left  →  960×1080 at (0, 0) — left half only, talking head visible right
  panel-right →  960×1080 at (960, 0) — right half only, talking head visible left
  panel-top   → 1920×540  at (0, 0) — top half only

Audio from the base video plays uninterrupted throughout.

Usage:
  python3 scripts/bake_overlays.py --week 2026-W22 --niche ds
  python3 scripts/bake_overlays.py --week 2026-W22 --niche ds --dry-run
  python3 scripts/bake_overlays.py --week 2026-W22 --niche ds \\
      --video assets/video/edited/2026-W22/slug.mp4

Output:
  assets/video/edited/{week}/{slug}_baked.mp4
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from render_overlay_scenes import find_overlay_plan, output_dir as overlay_output_dir

SCENE_PLANS_ROOT = REPO / "remotion" / "public" / "scene-plans"
VIDEO_DIR = REPO / "assets" / "video" / "edited"

NICHE_SLUG_FRAGMENT = {
    "ds": "data_science",
    "life": "life_self_dev",
    "poetry": "poetry_quotes",
}

LAYOUT_CONFIG = {
    "fullscreen":  {"w": 1920, "h": 1080, "x": 0,   "y": 0},
    "panel-left":  {"w": 960,  "h": 1080, "x": 0,   "y": 0},
    "panel-right": {"w": 960,  "h": 1080, "x": 960, "y": 0},
    "panel-top":   {"w": 1920, "h": 540,  "x": 0,   "y": 0},
}
DEFAULT_LAYOUT = LAYOUT_CONFIG["fullscreen"]


def find_base_video(week: str, niche: str, video_arg: str | None) -> Path:
    if video_arg:
        p = Path(video_arg)
        return p if p.is_absolute() else REPO / p

    week_dir = VIDEO_DIR / week
    if not week_dir.exists():
        # Fallback: flat dir
        week_dir = VIDEO_DIR
    keyword = NICHE_SLUG_FRAGMENT.get(niche, niche)
    matches = list(week_dir.glob(f"*{keyword}*.mp4"))
    matches = [m for m in matches if "_baked" not in m.name and "_reel" not in m.name]
    if not matches:
        matches = list(VIDEO_DIR.glob(f"*{keyword}*.mp4"))
        matches = [m for m in matches if "_baked" not in m.name and "_reel" not in m.name]
    if not matches:
        return None
    return sorted(matches)[0]


def find_overlay_clip(scenes_dir: Path, niche: str, scene_id: str, component: str) -> Path | None:
    name = f"{niche}_{scene_id}_{component}.mp4"
    p = scenes_dir / name
    return p if p.exists() else None


def build_ffmpeg_cmd(base: Path, scenes: list[dict], scenes_dir: Path,
                     niche: str, output: Path) -> list[str] | None:
    inputs = ["-i", str(base)]
    scale_parts = []
    overlay_parts = []
    valid_scenes = []

    for scene in scenes:
        scene_id = scene.get("sceneId", "")
        component = scene.get("componentName", "")
        at_sec = scene.get("atSec")
        dur_sec = scene.get("durationSec", 6)
        layout = scene.get("layout", "fullscreen")

        if at_sec is None:
            print(f"  [skip] {scene_id}: no atSec — cannot place in timeline")
            continue

        clip = find_overlay_clip(scenes_dir, niche, scene_id, component)
        if not clip:
            print(f"  [skip] {scene_id}: clip not found in {scenes_dir}")
            continue

        cfg = LAYOUT_CONFIG.get(layout, DEFAULT_LAYOUT)
        end_sec = at_sec + dur_sec
        idx = len(valid_scenes) + 1

        inputs += ["-i", str(clip)]
        scale_parts.append(
            f"[{idx}:v]scale={cfg['w']}:{cfg['h']}[ov{idx}]"
        )
        valid_scenes.append((idx, cfg, at_sec, end_sec))

    if not valid_scenes:
        return None

    # Chain overlay filters
    prev = "0:v"
    for i, (idx, cfg, at_sec, end_sec) in enumerate(valid_scenes):
        out_label = f"v{i + 1}"
        overlay_parts.append(
            f"[{prev}][ov{idx}]overlay={cfg['x']}:{cfg['y']}:"
            f"enable='between(t,{at_sec},{end_sec})'[{out_label}]"
        )
        prev = out_label

    filter_complex = "; ".join(scale_parts + overlay_parts)

    cmd = [
        "/opt/homebrew/bin/ffmpeg",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", f"[{prev}]",
        "-map", "0:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "copy",
        "-y", str(output),
    ]
    return cmd


def main() -> None:
    parser = argparse.ArgumentParser(description="Bake overlay scenes onto long-form video")
    parser.add_argument("--week", required=True, help="ISO week, e.g. 2026-W22")
    parser.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    parser.add_argument("--video", default=None, help="Explicit path to base video (overrides auto-detect)")
    parser.add_argument("--dry-run", action="store_true", help="Print ffmpeg command, don't run")
    args = parser.parse_args()

    plan_path = find_overlay_plan(args.week, args.niche)
    if not plan_path:
        sys.exit(f"No overlay plan found for {args.niche} in {args.week}")
    print(f"Plan: {plan_path.relative_to(REPO)}")

    scenes = json.loads(plan_path.read_text())

    base = find_base_video(args.week, args.niche, args.video)
    if not base or not base.exists():
        sys.exit(f"Base video not found for niche={args.niche} week={args.week}. Use --video to specify path.")
    print(f"Base: {base.relative_to(REPO)}")

    scenes_dir = overlay_output_dir(args.week)
    if not scenes_dir.exists():
        sys.exit(f"Overlay scenes dir not found: {scenes_dir}\nRun render_overlay_scenes.py first.")

    slug = base.stem
    output = base.parent / f"{slug}_baked.mp4"
    print(f"Output: {output.relative_to(REPO)}")
    print(f"Scenes: {len(scenes)} total")

    cmd = build_ffmpeg_cmd(base, scenes, scenes_dir, args.niche, output)
    if not cmd:
        sys.exit("No valid overlay scenes to bake — check that render_overlay_scenes.py ran successfully.")

    if args.dry_run:
        print("\n[DRY-RUN] ffmpeg command:")
        print(" \\\n  ".join(cmd))
        return

    print(f"\nBaking {args.niche.upper()} overlays onto long-form...")
    t0 = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - t0

    if result.returncode != 0:
        print(f"[FAIL] ffmpeg error ({elapsed:.1f}s):")
        print(result.stderr[-500:])
        sys.exit(1)

    size_mb = output.stat().st_size / 1_048_576
    print(f"[OK] {output.name} — {elapsed:.1f}s — {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
