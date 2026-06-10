# Thursday — Edit, Render & Upload Videos (~2–3 hrs)

Raw footage exists from Wednesday. Today: render long-form + shorts via Remotion, upload to YouTube, schedule.

## Thursday at a glance

| Time | Action | Output |
|------|--------|--------|
| 9:00 AM | Prepare captions JSON (all 3) | `remotion/public/captions/{week}/{slug}.json` |
| 9:30 AM | Render long-form videos (all 3) | `output/animations/{week}/{slug}.mp4` |
| 10:30 AM | Render thumbnails (still export) | `output/visuals/{week}/{slug}_thumb.png` |
| 11:00 AM | Upload DS long-form → YouTube | **@breathofdatascience** |
| 11:15 AM | Upload Life long-form → YouTube | **@breathoflife_** |
| 11:30 AM | Upload Poetry long-form → YouTube | **@breathofpoetry** |
| 12:00 PM | Render shorts batch (all 3 niches) | `output/animations/{week}/{slug}_s*.mp4` |
| 1:00 PM  | Upload shorts to all channels | YouTube Shorts — 2/day Mon–Sun queue |
| 6:00 PM  | Videos go live | YouTube channels |

---

## Step 1 — Prepare edit plans + captions

Each video needs an edit plan JSON and a captions JSON in `remotion/public/`:

```
remotion/public/
  edit-plans/{week}/{slug}.json      # EditPlan schema (see src/types.ts)
  captions/{week}/{slug}.json        # Caption[] from @remotion/captions
```

Generate captions from raw audio:
```bash
# Whisper → JSON caption file
python3 scripts/generate_captions.py \
  --audio assets/raw/{week}/{slug}.mov \
  --output remotion/public/captions/{week}/{slug}.json
```

Build/update the edit plan (cut segments, b-roll cues):
```bash
# Open in Remotion Studio for visual timeline editing
cd remotion && npm run dev
# → http://localhost:3000 → CourseLesson → adjust props live
```

---

## Step 2 — Render long-form videos

**Render all 3 at once:**
```bash
python3 scripts/render_week.py --week 2026-W{nn}
```

**Or render a single slug:**
```bash
cd remotion
npx remotion render CourseLesson output/animations/2026-W{nn}/{slug}.mp4 \
  --props='{"editPlanFile":"edit-plans/2026-W{nn}/{slug}.json"}'
```

Long-form output: `output/animations/{week}/{slug}.mp4`

---

## Step 3 — Render thumbnails

```bash
cd remotion

# Variant A (dark, left-aligned)
npx remotion still Thumbnail output/visuals/2026-W{nn}/{slug}_thumb_a.png \
  --props='{"titleText":"Your Title Here","niche":"ds","variant":"a","bgType":"dark"}'

# Variant B (centered glass card) — for A/B testing
npx remotion still Thumbnail output/visuals/2026-W{nn}/{slug}_thumb_b.png \
  --props='{"titleText":"Your Title Here","niche":"ds","variant":"b"}'
```

Repeat for Life (`"niche":"life"`) and Poetry (`"niche":"poetry"`).

---

## Step 4 — Upload long-form to YouTube

```bash
python3 scripts/upload_youtube.py \
  --video output/animations/{week}/{ds_slug}.mp4 \
  --metadata content/derivatives/{week}/{ds_slug}/youtube_metadata.json \
  --thumbnail output/visuals/{week}/{ds_slug}_thumb_a.png \
  --channel breathofdatascience \
  --scheduled "2026-MM-DDTHH:MM:00+05:30"
```

Repeat for Life (`--channel breathoflife_`) and Poetry (`--channel breathofpoetry`).

---

## Step 5 — Render shorts batch

Each slug needs `content/derivatives/{week}/{slug}/shorts_manifest.json` — see schema in `scripts/render_shorts_batch.py`.

```bash
# Render all 3 niches
python3 scripts/render_shorts_batch.py --week 2026-W{nn} --niche ds
python3 scripts/render_shorts_batch.py --week 2026-W{nn} --niche life
python3 scripts/render_shorts_batch.py --week 2026-W{nn} --niche poetry
```

Shorts output: `output/animations/{week}/{slug}_s{slot:02d}.mp4`

**Clip-based short** (fast, reuse long-form footage):
```bash
cd remotion
npx remotion render ShortClip output/animations/{week}/{slug}_s00.mp4 \
  --props='{"editPlanFile":"edit-plans/{week}/{slug}.json","clipStartSec":10,"clipEndSec":70}'
```

**Motion graphic short** (pure animation, no camera):
```bash
# After populating remotion/public/scene-plans/{week}/{slug}_s01.json
cd remotion
npx remotion render DSMotionShort output/animations/{week}/{slug}_s01.mp4 \
  --props='{"scenePlanFile":"scene-plans/{week}/{slug}_s01.json"}'
```

YouTube Shorts schedule: **2/day Mon–Sun** at 10:00 AM and 8:00 PM IST

---

## Optional — HyperFrames visual augmentation

Run AFTER long-form Remotion render. Applies Claude-powered visual overlays (glass cards, code callouts, stat cards, flow arrows) on top of the rendered MP4. Not required — use it when the Remotion render alone lacks on-screen data visualizations.

