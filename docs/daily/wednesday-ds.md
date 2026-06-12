# Wednesday — DS Track (~2.5 hrs)

Scripts and assets exist from Tuesday. Today: publish DS blog, shoot screen recording, generate captions, build edit plan.

---

## Step 1 — Publish DS blog to Substack (~10 min)

**1a. Upload cover image:**
```
mcp__substack-breathofdatascience__upload_image
  image_path: "content/blogs/{week}/{ds_slug}_images/cover.jpg"
```
Returns `image_id`.

**1b. Create post:**
```
mcp__substack-breathofdatascience__create_formatted_post
  title: "[title from blog frontmatter]"
  subtitle: "[first sentence of blog]"
  cover_image_id: "[image_id from 1a]"
```
Returns `post_id`.

**1c. Preview:**
```
mcp__substack-breathofdatascience__preview_draft
  post_id: "[post_id]"
```
Verify formatting, images, code blocks.

**1d. Publish:**
```
mcp__substack-breathofdatascience__publish_post
  post_id: "[post_id]"
  send_email: true
```

Save the URL:
```bash
python3 scripts/update_schedule.py \
  --slug {ds_slug} --week {week} \
  --substack-url 'https://breathofdatascience.substack.com/p/{ds_slug}'
```

**Manual fallback:** Open Substack in browser, paste markdown, set cover image, publish.

---

## Step 2 — Publish DS blog to Medium (~8 min)

```bash
python3 scripts/publish_medium.py \
  --input content/blogs/{week}/{ds_slug}.md \
  --canonical-url 'https://breathofdatascience.substack.com/p/{ds_slug}'
```

**To publish to Towards Data Science (if accepted):**
```bash
python3 scripts/publish_medium.py \
  --input content/blogs/{week}/{ds_slug}.md \
  --canonical-url 'https://breathofdatascience.substack.com/p/{ds_slug}' \
  --publication towards-data-science
```

Save URL:
```bash
python3 scripts/update_schedule.py \
  --slug {ds_slug} --week {week} \
  --medium-url 'https://medium.com/@tarun-gupta/{ds_slug}'
```

---

## Step 3 — Shoot DS screen recording (~60 min)

### Setup
- Primary screen: IDE open, font zoomed to 20pt+
- Second screen or iPad: teleprompter showing `content/scripts/{week}/{ds_slug}_yt.md`
- OBS or QuickTime: screen recording at 1920×1080, 30fps
- Face cam (optional PIP): Continuity Camera or USB webcam

### Before recording
1. Do Not Disturb: ON
2. Quit Slack, Mail, notifications
3. Terminal font: 20pt minimum (viewers read code)
4. Test audio: mic showing −12 dB peaks max in OBS

### Shoot checklist
- [ ] 3-second clean slate before first word
- [ ] Clap once before each take / major section
- [ ] Show code RUNNING end-to-end — not just typed, actually executed
- [ ] Follow `[SCREEN:]` cues — zoom/highlight relevant code region
- [ ] Follow `[CODE_INSERT:]` cues — paste block and talk through it live
- [ ] Record 2 takes for critical demo sections
- [ ] End with 3 seconds of silence

```bash
mkdir -p "assets/raw/{week}"
mv ~/Desktop/{recording}.mov "assets/raw/{week}/{ds_slug}_screen.mov"
```

---

## Step 4 — Generate captions (~5 min)

```bash
python3 scripts/generate_captions.py \
  --audio "assets/raw/{week}/{ds_slug}_screen.mov" \
  --format remotion_json \
  --output "remotion/public/captions/{week}/{ds_slug}.captions.json" \
  --model medium
```

Verify:
```bash
python3 -c "
import json
caps = json.load(open('remotion/public/captions/{week}/{ds_slug}.captions.json'))
print(f'{len(caps)} tokens, {caps[0][\"startMs\"]}–{caps[-1][\"endMs\"]}ms')
"
```

---

## Step 5 — Generate overlay scene plan (optional, run before Step 6)

```bash
python3 scripts/generate_scene_plans.py \
  --script "content/scripts/{week}/{ds_slug}_yt.md" \
  --niche ds --week {week} --mode overlay
```

Output: `remotion/public/scene-plans/{week}/{ds_slug}_overlay.json`

DS overlay components: `DataVizReveal` · `CodeAnnotation` · `ConceptExplainer` · `ToolComparison`

Layout options auto-assigned by Claude:
- `"fullscreen"` — full-frame cutaway (4–6s), replaces talking head
- `"panel-left"` / `"panel-right"` — fills 1/3 screen; speaker clips to 2/3 (6–10s)

If file missing when edit plan builds, overlays are silently skipped.

---

## Step 6 — Build edit plan (~5 min)

```bash
python3 scripts/prepare_remotion_edit.py \
  --raw "assets/raw/{week}/{ds_slug}_screen.mov" \
  --script "content/scripts/{week}/{ds_slug}_yt.md" \
  --niche ds --slug {ds_slug} --week {week}
```

Output: `remotion/public/edit-plans/{week}/{ds_slug}.json`

### Manual tweaks after auto-generation
- Bad cut point → adjust `cutSegments[n].startSec` / `endSec`
- Wrong B-roll description → update `brollCues[n].description`
- Fix title text → update `titleCard.titleText`

### Preview in Remotion Studio
```bash
cd remotion && npm run dev
# → http://localhost:3000
# Select "CourseLesson"
# Props → editPlanFile: "edit-plans/{week}/{ds_slug}.json"
```

---

## Verify

```bash
ls -la remotion/public/edit-plans/{week}/{ds_slug}*.json
ls -la remotion/public/captions/{week}/{ds_slug}*.json
```

Both files present → DS Wednesday complete.

### Troubleshooting

**Whisper finds no audio:**
```bash
ffprobe "assets/raw/{week}/{ds_slug}_screen.mov" 2>&1 | grep Audio
```

**No cut points found:**
```bash
python3 scripts/prepare_remotion_edit.py ... --week {week} --sensitivity 0.003
# Or:
python3 scripts/prepare_remotion_edit.py ... --week {week} --no-clap-detection
```

**Substack 401:**
Token expired (30-day TTL). Re-authenticate via MCP server docs or re-paste browser cookie.

**Medium "story too long" (~4,000 word cap):**
Trim blog or publish manually via browser.
