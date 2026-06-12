# Friday — Life Track (~20 min)

Videos are live on YouTube from Thursday. Today: generate Life Metricool CSV, import it, verify LinkedIn scheduler for Life, and queue Life Twitter thread.

**Pivot rule:** Content produced this week posts NEXT week.

---

## Step 1 — Generate Metricool CSV (~2 min)

```bash
python3 scripts/load_posts.py
```

Writes: `output/scheduled/metricool_mistakenlyhuman.csv` (Life + Poetry combined)

Also inserts Life LinkedIn post into `data/scheduling.db`.

### If Life blog URL is missing in the CSV

```bash
python3 -c "
import json, glob
for f in glob.glob('content/derivatives/{week}/*life_self_dev*/schedule.json'):
    d = json.load(open(f))
    print('Medium:', d.get('medium_url', 'MISSING'))
    print('Substack:', d.get('substack_url', 'MISSING'))
"
```

Add missing URL, then re-run `load_posts.py`:
```bash
python3 scripts/update_schedule.py \
  --slug {life_slug} --week {week} \
  --medium-url 'https://medium.com/@tarun-gupta/{life_slug}'

python3 scripts/load_posts.py
```

### If Life image URL is missing

1. Upload `assets/social_posts/{week}/{life_slug}_instagram.png` to Google Drive
2. Set "Anyone with the link can view"
3. Get URL: `https://drive.google.com/uc?id=FILE_ID&export=view`
4. Save and regenerate:
```bash
python3 scripts/update_schedule.py \
  --slug {life_slug} --week {week} \
  --image-url 'https://drive.google.com/uc?id=FILE_ID&export=view'
python3 scripts/load_posts.py
```

---

## Step 2 — Import Life portion into Metricool (~5 min)

1. [metricool.com](https://metricool.com) → select brand **"Mistakenly Human"**
2. **Schedule** → **Bulk Schedule** → **Upload CSV**
3. Select: `output/scheduled/metricool_mistakenlyhuman.csv` (contains both Life + Poetry rows)
4. Verify preview — confirm Life rows:
   - `life_self_dev` slug rows land on **Tuesday** (IG 8 AM, Threads 8 PM)
   - Dates are NEXT week
   - Images show thumbnail (not red X)
5. Click **Schedule All**

**Life posting schedule (next week):**

| Platform | Day | Time IST |
|---------|-----|---------|
| Instagram + Facebook | Tue | 8:00 AM |
| Threads | Tue | 8:00 PM |
| LinkedIn | Tue | 8:00 AM *(scheduler.py)* |

---

## Step 3 — Verify Life in LinkedIn scheduler (~3 min)

```bash
sqlite3 data/scheduling.db \
  "SELECT platform, scheduled_at, substr(content_text,1,80) AS preview
   FROM posts
   WHERE status='pending' AND platform='linkedin'
     AND content_text LIKE '%life%'
   ORDER BY scheduled_at LIMIT 5"
```

Expected: 1 Life row, scheduled next Tuesday ~8:00 AM.

Scheduler running check:
```bash
ps aux | grep 'scheduler.py' | grep -v grep
```

Not running → start it:
```bash
nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &
```

---

## Step 4 — Life Twitter thread (~5 min)

Post next **Monday at 1:00 PM IST**.

```bash
cat content/derivatives/{week}/{life_slug}/twitter_thread.txt
```

Edit to match your current voice (drafts are starting points). Format: personal hook → story beat → insight → CTA.

Set calendar reminder: **next Mon 1:00 PM IST** — thread post + 30-min reply window.

---

## Buffer check (Life portion)

```bash
count=$(ls content/buffer/week-*/life_self_dev/*_meta.md 2>/dev/null | wc -l | tr -d ' ')
echo "Life buffer: ${count}/4"
```

< 4 → replenish:
```bash
conda run -n content_engine_env python3 scripts/generate_buffer.py --niche life
# AutoTune temp: 0.85
```
