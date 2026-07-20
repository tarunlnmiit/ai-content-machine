---
title: "Thursday — Edit, Render & Upload Videos (~2–3 hrs)"
type: doc
slug: thursday
tags: [content/doc]
---
> ⚠️ **PIPELINE UPDATED 2026-06-20 — canonical model: [`docs/pipeline-2026.md`](../../guides/pipeline-2026.md).**
> Twitter **dropped**. Instagram / Threads **auto-publish** via the Meta Graph API (`scripts/scheduler.py`); Facebook mirrors Instagram; LinkedIn **active** (employer cleared) with the blog link in the **pinned first comment**. Reels → **Instagram Reels + YouTube Shorts only**, ≈9 **distinct** reels/week (not ~56). 3 long-form (1/niche). Poetry short = **poem only**; poetry Medium = poem + 150–350w essay. Worksheet email CTA (DS/Life) is the owned channel (Substack retired). Run `python3 scripts/weekly_winners.py` before producing. Only manual steps left: record · ~10-min approve · reply to comments/DMs.
>
> Where any step below disagrees with this banner or the canonical doc, the canonical doc wins.

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
# Whisper → Caption[] JSON for @remotion/captions
python3 scripts/generate_captions.py \
  --audio assets/raw/{week}/{slug}.mov \
  --format remotion_json \
  --output remotion/public/captions/{week}/{slug}.captions.json \
  --model medium
```

Build/update the edit plan (cut segments, b-roll cues):
```bash
# Open in Remotion Studio for visual timeline editing
cd remotion && npm run dev
# → http://localhost:3000 → CourseLesson → adjust props live
```

---

## Step 1b — Start render server (first Thursday of the week)

The render server handles batch stills and long-form renders via HTTP. Start it once and leave it running:

```bash
cd remotion/server
npm install          # first time only
ts-node index.ts &   # starts on http://localhost:3001
```

Health check:
```bash
curl http://localhost:3001/health
# → {"status":"ok","bundleCached":false}
```

The first render request triggers a one-time Webpack bundle (~60s). Subsequent renders are fast.

---

## Step 2 — Render long-form videos

**Render all 3 at once:**
```bash
python3 scripts/render_week.py --week 2026-W{nn}
```
Renders run 2-at-a-time by default (`--concurrency 2`). Remotion+ffmpeg is
CPU-bound — raise to `--concurrency 3` only with CPU/RAM headroom, drop to
`--concurrency 1` if the machine thrashes.

**Or render a single slug:**
```bash
cd remotion
npx remotion render CourseLesson output/animations/2026-W{nn}/{slug}.mp4 \
  --props='{"editPlanFile":"edit-plans/2026-W{nn}/{slug}.json"}'
```

Long-form output: `output/animations/{week}/{slug}.mp4`

---

## Step 3 — Generate thumbnails ⛔ BLOCKING — do not upload without completing this

**Why this is blocking:** thumbnails without a face get 0.3–1.1% CTR across all three channels. Thumbnails with face + hook text target 5%+. This is the highest-leverage step before upload.

### Thumbnail checklist — ALL three must pass before uploading

- [ ] **Face visible** — your expression (surprised, confused, pointing) fills 40–60% of the frame. Zero text-only thumbnails. Zero diagram thumbnails. Zero "Breath of X" branded-color thumbnails.
- [ ] **Hook text present** — 3–5 words, high contrast, readable at 120px wide. Names the specific problem or result ("Setup That Breaks Everything"), not the category ("Python Tutorial").
- [ ] **No series numbers** — no "Tutorial 1/10", no "8." prefix. Series numbering goes in the description only.

### Mode A — Canva AI (automated, no photo needed)

```bash
# DS
python3 scripts/generate_thumbnail.py \
  --niche ds \
  --hook "The Setup Mistake Everyone Makes" \
  --week 2026-W{nn} \
  --slug {ds_slug}

