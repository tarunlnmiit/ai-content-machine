---
title: "V2 Video Pipeline — HyperFrames + AI Storyboard"
type: doc
slug: v2-pipeline
tags: [content/doc]
---
# V2 Video Pipeline — HyperFrames + AI Storyboard

> Added 2026-06-24. This replaces the old manual-DaVinci path for both talking-head and
> voiceover long-form videos, AND handles reels (blog-to-reel + tool reels) in the same pipeline.
> The old scripts (prepare_remotion_edit.py, create_vertical_reels.py) still exist and are NOT deleted.

---

## One-sentence summary

Record → run one command → get a finished MP4. No DaVinci, no manual stops.

---

## Quick start (new reel from a blog post)

```bash
# 1. Write the reel script (before you record)
python3 v1/scripts/prepare_reel_script.py \
  --from blog content/blogs/2026-W26/2026-06-24_ds_python-tips.md \
  --niche ds \
  --slug 2026-06-24_ds_python-tips-reel

# 2. Read v1/content/reels/2026-W26/2026-06-24_ds_python-tips-reel/reel_script.md
#    Record your talking head or voiceover. Save to assets/raw/

# 3. Run the pipeline (no further manual steps)
python3 v1/scripts/run_video_pipeline.py \
  --raw assets/raw/2026-06-24_ds_python-tips.mov \
  --manifest v1/content/reels/2026-W26/2026-06-24_ds_python-tips-reel/manifest.json
```

Output lands in `assets/reels_video/2026-W26/2026-06-24_ds_python-tips-reel.mp4`.

---

## Quick start (tool/build-in-public reel)

```bash
# 1. Write the reel script
python3 v1/scripts/prepare_reel_script.py \
  --from tool 2026-W26 \
  --niche ds \
  --project free_tool_ds \
  --slug 2026-06-24_ds_n8n-tool-reel

# 2. Record reel_script.md. Save to assets/raw/

# 3. Run pipeline
python3 v1/scripts/run_video_pipeline.py \
  --raw assets/raw/2026-06-24_ds_n8n-tool.mov \
  --manifest v1/content/reels/2026-W26/2026-06-24_ds_n8n-tool-reel/manifest.json
```

---

## Quick start (long-form talking head — no manifest)

```bash
python3 v1/scripts/run_video_pipeline.py \
  --raw assets/raw/2026-06-24_ds_longform.mov \
  --niche ds \
  --format longform \
  --slug 2026-06-24_ds_longform
```

---

## Quick start (voiceover / audio-only)

```bash
python3 v1/scripts/run_video_pipeline.py \
  --raw assets/audio/2026-06-24_life_voiceover.m4a \
  --niche life \
  --format longform \
  --slug 2026-06-24_life-habits-voiceover \
  --voiceover
```

---

## Pipeline phases

| Phase | What happens | Script / function |
|---|---|---|
| 1 Preflight | Check binaries (ffmpeg, claude, hyperframes), validate manifest | `run_video_pipeline.py` |
| 2 Trim | Whisper transcribe (one pass), adaptive silence detection, retake removal (pause + token overlap), filler word disambiguation | `scripts/video_trim.py` |
| 3 Crop | Portrait 9:16 crop for reels only; skipped for long-form | `scripts/lib/video_utils.py:crop_vertical` |
| 4 Storyboard | Claude Opus reads transcript + DESIGN.md → JSON beat list (block types, timestamps, captions) | `scripts/lib/storyboard_gen.py` |
| 5 HyperFrames | Claude Opus writes composition HTML per beat → `hyperframes render` per beat → FFmpeg composite all beats over trimmed video | `scripts/hyperframes_pipeline.py` |
| 6 Output | Copy final.mp4 to canonical path, write pipeline_meta.json | `run_video_pipeline.py:phase_output` |

---

## Phase checkpointing

Each phase writes a `.phase_N_done` marker to the working directory. Re-running is idempotent:
```bash
# Resume from a failed phase
python3 v1/scripts/run_video_pipeline.py --raw ... --manifest ... --restart-from 4
```

`--restart-from 4` clears phase markers 4, 5, 6 and re-runs storyboard + HF + output.

---

## Working directory layout

```
content/reels/<week>/<slug>/_pipeline/   (reels)
assets/hyperframes/<week>/<slug>/         (long-form)
  .phase_1_done
  .phase_2_done
  ...
  trimmed.mp4
  transcript.json          ← word-level timestamps (remapped post-cut)
  debug/trim_debug.json
  cropped.mp4              (reel only)
  storyboard.json
  hf_beats/
    beat_00_code-particle-assemble/
      index.html
    beat_01_matrix-decode/
      index.html
    ...
  hf_renders/
    beat_00_code-particle-assemble.mov
    beat_01_matrix-decode.mov
    ...
  final.mp4
```

