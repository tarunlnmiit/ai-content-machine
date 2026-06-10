# Weekly Operating Guide

Last updated: 2026-06-10

## Production Workflow (task-batched)

| Day | Task | Niches | Guide |
|-----|------|--------|-------|
| [Monday](monday.md) | Generate all blogs + repurpose → derivatives | DS + Life + Poetry | ~45 min |
| [Tuesday](tuesday.md) | Video scripts + social visual assets + scene plans + worksheets | DS + Life + Poetry | ~45 min |
| [Wednesday](wednesday.md) | Publish blogs (Substack + Medium) + shoot videos + generate captions + build edit plans | DS + Life + Poetry | ~3 hrs |
| [Thursday](thursday.md) | Render (Remotion) + optional HyperFrames + upload + Notion sync + verify | DS + Life + Poetry | ~3 hrs |
| [Friday](friday.md) | Schedule social (THIS week → posts NEXT week) + buffer check + refresh tracker | DS + Life + Poetry | ~45 min |
| [Saturday](saturday.md) | **Free** — catchup only if something slipped | — | — |
| [Sunday](sunday.md) | Read analytics + KB + sync ideas (~15 min) | — | ~15 min |

**Audit tool:**
```bash
python3 scripts/list_week_content.py 2026-W{nn}         # content + asset status
python3 scripts/list_week_content.py 2026-W{nn} --plan  # Mon-Fri production checklist
```

---

## Render Pipeline Overview

```
Raw footage (assets/raw/{week}/)
    │
    ▼ [Wednesday] generate_captions.py → Whisper
remotion/public/captions/{week}/{slug}.json
    │
    ▼ [Wednesday] prepare_remotion_edit.py
remotion/public/edit-plans/{week}/{slug}.json
    │
    ▼ [Thursday] render_week.py → npx remotion render CourseLesson
output/animations/{week}/{slug}.mp4          ← PRIMARY output
    │
    ├── [Thursday, optional] hyperframes_render.py
    │   assets/hyperframes/{date}_{slug}-aug.mp4  ← HyperFrames augmented
    │
    ├── [Thursday] render_shorts_batch.py
    │   output/animations/{week}/{slug}_s{slot:02d}.mp4  ← up to 14 shorts/niche
    │
    └── [Thursday] upload_youtube.py → YouTube
        @breathofdatascience / @breathoflife_ / @breathofpoetry
```

---

## Posting Times at a Glance (IST)

### Week N — Long-form + Blog (Substack · Medium · YouTube)

| Day | Time IST | Niche | Platform(s) | Content type |
|-----|----------|-------|-------------|--------------|
| Wed | 2:00 PM  | 🟢 Life   | Substack · Medium | Blog upload |
| Wed | 2:00 PM  | 🔵 DS     | Substack · Medium | Blog upload |
| Wed | 2:00 PM  | 🟣 Poetry | Substack · Medium | Blog upload |
| Thu | 6:00 PM  | 🟢 Life   | YouTube | Long-form video upload |
| Thu | 6:00 PM  | 🔵 DS     | YouTube | Long-form video upload |
| Thu | 6:00 PM  | 🟣 Poetry | YouTube | Long-form video upload |

### Week N+1 — Social (one week after long-form)

> **Pivot rule:** IG, Facebook, Threads, Twitter threads all publish the week AFTER the long-form goes live. LinkedIn is the only exception — it goes same week (auto via scheduler.py).

