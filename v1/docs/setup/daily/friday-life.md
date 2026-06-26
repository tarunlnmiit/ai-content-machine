> ⚠️ **PIPELINE UPDATED 2026-06-20 — canonical model: [`docs/pipeline-2026.md`](../../guides/pipeline-2026.md).**
> Twitter **dropped**. Instagram / Threads **auto-publish** via the Meta Graph API (`scripts/scheduler.py`); Facebook mirrors Instagram; LinkedIn **active** (employer cleared), blog link in the **pinned first comment**. Reels → **Instagram Reels + YouTube Shorts only**, ≈9 **distinct** reels/week (not ~56). Poetry short = **poem only**. Worksheet email CTA (DS/Life) is the owned channel (Substack retired). Run `python3 scripts/weekly_winners.py` before producing. Manual steps left: record · ~10-min approve · reply.
>
> Where any step below disagrees, the canonical doc wins.

# Friday — Life Track (~20 min)

Videos are live on YouTube from Thursday. Today: stage the Life LinkedIn post, gather the Life blog URL for captions, and queue the Life Twitter thread. **No Metricool/Publer** — IG / FB / Threads / Twitter are posted manually; LinkedIn is manual until employer clearance.

**Pivot rule:** Content produced this week posts NEXT week.

> **Reference docs:** `config/hashtags.json` (edit per-niche hashtag pools — no code change needed) · `docs/weekly-operating-guide.md` (scheduler.py setup) · `docs/weekly-runner.md` Step 22 (manual posting model)

---

## Step 1 — Stage Life LinkedIn + gather blog URL (~2 min)

```bash
python3 scripts/load_posts.py
```

Inserts the Life LinkedIn post into `data/scheduling.db` (held manual until clearance). No Metricool/Publer CSV.

### Gather the Life Medium URL for your captions

```bash
python3 -c "
import json, glob
for f in glob.glob('content/derivatives/{week}/*life_self_dev*/schedule.json'):
    d = json.load(open(f))
    print('Medium:', d.get('medium_url', 'MISSING'))
"
```

Record a missing URL so it's on hand when you post:
```bash
python3 scripts/update_schedule.py \
  --slug {life_slug} --week {week} \
  --medium-url 'https://medium.com/@tarun-gupta/{life_slug}'
```

---

## Step 2 — Post Life static content manually (~5 min)

Post by hand in the Life window (no Metricool import):

- **Instagram + Facebook** (@mistakenlyhuman): caption `content/derivatives/{week}/{life_slug}/instagram_caption.txt`; image `assets/social_posts/{week}/{life_slug}_instagram.png`. Paste the Medium URL inline.
- **Threads:** body `content/derivatives/{week}/{life_slug}/threads_post.txt`.

**Life posting schedule (next week):**

| Platform | Day | Time IST |
|---------|-----|---------|
| Instagram + Facebook | Tue | 8:00 AM |
| Threads | Tue | 8:00 PM |
| LinkedIn | Tue | 8:00 AM *(manual until clearance)* |

---

## Step 3 — Life LinkedIn: staged, post manually (~3 min)

LinkedIn is **manual until employer clearance** — staged in the DB but the daemon stays off. At the Tuesday 8 AM slot, post `linkedin_post.txt` by hand, then add the Medium link as the first comment.

Confirm it's staged:
```bash
sqlite3 data/scheduling.db \
  "SELECT platform, scheduled_at, substr(content_text,1,80) AS preview
   FROM posts
   WHERE status='pending' AND platform='linkedin'
     AND content_text LIKE '%life%'
   ORDER BY scheduled_at LIMIT 5"
```

Expected: 1 Life row, scheduled next Tuesday ~8:00 AM. (Do NOT start `scheduler.py` until cleared.)

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
