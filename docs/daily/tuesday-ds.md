# Tuesday — DS Track (~1 hr)

Blog exists from Monday. Today: worksheet **first**, then YouTube script, scene plans, social images, slide deck, carousel.

---

## Step 1 — Generate worksheet (~10 min) — do this FIRST

Worksheet before the script so the script can auto-append a spoken "worksheet in the description" CTA (only fires if the worksheet is already in the manifest).

```bash
python3 scripts/generate_worksheet_outline.py \
  -i content/blogs/{week}/{ds_slug}.md

python3 scripts/generate_canva_worksheet_prompt.py \
  -i content/worksheets/{ds_slug}_worksheet.json
```

Paste the printed Canva prompt into Canva AI → export PDF → save to:
```
output/worksheets/{week}/{ds_slug}_worksheet.pdf
```

Build the manifest so the slug is live and the script can see it:
```bash
node scripts/build-worksheets-manifest.mjs
python3 scripts/worksheet_links.py --week {week} --niche data_science_tech
```
No ConvertKit landing page — committing the PDF makes the gated link live. The emitter prints the URL + a blog line + a YouTube description block. (See `documentation/WORKSHEET_WORKFLOW.md`.)

---

## Step 2 — Generate DS YouTube script (~10 min)

Screen-recording style (code tutorial, 8–12 min).

```bash
python3 scripts/ghostwrite.py \
  --source content/blogs/{week}/{ds_slug}.md \
  --niche ds \
  --format yt
```

**Stock/conceptual style** (if not screen recording):
```bash
python3 scripts/ghostwrite.py \
  --source content/blogs/{week}/{ds_slug}.md \
  --niche ds \
  --format yt \
  --video-style stock
```

Output: `content/scripts/{week}/{ds_slug}_yt.md` — includes a spoken `[WORKSHEET CTA]` line (Step 1 worksheet exists) + `ghostwrite.py` prints the YouTube description block to paste at upload.

DS script cues:
```
[HOOK: opening line that stops the scroll]
[SCREEN: show the problem visually]
[CODE_INSERT: paste code block here]
[PAUSE]
[BROLL: cut to relevant b-roll]
[ANIMATION: describe what to animate]
```

**Verify:**
```bash
wc -w content/scripts/{week}/{ds_slug}_yt.md
# Target: 960–1,440 words (8–12 min at 120 wpm)
```

---

## Step 3 — Generate scene plan (~5 min)

Motion short scene plans — 7 unique 30–60s shorts from one script, each a different angle (components auto-chosen by Claude Opus).

```bash
python3 scripts/generate_scene_plans.py \
  --script content/scripts/{week}/{ds_slug}_yt.md \
  --niche ds --week {week} --mode short --shorts 7
```

Output: `remotion/public/scene-plans/{week}/{ds_slug}_s01.json` … `_s07.json`

**Available DS components:** `DataVizReveal` · `CodeAnnotation` · `ConceptExplainer` · `ToolComparison` · `WordReveal` · `NumberedTips`

**Optional — long-form overlay plan** (panels/cutaways on camera footage):
```bash
python3 scripts/generate_scene_plans.py \
  --script content/scripts/{week}/{ds_slug}_yt.md \
  --niche ds --week {week} --mode overlay
# → remotion/public/scene-plans/{week}/{ds_slug}_overlay.json
```

Run BEFORE `prepare_remotion_edit.py` on Wednesday if you want overlay alignment.

**Dry-run to preview:**
```bash
python3 scripts/generate_scene_plans.py \
  --script content/scripts/{week}/{ds_slug}_yt.md \
  --niche ds --week {week} --mode short --dry-run
```

### Generate shorts manifest
```bash
python3 scripts/generate_shorts_manifest.py --week {week} --niche ds
```
Writes: `content/derivatives/{week}/{ds_slug}/shorts_manifest.json` — one slot per `_sNN.json` plan (7 slots).

---

## Step 4 — Generate social images (~10 min)

```bash
python3 scripts/generate_social_images.py --slug {ds_slug}
```

Outputs in `assets/social_posts/{week}/`:
- `{ds_slug}_instagram.png` (1080×1080)
- `{ds_slug}_linkedin.png` (1200×628)
- `{ds_slug}_threads.png` (1080×1080)
- `{ds_slug}_twitter.png` (1200×675)

Upload `{ds_slug}_instagram.png` to Google Drive → `Content/{week}/social/` → set "Anyone with link can view" → copy URL:
```bash
python3 scripts/update_schedule.py \
  --slug {ds_slug} --week {week} \
  --image-url 'https://drive.google.com/uc?id=FILE_ID&export=view'
```

---

## Step 5 — Generate slide deck (~5 min)

```bash
python3 scripts/generate_slide_deck.py --slug {ds_slug}
```

Outputs in `assets/slides/{week}/`:
- `{ds_slug}_slides.html`
- `{ds_slug}/slide_N.png` (7 slides)
- `{ds_slug}/{ds_slug}_slides.pdf`

---

## Step 6 — Generate Instagram carousel (~5 min)

```bash
python3 scripts/generate_carousel.py \
  --blog content/blogs/{week}/{ds_slug}.md
```

Outputs:
- `assets/carousels/{week}/{ds_slug}_carousel.html`
- `assets/carousels/{week}/{ds_slug}/slide_1.png` … `slide_7.png` (1080×1350)

---

## Verify

```bash
python3 scripts/list_week_content.py {week}
```

DS row should show ✓ for: SCRIPTS · SCENE PLANS · IMAGES · SLIDES · CAROUSELS · WORKSHEETS · SHORTS MFST
