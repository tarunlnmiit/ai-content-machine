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
import time
from pathlib import Path

_T0 = time.time()


def step(label: str) -> None:
    """Print a clear, timestamped stage banner so progress is visible in logs."""
    elapsed = time.time() - _T0
    print(f"\n{'━' * 64}\n▶ {label}   (+{elapsed:.0f}s elapsed)\n{'━' * 64}", flush=True)

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
    """Cut [start,end] of any source (wav/mp3/mov/mp4) to a WAV slice. -vn keeps audio only."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    return run([
        FFMPEG_BIN, "-ss", f"{start:.2f}", "-to", f"{end:.2f}", "-i", str(src),
        "-vn", "-c:a", "pcm_s16le", str(dst), "-y",
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


def hyperframes(video: Path, slug: str, captions: bool, caption_y: float, dry: bool, fresh: bool = False) -> bool:
    # Single-file mode: pass the rendered mp4 directly. Portrait re-encode is automatic
    # (extract_video detects orientation) — do NOT use --shorts (that is glob-batch mode).
    cmd = ["python3", SCRIPTS / "hyperframes_render.py", str(video), "--slug", slug, "--intensity", "light"]
    if captions:
        cmd += ["--caption-y", str(caption_y)]
    else:
        cmd += ["--no-captions"]
    if fresh:
        cmd += ["--fresh"]
    return run(cmd, dry)


def hyperframes_done(hf_slug: str) -> bool:
    # Output is assets/hyperframes/{YYYY-MM-DD}_{hf_slug}.mp4 (date-prefixed) — match by glob.
    return bool(list((REPO / "assets" / "hyperframes").glob(f"*_{hf_slug}.mp4")))


def broll_ready(broll_dir: Path) -> bool:
    vm = broll_dir / "VIDEO_MAP.json"
    if not vm.exists():
        return False
    try:
        return any(v.get("downloaded") for v in json.loads(vm.read_text()).values())
    except Exception:
        return False


def render(composition: str, out_file: Path, edit_plan_rel: str, dry: bool) -> bool:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    props = json.dumps({"editPlanFile": edit_plan_rel})
    return run(["npx", "remotion", "render", composition, str(out_file), "--props", props], dry, cwd=REMOTION_DIR)


def main() -> None:
    ap = argparse.ArgumentParser(description="Voiceover-first pipeline orchestrator (one niche)")
    ap.add_argument("--audio", required=True, help="Voiceover source — wav/mp3/m4a or a video (mov/mp4); only the audio is used")
    ap.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    ap.add_argument("--week", required=True)
    ap.add_argument("--slug", required=True, help="Full slug e.g. 2026-06-22_ds_slug")
    ap.add_argument("--no-captions", action="store_true", help="Do not burn captions in hyperframes")
    ap.add_argument("--caption-y", type=float, default=0.82, help="Caption vertical position (0=top,1=bottom). Default 0.82 = a little above the bottom, clear of lower-third overlays.")
    ap.add_argument("--grade", default="auto",
                    choices=["auto", "cinematic", "poetry", "niche", "none"],
                    help="Color look passed to both long-form + shorts. auto = poetry niche→poetry, else cinematic.")
    ap.add_argument("--skip-shorts", action="store_true")
    ap.add_argument("--force", action="store_true", help="Redo every step even if its output already exists.")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    captions_on = not args.no_captions
    dry = args.dry_run
    force = args.force
    force_flag = ["--force"] if force else []

    def skip(label: str, exists: bool) -> bool:
        """Return True (→ skip the step) when output exists and not --force."""
        if exists and not force:
            print(f"  [skip] {label} (exists; --force to redo)")
            return True
        return False
    audio = Path(args.audio)
    if not audio.is_absolute():
        audio = REPO / audio
    if not audio.exists() and not dry:
        sys.exit(f"ERROR: audio not found: {audio}")

    caps_rel = f"captions/{args.week}/{args.slug}.captions.json"
    caps_path = REMOTION_PUBLIC / caps_rel
    scene_rel = f"scene-plans/{args.week}/{args.slug}_voiceover.json"
    broll_dir = REPO / "assets" / "videos" / args.slug

    print(f"\n=== Voiceover-first pipeline: {args.slug} ({args.niche}) ===")

    yt_script_path = REPO / "content" / "scripts" / args.week / f"{args.slug}_yt.md"
    edit_plan_path = REMOTION_PUBLIC / "edit-plans" / args.week / f"{args.slug}.json"
    long_out = REPO / "output" / "animations" / args.week / f"{args.slug}.mp4"

    # ── 1. Transcribe ──────────────────────────────────────────────
    step("[1/8] Transcribe voiceover (Whisper)")
    caps_path.parent.mkdir(parents=True, exist_ok=True)
    if not skip("captions", caps_path.exists()):
        if not run(["python3", SCRIPTS / "generate_captions.py", "--audio", str(audio),
                    "--format", "remotion_json", "--output", str(caps_path), "--model", "base"], dry):
            sys.exit(1)

    # ── 2. YouTube script deliverable ──────────────────────────────
    step("[2/8] Generate YouTube script (deliverable)")
    if not skip("yt script", yt_script_path.exists()):
        run(["python3", SCRIPTS / "generate_yt_script.py", "--captions", str(caps_path),
             "--niche", args.niche, "--week", args.week, "--slug", args.slug] + force_flag, dry)

    # ── 3. Overlay scene plan (voiceover mode) ─────────────────────
    step("[3/8] Generate overlay scene plan")
    if not skip("scene plan", (REMOTION_PUBLIC / scene_rel).exists()):
        run(["python3", SCRIPTS / "generate_scene_plans.py", "--captions", str(caps_path),
             "--niche", args.niche, "--week", args.week, "--slug", args.slug, "--mode", "voiceover"] + force_flag, dry)

    # ── 4. Landscape B-roll from transcript ────────────────────────
    step("[4/8] Fetch landscape B-roll (from transcript)")
    duration = probe_duration(audio) if not dry else 240.0
    if not skip("b-roll", broll_ready(broll_dir)):
        run(["python3", SCRIPTS / "fetch_videos.py", "--captions", str(caps_path),
             "--niche", args.niche, "--orientation", "landscape",
             "--target-clips", str(target_clips(duration))], dry)

    # ── 5. Long-form edit plan ─────────────────────────────────────
    step("[5/8] Build long-form edit plan (montage)")
    if not skip("edit plan", edit_plan_path.exists()):
        run(["python3", SCRIPTS / "prepare_voiceover_edit.py", "--audio", str(audio),
             "--broll-dir", str(broll_dir), "--scene-plan", scene_rel,
             "--niche", args.niche, "--week", args.week, "--slug", args.slug,
             "--output-size", "16x9", "--grade", args.grade, "--captions", caps_rel], dry)

    # ── 6. Render long-form + hyperframes ──────────────────────────
    step("[6/8] Render long-form (Remotion)")
    if not skip("long-form render", long_out.exists()):
        render("VoiceoverLong", long_out, f"edit-plans/{args.week}/{args.slug}.json", dry)
    step("[6/8] Hyperframes long-form (captions + overlays)")
    if not skip("long-form hyperframes", hyperframes_done(f"{args.week}_{args.slug}")):
        hyperframes(long_out, f"{args.week}_{args.slug}", captions_on, args.caption_y, dry=dry, fresh=force)

    if args.skip_shorts:
        print("\n[done] long-form complete (shorts skipped).")
        return

    # ── 7. Detect self-complete sections ───────────────────────────
    step("[7/8] Detect self-complete short sections")
    sections_path = REPO / "content" / "derivatives" / args.week / args.slug / "short_sections.json"
    if not skip("short sections", sections_path.exists()):
        run(["python3", SCRIPTS / "detect_short_sections.py", "--captions", str(caps_path),
             "--niche", args.niche, "--week", args.week, "--slug", args.slug] + force_flag, dry)

    if dry:
        print("\n[dry-run] would now build one portrait short per detected section.")
        return

    if not sections_path.exists():
        print("[shorts] no sections file produced — skipping shorts.")
        return
    sections = json.loads(sections_path.read_text())
    full_caps = json.loads(caps_path.read_text())

    # ── 8. Per-section portrait shorts ─────────────────────────────
    step(f"[8/8] Build {len(sections)} portrait short(s)")
    for i, sec in enumerate(sections):
        nn = f"{i + 1:02d}"
        sslug = f"{args.slug}_s{nn}"
        start, end = float(sec["startSec"]), float(sec["endSec"])
        print(f"\n──── Short {nn}/{len(sections)}: {start:.1f}-{end:.1f}s ────")

        sec_caps_rel = f"captions/{args.week}/{sslug}.captions.json"
        sec_caps_path = REMOTION_PUBLIC / sec_caps_rel
        sec_broll_dir = REPO / "assets" / "videos" / f"{sslug}_portrait"
        sec_scene_rel = f"scene-plans/{args.week}/{sslug}_voiceover.json"
        sec_edit_plan = REMOTION_PUBLIC / "edit-plans" / args.week / f"{sslug}.json"
        sec_wav = REPO / "assets" / "audio" / args.week / f"{sslug}_voiceover.wav"
        short_out = REPO / "output" / "animations" / args.week / f"{sslug}.mp4"

        if not skip("section wav", sec_wav.exists()):
            cut_wav(audio, start, end, sec_wav, dry)
        if force or not sec_caps_path.exists():
            write_section_captions(full_caps, start, end, sec_caps_path)

        # portrait B-roll for this section (fetch_videos derives the stem from the captions
        # filename = sslug; out-suffix is appended → assets/videos/{sslug}_portrait)
        sec_duration = end - start
        if not skip("section b-roll", broll_ready(sec_broll_dir)):
            run(["python3", SCRIPTS / "fetch_videos.py", "--captions", str(sec_caps_path),
                 "--niche", args.niche, "--orientation", "portrait",
                 "--out-suffix", "_portrait",
                 "--target-clips", str(target_clips(sec_duration, portrait=True))], dry)

        if not skip("section scene plan", (REMOTION_PUBLIC / sec_scene_rel).exists()):
            run(["python3", SCRIPTS / "generate_scene_plans.py", "--captions", str(sec_caps_path),
                 "--niche", args.niche, "--week", args.week, "--slug", sslug, "--mode", "voiceover"] + force_flag, dry)

        if not skip("section edit plan", sec_edit_plan.exists()):
            run(["python3", SCRIPTS / "prepare_voiceover_edit.py", "--audio", str(sec_wav),
                 "--broll-dir", str(sec_broll_dir), "--scene-plan", sec_scene_rel,
                 "--niche", args.niche, "--week", args.week, "--slug", sslug,
                 "--output-size", "9x16", "--grade", args.grade, "--captions", sec_caps_rel], dry)

        if not skip("section render", short_out.exists()):
            render("VoiceoverShort", short_out, f"edit-plans/{args.week}/{sslug}.json", dry)
        if not skip("section hyperframes", hyperframes_done(f"{args.week}_{sslug}")):
            hyperframes(short_out, f"{args.week}_{sslug}", captions_on, args.caption_y, dry=dry, fresh=force)

    print(f"\n[done] long-form + {len(sections)} short(s) built for {args.slug}.")


if __name__ == "__main__":
    main()
