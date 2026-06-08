# Weekly Operating Guide

Last updated: 2026-06-08

## Posting Times at a Glance (IST)

### Week N — Long-form + Blog (YouTube · Substack · Medium)

| Day | Time IST | Niche | Platform(s) | Content type |
|-----|----------|-------|-------------|--------------|
| Tue | 2:00 PM  | 🟢 Life   | YouTube · Substack · Medium | Long-form + Blog |
| Thu | 6:00 PM  | 🔵 DS     | YouTube · Substack · Medium | Long-form + Blog |
| Fri | 3:00 PM  | 🟣 Poetry | YouTube · Substack · Medium | Long-form + Blog |

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

## Week at a Glance

| Day | Focus | Time |
|-----|-------|------|
| [Monday](monday.md) | Life: LinkedIn + Twitter thread (social-first, no video yet) | ~15 min |
| [Tuesday](tuesday.md) | Life: IG carousel → Long-form video → Blog → Newsletter → Short(s) same day | ~2.5 hrs |
| [Wednesday](wednesday.md) | DS: LinkedIn + Twitter thread + IG carousel | ~20 min |
| [Thursday](thursday.md) | DS: Long-form video → Blog → Newsletter → Short(s) same evening | ~2 hrs |
| [Friday](friday.md) | Poetry: LinkedIn + Twitter → Long-form video → Blog → Newsletter → Short(s) same day | ~2.5 hrs |
| [Saturday](saturday.md) | Buffer replenishment + week review + Notion sync | ~1 hr |
| [Sunday](sunday.md) | Analytics review + generate week N+4 buffer slot | ~30 min |

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
**MINIMUM: 4 weeks per niche at all times (12 total).** Replenish on Sunday before it ever drops to 3.

**Replenish buffer (Sunday):**
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
# After using week-1 content across all 3 niches:
rm -rf content/buffer/week-1
mv content/buffer/week-2 content/buffer/week-1
mv content/buffer/week-3 content/buffer/week-2
mv content/buffer/week-4 content/buffer/week-3
# Update week numbers in data/buffer/topics.yaml
# Then fill week-4 and generate to restore 4-week depth
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

Install dependencies:
```bash
pip install openai-whisper nltk anthropic python-dotenv
```

Install ffmpeg + Whisper:
```bash
brew install ffmpeg
pip install openai-whisper
```

Remotion (video editing — already scaffolded in `remotion/`):
```bash
cd remotion && npm install
```

Primary editing pipeline: `scripts/prepare_remotion_edit.py` → Remotion Studio preview → `npx remotion render` — see `docs/video-production-guide.md`

Animation prompts: `scripts/generate_animation_prompts.py <script.md>` → `content/prompts/{slug}_animation_prompts.txt` — extracts `[ANIMATION:]` tags, writes Remotion component specs per tag. Add `--render` to render each animation directly to `output/animations/` MP4 using built-in brand templates.

Courses (separate product line, original content, Sonnet-backed): `scripts/draft_lesson_script.py` drafts a lesson script from `--title` + repeated `--point` + `--story`; `scripts/generate_course_worksheet.py` makes an original worksheet from `--topic` + `--objective`. Both route to `claude-sonnet-4-6`. Config + pricing in `data/courses/graphy_config.yaml`; full workflow in `docs/course-production-guide.md`.

DaVinci Resolve (optional, manual polish only):
- Free version sufficient for music/text overlays on rendered MP4

Start scheduler daemon:
```bash
nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &
```

**Claude Design (primary visual tool)**
Access: claude.ai → Design tab
Used Wednesday for: slide decks · Instagram story sequences · reel covers · social post sets (IG · LinkedIn · Twitter/X · Threads)

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

**Remaining before fully automated:**
- Load current blogs: `python3 scripts/load_posts.py`
- Start APScheduler (now managed by launchd): `launchctl load ~/Library/LaunchAgents/com.contentmachine.scheduler.plist`
- Build Streamlit dashboard: `dashboard/app.py` (not yet created)
- Get Twitter archive → build `data/kb/twitter_hook_patterns.json`

---

## What runs automatically

