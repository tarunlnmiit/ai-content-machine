---
title: "Wednesday — Life Track (~1.5 hrs)"
type: doc
niche: life_self_dev
slug: wednesday-life
tags: [content/doc, niche/life_self_dev]
---
> ⚠️ **PIPELINE UPDATED 2026-06-20 — canonical model: [`docs/pipeline-2026.md`](../../guides/pipeline-2026.md).**
> Twitter **dropped**. Instagram / Threads **auto-publish** via the Meta Graph API (`scripts/scheduler.py`); Facebook mirrors Instagram; LinkedIn **active** (employer cleared), blog link in the **pinned first comment**. Reels → **Instagram Reels + YouTube Shorts only**, ≈9 **distinct** reels/week (not ~56). Poetry short = **poem only**. Worksheet email CTA (DS/Life) is the owned channel (Substack retired). Run `python3 scripts/weekly_winners.py` before producing. Manual steps left: record · ~10-min approve · reply.
>
> Where any step below disagrees, the canonical doc wins.

# Wednesday — Life Track (~1.5 hrs)

Scripts and assets exist from Tuesday. Today: publish Life blog, shoot talking-head, generate captions, build edit plan.

> **Reference docs:** `prompts/medium-virality-prompt.md` + `data/analytics/medium-stats-2026.md` (pre-publish title check — target read ratio ≥ 40%) · `docs/recording-guide.md` (camera, ring light, audio setup)

---

## Step 1 — Publish Life blog to Medium (~8 min)

```bash
python3 scripts/publish_medium.py \
  --input content/blogs/{week}/{life_slug}.md
```

**To publish to The Ascent (if accepted):**
```bash
python3 scripts/publish_medium.py \
  --input content/blogs/{week}/{life_slug}.md \
  --publication the-ascent
```

Save URL:
```bash
python3 scripts/update_schedule.py \
  --slug {life_slug} --week {week} \
  --medium-url 'https://medium.com/@tarun-gupta/{life_slug}'
```

**Set Medium SEO (manual — API can't):** `publish_medium.py` prints the SEO title +
description + target keyphrase when it finishes. In the Medium draft: ••• → **SEO settings** →
paste them. Then re-upload images. See [medium-seo.md](../../guides/medium-seo.md).

---

## Step 2 — Shoot Life talking-head (~45 min)

### Equipment setup
- iPhone on tripod, 4K 30fps, front-facing
- Ring light at 45° angle; natural light behind camera if available
- Rode Wireless mic or lapel direct to iPhone
- Teleprompter app on second iPhone/iPad: font 60pt+, scroll speed pre-tested

### Before recording
1. Lock white balance: tap background → AE/AF Lock
2. Lock exposure: tap face
3. Script open in teleprompter app — test scroll speed end-to-end before first take
4. Quiet room — turn off fan/AC if audible on mic

### Shoot checklist
- [ ] 3-second clean slate
- [ ] Clap between takes
- [ ] One full uninterrupted take (preferred)
- [ ] Hold 3-second silence at every `[PAUSE]` tag
- [ ] For `[BROLL:]` cues: keep speaking — B-roll overlays picture only
- [ ] Record spontaneous take AFTER scripted one (often more authentic)
- [ ] End with 3-second silence

```bash
mv ~/Downloads/{iphone_recording}.mov "assets/raw/{week}/{life_slug}.mov"
```

---

## Step 3 — Generate captions (~5 min)

```bash
python3 scripts/generate_captions.py \
  --audio "assets/raw/{week}/{life_slug}.mov" \
  --format remotion_json \
  --output "remotion/public/captions/{week}/{life_slug}.captions.json" \
  --model medium
```

Verify:
```bash
python3 -c "
import json
caps = json.load(open('remotion/public/captions/{week}/{life_slug}.captions.json'))
print(f'{len(caps)} tokens, {caps[0][\"startMs\"]}–{caps[-1][\"endMs\"]}ms')
"
```

---

## Step 4 — Generate overlay scene plan (optional, run before Step 5)

```bash
python3 scripts/generate_scene_plans.py \
  --script "content/scripts/{week}/{life_slug}_yt.md" \
  --niche life --week {week} --mode overlay
```

Output: `remotion/public/scene-plans/{week}/{life_slug}_overlay.json`

Life overlay components: `TransformationArc` · `HabitLoop` · `WordReveal` · `QuoteCard` · `StatHighlight`

Layout options:
- `"panel-left"` / `"panel-right"` — fills 1/3 screen; speaker clips to 2/3 (6–10s)
- `"panel-top"` — cinematic banner above speaker; bottom 70% stays (5–8s)

Life videos are reflective → typically 3–6 overlay moments (less dense than DS).

---

## Step 5 — Build edit plan (~5 min)

```bash
python3 scripts/prepare_remotion_edit.py \
  --raw "assets/raw/{week}/{life_slug}.mov" \
  --script "content/scripts/{week}/{life_slug}_yt.md" \
  --niche life --slug {life_slug} --week {week}
```

Output: `remotion/public/edit-plans/{week}/{life_slug}.json`

### Manual tweaks after auto-generation
- Bad cut point → adjust `cutSegments[n].startSec` / `endSec`
- Wrong B-roll description → update `brollCues[n].description`
- Fix title text → update `titleCard.titleText`

### Preview in Remotion Studio
```bash
cd remotion && npm run dev
# → http://localhost:3000
# Select "CourseLesson"
# Props → editPlanFile: "edit-plans/{week}/{life_slug}.json"
```

---

## Verify

```bash
ls -la remotion/public/edit-plans/{week}/{life_slug}*.json
ls -la remotion/public/captions/{week}/{life_slug}*.json
```

Both files present → Life Wednesday complete.

### Troubleshooting

**Whisper finds no audio:**
```bash
ffprobe "assets/raw/{week}/{life_slug}.mov" 2>&1 | grep Audio
```

**No cut points found:**
```bash
python3 scripts/prepare_remotion_edit.py ... --week {week} --sensitivity 0.003
# Or:
python3 scripts/prepare_remotion_edit.py ... --week {week} --no-clap-detection
```
