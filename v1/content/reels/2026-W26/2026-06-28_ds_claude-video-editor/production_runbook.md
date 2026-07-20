---
title: "Production Runbook — \"Claude replaced my video editor\" (granular, how-to)"
type: reel
niche: data_science_tech
week: 2026-W26
slug: production-runbook
tags: [content/reel, niche/data_science_tech, week/2026-W26]
---
# Production Runbook — "Claude replaced my video editor" (granular, how-to)

Companion to `reel_brief.md`. This is the **how**, step by step. Times assume macOS (your
binaries: ffmpeg at `/opt/homebrew/bin`, `claude` at `~/.local/bin`, `hyperframes` via npm).
Work in `v1/` for every command.

Total realistic time: **~75–90 min** first time, ~40 min once you've done it once.

---

## PHASE 0 — Environment check (5 min, do once)

Confirm the pipeline's required binaries exist, because Phase 1 preflight hard-fails without them.

```bash
cd "/Users/tarungupta/Making It Big/Claude/content-machine/v1"
which ffmpeg ffprobe claude hyperframes
ffmpeg -version | head -1
```

- If `hyperframes` is missing: `npm ls -g hyperframes` then symlink it where the script looks
  (`/opt/homebrew/bin` or `~/.local/bin`). The script searches those paths (see `HF_BIN` in
  `run_video_pipeline.py`).
- If `claude` is missing from PATH, the script falls back to `~/.local/bin/claude` — make sure
  it's logged in: run `claude` once interactively and confirm it responds.
- Whisper is used in Phase 2 for transcription. Confirm it's installed:
  `python3 -c "import whisper"` (or whatever `video_trim.py` imports). If it errors, install per
  your existing setup before recording.

**Why first:** every later phase assumes these. Catch it now, not at 11pm after recording.

---

## PHASE 1 — Lock the script & set the recording state (10 min)

1. Open `reel_brief.md` → the **ORIGINAL SCRIPT** section. Print it or put it on a second screen.
2. Rewrite each beat in **your** spoken cadence — read it out loud once and cut any word that
   doesn't survive being said. Target **~95–110 words total** (40s at 140–160 wpm).
3. Mark your **3 hardest lines** (usually the hook + the 3-step list). You'll do extra takes on those.
4. Decide the **proof shot** now: you will screen-record your own terminal running *this very
   pipeline*. That clip is beat 3's B-roll. Plan it (see Phase 3).

**How to memorize without sounding scripted:** memorize beat-by-beat, not word-by-word. Say the
*idea* of each beat in one breath. Re-record until it sounds like you're telling a friend.

---

## PHASE 2 — Record the talking head (20–30 min)

### Gear & setup (how, specifically)
- **Camera:** phone, rear lens, 4K 30fps (gives crop room for 9:16). Lock exposure & focus
  (tap-and-hold on your face until "AE/AF Lock").
- **Framing:** vertical isn't required at capture (pipeline crops to 9:16 in Phase 3), but frame
  yourself **center-left** with headroom so the crop keeps your face and leaves room for on-screen
  text top-center. Eyes on the top third.
- **Distance:** ~arm's length plus a bit. Lens at eye level — raise the phone, don't shoot up your chin.
- **Lighting:** face a window or a key light. No window *behind* you. One soft source > overhead.
- **Audio (most important):** record in a soft room (bed/curtains kill echo). Use wired earbuds or
  a lav mic if you have one; phone mic only as last resort. Phase 2 trims silences and fillers —
  clean audio makes that step accurate.

### Recording technique
- **Hook (beat 1):** record it **5 separate times** as standalone clips. Vary energy: one calm,
  one punchy, one with a gesture. You'll pick the winner. First 3s decide everything.
- **Body (beats 2–5):** record in **one continuous take** if you can, pausing ~1s of silence
  between beats (gives the trimmer clean cut points). Mess up a line? Pause, then re-say the whole
  sentence — the trimmer removes retakes and keeps the last clean version.
- **Energy:** ~10% more than feels natural. Flat reads die on Reels.
- Do **2–3 full body takes.** Keep the best.

### Hand-off the file
- AirDrop/transfer to the Mac. Rename and place it exactly where the pipeline expects:

```bash
mkdir -p "/Users/tarungupta/Making It Big/Claude/content-machine/v1/assets/raw"
# move/copy your recording to:
#   assets/raw/2026-06-28_ds_claude-video-editor.mov
```

Use `.mov` or `.mp4`. Keep it under a few GB; 4K is fine.

---

## PHASE 3 — Capture the proof B-roll (15 min) ← your edge

