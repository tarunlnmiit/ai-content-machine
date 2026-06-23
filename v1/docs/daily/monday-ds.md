> ⚠️ **PIPELINE UPDATED 2026-06-20 — canonical model: [`docs/pipeline-2026.md`](../pipeline-2026.md).**
> Twitter **dropped**. Instagram / Threads **auto-publish** via the Meta Graph API (`scripts/scheduler.py`); Facebook mirrors Instagram; LinkedIn **active** (employer cleared), blog link in the **pinned first comment**. Reels → **Instagram Reels + YouTube Shorts only**, ≈9 **distinct** reels/week (not ~56). Poetry short = **poem only**. Worksheet email CTA (DS/Life) is the owned channel (Substack retired). Run `python3 scripts/weekly_winners.py` before producing. Manual steps left: record · ~10-min approve · reply.
>
> Where any step below disagrees, the canonical doc wins.

# Monday — DS Track (~45 min)

Generate the Data Science blog, fill personal inserts, fetch images, and repurpose to derivatives.

> **Reference docs:** `docs/weekly-operating-guide.md` · `prompts/medium-virality-prompt.md` · `data/analytics/medium-stats-2026.md` · `data/kb/projects.json` (build-in-public project keys — pass via `--project` flag) · `data/kb/voice/` (DS hook archetypes + idea bank)

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

### Recent DS angles (required) — from shipped blog slugs
```bash
python3 -c "
import glob, os
from datetime import datetime, timedelta
cutoff = datetime.today() - timedelta(days=90)
seen = set()
for path in sorted(glob.glob('content/blogs/2026-W*/*')):
    name = os.path.basename(path)
    slug = name[:-7] if name.endswith('_images') else (name[:-3] if name.endswith('.md') else None)
    if not slug or 'data_science_tech' not in slug: continue
    try: d = datetime.strptime(slug[:10], '%Y-%m-%d')
    except ValueError: continue
    if d >= cutoff: seen.add((slug[:10], slug.split('data_science_tech_',1)[-1].replace('-',' ')))
for dt, topic in sorted(seen): print(' ', dt, topic)
"
```
Never repeat an angle covered in the last 90 days. (Source = `content/blogs/` slugs, not the tracker — the tracker drops titles when a week commits.)

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
- **Title formula** — uses one of: specific incident / counter-intuitive result / specific number + outcome. Kill: "Everything You Need to Know About X" / "The Ultimate Guide to Y" / "Why Z Matters"
- **First paragraph test** — remove it mentally: if the article still reads fine from paragraph 2, it's throat-clearing; rewrite so the opening line *is* the hook
- **Subheadings are hooks**, not labels — "The Bug That Cost Me 3 Days" not "The Problem"
- **Shareable sentence** — find the one line a stranger would screenshot; mark it `[QUOTABLE]` in the draft
- **Ending** — no bullet recap, no "Let me know your thoughts in the comments"; last line carries weight

> ### ⚡ Virality angle — DS (from `data/kb/reels/06_mavgpt_caption_formula.md`)
> The same caption-IS-product logic that drives the @mavgpt reels applies to the blog:
> - **Title states the OUTCOME, not the topic.** "The Type Error That Makes Your Analysis Wrong Without Crashing" beats "Variables, Data Types & Structures." Pattern: `[the dramatic result]` or `[N] hidden X for [tool]` — never "Tutorial 2/10" as the lead.
> - **The post IS the product.** Put the full, immediately-usable value in the body verbatim — runnable code, the actual prompt, the exact steps. A reader should be able to act from the post alone, not a teaser that defers to a link.
> - **Serialize for returning readers** — name a series ("Prompt Anatomy", "DS Tools") but keep the *title* outcome-led; the series number is a subtitle, not the hook.
> - Honesty guardrail: claim only what you can show. No "this 10x'd my salary" headlines.

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
for f in glob.glob('content/derivatives/*/*data_science_tech*/schedule.json'):
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