---

## Design look bibles (per niche)

Edit these files to change colors, typography, allowed blocks, or motion pacing:
- `v1/data/kb/design/ds_design.md`    — Data Science niche
- `v1/data/kb/design/life_design.md`  — Life & Self-Development niche
- `v1/data/kb/design/poetry_design.md` — Poetry niche

Each file has a `## SHORT-FORM OVERRIDES` section that kicks in when `manifest.format = "reel"`.

---

## Reel script generator

Before recording, always run `prepare_reel_script.py`. It outputs:
- `reel_script.md` — what to say, 5-beat structure, ~45 seconds
- `manifest.json`  — pipeline reads this after you record

```bash
python3 v1/scripts/prepare_reel_script.py --help
```

Two modes:
- `--from blog <path>` — condense a blog post into a 5-beat reel
- `--from tool <week>` — build-in-public/tool reel with `--project <key>`

---

## HyperFrames beat format

Each beat renders to a MOV (alpha) or MP4 (opaque) via:
```bash
hyperframes render ./hf_beats/beat_00_block_type \
  --format mov \
  --resolution portrait \
  --fps 30 \
  --quality high \
  --variables '{"caption_text":"..."}' \
  --quiet
```

- **Alpha beats** (MOV): overlaid on trimmed talking head at their timestamp
- **Full-frame beats** (MP4): replace the base video frame for their window
- Variables are injected at render time — caption text, colors, etc.

### Composite timing & panel handling (`build_ffmpeg_composite`)

- **Half-open beat windows.** Every overlay `enable` predicate uses
  `gte(t,start)*lt(t,end-half_frame)` (half_frame = 1/60s at 30fps) instead of an
  inclusive `between(t,start,end)`. Back-to-back beats sharing a boundary (A ends
  at t=20, B starts at t=20) no longer both fire on that frame — no one-frame
  double-overlay.
- **Panel pan/crop shift (all niches; opt-out for screen recordings).** When a
  `panel-right` / `panel-left` beat is active, the panel hides half the frame, so the
  base video is panned the opposite way during that window so the speaker sits CLEAR
  of the panel: `panel-right` → crop an aspect-preserving 16:9 window panned right
  (speaker moves left), `panel-left` → window panned left (speaker moves right), each
  rescaled to 1920×1080. The crop keeps 16:9 (`SHIFT_CROP_W × SHIFT_CROP_W*9/16`,
  vertically centred) so it is a clean punch-in + pan — **not** an anamorphic stretch;
  faces keep their proportions. `SHIFT_CROP_W=1500` moves a centred speaker from x≈960
  to x≈691, clear of the panel-right edge (x≈980); narrow toward 1440 for a stronger
  pan, widen toward 1600 for a gentler one. A pure zero-zoom translate is not used —
  it would expose an empty strip the panel can't fully cover. The shift
  is injected as a time-gated overlay **before** the panel's alpha beat composites on
  top. The ONLY case left unshifted is a DS video whose base is a screen recording —
  set `"has_screen_recording": true` in the manifest, and DS panels then sit beside the
  code without panning it. (Standalone runs: `--has-screen-recording`.) The flag flows
  manifest → `run_video_pipeline.phase_hf` → `run_hf_pipeline` → `build_ffmpeg_composite`.

The composition HTML is generated by `hf_beat_builder.py` via Claude Opus, one call per beat.
Beat HTML is cached by content hash at `v1/.hf_beat_cache/` (cache version `v9`).

- **Liquid-glass fullscreen overlays (life/poetry).** Fullscreen beats that are not
  `weight-shift` or `logo-outro` get a frosted-glass background rule injected into
  the prompt (`rgba(10,8,5,0.55)` + `backdrop-filter:blur(18px)`) so the talking
  head stays partially visible underneath; `weight-shift`/`logo-outro` keep their
  intentional dark background.

- **No overlapping text strings.** The composition prompt forbids placing two
  *different* phrases at the same `top/left` and crossfading between them (a dimmed
  line behind a bright line reads as garbled half-rendered text). Two-phrase content
  (split on `·` / `/` / line break) must go on distinct rows, both fully legible for
  the whole beat. Lever: `hf_beat_builder.py:_compose_prompt`.

