#!/usr/bin/env python3
"""Green-screen key + composite over a niche studio background.

Automates the validated /greenscreen-composite pipeline (2026-07-05) for the
raw-session lane's FIXED setup (same screen, same framing every week):

  1. Sample the ACTUAL screen color (never assume 0x00FF00) from frame corners.
  2. Auto-tune chromakey similarity against numeric alpha gates
     (subject patch ≥ 0xf0, screen patches ≤ 0x05). blend capped at 0.05 —
     higher makes the subject semi-transparent (validated failure mode).
  3. Composite: despill → grade → vignette+grain glue → background.
  4. Cache calibrated key params next to the background so subsequent clips
     from the same setup skip calibration.

Keying is ffmpeg-only. Palmier Pro is for the optional editable finish
(ProRes 4444 handoff via --prores) — NEVER Palmier key.chroma (alpha veil).

Usage:
    python3 scripts/composite_greenscreen.py --input clips/q01.mp4 --niche life
    python3 scripts/composite_greenscreen.py --input clip.mp4 --bg assets/brand/backgrounds/life_studio.png
    python3 scripts/composite_greenscreen.py --input clip.mp4 --niche life --prores  # Palmier handoff
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.video_utils import probe_duration  # noqa: E402

FFMPEG = "/opt/homebrew/bin/ffmpeg"
FFPROBE = "/opt/homebrew/bin/ffprobe"
BG_DIR = REPO / "assets" / "brand" / "backgrounds"

BLEND = 0.03          # NEVER above 0.05 — subject goes semi-transparent
DESPILL_MIX = 0.7
SIM_START, SIM_MIN, SIM_MAX, SIM_STEP = 0.10, 0.04, 0.24, 0.02
SUBJECT_ALPHA_MIN = 0xF0
SCREEN_ALPHA_MAX = 0x05


def probe_dims(path: Path) -> tuple[int, int, float]:
    r = subprocess.run(
        [FFPROBE, "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,r_frame_rate",
         "-of", "json", str(path)],
        capture_output=True, text=True, check=True)
    s = json.loads(r.stdout)["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return int(s["width"]), int(s["height"]), float(num) / float(den)


def _patch_rgb(video: Path, t: float, x: int, y: int, size: int = 120) -> tuple[int, int, int]:
    r = subprocess.run(
        [FFMPEG, "-v", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1",
         "-vf", f"crop={size}:{size}:{x}:{y},scale=1:1",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True, check=True)
    b = r.stdout[:3]
    return b[0], b[1], b[2]


def sample_screen_color(video: Path, w: int, h: int, t: float) -> str:
    """Pick the greenest of several edge patches — that's the screen."""
    candidates = [
        (int(w * 0.05), int(h * 0.08)), (int(w * 0.85), int(h * 0.08)),
        (int(w * 0.05), int(h * 0.75)), (int(w * 0.85), int(h * 0.75)),
        (int(w * 0.45), int(h * 0.05)),
    ]
    best, best_greenness = None, -1.0
    for x, y in candidates:
        rgb = _patch_rgb(video, t, x, y)
        greenness = rgb[1] - (rgb[0] + rgb[2]) / 2
        if greenness > best_greenness:
            best, best_greenness = rgb, greenness
    if best is None or best_greenness < 30:
        raise RuntimeError(
            f"No green-screen patch found (best greenness {best_greenness:.0f}) — "
            "is this a green-screen clip? Check framing.")
    return f"0x{best[0]:02X}{best[1]:02X}{best[2]:02X}"


