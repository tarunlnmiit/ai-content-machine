# Tuesday — Poetry Track (~40 min)

Blog exists from Monday. Today: generate YouTube script, scene plans, social images, slide deck, and carousel. No worksheet for Poetry.

---

## Step 1 — Generate Poetry YouTube script (~10 min)

Talking-head + voiceover style (poem reading + reflection, 4–8 min).

```bash
python3 scripts/ghostwrite.py \
  --source content/blogs/{week}/{poetry_slug}.md \
  --niche poetry \
  --format yt
```

Output: `content/scripts/{week}/{poetry_slug}_yt.md`

Poetry script cues:
```
[HOOK: evocative opening line or image]
[POEM: read the poem slowly — mark pauses]
[REFLECTION: personal thought on the poem]
[PAUSE]
[BROLL: atmospheric visuals — nature, mood]
[CTA: subscribe / comment favorite line]
```

**Verify:**
```bash
wc -w content/scripts/{week}/{poetry_slug}_yt.md
# Target: 480–960 words (4–8 min at 120 wpm)
```

---

## Step 2 — Generate scene plan (~5 min)

Motion short scene plans — 7 unique 30–60s shorts from one script, each a different angle (components auto-chosen by Claude Opus).

```bash
python3 scripts/generate_scene_plans.py \
  --script content/scripts/{week}/{poetry_slug}_yt.md \
  --niche poetry --week {week} --mode short --shorts 7
```

Output: `remotion/public/scene-plans/{week}/{poetry_slug}_s01.json` … `_s07.json`

**Available Poetry components:** `LineReveal` · `AtmosphericQuote` · `WordReveal` · `QuoteCard` · `FadeTitle`

**Dry-run to preview:**
```bash
python3 scripts/generate_scene_plans.py \
  --script content/scripts/{week}/{poetry_slug}_yt.md \
  --niche poetry --week {week} --mode short --dry-run
```

### Generate shorts manifest
```bash
python3 scripts/generate_shorts_manifest.py --week {week} --niche poetry
```
Writes: `content/derivatives/{week}/{poetry_slug}/shorts_manifest.json` — one slot per `_sNN.json` plan (7 slots).

> Note: `generate_scene_plans.py --shorts 7` now produces 7 distinct shorts directly. The old `split_scene_plan.py` workaround (splitting one 12-scene plan into N files) is no longer needed.

---

## Step 3 — Generate social images (~5 min)

```bash
python3 scripts/generate_social_images.py --slug {poetry_slug}
```

Outputs in `assets/social_posts/{week}/`:
- `{poetry_slug}_instagram.png` (1080×1080)
- `{poetry_slug}_linkedin.png` (1200×628)
- `{poetry_slug}_threads.png` (1080×1080)
- `{poetry_slug}_twitter.png` (1200×675)

Upload `{poetry_slug}_instagram.png` to Google Drive → `Content/{week}/social/` → set "Anyone with link can view" → copy URL:
```bash
python3 scripts/update_schedule.py \
  --slug {poetry_slug} --week {week} \
  --image-url 'https://drive.google.com/uc?id=FILE_ID&export=view'
```

---

## Step 4 — Generate slide deck (~5 min)

```bash
python3 scripts/generate_slide_deck.py --slug {poetry_slug}
```

Outputs in `assets/slides/{week}/`:
- `{poetry_slug}_slides.html`
- `{poetry_slug}/slide_N.png` (7 slides)
- `{poetry_slug}/{poetry_slug}_slides.pdf`

---

## Step 5 — Generate Instagram carousel (~5 min)

```bash
python3 scripts/generate_carousel.py \
  --blog content/blogs/{week}/{poetry_slug}.md
```

Outputs:
- `assets/carousels/{week}/{poetry_slug}_carousel.html`
- `assets/carousels/{week}/{poetry_slug}/slide_1.png` … `slide_7.png` (1080×1350)

---

## Verify

```bash
python3 scripts/list_week_content.py {week}
```

Poetry row should show ✓ for: SCRIPTS · SCENE PLANS · IMAGES · SLIDES · CAROUSELS · SHORTS MFST

No worksheet for Poetry niche — skip that column.