This is what makes your reel honest and un-copyable: **film your screen actually running this pipeline.**

### How to screen-record (macOS)
1. Press **⌘⇧5** → choose **Record Selected Portion** → draw a box around your terminal window.
2. Click **Options → Microphone: None** (you want clean screen video, voice comes from the talking head).
3. Click **Record.**
4. In the terminal, type a real instruction to Claude and let it visibly work — e.g. open the
   Claude desktop app's Code mode, or run a `claude -p` command that edits a clip. Let viewers
   *see* text → action. 8–15 seconds is plenty.
5. **⌘⇧5 → Stop** (or click the stop icon in the menu bar).
6. Save it as:

```bash
# place screen-recordings where you'll find them, e.g.:
#   assets/broll/2026-06-28_claude-editor-screen.mov
mkdir -p "/Users/tarungupta/Making It Big/Claude/content-machine/v1/assets/broll"
```

### Make it mobile-legible
Screen text is tiny on a phone. Either zoom your terminal font to ~18–20pt **before** recording,
or crop/zoom in post. Quick zoom-crop with ffmpeg (focus on the action region):

```bash
ffmpeg -i assets/broll/2026-06-28_claude-editor-screen.mov \
  -vf "crop=in_w/1.6:in_h/1.6:in_w/6:in_h/6,scale=1080:-2" \
  -an assets/broll/2026-06-28_claude-editor-screen_zoom.mp4
```

