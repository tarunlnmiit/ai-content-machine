#!/usr/bin/env python3
"""Shim: re-transcribe a hand-edited video → SRT + edit_meta.json for clip_shorts.py.

Use when the Remotion pipeline produced the final .mp4 but clip_shorts.py
complains about missing _edit_meta.json / stale captions timestamps.

Usage:
  python3 scripts/make_shorts_meta.py --slug life_habits --video assets/video/edited/life_habits.mp4
  python3 scripts/make_shorts_meta.py --slug my-slug --video /path/to/final.mp4 --whisper-model small
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).parent.parent


def probe_duration(video: Path) -> float:
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", str(video),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ffprobe failed: {r.stderr[-400:]}")
    try:
        return float(json.loads(r.stdout)["format"]["duration"])
    except (KeyError, ValueError) as e:
        sys.exit(f"ffprobe: could not parse duration — {e}")


def transcribe_to_srt(video: Path, srt_out: Path, model: str) -> None:
    whisper_bin = Path(sys.executable).parent / "whisper"
    env = {**os.environ, "KMP_DUPLICATE_LIB_OK": "TRUE"}

    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [
            str(whisper_bin), str(video),
            "--model", model,
            "--output_format", "srt",
            "--output_dir", tmpdir,
        ]
        print(f"[whisper] transcribing {video.name} (model={model})…")
        r = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if r.returncode != 0:
            sys.exit(f"whisper failed: {r.stderr[-600:]}")

        srt_tmp = Path(tmpdir) / (video.stem + ".srt")
        if not srt_tmp.exists():
            sys.exit("whisper: no .srt output found in temp dir")

        srt_out.parent.mkdir(parents=True, exist_ok=True)
        srt_out.write_text(srt_tmp.read_text())
        print(f"[whisper] SRT → {srt_out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--video", required=True, help="Path to final edited .mp4")
    ap.add_argument("--whisper-model", default="base",
                    choices=["tiny", "base", "small", "medium", "large"])
    args = ap.parse_args()

    video = Path(args.video)
    if not video.is_absolute():
        video = REPO / video
    if not video.exists():
        sys.exit(f"video not found: {video}")

    srt_out = REPO / "assets" / "video" / "_work" / args.slug / f"{args.slug}.srt"
    meta_out = REPO / "assets" / "video" / "edited" / f"{args.slug}_edit_meta.json"

    print(f"=== make_shorts_meta: {args.slug} ===")

    print("\n[1/3] probe duration")
    duration = probe_duration(video)
    print(f"  duration: {duration:.1f}s")

    print("\n[2/3] transcribe → SRT")
    transcribe_to_srt(video, srt_out, args.whisper_model)

    print("\n[3/3] write edit_meta.json")
    meta = {
        "slug": args.slug,
        "srt": str(srt_out),
        "duration_sec": round(duration, 3),
        "video": str(video),
        "source": "make_shorts_meta",
    }
    meta_out.write_text(json.dumps(meta, indent=2))
    print(f"  meta → {meta_out}")

    print(f"\n✓ done — run clip_shorts.py --slug {args.slug}")


if __name__ == "__main__":
    main()
