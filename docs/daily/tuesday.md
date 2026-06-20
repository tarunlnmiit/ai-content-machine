# Tuesday — Video Scripts + Visuals + Scene Plans (~1 hr)

Blogs exist from Monday. Today: produce worksheets **first** (so YouTube scripts can reference them in the description), generate YouTube scripts for all 3 niches, Remotion scene plans for motion shorts, and all social visual assets.

> **Reference docs:**
> - DS screen-recording script agent (use when prompting Claude): `prompts/yt_screen_script_agent.md`
> - DS combo script agent (stock B-roll + screen recording hybrid): `prompts/yt_combo_script_agent.md`
> - Life + Poetry script agent (also produces podcast script): `prompts/podcast_agent.md`
> - 5-beat viral Shorts formula (reverse-engineered from 38k-view reel): `data/kb/viral_reel_formula.md`
> - Twitter hook patterns (load before Viral Readiness Audit Step 5): `data/kb/twitter_hook_patterns.json`
> - YouTube virality framework (titles, thumbnails, retention): `prompts/youtube-virality-prompt.md`

## Tuesday at a glance

| Time | Task | Output |
|------|------|--------|
| 9:00 AM | Generate worksheets (DS + Life) + build manifest | `output/worksheets/{week}/{slug}_worksheet.pdf` |
| 9:20 AM | Generate DS YT script | `content/scripts/{week}/{ds_slug}_yt.md` |
| 9:35 AM | Generate Life YT script | `content/scripts/{week}/{life_slug}_yt.md` |
| 9:50 AM | Generate Poetry YT script | `content/scripts/{week}/{poetry_slug}_yt.md` |
| 9:55 AM | Pick + script the weekly combo reel (rotation log in Step 2b) | `content/scripts/{week}/{slug}_reel.md` |
| 10:05 AM | Generate Remotion scene plans (all 3) | `remotion/public/scene-plans/{week}/*.json` |
| 10:20 AM | Generate social images (all 3) | `assets/social_posts/{week}/{slug}_*.png` |
| 10:35 AM | Generate slide decks (all 3) | `assets/slides/{week}/{slug}_slides.pdf` |
| 10:50 AM | Generate IG carousels (all 3) | `assets/carousels/{week}/{slug}/slide_1–7.png` |
| 11:05 AM | Verify all assets | `scripts/list_week_content.py {week}` |

---

## Step 1 — Generate lead-magnet worksheets (DS + Life) — do this FIRST

Worksheets come first so the YouTube scripts (Step 2) can auto-append a spoken "worksheet in the description" CTA — that only fires if the worksheet already exists in the manifest. Poetry auto-skips (reflection format). Low-engagement blogs skip too.

### DS worksheet:
```bash
python3 scripts/generate_worksheet_outline.py \
  -i content/blogs/{week}/{ds_slug}.md

python3 scripts/generate_canva_worksheet_prompt.py \
  -i content/worksheets/{ds_slug}_worksheet.json
```

### Life worksheet:
```bash
python3 scripts/generate_worksheet_outline.py \
  -i content/blogs/{week}/{life_slug}.md

python3 scripts/generate_canva_worksheet_prompt.py \
  -i content/worksheets/{life_slug}_worksheet.json
```

The Canva prompt prints to console. Paste into Canva AI to generate the PDF. Export and save to:
```
output/worksheets/{week}/{slug}_worksheet.pdf
```

Then build the manifest so the slug is live and the scripts can see it:
```bash
node scripts/build-worksheets-manifest.mjs
python3 scripts/worksheet_links.py --week {week}
```

No ConvertKit landing page — committing the PDF makes the email-gated link live on the Vercel app. `worksheet_links.py` prints the URL + a blog paste line + a YouTube description block per worksheet. See `documentation/WORKSHEET_WORKFLOW.md` for the delivery system + one-time Kit setup.

---

## Step 2 — Generate YouTube scripts

### DS (screen-recording style, ~10 min)

```bash
python3 scripts/ghostwrite.py \
  --source content/blogs/{week}/{ds_slug}.md \
  --niche ds \
  --format yt
```

**Stock video / conceptual style** (if not doing screen recording):
```bash
python3 scripts/ghostwrite.py \
  --source content/blogs/{week}/{ds_slug}.md \
  --niche ds \
  --format yt \
  --video-style stock
```

Output: `content/scripts/{week}/{ds_slug}_yt.md`

