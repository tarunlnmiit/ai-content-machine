# Wednesday — Publish Blogs + Shoot Videos + Prepare Edit Plans (~3 hrs)

Scripts and assets exist from Tuesday. Today: publish all 3 blogs to Substack + Medium, shoot all 3 videos, generate captions, and build edit plans so Thursday's renders can start immediately.

## Wednesday at a glance

| Time | Action | Output |
|------|--------|--------|
| 9:00 AM | Publish DS blog → Substack (MCP) | Live on breathofdatascience.substack.com |
| 9:10 AM | Publish Life blog → Substack (MCP) | Live on thisisbreathoflife.substack.com |
| 9:20 AM | Publish Poetry blog → Substack (MCP) | Live on breathofpoetry.substack.com |
| 9:30 AM | Publish all 3 → Medium | Live on medium.com/@tarun-gupta |
| 10:00 AM | Shoot DS screen recording + talking-head | `assets/raw/{week}/{ds_slug}_screen.mov` + `{ds_slug}.mov` |
| 11:00 AM | Shoot Life talking-head | `assets/raw/{week}/{life_slug}.mov` |
| 12:00 PM | Shoot Poetry talking-head | `assets/raw/{week}/{poetry_slug}.mov` |
| 1:00 PM | Generate captions (Whisper) all 3 | `remotion/public/captions/{week}/*.json` |
| 1:30 PM | Build edit plans all 3 | `remotion/public/edit-plans/{week}/*.json` |
| 2:30 PM | Verify edit plans in Remotion Studio | Confirm timeline looks right |

---

## Step 1 — Publish to Substack (MCP tool calls)

Use Claude Code with Substack MCP tools. Three MCP servers map to three publications.

### DS → breathofdatascience.substack.com

**1a. Upload cover image:**
```
mcp__substack-breathofdatascience__upload_image
  image_path: "content/blogs/{week}/{ds_slug}_images/cover.jpg"
```
Returns `image_id`. Use in Step 1b.

**1b. Create formatted post:**
```
mcp__substack-breathofdatascience__create_formatted_post
  title: "[title from blog frontmatter]"
  subtitle: "[first sentence of blog]"
  cover_image_id: "[image_id from 1a]"
```
Returns `post_id`.

**1c. Preview (recommended before publishing):**
```
mcp__substack-breathofdatascience__preview_draft
  post_id: "[post_id]"
```
Opens preview URL — verify formatting, images, code blocks look right.

**1d. Publish:**
```
mcp__substack-breathofdatascience__publish_post
  post_id: "[post_id]"
  send_email: true
```

Copy the live URL. Save it:
```bash
python3 scripts/update_schedule.py \
  --slug {ds_slug} --week {week} \
  --substack-url 'https://breathofdatascience.substack.com/p/{ds_slug}'
```

### Life → thisisbreathoflife.substack.com

```
mcp__substack-breathoflife__upload_image
  image_path: "content/blogs/{week}/{life_slug}_images/cover.jpg"

mcp__substack-breathoflife__create_formatted_post
  title: "[title]"
  subtitle: "[subtitle]"
  cover_image_id: "[image_id]"

mcp__substack-breathoflife__publish_post
  post_id: "[post_id]"
  send_email: true
```

### Poetry → breathofpoetry.substack.com

```
mcp__substack-breathofpoetry__upload_image
  image_path: "content/blogs/{week}/{poetry_slug}_images/cover.jpg"

mcp__substack-breathofpoetry__create_formatted_post
  title: "[title]"
  cover_image_id: "[image_id]"

mcp__substack-breathofpoetry__publish_post
  post_id: "[post_id]"
  send_email: true
```

**Manual fallback if MCP fails:**
Open Substack in browser, paste the blog markdown text into the editor, set cover image, publish. Save the URL manually.

---

## Step 2 — Publish to Medium (~15 min)

Medium accepts blogs with canonical URL pointing back to Substack (signals Substack as the original source — good for SEO).

