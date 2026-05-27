# Video Production Guide — Record → Polished Long-form

End-to-end pipeline. You record. Scripts do the rest.

## TL;DR

```bash
# 1. Record (front cam, looking at camera). Save to assets/raw/
# 2. Prepare edit plan (transcribe + silence detect + fetch b-roll):
python3 scripts/prepare_remotion_edit.py \
  --raw "assets/raw/life_habits.MOV" \
  --script "content/scripts/2026-05-22_..._yt.md" \
  --niche life \
  --slug life_habits

# 3. Preview in browser:
cd remotion && npx remotion studio
# → select composition, scrub through

# 4. Render final MP4:
npx remotion render LifeHabits --output ../assets/video/edited/life_habits.mp4
```

Output: `assets/video/edited/<slug>.mp4` — animated word-by-word captions + stock b-roll.

---

## One-Time Setup

```bash
pip install openai-whisper
brew install ffmpeg
```

`.env` needs `PEXELS_API_KEY` + `PIXABAY_API_KEY` for stock b-roll.

Remotion (already installed in `remotion/`):
```bash
cd remotion && npm install
```

Verify:
```bash
python3 -c "import whisper; print('ok')"
which ffmpeg
cd remotion && node -e "require('remotion')" && echo ok
```

---

## Recording Guide

### Audio (most critical)

**Mic gain: set -6 dB lower than default.** Current life/poetry files peak at 0 dBFS = clipped. Clipped audio → clap detector dies (safety cap triggers, 0 clap cuts). Target peak: -6 to -3 dBFS. Test before recording.

**Clap technique:** one hard clap, hands clear of mic, then 1.5 s silence before speaking. Detector requires ≥1 s pre-gap + 1.5 s post-settle. Soft taps or back-to-back claps = missed cuts. Clap at start of recording AND before any retake.

**External mic preferred** (Rode VideoMic, lav, or USB desk mic). Camera mic = noise floor + clipping risk.

**Quiet room.** AC off, fridge off. Low noise floor = fewer false-positive cut detections.

### Camera

**Lock exposure + white balance manually.** Auto-exposure mid-take = color grade inconsistency.

**Tripod, static frame.** Talking head centered, eyes upper third. Keep face out of bottom 25% — caption bar sits there.

**Resolution:** 4K 30fps or 1080p 60fps. Match Remotion comp (1920×1080 / 30fps). Frame rate mismatch → stutter.

**Lighting:** soft key + fill (window beside face, not behind). Color grade adds contrast — harsh shadows get crushed.

### Performance

**Pause 1 s between sentences** you might cut. Whisper segments cleanly, captions break at sentence boundaries.

**Full retakes only.** On mistake: stop, clap, restart sentence from the top. Mid-sentence self-edits → awkward caption splice.

**Match script markers.** Say exactly what's in script at `[BROLL:]` / `[SCREEN:]` marker points — pipeline uses script text to search stock footage, not what you actually said.

### DS / Screen content

**One PNG per `[SCREEN:]` marker** → save numbered `01_topic.png`, `02_topic.png` to `assets/script_images/<script-stem>/`. Pipeline copies them as b-roll overlays.

**1920×1080 or higher.** Renderer uses `objectFit: contain` — different aspect ratio = letterbox on black.

### Pre-shoot checklist

| Item | Why |
|---|---|
| Mic gain test — speak loud, peak ≤ −3 dBFS | Clapped audio = no clap detection |
| Tripod locked, exposure locked, WB locked | Consistent color grade |
| Room silent (10 s test recording) | Reduce false clap detections |
| Script open with `[BROLL:]` / `[SCREEN:]` markers | Must match pipeline keywords exactly |
| Clap once hard at start, count 2 s, begin | Clap-sync requires pre/post silence gap |
| Save to `assets/raw/YYYY-MM-DD_niche_slug.MOV` | Pipeline auto-matches slug |

---

## Step-by-Step

### 1. Record

Save: `assets/raw/2026-05-21-life-habits.MOV`

### 2. Run `prepare_remotion_edit.py`

```bash
python3 scripts/prepare_remotion_edit.py \
  --raw "assets/raw/2026-05-21-life-habits.MOV" \
  --script "content/scripts/2026-05-22_..._yt.md" \
  --niche life \
  --slug life_habits
```

What it does:
1. **Whisper transcribe** → word timestamps → `remotion/public/captions/<slug>.json`
2. **Adaptive silence detect** → trims leading/trailing silence only
3. **Multi-clap detect** → scans full video, finds every clap-sync marker, builds `cutSegments` that excise each clap + 2s settle time
4. **Fetch stock b-roll** → parses `[BROLL:]` cues → Pexels + Pixabay → `remotion/public/broll/<slug>/` → uses **all downloaded clips** (not just `[BROLL:]` count), evenly distributed with ±2s jitter
5. **MP4 transcode w/ loudnorm** → `loudnorm=I=-16:TP=-1.5:LRA=11` bakes podcast-standard loudness (-16 LUFS) into the audio track
6. **Write edit plan** → `remotion/public/edit-plans/<slug>.json` (cut segments, b-roll timings, caption file)

Runtime: ~3–8 min per 10 min of raw on M-series Mac (Whisper dominates).

Flags: none needed for standard run. Edit plan JSON is human-editable if timings feel off.

### 3. Preview in Remotion Studio

```bash
cd remotion && npx remotion studio
```

Opens `localhost:3000`. Select composition (`LifeHabits`, `PoetryLove`, etc.).

