# Friday — Poetry Track (~20 min)

Videos are live on YouTube from Thursday. Today: stage the Poetry LinkedIn post, gather the Poetry blog URL for captions, and queue the Poetry Twitter thread. **No Metricool/Publer** — IG / FB / Threads / Twitter are posted manually; LinkedIn is manual until employer clearance.

**Pivot rule:** Content produced this week posts NEXT week.

> **Reference docs:** `config/hashtags.json` (edit per-niche hashtag pools — no code change needed) · `docs/weekly-operating-guide.md` (scheduler.py setup) · `docs/weekly-runner.md` Step 22 (manual posting model)

---

## Step 1 — Stage Poetry LinkedIn + gather blog URL (~2 min)

```bash
python3 scripts/load_posts.py
```

Inserts the Poetry LinkedIn post into `data/scheduling.db` (held manual until clearance). No Metricool/Publer CSV.

> Note: Poetry often skips LinkedIn — only stage/post it if the piece translates to a professional context.

### Gather the Poetry Medium URL for your captions

```bash
python3 -c "
import json, glob
for f in glob.glob('content/derivatives/{week}/*poetry_quotes*/schedule.json'):
    d = json.load(open(f))
    print('Medium:', d.get('medium_url', 'MISSING'))
"
```

Record a missing URL so it's on hand when you post:
```bash
python3 scripts/update_schedule.py \
  --slug {poetry_slug} --week {week} \
  --medium-url 'https://medium.com/@tarun-gupta/{poetry_slug}'
```

---

## Step 2 — Post Poetry static content manually (~5 min)

Post by hand in the Poetry window (no Metricool import):

- **Instagram + Facebook** (@mistakenlyhuman): caption `content/derivatives/{week}/{poetry_slug}/instagram_caption.txt`; image `assets/social_posts/{week}/{poetry_slug}_instagram.png`. Poetry caption is often the poem verbatim — save trigger, not a link dump.
- **Threads:** body `content/derivatives/{week}/{poetry_slug}/threads_post.txt`.

**Poetry posting schedule (next week):**

| Platform | Day | Time IST |
|---------|-----|---------|
| Instagram + Facebook | Fri | 10:00 AM |
| Threads | Fri | 12:00 PM |
| LinkedIn | Tue | 8:00 AM *(manual until clearance, often skipped)* |

---

## Step 3 — Poetry LinkedIn: staged, post manually (~3 min)

If you staged a Poetry LinkedIn post, it's **manual until employer clearance** — daemon stays off. Post `linkedin_post.txt` by hand at the slot, then add the Medium link as the first comment.

Confirm it's staged:
```bash
sqlite3 data/scheduling.db \
  "SELECT platform, scheduled_at, substr(content_text,1,80) AS preview
   FROM posts
   WHERE status='pending' AND platform='linkedin'
     AND content_text LIKE '%poem%'
   ORDER BY scheduled_at LIMIT 5"
```

(Do NOT start `scheduler.py` until cleared.)

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
5. CTA: "Read the full piece → medium.com/@tarun-gupta/{poetry_slug}"

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

- [ ] Static captions/images ready for all 3 niches (IG + Threads)
- [ ] Reminders set for next-week posting windows: Tue (Life), Wed (DS), Fri (Poetry)
- [ ] LinkedIn queue has up to 3 pending posts in DB (daemon OFF until clearance)
- [ ] Twitter reminders set: Life Mon 1 PM, DS (flexible), Poetry Fri 12 PM
- [ ] YouTube videos uploaded and scheduled (done Thursday)
- [ ] Notion status: Uploaded for all 3 content items
- [ ] Buffer depth ≥ 4 for all 3 niches

```bash
python3 scripts/sync_tracker.py
# → data/content_tracker.csv updated with this week's final state

python3 scripts/generate_posting_tracker.py --year 2026
# → output/trackers/annual-tracker-2026.xlsx updated with new content titles
```