```bash
# DS blog
python3 scripts/publish_medium.py \
  --input content/blogs/{week}/{ds_slug}.md \
  --canonical-url 'https://breathofdatascience.substack.com/p/{ds_slug}'

# Life blog
python3 scripts/publish_medium.py \
  --input content/blogs/{week}/{life_slug}.md \
  --canonical-url 'https://thisisbreathoflife.substack.com/p/{life_slug}'

# Poetry blog
python3 scripts/publish_medium.py \
  --input content/blogs/{week}/{poetry_slug}.md \
  --canonical-url 'https://breathofpoetry.substack.com/p/{poetry_slug}'
```

**Publish to a publication instead of personal profile:**
```bash
python3 scripts/publish_medium.py \
  --input content/blogs/{week}/{ds_slug}.md \
  --canonical-url '...' \
  --publication 'towards-data-science'
```

Available publications (if accepted): `towards-data-science` · `humans-are-stories` · `the-ascent`

**Tags (auto-generated; override if wrong):**
```bash
--tags 'python,data-science,machine-learning'
```

After publish, save the Medium URL:
```bash
python3 scripts/update_schedule.py \
  --slug {ds_slug} --week {week} \
  --medium-url 'https://medium.com/@tarun-gupta/your-post-slug'
```

Medium URLs are injected into Instagram/Facebook captions by `load_posts.py` on Friday.

### Verify all 3 blog URLs saved

```bash
python3 -c "
import json, glob
for f in glob.glob('content/derivatives/{week}/*/schedule.json'):
    d = json.load(open(f))
    slug = f.split('/')[-2][:45]
    print(slug)
    print('  Substack:', d.get('substack_url', 'MISSING'))
    print('  Medium:  ', d.get('medium_url', 'MISSING'))
"
```

All 6 URLs should be present. Missing Medium URL → add manually. Missing Substack URL → re-run the update_schedule.py line above.

---

## Step 3 — Shoot DS video (screen recording, ~45 min)

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
- [ ] Follow `[CODE_INSERT:]` cues — paste the code block and talk through it live
- [ ] Record 2 takes for the most important demo sections
- [ ] End with 3 seconds of silence

```bash
mkdir -p "assets/raw/{week}"
# Move recording after:
mv ~/Desktop/{recording}.mov "assets/raw/{week}/{ds_slug}_screen.mov"
```

---

## Step 4 — Shoot Life video (talking-head, ~30 min)

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

```bash
# Transfer via AirDrop or Lightning cable, then:
mv ~/Downloads/{iphone_recording}.mov "assets/raw/{week}/{life_slug}.mov"
```

---

## Step 5 — Shoot Poetry talking-head (~30 min)

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

```bash
mv ~/Downloads/{iphone_recording}.mov "assets/raw/{week}/{poetry_slug}.mov"
```

---

## Step 6 — Generate captions with Whisper (~5 min per video)

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

## Step 7 — Build edit plans (~5 min each)

Edit plans define the Remotion assembly: cut boundaries, B-roll inserts, title card, lower third, outro.

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
  "videoFile": "videos/{week}/{slug}_screen.mov",
  "captionFile": "captions/{week}/{slug}.json",
  "silenceTrimStartSec": 2.1,
  "silenceTrimEndSec": 847.3,
  "cutSegments": [
    { "startSec": 2.1, "endSec": 245.0 },
    { "startSec": 247.5, "endSec": 490.2 }
  ],
  "brollCues": [
    { "atSec": 60.0, "durationSec": 5, "query": "Python code dark screen" }
  ],
  "titleCard": {
    "titleText": "Your Video Title",
    "durationFrames": 90,
    "insertAtFrame": 0
  },
  "outroCard": {
    "nextText": "Next: Upcoming Video Title",
    "durationFrames": 150
  },
  "niche": "ds"
}
```

### Manual tweaks after auto-generation
- Bad cut point → adjust `cutSegments[n].startSec` / `endSec`
- Wrong B-roll → change `brollCues[n].query` string
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

## Step 8 — Verify (5 min)

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
python3 scripts/prepare_remotion_edit.py ... --sensitivity 0.003
# Or force single segment (no cuts):
python3 scripts/prepare_remotion_edit.py ... --no-clap-detection
```

**Substack MCP returns 401 Unauthorized:**
- Token expired — tokens last 30 days
- Re-authenticate: check MCP server docs for re-auth flow, or re-paste cookie from browser DevTools

**Medium publish fails "story too long":**
- ~4,000 word soft cap for API publish
- Trim blog OR publish manually via browser
