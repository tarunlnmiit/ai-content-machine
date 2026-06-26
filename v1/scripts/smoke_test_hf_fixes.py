#!/usr/bin/env python3
"""Smoke-test the HyperFrames v2 render fixes by producing frames to eyeball.

Tests three fixes without running the full 17-min pipeline:
  1. Overlay text overlap — regenerates the two beats that previously ghosted
     (first overlay + lower-third-minimal) with cache OFF and the current prompt,
     renders each, and extracts a frame after both lines appear.
  2. Panel pan-shift — composites a panel-right beat window over the base with the
     new shift, extracting one frame, so you can confirm the speaker clears the panel.
  3. (Outro length is a deterministic Python clamp — see Tier 0 in the docs; not
     re-tested here since it needs no render.)

All output PNGs land in <work_dir>/smoke_out/. Open them and check:
  - beat frames: BOTH text lines readable, on separate rows, no ghost overlap.
  - shift frame: the speaker/base content sits clear of the right-half panel.

Usage:
  python3 scripts/smoke_test_hf_fixes.py \
    --work-dir assets/hyperframes/2026-W26/2026-06-26_test-ds-longform-full \
    --niche ds
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS / "lib"))

import hf_beat_builder as B  # noqa: E402

FFMPEG = "/opt/homebrew/bin/ffmpeg"
HF = "/usr/local/bin/hyperframes"


def _storyboard(work_dir: Path) -> dict:
    for name in ("STORYBOARD.json", "storyboard.json"):
        p = work_dir / name
        if p.exists():
            return json.loads(p.read_text())
    raise FileNotFoundError(f"No storyboard in {work_dir}")


def _beat_spec(raw: dict, words: list[dict], caption_style: str) -> B.BeatSpec:
    start, end = float(raw["start_sec"]), float(raw["end_sec"])
    spoken = [w["word"] for w in words
              if w.get("start", 0) >= start and w.get("end", 0) <= end + 0.1]
    caption = " ".join(spoken) if spoken else raw.get("transcript_excerpt", "")
    block = raw.get("overlay_block") or "editorial-emphasis"
    layout = raw.get("overlay_layout") or "fullscreen"
    content = raw.get("overlay_content") or ""
    return B.BeatSpec(
        idx=raw.get("beat_id", 0), block_type=block, start=start, end=end,
        caption=caption, caption_style=caption_style,
        data={"content": content} if content else {}, layout=layout,
        broll_keywords=raw.get("broll_keywords"),
    )


def _render_and_frame(beat: B.BeatSpec, niche: str, out: Path, label: str) -> None:
    project = B.build_beat_project(beat, niche, out / "_proj", use_cache=False)
    fmt = B.get_render_format(beat.block_type, beat.layout)
    mov = out / f"{label}.{fmt}"
    cmd = [HF, "render", str(project), "--format", fmt, "--output", str(mov),
           "--fps", "30", "--variables", json.dumps({"caption_text": beat.caption}),
           "--quiet"]
    env = {"FFMPEG_PATH": FFMPEG}
    import os
    r = subprocess.run(cmd, capture_output=True, text=True,
                       env={**os.environ, **env}, timeout=600)
    if r.returncode != 0:
        print(f"  ✗ render failed for {label}: {r.stderr[-300:]}")
        return
    # frame after both lines have appeared (~75% through the beat, min 3s)
    t = max(3.0, (beat.end - beat.start) * 0.75)
    png = out / f"{label}_t{int(t)}.png"
    over_white = ("[1]format=rgba[fg];color=white:s=1920x1080[bg];"
                  "[bg][fg]scale2ref[bg][fg];[bg][fg]overlay")
    subprocess.run([FFMPEG, "-y", "-v", "error", "-i", str(mov), "-i", str(mov),
                    "-ss", str(t), "-frames:v", "1", str(png)],
                   capture_output=True)
    if not png.exists():  # alpha mov: extract straight (viewer shows transparency)
        subprocess.run([FFMPEG, "-y", "-v", "error", "-ss", str(t), "-i", str(mov),
                        "-frames:v", "1", str(png)], capture_output=True)
    print(f"  ✓ {label}: {png}")


def _find_or_render_panel(beat: B.BeatSpec, niche: str, wd: Path, out: Path) -> Path | None:
    """Reuse an existing rendered panel MOV if present, else render one."""
    fmt = B.get_render_format(beat.block_type, beat.layout)
    for cand in (wd / "hf_renders").glob(f"*{beat.block_type}*.{fmt}"):
        return cand
    project = B.build_beat_project(beat, niche, out / "_proj", use_cache=False)
    mov = out / f"panel_{beat.block_type}.{fmt}"
    import os
    r = subprocess.run(
        [HF, "render", str(project), "--format", fmt, "--output", str(mov),
         "--fps", "30", "--variables", json.dumps({"caption_text": beat.caption}), "--quiet"],
        capture_output=True, text=True, env={**os.environ, "FFMPEG_PATH": FFMPEG}, timeout=600)
    return mov if r.returncode == 0 and mov.exists() else None


def _panel_frame(base: Path, panel: Path, base_t: float, panel_t: float,
                 shift: bool, dst: Path) -> None:
    """One frame of panel overlaid on base, optionally with the pan-shift applied."""
    if shift:  # mirrors hyperframes_pipeline: aspect-preserving 16:9 pan, no stretch
        base_chain = "[0:v]scale=1920:1080,crop=1500:844:420:118,scale=1920:1080[b]"
    else:
        base_chain = "[0:v]scale=1920:1080[b]"
    fc = f"{base_chain};[1:v]format=rgba[p];[b][p]overlay=0:0[v]"
    subprocess.run(
        [FFMPEG, "-y", "-v", "error",
         "-ss", f"{base_t:.2f}", "-i", str(base),
         "-ss", f"{panel_t:.2f}", "-i", str(panel),
         "-filter_complex", fc, "-map", "[v]", "-frames:v", "1", str(dst)],
        capture_output=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work-dir", required=True)
    ap.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    args = ap.parse_args()

    wd = Path(args.work_dir)
    out = wd / "smoke_out"
    out.mkdir(exist_ok=True)
    sb = _storyboard(wd)
    words = json.loads((wd / "transcript.json").read_text())
    cstyle = sb.get("caption_style", "matrix-decode")
    overlays = [b for b in sb["beats"] if b.get("beat_type") == "overlay"]

    print("\n[1] Overlay text-overlap fix — regenerating first overlay + any lower-third")
    targets = []
    if overlays:
        targets.append(("first_overlay", overlays[0]))
    lt = next((b for b in overlays if b.get("overlay_block") == "lower-third-minimal"), None)
    if lt:
        targets.append(("lower_third", lt))
    for label, raw in targets:
        _render_and_frame(_beat_spec(raw, words, cstyle), args.niche, out, label)

    print("\n[2] Panel pan-shift — real panel composited over base, BEFORE vs AFTER shift")
    pr = next((b for b in overlays if b.get("overlay_layout") == "panel-right"), None)
    base = wd / "trimmed.mp4"
    if pr and base.exists():
        mid = (float(pr["start_sec"]) + float(pr["end_sec"])) / 2
        # Render the actual panel (alpha MOV) so the preview shows the real overlay,
        # not just a cropped base. Reuse an existing hf_renders/*.mov if present.
        beat = _beat_spec(pr, words, cstyle)
        panel_mov = _find_or_render_panel(beat, args.niche, wd, out)
        if panel_mov is None:
            print("  (could not render panel beat — skipped)")
        else:
            # local panel time = beat-relative offset of `mid`
            pt = max(0.5, mid - float(pr["start_sec"]))
            # BEFORE: panel over un-shifted base (what the panel covers today)
            _panel_frame(base, panel_mov, mid, pt, shift=False,
                         dst=out / "panel_BEFORE_noshift.png")
            # AFTER: panel over shifted base (new behaviour)
            _panel_frame(base, panel_mov, mid, pt, shift=True,
                         dst=out / "panel_AFTER_shift.png")
            print(f"  ✓ panel_BEFORE_noshift.png  (speaker behind the panel — old behaviour)")
            print(f"  ✓ panel_AFTER_shift.png     (speaker panned clear — new behaviour)")
            print("    Compare the two. If THIS base is a screen recording, you WANT the")
            print("    BEFORE look — set has_screen_recording:true so it does NOT shift.")
    else:
        print("  (no panel-right beat or trimmed.mp4 — skipped)")

    print(f"\nDone. Open the PNGs in: {out}")


if __name__ == "__main__":
    main()
