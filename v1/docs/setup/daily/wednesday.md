> ⚠️ **PIPELINE UPDATED 2026-06-20 — canonical model: [`docs/pipeline-2026.md`](../../guides/pipeline-2026.md).**
> Twitter **dropped**. Instagram / Threads **auto-publish** via the Meta Graph API (`scripts/scheduler.py`); Facebook mirrors Instagram; LinkedIn **active** (employer cleared) with the blog link in the **pinned first comment**. Reels → **Instagram Reels + YouTube Shorts only**, ≈9 **distinct** reels/week (not ~56). 3 long-form (1/niche). Poetry short = **poem only**; poetry Medium = poem + 150–350w essay. Worksheet email CTA (DS/Life) is the owned channel (Substack retired). Run `python3 scripts/weekly_winners.py` before producing. Only manual steps left: record · ~10-min approve · reply to comments/DMs.
>
> Where any step below disagrees with this banner or the canonical doc, the canonical doc wins.

# Wednesday — Publish Blogs + Shoot Videos + Prepare Edit Plans (~3 hrs)

Scripts and assets exist from Tuesday. Today: publish all 3 blogs to Medium, shoot all 3 videos, generate captions, and build edit plans so Thursday's renders can start immediately.

## Wednesday at a glance

| Time | Action | Output |
|------|--------|--------|
| 9:00 AM | Publish all 3 blogs → Medium | Live on medium.com/@tarun-gupta |
| 10:00 AM | Shoot DS screen recording + talking-head | `assets/raw/{week}/{ds_slug}_screen.mov` + `{ds_slug}.mov` |
| 11:00 AM | Shoot Life talking-head | `assets/raw/{week}/{life_slug}.mov` |
| 12:00 PM | Shoot Poetry talking-head | `assets/raw/{week}/{poetry_slug}.mov` |
| 1:00 PM | Generate captions (Whisper) all 3 | `remotion/public/captions/{week}/*.json` |
| 1:30 PM | Build edit plans all 3 | `remotion/public/edit-plans/{week}/*.json` |
| 2:30 PM | Verify edit plans in Remotion Studio | Confirm timeline looks right |

---

## Step 1 — Publish to Medium (~15 min)

Medium is the primary publishing destination. No canonical URL needed — Medium is the original source.

> Pre-publish check: title + first paragraph against `prompts/medium-virality-prompt.md`. Target read ratio ≥ 40%.

```bash
# DS blog
python3 scripts/publish_medium.py \
  --input content/blogs/{week}/{ds_slug}.md

# Life blog
python3 scripts/publish_medium.py \
  --input content/blogs/{week}/{life_slug}.md

# Poetry blog
python3 scripts/publish_medium.py \
  --input content/blogs/{week}/{poetry_slug}.md
```

**Publish to a publication instead of personal profile:**
```bash
python3 scripts/publish_medium.py \
  --input content/blogs/{week}/{ds_slug}.md \
  --publication 'towards-data-science'
```

Available publications (if accepted): `towards-data-science` · `humans-are-stories` · `the-ascent`

After publish, save the Medium URL:
```bash
python3 scripts/update_schedule.py \
  --slug {ds_slug} --week {week} \
  --medium-url 'https://medium.com/@tarun-gupta/your-post-slug'
```

Medium URLs are injected into Instagram/Facebook captions by `load_posts.py` on Friday.

### Verify all 3 Medium URLs saved

```bash
python3 -c "
import json, glob
for f in glob.glob('content/derivatives/{week}/*/schedule.json'):
    d = json.load(open(f))
    slug = f.split('/')[-2][:45]
    print(slug)
    print('  Medium:  ', d.get('medium_url', 'MISSING'))
"
```

All 3 Medium URLs should be present. Missing URL → add manually with the update_schedule.py line above.

---

## Step 2 — Shoot DS video (screen recording, ~45 min)

> **Full physical setup reference:** `docs/recording-guide.md` — camera position, ring light angles, audio levels, teleprompter app setup, and common recording problems. Read it once before your first shoot; use it as a quick-reference checklist after that.

### Equipment setup
- Primary screen: IDE open, font zoomed to 20pt+
- Second screen or iPad/iPhone: teleprompter showing script
- OBS or QuickTime: screen recording at 1920×1080, 30fps
- Face cam (optional for pip): use Continuity Camera or external USB webcam

