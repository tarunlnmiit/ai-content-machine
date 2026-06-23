> ⚠️ **PIPELINE UPDATED 2026-06-20 — canonical model: [`docs/pipeline-2026.md`](../pipeline-2026.md).**
> Twitter **dropped**. Instagram / Threads **auto-publish** via the Meta Graph API (`scripts/scheduler.py`); Facebook mirrors Instagram; LinkedIn **active** (employer cleared), blog link in the **pinned first comment**. Reels → **Instagram Reels + YouTube Shorts only**, ≈9 **distinct** reels/week (not ~56). Poetry short = **poem only**. Worksheet email CTA (DS/Life) is the owned channel (Substack retired). Run `python3 scripts/weekly_winners.py` before producing. Manual steps left: record · ~10-min approve · reply.
>
> Where any step below disagrees, the canonical doc wins.

# Thursday — DS Track (~1.5 hrs)

Edit plans + captions exist from Wednesday. Today: render DS long-form, render thumbnail, upload to YouTube (if authorized), render shorts, update Notion.

> **Reference docs:** `prompts/youtube-virality-prompt.md` (YT title/description/tags before upload) · `data/kb/viral_reel_formula.md` (5-beat structure for any short/reel rendered today) · `data/kb/twitter_hook_patterns.json` (hook taxonomy for thumbnail text)

---

## Step 1 — Start render server (once per session)

```bash
cd remotion/server
npm install   # first time only
ts-node index.ts &
```

Health check:
```bash
curl http://localhost:3001/health
# → {"status":"ok","bundleCached":false}
```

First render triggers a one-time webpack bundle (~60s). Subsequent renders are fast.

---

## Step 2 — Render DS long-form (~20 min)

```bash
cd remotion
npx remotion render CourseLesson \
  output/animations/{week}/{ds_slug}.mp4 \
  --props='{"editPlanFile":"edit-plans/{week}/{ds_slug}.json"}'
```

Or via batch script:
```bash
python3 scripts/render_week.py --week {week} --niche ds
```

Output: `output/animations/{week}/{ds_slug}.mp4`

---

## Step 3 — Generate DS thumbnail ⛔ BLOCKING

Face + hook text thumbnails target 5%+ CTR. Text-only Remotion thumbnails produce ~0.5% CTR. Do not upload without completing this step.

**Checklist:**
- [ ] Face visible (surprised/confused expression, 40–60% of frame)
- [ ] Hook text: 3–5 words, high contrast, no "Tutorial 1/10" numbering
- [ ] Hook matches Tuesday's `thumbnail_brief` (if you wrote it) — use that hook

```bash
# Mode A — Canva AI (no face photo needed, hook from Tuesday brief)
python3 scripts/generate_thumbnail.py \
  --blog content/scripts/{week}/{ds_slug}_yt.md \
  --niche ds \
  --hook "Your 3-5 word hook here" \
  --week {week} \
  --canva

# Mode B — Canva AI + reaction photo (higher CTR)
python3 scripts/generate_thumbnail.py \
  --blog content/scripts/{week}/{ds_slug}_yt.md \
  --niche ds \
  --hook "Your 3-5 word hook here" \
  --face assets/raw/{week}/thumbs/{ds_slug}_face_01.jpg \
  --week {week} \
  --canva
```

Output: `output/visuals/{week}/{ds_slug}_thumb_canva.png`

**Fallback (Canva MCP unavailable):**
```bash
cd remotion
npx remotion still Thumbnail \
  output/visuals/{week}/{ds_slug}_thumb_a.png \
  --props='{"titleText":"Your Hook Here","niche":"ds","variant":"a","bgType":"dark"}'
```
⚠️ Fallback has no face — expect ~0.5% CTR. Replace as soon as Canva is available.

---

## Step 4 — Optional: HyperFrames overlay (DS recommended)

DS tutorials benefit from code callout cards and stat cards. Run AFTER long-form render.

```bash
python3 scripts/hyperframes_render.py \
  output/animations/{week}/{ds_slug}.mp4 \
  --slug {ds_slug}-aug
# Output: assets/hyperframes/{date}_{ds_slug}-aug.mp4
```