| Day | Time IST | Niche | Platform(s) | Content type |
|-----|----------|-------|-------------|--------------|
| Tue | 8:00 AM  | 🟢 Life   | LinkedIn *(auto — scheduler.py)* | LinkedIn post |
| Tue | 8:00 AM  | 🔵 DS     | LinkedIn *(auto — scheduler.py)* | LinkedIn post |
| Tue | 8:00 AM  | 🟣 Poetry | LinkedIn *(auto — scheduler.py)* | LinkedIn post |
| Mon | 1:00 PM  | 🟢 Life   | Twitter/X *(manual — reminder set)* | Twitter thread |
| Tue | 8:00 AM  | 🟢 Life   | Instagram · Facebook *(Metricool CSV)* | IG carousel |
| Tue | 8:00 PM  | 🟢 Life   | Threads *(Metricool CSV)* | Threads post |
| Wed | 8:00 AM  | 🔵 DS     | Instagram · Facebook *(Metricool CSV)* | IG carousel |
| Wed | 8:00 PM  | 🔵 DS     | Threads *(Metricool CSV)* | Threads post |
| Fri | 10:00 AM | 🟣 Poetry | Instagram · Facebook *(Metricool CSV)* | IG carousel |
| Fri | 12:00 PM | 🟣 Poetry | Twitter/X *(manual — reminder set)* | Twitter thread |
| Fri | 12:00 PM | 🟣 Poetry | Threads *(Metricool CSV)* | Threads post |

### YouTube Shorts — 2/day all niches (Mon–Sun)

| Slot | Day | Time IST | Phase |
|------|-----|----------|-------|
| short_00 | Mon | 10 AM | Tease |
| short_01 | Mon | 8 PM | Tease |
| short_02 | Tue | 10 AM | Tease |
| short_03 | Tue | 8 PM | **Life ★** post-long-form · DS/Poetry tease |
| short_04 | Wed | 10 AM | Life post-long-form · DS/Poetry tease |
| short_05 | Wed | 8 PM | Life post-long-form · DS/Poetry tease |
| short_06 | Thu | 10 AM | Life post-long-form · DS/Poetry tease |
| short_07 | Thu | **9 PM** | Life post-long-form · **DS ★** post-long-form · Poetry tease |
| short_08 | Fri | 10 AM | DS post-long-form · Poetry tease |
| short_09 | Fri | 8 PM | DS post-long-form · **Poetry ★** post-long-form |
| short_10 | Sat | 10 AM | All post-long-form |
| short_11 | Sat | 8 PM | All post-long-form |
| short_12 | Sun | 10 AM | All post-long-form |
| short_13 | Sun | 8 PM | All post-long-form |

★ = first slot after that niche's long-form goes live. Add live video URL to descriptions from ★ onward.

> Dashboard: **🗓️ Posting Schedule** page shows this with actual dates for the current week.

---

### Same-Week Derivatives Rule

**All derivatives from any content piece — including ALL shorts (up to 14 per niche) — must publish in the same Mon–Sun week as the long-form video. No content carries over to the following week.**

#### Shorts cadence: 2 per day per channel × 7 days = 14 max

Each channel has two daily short slots: **10 AM IST** and **8 PM IST**.  
Upload whichever slots have shorts available; leave empty slots unfilled.

Standard slot assignment per niche (short_00 → slot 0, short_01 → slot 1, etc.):

| Slot | Day | Time IST | Notes |
|------|-----|----------|-------|
| 0 | Mon | 10 AM | Tease (long-form not yet live) |
| 1 | Mon | 8 PM | Tease |
| 2 | Tue | 10 AM | Tease |
| 3 | Tue | 8 PM | Tease |
| 4 | Wed | 10 AM | Tease |
| 5 | Wed | 8 PM | Tease |
| 6 | Thu | 10 AM | Tease (Life: post-long-form) |
| 7 | Thu | 9 PM | Post-long-form (DS: same evening) |
| 8 | Fri | 10 AM | Post-long-form |
| 9 | Fri | 8 PM | Post-long-form |
| 10 | Sat | 10 AM | Post-long-form |
| 11 | Sat | 8 PM | Post-long-form |
| 12 | Sun | 10 AM | Post-long-form |
| 13 | Sun | 8 PM | Post-long-form |

Shorts before the long-form are standalone teasers — no parent-video link required by YouTube. Shorts posted after the long-form should have the video URL in their description (update retroactively if needed).

#### Per-niche publishing order (enforce every week)

1. **Social first** (LinkedIn + Twitter) — prior day or same morning. Drives anticipation, no link needed.
2. **IG carousel** — 1 day before the long-form (8 AM slot). Teaser visual, no link needed.
3. **Long-form video + Blog** — simultaneous publish (Substack → Medium canonical).
   Medium tags (max 5, use `--tags` flag):
   - Life/Self-dev: `self-improvement,personal-development,habits,productivity,mindset`
   - Data Science:  `python,data-science,machine-learning,tutorial,programming`
   - Poetry/Quotes: `poetry,love,writing,quotes,literature`
