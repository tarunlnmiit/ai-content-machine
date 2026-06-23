#!/usr/bin/env python3
"""Orchestrate generation of 3 reels + 3 stories from edited YouTube videos."""

import argparse
from pathlib import Path
from create_story_clips import create_story
from create_vertical_reels import create_reel
from find_best_reel_moment import find_best_moment, transcribe_video

REPO = Path(__file__).parent.parent
VIDEO_DIR = REPO / "assets" / "video" / "edited"
BLOG_DIR = REPO / "content" / "blogs"
REELS_VIDEO_DIR = REPO / "assets" / "reels_video"
STORIES_VIDEO_DIR = REPO / "assets" / "stories_video"


def find_blog_for_video(video_path: Path) -> Path | None:
    """Infer matching blog .md from video filename.

    Video naming: {export-date}_{blog-date}-{niche}-{slug}_yt.mp4
    Blog naming: {blog-date}_{niche}_{slug}.md (underscores in niche)
    """

    stem = video_path.stem
    if stem.endswith("_yt"):
        stem = stem[:-3]

    # Split on first underscore: "{export-date}" | "{blog-date}-{niche}-{slug}"
    parts = stem.split("_", 1)
    if len(parts) != 2:
        return None

    blog_part = parts[1]  # e.g., "2026-05-14-poetry-quotes-the-end-of-poetry-by-ada-limó"

    # Replace all hyphens with underscores for blog filename matching
    # But we need to be careful: the niche part has underscores
    # Known niches: data_science_tech, life_self_dev, poetry_quotes
    # In video: data-science-tech, life-self-dev, poetry-quotes

    # Strategy: extract first 10 chars (date YYYY-MM-DD), then search the rest for niche keywords
    if len(blog_part) < 10:
        return None

    date_part = blog_part[:10]  # YYYY-MM-DD
    rest = blog_part[10:].lstrip("-")  # Remove leading hyphen if present

    # Find which niche this is
    niche = None
    slug = None
    if rest.startswith("data-science-tech"):
        niche = "data_science_tech"
        slug = rest[len("data-science-tech-") :]
    elif rest.startswith("life-self-dev"):
        niche = "life_self_dev"
        slug = rest[len("life-self-dev-") :]
    elif rest.startswith("poetry-quotes"):
        niche = "poetry_quotes"
        slug = rest[len("poetry-quotes-") :]
    else:
        return None

    blog_filename = f"{date_part}_{niche}_{slug}.md"
    blog_path = BLOG_DIR / blog_filename

    if blog_path.exists():
        return blog_path

    return None


def find_srt_for_video(video_path: Path) -> Path | None:
    """Find the _Subtitle 1.srt next to the video file."""

    # SRT filename is {video.mp4}_Subtitle 1.srt
    # Try exact match first, then glob fallback
    exact_srt = Path(str(video_path) + "_Subtitle 1.srt")
    if exact_srt.exists():
        return exact_srt

    # Fallback: glob all SRTs and find closest match
    srt_candidates = list(video_path.parent.glob("*.srt"))
    if srt_candidates:
        return srt_candidates[0]
    return None


def is_already_processed(slug: str) -> bool:
    """Return True if reels/{slug}/reel_3.mp4 exists (idempotent check)."""

    reel_3 = REELS_VIDEO_DIR / slug / "reel_3.mp4"
    return reel_3.exists()


