# Friday — Poetry Track (~20 min)

Videos are live on YouTube from Thursday. Today: generate Poetry Metricool CSV, import it, verify LinkedIn scheduler for Poetry, and queue Poetry Twitter thread.

**Pivot rule:** Content produced this week posts NEXT week.

---

## Step 1 — Generate Metricool CSV (~2 min)

```bash
python3 scripts/load_posts.py
```

Writes: `output/scheduled/metricool_mistakenlyhuman.csv` (Poetry + Life combined)

Also inserts Poetry LinkedIn post into `data/scheduling.db`.

### If Poetry blog URL is missing in the CSV

```bash
python3 -c "
import json, glob
for f in glob.glob('content/derivatives/{week}/*poetry_quotes*/schedule.json'):
    d = json.load(open(f))
    print('Medium:', d.get('medium_url', 'MISSING'))
    print('Substack:', d.get('substack_url', 'MISSING'))
"
```

Add missing URL, then re-run `load_posts.py`:
```bash
python3 scripts/update_schedule.py \
  --slug {poetry_slug} --week {week} \
  --medium-url 'https://medium.com/@tarun-gupta/{poetry_slug}'

python3 scripts/load_posts.py
```

### If Poetry image URL is missing

1. Upload `assets/social_posts/{week}/{poetry_slug}_instagram.png` to Google Drive
2. Set "Anyone with the link can view"
3. Get URL: `https://drive.google.com/uc?id=FILE_ID&export=view`
4. Save and regenerate:
```bash
python3 scripts/update_schedule.py \
  --slug {poetry_slug} --week {week} \
  --image-url 'https://drive.google.com/uc?id=FILE_ID&export=view'
python3 scripts/load_posts.py
```

---

## Step 2 — Import Poetry portion into Metricool (~5 min)

1. [metricool.com](https://metricool.com) → select brand **"Mistakenly Human"**
2. **Schedule** → **Bulk Schedule** → **Upload CSV**
3. Select: `output/scheduled/metricool_mistakenlyhuman.csv` (contains both Poetry + Life rows)
4. Verify preview — confirm Poetry rows:
   - `poetry_quotes` slug rows land on **Friday** (IG 10 AM, Threads 12 PM)
   - Dates are NEXT week
   - Images show thumbnail (not red X)
5. Click **Schedule All**

**Poetry posting schedule (next week):**

| Platform | Day | Time IST |
|---------|-----|---------|
| Instagram + Facebook | Fri | 10:00 AM |
| Threads | Fri | 12:00 PM |
| LinkedIn | Tue | 8:00 AM *(scheduler.py)* |

---

## Step 3 — Verify Poetry in LinkedIn scheduler (~3 min)

```bash
sqlite3 data/scheduling.db \
  "SELECT platform, scheduled_at, substr(content_text,1,80) AS preview
   FROM posts
   WHERE status='pending' AND platform='linkedin'
     AND content_text LIKE '%poem%'
   ORDER BY scheduled_at LIMIT 5"
```

Expected: 1 Poetry row, scheduled next Tuesday ~8:00 AM.

Scheduler running check:
```bash
ps aux | grep 'scheduler.py' | grep -v grep
```

Not running → start it:
```bash
nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &
```

---

## Step 4 — Poetry Twitter thread (~5 min)

Post next **Friday at 12:00 PM IST**.

```bash
cat content/derivatives/{week}/{poetry_slug}/twitter_thread.txt
```

Poetry thread format:
1. Opening couplet or striking image description
2. Poem excerpt (2–3 tweets)
3. Context: what inspired the poem
4. Personal reflection
5. CTA: "Read the full piece → [Substack link]"

Edit to match your current voice before posting.

Set calendar reminder: **next Fri 12:00 PM IST** — thread post + 30-min reply window.

---

## Buffer check (Poetry portion)

```bash
count=$(ls content/buffer/week-*/poetry_quotes/*_meta.md 2>/dev/null | wc -l | tr -d ' ')
echo "Poetry buffer: ${count}/4"
```

< 4 → replenish:
```bash
conda run -n content_engine_env python3 scripts/generate_buffer.py --niche poetry
# AutoTune temp: 1.15
```

---

## Final end-of-week checklist

Run once after all 3 niche Friday guides are done:

- [ ] Metricool CSVs imported for both brands
- [ ] Metricool calendar shows posts: Tue (Life), Wed (DS), Fri (Poetry) next week
- [ ] LinkedIn queue has 3 pending posts in DB
- [ ] scheduler.py running (or launchd plist loaded)
- [ ] Twitter reminders set: Life Mon 1 PM, DS (flexible), Poetry Fri 12 PM
- [ ] YouTube videos uploaded and scheduled (done Thursday)
- [ ] Notion status: Uploaded for all 3 content items
- [ ] Buffer depth ≥ 4 for all 3 niches

```bash
python3 scripts/sync_tracker.py
# → data/content_tracker.csv updated with this week's final state
```
