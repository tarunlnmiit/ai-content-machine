# Friday — DS Track (~20 min)

Videos are live on YouTube from Thursday. Today: generate DS Metricool CSV, import it, verify LinkedIn scheduler for DS, and queue DS Twitter thread.

**Pivot rule:** Content produced this week posts NEXT week.

---

## Step 1 — Generate Metricool CSV (~2 min)

```bash
python3 scripts/load_posts.py
```

Writes: `output/scheduled/metricool_breathofds.csv`

Also inserts DS LinkedIn post into `data/scheduling.db`.

### If DS blog URL is missing in the CSV

```bash
# Check:
python3 -c "
import json, glob
for f in glob.glob('content/derivatives/{week}/*data_science_tech*/schedule.json'):
    d = json.load(open(f))
    print('Medium:', d.get('medium_url', 'MISSING'))
    print('Substack:', d.get('substack_url', 'MISSING'))
"
```

Add missing URL, then re-run `load_posts.py`:
```bash
python3 scripts/update_schedule.py \
  --slug {ds_slug} --week {week} \
  --medium-url 'https://medium.com/@tarun-gupta/{ds_slug}'

python3 scripts/load_posts.py
```

### If DS image URL is missing

1. Upload `assets/social_posts/{week}/{ds_slug}_instagram.png` to Google Drive
2. Set "Anyone with the link can view"
3. Get URL: `https://drive.google.com/uc?id=FILE_ID&export=view`
4. Save and regenerate:
```bash
python3 scripts/update_schedule.py \
  --slug {ds_slug} --week {week} \
  --image-url 'https://drive.google.com/uc?id=FILE_ID&export=view'
python3 scripts/load_posts.py
```

---

## Step 2 — Import DS CSV into Metricool (~5 min)

1. [metricool.com](https://metricool.com) → select brand **"Breath of Data Science"**
2. **Schedule** → **Bulk Schedule** → **Upload CSV**
3. Select: `output/scheduled/metricool_breathofds.csv`
4. Verify preview:
   - Dates are NEXT week
   - Captions include blog link
   - Images show thumbnail (not red X)
   - Timezone: Asia/Kolkata (IST)
5. Click **Schedule All**

**DS posting schedule (next week):**

| Platform | Day | Time IST |
|---------|-----|---------|
| Instagram + Facebook | Wed | 8:00 AM |
| Threads | Wed | 8:00 PM |
| LinkedIn | Tue | 8:00 AM *(scheduler.py)* |

---

## Step 3 — Verify DS in LinkedIn scheduler (~3 min)

```bash
sqlite3 data/scheduling.db \
  "SELECT platform, scheduled_at, substr(content_text,1,80) AS preview
   FROM posts
   WHERE status='pending' AND platform='linkedin'
     AND content_text LIKE '%data%'
   ORDER BY scheduled_at LIMIT 5"
```

Expected: 1 DS row, scheduled next Tuesday ~8:00 AM.

Scheduler running check:
```bash
ps aux | grep 'scheduler.py' | grep -v grep
```

Not running → start it:
```bash
nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &
```

---

## Step 4 — DS Twitter thread (~5 min)

DS thread has no fixed posting slot — post when you're active and can reply within the first hour.

```bash
cat content/derivatives/{week}/{ds_slug}/twitter_thread.txt
```

Draft is a starting point — edit to match current voice before posting. Format: hook tweet → 4–6 explanation tweets → insight tweet → CTA with Medium link.

No calendar reminder needed — post when you're in the timeline.

---

## Buffer check (DS portion)

```bash
count=$(ls content/buffer/week-*/data_science_tech/*_meta.md 2>/dev/null | wc -l | tr -d ' ')
echo "DS buffer: ${count}/4"
```

< 4 → replenish:
```bash
conda run -n content_engine_env python3 scripts/generate_buffer.py --niche ds
# AutoTune temp: 0.4
```