## Outro timing

The outro is a **short sign-off card on the final 5–10 seconds** (target 8s),
hugging the end of the video — *not* a fraction of runtime. The old "outro starts at
≥90% of total_duration" rule ballooned the outro to ~105s on a 17-minute video.
`storyboard_gen.py` now clamps any outro beat to `[total_duration − 8s, total_duration]`
(constants `OUTRO_TARGET_SEC` / `OUTRO_MIN_SEC` / `OUTRO_MAX_SEC`). The speaker (base
video) stays on-camera up to that point; the uncovered tail before the outro simply
shows the trimmed talking-head footage (beats composite over a continuous base video).

---

## Captions — continuous word-synced track (2026-07-01)

Captions are burned as ONE continuous track over the final composite, not per beat.

- **Source:** `transcript.json` word-level timings. Module: `scripts/lib/caption_track.py`.
- **Style:** karaoke active-word pop — two lines, primary white (`#f0f4ff`), the
  currently-spoken word enlarged + tinted with the niche accent (`NICHE_ACCENT`:
  ds cyan, life amber, poetry violet). Font Inter 700, mobile-safe margins.
- **Coverage:** EVERY segment, including plain talking-head stretches. Previously the
  per-beat pill only appeared on overlay beats (`build_all_beats` skips `talking_head`
  beats), so talking-head reels had caption gaps — the reel formula requires captions
  burned in (85% watch muted).
- **Suppression:** words inside a beat whose block ∈ `NO_CAPTION_BLOCKS` are dropped
  (that block already renders the text) — no double subtitles.
- **Wiring:** `run_hf_pipeline(..., burn_global_captions=True)` burns the track right
  after `build_ffmpeg_composite` (Phase 4b). When on, the per-beat pill is suppressed
  via `build_all_beats(..., global_captions=True)`. Beat cache bumped to `v10`. Toggle
  off with `burn_global_captions=False`.
- **ffmpeg requirement (libass):** burning the `.ass` track needs an ffmpeg built with
  **libass**. The pipeline's default `/opt/homebrew/bin/ffmpeg` on this machine is a
  stripped build WITHOUT libass, so `burn_caption_track` (`caption_track.py`) resolves at
  runtime to a libass-capable binary — it tries the passed bin, then the ffmpeg sibling of
  the running python (`content_engine_env` conda ffmpeg HAS libass), then PATH; the first
  with the `ass` filter wins. It also picks an available H.264 encoder: `libx264`
  (`-crf 18 -preset medium`) if present, else `h264_videotoolbox` (`-b:v 10M`, since
  VideoToolbox rejects `-crf`/`-preset`). Run the pipeline under the conda env python so
  the sibling resolves. If no libass ffmpeg is found it raises a clear error.

---

## Hook, overlays & beat prompt (2026-07-01, Phase 2)

- **Hook overlay (retention):** beat 1 is always a hook overlay covering ~0–3s.
  `build_storyboard_prompt` requires it (rule 13) and `parse_storyboard_response`
  ENFORCES it via `_ensure_hook_overlay` — if the model opens on a bare talking_head, a
  hook overlay is auto-inserted (block = the video's caption_style or a text fallback;
  content derived from the opening line). Toggle with `force_hook=False`.
- **Reel overlay cap fixed:** the density downgrade used a hardcoded 40% for ALL
  formats, silently converting most reel overlays back to talking_head (this starved
  reels of overlays *and* the hook). Now `overlay_cap = 1.0` for reels (all-overlay by
  design) / `0.40` for long-form; prompt `overlay_cap_pct` for reels raised 70→100.
- **Enumeration → labeled callouts:** storyboard rule 14 — when narration lists named
  parts/steps ("in five parts: role, task…"), emit one labeled overlay per item
  (`lower-third-minimal` / `floating-pill-badge` / `bento-data-grid`); mandatory over
  screen-recordings so a raw capture is never left unlabeled.
- **Beat prompt (`hf_beat_builder._compose_prompt`):** removed the hardcoded blue
  gradient/glow (it leaked DS colours into life/poetry) — it now references the injected
  DESIGN CONSTANTS palette by name; `is_reel` now adds a vertical-safe-area + big-type
  guidance block; `_load_design_constants` cap raised 2500→6000 so the full
  PALETTE/MOTION/CAPTION/SHORT-FORM sections reach the model.

---

## Review gate — `--review` (2026-07-01)

A human checkpoint between the (cheap) storyboard and the (expensive) beat render.

