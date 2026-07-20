---
title: "Pipeline Polish Plan — HyperFrames + Remotion"
type: doc
slug: implementation-plan
tags: [content/doc]
---
# Pipeline Polish Plan — HyperFrames + Remotion

> Created 2026-07-01. Goal: raise the quality of the V2 video output (long-form + reels)
> across four axes — **captions, pacing, B-roll, overlay/motion** — and add a **human
> review gate** so each video can be steered before final render ("better defaults +
> review gate"). Plan-first per Antigravity Mode C. **No code touched yet — approve before execute.**

---

## Evidence (sampled reel: `assets/reels_video/2026-W25/…ai-prompt-anatomy-travel.mp4`)

Four frames pulled at ~2s / 9s / 18s / 42s:

| Time | What's on screen | Problem |
|---|---|---|
| 2s (hook) | Raw webcam, nothing else | No hook text/overlay in the 0–3s window — the most important 3 seconds are bare |
| 9s (B-roll) | Eiffel + Louvre **landscape** clips **stacked** into 9:16 | Letterboxed two-clip stack looks amateur; no caption over it |
| 18s (screen-rec) | Full-frame ChatGPT screenshot, tiny text | Unreadable on mobile; no zoom/punch-in or callout on the "role" line the video is about |
| 42s | Raw webcam | No caption |

**Across all four frames: zero burned captions.**

---

## Root-cause map

| Axis | Where it's decided | Root cause found in code |
|---|---|---|
| **Captions** | `hf_beat_builder.build_all_beats` + `hf_templates.build_caption_layer` | `talking_head` beats are skipped (builder line ~553), so captions exist **only** on overlay beats. Plain talking-head stretches — the bulk of a reel — get no caption track. Caption is also per-beat, not a continuous timeline. |
| **Overlay/motion** | `hf_beat_builder._compose_prompt` (Opus, `MODEL_BEAT` line 46) | Prompt hardcodes a **blue/purple DS gradient** (`#3b82f6,#8b5cf6,#06b6d4`) and blue glow as the example for *every* niche → life/poetry get DS-colored graphics. `_load_design_constants` truncates each design bible to **2500 chars** and only 4 sections. `is_reel` is passed but **never used** in the prompt → no reel-specific density/safe-area guidance. |
| **Storyboard choices** | `storyboard_gen.build_storyboard_prompt` (Opus) | One `caption_style` for the whole video (rule 4). No forced hook-overlay beat at 0–3s. `broll_keywords` only emitted for `talking_head` beats in **voiceover** videos (rule 9) → talking-head reels get thin B-roll cueing. "Anatomy/list/comparison" narration isn't mapped to labeled overlay callouts. |
| **B-roll** | `video_utils.overlay_broll` / `fetch_broll` / `plan_insertions` | Landscape clips composited as a stacked montage rather than a single full-bleed 9:16 with a punch-in; placement is even-distribution, not narration-aligned. |
| **Screen recordings** | composite + `detect_code_x_center` | `has_screen_recording` disables panel pan but nothing zooms/punches into the active region → tiny unreadable UI on mobile. |
| **Pacing** | `video_trim.py` constants | Tunable but currently untested against your taste; no preview gate before the cut is committed. |
| **Doc drift** | `docs/guides/v2-pipeline.md` | Model table says beat HTML = Haiku; code says **Opus**. Stale — fix to prevent wrong mental model. |

---

## The plan (phased; quick, visible wins first)

### Phase 0 — Safety + sample harness (no risk)
- Create `v1/sandbox/polish/` with a **copy** of the W25 reel's raw input + its `manifest.json` so every change is validated by re-rendering one known video. Nothing in `assets/` production paths is touched.
- Add a frame-diff helper: extract frames at fixed % and lay old-vs-new side by side after each phase.
- Fix the stale Opus/Haiku line in `v2-pipeline.md` (per UPDATE-GUIDES-ALWAYS).
- `git` checkpoint before each phase; bump `_CACHE_VERSION` when the beat prompt changes so cache doesn't serve stale HTML.

### Phase 1 — Captions (biggest visible win)
- Add a **continuous, word-synced caption track** burned across the *entire* timeline (incl. talking-head stretches), decoupled from beats. Source of truth = `transcript.json` word timings already produced in Phase 2 of the pipeline.
- Suppress the global track only where a beat *is* the text (`NO_CAPTION_BLOCKS`) to avoid double text.
- Caption style pass: mobile-safe bottom margin (clear of UI chrome), larger weight, karaoke-style active-word highlight, 1–2 lines max, per-niche color from the design bible (not hardcoded blue).
- Files: new global burn step in `hyperframes_pipeline.py` (reuse `video_utils.burn_captions`), retire the per-beat-only assumption in `build_caption_layer` usage.

### Phase 2 — Hook + overlay usage
- Storyboard: **force a hook beat** covering 0–3s with a text overlay drawn from the reel script's hook line.
- Teach the storyboard prompt to map "anatomy / list / steps / comparison" narration to **labeled overlay callouts** (e.g. ROLE / TASK / CONSTRAINTS tags on the prompt) instead of leaving a raw screenshot bare.
- Fix `_compose_prompt`: remove the hardcoded blue gradient/glow → inject the **niche palette**; raise the 2500-char design cap (or send the full PALETTE/MOTION sections); actually use `is_reel` to add vertical-safe-area + higher-density guidance.

### Phase 3 — B-roll presentation
- Replace stacked-landscape with a **single full-bleed 9:16** clip + subtle Ken-Burns punch-in; if two clips are needed, hard-cut, don't stack.
- Align insertions to narration (keyword→timestamp) rather than even distribution; keep the caption track on top of B-roll.

### Phase 4 — Screen recordings (DS niche)
- Auto **zoom/punch-in** to the active region (use/extend `detect_code_x_center`) so UI text is legible on a phone; add a highlight/spotlight on the referenced element; keep captions on.

### Phase 5 — Pacing
- Tune `video_trim.py` constants against your taste (breath/sentence/retake thresholds); expose them in the review gate so you can nudge per video.

### Phase R — The review gate (the "control" you asked for)
- Add a `--review` flag: the pipeline **halts after storyboard** (and optionally after first beat render), writes `storyboard.json` + a preview, and waits.
- You open the sandbox in the **Claude Code desktop app**, preview with live reload, edit `storyboard.json` / a beat's `index.html` by prompt, watch the diff, then resume the render. This is the prompt→preview→diff→render loop layered on top of the automated pipeline — defaults do the heavy lifting, you approve/tweak before the final composite.

---

## Verification (each phase)
Re-render the sandbox reel → extract frames at the same timestamps → confirm: captions present on every segment, hook overlay in 0–3s, B-roll full-bleed, screen-rec legible, niche-correct colors. Keep a before/after frame strip per phase. High-stakes changes get a second-pass review before merging back toward production.

## Risks & no-overwrite safety
- All work happens in `v1/sandbox/polish/`; production `scripts/` changes are gated behind the sandbox passing.
- Beat-prompt edits require a `_CACHE_VERSION` bump or a `.hf_beat_cache/` clear, else stale HTML is served.
- `git` checkpoint per phase = one-command rollback.

## Decisions for you
1. Start with **Phase 1 (captions)** — recommended, fastest visible lift — or the **review gate** first so you can steer everything by hand from day one?
2. Caption style: word-by-word karaoke highlight, or clean 1–2 line blocks? (I'll mock both on the sandbox reel.)
3. Any specific reel you consider your "good" reference to calibrate taste against?
