#!/usr/bin/env python3
"""Generate 15s story clips with caption burn-in from edited videos and SRT files."""

import re
import subprocess
from pathlib import Path
from datetime import timedelta

SRT_OFFSET_SECONDS = 3600


def time_to_seconds(time_str: str) -> float:
    """Convert HH:MM:SS,mmm or MM:SS,mmm to seconds."""
    parts = time_str.replace(",", ".").split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    return float(time_str)


def parse_srt(srt_path: Path) -> list[dict]:
    """Parse SRT into list of {start_sec, end_sec, text} dicts.
    Auto-detects and subtracts 1-hour editor offset if present."""

    content = srt_path.read_text(encoding="utf-8")
    entries = []
    blocks = re.split(r"\n\s*\n", content.strip())

    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue

        # Line 0: index (skip)
        # Line 1: timestamps "HH:MM:SS,mmm --> HH:MM:SS,mmm"
        # Lines 2+: text
        time_line = lines[1]
        text = "\n".join(lines[2:]).strip()

        try:
            start_str, end_str = time_line.split(" --> ")
            start_sec = time_to_seconds(start_str)
            end_sec = time_to_seconds(end_str)

            # Detect and subtract offset (1-hour = 3600s)
            if start_sec > 3500:
                start_sec -= SRT_OFFSET_SECONDS
                end_sec -= SRT_OFFSET_SECONDS

            entries.append({"start_sec": start_sec, "end_sec": end_sec, "text": text})
        except (ValueError, IndexError):
            continue

    return entries


def extract_captions_for_window(
    captions: list[dict], clip_start_sec: float, clip_duration: float = 15.0
) -> list[dict]:
    """Filter captions overlapping [clip_start, clip_start+duration].
    Returns re-zeroed captions (timestamps relative to clip start, 0-based)."""

    clip_end_sec = clip_start_sec + clip_duration
    window_captions = []

    for cap in captions:
        # Check overlap: caption.end > clip_start AND caption.start < clip_end
        if cap["end_sec"] > clip_start_sec and cap["start_sec"] < clip_end_sec:
            # Re-zero: subtract clip_start from both times
            new_start = max(0, cap["start_sec"] - clip_start_sec)
            new_end = min(clip_duration, cap["end_sec"] - clip_start_sec)

            window_captions.append(
                {"start_sec": new_start, "end_sec": new_end, "text": cap["text"]}
            )

    return window_captions


def seconds_to_srt_time(seconds: float) -> str:
    """Convert float seconds to SRT timestamp HH:MM:SS,mmm."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    ms = int((secs % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(secs):02d},{ms:03d}"


def write_temp_srt(captions: list[dict], output_path: Path) -> Path:
    """Write re-zeroed captions to a temp SRT file for FFmpeg."""

    lines = []
    for i, cap in enumerate(captions, 1):
        lines.append(str(i))
        lines.append(f"{seconds_to_srt_time(cap['start_sec'])} --> {seconds_to_srt_time(cap['end_sec'])}")
        lines.append(cap["text"])
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def time_to_seconds_input(time_str: str) -> float:
    """Convert HH:MM:SS or MM:SS to seconds."""
    parts = time_str.split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    return float(time_str)


def create_story(
    mp4_path,
    srt_path,
    output_path,
    start_time: str = "0",
    duration: float = 15.0,
    font_size: int = 22,
    font_color: str = "&H00FFFFFF",
    outline_color: str = "&H00000000",
) -> Path:
    """Crop to 9:16, trim to 15s, burn captions. Returns output_path on success."""

    start_sec = time_to_seconds_input(start_time)

    # Parse SRT and extract captions for this window
    captions = parse_srt(Path(srt_path))
    window_captions = extract_captions_for_window(captions, start_sec, duration)

    # Write temp SRT for FFmpeg
    temp_srt = Path("/tmp") / f"story_{Path(output_path).stem}.srt"
    write_temp_srt(window_captions, temp_srt)

    try:
        # Build filter chain with subtitle burn-in
        subtitle_filter = (
            f"subtitles='{temp_srt}':force_style="
            f"'FontSize={font_size},PrimaryColour={font_color},"
            f"OutlineColour={outline_color},Outline=2,Shadow=1,"
            "Alignment=2,MarginV=60'"
        )

        vf = f"crop=min(iw\\,ih*9/16):min(ih\\,iw*16/9),scale=1080:1920,{subtitle_filter}"

        cmd = [
            "ffmpeg",
            "-ss",
            str(start_sec),
            "-i",
            str(mp4_path),
            "-t",
            str(duration),
            "-vf",
            vf,
            "-c:v",
            "h264_videotoolbox",
            "-c:a",
            "aac",
            "-y",
            str(output_path),
        ]

        print(f"Creating story: {start_time} ({duration}s) with captions")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            return None

        return Path(output_path)

    finally:
        # Clean up temp SRT
        if temp_srt.exists():
            temp_srt.unlink()
