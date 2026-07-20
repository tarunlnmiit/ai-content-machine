---
title: "W22 Weekend Publishing Plan"
type: doc
slug: w22-weekend-publishing-plan
tags: [content/doc]
---
# W22 Weekend Publishing Plan
**Date:** June 20–22, 2026 (Sat/Sun)
**Goal:** Schedule and post W22 content (3 pieces, 3 reels) before Monday.

W22 content was produced but never scheduled. Everything needed exists — videos, blogs, derivatives, reel briefs. This is purely an execution checklist.

---

## What exists already

| Piece | Blog | Video | Reel Brief | Clips cut? |
|-------|------|-------|-----------|-----------|
| DS: Python Variables & Types | ✓ | ✓ `.mp4` + `.srt` | ✓ `ig_reel_brief.md` | Run command below |
| Life: Mental Health / Stigma | ✓ | ✓ `.mp4` | ✓ `ig_reel_brief.md` | Run command below |
| Poetry: Intoxicated Senses | ✓ | ✓ `.mp4` | ✓ `ig_reel_brief.md` | Use video as-is |

---

## Step 1 — Cut Instagram Reels from W22 videos (~10 min)

```bash
cd "/Users/tarungupta/Making It Big/Claude/content-machine"

# DS: Python tutorial — uses existing SRT for smart clip selection
python3 scripts/clip_shorts.py \
  --slug 2026-05-25_data_science_tech_python-for-data-science-tutorial-210 \
  --count 3 \
  --smart-crop

# Life: Mental health video
python3 scripts/clip_shorts.py \
  --slug 2026-05-29_2026-05-26-life-self-dev-mental-health-openness-and-breaking \
  --count 3

# Poetry: Use existing video directly (no clipping needed)
# Source: assets/video/edited/2026-W22/2026-05-29_2026-05-27-poetry-quotes-intoxicated-senses_yt.mp4
python3 scripts/create_vertical_reels.py \
  --slug 2026-05-29_2026-05-27-poetry-quotes-intoxicated-senses_yt \
  --start 0:00 \
  --duration 60
```

Clips will be at: `assets/video/edited/shorts/{slug}_short_00.mp4`

---

## Step 2 — Open reel briefs and pick hooks (~5 min)

Read each brief and confirm the hook. The hook must appear as:
1. The first words you hear in the video (spoken line — already in the edited file), AND
2. A `[TEXT_OVERLAY: shown at 0:00]` tag in the reel script (annotated on Tuesday)

```
content/derivatives/2026-W22/2026-05-25_data_science_tech_python-for-data-science-tutorial-210/ig_reel_brief.md
content/derivatives/2026-W22/2026-05-26_life_self_dev_mental-health-openness-and-breaking-stigmas/ig_reel_brief.md
content/derivatives/2026-W22/2026-05-27_poetry_quotes_intoxicated-senses/ig_reel_brief.md
```

**Recommended hooks for W22:**
- DS: *"Python gave me a perfectly confident wrong number. No error. No crash. I trusted it for a week."*
- Life: *"Break a bone and people hold the door for you. Tell someone you haven't slept in 3 weeks because your chest feels like it's caving in — the room goes quiet."*
- Poetry: *"There's a specific kind of madness that doesn't announce itself. One day you're fine."*

---

## Step 3 — Render reels with overlays via Remotion (~5 min per reel, automated)

Text overlays are rendered automatically — no manual editing tool needed. Remotion reads the `[TEXT_OVERLAY]` tags from the script and bakes them onto the vertical clip.

