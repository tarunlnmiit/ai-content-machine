#!/usr/bin/env python3
"""Ken Burns B-roll montage renderer (ffmpeg).

Renders a voiceover-lane EditPlan's `brollCues` into a full-bleed montage MP4:
each clip is cover-cropped to the target frame (no letterbox), given a subtle
Ken Burns punch-in (alternating zoom-in / zoom-out for variety), cross-dissolved
between slots, and muxed under the voiceover audio.

This is a standalone alternative to the (currently absent) Remotion VoiceoverEdit
composition — it consumes the SAME EditPlan JSON that `prepare_voiceover_edit.py`
already writes, so it drops into the existing artifacts.

CLI:
    python3 -m lib.broll_montage \
        --plan remotion/public/edit-plans/2026-W27/<slug>.json \
        --public-root remotion/public \
        --out montage.mp4

Library:
    from lib.broll_montage import render_montage_from_plan
    render_montage_from_plan(plan_path, public_root, out_path)
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

FPS = 30
CROSSFADE_SEC = 0.4
ZOOM_MAX = 1.12  # Ken Burns punch depth (12%)

TARGET_DIMS: dict[str, tuple[int, int]] = {
    "9x16": (1080, 1920),
    "16x9": (1920, 1080),
    "1x1": (1080, 1080),
}


def _ffprobe_duration(path: Path, ffprobe: str = "ffprobe") -> float:
    r = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nk=1:np=0", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except (ValueError, AttributeError):
        return 0.0


def _kenburns_vf(w: int, h: int, frames: int, fps: int, zoom_in: bool) -> str:
    """Cover-crop to WxH then a linear Ken Burns zoom driven by output frame index."""
    inc = ZOOM_MAX - 1.0
    per = inc / max(1, frames)
    if zoom_in:
        z = f"min(1.0+{per:.6f}*on,{ZOOM_MAX})"
    else:
        z = f"max({ZOOM_MAX}-{per:.6f}*on,1.0)"
    return (
        f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
        f"zoompan=z='{z}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"s={w}x{h}:fps={fps},setsar=1,format=yuv420p"
    )


def _render_slot(clip: Path, dur: float, w: int, h: int, fps: int,
                 zoom_in: bool, out: Path, ffmpeg: str) -> None:
    frames = max(1, round(dur * fps))
    vf = _kenburns_vf(w, h, frames, fps, zoom_in)
    cmd = [
        ffmpeg, "-nostdin", "-v", "error", "-y",
        "-stream_loop", "-1", "-i", str(clip),   # loop if the clip is shorter than the slot
        "-t", f"{dur:.3f}", "-vf", vf, "-an", "-r", str(fps),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not out.exists():
        raise RuntimeError(f"slot render failed ({clip.name}):\n{r.stderr[-600:]}")


def render_montage(
    cues: list[dict],
    public_root: Path,
    audio_path: Path | None,
    out_path: Path,
    size: str = "9x16",
    crossfade_sec: float = CROSSFADE_SEC,
    fps: int = FPS,
    ffmpeg: str = "ffmpeg",
) -> Path:
    """Render brollCues into a full-bleed Ken Burns montage MP4 (+ audio if given)."""
    if not cues:
        raise ValueError("no brollCues to render")
    w, h = TARGET_DIMS.get(size, TARGET_DIMS["9x16"])
    work = Path(tempfile.mkdtemp(prefix="brollmontage_"))
    try:
        # 1. Render each slot with a cover-crop + alternating Ken Burns punch.
        n = len(cues)
        total = sum(float(c.get("durationSec", 0)) for c in cues)
        slots: list[Path] = []
        for i, cue in enumerate(cues):
            clip = public_root / cue["clipFile"]
            if not clip.exists():
                raise FileNotFoundError(f"clip not found: {clip}")
            dur = float(cue.get("durationSec", 0)) or 3.0
            # Extend the LAST slot by the crossfade overlap so the montage length
            # stays == total after all the dissolves eat (n-1)*crossfade.
            if i == n - 1 and n > 1:
                dur += (n - 1) * crossfade_sec
            slot = work / f"slot_{i:02d}.mp4"
            _render_slot(clip, dur, w, h, fps, zoom_in=(i % 2 == 0), out=slot, ffmpeg=ffmpeg)
            slots.append(slot)

        # 2. Chain the slots with cross-dissolves (or copy the single slot).
        video_only = work / "montage_noaudio.mp4"
        if n == 1:
            shutil.copy(slots[0], video_only)
        else:
            inputs: list[str] = []
            for s in slots:
                inputs += ["-i", str(s)]
            # offset_k = cue[k].startSec - k*crossfade  (contiguous-tiling identity)
            steps: list[str] = []
            last = "[0:v]"
            for k in range(1, n):
                off = float(cues[k].get("startSec", 0)) - k * crossfade_sec
                lbl = f"[x{k}]"
                steps.append(
                    f"{last}[{k}:v]xfade=transition=fade:duration={crossfade_sec}:"
                    f"offset={max(0.0, off):.3f}{lbl}"
                )
                last = lbl
            cmd = [
                ffmpeg, "-nostdin", "-v", "error", "-y", *inputs,
                "-filter_complex", ";".join(steps), "-map", last,
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                str(video_only),
            ]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0 or not video_only.exists():
                raise RuntimeError(f"xfade concat failed:\n{r.stderr[-800:]}")

        # 3. Mux the voiceover audio (montage length ~= audio length; -shortest trims).
        if audio_path and audio_path.exists():
            cmd = [
                ffmpeg, "-nostdin", "-v", "error", "-y",
                "-i", str(video_only), "-i", str(audio_path),
                "-map", "0:v", "-map", "1:a",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                str(out_path),
            ]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0 or not out_path.exists():
                raise RuntimeError(f"audio mux failed:\n{r.stderr[-600:]}")
        else:
            shutil.copy(video_only, out_path)
        return out_path
    finally:
        shutil.rmtree(work, ignore_errors=True)


def render_montage_from_plan(
    plan_path: Path,
    public_root: Path,
    out_path: Path,
    crossfade_sec: float = CROSSFADE_SEC,
    fps: int = FPS,
    ffmpeg: str = "ffmpeg",
) -> Path:
    """Render the montage described by a voiceover EditPlan JSON."""
    plan = json.loads(Path(plan_path).read_text())
    cues = plan.get("brollCues", [])
    size = plan.get("outputSize", "9x16")
    audio_rel = plan.get("audioFile")
    audio_path = (public_root / audio_rel) if audio_rel else None
    return render_montage(cues, public_root, audio_path, out_path,
                          size=size, crossfade_sec=crossfade_sec, fps=fps, ffmpeg=ffmpeg)


def main() -> None:
    ap = argparse.ArgumentParser(description="Render a voiceover EditPlan's B-roll into a Ken Burns montage MP4")
    ap.add_argument("--plan", required=True, help="Path to the EditPlan JSON")
    ap.add_argument("--public-root", required=True, help="remotion/public root (clipFile/audioFile are relative to this)")
    ap.add_argument("--out", required=True, help="Output montage MP4")
    ap.add_argument("--crossfade", type=float, default=CROSSFADE_SEC)
    ap.add_argument("--fps", type=int, default=FPS)
    ap.add_argument("--ffmpeg", default=shutil.which("ffmpeg") or "ffmpeg")
    args = ap.parse_args()
    out = render_montage_from_plan(
        Path(args.plan), Path(args.public_root), Path(args.out),
        crossfade_sec=args.crossfade, fps=args.fps, ffmpeg=args.ffmpeg,
    )
    print(f"[broll-montage] wrote {out}")


if __name__ == "__main__":
    main()