# Life
python3 scripts/generate_thumbnail.py \
  --niche life \
  --hook "I Did This for 3 Years. Wrong." \
  --week 2026-W{nn} \
  --slug {life_slug}

# Poetry
python3 scripts/generate_thumbnail.py \
  --niche poetry \
  --hook "Love Doesn't Announce Itself" \
  --week 2026-W{nn} \
  --slug {poetry_slug}
```

Output: `output/visuals/{week}/{slug}_thumb_canva.png`

The hook comes from your Tuesday script's `[HOOK]` line, shortened to 3–5 words.

### Mode B — Photo-based (use when you have reaction shots from Wednesday)

```bash
python3 scripts/generate_thumbnail.py \
  --niche ds \
  --hook "The Setup Mistake Everyone Makes" \
  --face assets/raw/{week}/thumbs/{slug}_face_01.jpg \
  --week 2026-W{nn} \
  --slug {ds_slug}
```

See `docs/recording-guide.md` → Thumbnail Reaction Shots for how to capture these.

### Fallback — Remotion still (only if Canva MCP is down)

⚠️ No face = ~0.5% CTR. Use only as last resort.

```bash
cd remotion
npx remotion still Thumbnail output/visuals/2026-W{nn}/{slug}_thumb_a.png \
  --props='{"titleText":"Your Hook Here","niche":"ds","variant":"a","bgType":"dark"}'
```

### Verify before uploading

Open each thumbnail at full resolution. If any checklist item fails → regenerate (adjust hook wording) or reshoot expression photo.

---

## Step 4 — Upload long-form to YouTube

> **Virality reference:** `prompts/youtube-virality-prompt.md` — title formula, description structure, tag strategy, and upload checklist. Apply before filling metadata.

**Title pre-flight (30 seconds, mandatory):**
- [ ] Title leads with the specific problem/hook — not the category label
- [ ] No series number in the title ("Tutorial 1/10", "Episode 8") — move to description
- [ ] Title passes the "would I click this cold?" test — if no, rewrite before uploading

```bash
python3 scripts/upload_youtube.py \
  --video output/animations/{week}/{ds_slug}.mp4 \
  --metadata content/derivatives/{week}/{ds_slug}/youtube_metadata.json \
  --thumbnail output/visuals/{week}/{ds_slug}_thumb_canva.png \
  --channel breathofdatascience \
  --scheduled "2026-MM-DDTHH:MM:00+05:30"
```

Repeat for Life (`--channel breathoflife_`) and Poetry (`--channel breathofpoetry`).

Note: `--thumbnail` now defaults to the Canva-generated file (`_thumb_canva.png`). If Mode A/B wasn't run, fall back to `_thumb_a.png` — but flag it as needing replacement.

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

## Step 6 — Generate Instagram Reel briefs (NEW — ~5 min)

After shorts are cut, generate Instagram-specific hooks, captions, and DM keywords for all 3 niches. This is the layer that turns YouTube Shorts into Instagram Reels with the right framing for each account.

```bash
# Generate briefs for all 3 niches in one command
python3 scripts/generate_ig_reel_brief.py --week 2026-W{nn}
```

Or per-slug if you only need one:
```bash
python3 scripts/generate_ig_reel_brief.py \
  --week 2026-W{nn} \
  --slug {slug}