4. **Shorts** — 2/day, Mon–Sun, all within same calendar week.

Niche windows:
- **Life** → Mon social · Tue IG + long-form + blog + newsletter · Mon–Sun shorts (slots 0–13)
- **DS** → Wed social · Wed IG + Thu long-form + blog + newsletter · Mon–Sun shorts (slots 0–13)
- **Poetry** → Fri social + long-form + blog + newsletter · Mon–Sun shorts (slots 0–13)

---

## Content Buffer

A rolling 4-week buffer of ready-to-publish content protects output during travel, illness, or low-energy weeks.

**Buffer structure:**
```
content/buffer/
  week-1/
    data_science_tech/   ← youtube_script + substack_post + social_copy + meta
    life_self_dev/
    poetry_quotes/
  week-2/ … week-4/

data/buffer/topics.yaml  ← source of truth: all 12 topic slots + angles
```

**Buffer depth check (run any time):**
```bash
for niche in data_science_tech life_self_dev poetry_quotes; do
  count=$(ls content/buffer/week-*/${niche}/*_meta.md 2>/dev/null | wc -l | tr -d ' ')
  echo "$niche: $count weeks buffered"
done
```
**MINIMUM: 4 weeks per niche at all times (12 total).** Replenish on Friday (end of production week) before it ever drops to 3.

**Replenish buffer (Friday Step 6):**
```bash
# 1. Open data/buffer/topics.yaml — fill empty week slots with topic + angle
#    (check Notion Published items first to avoid repeat angles)
# 2. Generate content for new slots:
conda run -n content_engine_env python3 scripts/generate_buffer.py
# Targeted:
conda run -n content_engine_env python3 scripts/generate_buffer.py --week 4
conda run -n content_engine_env python3 scripts/generate_buffer.py --niche ds
```

Generation uses **AutoTune temps** (DS=0.4, Life=0.85, Poetry=1.15) + **STM normalization** (strips filler/hedges) automatically.
Models: DS → `claude-opus-4-7` · Life + Poetry → `claude-sonnet-4-6` (set in `data/brand/brand_kit.yaml`).

**Push produced content into buffer (after a live production week):**
```bash
# Preview what will be copied
python3 scripts/push_to_buffer.py --niche ds --week 2 --dry-run

# Push all 3 niches into week-2 slot (use --date YYYY-MM-DD to target specific production date)
python3 scripts/push_to_buffer.py --niche ds     --week 2 --date 2026-05-21
python3 scripts/push_to_buffer.py --niche life   --week 2 --date 2026-05-21
python3 scripts/push_to_buffer.py --niche poetry --week 2 --date 2026-05-21
# Copies: blog → substack_post · YT script → youtube_script · derivatives → social_copy
```

**Consume from buffer (when skipping live production):**
- Open `content/buffer/week-1/{niche}/` → use `_substack_post.md`, `_youtube_script.md`, `_social_copy.md`
- After publishing: delete that week's niche folder → shift remaining weeks down → add new week-4 slot
- Log consumed items in Notion: status `Script` → `Published`

**Shift buffer after consuming:**
```bash
bash scripts/shift_buffer.sh --dry-run   # verify week-4 has content
bash scripts/shift_buffer.sh             # rotate: week-2→1, week-3→2, week-4→3
# Then fill week-4 in data/buffer/topics.yaml and regenerate:
conda run -n content_engine_env python3 scripts/generate_buffer.py --week 4
```

**Buffer vs. live production:**
- Normal week: produce fresh content via daily guides → buffer untouched
- Busy/travel week: pull from buffer → no production required
- **Rule: buffer is the floor. Never post from week-1 without immediately scheduling week-4 generation.**

---

## Alternative: Sunday Batch Mode

Free Sunday? Skip daily grind. Use **[Sunday Batch Playbook](sunday-batch.md)** — produce full week's content in one 3–4 hour sitting, then hands-off Mon–Sat.

