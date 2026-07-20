---
title: "NEXT STEPS — test the polished pipeline on the *ai-prompt-anatomy-travel* reel"
type: doc
slug: next-steps-2026-07-01
tags: [content/doc]
---
# NEXT STEPS — test the polished pipeline on the *ai-prompt-anatomy-travel* reel

Everything from the polish session is in this repo, **uncommitted**. This file is
copy‑paste ready: run the blocks from the **repo root** (`content-machine/`), or paste
the "Ask Claude Code" prompts straight into Claude Code.

Slug used below: `2026-06-16_data_science_tech_ai-prompt-anatomy-travel`

---

## 0. One‑time prerequisites

Ask Claude Code:

> Check that Node 22+, FFmpeg, Whisper (`whisper` or `faster-whisper`), the `claude` CLI
> (logged in), and Python Pillow are installed. Install anything missing for macOS.

---

## 1. Fastest end‑to‑end test — runs NOW, no raw recording needed

This re‑runs the **existing reel** through the improved pipeline in `--pre-edited` mode
(skips silence/retake trimming, transcribes it, then storyboard → hook → overlays → gold
captions). A `_v2test` slug is used so it never overwrites your original.

**Step A — build + pause at the storyboard.** Ask Claude Code:

> From the repo root, run this and then show me the storyboard summary it prints and open
> the STORYBOARD.json it points to:
>
> ```bash
> python3 v1/scripts/run_video_pipeline.py \
>   --raw "v1/assets/reels_video/2026-W25/2026-06-16_data_science_tech_ai-prompt-anatomy-travel.mp4" \
>   --niche ds --format reel \
>   --slug "2026-06-16_data_science_tech_ai-prompt-anatomy-travel_v2test" \
>   --pre-edited --review
> ```

**Step B — render.** Once the storyboard looks right (edit STORYBOARD.json if you want),
re‑run the **exact same command without `--review`**:

```bash
python3 v1/scripts/run_video_pipeline.py \
  --raw "v1/assets/reels_video/2026-W25/2026-06-16_data_science_tech_ai-prompt-anatomy-travel.mp4" \
  --niche ds --format reel \
  --slug "2026-06-16_data_science_tech_ai-prompt-anatomy-travel_v2test" \
  --pre-edited
```

**Output:** `v1/assets/reels_video/2026-W25/2026-06-16_data_science_tech_ai-prompt-anatomy-travel_v2test.mp4`

> Note: `--pre-edited` skips the trim step, so this test does **not** exercise pacing
> (`--pace`). It's the quickest way to see captions + hook + overlays on the real footage.

---

## 2. The real end‑to‑end (only if you still have the original raw recording)

This is the true test (trim → storyboard → beats → render) and exercises pacing too.

```bash
# a) generate the reel script + manifest from the blog (prints the manifest path)
python3 v1/scripts/prepare_reel_script.py \
  --from "v1/content/blogs/2026-W25/2026-06-16_data_science_tech_ai-prompt-anatomy-travel.md" \
  --niche ds --week 2026-W25 \
  --slug "2026-06-16_data_science_tech_ai-prompt-anatomy-travel"

# b) run the full pipeline on your raw file, pausing at the storyboard
python3 v1/scripts/run_video_pipeline.py \
  --raw "<PATH_TO_YOUR_RAW_RECORDING.mov>" \
  --manifest "<MANIFEST_PATH_FROM_STEP_A>" \
  --review --pace natural

# c) resume: same command without --review
```

Try `--pace tight` for a snappier cut or `--pace relaxed` for more breathing room.

---

## 3. What to check in the rendered video

- **Captions:** gold word‑by‑word captions across the WHOLE clip (talking‑head included),
  nothing running off the edges.
- **Hook:** a punchy text overlay in the first 0–3s — not a bare face.
- **Overlays:** actually present through the reel (the old bug stripped them to plain
  talking‑head after 40%).
- **Colors:** DS blue/cyan accents, not leaking odd colors.

---

## 4. If something's off — toggles (no code archaeology needed)

- **Turn the new captions off:** `run_hf_pipeline(..., burn_global_captions=False)` in
  `v1/scripts/hyperframes_pipeline.py`.
- **Change caption color:** `NICHE_ACCENT` in `v1/scripts/lib/caption_track.py`.
- **Disable forced hook:** `parse_storyboard_response(..., force_hook=False)` in
  `v1/scripts/lib/storyboard_gen.py`.
- **Pacing:** drop `--pace` for the tuned defaults.
- **Revert anything:** it's all uncommitted — `git diff` shows every change,
  `git checkout -- <file>` reverts one file.

---

## 5. Voiceover lane (life niche) — separate test for the B‑roll montage

The Ken Burns montage renderer is wired into `run_voiceover_week.py`. Test it on a
voiceover piece (needs a voiceover audio + fetched B‑roll):

```bash
python3 v1/scripts/run_voiceover_week.py --week <WEEK> --slug <VOICEOVER_SLUG> --audio "<voiceover.wav>" ...
```

It now renders the full‑bleed + Ken Burns + crossfade montage via ffmpeg (the Remotion
`VoiceoverEdit` composition it used to call isn't in the repo). Overlay *scenes* aren't
reproduced; captions still burn via hyperframes.

---

## 6. Commit when you're happy

```bash
git add -A
git commit -m "polish: captions, hook/overlays, review gate, b-roll montage, screen-zoom, pacing"
```

Changed/added files: `lib/caption_track.py`, `lib/broll_montage.py`, `lib/screen_zoom.py`
(new); `hyperframes_pipeline.py`, `lib/hf_beat_builder.py`, `lib/storyboard_gen.py`,
`run_video_pipeline.py`, `run_voiceover_week.py`, `video_trim.py` (edited); plus docs in
`v1/docs/guides/` and `v1/docs/implementation_plan.md`.
