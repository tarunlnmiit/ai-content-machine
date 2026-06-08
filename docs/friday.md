# Friday — Life + Poetry Video: Scripts + B-roll + Recording (~2 hrs)

Record both Life and Poetry today. Edit moves to Saturday.

## Friday at a glance

| Time | Action | Output goes live |
|------|--------|------------------|
| 9:00 AM | Record Life video (script + B-roll) | — |
| 11:00 AM | Poetry LinkedIn post via scheduler | Poetry LinkedIn goes live |
| 12:00 PM | Record Poetry video (script + B-roll) | — |
| 12:00 PM | Poetry Twitter thread posts via reminder | Poetry Twitter thread goes live |
| 3:00 PM | Poetry long-form + blog + shorts + Metricool | **Poetry video goes live on YouTube** · **Substack** · **Medium** · IG/FB/Threads scheduled for next Fri |
| 8:00 PM | Poetry shorts post (slot 9) | Poetry shorts start going live throughout week |
| 10:00 PM | IG/FB carousel (Poetry) posts next Fri | (Week+1) |

---

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
- `[ANIMATION:]` markers — title card (top) + 1–2 lower thirds (mid) + outro card (end)
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
- `[ANIMATION:]` markers — title card (poem title) + 1–2 lower thirds (key stanza lines) + outro card

---

## Step 2b — Generate animation overlays for Life + Poetry (~2 min)

Renders Remotion title card, lower thirds, and outro card from `[ANIMATION:]` tags in each script.

```bash
python3 scripts/generate_animation_prompts.py \
  content/scripts/YYYY-MM-DD-life-self-dev-{slug}_yt.md \
  --render

python3 scripts/generate_animation_prompts.py \
  content/scripts/YYYY-MM-DD-poetry-quotes-{slug}_yt.md \
  --render
```

Output: `output/animations/{slug}_{n}_{type}.mp4` — one MP4 per tag (title card + lower thirds + outro card). Drop into DaVinci as overlay tracks during Step 1/2 of Saturday edit.

**No `[ANIMATION:]` tags in script?** Script was generated before this feature. Add them manually or regenerate with `ghostwrite.py`.

---

## Step 3 — Fetch stock B-roll for Life + Poetry (~2 min)

```bash
python3 scripts/fetch_videos.py \
  --script content/scripts/YYYY-MM-DD-life-self-dev-{slug}_yt.md \
  --niche life

python3 scripts/fetch_videos.py \
  --script content/scripts/YYYY-MM-DD-poetry-quotes-{slug}_yt.md \
  --niche poetry
```

Pulls from Pexels (landscape preferred) + Pixabay. Stores clips in `assets/videos/{slug}/`. Pipeline uses all downloaded clips evenly distributed across `[BROLL:]` cues in Saturday edit step.

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
python3 scripts/push_to_buffer.py --auto              # run
```
→ Decision logic + file naming: [_buffer_decision.md](_buffer_decision.md)

