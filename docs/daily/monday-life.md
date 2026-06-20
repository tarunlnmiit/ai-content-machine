> ⚠️ **PIPELINE UPDATED 2026-06-20 — canonical model: [`docs/pipeline-2026.md`](../pipeline-2026.md).**
> Twitter **dropped**. Instagram / Threads **auto-publish** via the Meta Graph API (`scripts/scheduler.py`); Facebook mirrors Instagram; LinkedIn **active** (employer cleared), blog link in the **pinned first comment**. Reels → **Instagram Reels + YouTube Shorts only**, ≈9 **distinct** reels/week (not ~56). Poetry short = **poem only**. Worksheet email CTA (DS/Life) is the owned channel (Substack retired). Run `python3 scripts/weekly_winners.py` before producing. Manual steps left: record · ~10-min approve · reply.
>
> Where any step below disagrees, the canonical doc wins.

# Monday — Life Track (~45 min)

Generate the Life & Self-Development blog, fill personal inserts, fetch images, and repurpose to derivatives.

> **Reference docs:** `docs/weekly-operating-guide.md` · `prompts/medium-virality-prompt.md` · `data/analytics/medium-stats-2026.md` · `data/kb/projects.json` (build-in-public project keys — pass via `--project` flag) · `data/kb/voice/` (Life hook archetypes + high-emotion idea bank)

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

### Recent Life angles (required) — from shipped blog slugs
```bash
python3 -c "
import glob, os
from datetime import datetime, timedelta
cutoff = datetime.today() - timedelta(days=90)
seen = set()
for path in sorted(glob.glob('content/blogs/2026-W*/*')):
    name = os.path.basename(path)
    slug = name[:-7] if name.endswith('_images') else (name[:-3] if name.endswith('.md') else None)
    if not slug or 'life_self_dev' not in slug: continue
    try: d = datetime.strptime(slug[:10], '%Y-%m-%d')
    except ValueError: continue
    if d >= cutoff: seen.add((slug[:10], slug.split('life_self_dev_',1)[-1].replace('-',' ')))
for dt, topic in sorted(seen): print(' ', dt, topic)
"
```
Never repeat an angle covered in the last 90 days. (Source = `content/blogs/` slugs, not the tracker — the tracker drops titles when a week commits.)

---

## Step 1 — Generate Life blog (~15 min)

### Pick topic
```bash
cat data/ideas/weekly_ideas.md
# Life section: top 5 ideas ranked by score
cat data/kb/master_brief.md  # voice context
```

**Idea scoring (updated):** Life ideas now rank higher when titles contain fear, curiosity-gap, or strong-emotion signals. Prefer the top idea unless it's weak — in that case, look for one that triggers fear or curiosity over a generic self-help angle.

**Hook reference:** `data/kb/voice/01_hook_library.md` — archetypes 9 (Fear Trigger) and 10 (Curiosity Gap) are new. High-emotion idea bank: `data/kb/voice/02_idea_bank.md` themes 15–18 (slow fade, habit honesty, the lie, why smart people stay stuck). Use these if the auto-ranked list feels flat.

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
- **Title formula** — uses one of: specific incident / named lesson / counter-intuitive result. Kill: "Everything You Need to Know About X" / "Why Z Matters" / anything that describes content without tension
- **First paragraph test** — remove it mentally: if the article reads fine from paragraph 2, it's throat-clearing; rewrite so the opening line *is* the specific moment
- **Subheadings are hooks**, not labels — "The Call That Made Me Realise" not "The Turning Point"
- **Shareable sentence** — the one line someone would DM to a friend; mark it `[QUOTABLE]` in the draft
- **Ending** — no bullet recap, no "Let me know your thoughts in the comments"; end on the quotable sentence, a question, or a one-sentence implication

> ### ⚡ Virality angle — Life (from `data/kb/voice/life_formula.md`)
> Reverse-engineered from @ankurwarikoo + @joeykidney. The teach-don't-inspire system:
> - **Title = a declarative claim, not a question.** "Self-discipline is a myth" beats "Is self-discipline real?" The reader reacts (agree/disagree) before they click.
> - **The mechanism line is the product.** Name *why* this keeps happening to the reader in one precise sentence ("you don't procrastinate from laziness — the task has no clear first step"). That line is the `[QUOTABLE]`.
> - **Unexpected-source angle fits Tarun exactly** — find the life truth in data/probability/systems ("What Bayesian thinking taught me about regret"). Merges DS + Life without forcing it.
> - **Lead from the analytical identity as the disarmer** for heavy topics ("I work with data, I don't feel things easily, and yet…").
> - **No motivational crescendo.** Close flat and instructional ("start with the one that stings"), never "YOU'VE GOT THIS."

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
