> ⚠️ **PIPELINE UPDATED 2026-06-20 — canonical model: [`docs/pipeline-2026.md`](../pipeline-2026.md).**
> Twitter **dropped**. Instagram / Threads **auto-publish** via the Meta Graph API (`scripts/scheduler.py`); Facebook mirrors Instagram; LinkedIn **active** (employer cleared) with the blog link in the **pinned first comment**. Reels → **Instagram Reels + YouTube Shorts only**, ≈9 **distinct** reels/week (not ~56). 3 long-form (1/niche). Poetry short = **poem only**; poetry Medium = poem + 150–350w essay. Worksheet email CTA (DS/Life) is the owned channel (Substack retired). Run `python3 scripts/weekly_winners.py` before producing. Only manual steps left: record · ~10-min approve · reply to comments/DMs.
>
> Where any step below disagrees with this banner or the canonical doc, the canonical doc wins.

# Monday — Generate All Blogs + Repurpose (~45 min)

All three niches processed today. By end of Monday: every blog draft, every derivative file, and every schedule.json for the week exists and is verified.

> **Reference docs:**
> - First time running the machine? Complete `docs/one-time-platform-setup.md` before starting week 1.
> - Full weekly rhythm and task-batching overview: `docs/weekly-operating-guide.md`
> - How the 6 AM ideas script works and how to set it up: `docs/launchd-daily-ideas.md`
> - Medium virality framework (full prompt + real examples): `prompts/medium-virality-prompt.md`
> - Real read-ratio data from 75 Tarun articles (June 2026): `data/analytics/medium-stats-2026.md`
> - Brand colors, AutoTune temperatures, and model routing (single source of truth): `data/brand/brand_kit.yaml`
> - Virality KB for Life/Poetry — read the index first: `data/kb/voice/INDEX.md`
> - Virality KB for DS/build-in-public — read the index first: `data/kb/reels/INDEX.md`
> - Build-in-public projects (angle + DM keyword + cadence per project): `data/kb/projects.json`
> - Blog writing agent (use when prompting Claude to write long-form): `prompts/writing_agent.md`
> - Ghostwriter agent (use when converting your own notes/transcript to a blog): `prompts/ghostwriter_agent.md`

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

### 0d. Recent angles (REQUIRED before picking topics) — from shipped blog slugs

