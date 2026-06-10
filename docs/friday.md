# Friday — Schedule All Social Posts (~45 min)

Videos are live on YouTube from Thursday. Today: generate Metricool CSVs, import into Metricool for both brands, verify LinkedIn scheduler is running, and queue Twitter threads.

**Pivot rule:** Today you schedule content produced THIS week. It posts NEXT week. Blogs + videos already went live this week (Wed/Thu). Social posts (IG, Threads, Twitter, LinkedIn) fire in week N+1 — that's what today's CSV imports and scheduler queue set up.

## Friday at a glance

| Time | Action | Output |
|------|--------|--------|
| 9:00 AM | Generate Metricool CSVs | `output/scheduled/metricool_breathofds.csv` + `metricool_mistakenlyhuman.csv` |
| 9:15 AM | Import CSVs into Metricool | Posts scheduled in Metricool calendar |
| 9:30 AM | Verify LinkedIn scheduler | scheduler.py running, queue populated |
| 9:45 AM | Queue Twitter threads | Reminders set or MCP posted |
| 10:00 AM | Final verification | Calendar view confirms all posts for next week |

---

## Step 1 — Generate Metricool CSVs (5 min)

Generate CSVs for **this week's content** (posts fire next week — the +1 pivot rule):

```bash
python3 scripts/load_posts.py
```

This reads all `content/derivatives/{week}/*/schedule.json` and:
- Builds `output/scheduled/metricool_breathofds.csv` — DS niche (brand: @breathofdatascience)
- Builds `output/scheduled/metricool_mistakenlyhuman.csv` — Life + Poetry niches (brand: @mistakenlyhuman)
- Inserts LinkedIn posts into `data/scheduling.db` (scheduler.py fires these)

### If blog URLs are missing in CSV captions

```bash
# Check which slugs are missing Medium URLs
python3 -c "
import json, glob
for f in glob.glob('content/derivatives/{week}/*/schedule.json'):
    d = json.load(open(f))
    if not d.get('medium_url'):
        print('MISSING medium_url:', f.split('/')[-2][:50])
"
```

Add missing URLs then re-run:
```bash
python3 scripts/update_schedule.py \
  --slug {slug} --week {week} \
  --medium-url 'https://medium.com/@tarun-gupta/your-post-slug'

python3 scripts/load_posts.py
```

### If image URLs are missing

1. Upload social image to Google Drive: `assets/social_posts/{week}/{slug}_instagram.png`
2. Set sharing to "Anyone with the link can view"
3. Get direct download URL format: `https://drive.google.com/uc?id=FILE_ID&export=view`
4. Save and regenerate:
```bash
python3 scripts/update_schedule.py \
  --slug {slug} --week {week} \
  --image-url 'https://drive.google.com/uc?id=FILE_ID&export=view'
python3 scripts/load_posts.py
```

---

## Step 2 — Import CSVs into Metricool (~10 min)

### DS brand (@breathofdatascience)

