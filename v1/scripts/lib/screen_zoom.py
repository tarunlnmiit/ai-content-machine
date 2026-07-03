#!/usr/bin/env python3
"""Auto-zoom for screen recordings (mobile legibility).

A raw screen capture cropped to 9:16 still shows tiny UI text on a phone. This
module detects the dense-content region (trimming low-energy margins via edge
density) and zooms into it, so the text that matters fills more of the frame.
It is aspect-correct and clamped by `max_zoom` so it degrades safely — a
full-bleed code editor barely zooms; a small prompt box on a mostly-empty screen
zooms in a lot.

    from lib.screen_zoom import zoom_to_content
    zoom_to_content(src, dst, target_w=1080, target_h=1920)

Falls back to a centered cover-crop if Pillow is unavailable or detection fails.
"""

from __future__ import annotations

import io
import subprocess
from pathlib import Path

TARGET_W, TARGET_H = 1080, 1920
MAX_ZOOM = 1.9           # never zoom more than this vs the full-height crop
ENERGY_TRIM = 0.06       # trim this fraction of edge-energy from each margin
PAD_FRAC = 0.04          # padding around the detected box (fraction of frame)


def _probe_wh(video: Path, ffprobe: str = "ffprobe") -> tuple[int, int] | None:
    r = subprocess.run(
        [ffprobe, "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", str(video)],
        capture_output=True, text=True,
    )
    try:
        w, h = r.stdout.strip().split(",")[:2]
        return int(w), int(h)
    except (ValueError, AttributeError):
        return None


def _trim_interval(energy: list[float], trim: float) -> tuple[int, int]:
    """Smallest [lo, hi] index range holding the central (1 - 2*trim) of energy."""
    total = sum(energy)
    if total <= 0:
        return 0, len(energy) - 1
    lo_target, hi_target = total * trim, total * (1.0 - trim)
    cum = 0.0
    lo, hi = 0, len(energy) - 1
    for i, e in enumerate(energy):
        cum += e
        if cum >= lo_target:
            lo = i
            break
    cum = 0.0
    for i, e in enumerate(energy):
        cum += e
        if cum >= hi_target:
            hi = i
            break
    if hi <= lo:
        return 0, len(energy) - 1
    return lo, hi


