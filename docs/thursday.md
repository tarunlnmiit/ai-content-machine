# Thursday — DS Video: Script + Record + Edit + Reel + Upload (~2 hrs)

DS is self-contained today. Life + Poetry video production moves to Friday.

## Thursday at a glance

| Time | Action | Output goes live |
|------|--------|------------------|
| 12:00 PM | DS LinkedIn posts via scheduler | DS LinkedIn goes live |
| 1:00 PM | DS Twitter thread posts via reminder | DS Twitter thread goes live |
| 2:00 PM | Script / Record / Edit DS video | — |
| 6:00 PM | DS long-form + blog + shorts + Metricool | **DS video goes live on YouTube** · **Substack** · **Medium** · IG/FB/Threads scheduled for next Wed |
| 9:00 PM | DS shorts post (slot 7) | DS shorts start going live throughout week |

---

---

## Step 0 — Check buffer for DS script (1 min)

```bash
ls content/buffer/week-1/data_science_tech/*_youtube_script.md 2>/dev/null
```

**Buffer has script?** → Skip Step 1. Use it directly:
- Script: `content/buffer/week-1/data_science_tech/*_youtube_script.md`

Jump to Step 2 (validate code blocks). After consuming: log in Notion as `Script`.

**No buffer?** → Proceed with Step 1 below.

---

## Step 1 — Generate DS YouTube script (~5 min)

Screen recording script with [SCREEN:] cues:
```bash
python3 scripts/ghostwrite.py \
  --source content/blogs/[monday_ds_blog].md \
  --niche ds --format yt
# --video-style screen is default for DS
```

Output: `content/scripts/YYYY-MM-DD-data-science-tech-{slug}_yt.md`
- [SCREEN: show X] cues for screen transitions
- [CODE_INSERT: filename/function] for code blocks
- [PAUSE] markers for breath points

Optional — conceptual DS (no screen recording):
```bash
python3 scripts/ghostwrite.py \
  --source content/blogs/[monday_ds_blog].md \
  --niche ds --format yt --video-style stock
# Then follow Life/Poetry B-roll workflow (Friday)
```

---

## Step 1b — Generate animation prompts from script (~1 min)

Extracts every `[ANIMATION: ...]` tag and writes Remotion component prompts.

```bash
python3 scripts/generate_animation_prompts.py \
  content/scripts/YYYY-MM-DD-data-science-tech-{slug}_yt.md
```

Output: `content/prompts/{slug}_animation_prompts.txt` — one prompt per animation tag.
Feed each prompt to Claude to generate the corresponding `remotion/src/compositions/` component.

**To render MP4s directly** (skips manual TSX step — uses built-in templates):

```bash
python3 scripts/generate_animation_prompts.py \
  content/scripts/YYYY-MM-DD-data-science-tech-{slug}_yt.md \
  --render
```

Output: `output/animations/{slug}_{n}_{type}.mp4` — one MP4 per animation tag.

---

## Step 2 — Generate teleprompter for DS script (~1 min)

```bash
python3 scripts/generate_teleprompter.py \
  --script content/scripts/YYYY-MM-DD-data-science-tech-{slug}_yt.md \
  --open
```

Output: `assets/teleprompter/{slug}_teleprompter.html` — opens in browser.
Controls: `Space` start/pause · `↑↓` speed · `R` restart · `F` fullscreen

---

## Step 3 — Screen record DS code walkthrough (30–45 min)

1. Open teleprompter full-screen on a second monitor (or phone via AirPlay)
2. Open screen recorder (ScreenFlow · OBS · built-in Mac)
3. Open IDE showing blog code at 200% zoom for visibility
4. Follow script — show code, run demos, narrate [SCREEN:] cues
5. Save: `assets/video/raw/{slug}_screen.mp4`

---

## Step 4 — Record DS voiceover (15–20 min)

1. Read script aloud naturally at ~130 wpm
2. Clap at [PAUSE] points (visible in waveform for easy trim)
3. Save: `assets/audio/{slug}_voiceover.wav`

