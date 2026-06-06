# Video Production Guide — Record → Manual Edit → Publish

Record talking head. Prepare transcription + b-roll. Edit manually in DaVinci.

## TL;DR

```bash
# 1. Record (front cam, looking at camera). Save to assets/raw/
# 2. Prepare edit metadata (transcribe + silence detect + fetch b-roll):
python3 scripts/prepare_remotion_edit.py \
  --raw "assets/raw/life_habits.MOV" \
  --script "content/scripts/2026-05-22_..._yt.md" \
  --niche life \
  --slug life_habits

# 2b. Generate Remotion animation prompts for [ANIMATION:] tags in script:
python3 scripts/generate_animation_prompts.py "content/scripts/2026-05-22_..._yt.md"
# → content/prompts/{slug}_animation_prompts.txt  (one prompt per tag, feed to Claude)

# 2b (alt). Render animations directly to MP4 (uses built-in brand templates):
python3 scripts/generate_animation_prompts.py "content/scripts/2026-05-22_..._yt.md" --render
# → output/animations/{slug}_{n}_{type}.mp4  (one MP4 per animation tag)

# 3. Edit manually in DaVinci:
# - Trim silence (reference: prepare script output)
# - Overlay b-roll from assets/videos/life_habits/
# - Color grade per niche (see niche notes below)
# - Export to assets/video/edited/life_habits.mp4

# 4. Generate shorts from final MP4:
python3 scripts/clip_shorts.py --slug life_habits --count 4
```

Output: `assets/video/edited/<slug>.mp4` edited manually with captions + stock b-roll.

---

## One-Time Setup

```bash
pip install openai-whisper
brew install ffmpeg
```

`.env` needs `PEXELS_API_KEY` + `PIXABAY_API_KEY` for stock b-roll.

DaVinci (download from blackmagicdesign.com). Free version sufficient for manual editing.

Verify:
```bash
python3 -c "import whisper; print('ok')"
which ffmpeg
which davinci  # or open DaVinci app
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

### 1b. Generate animation prompts (optional, for scripts with `[ANIMATION:]` tags)

```bash
python3 scripts/generate_animation_prompts.py \
  "content/scripts/2026-05-21-data-science-tech-{slug}_yt.md"
```

Output: `content/prompts/{slug}_animation_prompts.txt`. Each block is a complete Remotion component spec (frame ranges, spring physics, brand colors, required props). Feed each block to Claude → get a `.tsx` file → drop into `remotion/src/compositions/`.

**Or render MP4s directly** using built-in brand templates (no manual TSX step):

```bash
python3 scripts/generate_animation_prompts.py \
  "content/scripts/2026-05-21-data-science-tech-{slug}_yt.md" \
  --render
```

Output: `output/animations/{slug}_{n}_{type}.mp4`. Writes temp TSX components to `remotion/src/compositions/animations/`, renders via `npx remotion render`, then cleans up.

Classifies tag type automatically: `title_card`, `outro_card`, `lower_third`, `transition`, `generic`.

---

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

**Cut punch-in:** the `TalkingHeadEdit` composition applies a subtle scale punch-in
(~3.5% over ~0.23s, easing out) at every cut point after the first segment, so clap
cuts read as intentional human edits instead of jarring jump-cuts. Tunable via
`CUT_PUNCH_SCALE` / `CUT_PUNCH_FRAMES` in `remotion/src/compositions/TalkingHeadEdit.tsx`.

Flags:

| Flag | Default | Description |
|------|---------|-------------|
| `--subtitles` | off | Burn animated word-by-word captions into the render |

Add `--subtitles` to burn in captions. Omit for a clean render (e.g. when platform adds its own captions, or you'll add SRT separately).

### 3. Manual Edit in DaVinci

Open DaVinci → import `assets/raw/<slug>.MOV`.

Reference these prepare script outputs:
- **Silence trim:** See `remotion/public/edit-plans/<slug>.json` → `silenceTrimStartSec` / `silenceTrimEndSec`
- **Cut segments (claps):** See `cutSegments` array in same JSON for exact frame boundaries to remove
- **B-roll clips:** Stored in `assets/videos/<slug>/` — use `remotion/public/edit-plans/<slug>.json` → `brollCues` for timing + descriptions
- **Captions JSON:** `remotion/public/captions/<slug>.json` has word-level timestamps (Whisper output) if you want to burn captions

Editing checklist:
- Trim leading/trailing silence
- Cut out clap sync markers + 2s settle time (per `cutSegments`)
- Layer stock b-roll from `assets/videos/<slug>/` per `brollCues` timings
- Color grade (see niche specs below)
- Mix volume (-16 LUFS target, ~-4dB boost on talking head)
- Export to `assets/video/edited/<slug>.mp4`

---

## Edit Plan Reference

`prepare_remotion_edit.py` outputs to `remotion/public/edit-plans/<slug>.json`:

```json
{
  "slug": "life_habits",
  "silenceTrimStartSec": 1.5,
  "silenceTrimEndSec": 683.9,
  "cutSegments": [
    { "startSec": 5.2, "endSec": 7.2 },
    { "startSec": 318.1, "endSec": 320.1 }
  ],
  "brollCues": [
    {
      "id": "cue-0",
      "description": "morning light through window",
      "startSec": 114.0,
      "durationSec": 5.0,
      "clipFile": "cue-0.mp4"
    }
  ],
  "captionsFile": "captions/life_habits.json"
}
```

Use `cutSegments` frame boundaries to align clap cuts in DaVinci. Use `brollCues` timing + descriptions to layer stock footage.

---

## Per-Niche Notes

### Life & Self-Development
- Talking-head full-frame. B-roll for emotional beats + Remotion animation overlays.
- `--niche life` → Pexels searches for lifestyle/nature/growth visuals.
- Script contains `[BROLL:]` cues (stock clips) + `[ANIMATION:]` markers (Remotion overlays):
  - `[ANIMATION: 3-second title card — "Episode Title"]` — before first word
  - `[ANIMATION: 3-second lower third — "Core insight ≤8 words"]` — at 1–2 key moments mid-script
  - `[ANIMATION: 5-second outro card — "Next: tease"]` — after final word
- Render animations Friday (Step 2b) → `output/animations/[slug]_*.mp4` → layer in DaVinci as overlay tracks
- **Brand auto-detected** from `SHOW: Breath of Life` in script header → warm amber (`#d4885a`) + Georgia font. No flag needed.