### Before recording
1. Do Not Disturb: ON
2. Quit Slack, Mail, notifications
3. Terminal font: 20pt minimum (viewers need to read code)
4. Teleprompter open on second screen with DS script from `content/scripts/{week}/{ds_slug}_yt.md`
5. Test audio: speak into mic, verify OBS meter shows −12 dB peaks max

### Shoot checklist
- [ ] 3-second clean slate before first word (silence for Whisper calibration)
- [ ] Clap once before each take / major section (audio spike = easy cut point)
- [ ] Show code RUNNING end-to-end — not just typed, actually executed
- [ ] Follow `[SCREEN:]` cues — zoom/highlight relevant code region
- [ ] Talk through each inline ```python block live; for chart `[SCREEN:]` cues, run the preceding block and screenshot the output as the marker PNG. Pull up any "Links to show on screen:" URLs.
- [ ] Record 2 takes for the most important demo sections
- [ ] End with 3 seconds of silence
- [ ] **Sound-off readiness — hook delivery:** Your FIRST spoken words must be the hook line from the `[TEXT_OVERLAY: shown at 0:00]` tag in the script. Do NOT say "alright let's start" or "okay so today we're going to". The moment you open your mouth, the hook comes out. 40% of your viewers will hear nothing — they read it. It must be on screen as text AND spoken.
- [ ] **Shareable moment hold:** When you reach the `[SHAREABLE_MOMENT]` line in the script, slow down and pause 0.5 seconds before and after. This gives the clip room to breathe and makes it easy to isolate for the IG reel.
- [ ] **CTA take:** When saying the comment keyword CTA ("Comment X and I'll send you Y"), look directly at camera. Pause after the keyword. Say it once, cleanly. This 5-second window is the ending of your Instagram reel.

```bash
mkdir -p "assets/raw/{week}"
# Move recording after:
mv ~/Desktop/{recording}.mov "assets/raw/{week}/{ds_slug}_screen.mov"
```

---

## Step 3 — Shoot Life video (talking-head, ~30 min)

### Equipment setup
- iPhone on tripod, 4K 30fps, front-facing
- Ring light at 45° angle; natural light behind camera if available
- Rode Wireless mic or lapel direct to iPhone
- Teleprompter app on second iPhone/iPad: font 60pt+, scroll speed pre-tested

### Before recording
1. Lock white balance (tap background → AE/AF Lock on iPhone)
2. Lock exposure (tap face)
3. Script open in teleprompter app — test scroll speed end-to-end before first take
4. Quiet room — turn off fan/AC if audible on mic

### Shoot checklist
- [ ] 3-second clean slate
- [ ] Clap between takes
- [ ] One full uninterrupted take (preferred) — restart from sentence start when stumbling
- [ ] Hold 3-second silence at every `[PAUSE]` tag (intentional breathing room)
- [ ] For `[BROLL:]` cues: keep speaking — B-roll replaces the picture, not the audio
- [ ] Record spontaneous take AFTER the scripted one (often more authentic)
- [ ] End with 3-second silence
- [ ] **Sound-off readiness — hook delivery:** Open your mouth with the hook line from `[TEXT_OVERLAY: shown at 0:00]` in the script. Not "Hi everyone" or "So today I want to talk about". The hook. First words. Non-negotiable.
- [ ] **Shareable moment hold:** Slow down at the `[SHAREABLE_MOMENT]` line. 0.5-second pause before and after. This becomes the most clipped moment of your reel.
- [ ] **CTA take:** Deliver the comment-keyword CTA looking directly at camera. Clear, unhurried. One clean take. ("Comment STIGMA and I'll send you the full post.")

```bash
# Transfer via AirDrop or Lightning cable, then:
mv ~/Downloads/{iphone_recording}.mov "assets/raw/{week}/{life_slug}.mov"
```

---

## Step 4 — Shoot Poetry talking-head (~30 min)

Poetry videos are talking-head + Remotion animations + optional B-roll. Same setup as Life.

### Equipment setup
- iPhone on tripod, 4K 30fps, front-facing
- Ring light at 45° angle; natural light behind camera if available
- Rode Wireless mic or lapel direct to iPhone
- Teleprompter app on second iPhone/iPad: font 60pt+, scroll speed pre-tested

### Before recording
1. Lock white balance + exposure
2. Script open in teleprompter — test scroll speed before first take
3. Quiet room — turn off fan/AC if audible

### Shoot checklist
- [ ] 3-second clean slate
- [ ] Clap between takes
- [ ] ~80 words/min pacing (poetry breathes — slower than Life)
- [ ] Hold 3+ seconds at every `[PAUSE]` cue (intentional breathing room)
- [ ] For `[BROLL:]` cues: keep speaking — B-roll overlays talking head
- [ ] Record 2–3 takes; pick the most natural read
- [ ] End with 3-second silence
- [ ] **Sound-off readiness — hook delivery:** The hook line from the script is your first spoken words. For poetry, this is the opening couplet or the image-description hook — say it slowly, clearly, without preamble. Viewers in a silent environment will read it as text while you speak it.
- [ ] **Shareable moment hold:** The `[SHAREABLE_MOMENT]` line (from Tuesday's script) — deliver it like you're reading to one person. Hold the camera. 0.5-second pause before and after. This is the clip that gets saved and shared.
- [ ] **Save CTA instead of comment CTA for Poetry:** Poetry CTAs use "Save this if it found you at the right time 🤍" — NOT a comment keyword. There is no comment keyword for poetry reels. The virality metric for poetry is saves ÷ views, not DMs.

```bash
mv ~/Downloads/{iphone_recording}.mov "assets/raw/{week}/{poetry_slug}.mov"
```

---

## Step 5 — Generate captions with Whisper (~5 min per video)

Captions feed Remotion's TikTok-style caption system in `TalkingHeadEdit.tsx`.

```bash
# DS
python3 scripts/generate_captions.py \
  --audio "assets/raw/{week}/{ds_slug}_screen.mov" \
  --format remotion_json \
  --output "remotion/public/captions/{week}/{ds_slug}.captions.json" \
  --model medium