DS script structure:
```
[HOOK: opening line that stops the scroll]
[SCREEN: show the problem visually]
```python
# code inline as a fenced block — NOT a [CODE_INSERT:] placeholder
```
[SCREEN: chart output]   # chart cues sit right after their generating code
[PAUSE]
[BROLL: cut to relevant b-roll]
[ANIMATION: describe what to animate]
```

### Life (talking-head style, ~10 min)

```bash
python3 scripts/ghostwrite.py \
  --source content/blogs/{week}/{life_slug}.md \
  --niche life \
  --format yt
```

Output: `content/scripts/{week}/{life_slug}_yt.md`

Life script structure:
```
[HOOK: personal story opening]
[BROLL: suggest b-roll scene]
[PAUSE]
[ANIMATION: lower third text]
```

### Poetry (voiceover over visuals, ~10 min)

The poem IS the script. The Medium blog file is also the YouTube script — no separate generation needed unless you want explicit B-roll cues.

```bash
# Optional: generate a version with BROLL cues added
python3 scripts/ghostwrite.py \
  --source content/blogs/{week}/{poetry_slug}.md \
  --niche poetry \
  --format yt
```

Output: `content/scripts/{week}/{poetry_slug}_yt.md`

Poetry script structure:
```
[HOOK: first 2-3 lines from the Medium hook]
[Read the poem — each line spoken slowly]
[PAUSE: intentional silence beat before the close line]
[Close line from the Medium piece]
[BROLL: atmospheric visual suggestion — one per stanza]
```

If you skip the script generation, copy the Medium blog file as-is to `content/scripts/{week}/{poetry_slug}_yt.md` — it's ready to read from.

### Worksheet CTA (DS/Life, auto)

Because Step 1 built the worksheet manifest, the **DS and Life** scripts now carry a spoken `[WORKSHEET CTA]` line ("free worksheet, linked in the description"), and `ghostwrite.py` printed a **YouTube description** block to paste at upload. Poetry has no worksheet, so nothing is added. Re-print the description block anytime:
```bash
python3 scripts/worksheet_links.py --week {week}
```

### DS script — Series compounding (add this to the END of every DS script)

Every DS script must end with a tease for next week's DS piece. This builds a pre-warmed audience who comes back for the sequel.

Open `content/scripts/{week}/{ds_slug}_yt.md` and verify the outro contains something like:

```
[OUTRO TEASE: "Next week — [1-sentence description of next DS topic]. If you don't want to miss it, subscribe."]
```

If it doesn't exist, add it manually. It should be:
- **One sentence maximum** describing the next piece
- **Specific** — not "more Python tips", but "next week I'll show you the pandas mistake that corrupted 6 months of data silently"
- Placed right before the subscribe CTA

If you don't know next week's topic yet, use a placeholder: `[OUTRO TEASE: "Next week — [next DS topic here]. Subscribe so you don't miss it."]`

You will fill this in once Monday's topic selection is done next week.

---

### Verify scripts

