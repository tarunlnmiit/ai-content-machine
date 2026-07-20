---
title: "Medium Blog Repurposing — Weekly Workflow"
type: doc
slug: medium-repurposing-guide
tags: [content/doc]
---
# Medium Blog Repurposing — Weekly Workflow

**Created:** 2026-05-12  
**Schedule:** Runs PARALLEL with existing `docs/weekly-operating-guide.md`  
**Session-aware:** Processes 1–2 blogs per week to avoid token exhaustion  
**Scope:** Start with top 30 (15 high-engagement + 15 medium), expand as workflow proves

---

## How This Fits With Weekly Guide

| Day | Weekly Guide | Medium Repurposing |
|-----|---|---|
| **Mon** | DS Blog production (25 min) | — |
| **Tue** | Life Blog production (25 min) | — |
| **Wed** | Poetry Blog production (25 min) | — |
| **Thu** | Video recording (prep) | **Repurpose 1 Medium blog** (ghostwrite scripts) |
| **Fri** | Distribution + scheduling | Record Medium video + podcast |
| **Sat** | — | Edit + upload Medium video + podcast |
| **Sun** | Analytics + KB refresh | Load posts to scheduler. Prep next Medium blog. |

**Key:** Medium repurposing happens AFTER original weekly content ships. No conflicts.

---

## Quick Teaser + Backlink — Existing Published Pieces

When you already have a published **YouTube video** or **Medium blog** and just want a short
teaser of the *whole thing* plus a link back to it (manual posting — no scheduler), use
`scripts/teaser_from_published.py`. It writes copy-paste-ready files with the UTM backlink
already in the body.

```bash
# Single piece (niche auto-detected; --niche to force)
python3 scripts/teaser_from_published.py --url https://medium.com/@tarun-gupta/<id> --niche ds
python3 scripts/teaser_from_published.py --url https://youtu.be/<id> --niche poetry

# Preview without writing
python3 scripts/teaser_from_published.py --url <URL> --dry-run

# Batch — one URL per line: `url[, niche][, project]`  ('#' comments allowed)
python3 scripts/teaser_from_published.py --urls urls.txt

# Pick platforms (default: all five)
python3 scripts/teaser_from_published.py --url <URL> --platforms twitter linkedin newsletter
```

