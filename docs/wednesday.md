# Wednesday — Poetry Blog + Repurpose All + Design (~40 min)

## Step 0 — Check buffer first (1 min)

```bash
ls content/buffer/week-1/poetry_quotes/*_meta.md 2>/dev/null
```

**Buffer has content?** → Skip Steps 1–3. Use buffer files directly:
- Blog: `content/buffer/week-1/poetry_quotes/*_substack_post.md`
- Social: `content/buffer/week-1/poetry_quotes/*_social_copy.md`

Jump straight to Step 4 (Repurpose all). After consuming: log in Notion as `Script`.

**No buffer?** → Proceed with Steps 1–3 below. Alert: buffer should never be empty — check Sunday Step 7.

---

## Step 1 — Produce Poetry blog

Option A — topic only:
```bash
python3 scripts/produce_blog.py --topic 'YOUR POETRY TOPIC' --niche poetry --humanize
```

Option B — have poem file:
```bash
# Store poem in data/poems/[slug].txt
python3 scripts/ghostwrite.py --source data/poems/[slug].txt --niche poetry --format blog --poet "Poet Name"
# Omit --poet if poem is Tarun's own
```

Option C — have notes/draft:
```bash
python3 scripts/ghostwrite.py --source draft.txt --niche poetry --voice conversational
```

## Step 2 — Fill personal sections
```bash
grep -rn 'PERSONAL_INSERT' content/blogs/
```

## Step 3 — Add images to Poetry blog
```bash
python3 scripts/fetch_images.py --input content/blogs/[wednesday_poetry_blog].md --dry-run
python3 scripts/fetch_images.py --input content/blogs/[wednesday_poetry_blog].md
```

## Step 4 — Repurpose Life + Poetry blogs (with design prompts)
```bash
python3 scripts/repurpose_blog.py --input content/blogs/[tuesday_life_blog].md --design
python3 scripts/repurpose_blog.py --input content/blogs/[wednesday_poetry_blog].md --design
# → content/derivatives/{slug}/ (10 files each)
# → output/scheduled/claude_design_prompts_{slug}.md (4 sections each)
```

## Step 5 — Thumbnail briefs + thumbnail images for Life + Poetry

```bash
# Generate briefs (JSON)
python3 scripts/thumbnail_brief.py --input content/blogs/[tuesday_life_blog].md
python3 scripts/thumbnail_brief.py --input content/blogs/[wednesday_poetry_blog].md
# DS brief already done Tuesday

# Render thumbnails to HTML + PNG (all 3 niches — DS, Life, Poetry)
conda run -n content_engine_env python3 scripts/generate_thumbnail.py \
  --blog content/blogs/[monday_ds_blog].md --export
# → assets/thumbnails/[ds_slug]_thumbnail.png (1280×720)

conda run -n content_engine_env python3 scripts/generate_thumbnail.py \
  --blog content/blogs/[tuesday_life_blog].md --export
# → assets/thumbnails/[life_slug]_thumbnail.png

conda run -n content_engine_env python3 scripts/generate_thumbnail.py \
  --blog content/blogs/[wednesday_poetry_blog].md --export
# → assets/thumbnails/[poetry_slug]_thumbnail.png
```

Open each `.html` in browser to preview before exporting. Use `--force` to regenerate.

## Step 6 — Generate worksheet prompts (IG lead magnets, 5–10 min)

```bash
# Data Science
python3 scripts/generate_worksheet_outline.py -i content/blogs/[monday_ds_blog].md
python3 scripts/generate_canva_worksheet_prompt.py -i content/worksheets/[monday_ds_blog_slug]_worksheet.json

# Life & Self-Dev
python3 scripts/generate_worksheet_outline.py -i content/blogs/[tuesday_life_blog].md
python3 scripts/generate_canva_worksheet_prompt.py -i content/worksheets/[tuesday_life_blog_slug]_worksheet.json

# Poetry — auto-skipped (reflection format, no worksheet expected)
python3 scripts/generate_worksheet_outline.py -i content/blogs/[wednesday_poetry_blog].md
```