Each script should be:
- 500–1,500 words (8–12 min at 120 wpm)
- Personal voice, no jargon without explanation
- `[SCREEN:]` / `[BROLL:]` / `[ANIMATION:]` cues throughout — code inline as fenced ```python blocks, **no** `[CODE_INSERT:]` placeholders (banned). DS chart `[SCREEN:]` cues sit right after their generating code; docs `[SCREEN:]` cues carry a "Links to show on screen:" line.
- For DS/Life: a `[WORKSHEET CTA]` line near the end (if a worksheet exists)
- No banned words

```bash
wc -w content/scripts/{week}/{ds_slug}_yt.md
wc -w content/scripts/{week}/{life_slug}_yt.md
wc -w content/scripts/{week}/{poetry_slug}_yt.md
```

---

## Step 2c — Viral Readiness Audit for each script (10 min, MANDATORY)

Do this for ALL THREE scripts before moving to Step 3. This prevents weak reels from being produced on Thursday.

Open each script file in VS Code. Go through the three checks below:

### Check 1 — Hook validation

Read the **first 3 sentences** of each script. The opening line must contain a specific number, result, or named moment.

**DS script hook test:**
```bash
head -5 content/scripts/{week}/{ds_slug}_yt.md
```
- Does it start with a specific incident, number, or named failure? → ✅ passes
- Does it start with "Today I want to talk about…", "In this video…", or any vague setup? → ❌ REWRITE IT

**How to rewrite a failing DS hook** — replace the opening with the specific-incident sentence you wrote down on Monday (the hook pre-qual test result). If you didn't write it down, open the blog and find the most surprising/counter-intuitive sentence.

**Life script hook test:**
```bash
head -5 content/scripts/{week}/{life_slug}_yt.md
```
Same check. Life hooks must open with a specific personal incident, not a generalization.

**Poetry script hook test:**
```bash
head -5 content/scripts/{week}/{poetry_slug}_yt.md
```
Poetry hooks must name a specific emotion or paradox in the opening line, not describe what the poem is about.

---

### Check 2 — Shareable moment identification

For each script, find the one line a stranger would send to a friend. This is the "shareable moment."

It is typically:
- A counter-intuitive observation ("The more I fixed it, the more wrong it got")
- A specific personal admission ("I didn't realise I was the reason the team was slow")
- A line that names a universal feeling specifically ("Not the anxiety before the deadline — the quiet dread after it passes")

Once you find it, add a `[SHAREABLE_MOMENT]` comment tag on the line above it in the script:

```
[SHAREABLE_MOMENT]
Python gave me a perfectly confident wrong number. No error. No crash. I trusted it for a week.
```

This tag is for your reference — it tells Claude which moment to prioritise when generating the IG reel brief on Thursday. If `generate_ig_reel_brief.py` sees this tag, it surfaces that moment as Hook Option 1.

---

### Check 3 — Sound-off overlay plan

40% of Instagram Reels are watched with sound OFF. Every critical moment in your reel must also appear as visible text on screen. These tags feed directly into `generate_scene_plans.py --mode overlay` on Thursday — Remotion reads them and bakes the overlays into the final reel automatically. No manual overlay work needed. Plan them now while the script is in front of you.

For each script, identify exactly **3 lines that MUST appear as text overlays** in the reel:

1. **The hook line** (your opening statement — always overlay #1, shown at second 0:00)
2. **The shareable moment** (the line tagged `[SHAREABLE_MOMENT]` above)
3. **The CTA line** (the comment-keyword prompt — "Comment KEYWORD and I'll send you X")

Add a `[TEXT_OVERLAY]` tag above each of those three lines in the script file:

```
[TEXT_OVERLAY: shown at 0:00]
Python gave me a perfectly confident wrong number.
```

```
[TEXT_OVERLAY: shareable moment]
I trusted it for a week. No error. No warning.
```

```
[TEXT_OVERLAY: CTA]
Comment TYPES and I'll send you the full breakdown.
```

You do NOT need more than 3. Additional overlays are optional. These 3 are non-negotiable.

---

### Check 4 — LinkedIn post hook

LinkedIn collapses every post after line 3. The reader sees only the first ~250 characters before a "…see more" button. If those first 3 lines don't make them click, they don't read the post. They definitely don't comment.

Open `content/derivatives/{week}/{slug}/linkedin_post.txt` for each niche.

**The test:** read only the first 3 lines. Ask: *"Would I click 'see more' if this appeared in my feed?"*

LinkedIn hook rules — the first line must be one of:
- A **bold, specific claim** — "I built a job application tracker in 4 hours using Python. Here's every line of code."
- A **counter-intuitive statement** — "The more I optimised my model, the worse my results got."
- A **specific personal admission** — "I called my parents when I was drowning in anxiety at work. They listed budgeting tips."
- A **direct question with a specific answer implied** — "Do you know what your pandas merge is doing with duplicate keys? Most data scientists don't."

LinkedIn hook anti-patterns — **rewrite immediately if you see any of these:**
- "I'm excited to share…"
- "Today I want to talk about…"
- "In this post, I'll cover…"
- "Mental health is important." (too vague)
- Starting with a hashtag

**If the first line fails:** open `linkedin_post.txt`, delete the first line, and replace it with the hook sentence you wrote during Monday's pre-qualification test. Then add a line break. The rest of the post can stay.

Add a `[LINKEDIN_HOOK]` tag comment at the top of each linkedin_post.txt to mark that the hook has been validated:

```
[LINKEDIN_HOOK: validated]
Python gave me a perfectly confident wrong number. No error. No crash. I trusted it for a week.

