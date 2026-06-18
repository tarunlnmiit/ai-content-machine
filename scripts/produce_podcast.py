#!/usr/bin/env python3
"""
produce_podcast.py — Extract audio from Life/Poetry video, mix BGM, publish via RSS.

Audio source: assets/hyperframes/{week}/{date}_{niche}_*.mp4
BGM source:   assets/audio/bgm/{niche}/*.mp3  (see download_bgm.py)
Output:       assets/audio/{week}/{slug}_podcast.mp3
RSS:          data/podcast/rss/{niche}.xml  (pushed to GitHub Pages)

USAGE:
    python3 scripts/produce_podcast.py --week 2026-W25 --niche life
    python3 scripts/produce_podcast.py --week 2026-W25 --niche poetry
    python3 scripts/produce_podcast.py --week 2026-W25          # both

    # Audio-only, skip RSS upload:
    python3 scripts/produce_podcast.py --week 2026-W25 --no-upload

    # Dry-run (no ffmpeg, no upload):
    python3 scripts/produce_podcast.py --week 2026-W25 --dry-run

    # Retroactive from archive drive:
    python3 scripts/produce_podcast.py --week 2026-W21 --archive-dir /Volumes/Archive/...

REQUIRES:
    ffmpeg installed (brew install ffmpeg)
    gh CLI authenticated (gh auth login)
    Public GitHub repo: tarunlnmiit/podcast-feed (gh repo create tarunlnmiit/podcast-feed --public)
"""

import argparse
import json
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

HYPERFRAMES_DIR = BASE_DIR / "assets" / "hyperframes"
AUDIO_OUT_DIR = BASE_DIR / "assets" / "audio"
BGM_DIR = BASE_DIR / "assets" / "audio" / "bgm"
DERIVATIVES_DIR = BASE_DIR / "content" / "derivatives"


# ── Video discovery ────────────────────────────────────────────────────────────

def find_video(week: str, niche: str, archive_dir: Path | None = None) -> Path:
    """Find the hyperframes video for a given week + niche."""
    if archive_dir is not None:
        # Archive structure: videos may be in niche subdirs, named with -aug.mp4 suffix
        search_root = archive_dir / "assets" / "hyperframes" / week
        if not search_root.exists():
            raise FileNotFoundError(f"No hyperframes directory in archive: {search_root}")
        candidates = [
            p for p in search_root.rglob("*.mp4")
            if f"_{niche}" in p.name or f"-{niche}-" in p.name
            if p.name.endswith("-aug.mp4")
            if "-short-" not in p.name
        ]
        if not candidates:
            raise FileNotFoundError(
                f"No {niche} long-form video (*-aug.mp4) found under {search_root}"
            )
        matches = sorted(candidates)
        if len(matches) > 1:
            print(f"  [warn] Multiple {niche} archive videos found; using latest: {matches[-1].name}")
        return matches[-1]

    week_dir = HYPERFRAMES_DIR / week
    if not week_dir.exists():
        raise FileNotFoundError(f"No hyperframes directory for {week}: {week_dir}")
    pattern = f"*_{niche}_*.mp4"
    matches = sorted(week_dir.glob(pattern))
    if not matches:
        matches = sorted(week_dir.glob(f"*_{niche}*.mp4"))
    if not matches:
        raise FileNotFoundError(f"No {niche} video found in {week_dir}/  (pattern: {pattern})")
    if len(matches) > 1:
        print(f"  [warn] Multiple {niche} videos found; using latest: {matches[-1].name}")
    return matches[-1]


def find_derivatives_slug(week: str, niche: str, archive_dir: Path | None = None) -> str | None:
    """Find the derivatives slug matching this week + niche."""
    base = (archive_dir / "content" / "derivatives") if archive_dir else DERIVATIVES_DIR
    week_dir = base / week
    if not week_dir.exists():
        return None
    niche_tag = "life" if niche == "life" else "poetry"
    for slug_dir in sorted(week_dir.iterdir()):
        if slug_dir.is_dir() and f"_{niche_tag}_" in slug_dir.name:
            return slug_dir.name
    return None


