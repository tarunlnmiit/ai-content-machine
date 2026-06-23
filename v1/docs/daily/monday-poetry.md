> ⚠️ **PIPELINE UPDATED 2026-06-20 — canonical model: [`docs/pipeline-2026.md`](../pipeline-2026.md).**
> Twitter **dropped**. Instagram / Threads **auto-publish** via the Meta Graph API (`scripts/scheduler.py`); Facebook mirrors Instagram; LinkedIn **active** (employer cleared), blog link in the **pinned first comment**. Reels → **Instagram Reels + YouTube Shorts only**, ≈9 **distinct** reels/week (not ~56). Poetry short = **poem only**. Worksheet email CTA (DS/Life) is the owned channel (Substack retired). Run `python3 scripts/weekly_winners.py` before producing. Manual steps left: record · ~10-min approve · reply.
>
> Where any step below disagrees, the canonical doc wins.

# Monday — Poetry Track (~45 min)

Generate the Poetry blog, fill personal inserts, fetch images, and repurpose to derivatives.

> **Reference docs:** `docs/weekly-operating-guide.md` · `prompts/medium-virality-prompt.md` · `data/analytics/medium-stats-2026.md` · `data/kb/voice/` (emotional hook archetypes 9–10 + idea bank themes 11–14)

---

## Preflight (~10 min)

### Buffer check
```bash
count=$(ls content/buffer/week-*/poetry_quotes/*_meta.md 2>/dev/null | wc -l | tr -d ' ')
echo "Poetry buffer: $count weeks"
```
Count < 4 → flag for Sunday replenishment (still generate fresh this week).

### Pre-existing buffer this week
```bash
ls content/buffer/week-1/poetry_quotes/*_meta.md 2>/dev/null
```
If exists → skip Steps 1–3; pull from `content/buffer/week-1/poetry_quotes/` instead.

### ISO week
```bash
python3 -c "from scripts.lib.schedule_calc import get_iso_week; from datetime import date; print(get_iso_week(str(date.today())))"
```
Use this `YYYY-Wnn` as `{week}` everywhere below.

### Recent Poetry angles (required) — from shipped blog slugs
```bash
python3 -c "
import glob, os
from datetime import datetime, timedelta
cutoff = datetime.today() - timedelta(days=90)
seen = set()
for path in sorted(glob.glob('content/blogs/2026-W*/*')):
    name = os.path.basename(path)
    slug = name[:-7] if name.endswith('_images') else (name[:-3] if name.endswith('.md') else None)
    if not slug or 'poetry_quotes' not in slug: continue
    try: d = datetime.strptime(slug[:10], '%Y-%m-%d')
    except ValueError: continue
    if d >= cutoff: seen.add((slug[:10], slug.split('poetry_quotes_',1)[-1].replace('-',' ')))
for dt, topic in sorted(seen): print(' ', dt, topic)
"
```
Never repeat an angle covered in the last 90 days. (Source = `content/blogs/` slugs, not the tracker — the tracker drops titles when a week commits.)

---

## Step 1 — Generate Poetry blog (~15 min)

### Pick topic
```bash
cat data/ideas/weekly_ideas.md
# Poetry section: top 5 ideas ranked by score
cat data/kb/master_brief.md  # voice context
```

**Idea scoring (updated):** Poetry ideas now rank higher when titles contain fear, pain, curiosity-gap, or dark-emotion signals. Prefer a fear/curiosity-trigger title over a soft contemplative one — the scoring already surfaces these first.

**Hook reference:** `data/kb/voice/01_hook_library.md` — archetypes 9 (Fear Trigger) and 10 (Curiosity Gap) are new. High-emotion idea bank: `data/kb/voice/02_idea_bank.md` themes 11–14 (3am fear, grief specifics, hidden self, what you traded). Use these if the auto-ranked list feels generic.

### Generate from a poem/theme
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

### Verify
- Title compelling, evocative
- Personal voice — not academic
- Word count ~1,200–2,000
- Contains `[PERSONAL_INSERT]` markers
- No banned words: "In conclusion" · "Dive into" · "Leverage" · "Game-changer" · "Synergy"
- **Title formula** — names a specific emotion or paradox; kill vague titles ("Love Is Complicated") and generic ones ("A Poem About Grief")
- **First paragraph test** — remove it mentally: if the poem or essay reads fine from line 2, rewrite so the opening names the sensation immediately
- **Subheadings** (if present) — evocative lines, not section labels
- **Shareable line** — the couplet or sentence that makes a reader stop; mark it `[QUOTABLE]` in the draft
- **Ending** — carries the emotional landing; no summary, no "share with someone who needs this"

> ### ⚡ Virality angle — Poetry (from `data/kb/voice/poetry_formula.md`)
> Reverse-engineered from @christi.steyn + @joeykidney. The poem is a projective surface — readers feel *seen*, then share their own story:
> - **Concrete nouns over abstract emotion.** Every line gets a physical object. "I would plant flowers on your pillow" beats "I love you so much." Tarun's edge: data/math precision — "the probability of finding you in all possible futures is less than one."
> - **One playful/mundane detail inside the tenderness** keeps it from feeling greeting-card ("but bird language is not on duolingo").
> - **Permission close** outperforms a sad close — "you are allowed to be this" / "and that is enough."
> - **Never explain the poem.** No "this is about grief," no "I wrote this when…" — context kills the projective magic.
> - The strongest single line can BE the whole social caption later (save-trigger); write toward one screenshot-worthy line.

---

## Step 2 — Fill PERSONAL_INSERT sections (~10 min)

```bash
grep -n 'PERSONAL_INSERT' content/blogs/{week}/YYYY-MM-DD_poetry_quotes_{slug}.md
```

Replace every `[PERSONAL_INSERT: ...]` with a genuine moment — the specific memory, image, or feeling that connects to the poem's theme.

Re-read full blog once for flow after filling.

---

## Step 3 — Fetch images (~5 min)

```bash
python3 scripts/fetch_images.py \
  --input content/blogs/{week}/YYYY-MM-DD_poetry_quotes_{slug}.md \
  --dry-run
```
Review, then:
```bash
python3 scripts/fetch_images.py \
  --input content/blogs/{week}/YYYY-MM-DD_poetry_quotes_{slug}.md
```
Output: `content/blogs/{week}/{slug}_images/` + `IMAGE_MAP.md`

---

## Step 4 — Repurpose → derivatives (~5 min)

```bash
python3 scripts/repurpose_blog.py \
  --input content/blogs/{week}/YYYY-MM-DD_poetry_quotes_{slug}.md
```

Creates `content/derivatives/{week}/{slug}/` with:
`twitter_thread.txt` · `linkedin_post.txt` · `instagram_caption.txt` · `threads_post.txt` · `newsletter.txt` · `youtube_metadata.json` · `youtube_shorts_metadata.json` · `slide_outline.json` · `thumbnail_brief.json` · `claude_design_brief.json` · `schedule.json`

### Verify schedule.json
```bash
python3 -c "
import json, glob
for f in glob.glob('content/derivatives/{week}/*poetry_quotes*/schedule.json'):
    d = json.load(open(f))
    print(f.split('/')[-2], '→', d.get('long_form', {}).get('publish_at', 'MISSING'))
"
```

---

## Verify

```bash
python3 scripts/list_week_content.py {week} --plan
```

Poetry row should show ✓ for: BLOGS · DERIVATIVES · IMAGES · SCHEDULE
