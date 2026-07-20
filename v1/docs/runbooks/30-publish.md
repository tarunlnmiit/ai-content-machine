---
title: "Runbook 30 — Publish Approved Outputs (tier: Haiku)"
type: doc
slug: 30-publish
tags: [content/doc]
---
# Runbook 30 — Publish Approved Outputs (tier: Haiku)

Precondition: the human marked items ✅ in `data/ideas/weekly_menu.md` or the
review folder. **If an item is not explicitly approved, it does not ship. Ever.**

## Steps

### 1. Read approvals
Open `data/ideas/weekly_menu.md` + `output/review/{week}/`. Build the ship list:
only ✅ items. Ambiguous mark = not approved.

### 2. YouTube uploads (episode + shorts)
Use the `/upload-youtube` skill per approved video. Episode routes by niche:
life → Breath of Life, poetry → Breath of Poetry, ds → Breath of Data Science.
Title/description/chapters come from `episode_{niche}_meta.md` — human-picked
title option if marked, else option 1. Shorts metadata from the reel's meta file.
**Success:** skill reports the video URL. Record it in STATUS.

### 3. Instagram / LinkedIn / Threads staging
Stage approved reels + posts into the scheduler:
```bash
python3 scripts/load_posts.py ...   # per docs/guides/blog-pipeline.md staging step
```
**Success:** rows appear in `data/scheduling.db` with status='pending' and the
menu's publish slots. The `scheduler.py` daemon fires them — do not post directly.

### 4. Medium (blogs)
Per approved blog: `/publish-medium` skill, then record it in the tracker — either edit the
table directly at `localhost:8765/tracker` (dropdowns + paste the link), or headless:
```bash
python3 scripts/update_tracker.py <slug> --set medium.status=published --set medium.url=<link>
```
Both save to `docs/content-tracker.md` and regenerate the HTML. Hand-editing the MD also
works (key = blog slug); then `python3 scripts/generate_tracker_html.py`.

### 5. Tracker
Update `output/trackers/annual-tracker-2026.xlsx`: Status='Published' for
shipped slugs (rule from CLAUDE.md).

### 6. Status
`[date] shipped: episode→BoL <url>, 3 reels staged, blog→Medium; skipped: <❌ items>`

## STOP if
- Any upload fails twice → stop that item, continue others, note in STATUS.
- scheduler.db writes fail → `50-recovery.md`.
- An asset referenced by the menu is missing from review folder → do NOT
  regenerate it yourself (that's runbook 20 / Sonnet); note and skip.