### Poetry / Quotes
- Heavy b-roll (abstract/nature) + Remotion animation overlays. `[PAUSE]` markers in script — silence detector leaves intentional pauses intact (only trims leading/trailing silence).
- `--niche poetry` → abstract/sky/water/contemplative visuals.
- Script contains `[BROLL:]` cues + `[ANIMATION:]` markers:
  - `[ANIMATION: 3-second title card — "Poem Title"]` — before first word
  - `[ANIMATION: 3-second lower third — "key stanza line"]` — at 1–2 key poem moments
  - `[ANIMATION: 5-second outro card — "Next: tease"]` — after final word
- Render animations Friday (Step 2b) → `output/animations/[slug]_*.mp4` → layer in DaVinci as overlay tracks
- **Brand auto-detected** from `SHOW: Breath of Poetry` in script header → violet (`#a78bfa`) + Georgia font. No flag needed.

### Data Science / Tech
- Talking-head for context; screen-record code sections separately.
- Composite talking-head + screen-record in DaVinci manually.
- `--niche ds` → code/data/tech visuals for non-screen b-roll.
- After editing, HyperFrames works well for DS: code snippets, bar charts, stat cards, flowcharts auto-placed per transcript.
- **Brand auto-detected** from `SHOW: Breath of Data Science` in script header → blue (`#58a6ff`) + JetBrains Mono font.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `whisper` import error | `pip install openai-whisper` |
| `ffmpeg: command not found` | `brew install ffmpeg` |
| Pexels/Pixabay 0 results | Shorten `[BROLL:]` cue text to 3–5 words |
| Captions out of sync | Re-run `prepare_remotion_edit.py` with `--whisper-model small` for better accuracy |
| B-roll timing reference missing | Ensure `remotion/public/edit-plans/<slug>.json` + `brollCues` exist before editing |
| Claps not clear in JSON | Inspect `cutSegments` in plan JSON — if timestamps seem wrong, tune `CLAP_PEAK_OFFSET_DB` or `CLAP_MAX_DURATION` in `prepare_remotion_edit.py` |
| DaVinci missing b-roll clips | Check `assets/videos/<slug>/` — run `prepare_remotion_edit.py` if empty |
| Audio levels too low | Use loudnorm in DaVinci: `loudnorm=I=-16:TP=-1.5:LRA=11` filter or manual level boost +4dB |

---

## What This Does NOT Do (Yet)

`prepare_remotion_edit.py` handles transcription, silence trimming, and b-roll prep only. Manual editing in DaVinci handles:
- ❌ Color grading
- ❌ Caption burning (use captions JSON for reference, burn in DaVinci)
- ❌ Intro/outro templates
- ❌ Auto-upload (use `upload_youtube.py` separately)

Shorts are generated via `clip_shorts.py` on the final MP4.

---

## HyperFrames: Automated Visual Augmentation

Post-production layer runs on **every edited MP4** after manual DaVinci editing. Claude analyzes transcript, picks element types, generates + renders augmented version automatically.

### What it does

1. Extracts audio → Whisper word timestamps
2. Groups words into smart caption lines (pause/punctuation detection)
3. Claude analyzes transcript → picks 4–7 elements with timing, position, content
4. Generates HyperFrames HTML with cinematic captions + overlays
5. Renders to MP4 via headless Chrome + FFmpeg

### Prerequisites (one-time)

```bash
pip install openai-whisper
node --version   # must be 22+
ffmpeg --version # must be installed
```

### Usage

