# Monday — DS Track (~45 min)

Generate the Data Science blog, fill personal inserts, fetch images, and repurpose to derivatives.

---

## Preflight (~10 min)

### Buffer check
```bash
count=$(ls content/buffer/week-*/data_science_tech/*_meta.md 2>/dev/null | wc -l | tr -d ' ')
echo "DS buffer: $count weeks"
```
Count < 4 → flag for Sunday replenishment (still generate fresh this week).

### Pre-existing buffer this week
```bash
ls content/buffer/week-1/data_science_tech/*_meta.md 2>/dev/null
```
If exists → skip Steps 1–3; pull from `content/buffer/week-1/data_science_tech/` instead.

### ISO week
```bash
python3 -c "from scripts.lib.schedule_calc import get_iso_week; from datetime import date; print(get_iso_week(str(date.today())))"
```
Use this `YYYY-Wnn` as `{week}` everywhere below.

### Notion: recent DS angles (required)
```bash
python3 scripts/query_notion_recent.py --days 90 --niche ds
```
Never repeat an angle covered in the last 90 days.

---

## Step 1 — Generate DS blog (~15 min)

### Pick topic
```bash
cat data/ideas/weekly_ideas.md
# DS section: top 5 ideas ranked by score
cat data/kb/master_brief.md  # voice context
```
Pick the top-scoring idea NOT in the last 90 days (per preflight).

### Generate
```bash
python3 scripts/produce_blog.py \
  --topic 'YOUR EXACT TOPIC TITLE' \
  --niche ds \
  --humanize
```

**Listicle format:**
```bash
python3 scripts/produce_blog.py \
  --topic 'Top 5 Python Libraries for Data Scientists' \
  --niche ds \
  --listicle 5 \
  --humanize
```

**From your own notes/transcript:**
```bash
python3 scripts/ghostwrite.py \
  --source /path/to/notes.txt \
  --niche ds \
  --voice analytical
```
Available `--voice`: `analytical` (default) · `conversational` · `deletion` · `decision`

Output: `content/blogs/{week}/YYYY-MM-DD_data_science_tech_{slug}.md`

### Verify
- Title compelling (not generic)
- Has personal opening anecdote
- Word count ~1,200–2,000
- Contains `[PERSONAL_INSERT]` markers
- Contains code blocks with valid Python
- No banned words: "In conclusion" · "Dive into" · "Leverage" · "Game-changer" · "Synergy"

---

## Step 2 — Fill PERSONAL_INSERT sections (~10 min)

```bash
grep -n 'PERSONAL_INSERT' content/blogs/{week}/YYYY-MM-DD_data_science_tech_{slug}.md
```

Replace every `[PERSONAL_INSERT: ...]` with a genuine story from your DS experience.

Examples:
- "When I was debugging a pandas merge that had a silent type mismatch..."
- "I spent 3 days on a feature engineering step that shaved 12 points off RMSE..."

Re-read full blog once for flow after filling.

---

## Step 3 — Fetch images (~5 min)

```bash
python3 scripts/fetch_images.py \
  --input content/blogs/{week}/YYYY-MM-DD_data_science_tech_{slug}.md \
  --dry-run
```
Review what will be fetched, then:
```bash
python3 scripts/fetch_images.py \
  --input content/blogs/{week}/YYYY-MM-DD_data_science_tech_{slug}.md
```
Output: `content/blogs/{week}/{slug}_images/` + `IMAGE_MAP.md`

---

## Step 4 — Repurpose → derivatives (~5 min)

```bash
python3 scripts/repurpose_blog.py \
  --input content/blogs/{week}/YYYY-MM-DD_data_science_tech_{slug}.md
```

Creates `content/derivatives/{week}/{slug}/` with:
`twitter_thread.txt` · `linkedin_post.txt` · `instagram_caption.txt` · `threads_post.txt` · `newsletter.txt` · `youtube_metadata.json` · `youtube_shorts_metadata.json` · `slide_outline.json` · `thumbnail_brief.json` · `claude_design_brief.json` · `schedule.json`

### Verify schedule.json
```bash
python3 -c "
import json, glob
for f in glob.glob('content/derivatives/{week}/*data_science_tech*/schedule.json'):
    d = json.load(open(f))
    print(f.split('/')[-2], '→', d.get('long_form', {}).get('publish_at', 'MISSING'))
"
```

---

## Verify

```bash
python3 scripts/list_week_content.py {week} --plan
```

DS row should show ✓ for: BLOGS · DERIVATIVES · IMAGES · SCHEDULE