def detect_content_box(
    video: Path,
    target_ar: float = TARGET_W / TARGET_H,
    n_samples: int = 5,
    max_zoom: float = MAX_ZOOM,
    ffmpeg: str = "ffmpeg",
    ffprobe: str = "ffprobe",
) -> tuple[int, int, int, int] | None:
    """Return an aspect-correct (x, y, w, h) crop box around the dense content."""
    try:
        from PIL import Image, ImageFilter  # type: ignore
    except ImportError:
        return None
    wh = _probe_wh(video, ffprobe)
    if not wh:
        return None
    vid_w, vid_h = wh

    thumb_w = 480
    scale = thumb_w / vid_w
    thumb_h = max(1, int(vid_h * scale))
    col_e = [0.0] * thumb_w
    row_e = [0.0] * thumb_h

    r = subprocess.run([ffprobe, "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(video)], capture_output=True, text=True)
    try:
        duration = float(r.stdout.strip())
    except (ValueError, AttributeError):
        duration = 6.0

    got = 0
    for i in range(n_samples):
        t = duration * (i + 1) / (n_samples + 1)
        fr = subprocess.run(
            [ffmpeg, "-nostdin", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video),
             "-frames:v", "1", "-vf", f"scale={thumb_w}:{thumb_h}", "-f", "image2",
             "-vcodec", "png", "pipe:1"],
            capture_output=True,
        )
        if fr.returncode != 0 or not fr.stdout:
            continue
        img = Image.open(io.BytesIO(fr.stdout)).convert("L").filter(ImageFilter.FIND_EDGES)
        px = list(img.getdata())
        w, h = img.size
        for y in range(h):
            base = y * w
            for x in range(w):
                v = px[base + x]
                col_e[x] += v
                row_e[y] += v
        got += 1
    if got == 0:
        return None

    x0, x1 = _trim_interval(col_e, ENERGY_TRIM)
    y0, y1 = _trim_interval(row_e, ENERGY_TRIM)
    # thumb → original px
    bx = x0 / scale
    by = y0 / scale
    bw = (x1 - x0 + 1) / scale
    bh = (y1 - y0 + 1) / scale

    # padding
    pad = PAD_FRAC * vid_w
    bx = max(0.0, bx - pad); by = max(0.0, by - pad)
    bw = min(vid_w - bx, bw + 2 * pad); bh = min(vid_h - by, bh + 2 * pad)

    # enforce target aspect (expand the deficient dimension around the box center)
    cx, cy = bx + bw / 2, by + bh / 2
    if bw / bh > target_ar:
        bh = bw / target_ar
    else:
        bw = bh * target_ar

    # clamp zoom: box height must be >= full_height_crop_height / max_zoom
    min_h = vid_h / max_zoom
    if bh < min_h:
        bh = min_h
        bw = bh * target_ar

    # re-center then clamp inside the frame
    bx, by = cx - bw / 2, cy - bh / 2
    bw = min(bw, vid_w); bh = min(bh, vid_h)
    bx = max(0.0, min(bx, vid_w - bw))
    by = max(0.0, min(by, vid_h - bh))
    return int(round(bx)), int(round(by)), int(round(bw)), int(round(bh))


def zoom_to_content(
    video_in: Path,
    video_out: Path,
    target_w: int = TARGET_W,
    target_h: int = TARGET_H,
    punch_in: bool = True,
    ffmpeg: str = "ffmpeg",
    ffprobe: str = "ffprobe",
) -> Path:
    """Crop to the detected content box and scale to target → mobile-legible text."""
    box = detect_content_box(video_in, target_ar=target_w / target_h,
                             ffmpeg=ffmpeg, ffprobe=ffprobe)
    if box is None:
        # Fallback: centered cover-crop, no zoom.
        vf = (f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase,"
              f"crop={target_w}:{target_h},setsar=1")
    else:
        x, y, w, h = box
        vf = f"crop={w}:{h}:{x}:{y},scale={target_w}:{target_h},setsar=1"
        if punch_in:
            vf += (f",zoompan=z='min(1.0+0.0006*on,1.06)':d=1:"
                   f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                   f"s={target_w}x{target_h}:fps=30")
    vf += ",format=yuv420p"
    audio_args = ["-an"] if _has_no_audio(video_in, ffprobe) else ["-c:a", "copy"]
    cmd = [
        ffmpeg, "-nostdin", "-v", "error", "-y", "-i", str(video_in),
        "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        *audio_args, str(video_out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not video_out.exists():
        raise RuntimeError(f"screen zoom failed:\n{r.stderr[-600:]}")
    return video_out


def _has_no_audio(video: Path, ffprobe: str = "ffprobe") -> bool:
    r = subprocess.run(
        [ffprobe, "-v", "error", "-select_streams", "a", "-show_entries",
         "stream=index", "-of", "csv=p=0", str(video)],
        capture_output=True, text=True,
    )
    return not r.stdout.strip()


def main() -> None:
    import argparse
    import shutil
    ap = argparse.ArgumentParser(
        description="Auto-zoom a screen recording into its content region for mobile legibility")
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--width", type=int, default=TARGET_W)
    ap.add_argument("--height", type=int, default=TARGET_H)
    ap.add_argument("--no-punch", action="store_true", help="Disable the subtle punch-in")
    ap.add_argument("--ffmpeg", default=shutil.which("ffmpeg") or "ffmpeg")
    ap.add_argument("--ffprobe", default=shutil.which("ffprobe") or "ffprobe")
    a = ap.parse_args()
    out = zoom_to_content(Path(a.src), Path(a.out), a.width, a.height,
                          punch_in=not a.no_punch, ffmpeg=a.ffmpeg, ffprobe=a.ffprobe)
    print(f"[screen-zoom] wrote {out}")


if __name__ == "__main__":
    main()