What you see:
- Camera footage with leading/trailing silence trimmed AND every detected clap region cut out (multi-segment stitch)
- Per-niche color grade: warm peach + soft-light overlay for `life`/`poetry`, cool teal for `ds`; contrast/saturation bumped
- Volume boosted +4 dB on top of loudnorm (Remotion `volume={1.6}` on main camera)
- Stock b-roll at **opacity 1.0** with black background — talking head is fully hidden during cue windows
- Poetry: visible film grain (8% opacity, animated SVG noise) + radial vignette (18%)
- Life: subtle grain (4%) + lighter vignette (10%)
- DS: no grain (clean modern look)
- Animated word-by-word captions with gold highlight on active word (rendered above grain layer for crispness)

To adjust b-roll timing: edit `remotion/public/edit-plans/<slug>.json` → change `brollCues[n].startSec` → Studio hot-reloads.

### 4. Render

```bash
cd remotion
npx remotion render LifeHabits --output ../assets/video/edited/life_habits.mp4
npx remotion render PoetryLove --output ../assets/video/edited/poetry_love.mp4
```

Render time: ~2–5× video duration (headless Chrome, frame-by-frame). 10 min video ≈ 20–50 min render.

---

## Composition IDs (Root.tsx)

| Slug | Composition ID | Niche |
|------|---------------|-------|
| `life_habits` | `LifeHabits` | life |
| `poetry_love` | `PoetryLove` | poetry |

To add a new video: add `prepare_remotion_edit.py` run with new `--slug`, then register composition in `remotion/src/Root.tsx`.

---

## Edit Plan JSON

`remotion/public/edit-plans/<slug>.json` — human-editable:

```json
{
  "slug": "life_habits",
  "niche": "life",
  "rawVideo": "videos/life_habits.mp4",
  "silenceTrimStartSec": 1.5,
  "silenceTrimEndSec": 683.9,
  "cutSegments": [
    { "startSec": 5.2, "endSec": 312.4 },
    { "startSec": 318.1, "endSec": 683.9 }
  ],
  "brollCues": [
    {
      "id": "cue-0",
      "description": "morning light...",
      "startSec": 114.0,
      "durationSec": 5.0,
      "clipFile": "broll/life_habits/cue-0.mp4"
    }
  ],
  "captionsFile": "captions/life_habits.json"
}
```

Adjust `startSec` / `durationSec` per cue → Studio reloads live.

---

## Output Layout

```
assets/
  raw/                          # recorded MOV files go here
    life_habits.MOV
  video/
    edited/                     # FINAL renders
      life_habits.mp4
      poetry_love.mp4

remotion/
  public/
    videos/                     # symlinks → assets/raw/*.MOV
    captions/                   # Caption[] JSON per slug
    broll/<slug>/               # downloaded stock clips
    edit-plans/                 # edit plan JSON per slug
  src/
    compositions/
      TalkingHeadEdit.tsx       # main composition
      CaptionPage.tsx           # word-highlight caption component
    Root.tsx                    # composition registry
```

---

## Per-Niche Notes

### Life & Self-Development
- Talking-head full-frame. B-roll for emotional beats.
- `--niche life` → Pexels searches for lifestyle/nature/growth visuals.

### Poetry / Quotes
- Heavy b-roll (abstract/nature). `[PAUSE]` markers in script — silence detector leaves intentional pauses intact (only trims leading/trailing silence).
- `--niche poetry` → abstract/sky/water/contemplative visuals.

### Data Science / Tech
- Talking-head for context; screen-record code sections separately.
- Composite talking-head + screen-record in Remotion or DaVinci manually.
- `--niche ds` → code/data/tech visuals for non-screen b-roll.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `whisper` import error | `pip install openai-whisper` |
| `ffmpeg: command not found` | `brew install ffmpeg` |
| Pexels/Pixabay 0 results | Shorten `[BROLL:]` cue text to 3–5 words |
| B-roll timing off | Edit `edit-plans/<slug>.json` `startSec` values → Studio reloads |
| Captions out of sync | Re-run `prepare_remotion_edit.py` with `--whisper-model small` for better accuracy |
| Remotion Studio blank | Edit plan JSON missing — run `prepare_remotion_edit.py` first |
| Render OOM | Close other apps; Remotion renders frame-by-frame in Chrome |
| New video not in Studio | Register composition in `remotion/src/Root.tsx` |
| Audio still quiet | Delete `remotion/public/videos/<slug>.mp4` and rerun prepare script — loudnorm only bakes on first transcode |
| Claps still audible | Inspect `cutSegments` in plan JSON — if only 1 segment, tune `CLAP_PEAK_OFFSET_DB` (lower = stricter) or `CLAP_MAX_DURATION` in `prepare_remotion_edit.py` |
| Want more/less grain | Edit `FilmGrainOverlay` in `remotion/src/compositions/TalkingHeadEdit.tsx` — change `grainOpacity` / `vignetteOpacity` per niche |
| Color tint wrong | Edit `gradingFor(niche)` in same file — `filter` string + `overlayColor` |

---

## What This Does NOT Do (Yet)

- ❌ Jump-cut silence removal mid-video (trims leading/trailing only — but multi-clap regions ARE cut)
- ❌ Face-tracking crop for shorts
- ❌ Intro/outro template
- ❌ Auto-upload (use `upload_youtube.py` separately)
- ❌ Shorts generation from Remotion render (use `clip_shorts.py` on output MP4)

---

## Legacy: `auto_edit.py`

Previous ffmpeg-based pipeline still works as fallback:

```bash
python3 scripts/auto_edit.py \
  --raw assets/raw/<slug>.MOV \
  --script content/scripts/<slug>_yt.md \
  --niche life \
  --slug <slug>
```

Faster to render (ffmpeg, not Chrome). Captions are static SRT burn (not animated). Use when Remotion render time is a bottleneck.