def _alpha_at(video: Path, t: float, key: str, sim: float,
              x: int, y: int, size: int = 90) -> int:
    r = subprocess.run(
        [FFMPEG, "-v", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1",
         "-vf", f"chromakey={key}:{sim:.2f}:{BLEND},format=rgba,alphaextract,"
                f"crop={size}:{size}:{x}:{y},scale=1:1",
         "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        capture_output=True, check=True)
    return r.stdout[0]


def calibrate(video: Path, w: int, h: int, t: float, key: str) -> float:
    """Find similarity where subject stays solid and screen fully clears."""
    subject = (int(w * 0.5) - 45, int(h * 0.42))        # face/chest, centered framing
    screens = [(int(w * 0.06), int(h * 0.10)), (int(w * 0.86), int(h * 0.10))]
    sim = SIM_START
    for _ in range(12):
        subj_a = _alpha_at(video, t, key, sim, *subject)
        scr_a = max(_alpha_at(video, t, key, sim, *s) for s in screens)
        print(f"  [key] sim={sim:.2f} → subject={subj_a:#04x} screen={scr_a:#04x}")
        if subj_a >= SUBJECT_ALPHA_MIN and scr_a <= SCREEN_ALPHA_MAX:
            return sim
        if scr_a > SCREEN_ALPHA_MAX and sim < SIM_MAX:
            sim = round(sim + SIM_STEP, 2)      # green residue → tighten
        elif subj_a < SUBJECT_ALPHA_MIN and sim > SIM_MIN:
            sim = round(sim - SIM_STEP, 2)      # subject eaten → loosen
        else:
            break
    raise RuntimeError(
        f"Alpha gates never converged (last sim={sim:.2f}, subject={subj_a:#04x}, "
        f"screen={scr_a:#04x}). Lighting/spill problem — run /greenscreen-composite "
        "interactively to diagnose.")


def composite(video: Path, bg: Path, out: Path, key: str, sim: float,
              w: int, h: int, fps: float, dur: float, grade: str) -> None:
    grade_chain = f"{grade}," if grade else ""
    fc = (
        f"[1:v]scale={w}:{h},setsar=1[bg];"
        f"[0:v]chromakey={key}:{sim:.2f}:{BLEND},despill=type=green:mix={DESPILL_MIX},"
        f"format=rgba,{grade_chain}null[subj];"
        f"[bg][subj]overlay=x=0:y=0:shortest=1[comp];"
        f"[comp]vignette=angle=PI/20:mode=backward,noise=alls=4:allf=t+u,format=yuv420p[out]"
    )
    cmd = [FFMPEG, "-y", "-v", "error", "-i", str(video),
           "-loop", "1", "-t", f"{dur:.3f}", "-i", str(bg),
           "-filter_complex", fc, "-map", "[out]", "-map", "0:a?",
           "-r", f"{fps:.3f}", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
           "-c:a", "aac", "-b:a", "192k", str(out)]
    subprocess.run(cmd, capture_output=True, text=True, check=True)


def export_prores(video: Path, out: Path, key: str, sim: float) -> None:
    """Keyed ProRes 4444 for Palmier Pro editable finish (HEVC-alpha is blocky there)."""
    subprocess.run(
        [FFMPEG, "-y", "-v", "error", "-i", str(video),
         "-vf", f"chromakey={key}:{sim:.2f}:{BLEND},despill=type=green:mix={DESPILL_MIX},format=yuva444p10le",
         "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le",
         "-c:a", "copy", str(out)],
        capture_output=True, text=True, check=True)


def _stream_types(path: Path) -> set[str]:
    r = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True)
    return set(r.stdout.split())


def verify_output(out: Path, expect_audio: bool) -> str:
    w, h, fps = probe_dims(out)
    streams = _stream_types(out)
    if "video" not in streams:
        raise RuntimeError(f"Output has no video stream ({streams}).")
    if expect_audio and "audio" not in streams:
        raise RuntimeError("Source had audio but output has none — silent-render trap. Check audio map.")
    return f"{w}x{h} @ {fps:.2f}fps, streams: {'+'.join(sorted(streams))}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Key green screen and composite over studio background.")
    ap.add_argument("--input", required=True)
    ap.add_argument("--niche", choices=["ds", "life", "poetry"],
                    help="picks assets/brand/backgrounds/{niche}_studio.png")
    ap.add_argument("--bg", help="explicit background image (overrides --niche)")
    ap.add_argument("--out", help="default: <input>_composited.mp4")
    ap.add_argument("--grade", default="",
                    help="optional colorbalance/eq chain to match bg temperature")
    ap.add_argument("--prores", action="store_true", help="also export keyed ProRes 4444 for Palmier")
    ap.add_argument("--recalibrate", action="store_true", help="ignore cached key params")
    args = ap.parse_args()

    video = Path(args.input).resolve()
    if args.bg:
        bg = Path(args.bg).resolve()
    elif args.niche:
        bg = BG_DIR / f"{args.niche}_studio.png"
    else:
        print("Need --niche or --bg.")
        return 1
    if not video.exists() or not bg.exists():
        print(f"Missing input: {video if not video.exists() else bg}")
        return 1
    out = Path(args.out) if args.out else video.with_name(f"{video.stem}_composited.mp4")

    w, h, fps = probe_dims(video)
    dur = probe_duration(video)
    t = min(2.0, dur / 2)
    print(f"[gs] {video.name}: {w}x{h} @ {fps:.2f}fps, {dur:.1f}s → bg {bg.name}")

    # Cached calibration per background (fixed studio setup)
    cache = bg.with_suffix(".keyparams.json")
    if cache.exists() and not args.recalibrate:
        params = json.loads(cache.read_text())
        key, sim = params["key"], params["sim"]
        print(f"[gs] cached key params: {key} sim={sim} (--recalibrate to redo)")
    else:
        key = sample_screen_color(video, w, h, t)
        print(f"[gs] measured screen color: {key}")
        sim = calibrate(video, w, h, t, key)
        cache.write_text(json.dumps({"key": key, "sim": sim, "blend": BLEND,
                                     "calibrated_from": video.name}, indent=2))
        print(f"[gs] calibrated: sim={sim} → cached {cache.name}")

    composite(video, bg, out, key, sim, w, h, fps, dur, args.grade)
    print(f"[gs] ✓ {out.name}: {verify_output(out, expect_audio='audio' in _stream_types(video))}")
    print(f"    key: chromakey={key}:{sim:.2f}:{BLEND}, despill mix {DESPILL_MIX}")

    if args.prores:
        pr = video.with_name(f"{video.stem}_keyed.mov")
        export_prores(video, pr, key, sim)
        print(f"[gs] ✓ ProRes 4444 for Palmier: {pr.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
