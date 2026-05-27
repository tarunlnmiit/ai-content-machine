# Friday — Life + Poetry Video: Scripts + B-roll + Recording (~2 hrs)

Record both Life and Poetry today. Edit moves to Saturday.

---

## Step 0 — Check buffer for video scripts (1 min)

```bash
ls content/buffer/week-1/life_self_dev/*_youtube_script.md 2>/dev/null
ls content/buffer/week-1/poetry_quotes/*_youtube_script.md 2>/dev/null
```

**Buffer has scripts?** → Skip Steps 1–2. Use buffer scripts directly for recording.
- Life script: `content/buffer/week-1/life_self_dev/*_youtube_script.md`
- Poetry script: `content/buffer/week-1/poetry_quotes/*_youtube_script.md`

Jump to Step 3 (B-roll). After consuming: log in Notion as `Script`.

**No buffer?** → Proceed with Steps 1–2 below.

---

## Step 1 — Generate Life YT script (~5 min)

```bash
python3 scripts/ghostwrite.py \
  --source content/blogs/[tuesday_life_blog].md \
  --niche life --format yt
```

Output: `content/scripts/YYYY-MM-DD-life-self-dev-{slug}_yt.md`
- Full talking-head script — read entirely on camera
- `[BROLL: description]` — editorial hints for B-roll cutaways during editing
- `[PAUSE]` markers for breath/clap points
- Suitable for both YouTube + Spotify podcast

---

## Step 2 — Generate Poetry YT script (~5 min)

```bash
python3 scripts/ghostwrite.py \
  --source content/blogs/[wednesday_poetry_blog].md \
  --niche poetry --format yt
```

Output: `content/scripts/YYYY-MM-DD-poetry-quotes-{slug}_yt.md`
- Full talking-head script — read entirely on camera
- Poem read twice: opening (uncontextualized) + mid-script (with pauses)
- Includes poet attribution if third-party poem
- `[BROLL:]` markers = editorial hints for B-roll cutaways during editing

---

## Step 3 — Generate AI B-roll for Life + Poetry (10–20 min)

Fires all active browser backends **in parallel** — each cue gets multiple clips with different prompt variants. Pick the best in editing.

```bash
python3 scripts/generate_video_ai.py \
  --script content/scripts/YYYY-MM-DD-life-self-dev-{slug}_yt.md \
  --niche life

python3 scripts/generate_video_ai.py \
  --script content/scripts/YYYY-MM-DD-poetry-quotes-{slug}_yt.md \
  --niche poetry
```

Output: `assets/videos/{slug}/`
- `{slug}_broll_00_hf.mp4`, `{slug}_broll_00_qwen.mp4`, `{slug}_broll_00_hunyuan.mp4`, ... (1 clip per backend per cue)
- `VIDEO_MAP.json` (all clips with backend, model, prompt used)

Check active backends:
```bash
python3 scripts/lib/browser_video_client.py --active
# → ['hf', 'hunyuan']  (both free, no login needed)
```

Worker pool: 2 backends = 2 workers, one clip per cue (not one per backend per cue). 5 cues → 5 clips. Browsers open visibly (`BROWSER_HEADLESS=0` in `.env`) — watch progress live.

Models: `hf` = LTX-2.3 · `hunyuan` = Wan 2.2 Fast

Fallback to stock footage (Pexels/Pixabay) if needed:
```bash
python3 scripts/fetch_videos.py \
  --script content/scripts/YYYY-MM-DD-life-self-dev-{slug}_yt.md \
  --niche life
```

---

## Step 4 — Generate production guides (1–2 min each)

```bash
python3 scripts/generate_production_guide.py \
  --script content/scripts/YYYY-MM-DD-life-self-dev-{slug}_yt.md \
  --niche life

python3 scripts/generate_production_guide.py \
  --script content/scripts/YYYY-MM-DD-poetry-quotes-{slug}_yt.md \
  --niche poetry \
  --poem data/poems/[slug].txt \
  --full-poem
```

Output: `content/scripts/{slug}_PRODUCTION_GUIDE.md`
- Section → clip mapping table
- Estimated runtime (~7–9 min)
- Used by `auto_edit.py` for broll timing (Saturday). DaVinci fallback steps included for manual passes.

Poetry only: `--full-poem` also generates `content/scripts/{slug}_poetry_overlay.srt` (full poem text distributed across voiceover duration for overlay captions)

---

## Step 5 — Generate teleprompters for Life + Poetry (~1 min)

```bash
python3 scripts/generate_teleprompter.py \
  --script content/scripts/YYYY-MM-DD-life-self-dev-{slug}_yt.md \
  --open

python3 scripts/generate_teleprompter.py \
  --script content/scripts/YYYY-MM-DD-poetry-quotes-{slug}_yt.md \
  --open
```

Output: `assets/teleprompter/{slug}_teleprompter.html` — opens in browser.
Controls: `Space` start/pause · `↑↓` speed · `R` restart · `F` fullscreen

---

## Step 6 — Record Life video (20–30 min)

**Setup:** See [recording-guide.md](recording-guide.md) for full setup, checklist, and tips.

1. Open teleprompter full-screen (`assets/teleprompter/[life_slug]_teleprompter.html`) — use second monitor or phone via AirPlay
2. Hit record on iPhone
3. Read entire script on camera at ~130 wpm — clap at `[PAUSE]` points for edit markers
4. `[BROLL:]` markers = notes for editor only, keep talking through them
5. Transfer recording to: `assets/raw/[life_slug].mov`

---

## Step 7 — Record Poetry video (20–30 min)

**Same setup as Step 6 — see [recording-guide.md](recording-guide.md).**

1. Open teleprompter full-screen (`assets/teleprompter/[poetry_slug]_teleprompter.html`) — use second monitor or phone via AirPlay
2. Hit record on iPhone
3. Read entire script on camera — poem twice as scripted (first read slow/uncontextualized, second with `[PAUSE]` markers)
4. `[BROLL:]` markers = notes for editor only, keep talking through them
5. Transfer recording to: `assets/raw/[poetry_slug].mov`

---

## Step 8 — Generate captions for Life + Poetry (~2 min each)

```bash
python3 scripts/generate_captions.py \
  --audio assets/raw/[life_slug].mov \
  --format srt \
  --output content/scripts/[life_slug]_captions.srt

python3 scripts/generate_captions.py \
  --audio assets/raw/[poetry_slug].mov \
  --format srt \
  --output content/scripts/[poetry_slug]_captions.srt
```

---

## After production — buffer or keep live?

```bash
python3 scripts/push_to_buffer.py --auto --dry-run   # preview
python3 scripts/push_to_buffer.py --auto              # auto-decide all niches
```
Buffer < 4 weeks → copied to next empty slot. Buffer full → stays as live content.
File naming: `content/blogs/YYYY-MM-DD_{niche}_{slug}.md` · scripts: `content/scripts/YYYY-MM-DD_{niche-dashes}-{slug}_yt.md`
See full naming table: [weekly-operating-guide.md § File Naming Conventions](weekly-operating-guide.md#file-naming-conventions)

