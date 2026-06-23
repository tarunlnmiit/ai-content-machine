> ⚠️ **PIPELINE UPDATED 2026-06-20 — canonical model: [`docs/pipeline-2026.md`](../pipeline-2026.md).**
> Twitter **dropped**. Instagram / Threads **auto-publish** via the Meta Graph API (`scripts/scheduler.py`); Facebook mirrors Instagram; LinkedIn **active** (employer cleared), blog link in the **pinned first comment**. Reels → **Instagram Reels + YouTube Shorts only**, ≈9 **distinct** reels/week (not ~56). Poetry short = **poem only**. Worksheet email CTA (DS/Life) is the owned channel (Substack retired). Run `python3 scripts/weekly_winners.py` before producing. Manual steps left: record · ~10-min approve · reply.
>
> Where any step below disagrees, the canonical doc wins.

# Wednesday — Poetry Track (~1.5 hrs)

Scripts and assets exist from Tuesday. Today: publish Poetry blog, shoot talking-head, generate captions, build edit plan.

> **Reference docs:** `prompts/medium-virality-prompt.md` + `data/analytics/medium-stats-2026.md` (pre-publish title check — target read ratio ≥ 40%) · `docs/recording-guide.md` (camera, ring light, audio setup)

---

## Step 1 — Publish Poetry piece to Medium (~8 min)

Poetry format: hook (2–3 lines) → poem → close (1–2 lines) → podcast CTA. Total ~150–200 words. If the file has reflection sections or a takeaway, trim before publishing.

```bash
python3 scripts/publish_medium.py \
  --input content/blogs/{week}/{poetry_slug}.md
```

**To publish to Humans Are Stories (if accepted):**
```bash
python3 scripts/publish_medium.py \
  --input content/blogs/{week}/{poetry_slug}.md \
  --publication humans-are-stories
```

Save URL:
```bash
python3 scripts/update_schedule.py \
  --slug {poetry_slug} --week {week} \
  --medium-url 'https://medium.com/@tarun-gupta/{poetry_slug}'
```

---

## Step 2 — Shoot Poetry talking-head (~45 min)

Poetry videos are talking-head + Remotion animations + optional B-roll. Slower, more intentional pacing than Life.

### Equipment setup
- iPhone on tripod, 4K 30fps, front-facing
- Ring light at 45° angle; natural light behind camera if available
- Rode Wireless mic or lapel direct to iPhone
- Teleprompter app on second iPhone/iPad: font 60pt+, scroll speed pre-tested (slower than Life)

### Before recording
1. Lock white balance: tap background → AE/AF Lock
2. Lock exposure: tap face
3. Script open in teleprompter — test scroll speed before first take (target ~80 wpm)
4. Quiet room — turn off fan/AC if audible

### Shoot checklist
- [ ] 3-second clean slate
- [ ] Clap between takes
- [ ] ~80 words/min pacing — poetry breathes, silence is intentional
- [ ] Hold 3+ seconds at every `[PAUSE]` cue
- [ ] For `[BROLL:]` cues: keep speaking — B-roll overlays talking head
- [ ] Record 2–3 takes; pick the most natural read
- [ ] End with 3-second silence

```bash
mv ~/Downloads/{iphone_recording}.mov "assets/raw/{week}/{poetry_slug}.mov"
```

---

## Step 3 — Generate captions (~5 min)

Use `large` model for Poetry — slow speech, pauses, and accuracy matter.

```bash
python3 scripts/generate_captions.py \
  --audio "assets/raw/{week}/{poetry_slug}.mov" \
  --format remotion_json \
  --output "remotion/public/captions/{week}/{poetry_slug}.captions.json" \
  --model large
```

Verify:
```bash
python3 -c "
import json
caps = json.load(open('remotion/public/captions/{week}/{poetry_slug}.captions.json'))
print(f'{len(caps)} tokens, {caps[0][\"startMs\"]}–{caps[-1][\"endMs\"]}ms')
"
```

---

## Step 4 — Generate overlay scene plan (optional, run before Step 5)

```bash
python3 scripts/generate_scene_plans.py \
  --script "content/scripts/{week}/{poetry_slug}_yt.md" \
  --niche poetry --week {week} --mode overlay
```

Output: `remotion/public/scene-plans/{week}/{poetry_slug}_overlay.json`

Poetry overlay components: `LineReveal` · `AtmosphericQuote` · `WordReveal` · `FadeTitle`

Layout options:
- `"panel-top"` — cinematic banner above speaker (5–8s) — use most often for poetry
- `"panel-left"` / `"panel-right"` — fills 1/3 screen; speaker clips to 2/3 (6–10s)

Poetry videos are reflective → typically 2–4 overlay moments. Less is more.

---

## Step 5 — Build edit plan (~5 min)

```bash
python3 scripts/prepare_remotion_edit.py \
  --raw "assets/raw/{week}/{poetry_slug}.mov" \
  --script "content/scripts/{week}/{poetry_slug}_yt.md" \
  --niche poetry --slug {poetry_slug} --week {week}
```

Output: `remotion/public/edit-plans/{week}/{poetry_slug}.json`

### Manual tweaks after auto-generation
- Bad cut point → adjust `cutSegments[n].startSec` / `endSec`
- Wrong B-roll description → update `brollCues[n].description`
- Fix title text → update `titleCard.titleText`

### Preview in Remotion Studio
```bash
cd remotion && npm run dev
# → http://localhost:3000
# Select "CourseLesson"
# Props → editPlanFile: "edit-plans/{week}/{poetry_slug}.json"
```

---

## Verify

```bash
ls -la remotion/public/edit-plans/{week}/{poetry_slug}*.json
ls -la remotion/public/captions/{week}/{poetry_slug}*.json
```

Both files present → Poetry Wednesday complete.

### Troubleshooting

**Whisper finds no audio:**
```bash
ffprobe "assets/raw/{week}/{poetry_slug}.mov" 2>&1 | grep Audio
```

**Captions mis-timed (slow speech detection):**
```bash
# Force larger model:
python3 scripts/generate_captions.py ... --model large --language en
```

**No cut points found:**
```bash
python3 scripts/prepare_remotion_edit.py ... --week {week} --sensitivity 0.003
# Or:
python3 scripts/prepare_remotion_edit.py ... --week {week} --no-clap-detection
```
