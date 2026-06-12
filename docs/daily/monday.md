# Monday — Generate All Blogs + Repurpose (~45 min)

All three niches processed today. By end of Monday: every blog draft, every derivative file, and every schedule.json for the week exists and is verified.

## Monday at a glance

| Time | Task | Output |
|------|------|--------|
| 9:00 AM | Check buffer + Notion for repeat angles | Decision: generate fresh vs. pull from buffer |
| 9:10 AM | Generate DS blog | `content/blogs/{week}/{ds_slug}.md` |
| 9:30 AM | Generate Life blog | `content/blogs/{week}/{life_slug}.md` |
| 9:50 AM | Generate Poetry blog | `content/blogs/{week}/{poetry_slug}.md` |
| 10:10 AM | Repurpose all 3 → derivatives | `content/derivatives/{week}/*/` |
| 10:25 AM | Fill PERSONAL_INSERT sections | Same blog files |
| 10:35 AM | Fetch blog images | `content/blogs/{week}/{slug}_images/` |
| 10:45 AM | Verify everything | `scripts/list_week_content.py {week} --plan` |

---

## Step 0 — Pre-flight: buffer + Notion check (5 min)

### 0a. Check buffer depth

```bash
for niche in data_science_tech life_self_dev poetry_quotes; do
  count=$(ls content/buffer/week-*/${niche}/*_meta.md 2>/dev/null | wc -l | tr -d ' ')
  echo "$niche: $count weeks buffered"
done
```

- Count ≥ 4 per niche → buffer healthy, proceed with fresh generation
- Any niche < 4 → flag for Sunday replenishment (still produce fresh this week)

### 0b. Check for pre-existing buffer content this week

```bash
ls content/buffer/week-1/data_science_tech/*_meta.md 2>/dev/null
ls content/buffer/week-1/life_self_dev/*_meta.md 2>/dev/null
ls content/buffer/week-1/poetry_quotes/*_meta.md 2>/dev/null
```

Buffer has content for a niche? → Skip Steps 1–3 for that niche; pull from `content/buffer/week-1/{niche}/` instead.

### 0c. Determine ISO week number

```bash
python3 -c "from scripts.lib.schedule_calc import get_iso_week; from datetime import date; print(get_iso_week(str(date.today())))"
# Example output: 2026-W24
```

Use this `YYYY-Wnn` string everywhere below as `{week}`.

### 0d. Query Notion for recent angles (REQUIRED before picking topics)

```bash
python3 scripts/query_notion_recent.py --days 90 --niche ds
python3 scripts/query_notion_recent.py --days 90 --niche life
python3 scripts/query_notion_recent.py --days 90 --niche poetry
```

Lists topics/angles published in last 90 days. **Never repeat an angle covered in this window.** If no script exists yet, check Notion Contents DB manually: filter Status = Published, sort by Publish Date descending, review Name + Topic columns.

---

## Step 1 — Generate DS blog (~15 min)

### 1a. Pick topic from weekly ideas

```bash
cat data/ideas/weekly_ideas.md
# DS section shows today's top 5 ideas ranked by score
# Also read data/kb/master_brief.md for voice context
```

Pick the top-scoring idea NOT covered in last 90 days (per Step 0d).

### 1b. Generate the blog

**Standard tutorial/explainer:**
```bash
python3 scripts/produce_blog.py \
  --topic 'YOUR EXACT TOPIC TITLE' \
  --niche ds
```

**With humanizer pass (removes AI-feel, recommended):**
```bash
python3 scripts/produce_blog.py \
  --topic 'YOUR EXACT TOPIC TITLE' \
  --niche ds \
  --humanize
```

**Listicle format (if topic suits it):**
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

Available `--voice` options: `analytical` (default) · `conversational` · `deletion` · `decision`
Available `--desire` options: `success` · `clarity` · `status` · `tribe` · `fear` · `enjoyment`

### 1c. Verify output

Output file: `content/blogs/{week}/YYYY-MM-DD_data_science_tech_{slug}.md`

```bash
python3 -c "
from scripts.lib.content_paths import blog_path
from datetime import date
print(blog_path('ds', 'your-topic-slug', str(date.today())))
"
```

Open and check:
- Title is compelling (not generic)
- Has a personal opening anecdote or example
- Word count ~1,200–2,000
- Contains `[PERSONAL_INSERT]` markers for custom sections
- Contains code blocks (DS only) with valid Python
- No banned words: "In conclusion" · "Dive into" · "Leverage" · "Game-changer" · "Synergy"

---

## Step 2 — Generate Life blog (~15 min)

```bash
python3 scripts/produce_blog.py \
  --topic 'YOUR LIFE TOPIC' \
  --niche life \
  --humanize
```

**Listicle:**
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

Check for `[PERSONAL_INSERT]` markers — Life blogs require the most personal content; these sections must be filled before publishing (Step 4).

---

## Step 3 — Generate Poetry blog (~15 min)

**From a poem/theme:**
```bash
python3 scripts/produce_blog.py \
  --topic 'YOUR POEM TITLE OR THEME' \
  --niche poetry \
  --humanize
```

**From an existing poem file:**
```bash
python3 scripts/ghostwrite.py \
  --source data/poems/{poem_slug}.txt \
  --niche poetry \
  --format blog
```

**Listicle (e.g., "5 Poems on Solitude"):**
```bash
python3 scripts/produce_blog.py \
  --topic 'Top 5 Poems About the Passage of Time' \
  --niche poetry \
  --listicle 5 \
  --humanize
```

Output: `content/blogs/{week}/YYYY-MM-DD_poetry_quotes_{slug}.md`

---

## Step 4 — Fill PERSONAL_INSERT sections (~10 min)

Find all placeholder markers across all three blogs:

