# Sunday — Publishing + Review (~20 min)

## Sunday at a glance

| Time | Action | Output goes live |
|------|--------|------------------|
| 10:00 AM | Week wrap-up + analytics review | — |
| 11:00 AM | Buffer depth check + refill week 4 if needed | Week 4 content ready by end of day |
| 12:00 PM | Notion sync (update Published status) | — |
| 1:00 PM | Import Metricool CSVs for next week's social | IG/FB/Threads scheduled for **week+1** Mon–Sun |
| 8:00 PM | Auto-run: collect analytics → weekly_insights.md | (via launchd cron) |
| 10:00 PM | Auto-run: build knowledge base | (via launchd cron) |

---

---

## Step 1 — Instagram + Facebook + Threads via Publer (10 min)

Open Publer dashboard:
- Import `output/scheduled/publer_ig_fb.csv` → select Instagram + Facebook → schedule
- Import `output/scheduled/publer_threads.csv` → select Threads → schedule

---

## Step 2 — Twitter/X (manual or auto)

Auto (APScheduler fires once `load_posts.py` ran Saturday):
```bash
sqlite3 data/scheduling.db \
  "SELECT * FROM posts WHERE platform='twitter' ORDER BY scheduled_at"
```

Manual:
```bash
cat content/derivatives/[ds_slug]/twitter_thread.txt
cat content/derivatives/[life_slug]/twitter_thread.txt
cat content/derivatives/[poetry_slug]/twitter_thread.txt
# Paste into Twitter/X scheduler
```

---

## Step 3 — Newsletter (optional, 5 min)

```bash
cat content/derivatives/[ds_slug]/newsletter.txt
cat content/derivatives/[life_slug]/newsletter.txt
cat content/derivatives/[poetry_slug]/newsletter.txt
# Copy each to Beehiiv → schedule
```

---

## Step 4 — Analytics review (5 min)

Cron auto-runs at 8pm:
```bash
cat data/analytics/weekly_insights.md     # auto-generated 8pm
cat data/analytics/research_log.txt | tail -20   # cron health
```

---

## Step 5 — Read KB for next week (5 min)

Cron auto-rebuilds at 10pm:
```bash
cat data/kb/master_brief.md
# Read before picking Monday's DS topic
```

---

## Step 6 — Push top ideas to Notion Contents DB (~1 min)

`daily_ideas.sh` writes top 5/niche to `weekly_ideas.md` at 6am. Sync the fresh set to Notion as `Idea` rows (Topic = Tech/Life/Poetry) so Monday topic pick can happen in Notion.

```bash
python3 scripts/sync_ideas_to_notion.py --dry-run   # preview
python3 scripts/sync_ideas_to_notion.py             # real sync (dedupes by title)
```

Config: reads `NOTION_CONTENTS_DB_ID` + `NOTION_INTEGRATION_SECRET` from `.env`. See [README.md](README.md#notion-integration-flow).

> Twitter + LinkedIn fire automatically via APScheduler once `load_posts.py` runs Saturday.
> Verify rows exist with correct `scheduled_at` times before closing.

---

## Step 7 — Check + replenish content buffer (~10–15 min)

**Rule: buffer MUST hold 4 weeks per niche at all times. This step is non-negotiable.**

Check current depth:
```bash
for niche in data_science_tech life_self_dev poetry_quotes; do
  count=$(ls content/buffer/week-*/${niche}/*_meta.md 2>/dev/null | wc -l | tr -d ' ')
  echo "$niche: $count / 4 weeks buffered"
done
```

**If any niche < 4:** stop here and fill before next week starts.

```bash
# 1. Open data/buffer/topics.yaml
#    Fill every empty week slot (topic + angle)
#    Check Notion Published first — avoid angles covered last 90 days

# 2. Preview what will generate:
conda run -n content_engine_env python3 scripts/generate_buffer.py --dry-run

# 3. Generate missing weeks (all niches):
conda run -n content_engine_env python3 scripts/generate_buffer.py

# Or targeted by week or niche:
conda run -n content_engine_env python3 scripts/generate_buffer.py --week 4
conda run -n content_engine_env python3 scripts/generate_buffer.py --niche poetry
```

Generation auto-applies **AutoTune temps** (DS=0.4 / Life=0.85 / Poetry=1.15) + **STM normalization**.
Models: DS → `claude-opus-4-7` · Life + Poetry → `claude-sonnet-4-6`.

**Alternative: push this week's live production into buffer instead of generating:**
```bash
# If you produced content Mon–Wed, push it into the next empty week slot
python3 scripts/push_to_buffer.py --niche ds     --week 4 --date YYYY-MM-DD
python3 scripts/push_to_buffer.py --niche life   --week 4 --date YYYY-MM-DD
python3 scripts/push_to_buffer.py --niche poetry --week 4 --date YYYY-MM-DD
# --dry-run first to preview. Omit --date to use latest by file date.
```

**After consuming a week's buffer (busy week) — restore immediately:**
```bash
bash scripts/shift_buffer.sh --dry-run   # verify week-4 has content
bash scripts/shift_buffer.sh             # rotate: week-2→1, week-3→2, week-4→3
# Then fill week-4 topics in data/buffer/topics.yaml and regenerate:
conda run -n content_engine_env python3 scripts/generate_buffer.py --week 4
```

Log consumed buffer items in Notion: Status → `Script`, add note "consumed from buffer [date]".