```bash
# Full pipeline — analyze + render (default intensity: light)
python3 scripts/hyperframes_render.py assets/video/edited/<slug>.mp4

# Control overlay density (default light). minimal/light = human-editor restraint;
# dense = legacy maximal coverage. Use minimal for courses/teaching content.
python3 scripts/hyperframes_render.py assets/video/edited/<slug>.mp4 --intensity minimal

# Clip to first N seconds
python3 scripts/hyperframes_render.py assets/video/edited/<slug>.mp4 --duration 60

# Generate HTML only — inspect/tweak before rendering
python3 scripts/hyperframes_render.py assets/video/edited/<slug>.mp4 --no-render
cd /tmp/hf_<slug> && npm run render

# Process ALL shorts for a slug in one command
python3 scripts/hyperframes_render.py --shorts --slug 2026-05-25_data_science_tech_python-for-data-science-tutorial-210
# → finds assets/video/edited/shorts/<slug>_short_*.mp4 and runs the full pipeline on each

# Force-rebuild cache (use when shorts get re-exported with same filename)
python3 scripts/hyperframes_render.py --shorts --slug <slug> --fresh

# All options
python3 scripts/hyperframes_render.py <video> [--slug name] [--duration N]
                                               [--model tiny|base|small|medium]
                                               [--intensity minimal|light|standard|dense]
                                               [--no-render] [--output-dir path]
                                               [--shorts] [--shorts-dir path]
                                               [--fresh]
```

**Intensity (overlay density):** `--intensity` defaults to `light`. `minimal`/`light` give
human-editor restraint — sparse overlays on genuine high-value beats, calm slide/fade motion.
`standard` is moderate; `dense` is the legacy maximal look (overlay every ~12–15s, bouncy
motion) — usually too much for teaching content. Verified on a 3-min sample: `minimal` → ~1
overlay/min, no overshoot anims; `dense` → ~1/13s. Elements cache per-slug, so **pass `--fresh`
after changing `--intensity`** or the prior run's elements are reused.

**Cache behavior:** Project cached at `/tmp/hf_<slug>/`. Auto-invalidates when input video mtime is newer than `assets/clip.mp4`. Use `--fresh` to force wipe (e.g. when filename unchanged but content swapped).

**Render quality (2026-06-04):** Pipeline now emits higher-fidelity MP4s:
- Source re-encode: `libx264 -preset medium -crf 17 -profile:v high`, rec.709 color tags, AAC 192k/48kHz audio (was `-preset fast -crf 18`, default AAC).
- Final HyperFrames render: invokes `hyperframes render` directly with `--quality high --crf 16 --fps 30 --browser-gpu` (was bare `npm run render` at default quality).
- Overlay CSS: real `backdrop-filter: blur(14px)` on glass cards, depth shadow, font-smoothing on all text, softer vignette (38%/0.62), crisper caption shadow, `object-fit: cover` on background video so off-aspect inputs no longer squash.
- Cost: ~30% longer render time; visibly sharper text, fuller voice, no color drift in downstream tools.

Output: `assets/hyperframes/<date>_<slug>.mp4`

### Element types — Claude picks automatically

| Type | Claude picks it when… |
|------|-----------------------|
| `glass-card` | concept intro, metaphor, key definition |
| `paradox-pair` | two opposing concepts in one sentence |
| `progress-bars` | speed/time contrast (gradually vs instantly) |
| `question-flip` | speaker explicitly shifts the question |
| `flow-arrow` | before→after, cause→effect transition |
| `icon-card` | emotional peak (heart, shield, star, brain, check, warning…) |
| `bar-chart` | comparing quantities or rankings with data |
| `line-chart` | trend, growth, accuracy over time |
| `stat-card` | key metric/percentage speaker mentions |
| `flowchart` | 3–4 step process or pipeline |
| `code-snippet` | programming/technical content with syntax highlight |
| `comparison-table` | before/after or two-approach contrast |
| `notification-card` | result, completion, achievement moment |

### Example outputs by niche

**Poetry/emotional** → glass-card, paradox-pair, icon-card (heart), flow-arrow, question-flip

**Data science/tech** → code-snippet, bar-chart, stat-card, flowchart, comparison-table

**Life/self-dev** → question-flip, comparison-table, flow-arrow, notification-card

### Composition rules (enforced automatically)

| Rule | Detail |
|------|--------|
| **Safe zones** | Left strip `x < 560px` OR right strip `x > 1360px` |
| **Vertical** | `top: 220–500px` — clears face + subtitle region |
| **No face overlap** | Claude instructed never to place elements over `x: 560–1360px` |
| **No overlapping** | Claude avoids same-position elements at same time |
| **SVG arrows** | flow-arrow uses `stroke-dashoffset` draw animation — reliable in headless render |

### Tweaking after `--no-render`

Open `/tmp/hf_<slug>/index.html`:

- Caption size: change `sz-md` → `sz-lg`/`sz-xl` on key lines
- Emphasis: wrap words in `<span class="em">text</span>`
- Re-run: `cd /tmp/hf_<slug> && npm run render`

### Known limitations

- **Burned-in source captions** conflict with overlays at talking-head shots — use clean export (no baked subs) for best results
- **Render time**: ~3 min per 60s (headless Chrome, 30fps, 1920×1080)
- **Chart data**: Claude derives values from transcript context; for exact numbers provide them in your video script

