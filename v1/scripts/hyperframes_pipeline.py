#!/usr/bin/env python3
"""HyperFrames pipeline — beats → renders → FFmpeg composite → final MP4.

Receives:
  - storyboard.json  (from storyboard_gen.py)
  - trimmed video    (from video_trim.py; already cropped to 9:16 for reels)
  - transcript.json  (word-level, remapped timeline)
  - niche, is_reel, work_dir

Produces:
  - {work_dir}/hf_beats/beat_NN_*/index.html  (one project dir per beat)
  - {work_dir}/hf_renders/beat_NN_*.mov/.mp4  (one rendered clip per beat)
  - {work_dir}/final.mp4                       (composited output)

Composite strategy:
  - Alpha beats (MOV) → overlaid on top of trimmed video at their timestamps
  - Full-frame beats (MP4) → replace the base video frame for their window
  - FFmpeg filter_complex chains all overlays in one pass

Usage:
    from scripts.hyperframes_pipeline import run_hf_pipeline
    final = run_hf_pipeline(storyboard_path, trimmed_video, transcript_json, niche, work_dir)
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.hf_beat_builder import BeatSpec, build_all_beats, get_render_format, needs_alpha
from lib.hf_validator import validate_render, validate_final_output

FFMPEG_BIN = "/opt/homebrew/bin/ffmpeg"

def _find_bin(name: str, fallbacks: list[str]) -> str:
    found = shutil.which(name)
    if found:
        return found
    for fb in fallbacks:
        if Path(fb).exists():
            return fb
    return name

FFPROBE_BIN = _find_bin("ffprobe", [
    "/opt/homebrew/bin/ffprobe",
    "/usr/local/bin/ffprobe",
    "/usr/bin/ffprobe",
])

HF_BIN = _find_bin("hyperframes", [
    "/usr/local/bin/hyperframes",
    "/opt/homebrew/bin/hyperframes",
    str(Path.home() / ".local" / "bin" / "hyperframes"),
    str(Path.home() / ".npm-global" / "bin" / "hyperframes"),
    "/opt/homebrew/lib/node_modules/.bin/hyperframes",
    "/usr/local/lib/node_modules/.bin/hyperframes",
])

def _get_video_duration(video_path: Path) -> float:
    """Return actual video duration in seconds via ffprobe."""
    r = subprocess.run(
        [FFPROBE_BIN, "-v", "quiet", "-print_format", "json",
         "-show_format", str(video_path)],
        capture_output=True, text=True, timeout=30
    )
    try:
        return float(json.loads(r.stdout)["format"]["duration"])
    except Exception:
        return 0.0


# Render quality per format (--quality flag is NOT passed — it adds x264-params
# which fails on FFmpeg builds without libx264. HyperFrames uses its default quality.)
RENDER_QUALITY = {
    "mov":  "high",    # alpha: preserve edge detail
    "webm": "high",    # opaque: VP9, no libx264 dependency
    "mp4":  "standard",
}

# FFmpeg encode settings for the final composite
FINAL_VIDEO_PRESET = "slow"
FINAL_VIDEO_CRF = "18"        # visually lossless
FINAL_AUDIO_CODEC = "copy"    # pass through trimmed audio unchanged


def render_beat(
    beat: BeatSpec,
    project_dir: Path,
    renders_dir: Path,
    is_reel: bool = False,
) -> Path:
    """Render one beat project directory with HyperFrames.

    Returns path to the rendered .mov or .mp4 file.
    """
    fmt = get_render_format(beat.block_type, beat.layout)
    output_path = renders_dir / f"beat_{beat.idx:02d}_{beat.block_type}.{fmt}"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    resolution = "portrait" if is_reel else "landscape"
    quality = RENDER_QUALITY[fmt]

    # Variables injected at render time
    variables = json.dumps({"caption_text": beat.caption})

    cmd = [
        HF_BIN, "render", str(project_dir),
        "--format", fmt,
        "--output", str(output_path),
        "--fps", "30",
        "--variables", variables,
        "--quiet",
    ]
    # --resolution is NOT passed for any format:
    # - webm and mov: rejected by HyperFrames ("outputResolution cannot be combined with alpha output")
    # - mp4: requires libx264, not available on Apple Silicon with Homebrew FFmpeg
    # HyperFrames renders at its default viewport (1280×720 landscape / 720×1280 portrait).
    # Compositions are authored at the same dimensions so content fills the frame exactly.
    # --quality triggers x264-params in HyperFrames' bundled FFmpeg which may not
    # support that flag. Omit and rely on HyperFrames' default quality.

    # Point HyperFrames at the system FFmpeg (homebrew) which has libx264.
    # HyperFrames' bundled FFmpeg may lack x264, causing 'Unrecognized option x264-params'.
    render_env = dict(os.environ)
    render_env["FFMPEG_PATH"] = "/opt/homebrew/bin/ffmpeg"

    render_timeout = max(300, int((beat.end - beat.start) * 30 * 2))  # 2s per frame, floor 300s
    print(f"    [hf-render] Beat {beat.idx:02d} → {output_path.name}")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=render_timeout, env=render_env)
    if r.returncode != 0:
        raise RuntimeError(
            f"hyperframes render failed for beat {beat.idx} ({beat.block_type}):\n"
            f"stdout: {r.stdout[-400:]}\nstderr: {r.stderr[-400:]}"
        )

    return output_path


def build_ffmpeg_composite(
    base_video: Path,
    beat_renders: list[tuple[BeatSpec, Path]],
    output_path: Path,
    niche: str,
    is_reel: bool = False,
    has_screen_recording: bool = False,
) -> Path:
    """Composite all beat renders over the base video using FFmpeg.

    Alpha MOVs are overlaid at their timestamp windows.
    Full-frame webm beats replace the base video for their window.
    The base video is scaled to the composition resolution (1920×1080 landscape /
    1080×1920 portrait) before compositing, so overlay geometry always lines up
    regardless of the source recording's native resolution.

    Whenever a panel-right/panel-left overlay comes in, the base video pans the
    opposite way during that window so the talking-head subject sits clear of the
    panel instead of behind it. The ONLY exception is a DS video whose base is a
    screen recording (manifest `has_screen_recording: true`) — there the panel is
    meant to sit beside the code, so the base is left in place.

    Beat enable windows use a half-open interval [start, end) — back-to-back beats
    never both evaluate true on the shared boundary frame (no one-frame double-overlay).
    """
    # Half-frame epsilon at 30fps closes the interval just shy of the end so the
    # next beat (which starts exactly at this end) owns the boundary frame alone.
    half_frame = 1 / 60.0
    # Split into alpha (overlay) beats and full-frame (replace) beats
    alpha_beats: list[tuple[BeatSpec, Path]] = []
    fullframe_beats: list[tuple[BeatSpec, Path]] = []
    for beat, render_path in beat_renders:
        if needs_alpha(beat.block_type, beat.layout):
            alpha_beats.append((beat, render_path))
        else:
            fullframe_beats.append((beat, render_path))

    # Target resolution matches RESOLUTION_MAP in hf_beat_builder.py
    target_w, target_h = (1080, 1920) if is_reel else (1920, 1080)

    # Build ffmpeg command
    # Input 0: base trimmed video
    # Inputs 1..N: beat renders (alpha first, then full-frame)
    # -itsoffset shifts each beat's t=0 to its start timestamp in the output.
    inputs = ["-i", str(base_video)]
    for beat, rp in alpha_beats + fullframe_beats:
        inputs += ["-itsoffset", f"{beat.start:.3f}", "-i", str(rp)]

    # Build filter_complex
    # Scale base video to composition resolution first so overlay coords align.
    final_label = "[outv]"
    filter_parts: list[str] = []
    # Scale base to composition resolution (no-op if already correct size)
    filter_parts.append(
        f"[0:v]scale={target_w}:{target_h}:force_original_aspect_ratio=disable,"
        f"setsar=1[base_scaled]"
    )

    n_alpha = len(alpha_beats)
    n_ff = len(fullframe_beats)
    total_beats = n_alpha + n_ff

    # ── Phase 0: base-video pan/crop shift for panel overlays ──────────────────
    # When a side panel covers half the frame, pan the base the opposite way so the
    # talking-head subject sits CLEAR of the panel instead of behind it. The shift
    # is injected as a time-gated overlay of a cropped base variant BEFORE the
    # panel's alpha beat composites on top of it.
    #
    # Applies to all niches EXCEPT a DS video whose base is a screen recording
    # (has_screen_recording) — there the panel is meant to sit beside the code.
    #
    # Strength: crop a SHIFT_CROP_W-wide window and rescale to full width. A narrower
    # window = stronger pan (the speaker moves further from the panel) at the cost of
    # more horizontal stretch. 1600 moves a centred speaker from x≈960 to x≈768,
    # clearing the panel-right left edge (x≈980) with margin. (panel zones: right
    # 980–1880, left 40–940.)
    SHIFT_CROP_W = 1600
    panel_beats = [
        (beat, render_path)
        for beat, render_path in alpha_beats
        if beat.layout in ("panel-right", "panel-left")
    ]
    do_shift = bool(panel_beats) and not (niche == "ds" and has_screen_recording)

    if do_shift:
        has_panel_right = any(b.layout == "panel-right" for b, _ in panel_beats)
        has_panel_left  = any(b.layout == "panel-left"  for b, _ in panel_beats)
        right_off = 1920 - SHIFT_CROP_W  # pan window fully right → speaker moves left
        # Only declare variants that are actually consumed — FFmpeg errors on unconnected pads
        if has_panel_right:
            filter_parts.append(
                f"[base_scaled]crop={SHIFT_CROP_W}:1080:{right_off}:0,scale=1920:1080[base_shift_left]"
            )
        if has_panel_left:
            filter_parts.append(
                f"[base_scaled]crop={SHIFT_CROP_W}:1080:0:0,scale=1920:1080[base_shift_right]"
            )

    current = "[base_scaled]"
    if do_shift:
        for si, (beat, _) in enumerate(panel_beats):
            shift_src = (
                "[base_shift_left]"
                if beat.layout == "panel-right"
                else "[base_shift_right]"
            )
            end_eps = beat.end - half_frame
            next_label = f"[shifted{si}]"
            filter_parts.append(
                f"{current}{shift_src}"
                f"overlay=0:0:enable='gte(t,{beat.start:.4f})*lt(t,{end_eps:.4f})'"
                f"{next_label}"
            )
            current = next_label

    # Phase 1: overlay alpha beats (transparent MOV over base video)
    alpha_input_idx = 1
    for i, (beat, _) in enumerate(alpha_beats):
        is_last = (i + 1 == total_beats)
        next_label = final_label if is_last else f"[tmp{i}]"
        overlay_input = f"[{alpha_input_idx}:v]"
        end_eps = beat.end - half_frame
        filter_parts.append(
            f"{current}{overlay_input}"
            f"overlay=0:0:enable='gte(t,{beat.start:.4f})*lt(t,{end_eps:.4f})'"
            f":format=auto{next_label}"
        )
        current = next_label
        alpha_input_idx += 1

    # Phase 2: full-frame beats (opaque MP4 replaces base video for their window)
    fullframe_input_idx = alpha_input_idx
    for i, (beat, _) in enumerate(fullframe_beats):
        is_last = (n_alpha + i + 1 == total_beats)
        next_label = final_label if is_last else f"[ff{i}]"
        ff_input = f"[{fullframe_input_idx}:v]"
        end_eps = beat.end - half_frame
        filter_parts.append(
            f"{current}{ff_input}"
            f"overlay=0:0:enable='gte(t,{beat.start:.4f})*lt(t,{end_eps:.4f})'"
            f":format=auto{next_label}"
        )
        current = next_label
        fullframe_input_idx += 1

    filter_complex = "; ".join(filter_parts) if filter_parts else f"[0:v]copy{final_label}"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        FFMPEG_BIN, "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", final_label,
        "-map", "0:a?",   # audio from base video (trimmed)
        "-c:v", "libx264",
        "-preset", FINAL_VIDEO_PRESET,
        "-crf", FINAL_VIDEO_CRF,
        "-c:a", FINAL_AUDIO_CODEC,
        "-movflags", "+faststart",
        str(output_path),
    ]

    print(f"  [hf-composite] FFmpeg compositing {len(alpha_beats)} alpha + "
          f"{len(fullframe_beats)} fullframe beats...")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if r.returncode != 0:
        raise RuntimeError(
            f"FFmpeg composite failed:\n{r.stderr[-800:]}"
        )

    return output_path


def run_hf_pipeline(
    storyboard_path: Path,
    trimmed_video: Path,
    transcript_json: Path,
    niche: str,
    work_dir: Path,
    is_reel: bool = False,
    has_screen_recording: bool = False,
) -> Path:
    """Full HyperFrames pipeline: storyboard → compositions → renders → composite.

    Returns path to final composited MP4.
    """
    print(f"\n[hf-pipeline] Starting HyperFrames pipeline")
    print(f"  storyboard : {storyboard_path}")
    print(f"  base video : {trimmed_video}")
    print(f"  niche      : {niche} | reel={is_reel}")

    # Load storyboard
    storyboard = json.loads(storyboard_path.read_text())
    print(f"  beats      : {len(storyboard['beats'])}")

    # ── Correct outro duration to actual video end ─────────────────────────
    # storyboard total_duration_sec = transcript last-word end time, which can be
    # 10-15s shorter than the trimmed video (trailing silence, B-roll, etc.).
    # Extend the outro beat to cover the full video so the base video never
    # bleeds through after the outro overlay ends.
    actual_video_duration = _get_video_duration(trimmed_video)
    transcript_end = storyboard.get("total_duration_sec", 0.0)
    if actual_video_duration > transcript_end + 0.5:
        print(f"  [hf-pipeline] Video ({actual_video_duration:.2f}s) > transcript "
              f"({transcript_end:.2f}s) — extending outro to video end")
        storyboard["total_duration_sec"] = actual_video_duration
        for beat_raw in storyboard["beats"]:
            if beat_raw.get("beat_type") == "outro":
                beat_raw["end_sec"] = actual_video_duration
                beat_raw["duration_sec"] = actual_video_duration - beat_raw["start_sec"]

    # Load transcript words
    transcript_words: list[dict] = []
    if transcript_json.exists():
        transcript_words = json.loads(transcript_json.read_text())

    renders_dir = work_dir / "hf_renders"
    renders_dir.mkdir(parents=True, exist_ok=True)

    # ── Phase 1: Build beat project directories ────────────────────────────
    print(f"\n[hf-pipeline] Phase 1: Building beat compositions")
    beat_projects = build_all_beats(storyboard, transcript_words, niche, work_dir, is_reel)
    print(f"  Built {len(beat_projects)} compositions")

    # ── Phase 2: Render each beat ──────────────────────────────────────────
    print(f"\n[hf-pipeline] Phase 2: Rendering beats with HyperFrames")
    beat_renders: list[tuple[BeatSpec, Path]] = []
    render_errors: list[str] = []

    for beat, project_dir in beat_projects:
        try:
            render_path = render_beat(beat, project_dir, renders_dir, is_reel)
        except RuntimeError as e:
            print(f"  ✗ Beat {beat.idx:02d} RENDER FAILED: {e}")
            render_errors.append(str(e))
            continue

        # ── Phase 3: Validate each render ─────────────────────────────────
        expected_duration = beat.end - beat.start
        resolution = "portrait" if is_reel else "landscape"
        val = validate_render(
            beat_idx=beat.idx,
            block_type=beat.block_type,
            output_path=render_path,
            expected_duration_sec=expected_duration,
            expected_resolution=resolution,
            needs_alpha=needs_alpha(beat.block_type, beat.layout),
        )

        for w in val.warnings:
            print(f"    ⚠  {w}")
        if not val.ok:
            for e in val.errors:
                print(f"    ✗  {e}")
            render_errors.append(f"Beat {beat.idx} validation: {'; '.join(val.errors)}")
            continue

        beat_renders.append((beat, render_path))

    if render_errors:
        print(f"\n[hf-pipeline] ⚠  {len(render_errors)} beats failed/skipped:")
        for e in render_errors:
            print(f"    - {e}")
        print("  Continuing composite with successful beats only.")

    if not beat_renders:
        raise RuntimeError("[hf-pipeline] All beats failed — cannot composite")

    # ── Phase 4: FFmpeg composite ──────────────────────────────────────────
    print(f"\n[hf-pipeline] Phase 3: FFmpeg composite ({len(beat_renders)} beats)")
    final_output = work_dir / "final.mp4"
    build_ffmpeg_composite(
        trimmed_video, beat_renders, final_output, niche, is_reel,
        has_screen_recording=has_screen_recording,
    )

    # ── Phase 5: Validate final output ─────────────────────────────────────
    print(f"\n[hf-pipeline] Phase 4: Validating final output")
    resolution = "portrait" if is_reel else "landscape"
    val_final = validate_final_output(
        output_path=final_output,
        expected_resolution=resolution,
        min_duration_sec=5.0,
    )
    for w in val_final.warnings:
        print(f"  ⚠  {w}")
    if not val_final.ok:
        for e in val_final.errors:
            print(f"  ✗  {e}")
        raise RuntimeError(f"Final output validation failed: {'; '.join(val_final.errors)}")

    print(f"\n[hf-pipeline] ✓ Done: {final_output}")
    print(f"  Duration : {val_final.actual_duration:.1f}s")
    print(f"  Size     : {final_output.stat().st_size / 1024 / 1024:.1f} MB")
    return final_output


# ── CLI entry point ────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(
        description="Run the HyperFrames pipeline: storyboard → composited MP4"
    )
    ap.add_argument("--storyboard", required=True, help="Path to storyboard.json")
    ap.add_argument("--video", required=True, help="Path to trimmed base video")
    ap.add_argument("--transcript", required=True, help="Path to transcript.json (remapped)")
    ap.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    ap.add_argument("--work-dir", required=True, help="Working directory for intermediate files")
    ap.add_argument("--reel", action="store_true", help="Short-form reel (portrait, 5-beat)")
    ap.add_argument("--has-screen-recording", action="store_true",
                    help="DS only: base is a screen recording, so don't pan it away from side panels")
    args = ap.parse_args()

    final = run_hf_pipeline(
        storyboard_path=Path(args.storyboard),
        trimmed_video=Path(args.video),
        transcript_json=Path(args.transcript),
        niche=args.niche,
        work_dir=Path(args.work_dir),
        is_reel=args.reel,
        has_screen_recording=args.has_screen_recording,
    )
    print(f"\nFinal output: {final}")


if __name__ == "__main__":
    main()
