---
title: "Blog Pipeline — one command (derivatives + media)"
type: doc
slug: blog-pipeline
tags: [content/doc]
---
# Blog Pipeline — one command (derivatives + media)

*Added 2026-06-21.* Once a blog exists, **one command** produces every non-video derivative.
**Videos are separate** (they need recorded audio — see [voiceover-runner.md](voiceover-runner.md)).

## Command

```bash
# existing blog
python3 scripts/run_blog_pipeline.py --input content/blogs/2026-W22/<slug>.md

# generate the blog first, then everything
python3 scripts/run_blog_pipeline.py --topic "Why X beats Y" --niche ds
```

Flags: `--project K`, `--force` (redo all), `--no-stage` (skip scheduler load), `--skip-thumbnail`,
`--humanize` / `--listicle N` / `--type tutorial|news` (topic mode → produce_blog), `--dry-run`.

> **`--interview` (two-call input flow)** is a `produce_blog.py` flag — run it **directly**
> (it's interactive: it asks you questions over stdin). See
> [Interview mode](#interview-mode-two-call-input) below.

`repurpose_blog.py` flags: `--step <name>` skips Phase 1 entirely and force-runs a single Phase 2 step.
Valid step names: `worksheet` · `blog-cta` · `linkedin-comment` · `slides` · `carousel` · `reel-brief` · `yt-script`

```bash
# Re-generate only the carousel (e.g. after brand kit change)
python3 scripts/repurpose_blog.py --input content/blogs/{week}/{slug}.md --step carousel

# Re-generate only the YT script
python3 scripts/repurpose_blog.py --input content/blogs/{week}/{slug}.md --step yt-script
```

### Carousel standalone commands

`generate_carousel.py` runs automatically inside `run_blog_pipeline.py` and `repurpose_blog.py --step carousel`. For direct calls:

```bash
# From existing blog (auto-detects niche)
python3 scripts/generate_carousel.py --blog content/blogs/{week}/{slug}.md

# From topic + niche
python3 scripts/generate_carousel.py --topic "Your topic here" --niche ds|life|poetry

# Authoritative slide-by-slide plan (overrides auto slide count + structure)
python3 scripts/generate_carousel.py --blog content/blogs/{week}/{slug}.md \
  --outline path/to/outline.md

# Re-export existing carousel HTML to 1080×1350 PNGs (2x supersampled)
python3 scripts/generate_carousel.py --export-only assets/carousels/{week}/{slug}_carousel.html
```

**Slide count:** content-driven, **5–12 slides**, sweet spot **8–10 for educational/framework content.** Each slide = one idea; never pad or merge to hit a round number.

**Export:** Playwright renders at 2× density (2160×2700) and downscales to 1080×1350 for sharpness. One PNG per slide to `assets/carousels/slides/{week}/{slug}/slide_N.png`.

> **`--type` is DS-only.** `--type tutorial` = code-first post with runnable Python; `--type news` = editorial/opinion piece with no code. Rejected for Life and Poetry.

Niche + ISO week are auto-derived from the blog slug.

## What it runs (in order, idempotent — skips when output exists)

| # | Step | Tool | Output |
|---|------|------|--------|
| 0 | (topic mode) write blog | `produce_blog.py` | `content/blogs/{week}/{slug}.md` |
| 1 | **Phase 1** text derivatives | `repurpose_blog.py` | `content/derivatives/{week}/{slug}/` — linkedin_post(+linkedin_second_comment=blog link), linkedin_document_caption (slide deck post body), instagram_caption(+clean), newsletter, polls, slide_outline, youtube_metadata, youtube_shorts_metadata, claude_design_brief, schedule.json. **Threads dropped.** LinkedIn comment order: 1st=Worksheet (Phase 2) · 2nd=Blog link (Phase 1). |
| 1b | **Phase 2** (auto, inside repurpose_blog.py) | same call | 2a worksheet (DS/Life): Claude-designed HTML → headless-Chrome PDF (no Canva) · 2b blog CTA inject · 2c linkedin_first_comment (worksheet, 1st) + 2c2 linkedin_document comments (worksheet 1st + YT link 2nd) · 2d slide deck (virality_block + master_brief) · 2e IG carousel (+Playwright PNG export, virality_block + caption formula + master_brief) · 2f IG reel brief · 2g YT filming script (virality_block + master_brief) |
| 2 | Social images | `generate_social_images.py --slug` | `assets/social_posts/{week}/{slug}_*.png` |
| 3 | Thumbnail brief (+HTML render) | `thumbnail_brief.py` + `generate_thumbnail.py --export --skip-remotion` | `thumbnail_brief.json` + `assets/thumbnails/{slug}_thumbnail.png` |
| 4 | Stage to scheduler | `load_posts.py --week` | scheduling DB → auto-publish daemon |

> Steps 3 (slide deck), 4 (IG reel brief), 6 (worksheet) in `run_blog_pipeline.py` are now **also run inside `repurpose_blog.py` Phase 2** — they skip idempotently if output already exists. Running `run_blog_pipeline.py` still works fine.

> **`produce_blog.py` also builds the IG carousel directly** (Step 5, all niches, non-fatal, skip with
> `--no-carousel`) — same `generate_carousel.py --blog … --export` call as Phase 2 step 2e. The overlap
> is safe: `generate_carousel.py` self-skips when the output HTML exists, so whichever entry point runs
> second is a no-op. Both `generate_carousel.py` and `generate_worksheet_html.py` prompts now append a
> compact **DESIGN SYSTEM REFERENCE** grounding block (`lib/design_system_ref.py`, fail-soft) — see
> [design-system-sync.md](design-system-sync.md).

> **Carousel output layout & UI contract** (`generate_carousel.py`):
> - HTML: `assets/carousels/{week}/{slug}_carousel.html`; referenced by `repurpose_blog.py`,
>   `generate_social_images.py`, `load_posts.py`.
> - Exported PNGs: `assets/carousels/slides/{week}/{slug}/slide_N.png` (one per slide, 1080×1350,
>   rendered at 2× density for sharpness).
> - **No per-carousel `_export.py` files are generated** — export is always run via Playwright
>   (`--export` flag, on by default; use `--no-export` to skip).
> - Required per-slide UI: `.progress-row` of `.progress-seg`/`.fill` segments (Playwright export
>   **bakes each slide's fill from slide index**). Plus `.follow-tag` ("Tap to follow") on final CTA
>   slide only, `.save-tag` ("Save this") on hook slide only, and `.cliffhanger` ("Next: …") on
>   every slide except the last — as real DOM elements, not CSS-only.

## Stays manual (by design)

- **Videos** — `run_voiceover_week.py` (needs recorded voiceover).
- **Worksheet (DS/Life)** — now fully automated, **no Canva**: `generate_worksheet_html.py`
  (Claude-designed Breath Network HTML → headless-Chrome PDF) + `build-worksheets-manifest.mjs`.
  Runs inside `produce_blog.py` and pipeline step 6. Only push/deploy stays manual.
- **Thumbnail Canva pass** — `generate_thumbnail.py --canva` (needs a face photo / hook); the
  pipeline only does the automatic HTML thumbnail.

## Interview mode (two-call input)

*Added 2026-06-26.* `produce_blog.py --interview` replaces the free-text "your thoughts"
step with a **two-call interview** that mines your first-hand material before writing.
**Topic selection and publishing are unchanged.** Without `--interview`, the classic
raw-input flow runs exactly as before — this is purely additive.

```bash
# interview-driven draft, no publishing (safe end-to-end test)
python3 scripts/produce_blog.py --niche ds --interview --dry-run

# real draft (still saves locally only; publishing is the separate publish_medium.py step)
python3 scripts/produce_blog.py --niche life --interview
```

Flow once a topic is picked:

1. **CALL 1 — questions.** Topic + Google/Medium trend context →
   `prompts/question_generator.md` → a suggested angle + 5–8 sharp questions.
2. **Interactive Q&A.** Questions are asked one at a time. Type a multi-line answer
   (blank line ends it), `skip` to skip one, then review/edit any answer by number.
   Empty input never crashes — it's recorded as skipped.
3. **CALL 2 — article.** Topic + your Q&A → `prompts/article_writer.md` → 3 title
   options, subtitle, full article, 5 tags, and an email CTA. You pick the title.
4. Draft is saved to `content/blogs/{week}/{slug}.md` like any other blog; tags are
   stored as a trailing `<!-- Medium tags: … -->` comment, followed by the SEO comments
   (see **Medium SEO** below). Continue to publishing as usual.

## Medium SEO (target keyphrase + SEO title/description)

*Added 2026-06-26.* Both blog generators now emit Medium SEO fields so stories rank on
Google (Medium has strong domain authority). The model picks a **target keyphrase**, weaves
it into the title + first paragraph, and produces a **search-facing SEO title + SEO
description** (distinct from the reader-facing title/subtitle). These are saved as trailing
comments in the blog `.md`:

```
<!-- Target keyphrase: … -->
<!-- SEO title: … -->
<!-- SEO description: … -->
```

**Medium's API can't set these** (`publish_medium.py` only sends title/tags/canonical/content),
so they're a **manual paste into Medium's SEO settings** (••• → SEO settings). `produce_blog.py`,
`run_blog_pipeline.py`, and `publish_medium.py` all **print the values + manual checklist** when
they finish. Parsing/rendering lives in `scripts/lib/seo.py`. Full rules:
[medium-seo.md](medium-seo.md).

**Editable without touching code:**

| What | Where |
|------|-------|
| Question-generator prompt | `prompts/question_generator.md` (keep the `{{TOPIC}}` etc. placeholders) |
| Article-writer prompt | `prompts/article_writer.md` (keep the `{{ANSWERS}}` etc. placeholders) |
| NICHE · AUDIENCE · AUTHOR_VOICE · EMAIL_CTA_TARGET | `config/interview.json` (per-niche, with a `defaults` block) |
| Per-run overrides | env vars `INTERVIEW_NICHE` · `INTERVIEW_AUDIENCE` · `INTERVIEW_AUTHOR_VOICE` · `INTERVIEW_EMAIL_CTA_TARGET` |

Notes:
- **`--interview` and `--listicle N` now combine** (2026-07-31). Passing both makes call 1
  ask for `N` discrete items instead of broad thematic questions, and call 2 applies the same
  Top-N structure override the classic path uses. This is the strongest combination available:
  the listicle supplies a validated structure, the interview supplies your real examples for
  each item — which is what stops a listicle reading as seven paragraphs of generic advice.
  The two directives are separate on purpose (`build_listicle_question_directive` shapes what
  the interview extracts; `build_listicle_directive` shapes how the article is written).
- `--interview` still ignores `--type` (that shapes the classic writing-agent prompt only).
- In interview mode the worksheet CTA is **not** auto-appended — the article already ends
  with a tailored email CTA from `EMAIL_CTA_TARGET`.
- `--dry-run` works in either mode: it runs the whole flow and saves the draft but prints
  "DRY RUN — nothing staged or published."
- `--no-worksheet` / `--no-carousel` skip the companion worksheet (DS/Life) and IG carousel
  (all niches) steps respectively; both steps are non-fatal and drop a retry command into
  `manual_steps.md` on failure.

Interview logic lives in `scripts/lib/interview.py`; `produce_blog.py` just calls it.

## Tracker integration

`produce_blog.py` reads `output/trackers/annual-tracker-2026.xlsx` as the primary 90-day angle-dedup source before suggesting topics (CLAUDE.md: "TRACKER FIRST"). Falls back to scanning `content/blogs/` if tracker is absent.

`load_posts.py` marks rows `Scheduled` when a slug is staged. `scheduler.py` marks them `Published` after each successful post via `lib/tracker.py:mark_published()`.

## Listicle research (`--listicle N`)

*Added 2026-07-30.* `--listicle N` now changes the **research phase** of `produce_blog.py`,
not just the writing prompt. When set, topic suggestion is grounded in live listicle-demand
research instead of the default Google Suggest + Medium RSS signals used for topic mode.

**Prerequisite — run first, in a Claude Code agent session:**

```bash
/research-listicle-trends --niche <ds|life|poetry> --listicle <N>
```

`.claude/commands/research-listicle-trends.md` drives Chrome across Google Trends, YouTube,
Instagram, and X, applies a listicle-shape regex prefilter, ranks survivors on demand +
decomposability, and writes `data/ideas/listicle_trends_<niche>_<YYYY-MM-DD>.json`.

> This is a separate slash command, not a `produce_blog.py` code path: `produce_blog.py` is a
> plain Python script and cannot call Claude-in-Chrome MCP tools — those exist only inside a
> Claude Code agent session.

**Freshness:** the artifact is valid for today's date only. `N` is stored inside the file, not
the filename, so one research run per niche per day serves any `--listicle N`.

**Graceful degradation:** if no artifact exists for today, `produce_blog.py` prints a warning
naming the exact command to run and falls back to standard research with a listicle-shape
nudge — it never blocks. Instagram and X may be skipped on login walls during research; the
run continues with whatever surfaces responded.

**Downstream effects:** titles are forced to lead with "Top N" or "N …"; the IG carousel step
receives a generated `carousel_outline.md` derived from the blog's `## 1.` … `## N.` headings,
passed to `generate_carousel.py --outline --slides N+2`.

```bash
# research first (agent session)
/research-listicle-trends --niche ds --listicle 7

# then write the blog, grounded in that research
python3 scripts/produce_blog.py --niche ds --listicle 7
```

## Idempotency

Re-running resumes — each step prints `[skip] … (exists)` when its output is present. `--force`
redoes everything (and propagates `--force` to the sub-tools that support it).

## inject_worksheet_ctas.py — retroactive worksheet injection

Run after a worksheet PDF is published to push URLs into all derivatives that were generated before
the worksheet existed. Now covers:

- `instagram_caption.txt` / `instagram_caption_clean.txt`
- `linkedin_post.txt` · `threads_post.txt` · `newsletter.txt`
- `youtube_metadata.json` (replaces `[LINKS_PLACEHOLDER]`)
- **`linkedin_first_comment.txt`** — worksheet URL in the 1st pinned comment (regular post)
- **`linkedin_document_first_comment.txt`** — worksheet URL in the 1st pinned comment (slide deck post)

```bash
python3 scripts/inject_worksheet_ctas.py          # W22 onwards
python3 scripts/inject_worksheet_ctas.py --dry-run
```

## Idea machine + viral reel pipeline

**Weekly idea generation:**
```bash
python3 scripts/idea_scorer.py              # writes data/ideas/weekly_ideas.md
python3 scripts/idea_scorer.py --force      # regenerate
python3 scripts/idea_scorer.py --week W27   # specific week
```

Outputs `weekly_ideas.md` with:
- One tool reel per niche (DS + Life) from `data/kb/projects.json`, angle rotating by ISO week
- 4 Hinglish Raw Take questions for Life (rotating, ~7-week cycle before repeat)
- 5 virality-scored blog/reel ideas per niche (Claude Haiku, deduped vs tracker)

**Standalone viral reel briefs** (recording plan — no existing blog required):
```bash
# Single idea
python3 scripts/generate_viral_reel_brief.py \
    --idea "5 Python one-liners I use daily" --niche ds --week 2026-W26

# This week's mandatory tool reels (reads weekly_ideas.md)
python3 scripts/generate_viral_reel_brief.py --from-weekly --week 2026-W26

# With project context
python3 scripts/generate_viral_reel_brief.py \
    --idea "Why I stopped journaling" --niche life --project free_tool_life --week 2026-W26
```

Output: `content/reels/{week}/{slugified-idea}_reel_brief.md` — full 5-beat recording plan,
5 hook variants, caption, DM keyword, B-roll ideas, recording checklist.

Differs from `generate_ig_reel_brief.py` (which plans clips from an existing recording).
`generate_viral_reel_brief.py` is for reels where nothing has been recorded yet.
