#!/usr/bin/env python3
"""Voiceover-first weekly pipeline orchestrator (one niche / one voiceover).

Given a blog (already written) and an AUDIO-ONLY voiceover, produces:
  - 1 long-form LANDSCAPE video: full-screen B-roll montage + voiceover + Remotion overlays,
    then hyperframes (captions burned by hyperframes).
  - N portrait SHORTS from auto-detected self-complete sections, each with portrait B-roll +
    its audio slice + overlays + hyperframes.

Downstream publishing (Medium / LinkedIn / scheduler) is unchanged — run the normal pipeline
after this. This script only builds the videos.

Usage:
  python3 scripts/run_voiceover_week.py \\
    --audio assets/audio/2026-W26/2026-06-22_ds_slug_voiceover.wav \\
    --niche ds --week 2026-W26 --slug 2026-06-22_ds_slug

Flags: --no-captions (skip hyperframes captions), --caption-y, --skip-shorts, --dry-run.
"""

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
REMOTION_DIR = REPO / "remotion"
REMOTION_PUBLIC = REMOTION_DIR / "public"
SCRIPTS = REPO / "scripts"

FFMPEG_BIN = "/opt/homebrew/bin/ffmpeg"

SECONDS_PER_CLIP = 12  # one unique B-roll clip per ~12s of audio (variety target)


def run(cmd: list[str], dry: bool, cwd: Path | None = None) -> bool:
    printable = " ".join(str(c) for c in cmd)
    print(f"\n$ {printable}")
    if dry:
        return True
    r = subprocess.run([str(c) for c in cmd], cwd=str(cwd) if cwd else None)
    if r.returncode != 0:
        print(f"  [FAIL] exit {r.returncode}: {printable[:80]}", file=sys.stderr)
        return False
    return True


def target_clips(duration_sec: float, portrait: bool = False) -> int:
    base = math.ceil(duration_sec / SECONDS_PER_CLIP)
    return max(4 if portrait else 5, min(base, 25))


def probe_duration(media: Path) -> float:
    out = subprocess.run(
        ["/opt/homebrew/bin/ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(media)],
        capture_output=True, text=True,
    ).stdout
    try:
        return float(json.loads(out)["format"]["duration"])
    except Exception:
        return 0.0


def cut_wav(src: Path, start: float, end: float, dst: Path, dry: bool) -> bool:
    dst.parent.mkdir(parents=True, exist_ok=True)
    return run([
        FFMPEG_BIN, "-ss", f"{start:.2f}", "-to", f"{end:.2f}", "-i", str(src),
        "-c", "copy" if src.suffix.lower() == ".wav" else "pcm_s16le", str(dst), "-y",
    ], dry) if src.suffix.lower() != ".wav" else run([
        FFMPEG_BIN, "-ss", f"{start:.2f}", "-to", f"{end:.2f}", "-i", str(src),
        "-c:a", "pcm_s16le", str(dst), "-y",
    ], dry)


def write_section_captions(full_caps: list[dict], start: float, end: float, dst: Path) -> None:
    """Subset captions to [start,end] and rebase to 0 — feeds keyword fetch + scene-plan timing."""
    s_ms, e_ms = start * 1000, end * 1000
    subset = []
    for c in full_caps:
        cs = c.get("startMs", 0)
        if cs < s_ms or cs > e_ms:
            continue
        shifted = dict(c)
        shifted["startMs"] = round(c.get("startMs", 0) - s_ms)
        shifted["endMs"] = round(c.get("endMs", 0) - s_ms)
        if "timestampMs" in shifted:
            shifted["timestampMs"] = round(c.get("timestampMs", 0) - s_ms)
        subset.append(shifted)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(subset, indent=2), encoding="utf-8")


def hyperframes(video: Path, slug: str, captions: bool, caption_y: float, dry: bool) -> bool:
    # Single-file mode: pass the rendered mp4 directly. Portrait re-encode is automatic
    # (extract_video detects orientation) — do NOT use --shorts (that is glob-batch mode).
    cmd = ["python3", SCRIPTS / "hyperframes_render.py", str(video), "--slug", slug, "--intensity", "light"]
    if captions:
        cmd += ["--caption-y", str(caption_y)]
    else:
        cmd += ["--no-captions"]
    return run(cmd, dry)


def render(composition: str, out_file: Path, edit_plan_rel: str, dry: bool) -> bool:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    props = json.dumps({"editPlanFile": edit_plan_rel})
    return run(["npx", "remotion", "render", composition, str(out_file), "--props", props], dry, cwd=REMOTION_DIR)