**Dry-run to review overlays first:**
```bash
python3 scripts/hyperframes_render.py \
  output/animations/{week}/{ds_slug}.mp4 \
  --no-render
open /tmp/hf_*/index.html
```

If the augmented output is better, use it for upload below.

---

## Step 5 — Upload DS long-form to YouTube

**Channel: @breathofdatascience**

```bash
python3 scripts/upload_youtube.py \
  --video output/animations/{week}/{ds_slug}.mp4 \
  --metadata content/derivatives/{week}/{ds_slug}/youtube_metadata.json \
  --thumbnail output/visuals/{week}/{ds_slug}_thumb_canva.png \
  --channel breathofdatascience \
  --scheduled "2026-MM-DDTHH:MM:00+05:30"
```

**With HyperFrames augmented version:**
```bash
python3 scripts/upload_youtube.py \
  --video "assets/hyperframes/{date}_{ds_slug}-aug.mp4" \
  --metadata content/derivatives/{week}/{ds_slug}/youtube_metadata.json \
  --thumbnail output/visuals/{week}/{ds_slug}_thumb_canva.png \
  --channel breathofdatascience \
  --scheduled "2026-MM-DDTHH:MM:00+05:30"
```

---

## Step 6 — Render DS shorts

Requires `content/derivatives/{week}/{ds_slug}/shorts_manifest.json`.

```bash
python3 scripts/render_shorts_batch.py --week {week} --niche ds
```

Outputs: `output/animations/{week}/{ds_slug}_s00.mp4`, `_s01.mp4`, `_s02.mp4`

**Single short manually:**
```bash
cd remotion
npx remotion render DSMotionShort \
  output/animations/{week}/{ds_slug}_s00.mp4 \
  --props='{"scenePlanFile":"scene-plans/{week}/{ds_slug}_s00.json"}'
```

---

## Step 6b — Optional: Raw clip shorts from long-form

Cuts real talking-head segments from the finished video — use when you want authentic face-cam clips instead of (or in addition to) Remotion motion shorts.

Copy Remotion output to the expected input path first:
```bash
cp output/animations/{week}/{ds_slug}.mp4 assets/video/edited/{ds_slug}.mp4
```

Then cut clips (Claude picks best 30–60s hook segments):
```bash
python3 scripts/clip_shorts.py --slug {ds_slug} --count 4 --smart-crop
```

`--smart-crop` detects the code region per segment and crops around it.

Skip AI selection (even-spacing fallback):
```bash
python3 scripts/clip_shorts.py --slug {ds_slug} --count 4 --smart-crop --no-claude
```

Output: `assets/video/edited/shorts/{week}/{ds_slug}_short_00.mp4`, `_short_01.mp4`, … (grouped in the ISO-week subfolder).

### Augment the clips with HyperFrames (optional)

Add Claude-powered overlays (code callouts, stat cards) on top of the cut clips:
```bash
python3 scripts/hyperframes_render.py --shorts --slug {ds_slug}
```
`--shorts` processes every `assets/video/edited/shorts/{week}/{ds_slug}_short_*.mp4` (auto-resolves the ISO-week subfolder; falls back to the flat root for legacy clips) → augmented MP4s in `assets/hyperframes/`. Portrait clips are auto re-encoded (stream-copy corrupts portrait framing under parallel load). Upload the augmented version if it beats the plain crop.

---

## Step 7 — Update Notion status

```bash
python3 scripts/update_notion_status.py \
  --title "{ds_topic_title}" \
  --status Uploaded \
  --url "https://youtube.com/watch?v={ds_video_id}"
```

Or manually: Notion → Contents DB → DS row → Status → Uploaded → paste YouTube URL.

---

## Verify

```bash
python3 scripts/list_week_content.py {week}
ls -la output/animations/{week}/{ds_slug}*.mp4
```

DS row should show ✓ for: LONG-FORM RENDER · THUMBNAIL · SHORTS · UPLOADED
