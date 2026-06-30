> ⚠️ **PIPELINE UPDATED 2026-06-20 — canonical model: [`docs/pipeline-2026.md`](../../guides/pipeline-2026.md).**
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

> **DS publishes 2 blogs/week — one TUTORIAL, one NEWS/OPINION.**
> Week cadence: Monday = TUTORIAL · Thursday = NEWS (or whichever day suits your schedule, but keep the split).
> Use `--type tutorial` or `--type news` to enforce the right format. Omitting `--type` is fine for single non-typed posts.

### Pick topic (interactive — script suggests 5 options)
```bash
# TUTORIAL week (code-first, runnable Python)
python3 scripts/produce_blog.py \
  --niche ds \
  --type tutorial \
  --humanize

# NEWS/OPINION week (no code, editorial take)
python3 scripts/produce_blog.py \
  --niche ds \
  --type news \
  --humanize
```

The script will:
1. Fetch live Google Suggest + Medium signals for the type you chose
2. Show 5 topic options — each pulls a different emotion lever (FOMO / FEAR / CURIOSITY GAP / COUNTERINTUITIVE / ASPIRATION / INSIDER SECRET / SOCIAL PROOF) + niche-routed trigger vocabulary, so the angles arrive emotionally charged → you pick one
3. Ask for your personal angle (stories, opinions, examples → Claude polishes, never quotes verbatim)
4. Show 5 title options across FEAR / ANXIETY / CURIOSITY GAP / COUNTERINTUITIVE / INSIDER levers → you pick one
5. Generate and save to `content/blogs/{week}/YYYY-MM-DD_data_science_tech_{slug}.md`

**Type `skip` at any prompt** (topic pick, personal angle, title pick — and interview/poem questions) and Claude answers it **on your behalf in your voice** (it reads `data/kb/master_brief.md` for authenticity). Lets you run a fully hands-off draft, or skip just the steps you don't have input for.

**If you already have a topic:**
```bash
python3 scripts/produce_blog.py \
  --topic 'Your topic here' \
  --niche ds \
  --type tutorial \
  --humanize
```

**Listicle format:**
```bash
python3 scripts/produce_blog.py \
  --niche ds \
  --type tutorial \
  --listicle 5 \
  --humanize
```

**Build-in-public angle (adds project virality context):**
```bash
python3 scripts/produce_blog.py \
  --niche ds \
  --type news \
  --project free_tool_ds \
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

### Verify — TUTORIAL posts
- Title compelling (not generic)
- Has personal opening anecdote
- Word count ~1,200–2,000
- Contains `[PERSONAL_INSERT]` markers
- Contains **at least 2 runnable Python code blocks** (not pseudocode)
- Code blocks appear inline (not batched at the end)
- No banned words: "In conclusion" · "Dive into" · "Leverage" · "Game-changer" · "Synergy"
- **Subheadings are hooks**, not labels — "The Bug That Cost Me 3 Days" not "The Problem"
- **Shareable sentence** marked `[QUOTABLE]`
- **Ending** — last line carries weight; no bullet recap

### Verify — NEWS/OPINION posts
- Title is a declarative opinion or tension-loaded claim, not a question or label
- Word count ~900–1,500
- **Zero code blocks** — any code reference is prose-level, not a snippet
- Has a clear editorial position (not both-sides-ism)
- Cites specific things: tool names, company names, dates, numbers
- No banned words
- **Subheadings are hooks**
- **Shareable sentence** marked `[QUOTABLE]`
- **Ending** — an implication, not a summary

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

## Step 4 — Repurpose → all derivatives (~10 min)

```bash
python3 scripts/repurpose_blog.py \
  --input content/blogs/{week}/YYYY-MM-DD_data_science_tech_{slug}.md
```

**Phase 1 (single Claude call):** `linkedin_post.txt` (+`linkedin_second_comment.txt` = blog link) · `linkedin_document_caption.txt` (slide deck post body) · `instagram_caption.txt` (+`instagram_caption_clean.txt`) · `newsletter.txt` · `youtube_metadata.json` · `youtube_shorts_metadata.json` · `slide_outline.json` · `polls.json` · `claude_design_brief.json` · `schedule.json`

LinkedIn comment order: **1st comment = Worksheet link** (written in Phase 2), **2nd comment = Blog link** (Phase 1).

**Phase 2 (auto, sequential):**
- `content/worksheets/{week}/{slug}_worksheet.json` — worksheet outline (structure + sections)
- `content/prompts/{week}/{slug}_worksheet_prompt.txt` — Canva design prompt (paste into Canva AI)
- Blog CTA inject — appends worksheet link block to the `.md` file (if worksheet published)
- `linkedin_first_comment.txt` — worksheet URL (pinned 1st, if worksheet published)
- `assets/slides/{week}/{slug}_slides.html` — slide deck
- `assets/carousels/{slug}_carousel.html` — IG carousel HTML (+ Playwright PNG export)
- `content/derivatives/{week}/{slug}/ig_reel_brief.md` — IG reel brief
- `content/scripts/{week}/{slug}_yt.md` — YT filming script

All Phase 2 steps are idempotent — skip if output already exists.

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
