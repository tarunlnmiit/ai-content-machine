#!/usr/bin/env python3
"""
transcribe_reel.py — Transcribe a reel/short video with Whisper and save as captions JSON.

Output format matches remotion/public/captions/ convention:
  [{"text": "...", "startMs": 0, "endMs": 1400, "timestampMs": 0, "confidence": null}]

Usage:
  python3 scripts/transcribe_reel.py \\
    --reel assets/reels_video/2026-W25/slug.mp4 \\
    --week 2026-W25 --slug slug

  # Custom output path:
  python3 scripts/transcribe_reel.py \\
    --reel /path/to/video.mp4 \\
    --out remotion/public/captions/2026-W25/slug.captions.json

  # Larger model for accuracy:
  python3 scripts/transcribe_reel.py --reel ... --model small
"""

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CAPTIONS_ROOT = REPO / "remotion" / "public" / "captions"


def transcribe(video_path: Path, model_name: str) -> list[dict]:
    """Run Whisper and return captions in standard JSON format."""
    try:
        import whisper
    except ImportError:
        print("ERROR: openai-whisper not installed. Run: pip install openai-whisper", file=sys.stderr)
        sys.exit(1)

    print(f"Loading Whisper model '{model_name}'...", file=sys.stderr)
    model = whisper.load_model(model_name)

    print(f"Transcribing: {video_path.name}", file=sys.stderr)
    result = model.transcribe(str(video_path), word_timestamps=False, verbose=False)

    captions = []
    for seg in result["segments"]:
        captions.append({
            "text": seg["text"].strip(),
            "startMs": int(seg["start"] * 1000),
            "endMs": int(seg["end"] * 1000),
            "timestampMs": int(seg["start"] * 1000),
            "confidence": None,
        })

    return captions


def default_out_path(week: str, slug: str) -> Path:
    return CAPTIONS_ROOT / week / f"{slug}.captions.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe reel video to captions JSON via Whisper")
    parser.add_argument("--reel", required=True, help="Path to reel video (.mp4 / .mov)")
    parser.add_argument("--week", default=None, help="ISO week e.g. 2026-W25 (for default output path)")
    parser.add_argument("--slug", default=None, help="Content slug (for default output path)")
    parser.add_argument("--out", default=None, help="Explicit output path (overrides --week/--slug)")
    parser.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper model size (default: base)")
    parser.add_argument("--dry-run", action="store_true", help="Print captions JSON, don't write file")
    args = parser.parse_args()

    reel_path = Path(args.reel)
    if not reel_path.is_absolute():
        reel_path = REPO / reel_path
    if not reel_path.exists():
        print(f"ERROR: reel not found: {reel_path}", file=sys.stderr)
        sys.exit(1)

    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = REPO / out_path
    elif args.week and args.slug:
        out_path = default_out_path(args.week, args.slug)
    else:
        parser.error("Provide either --out or both --week and --slug")

    captions = transcribe(reel_path, args.model)
    total_sec = captions[-1]["endMs"] / 1000 if captions else 0
    print(f"Transcribed {len(captions)} segments, {total_sec:.1f}s total", file=sys.stderr)

    if args.dry_run:
        print(json.dumps(captions, indent=2, ensure_ascii=False))
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(captions, indent=2, ensure_ascii=False))
    print(f"✓ Written: {out_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
