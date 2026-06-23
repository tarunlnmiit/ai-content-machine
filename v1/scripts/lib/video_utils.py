#!/usr/bin/env python3
"""Shared ffmpeg + whisper helpers for auto_edit and clip_shorts."""

import io
import json
import re
import subprocess
from pathlib import Path
from typing import Optional


def probe_duration(path: Path) -> float:
    """Return media duration in seconds via ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def run_ffmpeg(cmd: list, label: str = "") -> None:
    """Run ffmpeg, surface stderr tail on failure."""
    if label:
        print(f"  ffmpeg: {label}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        tail = res.stderr[-600:]
        raise RuntimeError(f"ffmpeg failed ({label}):\n{tail}")


def transcribe_whisper(media_path: Path, out_dir: Path, model: str = "base") -> dict:
    """Transcribe with whisper. Returns {srt: Path, json: Path, segments: list}."""
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "whisper", str(media_path),
        "--language", "English",
        "--model", model,
        "--output_format", "all",
        "--output_dir", str(out_dir),
        "--word_timestamps", "True",
    ]
    print(f"  whisper transcribing ({model})...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"whisper failed:\n{res.stderr[-400:]}")

    stem = media_path.stem
    srt = out_dir / f"{stem}.srt"
    js = out_dir / f"{stem}.json"
    segments = []
    if js.exists():
        with open(js) as f:
            segments = json.load(f).get("segments", [])
    return {"srt": srt, "json": js, "segments": segments}


def parse_srt(srt_path: Path) -> list:
    """Parse SRT → list of {start, end, text}."""
    if not srt_path.exists():
        return []
    raw = srt_path.read_text()
    blocks = re.split(r"\n\n+", raw.strip())
    out = []
    for blk in blocks:
        lines = blk.strip().split("\n")
        if len(lines) < 3:
            continue
        m = re.match(r"(\d+:\d+:\d+[,.]\d+)\s*-->\s*(\d+:\d+:\d+[,.]\d+)", lines[1])
        if not m:
            continue
        out.append({
            "start": _ts_to_sec(m.group(1)),
            "end": _ts_to_sec(m.group(2)),
            "text": " ".join(lines[2:]).strip(),
        })
    return out


def _ts_to_sec(ts: str) -> float:
    ts = ts.replace(",", ".")
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def _sec_to_ts(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec - h * 3600 - m * 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def slice_srt(srt_path: Path, start: float, end: float, out_path: Path) -> None:
    """Write SRT subset for [start,end], times rebased to 0."""
    cues = parse_srt(srt_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    idx = 1
    lines = []
    for c in cues:
        if c["end"] < start or c["start"] > end:
            continue
        s = max(c["start"], start) - start
        e = min(c["end"], end) - start
        lines.append(f"{idx}\n{_sec_to_ts(s)} --> {_sec_to_ts(e)}\n{c['text']}\n")
        idx += 1
    out_path.write_text("\n".join(lines))


def detect_silences(media_path: Path, noise_db: int = -30, min_dur: float = 0.6) -> list:
    """Return list of (start, end) silent regions via ffmpeg silencedetect."""
    cmd = [
        "ffmpeg", "-i", str(media_path), "-af",
        f"silencedetect=noise={noise_db}dB:d={min_dur}", "-f", "null", "-",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    stderr = res.stderr
    starts = [float(m.group(1)) for m in re.finditer(r"silence_start: ([\d.]+)", stderr)]
    ends = [float(m.group(1)) for m in re.finditer(r"silence_end: ([\d.]+)", stderr)]
    return list(zip(starts, ends))


CAPTION_STYLE_LANDSCAPE = (
    "FontName=Arial,FontSize=18,PrimaryColour=&H00FFFFFF,"
    "OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,"
    "Alignment=2,MarginV=40,Bold=1"
)

CAPTION_STYLE_PORTRAIT = (
    "FontName=Arial,FontSize=22,PrimaryColour=&H0000FFFF,"
    "OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=2,"
    "Alignment=2,MarginV=300,MarginL=60,MarginR=60,Bold=1"
)


def burn_captions(video_in: Path, srt_in: Path, video_out: Path, style: str = CAPTION_STYLE_LANDSCAPE) -> None:
    """Burn subtitles into video. NOTE: Currently disabled due to ffmpeg filter syntax issues with complex paths."""
    # TODO: Fix caption escaping for paths with spaces/colons
    # For now, just copy video without captions
    cmd = [
        "ffmpeg", "-y", "-i", str(video_in),
        "-c:v", "h264_videotoolbox", "-c:a", "copy",
        str(video_out),
    ]
    run_ffmpeg(cmd, "copy video (captions disabled)")


def overlay_broll(main_video: Path, broll_clips: list, out_path: Path,
                  insertions: list) -> None:
    """Overlay broll segments over main video at given times.

    insertions: [{start: float, duration: float, broll_path: Path}]
    Picture-in-picture style: broll covers full frame, main audio continues.
    """
    if not insertions:
        # No broll → copy
        run_ffmpeg(["ffmpeg", "-y", "-i", str(main_video), "-c", "copy", str(out_path)], "passthrough")
        return

    inputs = ["-i", str(main_video)]
    for ins in insertions:
        inputs += ["-i", str(ins["broll_path"])]

    filters = []
    last = "[0:v]"
    for i, ins in enumerate(insertions, start=1):
        scaled = f"[b{i}]"
        filters.append(f"[{i}:v]scale=1920:1080,setpts=PTS-STARTPTS{scaled}")
        out_lbl = f"[v{i}]"
        filters.append(
            f"{last}{scaled}overlay=enable='between(t,{ins['start']},{ins['start']+ins['duration']})'{out_lbl}"
        )
        last = out_lbl

    filter_complex = ";".join(filters)
    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", filter_complex,
        "-map", last, "-map", "0:a",
        "-c:v", "h264_videotoolbox", "-c:a", "aac",
        str(out_path),
    ]
    run_ffmpeg(cmd, f"overlay {len(insertions)} broll clips")


def detect_code_x_center(video: Path, n_samples: int = 5) -> Optional[int]:
    """Sample frames, find x-center of region with highest edge density (code text).
    Returns x-center in original video pixels, or None on failure."""
    try:
        from PIL import Image, ImageFilter  # type: ignore
    except ImportError:
        return None
    try:
        dur_out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height,duration",
             "-of", "csv=p=0", str(video)],
            capture_output=True, text=True, check=True
        )
        parts = dur_out.stdout.strip().split(",")
        vid_w, vid_h = int(parts[0]), int(parts[1])
        duration = float(parts[2]) if len(parts) > 2 else 10.0
        crop_w = int(vid_h * 9 / 16)
        if crop_w >= vid_w:
            return None  # already portrait
        THUMB_W = 480
        scale = THUMB_W / vid_w
        thumb_w = THUMB_W
        thumb_h = int(vid_h * scale)
        crop_w_s = int(crop_w * scale)
        col_energy = [0.0] * thumb_w
        sample_times = [duration * (i + 1) / (n_samples + 1) for i in range(n_samples)]
        for t in sample_times:
            r = subprocess.run(
                ["ffmpeg", "-ss", f"{t:.3f}", "-i", str(video),
                 "-frames:v", "1", "-vf", f"scale={thumb_w}:{thumb_h}",
                 "-f", "image2", "-vcodec", "png", "pipe:1"],
                capture_output=True
            )
            if r.returncode != 0 or not r.stdout:
                continue
            img = Image.open(io.BytesIO(r.stdout)).convert("L")
            edges = list(img.filter(ImageFilter.FIND_EDGES).getdata())
            w, h = img.size
            for y in range(h):
                row_offset = y * w
                for x in range(w):
                    col_energy[x] += edges[row_offset + x]
        # sliding window: find crop_w_s-wide band with max edge energy
        window = min(crop_w_s, thumb_w)
        cur = sum(col_energy[:window])
        best, best_x = cur, 0
        for x in range(1, thumb_w - window + 1):
            cur = cur - col_energy[x - 1] + col_energy[x + window - 1]
            if cur > best:
                best, best_x = cur, x
        x_center_scaled = best_x + window // 2
        x_center = int(x_center_scaled / scale)
        print(f"  [code-detect] best x-center: {x_center}px (of {vid_w}px wide, crop_w={crop_w})")
        return x_center
    except Exception as e:
        print(f"  [code-detect] failed: {e}")
        return None


def crop_vertical(video_in: Path, video_out: Path, srt_in: Optional[Path] = None,
                  x_center: Optional[int] = None) -> None:
    """Crop landscape → 9:16 vertical, optional caption burn.
    x_center: pixel x-position to crop around (default: center of frame)."""
    if x_center is not None:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height", "-of", "csv=p=0", str(video_in)],
            capture_output=True, text=True, check=True,
        )
        vid_w, vid_h = map(int, r.stdout.strip().split(","))
        crop_w = int(vid_h * 9 / 16)
        x_off = max(0, min(x_center - crop_w // 2, vid_w - crop_w))
        vf = f"crop={crop_w}:{vid_h}:{x_off}:0,scale=1080:1920,setsar=1"
    else:
        vf = "crop=ih*9/16:ih,scale=1080:1920,setsar=1"
    # TODO: Fix caption escaping for paths with spaces/colons in ffmpeg filters
    # For now, captions are disabled due to ffmpeg filter syntax issues with complex paths
    # if srt_in and srt_in.exists():
    #     srt_path = str(srt_in)
    #     srt_escaped = srt_path.replace("\\", "\\\\").replace(":", "\\:").replace(" ", "\\ ")
    #     srt_for_filter = srt_escaped.replace("'", "'\\''")
    #     vf += f",subtitles='{srt_for_filter}':force_style='{CAPTION_STYLE_PORTRAIT}'"
    cmd = [
        "ffmpeg", "-y", "-i", str(video_in),
        "-vf", vf,
        "-c:v", "h264_videotoolbox", "-c:a", "aac",
        str(video_out),
    ]
    run_ffmpeg(cmd, "crop vertical + captions")


def cut_segment(video_in: Path, start: float, end: float, out_path: Path) -> None:
    """Cut [start,end] from video (re-encode for frame accuracy)."""
    cmd = [
        "ffmpeg", "-y", "-i", str(video_in),
        "-ss", f"{start:.3f}", "-to", f"{end:.3f}",
        "-c:v", "h264_videotoolbox", "-c:a", "aac",
        str(out_path),
    ]
    run_ffmpeg(cmd, f"cut {start:.1f}-{end:.1f}s")