```

**Output:** `content/derivatives/{week}/{slug}/ig_reel_brief.md` for each piece

Each brief contains:
- Account routing (@breathofdatascience for DS, @mistakenlyhuman for Life + Poetry)
- 3 hook options (pick the one that fits your recording energy)
- Best clip timestamps Claude identified
- Instagram caption (ready to copy-paste, ~120 words)
- DM keyword for SuperProfile/CreatorFlow trigger
- Hashtags (5, mid-tier)

**Routing rules — hardcoded:**

| Niche | Account | Format |
|-------|---------|--------|
| data_science_tech | @breathofdatascience | tutorial-clip + smart-crop |
| life_self_dev | @mistakenlyhuman | talking-head |
| poetry_quotes | @mistakenlyhuman | spoken-word over hyperframe |

**Hook principle:** Every hook must contain a specific number, result, or named moment — not a vague promise. Claude enforces this in the prompt. If a hook feels generic, regenerate with `--no-cache` or rewrite manually before posting.

---

## Step 6a — Hook validation checkpoint (~5 min, MANDATORY before Friday)

Open each `ig_reel_brief.md` that was just generated. For each of the 3 hook options listed, run this test:

**Does the hook contain a specific number, specific result, or named moment?**

- ✅ PASS examples: "Python gave me a perfectly confident wrong number — no error, no crash, I trusted it for a week." / "Break a bone and people hold the door for you. Tell someone you haven't slept in 3 weeks — the room goes quiet."
- ❌ FAIL examples: "This is a really important topic." / "I learned something surprising about Python." / "Mental health is something we don't talk about enough."

**If a hook fails:** Do NOT post it as-is. Rewrite it manually in the `ig_reel_brief.md` file before Friday. Use the `[SHAREABLE_MOMENT]` line you identified on Tuesday as the raw material. The hook must name the exact incident, number, or sensation.

```bash
# Spot-check all 3 briefs:
for brief in content/derivatives/{week}/*/ig_reel_brief.md; do
  echo "=== $brief ==="
  head -30 "$brief" | grep -A2 "## Hooks"
  echo ""
done
```

Go through each hook, ask yourself: *"Would I stop scrolling for this?"* If no → rewrite it. This step directly determines whether the reel gets distributed beyond your followers.

---

## Step 6b — Series compounding check — DS only (~2 min)

Open the DS edit plan: `remotion/public/edit-plans/{week}/{ds_slug}.json`

Check the `outroCard` section — it should reference the next DS piece topic:

```json
"outroCard": {
  "nextText": "Next week: [1-sentence tease of next DS topic]",
  "durationFrames": 150
}
```

If `nextText` is generic ("More on Breath of Data Science") or blank → update it now:

```bash
# Open the edit plan and update the nextText field manually
code remotion/public/edit-plans/{week}/{ds_slug}.json
```

Change `nextText` to the specific next-week tease you wrote in the Tuesday script. Example: `"Next week: the pandas merge bug that corrupted 6 months of production data silently."`

Why this matters: the outro tease runs in the last 5 seconds of the YouTube video. It creates a pre-warmed audience that expects the next piece. Combined with the `[OUTRO TEASE]` you scripted on Tuesday, this is the series compounding mechanism. Skip it → viewers don't know to come back. Do it → repeat viewers who DM you before you even post.

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

### Shorts overlay (augment the clips cut by `clip_shorts.py`)

Run AFTER `clip_shorts.py` (see the per-niche thursday guides). `--shorts` globs every clip in `assets/video/edited/shorts/{slug}_short_*.mp4` and overlays each:

```bash
python3 scripts/hyperframes_render.py \
  --shorts \
  --slug {slug}
# {slug} must match the clip_shorts prefix, e.g. {ds_slug} / {life_slug} / {poetry_slug}
# Output: augmented MP4s in assets/hyperframes/. Portrait clips auto re-encode.
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

## Step 6c — Upload shorts

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

## Step 8 — Produce + upload podcasts (~15 min)

Life and Poetry YouTube videos double as podcast episodes. This step extracts audio, mixes in
low-volume BGM, uploads the MP3 to GitHub Releases, and pushes an RSS feed update. Spotify polls
the RSS feed and picks up new episodes automatically (within ~1hr).

**First time only** — create the public podcast-feed repo:
```bash
gh repo create tarunlnmiit/podcast-feed --public --description "Podcast RSS feeds"
# Then in GitHub → repo Settings → Pages → Source: main branch, / (root)
# Then in Spotify for Podcasters → Import podcast → paste RSS URLs:
#   https://tarunlnmiit.github.io/podcast-feed/life.xml
#   https://tarunlnmiit.github.io/podcast-feed/poetry.xml
```

### 8a — Episode title + description pre-flight (MANDATORY, ~5 min)

Before running the script, open `content/derivatives/{week}/{slug}/youtube_metadata.json`
for each Life and Poetry slug and verify the episode title and description pass the virality bar.
Spotify's #1 growth lever is completion rate — both fields directly determine it.

**Episode title must contain one of:**
- A specific incident or result — "I Called My Parents When I Was Drowning. They Gave Me a Budget."
- A specific counter-intuitive observation — "The More I 'Worked on Myself', the More I Lost Myself"
- A named emotional experience — "The Quiet Dread That Stays After the Deadline Passes"

**Anti-patterns to rewrite before running:**
- Vague topic labels: "Mental Health", "About Anxiety" → no tension, no reason to play
- Episode numbers alone: "Episode 14" → meaningless without context
- Question with an obvious answer: "Is Journaling Really Enough?" → skip

**Episode description is auto-generated from the YouTube description** by `format_podcast_description`.
It follows the virality formula: hook → emotional promise → Medium link → follow CTA.
Spotify shows only the first 1–2 sentences in search previews — the hook must land cold.

If the YouTube description doesn't have a strong opening paragraph, rewrite the first paragraph in
`youtube_metadata.json` before running — the script picks it up automatically.

**Cross-promo CTAs to verify are in the YouTube description** (auto-inherited by podcast):
- Medium link: `medium.com/@tarun-gupta/{slug}` — so the script can inject "Full piece: …"
- These are auto-added by `produce_blog.py` → check they're present if description came from buffer

### 8b — Produce + publish

**Every week:**
```bash
python3 scripts/produce_podcast.py --week 2026-W{nn}
# Runs both Life + Poetry
```

Or one niche at a time:
```bash
python3 scripts/produce_podcast.py --week 2026-W{nn} --niche life
python3 scripts/produce_podcast.py --week 2026-W{nn} --niche poetry
```

Audio-only (skip RSS publish):
```bash
python3 scripts/produce_podcast.py --week 2026-W{nn} --no-upload
```

**Outputs:**
- `assets/audio/{week}/{slug}_podcast.mp3` — final episode with BGM
- `data/podcast/rss/{niche}.xml` — updated RSS feed (pushed to GitHub Pages)
- `content/derivatives/{week}/{slug}/{slug}_podcast_shownotes.md` — show notes

**Requirements:**
- `gh` CLI authenticated (`gh auth status`)
- `tarunlnmiit/podcast-feed` public GitHub repo exists
- BGM tracks in `assets/audio/bgm/` — run `python3 scripts/download_bgm.py` once if empty

### 8c — Post-publish cross-promo CTAs

After both episodes are live on Spotify, verify these CTAs are in place for the week:

| Channel | CTA to add |
|---------|------------|
| YouTube video description (Life) | "🎙️ Podcast version: open.spotify.com/show/26d2VlDaSD0bf6tucQucie" |
| YouTube video description (Poetry) | "🎙️ Podcast version: open.spotify.com/show/0d7GfbQsYPc4t0idLhpYWT" |
| Instagram Life reel caption | "Also a podcast on Spotify — follow Breath of Life" |
| Instagram Poetry reel caption | "Also a podcast on Spotify — follow Breath of Poetry" |
| Medium post (Life) | "Prefer listening? Available as a podcast on Spotify." |
| Medium post (Poetry) | "Prefer listening? Available as a podcast on Spotify." |

Podcast growth comes from YouTube and Instagram, not from within Spotify. These CTAs are the only reliable acquisition path.

---

## Step 9 — Verify + refresh tracker (~3 min)

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
