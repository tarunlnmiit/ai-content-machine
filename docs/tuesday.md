# Tuesday — Video Scripts + Visuals + Scene Plans (~1 hr)

Blogs exist from Monday. Today: generate YouTube scripts for all 3 niches, create all social visual assets, generate Remotion scene plans for motion shorts, and produce worksheets.

## Tuesday at a glance

| Time | Task | Output |
|------|------|--------|
| 9:00 AM | Generate DS YT script | `content/scripts/{week}/{ds_slug}_yt.md` |
| 9:15 AM | Generate Life YT script | `content/scripts/{week}/{life_slug}_yt.md` |
| 9:30 AM | Generate Poetry YT script | `content/scripts/{week}/{poetry_slug}_yt.md` |
| 9:45 AM | Generate Remotion scene plans (all 3) | `remotion/public/scene-plans/{week}/*.json` |
| 10:00 AM | Generate social images (all 3) | `assets/social_posts/{week}/{slug}_*.png` |
| 10:15 AM | Generate slide decks (all 3) | `assets/slides/{week}/{slug}_slides.pdf` |
| 10:30 AM | Generate IG carousels (all 3) | `assets/carousels/{week}/{slug}/slide_1–7.png` |
| 10:45 AM | Generate worksheets (DS + Life) | `output/worksheets/{week}/{slug}_worksheet.pdf` |
| 11:00 AM | Verify all assets | `scripts/list_week_content.py {week}` |

---

## Step 1 — Generate YouTube scripts

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
[CODE_INSERT: paste code block here]
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

```bash
python3 scripts/ghostwrite.py \
  --source content/blogs/{week}/{poetry_slug}.md \
  --niche poetry \
  --format yt
```

Output: `content/scripts/{week}/{poetry_slug}_yt.md`

Poetry script structure:
```
[HOOK: opening line]
[BROLL: abstract/nature visual suggestion]
[PAUSE: intentional silence beat]
```

### Verify scripts

Each script should be:
- 500–1,500 words (8–12 min at 120 wpm)
- Personal voice, no jargon without explanation
- `[SCREEN:]` / `[BROLL:]` / `[CODE_INSERT:]` cues throughout
- No banned words

```bash
wc -w content/scripts/{week}/{ds_slug}_yt.md
wc -w content/scripts/{week}/{life_slug}_yt.md
wc -w content/scripts/{week}/{poetry_slug}_yt.md
```

---

## Step 2 — Generate Remotion scene plans (~5–8 min)

Scene plans drive motion graphic shorts (`DSMotionShort`, `LifeMotionShort`, `PoetryMotionShort`). Claude Opus 4.8 reads the full script semantically and decides WHERE motion graphics make the most sense — no `[ANIMATION:]` tags required.

```bash
# DS — motion short (scenes ARE the video):
python3 scripts/generate_scene_plans.py \
  --script content/scripts/{week}/{ds_slug}_yt.md \
  --niche ds --week {week} --mode short

# Life:
python3 scripts/generate_scene_plans.py \
  --script content/scripts/{week}/{life_slug}_yt.md \
  --niche life --week {week} --mode short

# Poetry:
python3 scripts/generate_scene_plans.py \
  --script content/scripts/{week}/{poetry_slug}_yt.md \
  --niche poetry --week {week} --mode short
```

Outputs: `remotion/public/scene-plans/{week}/{slug}.json`

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

Auto-generate motion-only manifests from scene plans (runs in seconds):

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

## Step 3 — Generate social images (~10 min)

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

After generating, **upload images to Google Drive** (public link required for Metricool CSV):
1. Upload each `{slug}_instagram.png` to Drive → `Content/{week}/social/`
2. Right-click → Get link → set "Anyone with the link can view"
3. Copy the direct download link (use `drive.google.com/uc?id=FILE_ID&export=view` format)
4. Save URL to `schedule.json`:
   ```bash
   python3 scripts/update_schedule.py \
     --slug {ds_slug} \
     --week {week} \
     --image-url 'https://drive.google.com/uc?id=FILE_ID&export=view'
   ```
   Or edit `content/derivatives/{week}/{ds_slug}/schedule.json` directly:
   ```json
   { "image_url": "https://drive.google.com/uc?id=FILE_ID&export=view" }
   ```

---

## Step 3a — Generate slide decks (~10 min)

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

## Step 3b — Generate Instagram carousels (~10 min)

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

## Step 3c — Generate lead-magnet worksheets (DS + Life)

Poetry auto-skips (reflection format, no worksheet). Low-engagement blogs skip too.

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

The Canva prompt prints to console. Paste into Canva AI to generate the worksheet PDF. Export and save to:
```
output/worksheets/{week}/{slug}_worksheet.pdf
```

After Canva export, update ConvertKit landing-page URL in `config/worksheet_config.json`:
```json
{
  "{ds_slug}": {
    "convertkit_url": "https://your-form-link",
    "ig_cta": "DM me WORKSHEET to get the free download"
  }
}
```

---

## Step 4 — Verify all assets (2 min)

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
- Script missing → `ghostwrite.py` failed silently — re-run Step 1
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