- Use when: full Sunday available + energy high
- Skip when: busy, tired, traveling — daily guides above still work
- Saturday = sabbath day (no content work) when batch done
- Partial batch fallback (2 hours, 1 niche) inside the playbook

---

## Setup (one-time)

### Core dependencies

```bash
# Python packages
pip install openai-whisper nltk anthropic python-dotenv

# ffmpeg (required for Whisper + caption generation)
brew install ffmpeg

# Whisper
pip install openai-whisper
```

### Remotion (video rendering)

```bash
# Install
cd remotion && npm install

# Start Remotion Studio (visual preview):
cd remotion && npm run dev
# → http://localhost:3000

# Compositions available:
# CourseLesson    — long-form talking head (1920×1080)
# ShortClip       — portrait crop of long-form (1080×1920)
# DSMotionShort   — pure DS motion short (1080×1920)
# LifeMotionShort — pure Life motion short (1080×1920)
# PoetryMotionShort — pure Poetry motion short (1080×1920)
# Thumbnail       — YouTube thumbnail still export (1280×720)
# AudiogramFeed   — podcast audiogram 1080×1080
# AudiogramStory  — podcast audiogram 1080×1920
# SocialCard1x1   — animated social card 1080×1080
# SocialCard9x16  — animated social card 1080×1920
# AbstractDS/Life/Poetry — b-roll loops (render once, reuse)

# Render a single composition:
cd remotion
npx remotion render CourseLesson output/animations/{week}/{slug}.mp4 \
  --props='{"editPlanFile":"edit-plans/{week}/{slug}.json"}'

# Render still (thumbnail):
npx remotion still Thumbnail output/visuals/{week}/{slug}_thumb.png \
  --props='{"titleText":"Title","niche":"ds","variant":"a","bgType":"dark"}'
```

### HyperFrames (optional visual overlay system)

```bash
# Install HyperFrames dependencies (one-time):
pip install -r scripts/hyperframes_requirements.txt

# Verify:
python3 scripts/hyperframes_render.py --help

# Usage (run AFTER Remotion render, same day — Thursday):
python3 scripts/hyperframes_render.py output/animations/{week}/{slug}.mp4 \
  --slug {slug}-aug
# → assets/hyperframes/{date}_{slug}-aug.mp4
```

HyperFrames applies Claude-powered glass card, code callout, stat card, and flow arrow overlays on top of any MP4. Primarily useful for DS content. Run Thursday after render, before upload. See `docs/video-production-guide.md` → HyperFrames section.

### Remotion source structure

```
remotion/
  src/
    styles/
      chronixel.ts          # design tokens: colors (#0a0a0f bg), fonts (Poppins ExtraBold), niche palettes
      niche.ts              # per-niche accent: DS #f97316, Life #f59e0b, Poetry #a78bfa
    compositions/
      TitleCard.tsx          # Chronixel title card (inject at frame 0)
      LowerThird.tsx         # Lower-third nameplate
      OutroCard.tsx          # Subscribe outro with niche CTA
      CaptionPage.tsx        # TikTok-style captions with word pop
      TalkingHeadEdit.tsx    # Main long-form assembly (wire-in all above)
      ShortClip.tsx          # 9:16 portrait crop + big captions
      DSMotionShort.tsx      # Pure DS motion short (loads scene-plan JSON)
      LifeMotionShort.tsx    # Pure Life motion short
      PoetryMotionShort.tsx  # Pure Poetry motion short
      Audiogram.tsx          # Podcast waveform + quote
      SocialCard.tsx         # Animated social card
      Thumbnail.tsx          # Programmatic YouTube thumbnail
      AbstractDS.tsx         # DS b-roll loop (particle network, data stream)
      AbstractLife.tsx       # Life b-roll loop (bokeh, organic)
      AbstractPoetry.tsx     # Poetry b-roll loop (ink-water, aurora)
      scenes/
        WordReveal.tsx
        AtmosphericQuote.tsx
        NumberedTips.tsx
        DataVizReveal.tsx
        CodeAnnotation.tsx
        ConceptExplainer.tsx
        ToolComparison.tsx
        TransformationArc.tsx
        HabitLoop.tsx
        LineReveal.tsx
    types.ts                 # EditPlan, ScenePlan, AudiogramPlan types
    Root.tsx                 # All compositions registered here
  public/
    edit-plans/
      {week}/                # *.json EditPlan files per slug
    captions/
      {week}/                # *.json Caption[] per slug (from Whisper)
    scene-plans/
      {week}/                # *.json ScenePlan[] for motion shorts
    broll/
      {week}/                # B-roll clips per week
    videos/
      {week}/                # Source videos (moved here from assets/raw)
    audio/
      {week}/                # Audio clips for audiograms
```