1. Go to [metricool.com](https://metricool.com) → log in
2. Top-left: select brand **"Breath of Data Science"**
3. Left sidebar: **Schedule** → **Bulk Schedule**
4. Click **Upload CSV**
5. Select: `output/scheduled/metricool_breathofds.csv`
6. Metricool shows a preview of all rows — verify:
   - Dates are in next week (not this week)
   - Captions include blog link ("Full post 👉 https://...")
   - Image thumbnail shows in preview (not a red X)
   - Timezone is IST (check in Settings if wrong)
7. Click **Schedule All**

### Life + Poetry brand (@mistakenlyhuman)

1. Top-left: switch brand to **"Mistakenly Human"**
2. **Schedule** → **Bulk Schedule** → **Upload CSV**
3. Select: `output/scheduled/metricool_mistakenlyhuman.csv`
4. Verify and click **Schedule All**

### CSV column format (for manual edits)

```
Date,Time,Caption,Picture Url 1,Platforms
2026-06-17,08:00,"Caption text here. Full post 👉 https://...","https://drive.google.com/uc?id=...","instagram,facebook"
2026-06-17,20:00,"Threads caption text. Link in bio.","https://drive.google.com/uc?id=...","threads"
```

- `Date`: `YYYY-MM-DD`
- `Time`: `HH:MM` in your Metricool account timezone (verify it's IST)
- `Picture Url 1`: public direct-download URL (Drive, Dropbox, S3)
- `Platforms`: comma-separated, lowercase: `instagram,facebook` · `threads` · `twitter` · `linkedin`

### Expected posting schedule for next week

| Niche | Platform | Day | Time IST |
|-------|---------|-----|---------|
| Life | Instagram + Facebook | Tue | 8:00 AM |
| Life | Threads | Tue | 8:00 PM |
| Life | LinkedIn | Tue | 8:00 AM *(scheduler.py)* |
| DS | Instagram + Facebook | Wed | 8:00 AM |
| DS | Threads | Wed | 8:00 PM |
| DS | LinkedIn | Tue | 8:00 AM *(scheduler.py)* |
| Poetry | Instagram + Facebook | Fri | 10:00 AM |
| Poetry | Threads | Fri | 12:00 PM |
| Poetry | LinkedIn | Tue | 8:00 AM *(scheduler.py)* |

### Common Metricool issues

| Symptom | Fix |
|---------|-----|
| Red X on image | URL is private or broken — re-upload to Drive, set to public, regenerate URL |
| "Invalid date" error | Date must be `YYYY-MM-DD` — open CSV in text editor and verify |
| Posts in wrong timezone | Metricool → Settings → Account → set timezone to Asia/Kolkata (IST) |
| Posts land on wrong day | Check the +1 week offset — content created this week posts NEXT week |

---

## Step 3 — Verify LinkedIn scheduler (5 min)

LinkedIn posts are handled by `scheduler.py` — not Metricool (Metricool LinkedIn requires Business plan).

### Check scheduler is running

```bash
ps aux | grep 'scheduler.py' | grep -v grep
```

Not running? Start it:
```bash
nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &
echo "Scheduler started, PID: $!"
```

Or via launchd (preferred — survives reboots):
```bash
launchctl load ~/Library/LaunchAgents/com.contentmachine.scheduler.plist
launchctl list | grep contentmachine
```

### Check what's queued for next week

```bash
sqlite3 data/scheduling.db \
  "SELECT platform, scheduled_at, substr(content_text,1,80) AS preview
   FROM posts
   WHERE status='pending' AND platform='linkedin'
   ORDER BY scheduled_at
   LIMIT 10"
```

Expected: 3 rows (one per niche), all scheduled for next Tuesday ~8:00 AM IST.

### If LinkedIn posts are missing from DB

Re-run `load_posts.py` — it re-inserts missing entries:
```bash
python3 scripts/load_posts.py
sqlite3 data/scheduling.db \
  "SELECT COUNT(*) FROM posts WHERE status='pending' AND platform='linkedin'"
# Should return 3
```

### Check recent scheduler activity

```bash
tail -30 data/analytics/scheduler.log
```

Look for `[POST]` lines for linkedin. If seeing `FAILED: 401` → LinkedIn token expired:
```bash
python3 scripts/auth_linkedin.py --refresh
```

LinkedIn tokens expire every 60 days — add a calendar reminder.

---

## Step 4 — Queue Twitter threads (~10 min)

Twitter/X threads are posted manually — scheduled tools flatten voice and context.

### Life thread — post Mon 1:00 PM IST (next week)

```bash
cat content/derivatives/{week}/{life_slug}/twitter_thread.txt
```

The draft has 8–12 tweets. Edit to match your current voice — drafts are starting points. Open Twitter/X:
- New tweet → type tweet 1 → click "Add another tweet" → paste/type tweet 2 → repeat
- **OR** use the MCP tool to post immediately (if you don't want to schedule):
  ```
  mcp__twitter-mcp__post_tweet
    text: "[tweet 1 text]"
  ```
  Then post subsequent tweets as replies.

Set a calendar reminder for **next Mon 1:00 PM IST**.

### Poetry thread — post Fri 12:00 PM IST (next week)

```bash
cat content/derivatives/{week}/{poetry_slug}/twitter_thread.txt
```

Poetry thread format:
1. Opening couplet or striking image description
2. The poem excerpt (2–3 tweets)
3. Context: what inspired the poem
4. Personal reflection
5. CTA: "Read the full piece → [link]"

Set a calendar reminder for **next Fri 12:00 PM IST**.

### DS thread — no fixed slot (post when engagement is high)

DS Twitter audience responds better to spontaneous hot-takes than scheduled threads. Read `content/derivatives/{week}/{ds_slug}/twitter_thread.txt` for the draft, but post it when you're active in the timeline and can reply to comments within the first hour.

---

## Step 5 — Final verification checklist (5 min)

### Metricool calendar view

1. In Metricool → **Calendar** view
2. Navigate to next week
3. Verify:
   - Tue: Life IG/FB + Life Threads (+ Life LinkedIn shown if plan allows)
   - Wed: DS IG/FB + DS Threads
   - Fri: Poetry IG/FB + Poetry Threads

### DB queue

```bash
sqlite3 data/scheduling.db \
  "SELECT platform, COUNT(*) AS count, MIN(scheduled_at) AS first
   FROM posts WHERE status='pending'
   GROUP BY platform ORDER BY first"
```

Expected: linkedin rows = 3, scheduled for next Tuesday.

### File artifacts

```bash
ls -la output/scheduled/
# metricool_breathofds.csv — modified today
# metricool_mistakenlyhuman.csv — modified today

wc -l output/scheduled/metricool_breathofds.csv
# ~4 lines (header + 3 posts)
wc -l output/scheduled/metricool_mistakenlyhuman.csv
# ~7 lines (header + 6 posts: Life + Poetry × 3 platforms)
```

### End-of-week checklist

- [ ] Metricool CSVs imported for both brands
- [ ] Metricool calendar shows posts across Tue/Wed/Fri next week
- [ ] LinkedIn queue has 3 pending posts in DB
- [ ] scheduler.py running (or launchd plist loaded)
- [ ] Twitter reminders set: Life Mon 1 PM, Poetry Fri 12 PM (both next week)
- [ ] YouTube videos uploaded and scheduled (done Thursday)
- [ ] Shorts queue active — 2/day Mon–Sun (done Thursday)
- [ ] Notion status updated: Status → Uploaded for all 3 content items

---

## Step 6 — Buffer depth check (~5 min)

Run every Friday to ensure buffer never drops below 4 weeks per niche before the weekend.

```bash
for niche in data_science_tech life_self_dev poetry_quotes; do
  count=$(ls content/buffer/week-*/${niche}/*_meta.md 2>/dev/null | wc -l | tr -d ' ')
  echo "$niche: ${count}/4"
done
```

All at 4 → done, weekend free.

Any niche < 4 → replenish now:
```bash
# 1. Open data/buffer/topics.yaml — fill empty week slots
#    Check Notion first: python3 scripts/query_notion_recent.py --days 90

# 2. Preview:
conda run -n content_engine_env python3 scripts/generate_buffer.py --dry-run

# 3. Generate:
conda run -n content_engine_env python3 scripts/generate_buffer.py
# Or targeted:
conda run -n content_engine_env python3 scripts/generate_buffer.py --niche poetry
conda run -n content_engine_env python3 scripts/generate_buffer.py --week 4
```

AutoTune temps: DS=0.4, Life=0.85, Poetry=1.15.

Also refresh the content tracker:
```bash
python3 scripts/sync_tracker.py
# → data/content_tracker.csv updated with this week's final state
```