# ── Metadata ───────────────────────────────────────────────────────────────────

def load_youtube_metadata(week: str, slug: str, derivatives_base: Path | None = None) -> dict:
    base = derivatives_base if derivatives_base else DERIVATIVES_DIR
    meta_path = base / week / slug / "youtube_metadata.json"
    if not meta_path.exists():
        return {}
    return json.loads(meta_path.read_text())


def format_podcast_description(yt_description: str) -> str:
    """Convert YouTube description to podcast show notes."""
    text = yt_description
    # Strip placeholder tokens
    text = re.sub(r"\[TIMESTAMPS_PLACEHOLDER\]", "", text)
    text = re.sub(r"\[LINKS_PLACEHOLDER\]", "", text)
    # Collapse excess blank lines
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


# ── BGM ────────────────────────────────────────────────────────────────────────

def pick_bgm(niche: str) -> Path | None:
    """Pick a random BGM track for the niche. Returns None if folder empty."""
    bgm_niche_dir = BGM_DIR / niche
    if not bgm_niche_dir.exists():
        return None
    tracks = list(bgm_niche_dir.glob("*.mp3"))
    return random.choice(tracks) if tracks else None


# ── Audio processing ───────────────────────────────────────────────────────────

def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    """Run a subprocess command, printing it first."""
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def extract_audio(video: Path, dest: Path) -> Path:
    """Extract voice audio from video as high-quality MP3."""
    voice_mp3 = dest / f"{video.stem}_voice.mp3"
    run([
        "ffmpeg", "-y", "-i", str(video),
        "-vn", "-ar", "44100", "-ac", "2", "-b:a", "192k",
        str(voice_mp3),
    ])
    return voice_mp3


def mix_bgm(voice: Path, bgm: Path, out: Path) -> None:
    """Mix voice audio with BGM at low volume (-23 dB / ~7% amplitude)."""
    # BGM: loop it, fade in 3s, let amix drop it when voice ends (dropout_transition)
    filter_graph = (
        "[1:a]volume=0.07,afade=t=in:st=0:d=3[bgm_low];"
        "[0:a][bgm_low]amix=inputs=2:duration=first:dropout_transition=5[out]"
    )
    run([
        "ffmpeg", "-y",
        "-i", str(voice),
        "-stream_loop", "-1", "-i", str(bgm),
        "-filter_complex", filter_graph,
        "-map", "[out]",
        "-ar", "44100", "-ac", "2", "-b:a", "192k",
        str(out),
    ])


def produce_audio(week: str, niche: str, video: Path, dry_run: bool) -> Path:
    """Extract + mix BGM. Returns path to final podcast MP3."""
    out_week_dir = AUDIO_OUT_DIR / week
    slug = video.stem  # e.g. 2026-06-13_life_w24
    final_mp3 = out_week_dir / f"{slug}_podcast.mp3"

    if final_mp3.exists():
        print(f"  [skip] audio already exists: {final_mp3.name}")
        return final_mp3

    if dry_run:
        print(f"  [dry-run] would produce: {final_mp3}")
        return final_mp3

    out_week_dir.mkdir(parents=True, exist_ok=True)
    bgm_track = pick_bgm(niche)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        print(f"  Extracting voice audio from {video.name}...")
        voice_mp3 = extract_audio(video, tmp_path)

        if bgm_track:
            print(f"  Mixing BGM: {bgm_track.name} at 7% volume...")
            mix_bgm(voice_mp3, bgm_track, final_mp3)
        else:
            print("  [warn] No BGM tracks found — run download_bgm.py first. Skipping mix.")
            import shutil
            shutil.copy(voice_mp3, final_mp3)

    size_mb = final_mp3.stat().st_size // (1024 * 1024)
    print(f"  [ok] {final_mp3.name} ({size_mb} MB)")
    return final_mp3