def main() -> None:
    ap = argparse.ArgumentParser(description="Voiceover-first pipeline orchestrator (one niche)")
    ap.add_argument("--audio", required=True, help="Audio-only voiceover (wav/mp3)")
    ap.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    ap.add_argument("--week", required=True)
    ap.add_argument("--slug", required=True, help="Full slug e.g. 2026-06-22_ds_slug")
    ap.add_argument("--no-captions", action="store_true", help="Do not burn captions in hyperframes")
    ap.add_argument("--caption-y", type=float, default=0.82, help="Caption vertical position (0=top,1=bottom). Default 0.82 = a little above the bottom, clear of lower-third overlays.")
    ap.add_argument("--skip-shorts", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    captions_on = not args.no_captions
    dry = args.dry_run
    audio = Path(args.audio)
    if not audio.is_absolute():
        audio = REPO / audio
    if not audio.exists() and not dry:
        sys.exit(f"ERROR: audio not found: {audio}")

    caps_rel = f"captions/{args.week}/{args.slug}.captions.json"
    caps_path = REMOTION_PUBLIC / caps_rel
    scene_rel = f"scene-plans/{args.week}/{args.slug}_voiceover.json"
    broll_dir = REPO / "assets" / "videos" / args.slug

    # ── 1. Transcribe ──────────────────────────────────────────────
    caps_path.parent.mkdir(parents=True, exist_ok=True)
    if not run(["python3", SCRIPTS / "generate_captions.py", "--audio", str(audio),
                "--format", "remotion_json", "--output", str(caps_path), "--model", "base"], dry):
        sys.exit(1)

    # ── 2. YouTube script deliverable ──────────────────────────────
    run(["python3", SCRIPTS / "generate_yt_script.py", "--captions", str(caps_path),
         "--niche", args.niche, "--week", args.week, "--slug", args.slug], dry)

    # ── 3. Overlay scene plan (voiceover mode) ─────────────────────
    run(["python3", SCRIPTS / "generate_scene_plans.py", "--captions", str(caps_path),
         "--niche", args.niche, "--week", args.week, "--slug", args.slug, "--mode", "voiceover"], dry)

    # ── 4. Landscape B-roll from transcript ────────────────────────
    duration = probe_duration(audio) if not dry else 240.0
    run(["python3", SCRIPTS / "fetch_videos.py", "--captions", str(caps_path),
         "--niche", args.niche, "--orientation", "landscape",
         "--target-clips", str(target_clips(duration))], dry)

    # ── 5. Long-form edit plan ─────────────────────────────────────
    run(["python3", SCRIPTS / "prepare_voiceover_edit.py", "--audio", str(audio),
         "--broll-dir", str(broll_dir), "--scene-plan", scene_rel,
         "--niche", args.niche, "--week", args.week, "--slug", args.slug,
         "--output-size", "16x9", "--captions", caps_rel], dry)

    # ── 6. Render long-form + hyperframes ──────────────────────────
    long_out = REPO / "output" / "animations" / args.week / f"{args.slug}.mp4"
    render("VoiceoverLong", long_out, f"edit-plans/{args.week}/{args.slug}.json", dry)
    hyperframes(long_out, f"{args.week}_{args.slug}", captions_on, args.caption_y, dry=dry)

    if args.skip_shorts:
        print("\n[done] long-form complete (shorts skipped).")
        return

    # ── 7. Detect self-complete sections ───────────────────────────
    sections_path = REPO / "content" / "derivatives" / args.week / args.slug / "short_sections.json"
    run(["python3", SCRIPTS / "detect_short_sections.py", "--captions", str(caps_path),
         "--niche", args.niche, "--week", args.week, "--slug", args.slug], dry)

    if dry:
        print("\n[dry-run] would now build one portrait short per detected section.")
        return

    if not sections_path.exists():
        print("[shorts] no sections file produced — skipping shorts.")
        return
    sections = json.loads(sections_path.read_text())
    full_caps = json.loads(caps_path.read_text())

    # ── 8. Per-section portrait shorts ─────────────────────────────
    for i, sec in enumerate(sections):
        nn = f"{i + 1:02d}"
        sslug = f"{args.slug}_s{nn}"
        start, end = float(sec["startSec"]), float(sec["endSec"])
        print(f"\n──── Short {nn}: {start:.1f}-{end:.1f}s ────")

        sec_wav = REPO / "assets" / "audio" / args.week / f"{sslug}_voiceover.wav"
        cut_wav(audio, start, end, sec_wav, dry)

        sec_caps_rel = f"captions/{args.week}/{sslug}.captions.json"
        sec_caps_path = REMOTION_PUBLIC / sec_caps_rel
        write_section_captions(full_caps, start, end, sec_caps_path)

        # portrait B-roll for this section (own output dir via out-suffix)
        sec_duration = end - start
        # fetch_videos derives the stem from the captions filename (= sslug); out-suffix is appended.
        run(["python3", SCRIPTS / "fetch_videos.py", "--captions", str(sec_caps_path),
             "--niche", args.niche, "--orientation", "portrait",
             "--out-suffix", "_portrait",
             "--target-clips", str(target_clips(sec_duration, portrait=True))], dry)
        sec_broll_dir = REPO / "assets" / "videos" / f"{sslug}_portrait"

        # overlay scene plan for the short (section-relative timing)
        sec_scene_rel = f"scene-plans/{args.week}/{sslug}_voiceover.json"
        run(["python3", SCRIPTS / "generate_scene_plans.py", "--captions", str(sec_caps_path),
             "--niche", args.niche, "--week", args.week, "--slug", sslug, "--mode", "voiceover"], dry)

        run(["python3", SCRIPTS / "prepare_voiceover_edit.py", "--audio", str(sec_wav),
             "--broll-dir", str(sec_broll_dir), "--scene-plan", sec_scene_rel,
             "--niche", args.niche, "--week", args.week, "--slug", sslug,
             "--output-size", "9x16", "--captions", sec_caps_rel], dry)

        short_out = REPO / "output" / "animations" / args.week / f"{sslug}.mp4"
        render("VoiceoverShort", short_out, f"edit-plans/{args.week}/{sslug}.json", dry)
        hyperframes(short_out, f"{args.week}_{sslug}", captions_on, args.caption_y, dry=dry)

    print(f"\n[done] long-form + {len(sections)} short(s) built for {args.slug}.")


if __name__ == "__main__":
    main()