Here's what actually happened — and the one-line fix that would have caught it...
```

---

### Check 5 — Twitter thread opener

Twitter thread openers have one job: make someone tap "Show this thread." Tweet 1 must work as a **standalone tweet** — someone who never reads the rest of the thread should still find value in it. If tweet 1 only makes sense with tweets 2–12, nobody will tap through.

Open `content/derivatives/{week}/{slug}/twitter_thread.txt` for each niche.

**Read only tweet 1.** Apply this test: if this were posted as a single tweet with no thread, would it get likes or replies on its own?

Twitter thread opener formulas that work:
- **The bold lesson** — "I spent 3 days debugging a pandas merge. The bug was one character. Here's what I learned: 🧵"
- **The counter-intuitive result** — "More features made my model worse. Here's why (and the fix): 🧵"
- **The personal hook** — "I called my parents when I was drowning in anxiety. They gave me budgeting tips. That gap is what mental health stigma actually looks like: 🧵"
- **The specific question** — "What does Python do when you divide by zero in a list comprehension? Not what you think: 🧵"

Twitter opener anti-patterns — **rewrite if any of these:**
- "A thread on [topic]:"
- "Here are X things about Y:"
- Starting with context before the hook ("As a data scientist who has worked in…")
- No 🧵 emoji at the end (signals it's a thread — readers expect it)

**If tweet 1 fails:** rewrite it to lead with the specific incident or counter-intuitive result. The rest of the thread can stay.

Add a `[TWITTER_HOOK: validated]` tag comment at the top of each `twitter_thread.txt`.

---

### Viral Readiness Audit checklist

Run this for all 3 scripts + derivatives before closing Tuesday:

- [ ] DS hook opens with a specific number, result, or named moment (not a generic setup)
- [ ] Life hook opens with a specific personal incident (not a generalization)
- [ ] Poetry hook names a specific emotion or paradox (not a description of the poem)
- [ ] `[SHAREABLE_MOMENT]` tag added to each script
- [ ] `[TEXT_OVERLAY: shown at 0:00]` tag on the hook line in each script
- [ ] `[TEXT_OVERLAY: CTA]` tag on the comment-keyword line in each script
- [ ] DS script ends with `[OUTRO TEASE:]` for next week's DS piece
- [ ] LinkedIn first line validated for all 3 posts — `[LINKEDIN_HOOK: validated]` tag added
- [ ] Twitter tweet 1 validated for all 3 threads — `[TWITTER_HOOK: validated]` tag added
- [ ] Thumbnail hook written for all 3 scripts (Step 2d below) ← **new**

---

## Step 2d — Write thumbnail hooks (5 min, do BEFORE closing Tuesday)

This is where thumbnail CTR is actually won or lost — not Thursday. The hook text for the thumbnail comes from this script session, while the angle is clearest in your head.

For each script, take the `[HOOK]` opening line and compress it to **3–5 words** that:
- Name the specific mistake, result, or feeling — not the topic category
- Work at 120px wide (no full sentences, no punctuation-heavy phrases)
- Have no series numbers ("Tutorial 1/10" → banned)

Write these to a thumbnail brief file:

```bash
python3 scripts/generate_thumbnail.py \
  --blog content/scripts/{week}/{ds_slug}_yt.md \
  --niche ds \
  --hook "Setup That Breaks Everything" \
  --week {week} \
  --canva --dry-run
