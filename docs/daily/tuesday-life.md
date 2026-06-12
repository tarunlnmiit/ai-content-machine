# Tuesday — Life Track (~55 min)

Blog exists from Monday. Today: worksheet **first**, then YouTube script, scene plans, social images, slide deck, carousel.

---

## Step 1 — Generate worksheet (~10 min) — do this FIRST

Worksheet before the script so the script can auto-append a spoken "worksheet in the description" CTA (only fires if the worksheet is already in the manifest).

```bash
python3 scripts/generate_worksheet_outline.py \
  -i content/blogs/{week}/{life_slug}.md

python3 scripts/generate_canva_worksheet_prompt.py \
  -i content/worksheets/{life_slug}_worksheet.json
```

Paste the printed Canva prompt into Canva AI → export PDF → save to:
```
output/worksheets/{week}/{life_slug}_worksheet.pdf
```

Build the manifest so the slug is live and the script can see it:
```bash
node scripts/build-worksheets-manifest.mjs
python3 scripts/worksheet_links.py --week {week} --niche life_self_dev
```
No ConvertKit landing page — committing the PDF makes the gated link live. The emitter prints the URL + a blog line + a YouTube description block. `config/worksheet_config.json` is optional — only to override the slug-derived title. (See `documentation/WORKSHEET_WORKFLOW.md`.)

---

## Step 2 — Generate Life YouTube script (~10 min)

Talking-head style (personal story, 6–10 min).

```bash
python3 scripts/ghostwrite.py \
  --source content/blogs/{week}/{life_slug}.md \
  --niche life \
  --format yt
```

Output: `content/scripts/{week}/{life_slug}_yt.md` — includes a spoken `[WORKSHEET CTA]` line (Step 1 worksheet exists) + `ghostwrite.py` prints the YouTube description block to paste at upload.

Life script cues:
```
[HOOK: opening story beat that stops the scroll]
[BROLL: cut to relevant b-roll]
[PAUSE]
[TRANSITION: scene shift]
[CTA: mid-roll ask — subscribe / comment / DM]
```

**Verify:**
```bash
wc -w content/scripts/{week}/{life_slug}_yt.md
# Target: 720–1,200 words (6–10 min at 120 wpm)
```

---

## Step 3 — Generate scene plan (~5 min)

Motion short scene plans — 7 unique 30–60s shorts from one script, each a different angle (components auto-chosen by Claude Opus).

```bash
python3 scripts/generate_scene_plans.py \
  --script content/scripts/{week}/{life_slug}_yt.md \
  --niche life --week {week} --mode short --shorts 7
```

Output: `remotion/public/scene-plans/{week}/{life_slug}_s01.json` … `_s07.json`

**Available Life components:** `TransformationArc` · `HabitLoop` · `WordReveal` · `NumberedTips` · `QuoteCard` · `StatHighlight`

**Dry-run to preview:**
```bash
python3 scripts/generate_scene_plans.py \
  --script content/scripts/{week}/{life_slug}_yt.md \
  --niche life --week {week} --mode short --dry-run
```

### Generate shorts manifest
```bash
python3 scripts/generate_shorts_manifest.py --week {week} --niche life
```
Writes: `content/derivatives/{week}/{life_slug}/shorts_manifest.json` — one slot per `_sNN.json` plan (7 slots).

---

## Step 4 — Generate social images (~10 min)

```bash
python3 scripts/generate_social_images.py --slug {life_slug}
```

Outputs in `assets/social_posts/{week}/`:
- `{life_slug}_instagram.png` (1080×1080)
- `{life_slug}_linkedin.png` (1200×628)
- `{life_slug}_threads.png` (1080×1080)
- `{life_slug}_twitter.png` (1200×675)

Upload `{life_slug}_instagram.png` to Google Drive → `Content/{week}/social/` → set "Anyone with link can view" → copy URL:
```bash
python3 scripts/update_schedule.py \
  --slug {life_slug} --week {week} \
  --image-url 'https://drive.google.com/uc?id=FILE_ID&export=view'
```

---

## Step 5 — Generate slide deck (~5 min)

```bash
python3 scripts/generate_slide_deck.py --slug {life_slug}
```

Outputs in `assets/slides/{week}/`:
- `{life_slug}_slides.html`
- `{life_slug}/slide_N.png` (7 slides)
- `{life_slug}/{life_slug}_slides.pdf`

---

## Step 6 — Generate Instagram carousel (~5 min)

```bash
python3 scripts/generate_carousel.py \
  --blog content/blogs/{week}/{life_slug}.md
```

Outputs:
- `assets/carousels/{week}/{life_slug}_carousel.html`
- `assets/carousels/{week}/{life_slug}/slide_1.png` … `slide_7.png` (1080×1350)

---

## Verify

```bash
python3 scripts/list_week_content.py {week}
```

Life row should show ✓ for: SCRIPTS · SCENE PLANS · IMAGES · SLIDES · CAROUSELS · WORKSHEETS · SHORTS MFST
