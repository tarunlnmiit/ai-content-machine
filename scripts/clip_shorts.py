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
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.video_utils import (  # noqa: E402
    cut_segment, crop_vertical, slice_srt, parse_srt, detect_code_x_center,
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
    timeout = max(180, count * 25)
    try:
        out = call_claude(prompt, cache=True, timeout=timeout).strip()
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


def _probe_duration(video: Path) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video)
    ], text=True)
    return float(out.strip())


def _whisper_srt(video: Path, out_dir: Path) -> Path:
    srt_out = out_dir / f"{video.stem}.srt"
    if srt_out.exists():
        print(f"  [whisper] SRT exists: {srt_out.name}")
        return srt_out
    print("  [whisper] transcribing (base model)…")
    whisper_bin = Path(sys.executable).parent / "whisper"
    with tempfile.TemporaryDirectory() as tmpdir:
        env = {**os.environ, "KMP_DUPLICATE_LIB_OK": "TRUE"}
        subprocess.run([
            str(whisper_bin), str(video),
            "--model", "base",
            "--output_format", "srt",
            "--output_dir", tmpdir,
        ], check=True, env=env)
        shutil.copy(Path(tmpdir) / f"{video.stem}.srt", srt_out)
    print(f"  [whisper] wrote {srt_out.name}")
    return srt_out


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
    ap.add_argument("--smart-crop", action="store_true",
                    help="Detect code region per segment and crop around it (DS videos)")
    args = ap.parse_args()

    edited_dir = REPO / "assets" / "video" / "edited"

    def find_video(slug: str) -> tuple:
        """Find video file (mp4 or mov) and return (video_path, meta_path)."""
        for ext in [".mp4", ".mov"]:
            # Try plain slug
            v = edited_dir / f"{slug}{ext}"
            if v.exists():
                m = edited_dir / f"{slug}_edit_meta.json"
                return v, m
            # Try date_slug format
            if len(slug) > 10 and slug[4] == "-" and slug[7] == "-":
                date_prefix = slug[:10]
                v = edited_dir / f"{date_prefix}_{slug}{ext}"
                if v.exists():
                    m = edited_dir / f"{date_prefix}_{slug}_edit_meta.json"
                    return v, m
        return None, None

    long_video, meta_file = find_video(args.slug)

    # If slug ends with -aug (hyperframes), fall back to base (_yt) video
    if not long_video and args.slug.endswith("-aug"):
        base_slug = args.slug[:-4]  # strip "-aug"
        long_video, meta_file = find_video(base_slug)
        if long_video:
            print(f"  note: using base video (pre-hyperframes): {long_video.name}")

    if not long_video.exists():
        sys.exit(f"long-form not found: {long_video}\nRun auto_edit.py first.")
    if not meta_file.exists():
        print(f"[meta] not found — auto-generating from video…")
        duration = _probe_duration(long_video)
        srt_path = _whisper_srt(long_video, edited_dir)
        meta_data = {"srt": str(srt_path), "duration_sec": duration}
        meta_file.write_text(json.dumps(meta_data, indent=2))
        print(f"[meta] wrote {meta_file.name}")

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

        x_center = detect_code_x_center(seg) if args.smart_crop else None
        final = shorts_dir / f"{args.slug}_short_{i:02d}.mp4"
        crop_vertical(seg, final, srt_in=sub_srt, x_center=x_center)
        outputs.append({"path": str(final), **p})

    # Manifest
    manifest = shorts_dir / f"{args.slug}_shorts_manifest.json"
    manifest.write_text(json.dumps(outputs, indent=2))
    print(f"\n[3/3] manifest → {manifest}")
    print(f"\n✓ done → {len(outputs)} shorts in {shorts_dir}")


if __name__ == "__main__":
    main()
