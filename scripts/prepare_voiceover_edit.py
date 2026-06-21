#!/usr/bin/env python3
"""Build a Remotion EditPlan for the VOICEOVER-FIRST (audio-only) lane.

Unlike prepare_remotion_edit.py (talking head), there is no face footage. The voiceover
audio is the spine; a full-screen B-roll montage tiles the whole timeline; overlay scenes
sit on top. Captions are NOT baked here — hyperframes_render.py adds them later.

Builds ONE plan (long-form OR a single short). The orchestrator run_voiceover_week.py calls
this once per long-form and once per detected short section.

Usage (long-form):
  python3 scripts/prepare_voiceover_edit.py \\
    --audio assets/audio/2026-W26/2026-06-22_ds_slug_voiceover.wav \\
    --broll-dir assets/videos/2026-06-22_ds_slug \\
    --scene-plan scene-plans/2026-W26/2026-06-22_ds_slug_voiceover.json \\
    --niche ds --week 2026-W26 --slug 2026-06-22_ds_slug --output-size 16x9

Output: remotion/public/edit-plans/{week}/{slug}.json
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
REMOTION_PUBLIC = REPO / "remotion" / "public"

FFMPEG_BIN = "/opt/homebrew/bin/ffmpeg"
FFPROBE_BIN = "/opt/homebrew/bin/ffprobe"

DEFAULT_SLOT_SEC = 6.0  # length of each B-roll montage slot; clips cycle to fill duration
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif"}


def probe_duration(media: Path) -> float:
    out = subprocess.run(
        [FFPROBE_BIN, "-v", "quiet", "-print_format", "json", "-show_format", str(media)],
        capture_output=True, text=True,
    ).stdout
    try:
        return float(json.loads(out)["format"]["duration"])
    except Exception:
        return 0.0


def default_grading(niche: str) -> dict:
    if niche == "ds":
        return {"saturate": 1.10, "hueRotate": 3, "contrast": 1.08,
                "brightness": 1.0, "overlayColor": "rgba(120, 180, 255, 0.05)"}
    return {"saturate": 1.18, "hueRotate": -3, "contrast": 1.06,
            "brightness": 1.02, "overlayColor": "rgba(255, 180, 120, 0.05)"}


def convert_audio(audio: Path, week: str, slug: str) -> str:
    """Loudnorm the voiceover to m4a under remotion/public/audio/. Returns staticFile path."""
    dst = REMOTION_PUBLIC / "audio" / week / f"{slug}.m4a"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        r = subprocess.run([
            FFMPEG_BIN, "-i", str(audio),
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-c:a", "aac", "-b:a", "192k", str(dst), "-y",
        ], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  ffmpeg audio convert error: {r.stderr[-400:]}", file=sys.stderr)
    return f"audio/{week}/{slug}.m4a"


def copy_broll(broll_dir: Path, week: str, slug: str) -> list[Path]:
    """Copy downloaded clips into remotion/public/broll/{week}/{slug}/, return dst paths in order."""
    dst_dir = REMOTION_PUBLIC / "broll" / week / slug
    dst_dir.mkdir(parents=True, exist_ok=True)

    map_file = broll_dir / "VIDEO_MAP.json"
    ordered: list[Path] = []
    if map_file.exists():
        vid_map = json.loads(map_file.read_text())
        names = [n for n, m in vid_map.items() if m.get("downloaded") and (broll_dir / n).exists()]
    else:
        names = [p.name for p in sorted(broll_dir.glob("*")) if p.suffix.lower() in (IMAGE_EXTS | {".mp4", ".mov"})]

    for i, name in enumerate(names):
        src = broll_dir / name
        dst = dst_dir / f"cue-{i}{src.suffix}"
        shutil.copy2(src, dst)
        ordered.append(dst)
    return ordered


def build_montage(clip_paths: list[Path], total_sec: float, week: str, slug: str,
                  slot_sec: float = DEFAULT_SLOT_SEC) -> list[dict]:
    """Tile clips across [0, total_sec] with no gaps; clips cycle if fewer than slots."""
    if not clip_paths or total_sec <= 0:
        return []
    cues: list[dict] = []
    t = 0.0
    i = 0
    n = len(clip_paths)
    while t < total_sec - 0.01:
        dur = min(slot_sec, total_sec - t)
        clip = clip_paths[i % n]
        cues.append({
            "id": f"cue-{i}",
            "description": "voiceover b-roll montage",
            "clipFile": f"broll/{week}/{slug}/{clip.name}",
            "startSec": round(t, 2),
            "durationSec": round(dur, 2),
        })
        t += dur
        i += 1
    return cues


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a voiceover-lane EditPlan (audio + B-roll montage + overlays)")
    parser.add_argument("--audio", required=True, help="Voiceover audio for THIS plan (full or a cut section)")
    parser.add_argument("--broll-dir", required=True, help="Dir with downloaded clips + VIDEO_MAP.json")
    parser.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    parser.add_argument("--week", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--scene-plan", default=None, help="Overlay scene plan path relative to remotion/public/ (with atSec set)")
    parser.add_argument("--output-size", default="16x9", choices=["16x9", "9x16", "1x1"])
    parser.add_argument("--captions", default=None, help="Captions path relative to remotion/public/ (for the captionsFile field)")
    parser.add_argument("--slot-sec", type=float, default=DEFAULT_SLOT_SEC)
    args = parser.parse_args()

    audio = Path(args.audio)
    if not audio.is_absolute():
        audio = REPO / audio
    if not audio.exists():
        sys.exit(f"ERROR: audio not found: {audio}")

    broll_dir = Path(args.broll_dir)
    if not broll_dir.is_absolute():
        broll_dir = REPO / broll_dir
    if not broll_dir.exists():
        sys.exit(f"ERROR: broll dir not found: {broll_dir}")

    print(f"\n=== Voiceover edit plan: {args.slug} ({args.output_size}) ===")

    duration = probe_duration(audio)
    if duration <= 0:
        sys.exit(f"ERROR: could not probe audio duration for {audio}")
    print(f"[audio] duration {duration:.1f}s")

    audio_file = convert_audio(audio, args.week, args.slug)
    clip_paths = copy_broll(broll_dir, args.week, args.slug)
    print(f"[broll] {len(clip_paths)} clip(s) copied")
    montage = build_montage(clip_paths, duration, args.week, args.slug, args.slot_sec)
    print(f"[montage] {len(montage)} slot(s) tiling {duration:.1f}s")

    scene_plan_file = None
    if args.scene_plan:
        sp = REMOTION_PUBLIC / args.scene_plan
        if sp.exists():
            scene_plan_file = args.scene_plan
        else:
            print(f"[scenes] scene plan not found at {args.scene_plan}, skipping overlays", file=sys.stderr)

    captions_file = args.captions or ""

    plan = {
        "slug": args.slug,
        "niche": args.niche,
        "kind": "voiceover",
        "audioFile": audio_file,
        "durationSec": round(duration, 2),
        "silenceTrimStartSec": 0.0,
        "silenceTrimEndSec": round(duration, 2),
        "brollCues": montage,
        "captionsFile": captions_file,
        "showSubtitles": False,  # captions are added by hyperframes, not Remotion
        **({"scenePlanFile": scene_plan_file} if scene_plan_file else {}),
        "colorGrading": default_grading(args.niche),
        "outputSize": args.output_size,
    }

    plan_path = REMOTION_PUBLIC / "edit-plans" / args.week / f"{args.slug}.json"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(json.dumps(plan, indent=2))
    print(f"[done] edit plan → {plan_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