### Scheduler daemon

```bash
# Start (survives shell close):
nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &

# Or via launchd (preferred — survives reboots):
launchctl load ~/Library/LaunchAgents/com.contentmachine.scheduler.plist
launchctl list | grep contentmachine

# Check activity:
tail -20 data/analytics/scheduler.log
sqlite3 data/scheduling.db "SELECT COUNT(*) FROM posts WHERE status='pending'"
```

LinkedIn tokens expire every 60 days. Refresh: `python3 scripts/auth_linkedin.py --refresh`

---

## Build Status

| Day | Focus | Status |
|-----|-------|--------|
| Day 1 | Foundation — folder, CLAUDE.md, MCPs | ✅ Done |
| Day 2 | Research + KB pipeline | ✅ Done |
| Day 3 | Writing + Repurposing agents | ✅ Done |
| Day 3b | Ghostwriter agent | ✅ Done (`ghostwrite.py` + `ghostwriter_agent.md`) |
| Day 4 | Claude Design pipeline | ✅ Done — `generate_design_prompts.py` + `claude_design_agent.md` |
| Day 5 | Distribution automation | ⚠️ Scripts done — scheduler not running, DB empty |
| Day 6 | First full production run | ⚠️ Blogs + derivatives exist, no posts loaded, no videos |
| Day 7 | SOP + analytics | ⚠️ `collect_analytics.py` done — Streamlit dashboard not built |
| Day 8 | Remotion video pipeline | ✅ Done — 25 compositions + 10 scene components + render scripts |

**Remaining before fully automated:**
- Load current blogs: `python3 scripts/load_posts.py`
- Start APScheduler: `launchctl load ~/Library/LaunchAgents/com.contentmachine.scheduler.plist`
- Build Streamlit dashboard: `dashboard/app.py` (not yet created)
- Get Twitter archive → build `data/kb/twitter_hook_patterns.json`

---

## What runs automatically

| Time | What |
|------|------|
| Every day 6am | `scripts/daily_ideas.sh` chains Reddit + YouTube + external feeds + Google/YouTube suggest + idea scorer → `data/ideas/weekly_ideas.md`. Install: see [launchd-daily-ideas.md](launchd-daily-ideas.md) |
| Sunday 8pm | `collect_analytics.py` → `data/analytics/weekly_insights.md` |
| Sunday 10pm | `build_knowledge_base.py` → `data/kb/master_brief.md` (`com.contentmachine.buildkb` installed) |
| Continuous | `scripts/scheduler.py` → fires pending posts from `data/scheduling.db` every 60s. Managed by launchd (`com.contentmachine.scheduler`, KeepAlive + RunAtLoad). |

> Check scheduler: `launchctl list | grep contentmachine` and `tail -20 data/analytics/scheduler.log`

---

## Notion sync