| Time | What |
|------|------|
| Every day 6am | `scripts/daily_ideas.sh` chains Reddit + YouTube + external feeds + Google/YouTube suggest + idea scorer → `data/ideas/weekly_ideas.md`. Install: see [launchd-daily-ideas.md](launchd-daily-ideas.md) |
| Sunday 8pm | `collect_analytics.py` → `data/analytics/weekly_insights.md` (plist not yet installed) |
| Sunday 10pm | `build_knowledge_base.py` → `data/kb/master_brief.md` (`com.contentmachine.buildkb` installed) |
| Continuous | `scripts/scheduler.py` → fires pending posts from `data/scheduling.db` every 60s. Managed by launchd (`com.contentmachine.scheduler`, KeepAlive + RunAtLoad). |

> Check scheduler: `launchctl list \| grep contentmachine` and `tail -20 data/analytics/scheduler.log`

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
**Niche keys:** `data_science_tech` · `life_self_dev` · `poetry_quotes`

| File type | Pattern | Example |
|-----------|---------|---------|
| Blog | `content/blogs/YYYY-MM-DD_{niche}_{slug}.md` | `2026-05-21_data_science_tech_python-for-ml.md` |
| YT script | `content/scripts/YYYY-MM-DD_{niche-dashes}-{slug}_yt.md` | `2026-05-22_data-science-tech-python-for-ml_yt.md` |
| Derivatives dir | `content/derivatives/YYYY-MM-DD-{niche-dashes}-{slug-50}/` | `content/derivatives/2026-05-21-data-science-tech-python-for-ml/` |
| Buffer blog | `content/buffer/week-N/{niche}/{slug}_substack_post.md` | `content/buffer/week-2/data_science_tech/python-for-ml_substack_post.md` |
| Buffer script | `content/buffer/week-N/{niche}/{slug}_youtube_script.md` | same dir, `_youtube_script.md` |
| Buffer social | `content/buffer/week-N/{niche}/{slug}_social_copy.md` | same dir, `_social_copy.md` |
| Raw video | `assets/raw/{slug}.mov` | `assets/raw/python-for-ml.mov` |
| Edited video | `assets/video/edited/{slug}.mp4` | `assets/video/edited/life_habits.mp4` |

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
data/brand/brand_kit.yaml                        ← brand colors, fonts, tones, AutoTune temps + models per niche (DS=Opus 4.7, rest=Sonnet 4.6)
data/buffer/topics.yaml                          ← 4-week buffer topic slots (fill + generate Sunday)
scripts/push_to_buffer.py                        ← auto-decide: buffer content or keep live (--auto flag)
data/ideas/weekly_ideas.md                       ← Monday topic picking
data/kb/master_brief.md                          ← read before every writing session
data/poems/                                      ← POETRY: one poem per file ({slug}.txt)

content/blogs/                                   ← finished blogs → YYYY-MM-DD_{niche}_{slug}.md
content/blogs/{stem}_images/                     ← downloaded images + IMAGE_MAP.md
content/scripts/
  ├── YYYY-MM-DD-{niche-dashes}-{slug}_yt.md     ← YouTube talking-head script ([BROLL:] = editor cutaway hints)
  ├── {slug}_PRODUCTION_GUIDE.md                 ← section → clip mapping + timing
  ├── {slug}_captions.srt                        ← Whisper captions (auto-burned by auto_edit.py)
  └── {slug}_poetry_overlay.srt                  ← POETRY ONLY: full poem SRT overlay

content/derivatives/{slug}/                      ← 10 files per blog
  ├── twitter_thread.txt
  ├── linkedin_post.txt
  ├── instagram_caption.txt
  ├── threads_post.txt
  ├── newsletter.txt
  ├── slide_outline.json
  ├── youtube_metadata.json
  ├── youtube_shorts_metadata.json
  ├── polls.json
  ├── thumbnail_brief.json
  └── claude_design_brief.json                   ← emotional core, key quotes, story frames

prompts/claude_design_agent.md                   ← Claude Design art direction system
output/scheduled/claude_design_prompts_{slug}.md ← 4 design prompts per blog (spec for the HTML below)
output/scheduled/validated_code_{slug}.json      ← DS tutorial: tested code blocks