**When to use:**
- DS tutorials → code callout cards, stat cards add significant value
- Life videos with data/numbers → stat cards add credibility
- Poetry → rarely needed (abstract B-roll is cleaner without overlays)

**When to skip:** If scene plan already includes rich motion graphics, HyperFrames is redundant.

### Long-form overlay pass

```bash
# Run overlay on rendered MP4
python3 scripts/hyperframes_render.py \
  output/animations/{week}/{slug}.mp4 \
  --slug {slug}-aug
# Output: assets/hyperframes/{date}_{slug}-aug.mp4
```

### Inspect overlays before rendering

```bash
# Dry-run: generates HTML overlay without rendering
python3 scripts/hyperframes_render.py \
  output/animations/{week}/{slug}.mp4 \
  --no-render

# Open in browser to review:
open /tmp/hf_*/index.html
# Edit overlay timing, text, positions in the HTML file

# Then render the edited version:
cd /tmp/hf_*/
npm run render
```

### Shorts overlay

```bash
python3 scripts/hyperframes_render.py \
  --shorts \
  --slug {full_slug}
# full_slug = YYYY-MM-DD_data_science_tech_{slug}
```

### Use augmented version

If the HyperFrames output is better, use it for upload:
```bash
# Upload augmented instead of plain Remotion render:
python3 scripts/upload_youtube.py \
  --video "assets/hyperframes/{date}_{slug}-aug.mp4" \
  --metadata content/derivatives/{week}/{slug}/youtube_metadata.json \
  --channel {channel_name}
```

Full HyperFrames reference: `docs/video-production-guide.md` → HyperFrames section

---

## Step 6 — Upload shorts

```bash
bash output/scheduled/upload_shorts.sh
```

---

## Step 7 — Update Notion status (~5 min)

Mark all 3 content items as **Uploaded** in Notion Contents DB.

```bash
# DS
python3 scripts/update_notion_status.py \
  --title "{ds_topic_title}" \
  --status Uploaded \
  --url "https://youtube.com/watch?v={ds_video_id}"

# Life
python3 scripts/update_notion_status.py \
  --title "{life_topic_title}" \
  --status Uploaded \
  --url "https://youtube.com/watch?v={life_video_id}"

# Poetry
python3 scripts/update_notion_status.py \
  --title "{poetry_topic_title}" \
  --status Uploaded \
  --url "https://youtube.com/watch?v={poetry_video_id}"
```

Or manually: open Notion → Contents DB → find each row → Status → Uploaded → paste YouTube URL.

---

## Step 8 — Verify + refresh tracker (~3 min)

```bash
# Confirm all 3 videos + blogs have URLs in derivatives
python3 scripts/list_week_content.py 2026-W{nn}
# All 3 slugs should show ✓ for video + blog

# Refresh content tracker CSV
python3 scripts/sync_tracker.py --week 2026-W{nn}
# → data/content_tracker.csv updated
```

If any video is missing: check YouTube Studio — it may still be processing (up to 30 min after upload).

---

## Optional — Audiogram clips (for social posts)

```bash
cd remotion

# 1080×1080 feed format
npx remotion render AudiogramFeed output/animations/{week}/{slug}_audiogram_feed.mp4 \
  --props='{"audioFile":"audio/{week}/{slug}_clip.mp3","startSec":0,"endSec":30,"quote":"Your quote here","niche":"ds","podcastName":"Breath of Data Science"}'

# 1080×1920 story format
npx remotion render AudiogramStory output/animations/{week}/{slug}_audiogram_story.mp4 \
  --props='{"audioFile":"audio/{week}/{slug}_clip.mp3","startSec":0,"endSec":30,"quote":"Your quote here","niche":"ds","podcastName":"Breath of Data Science"}'
```

---

## Verify

```bash
python3 scripts/list_week_content.py 2026-W{nn}
```

VIDEO & MEDIA → animations should show ✓ for all 3 slugs + their shorts.

---

## Render reference

| Composition | Format | Use case |
|------------|--------|----------|
| `CourseLesson` | 1920×1080 | Long-form talking head (any niche) |
| `ShortClip` | 1080×1920 | Portrait crop of long-form footage |
| `DSMotionShort` | 1080×1920 | Pure DS motion graphic short |
| `LifeMotionShort` | 1080×1920 | Pure Life motion graphic short |
| `PoetryMotionShort` | 1080×1920 | Pure Poetry motion graphic short |
| `Thumbnail` | 1280×720 | YouTube thumbnail (still export) |
| `AudiogramFeed` | 1080×1080 | Podcast audiogram for feed |
| `AudiogramStory` | 1080×1920 | Podcast audiogram for stories |
| `SocialCard1x1` | 1080×1080 | Animated social card for feed |
| `SocialCard9x16` | 1080×1920 | Animated social card for stories |
| `AbstractDS` | 1920×1080 | DS b-roll loop (render once, reuse) |
| `AbstractLife` | 1920×1080 | Life b-roll loop |
| `AbstractPoetry` | 1920×1080 | Poetry b-roll loop |