```bash
grep -rn 'PERSONAL_INSERT' content/blogs/{week}/
```

Each marker looks like: `[PERSONAL_INSERT: describe a time when you felt overwhelmed by data]`

Open each blog and replace every `[PERSONAL_INSERT: ...]` with a genuine personal story or observation. These sections are what makes the content unique — do not leave them as placeholders.

Examples of good fills:
- "When I was working at [company], I remember spending 3 days debugging a pandas merge that had a silent type mismatch..."
- "I used to start every morning checking Twitter. The anxiety it created was..."

After filling, re-read the full blog once for flow.

---

## Step 5 — Fetch images for each blog (~5 min)

### Preview what will be fetched (dry run):
```bash
python3 scripts/fetch_images.py \
  --input content/blogs/{week}/{ds_slug}.md \
  --dry-run

python3 scripts/fetch_images.py \
  --input content/blogs/{week}/{life_slug}.md \
  --dry-run

python3 scripts/fetch_images.py \
  --input content/blogs/{week}/{poetry_slug}.md \
  --dry-run
```

### Fetch for real:
```bash
python3 scripts/fetch_images.py --input content/blogs/{week}/{ds_slug}.md
python3 scripts/fetch_images.py --input content/blogs/{week}/{life_slug}.md
python3 scripts/fetch_images.py --input content/blogs/{week}/{poetry_slug}.md
```

Images saved to: `content/blogs/{week}/{slug}_images/`

An `IMAGE_MAP.md` is created in the images directory — maps alt text to local filenames.

---

## Step 6 — Repurpose all blogs → derivatives (~10 min)

Run for all three blogs. These commands generate 10 derivative files per blog:

```bash
python3 scripts/repurpose_blog.py \
  --input content/blogs/{week}/{ds_slug}.md

python3 scripts/repurpose_blog.py \
  --input content/blogs/{week}/{life_slug}.md

python3 scripts/repurpose_blog.py \
  --input content/blogs/{week}/{poetry_slug}.md
```

### What each repurpose produces

Each run creates `content/derivatives/{week}/{slug}/` with:

| File | Content | Used by |
|------|---------|---------|
| `twitter_thread.txt` | 8–12 tweet thread (+ 2 hashtags on closing tweet) | Friday manual post |
| `linkedin_post.txt` | 1,200-char professional post (+ 4 hashtags) | scheduler.py auto |
| `instagram_caption.txt` | Caption + hashtags (up to 12) | Metricool CSV |
| `threads_post.txt` | Threads-formatted post (+ 3 hashtags) | Metricool CSV |
| `newsletter.txt` | Email newsletter (~400 words) | Beehiiv Sunday |
| `youtube_metadata.json` | Title, description, tags, chapter markers | Thursday YouTube upload |
| `youtube_shorts_metadata.json` | Short-form title, description, tags | Thursday Shorts upload |
| `slide_outline.json` | 7-slide structure | Tuesday slide deck gen |
| `thumbnail_brief.json` | Hook, visual direction, colors | Tuesday Remotion thumbnail |
| `claude_design_brief.json` | Emotional core, story frames | Tuesday social images |
| `schedule.json` | Computed publish timestamps | Friday Metricool CSV |

**Hashtags (auto, per platform):** all four social derivatives get hashtags — Claude's topical tags merged with a curated per-niche pool, deduped + capped (Twitter 2 · Threads 3 · LinkedIn 4 · Instagram 12). Edit the pools in `config/hashtags.json` — no code change needed.

### Verify schedule.json was created correctly

```bash
python3 -c "
import json, glob
for f in glob.glob('content/derivatives/{week}/*/schedule.json'):
    d = json.load(open(f))
    print(f.split('/')[-2], '→', d.get('long_form', {}).get('publish_at', 'MISSING'))
"
```

All three slugs should show a publish timestamp. If any show MISSING, re-run `repurpose_blog.py` for that slug.

---

## Step 7 — Verify complete (2 min)

```bash
python3 scripts/list_week_content.py {week} --plan
```

**What the output should show:**
- BLOGS: ✓ for all 3 niches (ds, life, poetry)
- DERIVATIVES: ✓ for all 3 (all 10 files present)
- IMAGES: ✓ for all 3 (images directory exists)
- SCHEDULE: timestamps visible for all 3

**If anything is missing:**
- Missing blog → re-run Step 1/2/3 for that niche
- Missing derivatives → re-run Step 6 for that slug
- Missing images → re-run Step 5 for that blog
- Missing schedule.json → re-run `repurpose_blog.py` for that slug

---

## Step 8 — Optional: Push to buffer

If you want to archive this week's content into the buffer for reuse:

```bash
# Preview first
python3 scripts/push_to_buffer.py --auto --dry-run

# Push all 3 niches
python3 scripts/push_to_buffer.py --auto
```

Decision: buffer accepts content if depth < 4 weeks for that niche. If already at 4 weeks, prints "stays live" and skips.

---

## File naming quick reference

| Niche | Blog filename pattern |
|-------|--------------------|
| DS | `content/blogs/{week}/YYYY-MM-DD_data_science_tech_{slug}.md` |
| Life | `content/blogs/{week}/YYYY-MM-DD_life_self_dev_{slug}.md` |
| Poetry | `content/blogs/{week}/YYYY-MM-DD_poetry_quotes_{slug}.md` |

Derivative directories:
```
content/derivatives/{week}/YYYY-MM-DD-data-science-tech-{slug-50}/
content/derivatives/{week}/YYYY-MM-DD-life-self-dev-{slug-50}/
content/derivatives/{week}/YYYY-MM-DD-poetry-quotes-{slug-50}/
```
(Slug truncated at 50 chars, spaces → hyphens.)
