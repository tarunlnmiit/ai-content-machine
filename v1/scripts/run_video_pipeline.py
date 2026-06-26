#!/usr/bin/env python3
"""Master video pipeline — no manual stops, no attended steps.

Reads a manifest.json (written by prepare_reel_script.py or created manually)
and runs the complete pipeline from raw recording to final MP4:

  Phase 1: Preflight   — check binaries, manifest, source files
  Phase 2: Trim        — remove silences, retakes, filler words (video_trim.py)
  Phase 3: Crop        — portrait crop for reels only (video_utils.crop_vertical)
  Phase 4: Storyboard  — AI-generated beat list (storyboard_gen.py)
  Phase 5: HF Pipeline — HyperFrames compositions + renders + FFmpeg composite
  Phase 6: Output      — copy final.mp4 to canonical output path, write metadata

Each phase writes a phase marker file ({work_dir}/.phase_{N}_done) so the pipeline
is idempotent — re-running after a failure resumes from the failed phase.

Usage:
    # From a manifest (normal path after prepare_reel_script.py)
    python3 scripts/run_video_pipeline.py \\
        --raw assets/raw/2026-06-24_ds_recording.mov \\
        --manifest content/reels/2026-W26/my-slug/manifest.json

    # Inline (no manifest — for quick tests)
    python3 scripts/run_video_pipeline.py \\
        --raw assets/raw/2026-06-24_ds_recording.mov \\
        --niche ds \\
        --format reel \\
        --slug 2026-06-24_ds_test

    # Force re-run from a specific phase (e.g., redo storyboard + HF)
    python3 scripts/run_video_pipeline.py \\
        --raw assets/raw/... --manifest ... \\
        --restart-from 4
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.content_paths import derivatives_dir   # type: ignore[import]

FFMPEG_BIN  = "/opt/homebrew/bin/ffmpeg"
FFPROBE_BIN = "/opt/homebrew/bin/ffprobe"
CLAUDE_BIN  = shutil.which("claude") or "/Users/tarungupta/.local/bin/claude"

def _find_bin(name: str, fallbacks: list[str]) -> str:
    """Find a binary in PATH or known install locations."""
    found = shutil.which(name)
    if found:
        return found
    for fb in fallbacks:
        if Path(fb).exists():
            return fb
    return name  # let subprocess raise a clear error

HF_BIN = _find_bin("hyperframes", [
    "/usr/local/bin/hyperframes",
    "/opt/homebrew/bin/hyperframes",
    str(Path.home() / ".local" / "bin" / "hyperframes"),
    # npm global installs
    str(Path.home() / ".npm-global" / "bin" / "hyperframes"),
    "/opt/homebrew/lib/node_modules/.bin/hyperframes",
    "/usr/local/lib/node_modules/.bin/hyperframes",
])

# ── Phase marker helpers ───────────────────────────────────────────────────

def _phase_file(work_dir: Path, n: int) -> Path:
    return work_dir / f".phase_{n}_done"

def _phase_done(work_dir: Path, n: int) -> bool:
    return _phase_file(work_dir, n).exists()

def _mark_done(work_dir: Path, n: int, payload: dict | None = None) -> None:
    p = _phase_file(work_dir, n)
    p.write_text(json.dumps(payload or {"ts": datetime.now().isoformat()}))

def _phase_result(work_dir: Path, n: int) -> dict:
    p = _phase_file(work_dir, n)
    return json.loads(p.read_text()) if p.exists() else {}


# ── Preflight ──────────────────────────────────────────────────────────────

def phase_preflight(raw: Path, manifest: dict, work_dir: Path) -> None:
    print("\n[pipeline] Phase 1: Preflight")
    errors: list[str] = []

    # Binaries
    for name, path in [("ffmpeg", FFMPEG_BIN), ("ffprobe", FFPROBE_BIN), ("claude", CLAUDE_BIN)]:
        if not Path(path).exists():
            errors.append(f"Missing binary: {name} at {path}")

    if not Path(HF_BIN).exists() and shutil.which(HF_BIN) is None:
        errors.append(
            f"HyperFrames not found. Tried: {HF_BIN}\n"
            "   Run: which hyperframes  (then update HF_BIN or symlink to /usr/local/bin/)"
        )

    # Raw recording
    if not raw.exists():
        errors.append(f"Raw recording not found: {raw}")
    else:
        size_mb = raw.stat().st_size / 1024 / 1024
        print(f"  raw recording : {raw.name} ({size_mb:.1f} MB)")

    # Manifest fields
    required = ["niche", "format", "slug"]
    for field in required:
        if not manifest.get(field):
            errors.append(f"Manifest missing required field: '{field}'")

    niche = manifest.get("niche", "")
    if niche not in ("ds", "life", "poetry"):
        errors.append(f"Invalid niche: {niche!r} (must be ds|life|poetry)")

    if errors:
        print("\n[pipeline] ✗ PREFLIGHT FAILED:")
        for e in errors:
            print(f"   - {e}")
        raise SystemExit(1)

    print(f"  niche  : {manifest['niche']} | format: {manifest['format']} | slug: {manifest['slug']}")
    print("  Preflight PASSED ✓")


# ── Phase 2: Trim ──────────────────────────────────────────────────────────

def phase_trim(raw: Path, niche: str, work_dir: Path, is_audio_only: bool = False) -> Path:
    print("\n[pipeline] Phase 2: Trim (silence, retakes, fillers)")
    from video_trim import trim_video  # type: ignore[import]

    trim_out = work_dir / "trimmed.mp4"
    result = trim_video(
        raw=raw,
        out=trim_out,
        niche=niche,
        is_audio_only=is_audio_only,
    )

    print(f"  original  : {result.original_duration:.1f}s")
    print(f"  trimmed   : {result.trimmed_duration:.1f}s "
          f"(-{result.original_duration - result.trimmed_duration:.1f}s removed)")
    print(f"  cuts made : {len(result.cuts)}")

    _mark_done(work_dir, 2, {
        "trimmed_path": str(result.trimmed_path),
        "transcript_json": str(result.trimmed_path.parent / "transcript.json"),
        "debug_json": str(result.debug_json),
        "original_duration": result.original_duration,
        "trimmed_duration": result.trimmed_duration,
    })
    return result.trimmed_path


def phase_trim_pre_edited(raw: Path, work_dir: Path) -> Path:
    """Phase 2 for already-edited videos: skip silence/retake removal,
    copy the file as-is, then transcribe with Whisper to get transcript.json."""
    import json
    import shutil
    from video_trim import transcribe_raw  # type: ignore[import]
    from lib.video_utils import probe_duration  # type: ignore[import]

    print("\n[pipeline] Phase 2: Transcribe only (--pre-edited, no trimming)")

    trim_out = work_dir / "trimmed.mp4"
    debug_dir = work_dir / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    whisper_dir = debug_dir / "whisper"

    # Copy edited video as-is (re-encode to ensure container compatibility)
    print(f"  copying {raw.name} → trimmed.mp4 (no silence removal)")
    subprocess.run(
        [
            FFMPEG_BIN, "-y", "-loglevel", "error",
            "-i", str(raw),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
            str(trim_out),
        ],
        check=True,
    )

    duration = probe_duration(trim_out)
    print(f"  duration  : {duration:.1f}s (unchanged)")

    # Run Whisper transcription
    print("  transcribing with Whisper …")
    words = transcribe_raw(trim_out, whisper_dir)
    if not words:
        raise RuntimeError("Whisper returned no words — check audio in edited file")

    # Write transcript.json (no timestamp remapping needed — no cuts were made)
    transcript_out = work_dir / "transcript.json"
    transcript_out.write_text(json.dumps(
        [
            {
                "word": w.word, "text": w.text,
                "start": round(w.start, 3), "end": round(w.end, 3),
                "startMs": round(w.start * 1000), "endMs": round(w.end * 1000),
                "confidence": round(w.confidence, 3),
            }
            for w in words
        ],
        indent=2,
    ))
    print(f"  transcript: {len(words)} words → {transcript_out.name}")

    _mark_done(work_dir, 2, {
        "trimmed_path": str(trim_out),
        "transcript_json": str(transcript_out),
        "debug_json": "",
        "original_duration": duration,
        "trimmed_duration": duration,
        "pre_edited": True,
    })
    return trim_out


# ── Phase 3: Crop ──────────────────────────────────────────────────────────

def phase_crop(trimmed: Path, work_dir: Path) -> Path:
    print("\n[pipeline] Phase 3: Crop to portrait (9:16)")
    from lib.video_utils import crop_vertical  # type: ignore[import]

    cropped_out = work_dir / "cropped.mp4"
    crop_vertical(str(trimmed), str(cropped_out))
    print(f"  cropped → {cropped_out.name}")
    _mark_done(work_dir, 3, {"cropped_path": str(cropped_out)})
    return cropped_out


# ── Phase 4: Storyboard ────────────────────────────────────────────────────

def phase_storyboard(
    trimmed: Path,
    niche: str,
    slug: str,
    work_dir: Path,
    is_voiceover: bool = False,
    is_reel: bool = False,
) -> Path:
    print("\n[pipeline] Phase 4: Storyboard generation (Claude Opus)")
    transcript_json = trimmed.parent / "transcript.json"
    if not transcript_json.exists():
        # transcript is in work_dir
        transcript_json = work_dir / "transcript.json"
    if not transcript_json.exists():
        raise FileNotFoundError(f"transcript.json not found near {trimmed}")

    from lib.storyboard_gen import generate_storyboard  # type: ignore[import]

    storyboard, storyboard_path, debug_path = generate_storyboard(
        transcript_json=transcript_json,
        niche=niche,
        slug=slug,
        out_dir=work_dir,
        is_voiceover=is_voiceover,
        is_reel=is_reel,
    )

    n_beats = len(storyboard.beats)
    overlay_pct = sum(
        b.end_sec - b.start_sec for b in storyboard.beats if b.beat_type == "overlay"
    ) / storyboard.total_duration_sec * 100
    print(f"  beats     : {n_beats}")
    print(f"  overlay % : {overlay_pct:.0f}%  (cap: {'70' if is_reel else '40'}%)")
    print(f"  saved     : {storyboard_path}")

    _mark_done(work_dir, 4, {
        "storyboard_path": str(storyboard_path),
        "beats": n_beats,
    })
    return storyboard_path


# ── Phase 5: HyperFrames pipeline ─────────────────────────────────────────

def phase_hf(
    storyboard_path: Path,
    base_video: Path,
    transcript_json: Path,
    niche: str,
    work_dir: Path,
    is_reel: bool = False,
    has_screen_recording: bool = False,
) -> Path:
    print("\n[pipeline] Phase 5: HyperFrames build + render + composite")
    from hyperframes_pipeline import run_hf_pipeline  # type: ignore[import]

    final_mp4 = run_hf_pipeline(
        storyboard_path=storyboard_path,
        trimmed_video=base_video,
        transcript_json=transcript_json,
        niche=niche,
        work_dir=work_dir,
        is_reel=is_reel,
        has_screen_recording=has_screen_recording,
    )
    _mark_done(work_dir, 5, {"final_mp4": str(final_mp4)})
    return final_mp4


# ── Phase 6: Output ────────────────────────────────────────────────────────

def phase_output(
    final_mp4: Path,
    manifest: dict,
    work_dir: Path,
) -> Path:
    print("\n[pipeline] Phase 6: Output")
    niche = manifest["niche"]
    slug = manifest["slug"]
    fmt = manifest.get("format", "longform")
    week = manifest.get("week", _slug_to_week(slug))
    content_type = manifest.get("content_type", fmt)

    # Canonical output path
    if fmt == "reel":
        output_dir = REPO / "assets" / "reels_video" / week
    else:
        output_dir = REPO / "assets" / "video" / week
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{slug}.mp4"
    shutil.copy2(final_mp4, output_path)

    # Write pipeline metadata
    meta = {
        "slug": slug,
        "niche": niche,
        "format": fmt,
        "content_type": content_type,
        "week": week,
        "produced_at": datetime.now().isoformat(),
        "work_dir": str(work_dir),
        "output_path": str(output_path),
        "pipeline_version": "V2-HyperFrames",
    }
    meta_path = output_dir / f"{slug}_pipeline_meta.json"
    meta_path.write_text(json.dumps(meta, indent=2))

    size_mb = output_path.stat().st_size / 1024 / 1024
    print(f"\n[pipeline] ✓ COMPLETE")
    print(f"  output : {output_path}")
    print(f"  size   : {size_mb:.1f} MB")
    print(f"  week   : {week}")

    _mark_done(work_dir, 6, {"output_path": str(output_path)})
    return output_path


# ── Helpers ────────────────────────────────────────────────────────────────

def _slug_to_week(slug: str) -> str:
    import re
    from datetime import date
    m = re.match(r"(\d{4}-\d{2}-\d{2})", slug)
    if m:
        d = date.fromisoformat(m.group(1))
        iso = d.isocalendar()
        return f"{iso[0]}-W{iso[1]:02d}"
    return datetime.now().strftime("%Y-W%V")


def _load_manifest(manifest_path: Path) -> dict:
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    return json.loads(manifest_path.read_text())


def _build_work_dir(slug: str, fmt: str) -> Path:
    """Create a working directory for this pipeline run."""
    week = _slug_to_week(slug)
    if fmt == "reel":
        wd = REPO / "content" / "reels" / week / slug / "_pipeline"
    else:
        wd = REPO / "assets" / "hyperframes" / week / slug
    wd.mkdir(parents=True, exist_ok=True)
    return wd


# ── Main ───────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Run the full V2 video pipeline: raw recording → final MP4",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("--raw", required=True,
                    help="Path to raw recording (.mov, .mp4, .m4a for voiceover)")
    ap.add_argument("--manifest", default=None,
                    help="Path to manifest.json (from prepare_reel_script.py)")

    # Inline overrides (if no manifest)
    ap.add_argument("--niche", choices=["ds", "life", "poetry"],
                    help="Niche (required if no --manifest)")
    ap.add_argument("--format", dest="fmt", choices=["reel", "longform"],
                    default="longform", help="Content format (default: longform)")
    ap.add_argument("--slug", default=None,
                    help="Content slug (default: raw filename without extension)")
    ap.add_argument("--voiceover", action="store_true",
                    help="Audio-only voiceover (no talking head)")
    ap.add_argument("--pre-edited", action="store_true",
                    help="Input is already edited (skip silence/retake removal; only transcribe)")

    # Control
    ap.add_argument("--restart-from", type=int, default=None, metavar="N",
                    help="Re-run from phase N onward (1–6). Removes phase markers N+.")
    ap.add_argument("--work-dir", default=None,
                    help="Override working directory")
    args = ap.parse_args()

    raw = Path(args.raw)

    # Build manifest from args if not provided
    if args.manifest:
        manifest = _load_manifest(Path(args.manifest))
    else:
        if not args.niche:
            ap.error("--niche is required when --manifest is not provided")
        manifest = {
            "niche": args.niche,
            "format": args.fmt,
            "slug": args.slug or raw.stem,
            "content_type": args.fmt,
        }

    niche = manifest["niche"]
    fmt   = manifest.get("format", "longform")
    slug  = manifest.get("slug", raw.stem)
    is_reel = fmt == "reel"
    is_voiceover = args.voiceover or manifest.get("is_voiceover", False)
    is_audio_only = raw.suffix.lower() in (".m4a", ".mp3", ".aac", ".wav")
    is_pre_edited = args.pre_edited
    # When the base under a side panel is a screen recording (DS), do NOT pan the
    # base away — the panel is meant to sit beside the code. Default False: the base
    # is the talking head, so panels shift the speaker clear of the panel.
    has_screen_recording = manifest.get("has_screen_recording", False)

    work_dir = Path(args.work_dir) if args.work_dir else _build_work_dir(slug, fmt)
    work_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  V2 VIDEO PIPELINE")
    print(f"  slug      : {slug}")
    print(f"  niche     : {niche}  format: {fmt}  reel={is_reel}")
    print(f"  work_dir  : {work_dir}")
    print(f"{'='*60}")

    # Handle --restart-from: clear phase markers from N onward
    if args.restart_from:
        for n in range(args.restart_from, 7):
            pf = _phase_file(work_dir, n)
            if pf.exists():
                pf.unlink()
                print(f"  cleared phase {n} marker")

    t_start = time.time()

    # ── Phase 1: Preflight ─────────────────────────────────────────────────
    if not _phase_done(work_dir, 1):
        phase_preflight(raw, manifest, work_dir)
        _mark_done(work_dir, 1)
    else:
        print("[pipeline] Phase 1: Preflight — skipped (done)")

    # ── Phase 2: Trim ──────────────────────────────────────────────────────
    if not _phase_done(work_dir, 2):
        if is_pre_edited:
            trimmed = phase_trim_pre_edited(raw, work_dir)
        else:
            trimmed = phase_trim(raw, niche, work_dir, is_audio_only)
    else:
        print("[pipeline] Phase 2: Trim — skipped (done)")
        trimmed = Path(_phase_result(work_dir, 2)["trimmed_path"])

    # ── Phase 3: Crop (reel only) ──────────────────────────────────────────
    if is_reel:
        if not _phase_done(work_dir, 3):
            base_video = phase_crop(trimmed, work_dir)
        else:
            print("[pipeline] Phase 3: Crop — skipped (done)")
            base_video = Path(_phase_result(work_dir, 3)["cropped_path"])
    else:
        base_video = trimmed
        print("[pipeline] Phase 3: Crop — skipped (longform)")
        _mark_done(work_dir, 3, {"cropped_path": str(trimmed), "skipped": True})

    # Locate transcript (written by video_trim.py next to trimmed video)
    transcript_json = trimmed.parent / "transcript.json"
    if not transcript_json.exists():
        transcript_json = work_dir / "transcript.json"

    # ── Phase 4: Storyboard ────────────────────────────────────────────────
    if not _phase_done(work_dir, 4):
        storyboard_path = phase_storyboard(
            trimmed=trimmed,
            niche=niche,
            slug=slug,
            work_dir=work_dir,
            is_voiceover=is_voiceover,
            is_reel=is_reel,
        )
    else:
        print("[pipeline] Phase 4: Storyboard — skipped (done)")
        storyboard_path = Path(_phase_result(work_dir, 4)["storyboard_path"])

    # ── Phase 5: HyperFrames ───────────────────────────────────────────────
    if not _phase_done(work_dir, 5):
        final_mp4 = phase_hf(
            storyboard_path=storyboard_path,
            base_video=base_video,
            transcript_json=transcript_json,
            niche=niche,
            work_dir=work_dir,
            is_reel=is_reel,
            has_screen_recording=has_screen_recording,
        )
    else:
        print("[pipeline] Phase 5: HyperFrames — skipped (done)")
        final_mp4 = Path(_phase_result(work_dir, 5)["final_mp4"])

    # ── Phase 6: Output ────────────────────────────────────────────────────
    if not _phase_done(work_dir, 6):
        output = phase_output(final_mp4, manifest, work_dir)
    else:
        print("[pipeline] Phase 6: Output — skipped (done)")
        output = Path(_phase_result(work_dir, 6)["output_path"])

    elapsed = time.time() - t_start
    print(f"\n  Total time : {elapsed/60:.1f} min")
    print(f"  Final      : {output}\n")


if __name__ == "__main__":
    main()