Push top ideas → Notion Contents DB as `Idea` rows. Full flow + write-back loop: [README.md → Notion Integration Flow](README.md#notion-integration-flow).

```bash
python3 scripts/sync_ideas_to_notion.py --dry-run   # preview
python3 scripts/sync_ideas_to_notion.py             # real sync (dedup by title)
```

After publishing any content, close the loop:
```bash
python3 scripts/update_notion_status.py --title "<substring>" --status Published --url <url>
```

Config: `NOTION_CONTENTS_DB_ID` + `NOTION_INTEGRATION_SECRET` in `.env`.

---

## Git hooks (optional)

Pre-commit graphify update — keeps knowledge graph fresh on every commit:

```bash
cp docs/pre-commit-graphify.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
# Skip on any commit: git commit --no-verify
# Uninstall:         rm .git/hooks/pre-commit
```

---

## File Naming Conventions

All scripts auto-name files. Know these patterns to find content manually.

**Slug** = topic title lowercased, spaces → hyphens, truncated ~50 chars.
**Week** = ISO week string: `YYYY-Wnn` (e.g., `2026-W24`). Get it:
```bash
python3 -c "from scripts.lib.schedule_calc import get_iso_week; print(get_iso_week('2026-06-10'))"
```
**Niche keys:** `data_science_tech` · `life_self_dev` · `poetry_quotes`

| File type | Pattern | Example |
|-----------|---------|---------|
| Blog | `content/blogs/{week}/YYYY-MM-DD_{niche}_{slug}.md` | `content/blogs/2026-W24/2026-06-10_data_science_tech_python-for-ml.md` |
| YT script | `content/scripts/{week}/YYYY-MM-DD_{niche-dashes}-{slug}_yt.md` | `2026-W24/2026-06-10_data-science-tech-python-for-ml_yt.md` |
| Derivatives dir | `content/derivatives/{week}/YYYY-MM-DD_{niche-dashes}_{slug-50}/` | `content/derivatives/2026-W24/2026-06-10_data_science_tech_python-for-ml/` |
| Social images | `assets/social_posts/{week}/{slug}_instagram.png` | `assets/social_posts/2026-W24/{slug}_instagram.png` |
| Edited video | `output/animations/{week}/{slug}.mp4` | `output/animations/2026-W24/{slug}.mp4` |
| Short clip | `output/animations/{week}/{slug}_s{slot:02d}.mp4` | `output/animations/2026-W24/{slug}_s00.mp4` |
| Thumbnail | `output/visuals/{week}/{slug}_thumb_a.png` | `output/visuals/2026-W24/{slug}_thumb_a.png` |
| HyperFrames output | `assets/hyperframes/{date}_{slug}-aug.mp4` | `assets/hyperframes/2026-06-10_{slug}-aug.mp4` |
| Edit plan | `remotion/public/edit-plans/{week}/{slug}.json` | `remotion/public/edit-plans/2026-W24/{slug}.json` |
| Captions | `remotion/public/captions/{week}/{slug}.json` | `remotion/public/captions/2026-W24/{slug}.json` |
| Scene plan | `remotion/public/scene-plans/{week}/{slug}_s{slot}.json` | `remotion/public/scene-plans/2026-W24/{slug}_s01.json` |
| Shorts manifest | `content/derivatives/{week}/{slug}/shorts_manifest.json` | — |
| Buffer blog | `content/buffer/week-N/{niche}/{slug}_substack_post.md` | `content/buffer/week-2/data_science_tech/python-for-ml_substack_post.md` |
| Buffer script | `content/buffer/week-N/{niche}/{slug}_youtube_script.md` | same dir, `_youtube_script.md` |
| Metricool CSV | `output/scheduled/metricool_{brand}.csv` | `output/scheduled/metricool_breathofds.csv` |

**After producing content, run:**
```bash
python3 scripts/push_to_buffer.py --auto              # checks all 3 niches, auto-decides
python3 scripts/push_to_buffer.py --auto --niche ds   # single niche
python3 scripts/push_to_buffer.py --auto --dry-run    # preview first
```
If buffer < 4 weeks → copies into next empty slot. If buffer full → prints "stays live".

---

## Key Files

```
data/brand/brand_kit.yaml          ← brand colors, fonts, tones, AutoTune temps + models
data/buffer/topics.yaml            ← 4-week buffer topic slots (fill + generate Sunday)
data/ideas/weekly_ideas.md         ← Monday topic picking
data/kb/master_brief.md            ← read before every writing session
data/poems/                        ← POETRY: one poem per file ({slug}.txt)
data/scheduling.db                 ← post queue (LinkedIn auto-post via scheduler.py)
data/analytics/scheduler.log      ← APScheduler activity
data/content_tracker.csv          ← content pipeline status (run scripts/sync_tracker.py to refresh)

content/blogs/{week}/              ← finished blogs (grouped by ISO week)
content/scripts/{week}/            ← YT scripts + production guides
content/derivatives/{week}/        ← 10 derivative files per slug + schedule.json
content/buffer/                    ← 4-week rolling content buffer

remotion/src/styles/chronixel.ts   ← Chronixel design system tokens
remotion/src/Root.tsx              ← all Remotion compositions registered here
remotion/public/edit-plans/{week}/ ← EditPlan JSONs driving CourseLesson renders
remotion/public/captions/{week}/   ← Whisper caption JSONs
remotion/public/scene-plans/{week}/← ScenePlan JSONs for motion shorts

output/animations/{week}/          ← rendered MP4s (long-form + shorts)
output/visuals/{week}/             ← thumbnails + cover images
output/scheduled/
  metricool_breathofds.csv         ← DS brand Metricool import (@breathofdatascience)
  metricool_mistakenlyhuman.csv    ← Life+Poetry brand Metricool import (@mistakenlyhuman)
  upload_shorts.sh                 ← pre-filled YouTube Shorts upload commands

assets/raw/{week}/                 ← original camera recordings + screen recordings
assets/hyperframes/                ← HyperFrames augmented MP4s
assets/social_posts/{week}/        ← platform-specific social images
assets/slides/{week}/              ← slide decks + PDFs + per-slide PNG exports
assets/carousels/{week}/           ← Instagram carousel HTML + slide PNGs
```

---

## Load posts: schedule.json + blog URLs + images

`load_posts.py` now:
1. Checks for `schedule.json` in each slug dir — uses timestamps if present
2. Falls back to `next_weekday()` computation if absent (backwards compat)
3. **Blog URL lookup** — searches `medium_posts.json` for Medium links, appends to captions
   - If found in `medium_posts.json`, auto-injected into caption text as "Full post 👉 {url}"
   - If not found, prompts user (interactive mode only) to enter Medium URL, saves to `schedule.json`
   - If user skips, caption posts without link
4. **Image URL lookup** — detects local Instagram images, prompts for public CDN URLs
   - Checks `assets/social_posts/{week}/{slug}_instagram.png`
   - If local image exists but no URL in `schedule.json`, prompts user for public URL (Google Drive/Dropbox)
   - Saves entered URL to `schedule.json`, injects into Metricool CSV `Picture Url 1` field
   - If user skips, IG/FB posts without image (Metricool will flag error — manual image upload needed)
5. Result: idempotent — re-running `load_posts.py` skips all prompts (reads from saved `schedule.json`)

---

## Fallback: Canva path (if Claude Design unavailable)

```bash
python3 scripts/generate_canva_prompts_legacy.py   # Canva AI 2.0 prompts
python3 scripts/generate_slides.py                  # → output/scheduled/{slug}_slides.csv
python3 scripts/generate_quote_cards.py             # → output/scheduled/quote_cards.csv
python3 scripts/generate_canva_prompts.py           # → output/scheduled/canva_prompts.md (thumbnails)
```

---

## Schedule embedded in content

**Each generated piece of content carries its own schedule.json.**

When you run `produce_blog.py`, `repurpose_blog.py`, or generate shorts metadata, the scripts automatically compute and write `content/derivatives/{slug}/schedule.json` — no manual timestamp management needed.

### Inspecting schedules

```bash
# See full schedule for a slug
python3 -m json.tool content/derivatives/{week}/{slug}/schedule.json

# Extract just publish times
jq '.social, .long_form.publish_at' content/derivatives/{week}/{slug}/schedule.json
```

### Auto-generating the weekly checklist

```bash
python3 scripts/generate_checklist.py --week 2026-06-09
# → docs/week-2026-06-09-publishing-checklist.md
```

---

## Still to build

| Item | What's needed |
|------|--------------|
| Streamlit dashboard | `dashboard/app.py` — not yet created |
| Twitter hook patterns | Request Twitter archive → extract → `data/kb/twitter_hook_patterns.json` |
| LinkedIn OAuth refresh | Tokens expire 60 days — rerun `scripts/auth_linkedin.py --refresh` when needed |
| Worksheet automation | `scripts/auto_worksheet_workflow.py` — worksheet gen + Claude Design prompt in one call |