Tools: Voice Memos (quick) · Audacity (control) · Adobe Audition (pro)

---

## Step 5 — Generate captions with Whisper (~2 min)

```bash
python3 scripts/generate_captions.py \
  --audio assets/audio/{slug}_voiceover.wav \
  --format srt \
  --output content/scripts/{slug}_captions.srt
```

---

## Step 5b — Generate DS thumbnail image (~2 min)

Thumbnail brief already generated Tuesday. Render it to HTML + PNG now:

```bash
conda run -n content_engine_env python3 scripts/generate_thumbnail.py \
  --blog content/blogs/[monday_ds_blog].md

# Open in browser to verify, then export PNG
open assets/thumbnails/[ds_slug]_thumbnail.html

conda run -n content_engine_env python3 scripts/generate_thumbnail.py \
  --blog content/blogs/[monday_ds_blog].md --export
# → assets/thumbnails/[ds_slug]_thumbnail.png (1280×720)
```

Use `--force` to regenerate if design needs adjustment.

---

## Step 6 — Auto-edit DS (~5 min)

Reference: `docs/video-production-guide.md`

DS workflow has 2 paths:

**Path A — Talking-head only (recommended for explainer):**
```bash
python3 scripts/auto_edit.py \
  --raw assets/raw/[ds_slug].mov \
  --script content/scripts/YYYY-MM-DD-data-science-tech-[ds_slug]_yt.md \
  --niche ds \
  --slug [ds_slug]
# → assets/video/edited/[ds_slug].mp4 (broll overlay on talking-head + captions)
```

**Path B — Screen-recording + talking-head (manual composite):**
1. Run Path A on talking-head only → base mp4
2. Open in DaVinci, layer screen-recording on top of broll segments where you want code visible
3. Re-export

`fetch_videos.py` runs inside `auto_edit.py` automatically (uses `[BROLL:]` cues from script).

---

## Step 7 — HyperFrames visual augmentation (~5 min)

Claude picks element types automatically for DS content (code snippets, bar charts, stat cards, flowcharts, comparison tables).

```bash
# Long-form
python3 scripts/hyperframes_render.py \
  assets/video/edited/[ds_slug].mp4 \
  --slug ds-[slug]-aug

# All shorts in one command (auto-discovers from slug)
python3 scripts/hyperframes_render.py --shorts --slug [ds_slug]
```

Output: `assets/hyperframes/<date>_<slug>.mp4`

Reference: `docs/video-production-guide.md` → HyperFrames section.

---

## Step 8 — Auto-generate DS shorts (~3 min)

```bash
python3 scripts/clip_shorts.py --slug YYYY-MM-DD_data_science_tech_[ds_slug] --count 4
# → assets/video/edited/shorts/YYYY-MM-DD_data_science_tech_[ds_slug]_short_NN.mp4
```

Claude CLI picks best hook segments. Legacy single-reel workflow (`find_best_reel_moment.py` + `create_vertical_reels.py`) still available.

---

## Step 9 — Upload DS to YouTube (~10 min)

Long-form:
```bash
python3 scripts/upload_youtube.py \
  --video assets/video/edited/[ds_slug].mp4 \
  --slug [ds_slug]
```

Shorts (loop manifest):
```bash
for f in assets/video/edited/shorts/[ds_slug]_short_*.mp4; do
  python3 scripts/upload_youtube.py --shorts --slug [ds_slug] \
    --channel "Breath of Data Science" --video "$f"
done
```

Verify export:
```bash
ls -la assets/video/edited/
# Should show {slug}.mp4 + {slug}_reel.mp4
```

---

## After production — buffer or keep live?

```bash
python3 scripts/push_to_buffer.py --auto --dry-run   # preview
python3 scripts/push_to_buffer.py --auto              # run
```
→ Decision logic + file naming: [_buffer_decision.md](_buffer_decision.md)