# Life
python3 scripts/generate_captions.py \
  --audio "assets/raw/{week}/{life_slug}.mov" \
  --format remotion_json \
  --output "remotion/public/captions/{week}/{life_slug}.captions.json" \
  --model medium

# Poetry (use large — slow speech, accuracy matters)
python3 scripts/generate_captions.py \
  --audio "assets/raw/{week}/{poetry_slug}.mov" \
  --format remotion_json \
  --output "remotion/public/captions/{week}/{poetry_slug}.captions.json" \
  --model large
```

**Model guide:**
| Model | Speed | Use when |
|-------|-------|---------|
| `tiny` | 30× | Draft/preview only |
| `base` | 15× | Short clips (<5 min) |
| `medium` | 4× | Default |
| `large` | 1× | Poetry, heavy accent, or when accuracy is critical |

**Verify output:**
```bash
python3 -c "
import json
for slug in ['{ds_slug}', '{life_slug}', '{poetry_slug}']:
    caps = json.load(open(f'remotion/public/captions/{week}/{slug}.json'))
    ms_start = caps[0]['startMs'] if caps else 'empty'
    ms_end = caps[-1]['endMs'] if caps else 'empty'
    print(f'{slug}: {len(caps)} tokens, {ms_start}–{ms_end}ms')
"
```

---

## Step 5.5 — Generate overlay scene plans (optional, before Step 7)

Run BEFORE `prepare_remotion_edit.py` so timestamp alignment has the file ready.

```bash
python3 scripts/generate_scene_plans.py \
  --script "content/scripts/{week}/{ds_slug}_yt.md" \
  --niche ds --week {week} --mode overlay --slug {ds_slug}

python3 scripts/generate_scene_plans.py \
  --script "content/scripts/{week}/{life_slug}_yt.md" \
  --niche life --week {week} --mode overlay --slug {life_slug}

python3 scripts/generate_scene_plans.py \
  --script "content/scripts/{week}/{poetry_slug}_yt.md" \
  --niche poetry --week {week} --mode overlay --slug {poetry_slug}
