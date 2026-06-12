# Thursday — Life Track (~1 hr)

Edit plans + captions exist from Wednesday. Today: render Life long-form, render thumbnail, upload to YouTube (if authorized), render shorts, update Notion.

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

---

## Step 2 — Render Life long-form (~15 min)

```bash
cd remotion
npx remotion render CourseLesson \
  output/animations/{week}/{life_slug}.mp4 \
  --props='{"editPlanFile":"edit-plans/{week}/{life_slug}.json"}'
```

Or via batch script:
```bash
python3 scripts/render_week.py --week {week} --niche life
```

Output: `output/animations/{week}/{life_slug}.mp4`

---

## Step 3 — Render Life thumbnail (~2 min)

```bash
cd remotion

# Variant A — default upload
npx remotion still Thumbnail \
  output/visuals/{week}/{life_slug}_thumb_a.png \
  --props='{"titleText":"Your Title Here","niche":"life","variant":"a","bgType":"dark"}'

# Variant B — A/B test alternate
npx remotion still Thumbnail \
  output/visuals/{week}/{life_slug}_thumb_b.png \
  --props='{"titleText":"Your Title Here","niche":"life","variant":"b"}'
```

---

## Step 4 — Optional: HyperFrames overlay (Life — use when video has data/numbers)

```bash
python3 scripts/hyperframes_render.py \
  output/animations/{week}/{life_slug}.mp4 \
  --slug {life_slug}-aug
# Output: assets/hyperframes/{date}_{life_slug}-aug.mp4
```

**Dry-run to review overlays first:**
```bash
python3 scripts/hyperframes_render.py \
  output/animations/{week}/{life_slug}.mp4 \
  --no-render
open /tmp/hf_*/index.html
```

Skip if the video is primarily story/reflection — overlays add noise without data to show.

---

## Step 5 — Upload Life long-form to YouTube

**Channel: @breathoflife_**

```bash
python3 scripts/upload_youtube.py \
  --video output/animations/{week}/{life_slug}.mp4 \
  --metadata content/derivatives/{week}/{life_slug}/youtube_metadata.json \
  --thumbnail output/visuals/{week}/{life_slug}_thumb_a.png \
  --channel breathoflife_ \
  --scheduled "2026-MM-DDTHH:MM:00+05:30"
```

---

## Step 6 — Render Life shorts

Requires `content/derivatives/{week}/{life_slug}/shorts_manifest.json`.

```bash
python3 scripts/render_shorts_batch.py --week {week} --niche life
```

Outputs: `output/animations/{week}/{life_slug}_s00.mp4`, `_s01.mp4`, `_s02.mp4`

**Single short manually:**
```bash
cd remotion
npx remotion render LifeMotionShort \
  output/animations/{week}/{life_slug}_s00.mp4 \
  --props='{"scenePlanFile":"scene-plans/{week}/{life_slug}_s00.json"}'
```

---

## Step 6b — Optional: Raw clip shorts from long-form

Cuts real talking-head segments from the finished video — use when you want authentic face-cam clips instead of (or in addition to) Remotion motion shorts.

Copy Remotion output to the expected input path first:
```bash
cp output/animations/{week}/{life_slug}.mp4 assets/video/edited/{life_slug}.mp4
```

Then cut clips (Claude picks best 30–60s hook segments):
```bash
python3 scripts/clip_shorts.py --slug {life_slug} --count 4
```

Skip AI selection (even-spacing fallback):
```bash
python3 scripts/clip_shorts.py --slug {life_slug} --count 4 --no-claude
```

Output: `assets/video/edited/shorts/{life_slug}_short_00.mp4`, `_short_01.mp4`, …

### Augment the clips with HyperFrames (optional)

Add Claude-powered overlays (stat cards, lower thirds) on top of the cut clips:
```bash
python3 scripts/hyperframes_render.py --shorts --slug {life_slug}
```
`--shorts` processes every `assets/video/edited/shorts/{life_slug}_short_*.mp4` → augmented MP4s in `assets/hyperframes/`. Portrait clips are auto re-encoded (stream-copy corrupts portrait framing under parallel load). Upload the augmented version if it beats the plain crop.

---

## Step 7 — Update Notion status

```bash
python3 scripts/update_notion_status.py \
  --title "{life_topic_title}" \
  --status Uploaded \
  --url "https://youtube.com/watch?v={life_video_id}"
```

Or manually: Notion → Contents DB → Life row → Status → Uploaded → paste YouTube URL.

---

## Verify

```bash
python3 scripts/list_week_content.py {week}
ls -la output/animations/{week}/{life_slug}*.mp4
```

Life row should show ✓ for: LONG-FORM RENDER · THUMBNAIL · SHORTS · UPLOADED