**Where text comes from:** YouTube → transcript (via `youtube-transcript-api`) + title/channel
via oEmbed. Medium → article scrape, falling back to the local `content/blogs/**/*.md` when the
URL is in `output/published/medium_posts.json` (handles Medium's bot wall).

**Output** → `content/derivatives/{week}/{slug}/`:
`twitter_teaser.txt`, `linkedin_teaser.txt`, `instagram_teaser.txt`, `threads_teaser.txt`,
`newsletter_teaser.txt`, plus `teasers.md` (all-in-one bundle) and `source.json`.
Each post ends with a UTM-tagged backlink (`utm_source` / `utm_medium` / `utm_campaign` /
`utm_content=<slug>`). Default campaign `evergreen-repurpose` (`--campaign` to change).

**Tag existing posts instead of writing new ones** — append the backlink to derivative files
already in a slug folder (idempotent; safe to re-run):

```bash
python3 scripts/teaser_from_published.py \
  --inject-link content/derivatives/2026-W22/<slug> \
  --url https://medium.com/@tarun-gupta/<id>
```

Then schedule each post **by hand** on the platform. No CSV / Metricool / Publer step.

---

## Weekly Batch Workflow (Repeating)

Each week: **1 Medium blog → 1 YouTube video + 1 podcast episode + 4 social posts**

### Thursday (30 min) — SCRIPTING

Extract Medium blog + generate scripts (before session limit):

```bash
cd ~/Making\ It\ Big/Claude/content-machine

# 1. Copy Medium article text to:
# content/sources/{BLOG_SLUG}_medium.txt

# 2. Generate YouTube script
python3 scripts/ghostwrite.py \
  --source content/sources/{BLOG_SLUG}_medium.txt \
  --niche ds \
  --voice analytical \
  --desire clarity \
  --topic "{BLOG_TITLE}" \
  --format yt

# 3. Generate podcast script (different voice)
python3 scripts/ghostwrite.py \
  --source content/sources/{BLOG_SLUG}_medium.txt \
  --niche ds \
  --voice conversational \
  --desire enjoyment \
  --topic "{PODCAST_TITLE_VARIANT}" \
  --format podcast

# 4. Generate social posts
python3 scripts/repurpose_blog.py \
  --source content/sources/{BLOG_SLUG}_medium.txt \
  --platforms twitter instagram linkedin threads
```

**Output:** 2 scripts + 4 social post files ready.

---

### Friday (3–4 hrs) — RECORDING

Record both video + podcast in one session:

```bash
# Record YouTube video (2 hrs)
# - Use DaVinci Resolve or OBS
# - Open: content/scripts/{DATE}_{BLOG_SLUG}_yt.md
# - Record screen + voice with Python/coding demo
# - Save: assets/video/edited/{DATE}_{BLOG_SLUG}_yt.mp4
# - Target: 8–10 min final

# Record podcast episode (1–2 hrs)
# - Use Audacity or Voice Memos app
# - Open: content/scripts/{DATE}_{BLOG_SLUG}_podcast.md
# - Record voice only (no screen)
# - Save: assets/audio/{DATE}_{BLOG_SLUG}_podcast.wav
# - Target: 12–15 min

# Quick check: files exist
ls -lh assets/video/edited/{DATE}_{BLOG_SLUG}_yt.mp4
ls -lh assets/audio/{DATE}_{BLOG_SLUG}_podcast.wav
```

---

### Saturday (1 hr) — EDIT + UPLOAD

Minimal editing + load to scheduler:

```bash
# Quick edit if needed (DaVinci Resolve can do bulk export)
# No special effects needed — raw is fine

# Stage LinkedIn into scheduling.db (no Metricool/Publer CSV — IG/FB/Threads are manual)
python3 scripts/load_posts.py --week {WEEK}

# Output:
# - data/scheduling.db: LinkedIn staged (held manual until employer clearance)
# - output/scheduled/upload_shorts.sh: YouTube Shorts upload commands
```

---

### Sunday (30 min) — SYNC + PREP

Prep next week's blog (distribution is manual — nothing to import):

```bash
# 1. Confirm per-platform derivative files exist for manual posting
ls content/derivatives/{WEEK}/*/instagram_caption.txt content/derivatives/{WEEK}/*/threads_post.txt

# 2. (Post IG/FB/Threads by hand in their windows during the week — see docs/daily/friday.md)

# 3. LinkedIn stays manual until clearance — do NOT start scheduler.py
#    ps aux | grep scheduler.py   # expect it to be stopped

# 4. Select NEXT WEEK's Medium blog
# - Pick from top unprocessed in data/analytics/medium-stats-all.json
# - Save to: content/sources/{NEXT_BLOG}_medium.txt
# - NOTE IT in Notion Contents DB (create entry with Status="Script")

# 5. Check analytics on previous week's posts
python3 scripts/collect_analytics.py
cat data/analytics/weekly_insights.md
```

---

## Blog Selection Order

Run through these in order (avoids random picks, focuses on high engagement):

**HIGH-ENGAGEMENT TIER (>10k views, 15 blogs):**
```
1. Data Preprocessing in Python (148k)
2. Types of Data Sets (90k)
3. Node.js Coding Style (65k)
4. Data Preprocessing in Data Mining (49k)
5. Measures of Proximity (49k)
6. Continuous Data & Zero Frequency (25k)
7. Structuring NodeJS API (25k)
8. JavaScript Magical Tips (23k)
9. Working with Spreadsheets Python (22k)
10. Simple Linear Regression (16k)
11. Decision Tree Classifier (16k)
12. Node.js Tips (14k)
13. Implementing Naive Bayes (13k)
14. Assessing Quality of Data (12k)
15. Indexing in Pandas.series (11k)
```

**MEDIUM TIER (1k–10k views, 18 blogs):**
```
Pick next 18 by views after HIGH tier completes
```

**LONG TAIL (if engagement warrants it):**
```
Only start after Phase 1 (30 blogs) ships + you measure performance
```

---

## Weekly Checklist

Print this for each week:

```
WEEK OF: ____________

[ ] Thursday: Extract Medium blog + generate scripts (30 min)
[ ] Friday: Record video (2 hrs) + podcast (1.5 hrs)
[ ] Saturday: Edit + load posts to DB (1 hr)
[ ] Sunday: confirm derivative files ready for manual posting + select next blog (30 min)

Blog this week: _____________________
Video filename: _____________________
Podcast filename: ___________________
Publish date: _______________________

Notes:
- Video target length: 8–10 min
- Podcast target length: 12–15 min
- Social posts generated: 4 (Twitter, Instagram, LinkedIn, Threads)
- Scheduler running? YES / NO
```

---

## Month 1 Output (4 weeks)

| Week | Blog | Views | Video | Podcast | Social |
|------|---|---|---|---|---|
| 1 | Data Preprocessing | 148k | ✓ | ✓ | 4 posts |
| 2 | Types of Data Sets | 90k | ✓ | ✓ | 4 posts |
| 3 | Node.js Style | 65k | ✓ | ✓ | 4 posts |
| 4 | Data Mining Preprocessing | 49k | ✓ | ✓ | 4 posts |
| **Total** | **4 blogs** | **352k combined views** | **4 videos** | **4 episodes** | **16 posts** |

Ship 4 YouTube videos + 4 podcast episodes + 16 social posts by end of May.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Ghostwriter script too long | Add `--max-words 2000` to truncate |
| DaVinci Resolve export error | H.264 MP4, 1080p, 30fps, try H.265 if h.264 fails |
| Podcast audio too quiet | Use Audacity Normalize (Effect → Normalize to -3dB) |
| load_posts.py fails | Run `python3 scripts/db_setup.py` first; it only takes `--week` |
| IG/FB/Threads not going out | They're manual now — post by hand from the derivative files (no CSV) |
| Scheduler (post-clearance only) | Only run it once LinkedIn is cleared: `nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &` |

---

## Files Output Summary

| Day | Content Type | Output File | Publish Date |
|-----|---|---|---|
| 1–2 | YouTube | `assets/video/edited/2026-05-12_data_preprocessing_yt.mp4` | 2026-05-15 |
| 1–2 | Podcast | `assets/audio/2026-05-12_data_preprocessing_podcast.wav` | 2026-05-16 |
| 1–2 | Social (4 posts) | `content/derivatives/.../twitter_thread.txt` etc. | 2026-05-15–16 |
| 3–4 | YouTube | `assets/video/edited/2026-05-13_types_datasets_yt.mp4` | 2026-05-16 |
| 3–4 | Podcast | `assets/audio/2026-05-13_types_datasets_podcast.wav` | 2026-05-17 |
| 3–4 | Social (4 posts) | `content/derivatives/.../...` | 2026-05-16–17 |
| 5–6 | YouTube | `assets/video/edited/2026-05-14_nodejs_style_yt.mp4` | 2026-05-17 |
| 5–6 | Podcast | `assets/audio/2026-05-14_nodejs_style_podcast.wav` | 2026-05-18 |
| 5–6 | Social (4 posts) | `content/derivatives/.../...` | 2026-05-17–18 |
| 7 | Static posts (IG/FB/Threads) | `content/derivatives/{week}/{slug}/*.txt` | Post manually |
| 7 | YouTube uploads | Directly to @breathofdatascience/@breathoflife | Live |
| 7 | Podcast episodes | Spotify/Anchor | Live |

---

## Key Reminders

1. **Don't re-write.** Ghostwriter converts Medium → video/podcast script directly. Minimal editing.
2. **Record raw.** Don't over-produce. Edit basic cuts in DaVinci Resolve, ship.
3. **Reuse thumbnails.** Use existing Canva templates + AI prompt generator if needed.
4. **Test one loop.** If Day 1–2 feels good, repeat Days 3–6 without changes.
5. **Ship Day 7.** Don't delay uploads. Get content live by 2026-05-19.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Ghostwriter script too long (10k+ words) | Use `--max-words 2000` flag to compress |
| DaVinci Resolve export fails | Export as H.264 MP4, 1080p, 30fps |
| Spotify upload timeout | Break audio into <15min segments |
| Missing derivative file | Re-run `prompts/repurposing_agent.md` for that slug; post manually once present |
| Scheduler not posting | Check: `tail -f data/analytics/scheduler.log` |

