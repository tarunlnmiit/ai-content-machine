#!/usr/bin/env python3
"""
download_bgm.py — Download copyright-free background music for podcast episodes.
Uses yt-dlp to fetch Creative Commons licensed tracks from YouTube. No API key needed.

USAGE:
    python3 scripts/download_bgm.py
    python3 scripts/download_bgm.py --list        # preview queries, don't download
    python3 scripts/download_bgm.py --niche life  # one niche only

REQUIRES:
    yt-dlp  (brew install yt-dlp)
    ffmpeg  (brew install ffmpeg)

TRACKS:
    Life   → assets/audio/bgm/life/    (warm, ambient, lo-fi)
    Poetry → assets/audio/bgm/poetry/  (minimal, atmospheric, ethereal)
"""

import argparse
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BGM_DIR = BASE_DIR / "assets" / "audio" / "bgm"
TARGET_PER_NICHE = 4

# CC-licensed ambient music search queries per niche
NICHE_QUERIES: dict[str, list[str]] = {
    "life": [
        "ambient lo-fi piano relaxing background music",
        "calm acoustic instrumental background no copyright",
        "peaceful ambient music creative commons",
    ],
    "poetry": [
        "atmospheric minimal ambient strings no copyright",
        "ethereal piano meditation background music creative commons",
        "cinematic ambient peaceful instrumental no copyright",
    ],
}


def check_ytdlp() -> None:
    result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(
            "yt-dlp not found. Install with:\n"
            "  brew install yt-dlp\n"
            "  # or: pip install yt-dlp"
        )


def count_existing(dest: Path) -> int:
    return len(list(dest.glob("*.mp3"))) if dest.exists() else 0


def download_for_niche(niche: str, dry_run: bool) -> int:
    dest = BGM_DIR / niche
    existing = count_existing(dest)

    if existing >= TARGET_PER_NICHE:
        print(f"[{niche}] {existing} tracks already present — skipping")
        return existing

    needed = TARGET_PER_NICHE - existing
    print(f"\n[{niche}] Need {needed} more track(s) → {dest}/")

    if not dry_run:
        dest.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    for query in NICHE_QUERIES[niche]:
        if downloaded >= needed:
            break

        search_count = (needed - downloaded) * 4  # over-fetch; CC filter is strict
        cmd = [
            "yt-dlp",
            f"ytsearch{search_count}:{query}",
            "--match-filter", "license = 'Creative Commons Attribution license (reuse allowed)'",
            "-x", "--audio-format", "mp3", "--audio-quality", "192k",
            "--max-downloads", str(needed - downloaded),
            "-o", str(dest / "%(id)s_%(title).50s.%(ext)s"),
            "--no-playlist",
            "--progress",
            "--no-warnings",
        ]

        if dry_run:
            print(f"  [would run] yt-dlp ytsearch{search_count}:\"{query}\" --match-filter CC ...")
            downloaded += 1
            continue

        print(f"  Searching: \"{query}\"")
        result = subprocess.run(cmd)

        if result.returncode == 0:
            new_count = count_existing(dest)
            gained = new_count - existing - downloaded
            downloaded += max(gained, 0)
        else:
            print(f"  [warn] yt-dlp returned {result.returncode} for query: {query}")

    total = count_existing(dest) if not dry_run else existing + downloaded
    print(f"  {total} track(s) ready for {niche}")
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="Download CC BGM tracks for podcasts via yt-dlp.")
    parser.add_argument("--niche", choices=["life", "poetry"], help="One niche only")
    parser.add_argument("--list", action="store_true", dest="dry_run", help="Show what would run, no download")
    args = parser.parse_args()

    if not args.dry_run:
        check_ytdlp()

    niches = [args.niche] if args.niche else ["life", "poetry"]

    for niche in niches:
        download_for_niche(niche, dry_run=args.dry_run)

    print("\nDone. Run produce_podcast.py to use BGM in episodes.")


if __name__ == "__main__":
    main()
