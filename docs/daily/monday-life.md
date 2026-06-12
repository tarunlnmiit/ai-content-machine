# Monday — Life Track (~45 min)

Generate the Life & Self-Development blog, fill personal inserts, fetch images, and repurpose to derivatives.

---

## Preflight (~10 min)

### Buffer check
```bash
count=$(ls content/buffer/week-*/life_self_dev/*_meta.md 2>/dev/null | wc -l | tr -d ' ')
echo "Life buffer: $count weeks"
```
Count < 4 → flag for Sunday replenishment (still generate fresh this week).

### Pre-existing buffer this week
```bash
ls content/buffer/week-1/life_self_dev/*_meta.md 2>/dev/null
```
If exists → skip Steps 1–3; pull from `content/buffer/week-1/life_self_dev/` instead.

### ISO week
```bash
python3 -c "from scripts.lib.schedule_calc import get_iso_week; from datetime import date; print(get_iso_week(str(date.today())))"
```
Use this `YYYY-Wnn` as `{week}` everywhere below.

### Notion: recent Life angles (required)
```bash
python3 scripts/query_notion_recent.py --days 90 --niche life
```
Never repeat an angle covered in the last 90 days.

---

## Step 1 — Generate Life blog (~15 min)

### Pick topic
```bash
cat data/ideas/weekly_ideas.md
# Life section: top 5 ideas ranked by score
cat data/kb/master_brief.md  # voice context
```

### Generate
```bash
python3 scripts/produce_blog.py \
  --topic 'YOUR LIFE TOPIC' \
  --niche life \
  --humanize
```

**Listicle format:**
```bash
python3 scripts/produce_blog.py \
  --topic 'Top 3 Habits That Changed My Morning' \
  --niche life \
  --listicle 3 \
  --humanize
```

**From notes:**
```bash
python3 scripts/ghostwrite.py \
  --source /path/to/notes.txt \
  --niche life \
  --voice conversational
```

Output: `content/blogs/{week}/YYYY-MM-DD_life_self_dev_{slug}.md`

### Verify
- Title compelling (not generic)
- Has personal opening story
- Word count ~1,200–2,000
- Contains `[PERSONAL_INSERT]` markers — Life blogs require the most personal content
- No banned words: "In conclusion" · "Dive into" · "Leverage" · "Game-changer" · "Synergy"

---

## Step 2 — Fill PERSONAL_INSERT sections (~10 min)

```bash
grep -n 'PERSONAL_INSERT' content/blogs/{week}/YYYY-MM-DD_life_self_dev_{slug}.md
```

Replace every `[PERSONAL_INSERT: ...]` with a genuine personal story. These sections are what makes Life content unique — do not leave as placeholders.

Examples:
- "I used to start every morning checking Twitter. The anxiety it created was..."
- "The moment I realised this habit was costing me more than it was giving..."

Re-read full blog once for flow after filling.

---

## Step 3 — Fetch images (~5 min)

```bash
python3 scripts/fetch_images.py \
  --input content/blogs/{week}/YYYY-MM-DD_life_self_dev_{slug}.md \
  --dry-run
```
Review, then:
```bash
python3 scripts/fetch_images.py \
  --input content/blogs/{week}/YYYY-MM-DD_life_self_dev_{slug}.md
```
Output: `content/blogs/{week}/{slug}_images/` + `IMAGE_MAP.md`

---

## Step 4 — Repurpose → derivatives (~5 min)

```bash
python3 scripts/repurpose_blog.py \
  --input content/blogs/{week}/YYYY-MM-DD_life_self_dev_{slug}.md
```

Creates `content/derivatives/{week}/{slug}/` with:
`twitter_thread.txt` · `linkedin_post.txt` · `instagram_caption.txt` · `threads_post.txt` · `newsletter.txt` · `youtube_metadata.json` · `youtube_shorts_metadata.json` · `slide_outline.json` · `thumbnail_brief.json` · `claude_design_brief.json` · `schedule.json`

### Verify schedule.json
```bash
python3 -c "
import json, glob
for f in glob.glob('content/derivatives/{week}/*life_self_dev*/schedule.json'):
    d = json.load(open(f))
    print(f.split('/')[-2], '→', d.get('long_form', {}).get('publish_at', 'MISSING'))
"
```

---

## Verify

```bash
python3 scripts/list_week_content.py {week} --plan
```

Life row should show ✓ for: BLOGS · DERIVATIVES · IMAGES · SCHEDULE
