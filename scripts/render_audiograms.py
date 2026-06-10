#!/usr/bin/env python3
"""Render audiogram clips for a given ISO week.

Reads audiogram manifests from remotion/public/audio/{week}/ and renders
both feed (1080×1080) and story (1080×1920) formats.

Usage:
    python3 scripts/render_audiograms.py --week 2026-W24
    python3 scripts/render_audiograms.py --week 2026-W24 --dry-run
    python3 scripts/render_audiograms.py --week 2026-W24 --format feed

Audiogram manifest (remotion/public/audio/{week}/{slug}_audiograms.json):
    [
      {
        "audioFile": "audio/2026-W24/{slug}_clip00.mp3",
        "startSec": 0,
        "endSec": 30,
        "quote": "The quote or excerpt to display",
        "speakerLabel": "Tarun Gupta",
        "niche": "ds",
        "podcastName": "Breath of Data Science",
        "formats": ["feed", "story"]
      }
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
AUDIO_DIR = REPO_ROOT / "remotion" / "public" / "audio"

COMPOSITION_MAP = {
    "feed": "AudiogramFeed",
    "story": "AudiogramStory",
}


def output_dir(week: str) -> Path:
    d = REPO_ROOT / "output" / "animations" / week
    d.mkdir(parents=True, exist_ok=True)
    return d


def render_audiogram(
    entry: dict,
    slug: str,
    idx: int,
    fmt: str,
    week: str,
    dry_run: bool,
) -> tuple[str, bool, float]:
    composition = COMPOSITION_MAP[fmt]
    suffix = "feed" if fmt == "feed" else "story"
    out_name = f"{slug}_audiogram_{suffix}_{idx:02d}.mp4"
    out_file = output_dir(week) / out_name

    props = {
        "audioFile": entry["audioFile"],
        "startSec": entry["startSec"],
        "endSec": entry["endSec"],
        "quote": entry["quote"],
        "niche": entry["niche"],
        "podcastName": entry["podcastName"],
    }
    if "speakerLabel" in entry:
        props["speakerLabel"] = entry["speakerLabel"]

    cmd = [
        "npx", "remotion", "render", composition, str(out_file),
        "--props", json.dumps(props),
    ]

    label = f"{slug} clip{idx:02d} {fmt}"
    print(f"  {'[DRY-RUN] ' if dry_run else ''}render {composition} → {out_name}")
    if dry_run:
        return label, True, 0.0

    t0 = time.time()
    result = subprocess.run(cmd, cwd=str(REMOTION_DIR), capture_output=True, text=True)
    elapsed = time.time() - t0

    if result.returncode != 0:
        print(f"  [FAIL] {label}: {result.stderr[-400:]}")
        return label, False, elapsed

    size_mb = out_file.stat().st_size / 1_048_576 if out_file.exists() else 0
    print(f"  [OK] {label} — {elapsed:.1f}s — {size_mb:.1f} MB")
    return label, True, elapsed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--week", required=True, help="ISO week, e.g. 2026-W24")
    parser.add_argument("--format", choices=["feed", "story", "both"], default="both")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--concurrency", type=int, default=2)
    args = parser.parse_args()

    week_audio = AUDIO_DIR / args.week
    if not week_audio.exists():
        print(f"No audio directory at {week_audio}")
        print(f"Create remotion/public/audio/{args.week}/{{slug}}_audiograms.json to schedule audiograms.")
        sys.exit(0)

    formats = ["feed", "story"] if args.format == "both" else [args.format]

    # Find all audiogram manifests
    tasks: list[tuple[dict, str, int, str]] = []
    for manifest_file in sorted(week_audio.glob("*_audiograms.json")):
        slug = manifest_file.stem.replace("_audiograms", "")
        entries: list[dict] = json.loads(manifest_file.read_text())
        for idx, entry in enumerate(entries):
            entry_formats = entry.get("formats", formats)
            for fmt in formats:
                if fmt in entry_formats:
                    tasks.append((entry, slug, idx, fmt))

    if not tasks:
        print(f"No audiogram manifests found in {week_audio}")
        sys.exit(0)

    print(f"\n── render_audiograms {args.week} formats={formats} ──")
    print(f"   {len(tasks)} render(s)  concurrency={args.concurrency}")

    results: list[tuple[str, bool, float]] = []

    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {
            pool.submit(render_audiogram, entry, slug, idx, fmt, args.week, args.dry_run): (slug, idx, fmt)
            for entry, slug, idx, fmt in tasks
        }
        for fut in as_completed(futures):
            results.append(fut.result())

    ok = [r for r in results if r[1]]
    fail = [r for r in results if not r[1]]
    total_time = sum(r[2] for r in results)

    print(f"\n── Summary ────────────────────────────────────────")
    print(f"   OK:   {len(ok)}/{len(results)}")
    if fail:
        print(f"   FAIL: {', '.join(r[0] for r in fail)}")
    if not args.dry_run and results:
        print(f"   Time: {total_time:.1f}s total")


if __name__ == "__main__":
    main()
