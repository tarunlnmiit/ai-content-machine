#!/usr/bin/env python3
"""Auto-edit raw camera footage → polished long-form video.

Pipeline:
  1. Whisper transcribe raw video (word timestamps)
  2. Detect long silences → optionally trim
  3. Fetch B-roll via fetch_videos.py (Pexels/Pixabay) using script [BROLL:] cues
  4. Overlay B-roll on raw at section boundaries (heuristic timing)
  5. Burn captions
  6. Output: assets/video/edited/{slug}.mp4

Usage:
  python3 scripts/auto_edit.py --raw assets/raw/my_cam.mp4 \\
      --script content/scripts/2026-05-21-poetry-quotes-when-dreams-speak-of-love_yt.md \\
      --niche poetry --slug 2026-05-21-poetry-when-dreams
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
    probe_duration, transcribe_whisper, burn_captions,
    overlay_broll, cut_segment, parse_srt,
)


def fetch_broll(script_path: Path, niche: str, slug: str) -> Path:
    """Invoke existing fetch_videos.py. Returns dir with downloaded clips."""
    cmd = [
        "python3", str(REPO / "scripts" / "fetch_videos.py"),
        "--script", str(script_path),
        "--niche", niche,
    ]
    print(f"\n[broll] fetching via fetch_videos.py …")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  warn: fetch_videos.py exit {res.returncode}: {res.stderr[-300:]}")
    out_dir = REPO / "assets" / "videos" / script_path.stem
    return out_dir


def load_broll_map(broll_dir: Path) -> list:
    """Read VIDEO_MAP.json → ordered list of downloaded clip paths."""
    map_file = broll_dir / "VIDEO_MAP.json"
    if not map_file.exists():
        return []
    data = json.loads(map_file.read_text())
    clips = []
    for fname, meta in data.items():
        if meta.get("downloaded"):
            p = broll_dir / fname
            if p.exists():
                clips.append({"path": p, "cue": meta.get("section_cue", 0)})
    clips.sort(key=lambda c: c["cue"])
    return clips


def plan_insertions(raw_duration: float, clips: list, segments: list) -> list:
    """Decide when to overlay each broll clip.

    Strategy: distribute clips evenly across raw timeline at speech segment
    boundaries. Each broll plays 3-5s, gaps of >=8s between.
    """
    if not clips or raw_duration < 10:
        return []

    n = min(len(clips), max(2, int(raw_duration // 30)))
    # Pick segment boundaries to anchor cuts
    if segments and len(segments) >= n:
        anchors = [segments[i * len(segments) // (n + 1)]["start"]
                   for i in range(1, n + 1)]
    else:
        anchors = [raw_duration * (i + 1) / (n + 1) for i in range(n)]

    insertions = []
    for i, anchor in enumerate(anchors):
        dur = 4.0
        if anchor + dur > raw_duration - 2:
            continue
        insertions.append({
            "start": anchor,
            "duration": dur,
            "broll_path": clips[i]["path"],
        })
    return insertions


def write_metadata(out_dir: Path, slug: str, info: dict) -> None:
    """Write edit log for shorts pipeline + auditing."""
    meta_file = out_dir / f"{slug}_edit_meta.json"
    meta_file.write_text(json.dumps(info, indent=2, default=str))
    print(f"  meta → {meta_file}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, help="Raw camera footage path")
    ap.add_argument("--script", required=True, help="YT script .md with [BROLL:] cues")
    ap.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    ap.add_argument("--slug", required=True, help="Output slug")
    ap.add_argument("--whisper-model", default="base",
                    choices=["tiny", "base", "small", "medium"])
    ap.add_argument("--skip-broll", action="store_true")
    ap.add_argument("--skip-captions", action="store_true")
    args = ap.parse_args()

    raw = Path(args.raw)
    script = Path(args.script)
    if not raw.exists():
        sys.exit(f"raw not found: {raw}")
    if not script.exists():
        sys.exit(f"script not found: {script}")

    out_dir = REPO / "assets" / "video" / "edited"
    out_dir.mkdir(parents=True, exist_ok=True)
    work_dir = REPO / "assets" / "video" / "_work" / args.slug
    work_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== auto_edit: {args.slug} ===")
    duration = probe_duration(raw)
    print(f"  raw duration: {duration:.1f}s")

    # 1. Transcribe
    print("\n[1/4] transcribe")
    tx = transcribe_whisper(raw, work_dir, model=args.whisper_model)
    srt = tx["srt"]
    segments = tx["segments"]
    print(f"  segments: {len(segments)}  srt: {srt}")

    # 2. Fetch broll
    insertions = []
    if not args.skip_broll:
        print("\n[2/4] fetch broll")
        broll_dir = fetch_broll(script, args.niche, args.slug)
        clips = load_broll_map(broll_dir)
        print(f"  broll clips: {len(clips)}")
        insertions = plan_insertions(duration, clips, segments)
        print(f"  insertions planned: {len(insertions)}")
    else:
        print("\n[2/4] skip broll (flag)")

    # 3. Overlay
    print("\n[3/4] overlay broll")
    overlaid = work_dir / f"{args.slug}_overlaid.mp4"
    overlay_broll(raw, [i["broll_path"] for i in insertions], overlaid, insertions)

    # 4. Burn captions
    final = out_dir / f"{args.slug}.mp4"
    if args.skip_captions:
        print("\n[4/4] skip captions → copy")
        subprocess.run(["cp", str(overlaid), str(final)], check=True)
    else:
        print("\n[4/4] burn captions")
        burn_captions(overlaid, srt, final)

    write_metadata(out_dir, args.slug, {
        "slug": args.slug,
        "niche": args.niche,
        "raw": str(raw),
        "script": str(script),
        "duration_sec": duration,
        "segments": len(segments),
        "broll_insertions": insertions,
        "srt": str(srt),
        "final": str(final),
    })

    print(f"\n✓ done → {final}")
    print(f"  next: python3 scripts/clip_shorts.py --slug {args.slug}")


if __name__ == "__main__":
    main()