Prompts auto-save to `content/prompts/[slug]_worksheet_prompt.txt`

## Step 7 — Design worksheet + landing page in Claude Design (20 min)

**For DS Worksheet:**
1. Claude Design → Paste `content/prompts/[ds_slug]_worksheet_prompt.txt`
2. Generate worksheet design → Export PDF → `output/worksheets/[ds_slug]_worksheet.pdf`
3. Create new Claude Design → Design landing page layout
4. Embed ConvertKit form via HTML embed block
5. Export as shareable link → Save to `config/worksheet_config.json`

**For Life Worksheet:**
1. Claude Design → Paste `content/prompts/[life_slug]_worksheet_prompt.txt`
2. Generate worksheet design → Export PDF → `output/worksheets/[life_slug]_worksheet.pdf`
3. Create new Claude Design → Design landing page layout
4. Embed ConvertKit form via HTML embed block
5. Export as shareable link → Save to `config/worksheet_config.json`

## Step 8 — Claude Design: slides + stories + reel covers (~15 min, 3 blogs)

```bash
mkdir -p assets/{slides,stories,reels}
```

For each blog, open `output/scheduled/claude_design_prompts_{slug}.md` and paste into Claude Design:

| Section | Output | Save to |
|---------|--------|---------|
| 1. Slide deck | PDF | `assets/slides/{slug}_slides.pdf` |
| 2. Instagram Story sequence | PNG sequence | `assets/stories/{slug}_story_*.png` |
| 3. Reel cover | 9:16 PNG | `assets/reels/{slug}_cover.png` |

Section 4 (social post set) is replaced by carousel generation below.

## Step 9 — Generate carousels (replaces social post set, ~10 min, 3 blogs)

Carousels are the primary Instagram post format. Brand kit auto-loaded — no manual prompt.

```bash
mkdir -p assets/carousels

# DS
conda run -n content_engine_env python3 scripts/generate_carousel.py \
  --blog content/blogs/[monday_ds_blog].md

# Life
conda run -n content_engine_env python3 scripts/generate_carousel.py \
  --blog content/blogs/[tuesday_life_blog].md

# Poetry
conda run -n content_engine_env python3 scripts/generate_carousel.py \
  --blog content/blogs/[wednesday_poetry_blog].md
```

Open each `.html` in browser to preview. Then export to PNGs (requires `playwright install chromium` once):

```bash
conda run -n content_engine_env python3 scripts/generate_carousel.py \
  --blog content/blogs/[monday_ds_blog].md --export
# → assets/carousels/slides/{slug}/slide_1.png … slide_7.png
# Repeat for life + poetry blogs
```

**Iterate a slide:**
- Open `.html` in browser → note which slide needs change
- Tell Claude: *"swap slide 4 headline to X"*
- Regenerate: `generate_carousel.py --blog ... --force`

**Manual via Claude Projects:**
```bash
conda run -n content_engine_env python3 -c "
import sys; sys.path.insert(0,'scripts')
from generate_carousel import load_brand, CAROUSEL_SYSTEM
b = load_brand('data_science_tech')  # or life_self_dev / poetry_quotes
print(CAROUSEL_SYSTEM.format(**b, slides=7, initial='B'))
" | pbcopy
# Paste into claude.ai → Projects → Set project instructions
```

---

## After production — buffer or keep live?

```bash
python3 scripts/push_to_buffer.py --auto --dry-run   # preview
python3 scripts/push_to_buffer.py --auto              # auto-decide all niches
```
Buffer < 4 weeks → copied to next empty slot. Buffer full → stays as live content.
File naming: `content/blogs/YYYY-MM-DD_{niche}_{slug}.md` · scripts: `content/scripts/YYYY-MM-DD_{niche-dashes}-{slug}_yt.md`
See full naming table: [weekly-operating-guide.md § File Naming Conventions](weekly-operating-guide.md#file-naming-conventions)

