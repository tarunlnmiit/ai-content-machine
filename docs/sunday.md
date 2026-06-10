# Sunday — Analytics (~15 min)

Auto-runs at 8pm and 10pm produce everything you need. Your job: read them, sync ideas to Notion, verify the scheduler is healthy.

## What runs automatically

| Time | Script | Output |
|------|--------|--------|
| 6:00 AM | `scripts/daily_ideas.sh` | `data/ideas/weekly_ideas.md` |
| 8:00 PM | `scripts/collect_analytics.py` | `data/analytics/weekly_insights.md` |
| 10:00 PM | `scripts/build_knowledge_base.py` | `data/kb/master_brief.md` |
| Continuous | `scripts/scheduler.py` | Fires pending LinkedIn posts every 60s |

---

## Step 1 — Read weekly insights (after 8pm, ~5 min)

```bash
cat data/analytics/weekly_insights.md
```

**What to note:**
- Which niche/format had highest views or CTR this week?
- Any short that blew up — what was the hook?
- Blog: Substack open rate + Medium reads
- Social: saves > likes on Instagram; replies > likes on Twitter

Record observations:
```bash
echo "" >> data/analytics/research_log.txt
echo "=== $(date '+%Y-%m-%d') ===" >> data/analytics/research_log.txt
echo "DS: ..." >> data/analytics/research_log.txt
echo "Life: ..." >> data/analytics/research_log.txt
echo "Poetry: ..." >> data/analytics/research_log.txt
```

---

## Step 2 — Read knowledge base (after 10pm, ~5 min)

```bash
cat data/kb/master_brief.md
```

**This is the primary input for Monday's topic picks.** It contains what's performing, under-served angles, hook patterns with high engagement, and what not to repeat. Read it Sunday night or Monday morning before picking topics.

---

## Step 3 — Sync ideas to Notion (~3 min)

```bash
python3 scripts/sync_ideas_to_notion.py --dry-run   # preview
python3 scripts/sync_ideas_to_notion.py             # sync
```

Pushes this week's `weekly_ideas.md` entries to Notion Contents DB as `Idea` rows.

---

## Step 4 — Verify scheduler (1 min)

```bash
launchctl list | grep contentmachine
tail -5 data/analytics/scheduler.log
sqlite3 data/scheduling.db \
  "SELECT COUNT(*) FROM posts WHERE status='pending' AND platform='linkedin'"
# Should be ≥ 3 (next week's LinkedIn posts)
```

If LinkedIn count = 0: run `python3 scripts/load_posts.py` on Monday.

---

## Checklist

- [ ] `weekly_insights.md` read + notes added to `research_log.txt`
- [ ] `master_brief.md` read — ready for Monday topic picks
- [ ] Ideas synced to Notion
- [ ] Scheduler running, LinkedIn queue ≥ 3 pending