# ── Show notes ─────────────────────────────────────────────────────────────────

def write_show_notes(week: str, slug: str | None, title: str, description: str) -> Path:
    """Write podcast show notes markdown file."""
    filename = f"{slug or 'podcast'}_podcast_shownotes.md"
    out_path = DERIVATIVES_DIR / week / (slug or "_podcast") / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)

    content = f"# {title}\n\n{description}\n"
    out_path.write_text(content)
    print(f"  [ok] show notes → {out_path.relative_to(BASE_DIR)}")
    return out_path


# ── RSS publish ────────────────────────────────────────────────────────────────

def publish_via_rss(
    audio_mp3: Path,
    title: str,
    description: str,
    niche: str,
    week: str,
) -> None:
    """Publish episode via RSS feed + GitHub Releases."""
    sys.path.insert(0, str(BASE_DIR / "scripts"))
    import podcast_rss
    podcast_rss.publish_episode(audio_mp3, title, description, niche, week)


# ── Main ───────────────────────────────────────────────────────────────────────

def process_niche(
    week: str,
    niche: str,
    *,
    dry_run: bool,
    no_upload: bool,
    archive_dir: Path | None = None,
) -> None:
    print(f"\n{'='*50}")
    print(f"  Niche: {niche.upper()}  |  Week: {week}")
    if archive_dir:
        print(f"  Archive: {archive_dir}")
    print(f"{'='*50}")

    # 1. Find video
    video = find_video(week, niche, archive_dir=archive_dir)
    print(f"  Video: {video.name}")

    # 2. Load metadata
    derivatives_base = (archive_dir / "content" / "derivatives") if archive_dir else None
    slug = find_derivatives_slug(week, niche, archive_dir=archive_dir)
    meta = load_youtube_metadata(week, slug, derivatives_base=derivatives_base) if slug else {}
    title = meta.get("title", f"{niche.capitalize()} — {week}")
    description = format_podcast_description(meta.get("description", ""))

    print(f"  Title: {title}")
    print(f"  Slug:  {slug or '[not found]'}")

    # 3. Produce audio
    final_mp3 = produce_audio(week, niche, video, dry_run=dry_run)

    # 4. Write show notes
    if not dry_run:
        write_show_notes(week, slug, title, description)

    # 5. Publish via RSS
    if no_upload or dry_run:
        print(f"  [skip upload] Audio ready at: {final_mp3.relative_to(BASE_DIR)}")
        return

    print(f"  Publishing via RSS ({niche})...")
    publish_via_rss(final_mp3, title, description, niche, week)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Produce and upload podcast episode from Life/Poetry video.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--week", required=True, help="ISO week, e.g. 2026-W25")
    parser.add_argument("--niche", choices=["life", "poetry"], help="One niche only (default: both)")
    parser.add_argument("--no-upload", action="store_true", help="Skip RSS publish (audio only)")
    parser.add_argument("--dry-run", action="store_true", help="No ffmpeg, no upload — print plan only")
    parser.add_argument(
        "--archive-dir",
        type=Path,
        default=None,
        metavar="PATH",
        help="Root of archived week directory (e.g. /Volumes/Archive/content-archive/2026/W21)",
    )
    args = parser.parse_args()

    niches = [args.niche] if args.niche else ["life", "poetry"]

    archive_dir = args.archive_dir
    if archive_dir and not archive_dir.exists():
        sys.exit(f"ERROR: --archive-dir does not exist: {archive_dir}")

    for niche in niches:
        try:
            process_niche(
                args.week, niche,
                dry_run=args.dry_run,
                no_upload=args.no_upload,
                archive_dir=archive_dir,
            )
        except FileNotFoundError as e:
            print(f"  [error] {e}")
        except EnvironmentError as e:
            print(f"  [error] {e}")
            sys.exit(1)

    print("\nDone.")


if __name__ == "__main__":
    main()