assets/
  ├── slides/{slug}_slides.html                  ← Claude Design source: 9-slide deck (1920×1080)
  ├── slides/{slug}_story.html                   ← Claude Design source: 7-frame IG story (1080×1920)
  ├── slides/{slug}_social.html                  ← Claude Design source: 4 social variants
  ├── slides/{slug}_reel_cover.html              ← Claude Design source: 9:16 reel cover
  ├── slides/{slug}/slide_N.png                  ← deck PNGs 1920×1080 (export_html_deck.py)
  ├── slides/{slug}/{slug}_slides.pdf            ← deck PDF (export_html_deck.py --pdf)
  ├── slides/photos/{slug}_*.jpg                 ← stock photos filling story/reel image-slots
  ├── carousels/{slug}_carousel.html             ← Instagram carousel (swipeable HTML, export-ready)
  ├── carousels/slides/{slug}/slide_N.png        ← carousel PNGs 1080×1350 (generate_carousel.py --export)
  ├── stories/{slug}/{slug}_story.mp4            ← IG story video (export_story_animation.py)
  ├── stories/{slug}/{slug}_story_slide_NN.png   ← 7 story frames
  ├── social_posts/{slug}_instagram.png          ← 1080×1080  (export_html_deck.py)
  ├── social_posts/{slug}_linkedin.png           ← 1200×628
  ├── social_posts/{slug}_twitter.png            ← 1200×675
  ├── social_posts/{slug}_threads.png            ← 1080×1080
  ├── reels/{slug}_cover.png                     ← 9:16 reel cover (export_html_deck.py)
  ├── videos/{slug}/{slug}_raw.mp4               ← Life/Poetry: raw talking-head recording (iPhone)
  ├── videos/{slug}/                             ← B-roll clips + VIDEO_MAP.json
  ├── video/edited/{slug}.mp4                    ← long-form YouTube (FINAL)
  └── video/edited/{slug}_reel.mp4              ← YouTube Short / reel (FINAL, 9:16)

output/scheduled/publer_mistakenlyhuman_ig_fb.csv   ← Account 1 (mistakenlyhuman): Instagram + Facebook
output/scheduled/publer_mistakenlyhuman_threads.csv ← Account 1 (mistakenlyhuman): Threads
output/scheduled/publer_breathofds_ig_fb.csv        ← Account 2 (Breath of DS): Instagram + Facebook
output/scheduled/upload_shorts.sh               ← pre-filled YouTube Shorts upload commands
data/scheduling.db                              ← post queue
data/analytics/scheduler.log                   ← APScheduler activity
```

---

## Fallback Canva path (if Claude Design unavailable)

```bash
python3 scripts/generate_canva_prompts_legacy.py   # Canva AI 2.0 prompts
python3 scripts/generate_slides.py                  # → output/scheduled/{slug}_slides.csv
python3 scripts/generate_quote_cards.py             # → output/scheduled/quote_cards.csv
python3 scripts/generate_canva_prompts.py           # → output/scheduled/canva_prompts.md (thumbnails)
```

---

## Schedule Embedded in Content

**Each generated piece of content carries its own schedule.json.**

When you run `produce_blog.py`, `repurpose_blog.py`, or generate shorts metadata, the scripts automatically compute and write `content/derivatives/{slug}/schedule.json` — no manual timestamp management needed.

### Inspecting schedules

```bash
# See full schedule for a slug
cat content/derivatives/{slug}/schedule.json | python3 -m json.tool

# Extract just the publish times
jq '.social, .long_form.publish_at' content/derivatives/{slug}/schedule.json
```

### Auto-generating the weekly checklist

```bash
# Generate checklist for a given week (must be a Monday)
python3 scripts/generate_checklist.py --week 2026-06-09
# → docs/week-2026-06-09-publishing-checklist.md
```

The checklist reads all `schedule.json` files whose `long_form.publish_at` falls in that week, fills in YouTube upload commands with correct `--publish-at` values, and produces the canonical action list. No manual date entry required.

### Load posts: schedule.json + blog URLs + images

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

## Still to build

| Item | What's needed |
|------|--------------|
| Streamlit dashboard | `dashboard/app.py` — not yet created |
| Twitter hook patterns | Request Twitter archive → extract → `data/kb/twitter_hook_patterns.json` |
| LinkedIn OAuth refresh | Tokens expire 60 days — rerun `scripts/linkedin_auth.py` when needed |
| Worksheet automation | `scripts/auto_worksheet_workflow.py` — worksheet gen + Claude Design prompt in one call |