```

The `--dry-run` flag writes the brief JSON and prompt file without executing Canva — so Thursday's generation is a single command with no thinking required.

**Hook examples by niche:**

| Niche | Bad (too generic) | Good (specific) |
|-------|-------------------|-----------------|
| DS | "Python Tutorial" | "Setup That Breaks Everything" |
| DS | "Data Science Tips" | "Wrong for 6 Months" |
| Life | "Self Improvement" | "3 Years. Wrong." |
| Life | "Mental Health Tips" | "I Called Home. Budget Tips." |
| Poetry | "Love Poem" | "Love Doesn't Announce Itself" |
| Poetry | "About Loneliness" | "The Room Goes Quiet" |

Save each hook to the thumbnail brief so Thursday is just running a command, not thinking.

---

## Step 2b — Weekly combo reel (~10 min, build-in-public)

Every week, ship **ONE** extra build-in-public/promo reel using the 5-beat viral formula
(`data/kb/viral_reel_formula.md`), drawn from the idea bank in `data/kb/reels/working_combos.md`
(14 idea cards in Part A + 6 full shoot scripts in Part B). Honesty guardrail
(`data/kb/reels/04_honesty_guardrail.md`): only ever claim what you can show on screen.

This is the daily-flow version of the cadence in
[`weekly-operating-guide.md` → Build-in-Public Projects](../weekly-operating-guide.md).

**Process:**
1. Pick the next **unused** combo from `working_combos.md` (Part B shoot scripts first, then Part A
   cards) — don't repeat a prior week; log it in the rotation table below.
2. Write the reel script to `content/scripts/{week}/{date}_{slug}_reel.md` following the 5 beats
   (Hook → Problem → Reveal+proof → Payoff → CTA, ≤45s, captions burned in, ONE keyword CTA).
3. Build the UTM link with `scripts/lib/utm.py` (campaign per combo, `utm_content={date}_{slug}`);
   arm the comment→DM keyword (SuperProfile / CreatorFlow).
4. Flows downstream like any reel: **Wed** shoot (screen-record the proof), **Thu** render/upload +
   `scripts/generate_shorts_meta.py`, then derivatives via `prompts/repurposing_agent.md` →
   posted manually (no Metricool/Publer CSV; see `docs/daily/friday.md`).

**Rotation log:**

| Week | Combo / source | Keyword | Reel script | Status |
|------|----------------|---------|-------------|--------|
| 2026-W25 | **ChatGPT Prompt Anatomy** (from prompt-anatomy blog) | `PROMPT` | `content/scripts/2026-W25/2026-06-16_data_science_tech_ai-prompt-anatomy-travel_reel.md` | scripted ✅ |
| 2026-W26 | Combo #1 — ScrapeGraphAI ("free tool killed my $300 scraper") | `SCRAPE` | — | queued |
| 2026-W27 | Combo #6 — Claude + Metricool MCP | `CONTENT` | — | queued |
| 2026-W28 | Combo #4 — Local Claude Code on Mac | `LOCAL` | — | queued |
| 2026-W29 | Combo #10 — Claude in Excel | `EXCEL` | — | queued |
| 2026-W30 | Combo #2 — Claude + GitHub MCP | `REVIEW` | — | queued |

Keywords for W26–W30 come straight from the Part B shoot scripts in `working_combos.md`.

---

## Step 3 — Generate Remotion scene plans (~5–8 min)

Scene plans drive motion graphic shorts (`DSMotionShort`, `LifeMotionShort`, `PoetryMotionShort`). Claude Opus 4.8 reads the full script semantically and decides WHERE motion graphics make the most sense — no `[ANIMATION:]` tags required.

Short mode now produces **7 unique shorts per script** (`--shorts 7`, default). Each short takes a DIFFERENT angle/segment of the script and becomes its own self-contained 30–60s motion video — no scene reuse across shorts.

```bash
# DS — motion shorts (7 unique 30–60s shorts from one script):
python3 scripts/generate_scene_plans.py \
  --script content/scripts/{week}/{ds_slug}_yt.md \
  --niche ds --week {week} --mode short --shorts 7

# Life:
python3 scripts/generate_scene_plans.py \
  --script content/scripts/{week}/{life_slug}_yt.md \
  --niche life --week {week} --mode short --shorts 7

# Poetry:
python3 scripts/generate_scene_plans.py \
  --script content/scripts/{week}/{poetry_slug}_yt.md \
  --niche poetry --week {week} --mode short --shorts 7
```

Outputs: one file per short — `remotion/public/scene-plans/{week}/{slug}_s01.json` … `_s07.json`. Each file holds the plain scenes array (Remotion composition prop format unchanged).

**Optional — long-form overlay plan** (scenes appear ON TOP of camera footage at specific narration moments):
```bash
python3 scripts/generate_scene_plans.py \
  --script content/scripts/{week}/{ds_slug}_yt.md \
  --niche ds --week {week} --mode overlay
# → remotion/public/scene-plans/{week}/{ds_slug}_overlay.json
```

**Preview before writing:**
```bash
python3 scripts/generate_scene_plans.py \
  --script content/scripts/{week}/{ds_slug}_yt.md \
  --niche ds --week {week} --mode short --dry-run