Source = `content/blogs/2026-W*/` slugs, NOT the tracker (the tracker drops `Content Title` when a week commits, so it can't list recent angles). Covers every week — `.md` for recent, `_images/` dirs for older.

```bash
python3 -c "
import glob, os
from datetime import datetime, timedelta
cutoff = datetime.today() - timedelta(days=90)
NICHE = {'data_science_tech':'DS','life_self_dev':'Life','poetry_quotes':'Poetry'}
seen = {'DS':set(), 'Life':set(), 'Poetry':set()}
for path in sorted(glob.glob('content/blogs/2026-W*/*')):
    name = os.path.basename(path)
    slug = name[:-7] if name.endswith('_images') else (name[:-3] if name.endswith('.md') else None)
    if not slug: continue
    try: d = datetime.strptime(slug[:10], '%Y-%m-%d')
    except ValueError: continue
    if d < cutoff: continue
    rest = slug[11:]
    for k, lab in NICHE.items():
        if rest.startswith(k): seen[lab].add((slug[:10], rest[len(k)+1:].replace('-',' '))); break
for lab in ['DS','Life','Poetry']:
    print(f'\n--- {lab} ---')
    for dt, topic in sorted(seen[lab]): print(f'  {dt}  {topic}')
"
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

> ### ⚡ STOP — Viral Hook Pre-Qualification Test (30 seconds, MANDATORY)
>
> Before generating the blog, verify this topic can form a specific hook. A hook MUST contain **at least one** of:
> - A **specific number** — "I lost 3 days to this bug", "91% model accuracy and it was completely wrong", "40% of men won't seek help"
> - A **specific result** — "the merge silently returned wrong data for 6 days with no error"
> - A **named moment** — "the exact line that made my manager pull the model", "the call I got at midnight"
>
> **The test:** finish this sentence: *"I [did something] and [a specific, concrete thing happened]."*
>
> - ✅ You can finish it with specifics → **topic passes. Continue to Step 1b.**
> - ❌ You cannot finish it specifically (e.g., "I learned about X and it was useful") → **this topic will produce a weak reel.** Go back to `data/ideas/weekly_ideas.md`, pick the next-ranked DS idea, and run the test again.
>
> **Write the sentence down somewhere.** It becomes your first IG reel hook candidate on Thursday.

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
- **Title formula** — specific incident / counter-intuitive result / specific number + outcome. Kill: "Everything You Need to Know About X" / "The Ultimate Guide to Y" / "Why Z Matters"
- **First paragraph test** — remove it mentally: if the article reads fine from paragraph 2, it's throat-clearing; rewrite so the opening line is the hook
- **Subheadings are hooks**, not labels — "The Bug That Cost Me 3 Days" not "The Problem"
- **Ending** — no bullet recap, no "Let me know your thoughts in the comments"

> ### 🎯 Identify the Shareable Moment (1 minute)
>
> Skim the blog and find **the single most shareable sentence** — the one a stranger would screenshot and send to a friend. This is NOT the thesis. It is a surprising observation, a counter-intuitive fact, or a moment of specific vulnerability.
>
> Examples:
> - "Python gave me a perfectly confident wrong number. No error. No crash. I trusted it for a week."
> - "The model was 91% accurate on the training set. On production data it predicted the same class for everything."
>
> **Mark it in the draft file with `[QUOTABLE]` inline.** It becomes the "shareable moment" cue in Tuesday's script (`[SHAREABLE_MOMENT]` tag), the hook for the IG reel brief on Thursday, and the closing sentence candidate if it's the strongest line in the piece.

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

Verify:
- **Title formula** — specific incident / named lesson / counter-intuitive result. Kill: "Everything You Need to Know About X" / "Why Z Matters"
- **First paragraph test** — remove it mentally: if the article reads fine from paragraph 2, rewrite so the opening line is the specific moment
- **Subheadings are hooks**, not labels — "The Call That Made Me Realise" not "The Turning Point"
- **Shareable sentence** — mark it `[QUOTABLE]` in the draft; it's the line someone would DM to a friend
- **Ending** — no bullet recap, no "Let me know your thoughts in the comments"

> ### ⚡ Viral Hook Pre-Qualification Test — Life topic
>
> Same test as DS. Finish: *"I [did something] and [a specific, concrete thing happened]."*
>
> Examples of Life hooks that pass:
> - "I called my parents when I was drowning in anxiety at work. They listed budgeting tips. I needed someone to just say: I hear you."
> - "I used to start every morning checking Twitter. The anxiety it created lasted until noon. I didn't notice until I stopped."
>
> - ✅ Can finish it specifically → proceed.
> - ❌ Cannot → return to `data/ideas/weekly_ideas.md`, pick next Life idea, test again.
>
> **Write the sentence down.** It becomes your reel hook on Thursday.

---

## Step 3 — Write Poetry piece (~10 min)

Poetry on Medium is the poem + minimal framing. The poem is the product — not an essay about it. Total length: ~150–200 words including the poem.

**Format (strict):**
1. **Hook** — 2–3 lines max. The specific feeling or moment that triggered the poem. No preamble, no "today I wrote a poem about X."
2. `---` divider
3. **Poem** — as a blockquote (`> line`)
4. `---` divider
5. **Close** — 1–2 lines. One honest observation. NOT a summary, NOT a lesson, NOT "share this with someone who needs it."
6. **Podcast CTA** — one line: `*Prefer listening? Available on [Breath of Poetry](https://open.spotify.com/show/0d7GfbQsYPc4t0idLhpYWT).*`

**Generate:**
```bash
python3 scripts/produce_blog.py \
  --topic 'YOUR POEM TITLE OR THEME' \
  --niche poetry \
  --format poem \
  --humanize
```

**From an existing poem file:**
```bash
python3 scripts/ghostwrite.py \
  --source data/poems/{poem_slug}.txt \
  --niche poetry \
  --format poem
```

Output: `content/blogs/{week}/YYYY-MM-DD_poetry_quotes_{slug}.md`

**Checklist:**
- [ ] Hook is 2–3 lines, names a specific sensation — NOT "today I wrote a poem about X"
- [ ] Poem is indented as blockquote (`> line`)
- [ ] Close is 1–2 lines — one honest observation, nothing more
- [ ] Podcast CTA present (Breath of Poetry link)
- [ ] NO reflections, NO takeaways, NO analysis sections

> ### ⚡ Hook test — Poetry
>
> The hook must name the specific feeling: *"There's a specific kind of [X] that [exact detail]."*
>
> ✅ "There's a specific kind of madness that doesn't announce itself. One day you're fine. The next, someone's laugh is living rent-free in your head."
> ✅ "There's a moment — usually quiet, usually late — when the performance stops making sense."
> ❌ "Today I want to share a poem I wrote about love."
>
> **Write the hook line down.** It becomes your reel caption on Thursday.

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

> The prompt template behind `repurpose_blog.py` is `prompts/repurposing_agent.md`. Edit it to change derivative formats, platform copy rules, or hashtag strategy — no code change needed.

### What each repurpose produces

Each run creates `content/derivatives/{week}/{slug}/` with:

| File | Content | Used by |
|------|---------|---------|
| `twitter_thread.txt` | 8–12 tweet thread (+ 2 hashtags on closing tweet) | Friday manual post |
| `linkedin_post.txt` | 1,200-char professional post (+ 4 hashtags) | scheduler.py staged (manual until clearance) |
| `instagram_caption.txt` | Caption + hashtags (up to 12) | Friday manual post (IG/FB) |
| `threads_post.txt` | Threads-formatted post (+ 3 hashtags) | Friday manual post (Threads) |
| `newsletter.txt` | Email newsletter (~400 words) | Beehiiv Sunday |
| `youtube_metadata.json` | Title, description, tags, chapter markers | Thursday YouTube upload |
| `youtube_shorts_metadata.json` | Short-form title, description, tags | Thursday Shorts upload |
| `slide_outline.json` | 7-slide structure | Tuesday slide deck gen |
| `thumbnail_brief.json` | Hook, visual direction, colors | Tuesday Remotion thumbnail |
| `claude_design_brief.json` | Emotional core, story frames | Tuesday social images |
| `schedule.json` | Computed publish timestamps | Friday manual posting reference |

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
