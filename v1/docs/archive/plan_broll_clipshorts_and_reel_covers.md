# Plan: Emotional B-roll Clip-Shorts (3rd reel type) + Custom Reel Covers

## Context

The short-form pipeline today has two reel kinds, both routed through `shorts_manifest.json` slots:
- **`clip`** — camera footage cut from long-form, rendered by Remotion `ShortClip.tsx`.
- **`motion`** — pure Remotion motion-graphics reels, rendered by `{DS,Life,Poetry}MotionShort`.

The creator wants:
1. **A 3rd kind**: a clip-short that keeps the camera + original audio but **cuts away to emotional stock b-roll at chosen moments** (to invoke more emotion). Confirmed via clarifying question: *keep the camera clip, overlay b-roll at cue points* — NOT a voiceover-only stock reel.
2. **A custom-generated cover image for every reel, regardless of type**, built with **Remotion still** (confirmed choice).

Key reuse facts found during exploration:
- `ShortClip.tsx` already loads an `EditPlan` (which has a `brollCues` field) but **never renders b-roll**. `TalkingHeadEdit.tsx:327-355` already renders `plan.brollCues` (image/video, muted, frame-mapped). The cutaway logic exists — it just needs porting into `ShortClip` with clip-local frame translation.
- `BrollCue` type already exists in `remotion/src/types.ts`.
- `scripts/fetch_videos.py` exposes reusable `fetch_pexels_videos()`, `fetch_pixabay_videos()`, `download_video()`.
- `scripts/lib/video_utils.py` has `overlay_broll()` (ffmpeg cutaway) for the standalone `clip_shorts.py` path.
- `remotion/src/compositions/Thumbnail.tsx` (1280×720, niche accent/grid/glow, registered as a still in `Root.tsx:263`) is the template to fork for a vertical cover.
- `render_shorts_batch.py:163-169` already derives a motion short's hook text (first scene `script`) for captions — the same source feeds covers.
- No `renderStill` / `npx remotion still` usage exists yet; covers add the first.

---

## Feature A — Emotional b-roll clip-shorts

New manifest slot type **`clip_broll`** that renders the existing camera clip with emotional stock-b-roll cutaways. Existing `clip` slots are untouched (no behavior change for current shorts).

### A1. Render layer — `remotion/src/compositions/ShortClip.tsx`
- Add optional prop `brollCuesFile?: string` to `ShortClipProps`.
- On load, if `brollCuesFile` set, `fetch(staticFile(brollCuesFile))` → `BrollCue[]`; else fall back to `plan.brollCues`.
- Render cues whose `startSec ∈ [clipStartSec, clipEndSec]`, mapped to **clip-local frames**: `from = floor((cue.startSec − clipStartSec) * fps)`, `durationInFrames = ceil(cue.durationSec * fps)` (mirror the existing caption mapping already in this file at lines 112-138, and the media render block from `TalkingHeadEdit.tsx:340-354` — `Img` for image ext, muted `OffthreadVideo` else, `objectFit:"cover"`). Camera audio keeps playing underneath (b-roll is muted), so original audio is retained as required.
- Default behavior with no cues file and empty `plan.brollCues` = identical to today.

### A2. Cue generator — new `scripts/generate_clip_broll.py`
- Args: `--slug`, `--niche`, optional `--count` (cutaways per clip), `--project`, `--week`.
- Reuse: `lib.virality.virality_block("clip_select", niche, project_key)`, `lib.claude_cli.call_claude`, `lib.niche_config.model_for`, `data/kb/viral_reel_formula.md` + voice/reels KB for emotional framing.
- Read the clip window(s) from the slug's `shorts_manifest.json` clip slots (or `assets/video/edited/shorts/{slug}_shorts_manifest.json` from `clip_shorts.py`) + the SRT transcript.
- Prompt Claude for 2-4 **emotional cutaway moments** per clip: each returns `{atSec, durationSec, emotion, search_term}` grounded in the transcript and the niche's emotional register (poetry/life lean feel-seen; DS lean proof/contrast).
- For each moment: `fetch_pexels_videos(search_term)` → `download_video()` into `remotion/public/broll/{week}/{slug}/clip_broll/cue-N.mp4` (Pixabay fallback).
- Write a `BrollCue[]` file per slot: `remotion/public/broll-plans/{week}/{slug}_s{NN}_broll.json` (relative `clipFile` paths under `public/`).