```

**Regenerate (bypass cache):**
```bash
python3 scripts/generate_scene_plans.py ... --no-cache
```

Cache: results are cached 30 days by script content hash. Re-running with the same script is instant.

### Scene plan JSON structure

Each entry maps to a Remotion scene component:

```json
[
  {
    "sceneId": "scene-1",
    "componentName": "DataVizReveal",
    "script": "Model accuracy improved from 72% to 91% after feature engineering",
    "niche": "ds",
    "durationSec": 5,
    "props": {
      "data": [
        {"label": "Before", "value": 72},
        {"label": "After", "value": 91}
      ],
      "title": "Feature Engineering Impact",
      "chartType": "bar"
    }
  },
  {
    "sceneId": "scene-2",
    "componentName": "CodeAnnotation",
    "script": "fillna() prevents NaN propagation through the pipeline",
    "niche": "ds",
    "durationSec": 6,
    "props": {
      "code": ["df['score'] = df['score'].fillna(0)"],
      "highlightLine": 0,
      "annotationText": "Prevents NaN errors downstream"
    }
  }
]
```

### Available components by niche

**DS:** `DataVizReveal` · `CodeAnnotation` · `ConceptExplainer` · `ToolComparison` · `WordReveal` · `NumberedTips`

**Life:** `TransformationArc` · `HabitLoop` · `NumberedTips` · `AtmosphericQuote` · `WordReveal`

**Poetry:** `LineReveal` · `AtmosphericQuote` · `WordReveal`

**Any niche:** `NumberedTips` · `WordReveal` · `AtmosphericQuote`

Run for all 3:
```bash
python3 scripts/generate_animation_prompts.py content/scripts/{week}/{ds_slug}_yt.md --niche ds --scene-plans
python3 scripts/generate_animation_prompts.py content/scripts/{week}/{life_slug}_yt.md --niche life --scene-plans
python3 scripts/generate_animation_prompts.py content/scripts/{week}/{poetry_slug}_yt.md --niche poetry --scene-plans
```

Scene plan files saved to: `remotion/public/scene-plans/{week}/`

### Create shorts manifest

Auto-generate motion-only manifests from scene plans (runs in seconds). One slot per unique short plan — the 7 `_sNN.json` files become 7 manifest slots (falls back to a single slot for legacy `{slug}.json`):

```bash
python3 scripts/generate_shorts_manifest.py --week {week}

# Dry run first to verify:
python3 scripts/generate_shorts_manifest.py --week {week} --dry-run

# Single niche:
python3 scripts/generate_shorts_manifest.py --week {week} --niche ds
```

Writes `content/derivatives/{week}/{slug}/shorts_manifest.json` for all 3 slugs.

**On Wednesday** — after recording footage, swap slots to clip-based:
```json
[
  {"slot": 0, "type": "clip", "editPlanFile": "edit-plans/{week}/{slug}.json", "clipStartSec": 30,  "clipEndSec": 90},
  {"slot": 1, "type": "clip", "editPlanFile": "edit-plans/{week}/{slug}.json", "clipStartSec": 150, "clipEndSec": 210},
  {"slot": 2, "type": "clip", "editPlanFile": "edit-plans/{week}/{slug}.json", "clipStartSec": 300, "clipEndSec": 360}
]
```

Or mix motion + clip:
```json
[
  {"slot": 0, "type": "motion", "scenePlanFile": "scene-plans/{week}/{slug}.json"},
  {"slot": 1, "type": "clip",   "editPlanFile": "edit-plans/{week}/{slug}.json", "clipStartSec": 200, "clipEndSec": 260},
  {"slot": 2, "type": "motion", "scenePlanFile": "scene-plans/{week}/{slug}.json", "audioFile": "audio/{week}/{slug}_clip.mp3"}
]
```

- `type: "clip"` — cuts from long-form footage. Requires `editPlanFile` from Wednesday.
- `type: "motion"` — pure Remotion animation. Requires `scenePlanFile`.

---

## Step 4 — Generate social images (~10 min)

### Option A — Remotion animated PNGs (recommended, requires render server)

Exports pixel-perfect PNGs from the Remotion `SocialCard1x1`, `SocialCard9x16`, and `Thumbnail` compositions:

```bash
# Ensure render server is running (see thursday.md Step 1b)
# cd remotion/server && ts-node index.ts &

python3 scripts/export_social_cards.py --week {week}

# Or single niche:
python3 scripts/export_social_cards.py --week {week} --niche ds

# Dry run to verify before exporting:
python3 scripts/export_social_cards.py --week {week} --dry-run
```

Outputs: `assets/social_posts/{week}/{slug}_social_1x1.png`, `{slug}_social_9x16.png`, `output/visuals/{week}/{slug}_thumb.png`

### Option B — Claude-generated social images (fallback)

```bash
# All 3 niches in one pass:
python3 scripts/generate_social_images.py --week {week}

