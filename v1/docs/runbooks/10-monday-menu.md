---
title: "Runbook 10 — Monday Menu Prep (tier: Haiku; Sonnet on any error)"
type: doc
slug: 10-monday-menu
tags: [content/doc]
---
# Runbook 10 — Monday Menu Prep (tier: Haiku; Sonnet on any error)

Goal: by Monday morning the human opens ONE file — `data/ideas/weekly_menu.md` —
and ticks boxes. Nothing else to decide.

Run Sunday evening (or via the scheduler chain). All commands from `v1/`.

## Steps

### 1. Collect analytics
```bash
python3 scripts/collect_analytics.py
```
**Success:** `data/analytics/weekly_insights.md` has today's date in its header
and the summary section is NOT "Summary unavailable". If summary failed →
escalate per `50-recovery.md`.

### 2. Surface winners
```bash
python3 scripts/weekly_winners.py
```
**Success:** prints "REPRODUCE LAST WEEK'S WINNERS" block with ≥1 bullet.
Empty bullets are OK if the insights file is fresh (slow week).

### 3. Refresh idea inputs
```bash
python3 scripts/fetch_google_suggest.py
python3 scripts/fetch_external_feeds.py
```
**Success:** new `data/ideas/*_{today}.json` files exist and are >1KB.

### 4. Score ideas
```bash
python3 scripts/idea_scorer.py --force
```
**Success:** `data/ideas/weekly_ideas.md` header shows the CURRENT ISO week and
the "Blog + Reel Ideas (virality-scored)" sections are non-empty. If they say
"No ideas scored" → step 3 didn't produce input files; re-run step 3 once, then
escalate.

### 5. Generate the prompt pack
```bash
python3 scripts/generate_prompt_pack.py --force
```
Optional theme bias (Sonnet may set from step 2's winner themes; Haiku omits):
`--theme career,self-doubt`
**Success:** `content/sessions/{week}/prompt_pack.json` + `teleprompter.html`
exist; script printed 6–8 questions across life/poetry/ds.

### 6. Render the menu
```bash
python3 scripts/weekly_menu.py
```
(If `weekly_menu.py` does not exist yet, assemble `data/ideas/weekly_menu.md` by
hand from: prompt pack questions + this week's blog slots + winner headline.
Keep to one page, checkbox per item.)
**Success:** `data/ideas/weekly_menu.md` exists, dated this week, one ✅/❌
checkbox per proposed item, ONE headline metric from last week at top.

### 7. Status
Append one line to `output/review/{week}/STATUS.md`:
`[date] menu ready — N questions, M blog slots, winners: <one phrase>`

## STOP if
- Any script errors twice → `50-recovery.md` (Sonnet).
- `weekly_insights.md` still shows a stale week after step 1 → API/token issue, escalate.
- You are tempted to edit questions, hooks, or scores by hand → don't; note it.
