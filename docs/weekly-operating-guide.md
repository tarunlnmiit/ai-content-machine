# Weekly Operating Guide

Last updated: 2026-05-25

## Week at a Glance

| Day | Focus | Time |
|-----|-------|------|
| [Monday](monday.md) | DS Blog — produce, fill, images | ~25 min |
| [Tuesday](tuesday.md) | Life Blog + Repurpose DS (with design prompts) | ~35 min |
| [Wednesday](wednesday.md) | Poetry Blog + Repurpose all + Claude Design + Worksheets | ~40 min + 15–20 min Claude Design |
| [Thursday](thursday.md) | DS video: script → record → edit → reel → upload | ~2 hrs |
| [Friday](friday.md) | Life + Poetry: scripts → record talking head → B-roll hints for edit | ~2 hrs |
| [Saturday](saturday.md) | Auto-edit Life + Poetry ([video guide](video-production-guide.md)) → shorts → upload → publish Medium → load scheduler | ~1 hr |
| [Sunday](sunday.md) | Social scheduling (Publer + Twitter) + review | ~20 min |

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
output/scheduled/claude_design_prompts_{slug}.md ← 4 design prompts per blog (paste into Claude Design)
output/scheduled/validated_code_{slug}.json      ← DS tutorial: tested code blocks

assets/
  ├── carousels/{slug}_carousel.html             ← Instagram carousel (swipeable HTML, export-ready)
  ├── carousels/slides/{slug}/slide_N.png        ← 1080×1350 PNG exports (--export flag)
  ├── slides/{slug}_slides.pdf                   ← from Claude Design
  ├── stories/{slug}_story_*.png                 ← from Claude Design
  ├── social_posts/{slug}_instagram.png          ← 1080×1080
  ├── social_posts/{slug}_linkedin.png           ← 1200×628
  ├── social_posts/{slug}_twitter.png            ← 1200×675
  ├── social_posts/{slug}_threads.png            ← 1080×1080
  ├── reels/{slug}_cover.png                     ← 9:16 from Claude Design
  ├── videos/{slug}/{slug}_raw.mp4               ← Life/Poetry: raw talking-head recording (iPhone)
  ├── videos/{slug}/                             ← B-roll clips + VIDEO_MAP.json
  ├── video/edited/{slug}.mp4                    ← long-form YouTube (FINAL)
  └── video/edited/{slug}_reel.mp4              ← YouTube Short / reel (FINAL, 9:16)

output/scheduled/publer_ig_fb.csv               ← import with Instagram + Facebook selected
output/scheduled/publer_threads.csv             ← import with Threads selected
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

## Still to build

| Item | What's needed |
|------|--------------|
| Streamlit dashboard | `dashboard/app.py` — not yet created |
| Twitter hook patterns | Request Twitter archive → extract → `data/kb/twitter_hook_patterns.json` |
| LinkedIn OAuth refresh | Tokens expire 60 days — rerun `scripts/linkedin_auth.py` when needed |
| Worksheet automation | `scripts/auto_worksheet_workflow.py` — worksheet gen + Claude Design prompt in one call |
