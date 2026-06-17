#!/usr/bin/env python3
"""
download_bgm.py — Download copyright-free background music for podcast episodes.
Run once to populate assets/audio/bgm/.

USAGE:
    python3 scripts/download_bgm.py
    python3 scripts/download_bgm.py --list        # preview what would be downloaded
    python3 scripts/download_bgm.py --niche life  # one niche only

REQUIRES:
    PIXABAY_API_KEY in .env (free at https://pixabay.com/api/docs/)

TRACKS:
    Life  → assets/audio/bgm/life/   (warm, ambient, lo-fi)
    Poetry → assets/audio/bgm/poetry/ (minimal, atmospheric, ethereal)
"""

import argparse
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

BGM_DIR = BASE_DIR / "assets" / "audio" / "bgm"
PIXABAY_MUSIC_API = "https://pixabay.com/api/music/"

# Curated search queries per niche (ordered by preference)
NICHE_QUERIES: dict[str, list[str]] = {
    "life": [
        "ambient calm piano",
        "soft relaxing background music",
        "lo-fi peaceful instrumental",
        "gentle acoustic background",
    ],
    "poetry": [
        "atmospheric minimal ambient",
        "soft strings meditation",
        "ethereal ambient piano",
        "cinematic ambient peaceful",
    ],
}

TARGET_TRACKS_PER_NICHE = 4


def fetch_pixabay_tracks(api_key: str, query: str, per_page: int = 5) -> list[dict]:
    """Fetch music tracks from Pixabay API."""
    resp = requests.get(
        PIXABAY_MUSIC_API,
        params={"key": api_key, "q": query, "per_page": per_page},
        timeout=15,
    )
    if resp.status_code == 404:
        raise RuntimeError(
            "Pixabay music API returned 404. "
            "Download tracks manually from https://pixabay.com/music/ "
            "and place MP3 files in assets/audio/bgm/life/ and assets/audio/bgm/poetry/"
        )
    resp.raise_for_status()
    return resp.json().get("hits", [])


def download_track(track: dict, dest: Path, dry_run: bool = False) -> bool:
    """Download one track to dest/. Returns True on success."""
    audio_url = track.get("audio") or track.get("previewURL") or track.get("audioURL")
    if not audio_url:
        return False

    tags = track.get("tags", "bgm").replace(", ", "_")[:30].replace(" ", "_")
    track_id = track.get("id", "unknown")
    filename = f"{track_id}_{tags}.mp3"
    dest_file = dest / filename

    if dest_file.exists():
        print(f"  [skip] {filename}")
        return True

    if dry_run:
        print(f"  [would download] {filename}  ←  {audio_url}")
        return True

    resp = requests.get(audio_url, timeout=60, stream=True)
    resp.raise_for_status()
    dest_file.write_bytes(resp.content)
    size_kb = dest_file.stat().st_size // 1024
    print(f"  [ok] {filename} ({size_kb} KB)")
    return True


def download_for_niche(api_key: str, niche: str, dry_run: bool) -> int:
    dest = BGM_DIR / niche
    if not dry_run:
        dest.mkdir(parents=True, exist_ok=True)

    existing = len(list(dest.glob("*.mp3"))) if dest.exists() else 0
    if existing >= TARGET_TRACKS_PER_NICHE:
        print(f"[{niche}] {existing} tracks already present — skipping")
        return existing

    print(f"\n[{niche}] Downloading to {dest}/")
    downloaded = 0

    for query in NICHE_QUERIES[niche]:
        if downloaded + existing >= TARGET_TRACKS_PER_NICHE:
            break
        try:
            tracks = fetch_pixabay_tracks(api_key, query, per_page=3)
            for track in tracks:
                if downloaded + existing >= TARGET_TRACKS_PER_NICHE:
                    break
                if download_track(track, dest, dry_run=dry_run):
                    downloaded += 1
                    if not dry_run:
                        time.sleep(0.3)
        except RuntimeError as e:
            print(f"  [error] {e}")
            return downloaded
        except requests.HTTPError as e:
            print(f"  [warn] API error for '{query}': {e}")

    total = downloaded + existing
    print(f"  {total} tracks ready for {niche}")
    return total


def print_manual_instructions() -> None:
    print(
        "\n[manual fallback] Download ambient MP3 tracks and place them in:\n"
        "  assets/audio/bgm/life/    → warm, ambient, peaceful (e.g. lo-fi piano)\n"
        "  assets/audio/bgm/poetry/  → atmospheric, minimal, ethereal\n"
        "\n  Free sources:\n"
        "  • https://pixabay.com/music/   (CC0, filter by mood: Calm / Cinematic)\n"
        "  • https://incompetech.com/     (CC0, Kevin MacLeod)\n"
        "  • https://freemusicarchive.org (various CC licenses)\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Download BGM tracks for podcasts.")
    parser.add_argument("--niche", choices=["life", "poetry"], help="One niche only")
    parser.add_argument("--list", action="store_true", help="Dry-run: show what would be downloaded")
    args = parser.parse_args()

    api_key = os.environ.get("PIXABAY_API_KEY")
    if not api_key:
        sys.exit("ERROR: PIXABAY_API_KEY not set in .env")

    niches = [args.niche] if args.niche else ["life", "poetry"]
    dry_run = args.list

    all_ok = True
    for niche in niches:
        total = download_for_niche(api_key, niche, dry_run=dry_run)
        if total == 0:
            all_ok = False

    if not all_ok:
        print_manual_instructions()
    else:
        print("\nBGM library ready. Run produce_podcast.py to use it.")


if __name__ == "__main__":
    main()