def process_video(video_path: Path, dry_run: bool = False) -> None:
    """Full pipeline for one video: find moments -> reels -> stories."""

    slug = video_path.stem.removesuffix("_yt")

    # Resolve paths
    blog_path = find_blog_for_video(video_path)
    srt_path = find_srt_for_video(video_path)

    if not blog_path:
        print(f"✗ No blog found for {video_path.name}")
        return

    if not srt_path:
        print(f"✗ No SRT found for {video_path.name}")
        return

    print(f"\n{'=' * 60}")
    print(f"Processing: {video_path.name}")
    print(f"Blog: {blog_path.name}")
    print(f"SRT: {srt_path.name}")
    print(f"{'=' * 60}")

    if dry_run:
        print("[DRY RUN] Would process:")
        print(f"  - Video: {video_path}")
        print(f"  - Blog: {blog_path}")
        print(f"  - SRT: {srt_path}")
        return

    # Transcribe once, reuse for both reel and story scoring
    print("Transcribing video...")
    transcript = transcribe_video(str(video_path))

    if not transcript:
        print("✗ Failed to transcribe video")
        return

    # Find best 60s windows for reels
    print("\nFinding best 60s moments for reels...")
    reel_result = find_best_moment(str(blog_path), str(video_path), window_size=60, transcript=transcript)

    if not reel_result or not reel_result.get("top_moments"):
        print("✗ No reel moments found")
        return

    reel_timestamps = [m["start_seconds"] for m in reel_result["top_moments"]]

    # Find best 15s windows for stories
    print("Finding best 15s moments for stories...")
    story_result = find_best_moment(str(blog_path), str(video_path), window_size=15, transcript=transcript)

    if not story_result or not story_result.get("top_moments"):
        print("✗ No story moments found")
        return

    story_timestamps = [m["start_seconds"] for m in story_result["top_moments"]]

    # Create output directories
    reels_output_dir = REELS_VIDEO_DIR / slug
    stories_output_dir = STORIES_VIDEO_DIR / slug
    reels_output_dir.mkdir(parents=True, exist_ok=True)
    stories_output_dir.mkdir(parents=True, exist_ok=True)

    # Generate reels
    print(f"\nGenerating {len(reel_timestamps)} reels...")
    for i, start_sec in enumerate(reel_timestamps, 1):
        start_mm_ss = f"{int(start_sec // 60):02d}:{int(start_sec % 60):02d}"
        output_path = reels_output_dir / f"reel_{i}.mp4"
        create_reel(video_path, output_path, start_time=start_mm_ss, duration="60", srt_path=srt_path)

    # Generate stories
    print(f"\nGenerating {len(story_timestamps)} stories...")
    for i, start_sec in enumerate(story_timestamps, 1):
        start_mm_ss = f"{int(start_sec // 60):02d}:{int(start_sec % 60):02d}"
        output_path = stories_output_dir / f"story_{i}.mp4"
        create_story(video_path, srt_path, output_path, start_time=start_mm_ss, duration=15.0)

    print(f"\n✓ Complete! Generated 3 reels + 3 stories in:")
    print(f"  Reels:   {reels_output_dir}")
    print(f"  Stories: {stories_output_dir}")


def get_all_unprocessed_videos() -> list[Path]:
    """Glob VIDEO_DIR for *_yt.mp4, filter out already-processed."""

    videos = sorted(VIDEO_DIR.glob("*_yt.mp4"))
    return [v for v in videos if not is_already_processed(v.stem.removesuffix("_yt"))]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate 3 reels + 3 stories per edited YouTube video."
    )
    parser.add_argument(
        "--slug", help="Process specific video slug (e.g., 2026-05-16_2026-05-14-poetry-quotes-...)"
    )
    parser.add_argument(
        "--all", action="store_true", help="Process all unprocessed videos in assets/video/edited/"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be processed without executing"
    )
    args = parser.parse_args()

    if args.slug:
        # Find video matching slug
        video_candidates = list(VIDEO_DIR.glob(f"{args.slug}.mp4"))
        if video_candidates:
            process_video(video_candidates[0], dry_run=args.dry_run)
        else:
            print(f"✗ Video not found: {args.slug}")

    elif args.all:
        unprocessed = get_all_unprocessed_videos()
        if not unprocessed:
            print("✓ All videos already processed!")
        else:
            print(f"Found {len(unprocessed)} unprocessed video(s)")
            for video in unprocessed:
                process_video(video, dry_run=args.dry_run)

    else:
        parser.print_help()