# Or per-slug if needed:
python3 scripts/generate_social_images.py --slug {ds_slug}
python3 scripts/generate_social_images.py --slug {life_slug}
python3 scripts/generate_social_images.py --slug {poetry_slug}
```

**Outputs per slug** in `assets/social_posts/{week}/`:
| File | Dimensions | Platform |
|------|-----------|---------|
| `{slug}_instagram.png` | 1080×1080 | Instagram feed |
| `{slug}_linkedin.png` | 1200×628 | LinkedIn |
| `{slug}_threads.png` | 1080×1080 | Threads |
| `{slug}_twitter.png` | 1200×675 | Twitter/X |

These PNGs live at `assets/social_posts/{week}/`. Posting is **manual** now — no public Drive
URL needed: attach the local PNG directly when you post in-app on Friday (IG/FB/Threads). No
Metricool CSV, so the old `--image-url` / `schedule.json` public-link step is obsolete.

---

## Step 4a — Generate slide decks (~10 min)

```bash
python3 scripts/generate_slide_deck.py --week {week}

# Or per-slug:
python3 scripts/generate_slide_deck.py --slug {ds_slug}
python3 scripts/generate_slide_deck.py --slug {life_slug}
python3 scripts/generate_slide_deck.py --slug {poetry_slug}
```

Uses `content/derivatives/{week}/{slug}/slide_outline.json` + `claude_design_brief.json` to generate a 7-slide HTML deck styled per niche from `data/brand/brand_kit.yaml`.

**Outputs per slug** in `assets/slides/{week}/`:
| File | Use |
|------|-----|
| `{slug}_slides.html` | Source deck (open in browser, arrow keys to page) |
| `{slug}/slide_N.png` | Individual slide PNGs |
| `{slug}/{slug}_slides.pdf` | Assembled PDF (for downloads) |

---

## Step 4b — Generate Instagram carousels (~10 min)

```bash
python3 scripts/generate_carousel.py \
  --blog content/blogs/{week}/{ds_slug}.md

python3 scripts/generate_carousel.py \
  --blog content/blogs/{week}/{life_slug}.md

python3 scripts/generate_carousel.py \
  --blog content/blogs/{week}/{poetry_slug}.md
```

**Outputs per slug:**
- `assets/carousels/{week}/{slug}_carousel.html` — preview in browser
- `assets/carousels/{week}/{slug}/slide_1.png` … `slide_7.png` — 1080×1350 PNGs

Upload carousel PNGs to Google Drive and save URLs to `schedule.json` (same process as social images — adds `carousel_slide_urls` array).

---

## Step 5 — Verify all assets (2 min)

```bash
python3 scripts/list_week_content.py {week}
```

**Expected output:**
```
SCRIPTS:        ds ✓   life ✓   poetry ✓
SCENE PLANS:    ds ✓   life ✓   poetry ✓
IMAGES:         ds ✓   life ✓   poetry ✓
SLIDES:         ds ✓   life ✓   poetry ✓
CAROUSELS:      ds ✓   life ✓   poetry ✓
WORKSHEETS:     ds ✓   life ✓   (poetry skipped)
SHORTS MFST:    ds ✓   life ✓   poetry ✓
```

Missing anything? Re-run the relevant step. Most common failures:
- Script missing → `ghostwrite.py` failed silently — re-run Step 2
- Worksheet PDF missing → do Step 1 (Canva export) before scripts, else the script CTA won't attach
- Scene plan missing → re-run `generate_animation_prompts.py --scene-plans`
- Carousel missing → re-run `generate_carousel.py` for that blog
- Worksheet JSON missing → re-run `generate_worksheet_outline.py`

---

## Posting schedule reminder (applies next week, Week N+1)

| Niche | Instagram/Facebook | Threads | LinkedIn |
|-------|------------------|---------|----------|
| DS    | Wed 8:00 AM IST  | Wed 8:00 PM IST | Tue 8:00 AM IST |
| Life  | Tue 8:00 AM IST  | Tue 8:00 PM IST | Tue 8:00 AM IST |
| Poetry | Fri 10:00 AM IST | Fri 12:00 PM IST | Tue 8:00 AM IST |

Twitter: Life → Mon 1:00 PM (+1 wk) · Poetry → Fri 12:00 PM (+1 wk) · DS — manual
