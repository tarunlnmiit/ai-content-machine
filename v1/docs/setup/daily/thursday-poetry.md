> ⚠️ **PIPELINE UPDATED 2026-06-20 — canonical model: [`docs/pipeline-2026.md`](../../guides/pipeline-2026.md).**
> Twitter **dropped**. Instagram / Threads **auto-publish** via the Meta Graph API (`scripts/scheduler.py`); Facebook mirrors Instagram; LinkedIn **active** (employer cleared), blog link in the **pinned first comment**. Reels → **Instagram Reels + YouTube Shorts only**, ≈9 **distinct** reels/week (not ~56). Poetry short = **poem only**. Worksheet email CTA (DS/Life) is the owned channel (Substack retired). Run `python3 scripts/weekly_winners.py` before producing. Manual steps left: record · ~10-min approve · reply.
>
> Where any step below disagrees, the canonical doc wins.

# Thursday — Poetry Track (~1 hr)

Edit plans + captions exist from Wednesday. Today: render Poetry long-form, render thumbnail, upload to YouTube (if authorized), render shorts, update Notion.

> **Reference docs:** `prompts/youtube-virality-prompt.md` (YT title/description/tags before upload) · `data/kb/viral_reel_formula.md` (5-beat structure for any short/reel rendered today) · `prompts/podcast-virality-prompt.md` (Poetry YouTube doubles as podcast — apply before publishing to Spotify)

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

## Step 2 — Render Poetry long-form (~15 min)

```bash
cd remotion
npx remotion render CourseLesson \
  output/animations/{week}/{poetry_slug}.mp4 \
  --props='{"editPlanFile":"edit-plans/{week}/{poetry_slug}.json"}'
```

Or via batch script:
```bash
python3 scripts/render_week.py --week {week} --niche poetry
```

Output: `output/animations/{week}/{poetry_slug}.mp4`

---

## Step 3 — Generate Poetry thumbnail ⛔ BLOCKING

**Audit finding:** Poetry channel has 0 views on most recent video. Branded text-only thumbnails are invisible. **Shorts are the primary output for this channel** until long-form CTR improves — but when you do upload long-form, the thumbnail must have a face.

**Checklist:**
- [ ] Face visible (lyrical, contemplative expression — or atmospheric AI portrait if no photo)
- [ ] Hook text: the one line from the poem that makes someone stop — not the poem title
- [ ] Drop the `||` separator style from titles entirely

```bash
# Mode A — Canva AI (atmospheric editorial style for poetry)
python3 scripts/generate_thumbnail.py \
  --blog content/scripts/{week}/{poetry_slug}_yt.md \
  --niche poetry \
  --hook "Love Doesn't Announce Itself" \
  --week {week} \
  --canva

# Mode B — with photo
python3 scripts/generate_thumbnail.py \
  --blog content/scripts/{week}/{poetry_slug}_yt.md \
  --niche poetry \
  --hook "Love Doesn't Announce Itself" \
  --face assets/raw/{week}/thumbs/{poetry_slug}_face_01.jpg \
  --week {week} \
  --canva
```

Output: `output/visuals/{week}/{poetry_slug}_thumb_canva.png`

**Shorts-first reminder:** For @breathofpoetry, prioritise rendering and uploading Shorts (Step 6) over long-form until the channel reaches 50+ subscribers. Long-form with 8 subscribers starts at zero every time; Shorts reach cold audiences.

**Fallback (Remotion, no face):**
```bash
cd remotion
npx remotion still Thumbnail \
  output/visuals/{week}/{poetry_slug}_thumb_a.png \
  --props='{"titleText":"Your Hook Here","niche":"poetry","variant":"a","bgType":"dark"}'
```

---

## Step 4 — Optional: HyperFrames overlay (Poetry — rarely needed)

Poetry works best with clean atmospherics. Only run HyperFrames if you explicitly want `AtmosphericQuote` or `LineReveal` overlays on the final render.