(Adjust the crop fractions until the command + Claude's output fill the frame.)

> **Honesty guardrail while filming:** only show what's real. It *drives* Remotion from your
> English instructions; setup touches the terminal once. Don't fake an "it did everything alone"
> screen. The real thing is impressive enough.

---

## PHASE 4 — Generate the manifest (5 min)

The pipeline reads a `manifest.json`. Two ways:

### Option A — let the script make it (recommended)
```bash
cd "/Users/tarungupta/Making It Big/Claude/content-machine/v1"
python3 scripts/prepare_reel_script.py \
  --from tool \
  --niche ds \
  --project free_tool_ds \
  --slug 2026-06-28_ds_claude-video-editor
```
This writes `reel_script.md` + `manifest.json` into
`content/reels/2026-W26/2026-06-28_ds_claude-video-editor/`.
Then **overwrite** the generated `reel_script.md` with the polished script from `reel_brief.md`.

### Option B — write the manifest by hand
If you skip the generator, drop this file at
`content/reels/2026-W26/2026-06-28_ds_claude-video-editor/manifest.json`:

```json
{
  "slug": "2026-06-28_ds_claude-video-editor",
  "niche": "ds",
  "format": "reel",
  "content_type": "tool_reel",
  "week": "2026-W26",
  "source": "tool",
  "reel_script": "content/reels/2026-W26/2026-06-28_ds_claude-video-editor/reel_script.md",
  "project_key": "free_tool_ds"
}
```

Required fields the preflight checks: `niche` (must be `ds|life|poetry`), `format`, `slug`.
Everything else is metadata the later phases use for output paths.

---

## PHASE 5 — Run the pipeline (10–20 min, mostly unattended)

```bash
cd "/Users/tarungupta/Making It Big/Claude/content-machine/v1"
python3 scripts/run_video_pipeline.py \
  --raw assets/raw/2026-06-28_ds_claude-video-editor.mov \
  --manifest content/reels/2026-W26/2026-06-28_ds_claude-video-editor/manifest.json
```

### What each phase actually does (so you know what you're watching)
| Phase | Name | What happens | Where output goes |
|---|---|---|---|
| 1 | Preflight | Checks ffmpeg/ffprobe/claude/hyperframes + raw file + manifest fields. Hard-fails on any miss. | console |
| 2 | Trim | Removes silences, retakes, filler words; runs **Whisper** → `transcript.json`. | `_pipeline/trimmed.mp4` + `transcript.json` |
| 3 | Crop | Crops to **portrait 9:16** (reel only). | `_pipeline/cropped.mp4` |
| 4 | Storyboard | **Claude Opus** reads the transcript and writes the beat list (which scene per beat). | `_pipeline/` storyboard JSON |
| 5 | HyperFrames | Builds compositions per beat, renders them, FFmpeg-composites with your video + **burns captions**. | `_pipeline/final.mp4` |
| 6 | Output | Copies final to canonical path + writes metadata JSON. | `assets/reels_video/2026-W26/2026-06-28_ds_claude-video-editor.mp4` |

Work dir: `content/reels/2026-W26/2026-06-28_ds_claude-video-editor/_pipeline/`.

### Getting your screen-recording into beat 3
Phase 5 takes a `has_screen_recording` flag internally. Two ways to use your proof clip:
- **Simplest:** before running, edit your storyboard or the HF step to point beat 3 at
  `assets/broll/2026-06-28_claude-editor-screen_zoom.mp4`. (After Phase 4 runs once, open the
  storyboard JSON in `_pipeline/` and set beat 3's B-roll path, then resume.)
- **Or** insert it manually after the pipeline (Phase 6.5 below). For a first pass, manual is fine.

### Idempotency / fixing a failed phase
Each phase writes `.phase_N_done` in the work dir. Re-running **resumes** from the failure.
To force a redo from a phase (e.g., regenerate the storyboard):
```bash
python3 scripts/run_video_pipeline.py \
  --raw assets/raw/2026-06-28_ds_claude-video-editor.mov \
  --manifest content/reels/2026-W26/2026-06-28_ds_claude-video-editor/manifest.json \
  --restart-from 4
```

### Troubleshooting (most common)
- **Preflight fails on hyperframes** → it's not on PATH. `npm ls -g | grep hyperframes`, then
  symlink to `/opt/homebrew/bin/hyperframes`.
- **Phase 2 "Whisper returned no words"** → audio is too quiet or the mic was off. Re-record audio.
- **Phase 4 stalls** → Opus call; check `claude` is logged in (`claude` interactively once).
- **Crop cuts your head off** → you framed too tight. The crop is center 9:16; reframe with more
  headroom and re-run from Phase 3 (`--restart-from 3`).
- **Captions wrong/misplaced** → they're driven by `transcript.json`; a bad transcript = bad
  captions. Fix audio, redo from Phase 2.

---

## PHASE 6 — Manual finish (15 min)

### 6.1 Watch it muted
85% watch with no sound. If it makes sense muted, captions are doing their job. Check:
hook readable in first 3s, no clip > ~4s, ends on the result (loopable), no dead air.

### 6.2 Splice the proof clip if you didn't in Phase 5
If beat 3 still shows your face instead of the screen-record, overlay/replace it. Quick manual
splice (replace seconds 8–20 of the final with your zoomed screen clip) — easiest in any editor,
or ask Claude Code to do it in Remotion (on-brand). Re-export.

### 6.3 Build the thumbnail / cover
- Pull a sharp frame of your face mid-sentence: `⌘⇧5` frame grab, or
  `ffmpeg -i <final.mp4> -ss 1.5 -frames:v 1 cover.png`.
- Add the thumbnail text from `reel_brief.md`: **"Claude just replaced my video editor 😳"**.
  Big, high-contrast, top third. (Canva pass stays manual per your pipeline.)

---

## PHASE 7 — Publish & arm the funnel (10 min)

- **Reels = Instagram Reels + YouTube Shorts only** (LinkedIn/Twitter excluded for reels).
- **Caption:** paste the full caption from `reel_brief.md` — the steps live in the body
  (caption-IS-product). IG cover = your thumbnail.
- **Comment→DM:** arm your tool for keyword **EDIT**; pin a first comment prompting "Comment EDIT".
- **DM payload:** the formatted setup guide + your repo link, **UTM-tagged** via
  `scripts/lib/utm.py` so `collect_analytics.py` can attribute follows/stars.
- **YouTube Shorts:** put the guide link as the **first line** of the description + pinned comment;
  `#Shorts` in the title.
- Staging/derivatives flow through `load_posts.py` → `scheduler.py` as usual.

### After it's live
- Reply to the first ~20 comments fast (algorithm rewards early engagement).
- Set the tracker **Status = Published** for the matching slug rows.

---

## One-glance command sequence

```bash
cd "/Users/tarungupta/Making It Big/Claude/content-machine/v1"

# 0. check env
which ffmpeg ffprobe claude hyperframes

# 1. (optional) generate script + manifest
python3 scripts/prepare_reel_script.py --from tool --niche ds \
  --project free_tool_ds --slug 2026-06-28_ds_claude-video-editor

# 2. record talking head  -> assets/raw/2026-06-28_ds_claude-video-editor.mov
# 3. screen-record proof  -> assets/broll/2026-06-28_claude-editor-screen.mov  (then zoom-crop)

# 4. run pipeline
python3 scripts/run_video_pipeline.py \
  --raw assets/raw/2026-06-28_ds_claude-video-editor.mov \
  --manifest content/reels/2026-W26/2026-06-28_ds_claude-video-editor/manifest.json

# 5. final lands at: assets/reels_video/2026-W26/2026-06-28_ds_claude-video-editor.mp4
```
