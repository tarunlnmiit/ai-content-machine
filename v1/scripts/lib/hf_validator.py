#!/usr/bin/env python3
"""HyperFrames render output validator.

After each beat renders, verify the output matches expected parameters.
Returns a ValidationResult with pass/fail + list of warnings/errors.

Usage:
    from lib.hf_validator import validate_render
    result = validate_render(beat, output_path, expected_resolution)
    if not result.ok:
        for e in result.errors: print(e)
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

FFPROBE_BIN = "/opt/homebrew/bin/ffprobe"

# Tolerance for duration mismatch (seconds). HyperFrames may round to nearest frame.
DURATION_TOLERANCE_SEC = 0.15

RESOLUTION_MAP = {
    "landscape": (1920, 1080),
    "portrait":  (1080, 1920),
    "square":    (1080, 1080),
}

# MOV codec expected for alpha channel
ALPHA_CODECS = {"prores_ks", "prores", "png", "qtrle", "vp9"}
# Pixel formats that carry alpha
ALPHA_PIX_FMTS = {"yuva420p", "yuva444p", "yuva444p12le", "yuva444p10le",
                   "yuva420p10le", "rgba", "argb", "bgra", "gbrapf32le", "gbrap"}


@dataclass
class ValidationResult:
    beat_idx: int
    output_path: Path
    ok: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    codec: str = ""
    pix_fmt: str = ""
    actual_width: int = 0
    actual_height: int = 0
    actual_duration: float = 0.0
    has_alpha: bool = False


def _ffprobe(path: Path) -> dict:
    """Run ffprobe and return stream + format info as dict."""
    r = subprocess.run(
        [
            FFPROBE_BIN, "-v", "quiet",
            "-print_format", "json",
            "-show_streams", "-show_format",
            str(path),
        ],
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {path}: {r.stderr[:300]}")
    return json.loads(r.stdout)


def validate_render(
    beat_idx: int,
    block_type: str,
    output_path: Path,
    expected_duration_sec: float,
    expected_resolution: str = "landscape",
    needs_alpha: bool = False,
) -> ValidationResult:
    """Validate a rendered beat output file.

    Args:
        beat_idx: Beat index (for reporting).
        block_type: Block type string (for context in messages).
        output_path: Path to the rendered .mov or .mp4 file.
        expected_duration_sec: Expected duration in seconds (beat end - beat start).
        expected_resolution: "landscape", "portrait", or "square".
        needs_alpha: Whether this beat requires an alpha channel.

    Returns:
        ValidationResult with ok=True if all checks pass.
    """
    result = ValidationResult(beat_idx=beat_idx, output_path=output_path)

    # 1. File exists and is non-empty
    if not output_path.exists():
        result.ok = False
        result.errors.append(f"Output file not found: {output_path}")
        return result

    size_bytes = output_path.stat().st_size
    if size_bytes < 1024:
        result.ok = False
        result.errors.append(f"Output too small ({size_bytes} bytes) — likely a render failure")
        return result

    # 2. ffprobe
    try:
        probe = _ffprobe(output_path)
    except Exception as e:
        result.ok = False
        result.errors.append(f"ffprobe failed: {e}")
        return result

    video_streams = [s for s in probe.get("streams", []) if s.get("codec_type") == "video"]
    if not video_streams:
        result.ok = False
        result.errors.append("No video stream found in output")
        return result

    vs = video_streams[0]
    result.codec = vs.get("codec_name", "")
    result.pix_fmt = vs.get("pix_fmt", "")
    result.actual_width = vs.get("width", 0)
    result.actual_height = vs.get("height", 0)
    result.has_alpha = result.pix_fmt in ALPHA_PIX_FMTS

    # Duration from stream or format
    dur_str = vs.get("duration") or probe.get("format", {}).get("duration", "0")
    try:
        result.actual_duration = float(dur_str)
    except ValueError:
        result.warnings.append(f"Could not parse duration: {dur_str!r}")

    # 3. Resolution check
    exp_w, exp_h = RESOLUTION_MAP.get(expected_resolution, (1920, 1080))
    if result.actual_width != exp_w or result.actual_height != exp_h:
        # Warning only (not hard fail) — HyperFrames may scale differently
        result.warnings.append(
            f"Resolution mismatch: expected {exp_w}×{exp_h}, "
            f"got {result.actual_width}×{result.actual_height}"
        )

    # 4. Duration check
    dur_delta = abs(result.actual_duration - expected_duration_sec)
    if dur_delta > DURATION_TOLERANCE_SEC:
        result.ok = False
        result.errors.append(
            f"Duration mismatch: expected {expected_duration_sec:.2f}s, "
            f"got {result.actual_duration:.2f}s (delta {dur_delta:.2f}s > tolerance {DURATION_TOLERANCE_SEC}s)"
        )

    # 5. Alpha channel check (only for MOV beats)
    if needs_alpha and not result.has_alpha:
        result.warnings.append(
            f"Alpha channel expected (block_type={block_type}, format=mov) "
            f"but pix_fmt={result.pix_fmt!r} has no alpha. "
            "Composite will treat this as opaque (may look correct if block is full-frame)"
        )

    return result


def validate_final_output(
    output_path: Path,
    expected_resolution: str = "landscape",
    min_duration_sec: float = 10.0,
) -> ValidationResult:
    """Validate the final assembled video (H.264 MP4, no alpha needed)."""
    result = ValidationResult(beat_idx=-1, output_path=output_path)

    if not output_path.exists():
        result.ok = False
        result.errors.append(f"Final output not found: {output_path}")
        return result

    try:
        probe = _ffprobe(output_path)
    except Exception as e:
        result.ok = False
        result.errors.append(f"ffprobe on final output failed: {e}")
        return result

    video_streams = [s for s in probe.get("streams", []) if s.get("codec_type") == "video"]
    audio_streams = [s for s in probe.get("streams", []) if s.get("codec_type") == "audio"]

    if not video_streams:
        result.ok = False
        result.errors.append("Final output has no video stream")
        return result

    vs = video_streams[0]
    result.codec = vs.get("codec_name", "")
    result.actual_width = vs.get("width", 0)
    result.actual_height = vs.get("height", 0)
    dur_str = vs.get("duration") or probe.get("format", {}).get("duration", "0")
    try:
        result.actual_duration = float(dur_str)
    except ValueError:
        pass

    if not audio_streams:
        result.warnings.append("Final output has no audio stream")

    if result.actual_duration < min_duration_sec:
        result.ok = False
        result.errors.append(
            f"Final output too short: {result.actual_duration:.1f}s (expected >= {min_duration_sec}s)"
        )

    exp_w, exp_h = RESOLUTION_MAP.get(expected_resolution, (1920, 1080))
    if result.actual_width != exp_w or result.actual_height != exp_h:
        result.warnings.append(
            f"Final output resolution: {result.actual_width}×{result.actual_height} "
            f"(expected {exp_w}×{exp_h})"
        )

    return result