### A3. Manifest + batch routing
- `scripts/generate_shorts_manifest.py`: allow emitting `clip_broll` slots (carry `editPlanFile`, `clipStartSec`, `clipEndSec`, `brollCuesFile`, `coverHook`). Keep `motion` default; `clip_broll` opt-in.
- `scripts/render_shorts_batch.py`: route `slot["type"] == "clip_broll"` → `ShortClip` with `props={editPlanFile, clipStartSec, clipEndSec, brollCuesFile}`. Treat it like `clip` for the captions pass.
- **Standalone ffmpeg path (secondary):** add `--broll` to `scripts/clip_shorts.py` that, after `crop_vertical`, overlays the generated cues via existing `overlay_broll()`. Consumes the same `*_broll.json`. Lower priority than the Remotion path.

---

## Feature B — Custom reel covers (all 3 types, Remotion still)

### B1. Cover composition — new `remotion/src/compositions/ReelCover.tsx`
- Fork `Thumbnail.tsx` to **1080×1920** vertical: large hook headline (top-center), niche accent bar + grid + glow from `styles/chronixel` (`nicheAccent/nicheGlow/nicheGrid/nicheShowName`), brand lockup bottom. Props: `{ hookText: string; subText?: string; niche: Niche; variant?: "a"|"b"|"c" }`.
- Register in `remotion/src/Root.tsx` beside Thumbnail: `<Composition id="ReelCover" component={ReelCover} width={1080} height={1920} durationInFrames={1} fps={FPS} defaultProps={{ hookText: "Preview", niche: "ds" }} />`.

### B2. Cover generator — new `scripts/generate_reel_covers.py`
- Args: `--week`, `--niche`, optional `--slug`, `--force`.
- Uniform **hook-text-per-slot** helper `cover_hook_for_slot(slot, week)`:
  - `motion` → first scene `script` from `scenePlanFile` (reuse logic at `render_shorts_batch.py:163-169`).
  - `clip` / `clip_broll` → `slot["coverHook"]` if present, else first caption page text from `EditPlan.captionsFile`, else slug words.
- For each slot run: `npx remotion still ReelCover --props '{...}' output/animations/{week}/{slug}_s{NN}_cover.png` (subprocess from `remotion/`, mirror `render_shorts_batch.render_slot`).

### B3. Pipeline integration
- `render_shorts_batch.py`: after renders complete, call the cover step per slot unless `--no-covers`. `clip_shorts.py` already has `hook_line` per output → write `coverHook` into its manifest and emit a cover too.

---

## Files

**Modify:** `remotion/src/compositions/ShortClip.tsx`, `remotion/src/Root.tsx`, `scripts/render_shorts_batch.py`, `scripts/generate_shorts_manifest.py`, `scripts/clip_shorts.py`
**New:** `remotion/src/compositions/ReelCover.tsx`, `scripts/generate_clip_broll.py`, `scripts/generate_reel_covers.py`
**Reuse (no change):** `remotion/src/types.ts` (`BrollCue`), `scripts/fetch_videos.py`, `scripts/lib/video_utils.py` (`overlay_broll`), `scripts/lib/virality.py`, `scripts/lib/claude_cli.py`, `scripts/lib/niche_config.py`, `data/kb/viral_reel_formula.md`

## Docs (CLAUDE.md mandate — update before finishing)
- `docs/video-production-guide.md` — document the 3rd reel type + cover step.
- Relevant day guide (shorts render day) — new commands.
- `docs/weekly-operating-guide.md` setup — `generate_clip_broll.py`, `generate_reel_covers.py`.
- Run `graphify update .` after code changes.

## Verification
1. **TS compiles + composition registered:** `cd remotion && npx tsc --noEmit` ; `npx remotion compositions` lists `ReelCover`.
2. **Cover still (fast, no external API):** `python3 scripts/generate_reel_covers.py --week 2026-W24 --niche life` → PNGs exactly 1080×1920 in `output/animations/2026-W24/`. Open and eyeball hook text + branding.
3. **Emotional cues:** `python3 scripts/generate_clip_broll.py --slug <real_slug> --niche life --week 2026-W24` → `*_broll.json` written + clips downloaded under `remotion/public/broll/.../clip_broll/`.
4. **Render 3rd type:** set a `clip_broll` slot in that slug's `shorts_manifest.json`, then `python3 scripts/render_shorts_batch.py --week 2026-W24 --niche life --dry-run`, then real. Confirm output MP4 shows camera + b-roll cutaways at cue times with original audio continuing.
5. **No regression:** an existing `clip` slot (no `brollCuesFile`) renders identically to before.
