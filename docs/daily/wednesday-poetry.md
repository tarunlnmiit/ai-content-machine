# Wednesday — Poetry Track (~1.5 hrs)

Scripts and assets exist from Tuesday. Today: publish Poetry blog, shoot talking-head, generate captions, build edit plan.

---

## Step 1 — Publish Poetry blog to Substack (~10 min)

**1a. Upload cover image:**
```
mcp__substack-breathofpoetry__upload_image
  image_path: "content/blogs/{week}/{poetry_slug}_images/cover.jpg"
```
Returns `image_id`.

**1b. Create post:**
```
mcp__substack-breathofpoetry__create_formatted_post
  title: "[title from blog frontmatter]"
  cover_image_id: "[image_id from 1a]"
```
Returns `post_id`.

**1c. Preview:**
```
mcp__substack-breathofpoetry__preview_draft
  post_id: "[post_id]"
```

**1d. Publish:**
```
mcp__substack-breathofpoetry__publish_post
  post_id: "[post_id]"
  send_email: true
```

Save URL:
```bash
python3 scripts/update_schedule.py \
  --slug {poetry_slug} --week {week} \
  --substack-url 'https://breathofpoetry.substack.com/p/{poetry_slug}'
```

**Manual fallback:** Open Substack in browser, paste markdown, set cover image, publish.

---

## Step 2 — Publish Poetry blog to Medium (~8 min)

```bash
python3 scripts/publish_medium.py \
  --input content/blogs/{week}/{poetry_slug}.md \
  --canonical-url 'https://breathofpoetry.substack.com/p/{poetry_slug}'
```

**To publish to Humans Are Stories (if accepted):**
```bash
python3 scripts/publish_medium.py \
  --input content/blogs/{week}/{poetry_slug}.md \
  --canonical-url 'https://breathofpoetry.substack.com/p/{poetry_slug}' \
  --publication humans-are-stories
```

Save URL:
```bash
python3 scripts/update_schedule.py \
  --slug {poetry_slug} --week {week} \
  --medium-url 'https://medium.com/@tarun-gupta/{poetry_slug}'
```

---

## Step 3 — Shoot Poetry talking-head (~45 min)

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

## Step 4 — Generate captions (~5 min)

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

## Step 5 — Generate overlay scene plan (optional, run before Step 6)

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

## Step 6 — Build edit plan (~5 min)

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
