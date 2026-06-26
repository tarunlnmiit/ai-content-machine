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

> **`--type` is DS-only.** `--type tutorial` = code-first post with runnable Python; `--type news` = editorial/opinion piece with no code. Rejected for Life and Poetry.

Niche + ISO week are auto-derived from the blog slug.

## What it runs (in order, idempotent — skips when output exists)

| # | Step | Tool | Output |
|---|------|------|--------|
| 0 | (topic mode) write blog | `produce_blog.py` | `content/blogs/{week}/{slug}.md` |
| 1 | **Phase 1** text derivatives | `repurpose_blog.py` | `content/derivatives/{week}/{slug}/` — linkedin_post(+linkedin_second_comment=blog link), linkedin_document_caption (slide deck post body), instagram_caption(+clean), newsletter, polls, slide_outline, youtube_metadata, youtube_shorts_metadata, claude_design_brief, schedule.json. **Threads dropped.** LinkedIn comment order: 1st=Worksheet (Phase 2) · 2nd=Blog link (Phase 1). |
| 1b | **Phase 2** (auto, inside repurpose_blog.py) | same call | 2a worksheet outline JSON + Canva design prompt (DS/Life; PDF is Canva-manual) · 2b blog CTA inject · 2c linkedin_first_comment (worksheet, 1st) + 2c2 linkedin_document comments (worksheet 1st + YT link 2nd) · 2d slide deck (virality_block + master_brief) · 2e IG carousel (+Playwright PNG export, virality_block + caption formula + master_brief) · 2f IG reel brief · 2g YT filming script (virality_block + master_brief) |
| 2 | Social images | `generate_social_images.py --slug` | `assets/social_posts/{week}/{slug}_*.png` |
| 3 | Thumbnail brief (+HTML render) | `thumbnail_brief.py` + `generate_thumbnail.py --export --skip-remotion` | `thumbnail_brief.json` + `assets/thumbnails/{slug}_thumbnail.png` |
| 4 | Stage to scheduler | `load_posts.py --week` | scheduling DB → auto-publish daemon |

> Steps 3 (slide deck), 4 (IG reel brief), 6 (worksheet) in `run_blog_pipeline.py` are now **also run inside `repurpose_blog.py` Phase 2** — they skip idempotently if output already exists. Running `run_blog_pipeline.py` still works fine.

## Stays manual (by design)

- **Videos** — `run_voiceover_week.py` (needs recorded voiceover).
- **Worksheet PDF** — designed in Canva from the outline; then `build-worksheets-manifest.mjs` +
  `inject_worksheet_ctas.py` inject the gated URLs.
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
   stored as a trailing `<!-- Medium tags: … -->` comment. Continue to publishing as usual.

**Editable without touching code:**

| What | Where |
|------|-------|
| Question-generator prompt | `prompts/question_generator.md` (keep the `{{TOPIC}}` etc. placeholders) |
| Article-writer prompt | `prompts/article_writer.md` (keep the `{{ANSWERS}}` etc. placeholders) |
| NICHE · AUDIENCE · AUTHOR_VOICE · EMAIL_CTA_TARGET | `config/interview.json` (per-niche, with a `defaults` block) |
| Per-run overrides | env vars `INTERVIEW_NICHE` · `INTERVIEW_AUDIENCE` · `INTERVIEW_AUTHOR_VOICE` · `INTERVIEW_EMAIL_CTA_TARGET` |

Notes:
- `--interview` ignores `--listicle` / `--type` (those shape the classic writing-agent path).
- In interview mode the worksheet CTA is **not** auto-appended — the article already ends
  with a tailored email CTA from `EMAIL_CTA_TARGET`.
- `--dry-run` works in either mode: it runs the whole flow and saves the draft but prints
  "DRY RUN — nothing staged or published."

Interview logic lives in `scripts/lib/interview.py`; `produce_blog.py` just calls it.

## Tracker integration

`produce_blog.py` reads `output/trackers/annual-tracker-2026.xlsx` as the primary 90-day angle-dedup source before suggesting topics (CLAUDE.md: "TRACKER FIRST"). Falls back to scanning `content/blogs/` if tracker is absent.

`load_posts.py` marks rows `Scheduled` when a slug is staged. `scheduler.py` marks them `Published` after each successful post via `lib/tracker.py:mark_published()`.

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