```bash
python3 scripts/hyperframes_render.py \
  output/animations/{week}/{poetry_slug}.mp4 \
  --slug {poetry_slug}-aug
# Output: assets/hyperframes/{date}_{poetry_slug}-aug.mp4
```

**Dry-run to review overlays first:**
```bash
python3 scripts/hyperframes_render.py \
  output/animations/{week}/{poetry_slug}.mp4 \
  --no-render
open /tmp/hf_*/index.html
```

---

## Step 5 — Upload Poetry long-form to YouTube

**Channel: @breathofpoetry**

```bash
python3 scripts/upload_youtube.py \
  --video output/animations/{week}/{poetry_slug}.mp4 \
  --metadata content/derivatives/{week}/{poetry_slug}/youtube_metadata.json \
  --thumbnail output/visuals/{week}/{poetry_slug}_thumb_a.png \
  --channel breathofpoetry \
  --scheduled "2026-MM-DDTHH:MM:00+05:30"
```

---

## Step 6 — Render Poetry shorts

Requires `content/derivatives/{week}/{poetry_slug}/shorts_manifest.json` with 3 slots pointing to distinct scene plan files (`_s00.json`, `_s01.json`, `_s02.json`).

```bash
python3 scripts/render_shorts_batch.py --week {week} --niche poetry
```

Outputs: `output/animations/{week}/{poetry_slug}_s00.mp4`, `_s01.mp4`, `_s02.mp4`

**Single short manually:**
```bash
cd remotion
npx remotion render PoetryMotionShort \
  output/animations/{week}/{poetry_slug}_s00.mp4 \
  --props='{"scenePlanFile":"scene-plans/{week}/{poetry_slug}_s00.json"}'
```

**If all 3 shorts render identically:** The manifest is pointing to the same scene plan for all slots. Fix:
```bash
python3 scripts/split_scene_plan.py \
  --input remotion/public/scene-plans/{week}/{poetry_slug}.json \
  --splits 3
# Creates _s00.json, _s01.json, _s02.json (4 scenes each from a 12-scene plan)
# Then update shorts_manifest.json to reference each file per slot
```

---

## Step 6b — Optional: Raw clip shorts from long-form

Cuts real talking-head segments from the finished video — use when you want authentic face-cam clips instead of (or in addition to) Remotion motion shorts.

Copy Remotion output to the expected input path first:
```bash
cp output/animations/{week}/{poetry_slug}.mp4 assets/video/edited/{poetry_slug}.mp4
```

Then cut clips (Claude picks best 30–60s hook segments):
```bash
python3 scripts/clip_shorts.py --slug {poetry_slug} --count 3
```

Skip AI selection (even-spacing fallback):
```bash
python3 scripts/clip_shorts.py --slug {poetry_slug} --count 3 --no-claude
```

Output: `assets/video/edited/shorts/{poetry_slug}_short_00.mp4`, `_short_01.mp4`, …

### Augment the clips with HyperFrames (rarely needed for poetry)

Poetry usually reads cleaner without overlays — skip by default. If a clip needs a quote card or stat:
```bash
python3 scripts/hyperframes_render.py --shorts --slug {poetry_slug}
```
`--shorts` processes every `assets/video/edited/shorts/{poetry_slug}_short_*.mp4` → augmented MP4s in `assets/hyperframes/`. Portrait clips are auto re-encoded (stream-copy corrupts portrait framing under parallel load).

---

## Step 7 — Update Notion status

```bash
python3 scripts/update_notion_status.py \
  --title "{poetry_topic_title}" \
  --status Uploaded \
  --url "https://youtube.com/watch?v={poetry_video_id}"
```

Or manually: Notion → Contents DB → Poetry row → Status → Uploaded → paste YouTube URL.

---

## Verify

```bash
python3 scripts/list_week_content.py {week}
ls -la output/animations/{week}/{poetry_slug}*.mp4
```

Poetry row should show ✓ for: LONG-FORM RENDER · THUMBNAIL · SHORTS · UPLOADED