```bash
# Generate overlay scene plans (if not done on Tuesday)
python3 scripts/generate_scene_plans.py \
  --script content/scripts/2026-W22/2026-05-25_data_science_tech_python-for-data-science-tutorial-210_reel.md \
  --niche ds --week 2026-W22 --mode overlay

python3 scripts/generate_scene_plans.py \
  --script content/scripts/2026-W22/2026-05-26_life_self_dev_mental-health-openness-and-breaking-stigmas_reel.md \
  --niche life --week 2026-W22 --mode overlay

python3 scripts/generate_scene_plans.py \
  --script content/scripts/2026-W22/2026-05-27_poetry_quotes_intoxicated-senses_reel.md \
  --niche poetry --week 2026-W22 --mode overlay

# Render shorts. There is NO VerticalReel composition — pick a format per piece:
# Path A — clip-based vertical reels (already produced for W22):
#   assets/video/edited/shorts/2026-W22/{slug}_short_NN.mp4
# Path B — Remotion motion shorts (needs shorts_manifest.json per slug):
python3 scripts/render_shorts_batch.py --week 2026-W22 --niche ds      # then life, poetry
#   → output/animations/2026-W22/{slug}_s{NN}.mp4
```

Output: `assets/video/edited/shorts/2026-W22/` (Path A) or `output/animations/2026-W22/*_s*.mp4` (Path B) — ready to post.

**Trending audio:** Add natively in the Instagram app at post time (Audio button during Reel posting, 10–20% volume). Do not bake into the file.

---

## Step 4 — Post reels on Instagram (~15 min)

Post in this order and on these days:

| Reel | Account | Post Day | Time IST |
|------|---------|---------|---------|
| Life: Mental Health | @mistakenlyhuman | **Saturday June 20** | 7:00 PM |
| DS: Python Variables | @breathofdatascience | **Sunday June 21** | 8:00 AM |
| Poetry: Intoxicated Senses | @mistakenlyhuman | **Sunday June 21** | 8:00 PM |

For each reel:
1. Instagram → + → Reel
2. Select the exported clip
3. Paste caption from `ig_reel_brief.md` (it's ready to go)
4. Cover image: pick a frame with the hook text visible
5. Post (don't schedule — post manually for W22 since it's already delayed)

---

## Step 5 — Set DM keywords in SuperProfile (~5 min)

Three keywords to add:
- `TYPES` → link to DS blog: https://medium.com/@tarun-gupta/python-for-data-science-tutorial-2
- `STIGMA` → link to Life blog: https://medium.com/@tarun-gupta/the-lie-we-inherited-about-strength
- `POEM` → link to Poetry Substack: https://breathofpoetry.substack.com/

*(Update with actual published URLs once blogs are live on Medium/Substack)*

---

## Step 6 — Blog publishing (if not already done)

If W22 blogs haven't been published on Medium/Substack yet:

```bash
# Check status
python3 scripts/list_week_content.py 2026-W22

# Publish to Medium
python3 scripts/publish_medium.py --slug 2026-05-25_data_science_tech_python-for-data-science-tutorial-210 --week 2026-W22
python3 scripts/publish_medium.py --slug 2026-05-26_life_self_dev_mental-health-openness-and-breaking-stigmas --week 2026-W22

# Poetry → Substack (publish manually via breathofpoetry.substack.com)
```

---

## Step 7 — Post static posts manually (if not yet done)

Distribution is **manual** now (no Metricool/Publer CSV). For each W22 slug, post the static
content by hand in its window:

- **Instagram + Facebook:** `content/derivatives/2026-W22/{slug}/instagram_caption.txt` + the image at `assets/social_posts/2026-W22/{slug}_instagram.png`
- **Threads:** `content/derivatives/2026-W22/{slug}/threads_post.txt`

Optionally stage LinkedIn into the scheduler DB (held manual until clearance):
```bash
python3 scripts/load_posts.py --week 2026-W22
```

---

## Time estimate

| Step | Time |
|------|------|
| Cut clips (3 scripts) | 10 min |
| Review briefs, pick hooks | 5 min |
| Remotion render — 3 reels (automated, overlays baked in) | 5 min |
| Post on Instagram | 15 min |
| DM keyword setup | 5 min |
| Blog publish (if needed) | 15 min |
| Post static posts manually (IG/FB/Threads) | 10 min |
| **Total** | **~105 min** |

---

## What to skip this weekend

- YouTube upload for W22 — these videos were for a past week. Skip YouTube; just post the reels and blogs.
- New content creation — W25 is paused, use this weekend entirely for W22 catch-up.
- Generating briefs with the script — already done manually for W22. The script runs automatically from W23 onwards as part of Thursday Step 6.
