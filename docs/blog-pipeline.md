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
`--humanize` / `--listicle N` (topic mode → produce_blog), `--dry-run`.

Niche + ISO week are auto-derived from the blog slug.

## What it runs (in order, idempotent — skips when output exists)

| # | Step | Tool | Output |
|---|------|------|--------|
| 0 | (topic mode) write blog | `produce_blog.py` | `content/blogs/{week}/{slug}.md` |
| 1 | Text derivatives | `repurpose_blog.py` | `content/derivatives/{week}/{slug}/` — linkedin_post(+first_comment), instagram_caption(+clean), threads_post, newsletter, polls, slide_outline, youtube_metadata, youtube_shorts_metadata, claude_design_brief, schedule.json |
| 2 | Social images + carousel | `generate_social_images.py --slug` | `assets/social_posts/{week}/{slug}_*.png` + carousel |
| 3 | Slide deck | `generate_slide_deck.py --slug` | `assets/slides/{week}/{slug}_slides.html` (+PDF/PNG); poetry self-skips |
| 4 | IG reel brief | `generate_ig_reel_brief.py --slug` | `…/{slug}/ig_reel_brief.md` |
| 5 | Thumbnail brief (+HTML render) | `thumbnail_brief.py` + `generate_thumbnail.py --export --skip-remotion` | `thumbnail_brief.json` + `assets/thumbnails/{slug}_thumbnail.png` |
| 6 | Worksheet outline (DS/Life) | `generate_worksheet_outline.py` | `content/worksheets/{week}/{slug}_worksheet.json` |
| 7 | Stage to scheduler | `load_posts.py --week` | scheduling DB → auto-publish daemon |

## Stays manual (by design)

- **Videos** — `run_voiceover_week.py` (needs recorded voiceover).
- **Worksheet PDF** — designed in Canva from the outline; then `build-worksheets-manifest.mjs` +
  `inject_worksheet_ctas.py` inject the gated URLs.
- **Thumbnail Canva pass** — `generate_thumbnail.py --canva` (needs a face photo / hook); the
  pipeline only does the automatic HTML thumbnail.

## Idempotency

Re-running resumes — each step prints `[skip] … (exists)` when its output is present. `--force`
redoes everything (and propagates `--force` to the sub-tools that support it).
