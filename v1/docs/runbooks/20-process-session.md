---
title: "Runbook 20 — Process a Recorded Session (tier: Sonnet)"
type: doc
slug: 20-process-session
tags: [content/doc]
---
# Runbook 20 — Process a Recorded Session (tier: Sonnet)

Input: a green-screen recording in `assets/raw/inbox/` (batch sitting or ad-hoc).
Output: per-question clips → composited → trimmed → reels + episode, all in
`output/review/{week}/` for human approval. NOTHING publishes from this runbook.

Read the `video-edit-playbook` skill BEFORE any trim/render step (hard rule).

## Steps

### 1. Slice the session into per-question clips
```bash
python3 scripts/slice_raw_session.py --input "assets/raw/inbox/<file>" --week <YYYY-Wnn>
```
Dry-run first if unsure: add `--dry-run`.
**Success:** `content/sessions/{week}/clips/qNN.mp4` files + `session_manifest.json`.
Check `unmatched_questions` in the manifest — unmatched = not recorded or spoken
too differently; note them in STATUS, do not fabricate clips.

### 2. Composite over the niche studio background
Per clip (niche comes from the prompt pack entry for that qid):
```bash
python3 scripts/composite_greenscreen.py --input "content/sessions/{week}/clips/q01.mp4" --niche life
```
Key params are cached per background after first calibration. `--recalibrate`
only if lighting changed. `--prores` only when the human asked for a Palmier
editable finish.
**Success:** script prints alpha-gate line and `streams: audio+video`. If
calibration fails to converge → run the `/greenscreen-composite` command
interactively (its gates diagnose lighting/spill) — do not hand-guess params.

### 3. Trim each composited clip
```bash
python3 scripts/video_trim.py --raw "content/sessions/{week}/clips/q01_composited.mp4" --niche <niche> \
    --out "content/sessions/{week}/clips/q01_composited_trimmed.mp4"
```
**Success:** trimmed file plays, transcript.json alongside, duration shrank.

### 4. Reels — pick 3–4 clips
Selection rule (machine-scored, you only apply it): prefer clips whose questions
came from `raw_take_bank` themes that match last week's winners; break ties by
shorter duration. 3 reels minimum, 4 if the session was strong.
Per selected clip, portrait crop + captions via the existing pipeline:
```bash
python3 scripts/run_video_pipeline.py --raw "<trimmed clip>" --manifest "<reel manifest>" --restart-from 3
```
(Manifest per `prepare_reel_script.py`; the spoken question is the hook — do not
re-hook.) Captions: `embedded-captions` skill, `anchor` identity, English.
**Success per reel:** MP4 in `output/review/{week}/reels/`, ffprobe shows
video+audio, captions visible at 2 spot-check frames, ≤60s.

### 5. Episode
```bash
python3 scripts/assemble_episode.py --week <YYYY-Wnn> --niche <niche>
```
**Success:** `output/review/{week}/episode_{niche}.mp4` + `_meta.md` with title
options and chapters. Chapters must land on question starts (spot-check 2).

### 6. Thumbnails
```bash
python3 scripts/generate_thumbnail.py --face auto ...   # once --face auto ships
```
Until then: HTML/Playwright pipeline with the best available face photo. One
thumbnail per reel + episode into `output/review/{week}/thumbnails/`.

### 7. Status + handoff
Append to `output/review/{week}/STATUS.md`; end with the one-line human summary:
`ready for review: 1 episode (life, 14:32), 3 reels, 4 thumbnails; q05 unmatched`.

## STOP if
- Slicer matches <50% of pack questions → recording protocol drifted; tell human
  to check the "read question aloud" rule; do NOT lower `--min-score` below 0.6.
- Any render missing audio stream → mux per video-edit-playbook, re-verify.
- Scene validation errors → `scene-validation-autofix` skill, standard fixes only.
- Two failures on the same step → `50-recovery.md`.
