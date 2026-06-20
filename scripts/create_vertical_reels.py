#!/usr/bin/env python3
"""Convert + crop horizontal videos to vertical reels with timestamp selection."""

import json
import subprocess
import argparse
import tempfile
from pathlib import Path

REPO = Path(__file__).parent.parent
VIDEO_DIR = REPO / "assets" / "video" / "edited"

def time_to_seconds(time_str):
    """Convert HH:MM:SS or MM:SS to seconds."""
    parts = time_str.split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    return int(time_str)


def get_video_dimensions(mp4_path):
    """Return (width, height) via ffprobe, or (None, None) on failure."""
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_streams", str(mp4_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None, None
    data = json.loads(result.stdout)
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video":
            return stream["width"], stream["height"]
    return None, None


def find_smart_crop_x(mp4_path, start_sec, dur_sec, crop_w, src_w):
    """Return x offset with highest edge density for a crop_w-wide window.

    Extracts one frame at the clip midpoint, converts to greyscale, applies
    FIND_EDGES, sums per-column intensity, then slides a crop_w window to
    find the peak.  Falls back to center (returns None) if PIL unavailable.
    """
    mid_sec = start_sec + dur_sec / 2
    tmp = Path(tempfile.mktemp(suffix=".png"))
    try:
        cmd = [
            "ffmpeg", "-ss", str(mid_sec), "-i", str(mp4_path),
            "-vframes", "1", "-y", str(tmp)
        ]
        subprocess.run(cmd, capture_output=True, check=True)

        from PIL import Image, ImageFilter
        img = Image.open(tmp).convert("L")
        edges = img.filter(ImageFilter.FIND_EDGES)

        pixels = list(edges.getdata())
        w = img.size[0]

        col_density = [0] * w
        for i, p in enumerate(pixels):
            col_density[i % w] += p

        window_sum = sum(col_density[:crop_w])
        best_sum = window_sum
        best_x = 0
        for x in range(1, src_w - crop_w + 1):
            window_sum = window_sum - col_density[x - 1] + col_density[x + crop_w - 1]
            if window_sum > best_sum:
                best_sum = window_sum
                best_x = x

        return best_x
    except Exception as e:
        print(f"Smart crop analysis failed ({e}), falling back to center crop")
        return None
    finally:
        tmp.unlink(missing_ok=True)


def create_reel(mp4_path, output_path, start_time="0", duration="60", srt_path=None, smart_crop=False):
    """Crop video to 9:16 vertical, optionally from timestamp, with optional caption burn-in."""

    start_sec = time_to_seconds(start_time)
    dur_sec = time_to_seconds(duration)

    # Build crop filter
    if smart_crop:
        src_w, src_h = get_video_dimensions(mp4_path)
        if src_w and src_h:
            crop_w = min(src_w, src_h * 9 // 16)
            best_x = find_smart_crop_x(mp4_path, start_sec, dur_sec, crop_w, src_w)
            if best_x is not None:
                print(f"Smart crop: x={best_x} (crop_w={crop_w}, src={src_w}x{src_h})")
                vf = f"crop={crop_w}:{src_h}:{best_x}:0,scale=1080:1920"
            else:
                vf = "crop=min(iw\\,ih*9/16):min(ih\\,iw*16/9),scale=1080:1920"
        else:
            vf = "crop=min(iw\\,ih*9/16):min(ih\\,iw*16/9),scale=1080:1920"
    else:
        vf = "crop=min(iw\\,ih*9/16):min(ih\\,iw*16/9),scale=1080:1920"

    if srt_path and Path(srt_path).exists():
        # Import here to avoid circular import
        try:
            from create_story_clips import extract_captions_for_window, parse_srt, write_temp_srt

            captions = parse_srt(Path(srt_path))
            window_captions = extract_captions_for_window(captions, start_sec, dur_sec)

            if window_captions:
                temp_srt = Path("/tmp") / f"reel_{Path(output_path).stem}.srt"
                write_temp_srt(window_captions, temp_srt)

                # Add subtitle filter
                subtitle_filter = (
                    f"subtitles='{temp_srt}':force_style="
                    "'FontSize=22,PrimaryColour=&H00FFFFFF,"
                    "OutlineColour=&H00000000,Outline=2,Shadow=1,"
                    "Alignment=2,MarginV=60'"
                )
                vf = f"{vf},{subtitle_filter}"
        except (ImportError, ModuleNotFoundError):
            print("Warning: create_story_clips not found. Skipping caption burn-in for reel.")

    cmd = [
        "ffmpeg", "-i", str(mp4_path),
        "-ss", str(start_sec), "-t", str(dur_sec),
        "-vf", vf,
        "-c:v", "h264_videotoolbox", "-c:a", "aac", "-y",
        str(output_path)
    ]

    print(f"Creating reel: {start_time} ({dur_sec}s)" + (" with captions" if srt_path else ""))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr[-200:]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create vertical YouTube Shorts/Reels from horizontal video.")
    parser.add_argument("--slug", help="Blog slug (filename without extension)")
    parser.add_argument("--video", help="Direct path to video file (overrides --slug lookup)")
    parser.add_argument("--start", default="0", help="Start time (MM:SS or HH:MM:SS, default 0)")
    parser.add_argument("--duration", default="60", help="Duration in seconds (default 60)")
    parser.add_argument("--output-dir", default=str(VIDEO_DIR), help="Output directory (default assets/video/edited/)")
    parser.add_argument("--output-name", help="Output filename (default {slug}_reel.mp4)")
    parser.add_argument("--srt", help="Optional SRT file for caption burn-in")
    parser.add_argument("--smart-crop", action="store_true",
                        help="Detect best horizontal crop position (for screen recordings)")
    args = parser.parse_args()

    if args.video:
        mp4 = Path(args.video)
        if not mp4.is_absolute():
            mp4 = REPO / mp4
        slug = args.slug or mp4.stem
    elif args.slug:
        # Search flat dir and ISO-week subdirs
        mp4 = VIDEO_DIR / f"{args.slug}.mp4"
        if not mp4.exists():
            matches = list(VIDEO_DIR.glob(f"*/{args.slug}.mp4"))
            if matches:
                mp4 = matches[0]
        slug = args.slug
    else:
        print("Error: provide --slug or --video")
        exit(1)

    output_dir = Path(args.output_dir)
    output_name = args.output_name or f"{slug}_reel.mp4"
    reel = output_dir / output_name

    if not mp4.exists():
        print(f"Error: Video not found: {mp4}")
        exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    create_reel(mp4, reel, args.start, args.duration, srt_path=args.srt,
                smart_crop=args.smart_crop)
    print(f"✓ Saved: {reel}")
