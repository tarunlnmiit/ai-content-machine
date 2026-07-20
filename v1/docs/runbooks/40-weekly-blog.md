---
title: "Runbook 40 — Weekly Blog + Derivatives (tier: Opus)"
type: doc
slug: 40-weekly-blog
tags: [content/doc]
---
# Runbook 40 — Weekly Blog + Derivatives (tier: Opus)

The working spine — unchanged by the raw-session reboot. One blog per niche per
week (ds, life, poetry). Worksheets stay ON (DS/Life). Carousels/slide decks/
quote cards are PAUSED (2026-07 cadence decision) — skip them.

## Steps

### 1. Pick the topic
From `data/ideas/weekly_ideas.md`, the top-scored ✅-marked idea for the niche.
Check `output/trackers/annual-tracker-2026.xlsx` — no repeat angles within 90
days per niche (CLAUDE.md rule). Read `data/kb/master_brief.md` before writing.

### 2. Produce the blog
```bash
python3 scripts/produce_blog.py --topic "<topic>" --niche <ds|life|poetry>
```
Opus judgment applies INSIDE the blog: structure, examples, the `[QUOTABLE]`
line, virality levers. Voice rules + banned words per master_brief. Timeout is
long (hero_blog task) — do not kill it early.
**Success:** blog `.md` in `content/blogs/{week}/`, passes a self-read for voice.

### 3. Derivatives (carousel paused, worksheet on)
```bash
python3 scripts/run_blog_pipeline.py --input "<blog.md>" --no-carousel
```
**Success:** derivatives folder for the slug with posts + thumbnail brief +
worksheet (DS/Life); staging via load_posts happened (unless `--no-stage`).

### 4. Worksheet delivery
Generated worksheet lands via `generate_worksheet_html.py` inside the pipeline.
The push/deploy of the gated link stays MANUAL — note it in `manual_steps.md`.

### 5. Status
`[date] blog {niche} '{title}' + derivatives done; worksheet pending deploy`

## STOP if
- Blog generation times out twice → prompt too big; report, don't raise timeout.
- Tracker shows the angle was covered <90 days ago → pick the next idea down.
- You want to change cadence, revive carousels, or skip the tracker check → no;
  note the impulse in STATUS and move on.