```

Outputs: `remotion/public/scene-plans/{week}/{slug}_overlay.json`

**`--slug` must match the `--slug` you pass to `prepare_remotion_edit.py` in Step 7.** That's how `prepare_remotion_edit.py` auto-detects the overlay file. If they diverge (e.g. overlay generated without `--slug`), use `patch_edit_plan_overlays.py` to fix after the fact (see video-production-guide.md troubleshooting).

Claude decides how many overlay moments based on script density (data-heavy → 8–12; reflective → 2–4). If the file doesn't exist when `prepare_remotion_edit.py` runs, overlays are silently skipped — that's fine.

Each scene includes a `layout` field Claude assigns automatically:

| Layout | Components | Behavior |
|--------|-----------|---------|
| `"fullscreen"` | DataVizReveal, CodeAnnotation, ToolComparison | Full-frame cutaway replaces talking head (4–6s) |
| `"panel-left"` / `"panel-right"` | WordReveal, NumberedTips, ConceptExplainer, AtmosphericQuote, LineReveal, HabitLoop, TransformationArc | Scene fills 1/3 of screen; speaker clips to remaining 2/3 (6–10s) |
| `"panel-top"` | AtmosphericQuote, WordReveal, LineReveal | Cinematic banner above speaker; speaker occupies bottom 70% — poetry/life only, 1–2 per video (5–8s) |

Panel layouts keep the speaker on screen throughout; fullscreen layouts are complete cutaways. Camera slides in/out smoothly over 12 frames on panel entry/exit.

---

## Step 6 — Build edit plans (~5 min each)

Edit plans define the Remotion assembly: cut boundaries, B-roll inserts, title card, lower third, outro, color grading, and overlay scene plan.

```bash
python3 scripts/prepare_remotion_edit.py \
  --raw "assets/raw/{week}/{ds_slug}_screen.mov" \
  --script "content/scripts/{week}/{ds_slug}_yt.md" \
  --niche ds --slug {ds_slug} --week {week}

python3 scripts/prepare_remotion_edit.py \
  --raw "assets/raw/{week}/{life_slug}.mov" \
  --script "content/scripts/{week}/{life_slug}_yt.md" \
  --niche life --slug {life_slug} --week {week}

python3 scripts/prepare_remotion_edit.py \
  --raw "assets/raw/{week}/{poetry_slug}.mov" \
  --script "content/scripts/{week}/{poetry_slug}_yt.md" \
  --niche poetry --slug {poetry_slug} --week {week}
```

Outputs: `remotion/public/edit-plans/{week}/{slug}.json`

### Edit plan JSON structure
```json
{
  "slug": "{slug}",
  "niche": "ds",
  "rawVideo": "videos/{week}/{slug}_screen.mp4",
  "durationSec": 847.3,
  "silenceTrimStartSec": 2.1,
  "silenceTrimEndSec": 847.3,
  "cutSegments": [
    { "startSec": 2.1, "endSec": 245.0 },
    { "startSec": 247.5, "endSec": 490.2 }
  ],
  "brollCues": [
    {
      "id": "cue-0",
      "description": "Python code dark screen, terminal output",
      "startSec": 60.0,
      "durationSec": 5,
      "clipFile": "broll/{week}/{slug}/cue-0.mp4"
    }
  ],
  "captionsFile": "captions/{week}/{slug}.json",
  "showSubtitles": true,
  "titleCard": {
    "titleText": "Your Video Title",
    "showName": "Breath of Data Science",
    "durationFrames": 90,
    "insertAtFrame": 0
  },
  "lowerThird": {
    "text": "Breath of Data Science",
    "durationFrames": 90,
    "insertAtFrame": 150
  },
  "outroCard": {
    "nextText": "More on Breath of Data Science",
    "durationFrames": 150
  },
  "colorGrading": {
    "saturate": 1.12,
    "hueRotate": 3,
    "contrast": 1.07,
    "brightness": 1.0,
    "overlayColor": "rgba(120, 180, 255, 0.05)"
  },
  "scenePlanFile": "scene-plans/{week}/{slug}_overlay.json"
}
```

### Manual tweaks after auto-generation
- Bad cut point → adjust `cutSegments[n].startSec` / `endSec`
- Wrong B-roll → change `brollCues[n].description` (search hint) or `brollCues[n].clipFile` (swap clip directly)
- Title text → update `titleCard.titleText`
- Remove title card → delete `titleCard` key

### Preview in Remotion Studio
```bash
cd remotion && npm run dev
# → http://localhost:3000
# Select "CourseLesson" composition
# In Props panel, set: editPlanFile: "edit-plans/{week}/{ds_slug}.json"
# Scrub timeline to verify cuts, captions, B-roll alignment
```

---

## Step 7 — Verify (5 min)

```bash
# All 3 edit plans exist
ls -la remotion/public/edit-plans/{week}/
# All 3 caption files exist
ls -la remotion/public/captions/{week}/