- `python3 v1/scripts/run_video_pipeline.py --raw <file> --manifest <m> --review`
  runs Phases 1–4 (trim → transcript → storyboard) then **halts** before Phase 5,
  printing a beat summary and the paths to `STORYBOARD.json` (edit) and `STORYBOARD.md`
  (read).
- Edit `STORYBOARD.json` in the Claude Code desktop app (prompt → diff → keep): change a
  beat's `overlay_block`, timing, `overlay_content`, the hook text, `caption_style`, etc.
- **Resume:** re-run the SAME command **without** `--review`. The existing phase-marker
  system (`_phase_done` / `_mark_done`) skips Phases 1–4 and continues from Phase 5 using
  the edited storyboard. To regenerate the storyboard instead, use `--restart-from 4`.
- No new state or work_dir — the gate reuses the resumable pipeline; the only addition is
  the flag and a `_print_review_gate` banner.

---

## Trim settings

**Pacing presets (2026-07-01):** `--pace {tight,natural,relaxed}` (on `video_trim.py`
and `run_video_pipeline.py`, or a manifest `pace` key) nudges pacing without editing code —
`natural` == the tuned defaults below (a no-op), `tight` is snappier, `relaxed` leaves more
air. Fine-grained overrides on `video_trim.py`: `--breath-max`, `--sentence-target`,
`--long-pause-keep`, `--silence-db`. All applied by `apply_pace()` before the trim runs.

| Constant | Value | Effect |
|---|---|---|
| `SILENCE_DB_BELOW_SPEECH` | 22 dB | Adaptive threshold: measured speech level − 22 dB |
| `NATURAL_BREATH_MAX_SEC` | 0.8 s | Pauses ≤ 0.8s are left untouched |
| `SENTENCE_PAUSE_MAX_SEC` | 2.0 s | 0.8–2.0s pauses compressed to 350ms |
| `LONG_PAUSE_MIN_SEC` | 2.0 s | >2.0s pauses compressed to 400ms |
| `RETAKE_PAUSE_MIN_SEC` | 1.5 s | Long pause + ≥38% token overlap → cut earlier take |
| `CROSSFADE_SEC` | 0.03 s | 30ms crossfade between kept segments |

Edit these in `scripts/video_trim.py` top-of-file constants.

---

## Claude model usage

| Task | Model | Why |
|---|---|---|
| Reel script generation | `claude-opus-4-8` | Quality matters — this is what you record |
| Hook selection (reel) | `claude-haiku-4-5-20251001` | Fast, cheap classification |
| Storyboard generation | `claude-opus-4-8` | Complex beat layout, design-spec reasoning |
| Beat composition HTML | `claude-opus-4-8` | Design-rich HTML/GSAP — quality matters (`hf_beat_builder.MODEL_BEAT`) |
| Filler disambiguation | `claude-haiku-4-5-20251001` | Context-aware "so" / "like" decisions |

All calls use `claude -p` CLI subprocess. No Anthropic API key required — uses your Claude subscription.

---

## File locations after pipeline

| Artifact | Path |
|---|---|
| Final long-form MP4 | `assets/video/<week>/<slug>.mp4` |
| Final reel MP4 | `assets/reels_video/<week>/<slug>.mp4` |
| Reel script | `content/reels/<week>/<slug>/reel_script.md` |
| Storyboard | `<work_dir>/storyboard.json` |
| Transcript | `<work_dir>/transcript.json` |
| Beat HTML | `<work_dir>/hf_beats/beat_NN_*/index.html` |
| Beat renders | `<work_dir>/hf_renders/beat_NN_*.mov/.mp4` |

---

## Troubleshooting

**"hyperframes not found in PATH"**
```bash
npm install -g hyperframes
# verify
hyperframes --version
```

**"claude CLI not found"**
The pipeline expects `/Users/tarungupta/.local/bin/claude`. Log in once:
```bash
claude login
```

**Phase failed, want to re-run from storyboard:**
```bash
python3 v1/scripts/run_video_pipeline.py --raw ... --manifest ... --restart-from 4
```

**Beat composition looks wrong:**
Edit the prompt in `scripts/lib/hf_beat_builder.py:_compose_prompt()`, then clear the beat cache:
```bash
rm -rf v1/.hf_beat_cache/
```

**Silence detection not working well:**
Check the measured speech level in `<work_dir>/debug/trim_debug.json → measured_speech_level_dbs`.
If it's too high or low, adjust `SILENCE_DB_BELOW_SPEECH` in `scripts/video_trim.py`.
