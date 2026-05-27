#!/usr/bin/env python3
"""Cut polished long-form video → 3-5 vertical Shorts/Reels clips.

Pipeline:
  1. Load edit metadata + SRT for finished long-form
  2. Ask Claude (subprocess) to pick 3-5 best 30-60s hook segments from transcript
  3. ffmpeg cut each segment from long-form
  4. Crop 16:9 → 9:16 (center crop), burn caption subset
  5. Output: assets/video/edited/shorts/{slug}_short_{NN}.mp4

Usage:
  python3 scripts/clip_shorts.py --slug 2026-05-21-poetry-when-dreams
  python3 scripts/clip_shorts.py --slug ... --count 3
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.video_utils import (  # noqa: E402
    cut_segment, crop_vertical, slice_srt, parse_srt,
)
from lib.claude_cli import call_claude  # noqa: E402


def transcript_text(srt_path: Path) -> str:
    cues = parse_srt(srt_path)
    return "\n".join(f"[{c['start']:.1f}s] {c['text']}" for c in cues)


def pick_clips_with_claude(transcript: str, count: int) -> list:
    """Call claude CLI to extract best clip segments. Return list of dicts."""
    prompt = f"""You're picking vertical Short clips from a long-form video transcript.

Goal: find {count} segments, each 30-60 seconds, that work as self-contained Shorts/Reels.

Criteria for each segment:
- Opens with a HOOK (question, bold claim, surprising fact, or pattern interrupt)
- Self-contained (no "as I mentioned earlier", no missing setup)
- Ends with an insight, payoff, or cliffhanger
- High emotional or informational density

Return ONLY a JSON array, no prose. Schema:
[
  {{"start": <float seconds>, "end": <float seconds>, "hook_line": "<the opening line>", "why": "<1-sentence reason>"}}
]

Transcript (timestamps in seconds at start of each line):
{transcript[:12000]}
"""
    try:
        out = call_claude(prompt, cache=True, timeout=120).strip()
    except RuntimeError as e:
        print(f"  {e}")
        return []
    m = re.search(r"\[\s*\{.*\}\s*\]", out, re.DOTALL)
    if not m:
        print(f"  no JSON in claude output:\n{out[:400]}")
        return []
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}")
        return []


def fallback_pick(srt_path: Path, count: int, video_duration: float) -> list:
    """If claude unavailable: pick evenly-spaced 45s windows."""
    cues = parse_srt(srt_path)
    if not cues:
        return []
    picks = []
    for i in range(count):
        anchor = video_duration * (i + 1) / (count + 1)
        start = max(0, anchor - 20)
        end = min(video_duration, start + 45)
        # find nearest cue
        text = ""
        for c in cues:
            if c["start"] >= start:
                text = c["text"]
                break
        picks.append({"start": start, "end": end, "hook_line": text, "why": "even-spaced fallback"})
    return picks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--count", type=int, default=4)
    ap.add_argument("--no-claude", action="store_true",
                    help="Skip claude clip selection, use fallback")
    args = ap.parse_args()

    edited_dir = REPO / "assets" / "video" / "edited"
    long_video = edited_dir / f"{args.slug}.mp4"
    meta_file = edited_dir / f"{args.slug}_edit_meta.json"

    if not long_video.exists():
        sys.exit(f"long-form not found: {long_video}\nRun auto_edit.py first.")
    if not meta_file.exists():
        sys.exit(f"meta not found: {meta_file}")

    meta = json.loads(meta_file.read_text())
    srt = Path(meta["srt"])
    duration = float(meta["duration_sec"])

    print(f"=== clip_shorts: {args.slug} ({duration:.1f}s) ===")

    # Pick clips
    print("\n[1/3] pick clip segments")
    if args.no_claude:
        picks = fallback_pick(srt, args.count, duration)
    else:
        tr = transcript_text(srt)
        picks = pick_clips_with_claude(tr, args.count)
        if not picks:
            print("  claude returned 0 → fallback")
            picks = fallback_pick(srt, args.count, duration)

    # Validate
    valid = []
    for p in picks:
        s = float(p.get("start", 0))
        e = float(p.get("end", 0))
        if e - s < 15 or e > duration or s < 0:
            continue
        if e - s > 90:
            e = s + 60
        valid.append({**p, "start": s, "end": e})

    print(f"  picked {len(valid)} segments")
    for i, p in enumerate(valid):
        print(f"    [{i:02d}] {p['start']:.1f}-{p['end']:.1f}s  hook: {p['hook_line'][:60]}")

    # Cut + vertical
    shorts_dir = edited_dir / "shorts"
    shorts_dir.mkdir(exist_ok=True)
    work = REPO / "assets" / "video" / "_work" / args.slug / "shorts"
    work.mkdir(parents=True, exist_ok=True)

    print("\n[2/3] cut + vertical + captions")
    outputs = []
    for i, p in enumerate(valid):
        seg = work / f"seg_{i:02d}.mp4"
        cut_segment(long_video, p["start"], p["end"], seg)

        sub_srt = work / f"seg_{i:02d}.srt"
        slice_srt(srt, p["start"], p["end"], sub_srt)

        final = shorts_dir / f"{args.slug}_short_{i:02d}.mp4"
        crop_vertical(seg, final, srt_in=sub_srt)
        outputs.append({"path": str(final), **p})

    # Manifest
    manifest = shorts_dir / f"{args.slug}_shorts_manifest.json"
    manifest.write_text(json.dumps(outputs, indent=2))
    print(f"\n[3/3] manifest → {manifest}")
    print(f"\n✓ done → {len(outputs)} shorts in {shorts_dir}")


if __name__ == "__main__":
    main()