# Validate JSON + print segment summary
python3 -c "
import json, glob
for f in sorted(glob.glob('remotion/public/edit-plans/{week}/*.json')):
    d = json.load(open(f))
    segs = d.get('cutSegments', [])
    mins = sum(s['endSec']-s['startSec'] for s in segs)/60
    print(f.split('/')[-1], f'→ {len(segs)} cuts, ~{mins:.1f} min')
"
```

---

## Step 7.5 — Generate overlay manifest with timestamps (if using overlays)

**Only if Step 6.5 was run.** Align overlay scenes to caption timestamps and generate manifest for DaVinci placement.

```bash
# Step 1: For each niche, patch overlay scenes with timestamps from captions
python3 scripts/patch_edit_plan_overlays.py \
  --edit-plan "remotion/public/edit-plans/{week}/{ds_slug}.json" \
  --overlay   "remotion/public/scene-plans/{week}/{ds_slug}_overlay.json"

python3 scripts/patch_edit_plan_overlays.py \
  --edit-plan "remotion/public/edit-plans/{week}/{life_slug}.json" \
  --overlay   "remotion/public/scene-plans/{week}/{life_slug}_overlay.json"

python3 scripts/patch_edit_plan_overlays.py \
  --edit-plan "remotion/public/edit-plans/{week}/{poetry_slug}.json" \
  --overlay   "remotion/public/scene-plans/{week}/{poetry_slug}_overlay.json"

# Step 2: Render overlay scenes to MP4 + generate manifest.csv with startSec timestamps
python3 scripts/render_overlay_scenes.py --week {week}
```

Output: `output/animations/{week}/overlay-scenes/manifest.csv` with columns:
- `niche`, `scene_id`, `component_name`, `duration_sec`, `output_file`, `script`, **`startSec`**, **`matched`**

Use `startSec` to position each overlay on a separate track in DaVinci during manual editing. `matched=True` means the timestamp was anchored to a real spoken phrase in the transcript; `matched=False` means it was interpolated between neighbors (e.g. code snippets never spoken aloud) — eyeball those and nudge as needed.

**If the take was ad-libbed off-script** (triggers won't match the written script), re-anchor to the spoken transcript before patching:
```bash
python3 scripts/retrofit_scene_triggers.py \
  --overlay "remotion/public/scene-plans/{week}/{slug}_overlay.json"
# then re-run patch_edit_plan_overlays.py + render_overlay_scenes.py above
```

### Step 8.6 — Generate the manual placement sheet

One Markdown sheet per niche telling you which clip to drop where during the DaVinci edit:
```bash
python3 scripts/overlay_placement_sheet.py --week {week}
# → output/animations/{week}/overlay-scenes/{NICHE}_PLACEMENT.md  (one per niche)
```
Each sheet lists every overlay's timestamp (from your first spoken word), duration, clip filename, an Exact?/estimated flag, and the on-screen text. Open it beside DaVinci: talking-head on V1, drop each clip on V2 at its listed time (full-frame cutaway), or scale to ~35% for a side panel.

Expected: 3 edit plans parseable, 3 caption files present, total duration 8–15 min each.

---

## Troubleshooting

**Whisper finds no audio:**
```bash
# Check audio track exists:
ffprobe "assets/raw/{week}/{slug}.mov" 2>&1 | grep Audio
# No audio → re-export from camera app
```

**prepare_remotion_edit.py finds no silence (no cut points):**
```bash
# Lower threshold:
python3 scripts/prepare_remotion_edit.py ... --week {week} --sensitivity 0.003
# Or force single segment (no cuts):
python3 scripts/prepare_remotion_edit.py ... --week {week} --no-clap-detection
```

**Medium publish fails "story too long":**
- ~4,000 word soft cap for API publish
- Trim blog OR publish manually via browser
