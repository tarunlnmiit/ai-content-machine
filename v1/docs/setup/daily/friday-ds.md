---
title: "Friday — DS Track (~20 min)"
type: doc
niche: data_science_tech
slug: friday-ds
tags: [content/doc, niche/data_science_tech]
---
> ⚠️ **PIPELINE UPDATED 2026-06-20 — canonical model: [`docs/pipeline-2026.md`](../../guides/pipeline-2026.md).**
> Twitter **dropped**. Instagram / Threads **auto-publish** via the Meta Graph API (`scripts/scheduler.py`); Facebook mirrors Instagram; LinkedIn **active** (employer cleared), blog link in the **pinned first comment**. Reels → **Instagram Reels + YouTube Shorts only**, ≈9 **distinct** reels/week (not ~56). Poetry short = **poem only**. Worksheet email CTA (DS/Life) is the owned channel (Substack retired). Run `python3 scripts/weekly_winners.py` before producing. Manual steps left: record · ~10-min approve · reply.
>
> Where any step below disagrees, the canonical doc wins.

# Friday — DS Track (~20 min)

Videos are live on YouTube from Thursday. Today: stage the DS LinkedIn post, gather the DS blog URL for captions, and queue the DS Twitter thread. **No Metricool/Publer** — IG / FB / Threads / Twitter are posted manually; LinkedIn is manual until employer clearance.

**Pivot rule:** Content produced this week posts NEXT week.

> **Reference docs:** `config/hashtags.json` (edit per-niche hashtag pools — no code change needed) · `docs/weekly-operating-guide.md` (scheduler.py setup) · `docs/weekly-runner.md` Step 22 (manual posting model)

---

## Step 1 — Stage DS LinkedIn + gather blog URL (~2 min)

```bash
python3 scripts/load_posts.py
```

Inserts the DS LinkedIn post into `data/scheduling.db` (held manual until clearance). No Metricool/Publer CSV.

### Gather the DS Medium URL for your captions

```bash
python3 -c "
import json, glob
for f in glob.glob('content/derivatives/{week}/*data_science_tech*/schedule.json'):
    d = json.load(open(f))
    print('Medium:', d.get('medium_url', 'MISSING'))
"
```

Record a missing URL so it's on hand when you post:
```bash
python3 scripts/update_schedule.py \
  --slug {ds_slug} --week {week} \
  --medium-url 'https://medium.com/@tarun-gupta/{ds_slug}'
```

---

## Step 2 — Post DS static content manually (~5 min)

Post by hand in the DS window (no Metricool import):

- **Instagram + Facebook** (@breathofdatascience): caption `content/derivatives/{week}/{ds_slug}/instagram_caption.txt`; image `assets/social_posts/{week}/{ds_slug}_instagram.png`. Paste the Medium URL inline.
- **Threads:** body `content/derivatives/{week}/{ds_slug}/threads_post.txt`.

**DS posting schedule (next week):**

| Platform | Day | Time IST |
|---------|-----|---------|
| Instagram + Facebook | Wed | 8:00 AM |
| Threads | Wed | 8:00 PM |
| LinkedIn | Tue | 8:00 AM *(manual until clearance)* |

---

## Step 3 — DS LinkedIn: staged, post manually (~3 min)

LinkedIn is **manual until employer clearance** — the post is staged in the DB but the daemon stays off. At the Tuesday 8 AM slot, post `linkedin_post.txt` by hand, then add the Medium link as the first comment.

Confirm it's staged:
```bash
sqlite3 data/scheduling.db \
  "SELECT platform, scheduled_at, substr(content_text,1,80) AS preview
   FROM posts
   WHERE status='pending' AND platform='linkedin'
     AND content_text LIKE '%data%'
   ORDER BY scheduled_at LIMIT 5"
```

Expected: 1 DS row, scheduled next Tuesday ~8:00 AM. (Do NOT start `scheduler.py` until cleared.)

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
