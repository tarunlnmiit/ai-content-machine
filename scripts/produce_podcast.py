#!/usr/bin/env python3
"""
produce_podcast.py — Extract audio from Life/Poetry video, mix BGM, upload to Spotify.

Audio source: assets/hyperframes/{week}/{date}_{niche}_*.mp4
BGM source:   assets/audio/bgm/{niche}/*.mp3  (see download_bgm.py)
Output:       assets/audio/{week}/{slug}_podcast.mp3

USAGE:
    python3 scripts/produce_podcast.py --week 2026-W25 --niche life
    python3 scripts/produce_podcast.py --week 2026-W25 --niche poetry
    python3 scripts/produce_podcast.py --week 2026-W25          # both

    # First-time Spotify login (opens browser):
    python3 scripts/produce_podcast.py --week 2026-W25 --setup-spotify

    # Audio-only, skip upload:
    python3 scripts/produce_podcast.py --week 2026-W25 --no-upload

    # Dry-run (no ffmpeg, no upload):
    python3 scripts/produce_podcast.py --week 2026-W25 --dry-run

REQUIRES:
    ffmpeg installed (brew install ffmpeg)
    playwright installed (pip install playwright && playwright install chromium)
    SPOTIFY_LIFE_SHOW_NAME and SPOTIFY_POETRY_SHOW_NAME in .env
"""

import argparse
import json
import os
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

# Spotify session persisted here so login survives across runs
SPOTIFY_SESSION_DIR = Path.home() / ".config" / "content-machine" / "spotify-session"

SHOW_NAME_ENV: dict[str, str] = {
    "life": "SPOTIFY_LIFE_SHOW_NAME",
    "poetry": "SPOTIFY_POETRY_SHOW_NAME",
}


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


# ── Spotify upload (Playwright) ────────────────────────────────────────────────

def get_show_name(niche: str) -> str:
    env_key = SHOW_NAME_ENV[niche]
    name = os.environ.get(env_key)
    if not name:
        raise EnvironmentError(
            f"{env_key} not set in .env\n"
            f"Add: {env_key}=Breath of Life"
        )
    return name


def upload_to_spotify(
    audio_mp3: Path,
    title: str,
    description: str,
    niche: str,
    *,
    headless: bool = True,
) -> None:
    """Upload episode to Spotify for Podcasters via Playwright browser automation."""
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        sys.exit(
            "playwright not installed.\n"
            "Run: pip install playwright && playwright install chromium"
        )

    show_name = get_show_name(niche)
    SPOTIFY_SESSION_DIR.mkdir(parents=True, exist_ok=True)

    print(f"  Launching browser (headless={headless})...")
    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            str(SPOTIFY_SESSION_DIR),
            channel="chrome",
            headless=headless,
            slow_mo=200,
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
        )
        # Hide navigator.webdriver so Spotify OAuth doesn't flag as bot
        ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = ctx.new_page()

        # Go to dashboard
        page.goto("https://podcasters.spotify.com/", timeout=30_000)
        page.wait_for_load_state("networkidle", timeout=20_000)

        # If not logged in, the page shows a login prompt
        if "login" in page.url.lower() or page.get_by_text("Log in").is_visible():
            if headless:
                ctx.close()
                raise RuntimeError(
                    "Not logged in. Run with --setup-spotify to open browser for login."
                )
            print("  [login] Please log in to Spotify for Podcasters in the browser window...")
            page.wait_for_url("**/pod/**", timeout=120_000)

        # Find and click into the correct show
        try:
            page.get_by_text(show_name, exact=False).first.click(timeout=10_000)
            page.wait_for_load_state("networkidle", timeout=15_000)
        except PWTimeout:
            print(f"  [warn] Could not find show '{show_name}' by text — trying to proceed from current page")

        # Navigate to new episode creation
        try:
            new_ep_btn = (
                page.get_by_role("link", name="New episode")
                or page.get_by_role("button", name="New episode")
                or page.get_by_text("New episode", exact=False).first
            )
            new_ep_btn.click(timeout=10_000)
        except PWTimeout:
            # Fallback: navigate directly
            page.goto("https://podcasters.spotify.com/pod/episode-builder", timeout=20_000)

        page.wait_for_load_state("networkidle", timeout=20_000)

        # Upload audio file
        print(f"  Uploading audio file: {audio_mp3.name}")
        file_input = page.locator("input[type='file']").first
        file_input.set_input_files(str(audio_mp3))

        # Wait for upload to complete (progress bar disappears or title field becomes active)
        page.wait_for_timeout(3_000)

        # Fill episode title
        title_field = (
            page.get_by_label("Episode title", exact=False)
            or page.get_by_placeholder("Add a title", exact=False)
        )
        title_field.first.fill(title)

        # Fill episode description
        desc_field = (
            page.get_by_label("Episode description", exact=False)
            or page.get_by_placeholder("Tell listeners what this episode is about", exact=False)
            or page.locator("textarea").first
        )
        desc_field.first.fill(description)

        # Publish / Save
        try:
            page.get_by_role("button", name="Publish").click(timeout=10_000)
        except PWTimeout:
            page.get_by_role("button", name="Save").click(timeout=10_000)

        page.wait_for_timeout(3_000)
        print(f"  [ok] Episode published: {title}")

        ctx.close()


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

    # 5. Upload
    if no_upload or dry_run:
        print(f"  [skip upload] Audio ready at: {final_mp3.relative_to(BASE_DIR)}")
        return

    print(f"  Uploading to Spotify for Podcasters ({niche})...")
    upload_to_spotify(final_mp3, title, description, niche)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Produce and upload podcast episode from Life/Poetry video.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--week", required=True, help="ISO week, e.g. 2026-W25")
    parser.add_argument("--niche", choices=["life", "poetry"], help="One niche only (default: both)")
    parser.add_argument("--no-upload", action="store_true", help="Skip Spotify upload")
    parser.add_argument("--dry-run", action="store_true", help="No ffmpeg, no upload — print plan only")
    parser.add_argument(
        "--setup-spotify",
        action="store_true",
        help="Open browser (non-headless) for manual Spotify login, then save session",
    )
    parser.add_argument(
        "--archive-dir",
        type=Path,
        default=None,
        metavar="PATH",
        help="Root of archived week directory (e.g. /Volumes/Archive/content-archive/2026/W21)",
    )
    args = parser.parse_args()

    niches = [args.niche] if args.niche else ["life", "poetry"]

    if args.setup_spotify:
        # Run with headless=False so user can log in
        print("Opening browser for Spotify login. Log in and then close the browser.")
        # Trigger with a dummy niche just to open the browser
        dummy_mp3 = Path("/dev/null")
        upload_to_spotify(dummy_mp3, "setup", "setup", "life", headless=False)
        print("Session saved. Run without --setup-spotify for headless uploads.")
        return

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
