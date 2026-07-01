> ⚠️ **PIPELINE UPDATED 2026-06-20 — canonical model: [`docs/pipeline-2026.md`](pipeline-2026.md).**
> Twitter **dropped**. Instagram / Threads **auto-publish** via the Meta Graph API (`scripts/scheduler.py`); Facebook mirrors Instagram; LinkedIn **active** (employer cleared) with the blog link in the **pinned first comment**. Reels → **Instagram Reels + YouTube Shorts only**, ≈9 **distinct** reels/week (not ~56). 3 long-form (1/niche). Poetry short = **poem only**; poetry Medium = poem + 150–350w essay. Worksheet email CTA (DS/Life) is the owned channel (Substack retired). Run `python3 scripts/weekly_winners.py` before producing. Only manual steps left: record · ~10-min approve · reply to comments/DMs.
>
> Where any step below disagrees with this banner or the canonical doc, the canonical doc wins.

# Weekly Runner

One document. Every command. Every prompt. Run it top to bottom.

**Step labels:**
- **[CLAUDE]** — paste this prompt into Claude in this Cowork session
- **[SCRIPT]** — Claude runs this bash command for you in this session
- **[YOU]** — only you can do this (physical or platform action)

**Daily docs are troubleshooting reference only. You never need to open them to run a week.**

---

## Fill in before starting

| Variable | W22 value | Your week |
|----------|-----------|-----------|
| `{week}` | `2026-W22` | |
| `{ds_slug}` | `2026-05-25_data_science_tech_python-for-data-science-tutorial-210` | |
| `{life_slug}` | `2026-05-26_life_self_dev_mental-health-openness-and-breaking-stigmas` | |
| `{poetry_slug}` | `2026-05-27_poetry_quotes_intoxicated-senses` | |
| `{ds_publish_date}` | `YYYY-MM-DD` (Wednesday) | |
| `{life_publish_date}` | `YYYY-MM-DD` (Wednesday) | |
| `{poetry_publish_date}` | `YYYY-MM-DD` (Thursday) | |

---

## Track A — Existing drafts + edited video
*Blog .md files already written. Video already edited in DaVinci.*

---

### Phase 0 — Setup

**Step 1 — Full asset audit** [SCRIPT]

Why: every downstream step depends on specific files existing. Run this first — it tells you exactly what's missing and the exact command to create it. Nothing else in the runner should run until all blocking gaps are resolved.

```bash
python3 - << 'EOF'
import os, glob, re

WEEK   = "{week}"
SLUGS  = {
    "DS":     "{ds_slug}",
    "Life":   "{life_slug}",
    "Poetry": "{poetry_slug}",
}

def found(pattern):
    return bool(glob.glob(pattern))

def check(label, pattern, fix):
    ok = found(pattern)
    mark = "✅" if ok else "❌"
    print(f"  {mark}  {label}")
    if not ok:
        print(f"       FIX: {fix}")
        print()

print(f"\n{'='*60}")
print(f"ASSET AUDIT — {WEEK}")
print(f"{'='*60}\n")

for niche, slug in SLUGS.items():
    print(f"── {niche} ({slug[:30]}…)\n")

    # Asset-layer files (blog, thumbnail, captions, scene-plan) use the CONTENT slug.
    # Remotion-layer files (edit-plan, source video, render output, short) may use a
    # `_yt`/posting-date slug instead. The content DATE is present in every variant, so
    # match those by date to stay slug-tolerant.
    date = slug[:10]

    check(
        "Blog .md",
        f"content/blogs/{WEEK}/{slug}.md",
        "[YOU] Write the blog — Track B workflow (Monday step)"
    )
    check(
        "Edited video .mp4",
        f"assets/video/edited/{WEEK}/{slug}*.mp4",
        "[YOU] Record and edit in DaVinci Resolve — no automation available"
    )
    check(
        "Thumbnail .png",
        f"assets/thumbnails/{WEEK}/{slug}*thumbnail*.png",
        f"Step 12 [CLAUDE]: generate a ChatGPT image-creator prompt (blog + per-niche thumbnail rule)\n"
        f"       Then Step 13 [YOU]: paste into ChatGPT image creator, attach face photo,\n"
        f"       export PNG to assets/thumbnails/{WEEK}/{slug}_thumbnail.png"
    )
    check(
        "Captions .json",
        f"remotion/public/captions/{WEEK}/{slug}*.json",
        f"python3 scripts/generate_captions.py --slug {slug}\n"
        f"       (uses Whisper — takes 5-10 min per video)"
    )
    check(
        "Instagram reel brief",
        f"content/derivatives/{WEEK}/{slug}/ig_reel_brief.md",
        f"Step 11: python3 scripts/generate_ig_reel_brief.py --week {WEEK}"
    )
    check(
        "Overlay scene plan .json",
        f"remotion/public/scene-plans/{WEEK}/{slug}*overlay*.json",
        f"Step 16: python3 scripts/generate_scene_plans.py \\\n"
        f"           --captions remotion/public/captions/{WEEK}/{slug}*.json \\\n"
        f"           --niche {niche.lower()} --week {WEEK} --mode overlay\n"
        f"         (use --reel assets/video/edited/{WEEK}/{slug}*.mp4 if no captions yet)"
    )
    check(
        "Edit plan .json (drives render_week.py)",
        f"remotion/public/edit-plans/{WEEK}/*{date}*.json",
        f"python3 scripts/prepare_remotion_edit.py --slug {slug}\n"
        f"       (if overlay added later: patch_edit_plan_overlays.py --edit-plan <plan> --overlay <scene-plan>)"
    )
    # Source video must be a REAL file under remotion/public/videos — symlinks/placeholders
    # make Remotion 404 / 'moov atom not found' (this is what silently broke W22).
    src = sorted(glob.glob(f"remotion/public/videos/{WEEK}/*{date}*.mp4"))
    src_ok = bool(src) and not os.path.islink(src[0]) and os.path.getsize(src[0]) > 1_000_000
    print(f"  {'✅' if src_ok else '❌'}  Source video (real file, not symlink/stub) in remotion/public/videos/{WEEK}/")
    if not src_ok:
        print(f"       FIX: cp the edited .mp4 into remotion/public/videos/{WEEK}/ (copy, NOT symlink)")
        print()
    # Long-form render output: match by date, exclude shorts (_sNN / _short / _reel).
    longform = [f for f in glob.glob(f"output/animations/{WEEK}/*{date}*.mp4")
                if not re.search(r"(_s\d|_short|_reel)", os.path.basename(f))]
    print(f"  {'✅' if longform else '❌'}  Long-form .mp4 (Remotion CourseLesson output)")
    if not longform:
        print(f"       FIX: Step 17: python3 scripts/render_week.py --week {WEEK} --concurrency 1\n")
    check(
        "Short .mp4 (clip-based or motion)",
        f"assets/video/edited/shorts/{WEEK}/*{date}*_short_*.mp4",   # Path A; Path B → output/animations/*_sNN.mp4
        f"Step 17b: python3 scripts/create_vertical_reels.py (clip)  OR\n"
        f"          python3 scripts/render_shorts_batch.py --week {WEEK} --niche {niche.lower()} (motion → output/animations/{WEEK}/*_sNN.mp4)"
    )
    print()

print("──────────────────────────────────────────────────────")
print("Any ❌ above must be resolved before continuing.")
print("[YOU] items require manual work — no script can create them.")
print("All others: run the FIX command shown, then re-run this audit.")
EOF
```

---

**Step 2 — Angle check against the tracker** [SCRIPT → CLAUDE]

Why: Medium's curation algorithm penalises repeated angles. If you've covered the same angle in the last 90 days, the new piece needs to be reframed before publishing.

Source = shipped content slugs under `content/blogs/2026-W*/`, NOT the tracker. (The tracker drops `Content Title` when a week commits — committed weeks like W21 keep only untitled per-platform slots — so it can't supply recent angles. Blog slugs survive for every week: `.md` files for recent weeks, `_images/` dirs for older ones.)

First, run this to list every angle covered in the last 90 days:

```bash
python3 -c "
import glob, os
from datetime import datetime, timedelta

cutoff = datetime.today() - timedelta(days=90)
NICHE = {'data_science_tech':'DS','life_self_dev':'Life','poetry_quotes':'Poetry'}
seen = {'DS':[], 'Life':[], 'Poetry':[]}
for path in glob.glob('content/blogs/2026-W*/*'):
    name = os.path.basename(path)
    if name.endswith('_images'): slug = name[:-7]
    elif name.endswith('.md'):   slug = name[:-3]
    else: continue
    try: d = datetime.strptime(slug[:10], '%Y-%m-%d')
    except ValueError: continue
    if d < cutoff: continue
    rest = slug[11:]
    for k, lab in NICHE.items():
        if rest.startswith(k):
            topic = rest[len(k)+1:]
            if topic not in [t for _, t in seen[lab]]: seen[lab].append((slug[:10], topic))
            break
for lab in ['DS','Life','Poetry']:
    print(f'\n--- {lab} ---')
    for dt, topic in sorted(set(seen[lab])):
        print(f'  {dt}  {topic.replace(\"-\",\" \")}')
"
```

Then paste the output plus this prompt into Claude:

```
Above is every content angle (from shipped blog slugs) covered in the last 90 days, grouped by niche.
Now read these files:
- content/blogs/{week}/{ds_slug}.md
- content/blogs/{week}/{life_slug}.md
- content/blogs/{week}/{poetry_slug}.md

For each, extract the core angle (1-sentence summary of the claim or emotional territory).
Compare each angle against the 90-day list for that niche.
If there is overlap (same emotional territory, same mechanism, or same named observation),
flag it and suggest a reframe that approaches the topic from a different angle.
If no overlap, confirm it is clear to publish.
```

---

### Phase 1 — Virality audit

**Step 3 — Audit and rewrite all three blogs** [CLAUDE]

Why: Medium's read ratio (target ≥40%) is driven by the title, first paragraph, and whether skimmers are pulled in by subheadings. A weak title costs 60% of potential reads before anyone opens the article.

```
Read these three files:
- content/blogs/{week}/{ds_slug}.md
- content/blogs/{week}/{life_slug}.md
- content/blogs/{week}/{poetry_slug}.md

Also read docs/weekly-virality-framework.md Phase 1 for the rules.

For each blog, do all of the following and write changes directly to the file:

1. TITLE — Does it create tension AND signal who it's for?
   If not, propose a better one and update the frontmatter title field.

2. FIRST PARAGRAPH — Remove it mentally. Does the piece lose meaning?
   If it can be deleted without loss, it's throat-clearing — rewrite it.

3. QUOTABLE SENTENCE — The one line a reader would highlight or DM to a friend.
   Add [QUOTABLE] as a comment above it in the file.

4. SUBHEADINGS — Are they hooks or labels?
   "Lists: The Workhorse of Sequences" is a label. Rewrite any like this.
   (Skip for Poetry — minimal format has no subheadings.)

5. ENDING — Does it land with weight, or just tease the next piece?
   If it's only a teaser, add one weight-bearing sentence before it.

After editing all three files, print a summary table:
| Niche | Old title | New title | Quotable sentence |
```

---

### Phase 2 — Derivative copy

**Step 4 — ~~Twitter threads~~ DROPPED — skip** [N/A]

Twitter is dropped from the pipeline (dead in analytics). No threads, no polls, no staging.
Derivative copy for the live platforms (LinkedIn / Instagram / Threads) is produced by
`scripts/repurpose_blog.py` and Step 5 below. Go straight to Step 5.

---

**Step 5 — LinkedIn posts** [CLAUDE]

Why: LinkedIn distributes based on early comments in the first hour. The hook line must force a comment or reaction before the reader reaches the second line. Poetry skips LinkedIn — the niche doesn't translate to a professional context.

```
Read content/blogs/{week}/{ds_slug}.md and content/blogs/{week}/{life_slug}.md.
Also read data/kb/reels/06_mavgpt_caption_formula.md (DS) and data/kb/voice/life_formula.md (Life) for the virality angle.

Write a LinkedIn post for each and save to the paths below.

Rules for both:
- 200–400 words
- First 2 lines work as a standalone tweet (the hook must force a stop)
- No bullet points in the hook section — use them only in the body if needed
- Ends with a specific answerable question (not "what do you think?" —
  something like "What's the worst silent bug you've ever shipped?")
- 3–5 hashtags at the bottom, not inline

Virality angle:
- DS (mavgpt): hook states the OUTCOME/specific result, not the topic. The post carries a usable
  takeaway (a concrete rule or snippet a reader can apply now), not a teaser that only defers to the
  link. Honesty guardrail — claim only what you can show.
- Life (life_formula): hook = a contrarian DECLARATION, not a question; name the mechanism (WHY this
  keeps happening) as the spine; lead from the analytical-identity disarmer where it fits; no
  motivational crescendo in the body — the specific closing question carries the engagement.

Save DS post to:   content/derivatives/{week}/{ds_slug}/linkedin_post.md
Save Life post to: content/derivatives/{week}/{life_slug}/linkedin_post.md
```

**Publishing:** LinkedIn is **active** (employer cleared). Posts go out via the daemon —
`load_posts.py` → `data/scheduling.db` → `scheduler.py` → `post_linkedin.py`. The blog link is
posted as the **pinned first comment** (from `linkedin_first_comment.txt`), never in the body.

---

**Step 6 — Podcast intros + episode metadata** [CLAUDE]

Why: Podcast completion rate (target ≥65%) is decided in the first 60 seconds. The episode title determines whether a cold listener taps play. No intro music longer than 5 seconds before voice begins. DS has no podcast.

```
Read content/blogs/{week}/{life_slug}.md and content/blogs/{week}/{poetry_slug}.md.
Also read prompts/podcast_virality_prompt.md, and the niche formula:
data/kb/voice/life_formula.md (Life) / data/kb/voice/poetry_formula.md (Poetry).

For each, produce: episode title, backup title, description (5-line structure),
and a 90-second intro script (no preamble — hook is the first word spoken).

Episode title formula (the title decides whether a cold listener taps play):
- ✅ specific incident ("I Called My Parents When I Was Drowning. They Gave Me a Budget.")
- ✅ counter-intuitive observation ("The More I 'Worked on Myself', the More I Lost Myself")
- ✅ named emotional experience ("The Quiet Dread That Stays After the Deadline Passes")
- ❌ vague topic labels ("Mental Health", "About Anxiety") · ❌ episode numbers alone
- Life (life_formula): a declarative claim / specific incident; mechanism beneath it.
- Poetry (poetry_formula): name the exact feeling; concrete, not abstract; never "a poem about X".

Description structure:
Line 1–2: the hook (appears in Spotify previews — must land cold, no "In this episode")
Line 3: what the episode is about
Line 4: Full piece: medium.com/@tarun-gupta/{slug}
Line 5: Follow {show name} for new episodes every week.

90-sec intro: hook is the first word spoken; plant a reason-to-stay in the first 90s; vary pace.
Lead Life from the analytical-identity disarmer where it fits; close Poetry on permission, never explain.

Shows: Life → Breath of Life | Poetry → Breath of Poetry

Save Life podcast metadata to:   content/derivatives/{week}/{life_slug}/podcast_intro.md
Save Poetry podcast metadata to: content/derivatives/{week}/{poetry_slug}/podcast_intro.md
```

---

**Step 7 — YouTube descriptions** [CLAUDE]

Why: descriptions are indexed by YouTube search. Timestamps keep viewers on the video longer (boosts AVD). The Medium link in description drives blog read ratio by bringing in warm traffic.

```
Read the audited blog files for {week} and the virality-optimized titles from Step 3.
Also read the niche formula for the hook: data/kb/reels/06_mavgpt_caption_formula.md (DS) /
data/kb/voice/life_formula.md (Life) / data/kb/voice/poetry_formula.md (Poetry).

Write a YouTube video description for each niche.

The first 2–3 lines show before "Show more" and feed AVD — they must land cold (no "In this video").

DS description must include:
- 1-line hook (mavgpt: state the OUTCOME, not the topic — same as the video title hook)
- One concrete usable takeaway line (the rule/snippet a viewer can apply now) — not just a link tease
- Timestamps (0:00, key sections — estimate based on blog structure)
- 📄 Full write-up: medium.com/@tarun-gupta/{ds_slug slug without date prefix}
- 📊 Worksheet CTA — leave OUT; Step 10 (inject_worksheet_ctas.py) auto-appends the real URL via marker
- Series context (in description only, never the title/thumbnail): "Tutorial 2 of 10 — {tut 1 link} | Tutorial 3 coming {date}"
- 4 hashtags: #Python #DataScience #PythonTutorial #DataAnalysis

Life description must include:
- 1-line hook (life_formula: a contrarian declaration / the mechanism, not a topic label)
- Timestamps
- 📄 Full piece: medium.com/@tarun-gupta/{life_slug slug}
- 📊 Worksheet CTA — leave OUT; Step 10 auto-appends it (worksheets are DS + Life)
- 🎙️ Podcast version: Breath of Life on Spotify → [URL from podcast_intro.md]
- 3 hashtags: #MentalHealth #MensMentalHealth #SelfDevelopment

Poetry description must include:
- 2-line hook (poetry_formula: name the exact feeling, concrete; same as podcast intro opening; never explain the poem)
- 📄 Full poem: medium.com/@tarun-gupta/{poetry_slug slug}
- 🎙️ Podcast version: Breath of Poetry → [URL from podcast_intro.md]
- 3 hashtags: #SpokenWord #Poetry #Love

Save to:
content/derivatives/{week}/{ds_slug}/youtube_description.txt
content/derivatives/{week}/{life_slug}/youtube_description.txt
content/derivatives/{week}/{poetry_slug}/youtube_description.txt
```

---

### Phase 3 — Worksheets + Slides

**Step 8 — Generate worksheets** [SCRIPT]

Why: DS and Life readers expect a downloadable companion — it drives email signups and Medium read ratio by giving skimmers a reason to scroll to the end. Poetry never gets a worksheet (wrong niche). The worksheet URL must exist before you publish so it can be injected into the YouTube description and captions.

> **W22:** worksheets already exist (`output/worksheets/2026-W22/`) and are in `worksheets-manifest.json`. Skip to Step 9.

Three parts — the outline script does NOT produce the PDF; the design + manifest steps are required or Step 10's CTA injection silently does nothing.

**8a — Outline + Canva design prompt** `[SCRIPT]` (DS + Life; Poetry skipped):
```bash
python3 scripts/generate_worksheet_outline.py -i content/blogs/{week}/{ds_slug}.md
python3 scripts/generate_worksheet_outline.py -i content/blogs/{week}/{life_slug}.md
```
Writes `content/worksheets/{week}/{slug}_worksheet.json` (outline) + `content/prompts/{week}/{slug}_worksheet_prompt.txt` (Canva prompt). No PDF yet.

**8b — Design the PDF in Canva** `[YOU]`: paste each `{slug}_worksheet_prompt.txt` into Canva, export the PDF to `output/worksheets/{week}/{slug}.pdf` (the `_worksheet` suffix is optional — the manifest builder accepts either).

**8c — Build the manifest** `[SCRIPT]` (REQUIRED before Step 10 — `worksheet_exists()` reads this manifest, not the disk):
```bash
node scripts/build-worksheets-manifest.mjs
python3 scripts/worksheet_links.py --week {week}
```

Verify the slugs landed in the manifest:
```bash
python3 -c "import json; m=json.load(open('worksheets-manifest.json'))['worksheets']; print(len(m),'entries'); [print(' ',k) for k in m]"
```

---

**Step 9 — Generate slide decks** [SCRIPT]

Why: slide decks (DS + Life; **poetry deck dropped**) are repurposed as the LinkedIn document/PDF post and Instagram carousel. Running this now means the assets are ready when the daemon publishes in Phase 7.

The generator pulls the per-niche virality formula, so the **cover slide** follows the niche's hook rule (DS = outcome claim; Life = declarative text-wall claim; Poetry = the strongest line) — edit the `## Engine digest` of the niche's formula file to change it.

> **W22:** slides already exist at `assets/slides/2026-W22/`. Skip to Step 10.

```bash
# All 3 niches — generate_slide_deck.py processes the whole week at once
python3 scripts/generate_slide_deck.py --week {week}

# If only one niche needs regenerating:
python3 scripts/generate_slide_deck.py --slug {ds_slug}
python3 scripts/generate_slide_deck.py --slug {life_slug}
python3 scripts/generate_slide_deck.py --slug {poetry_slug}
```

Verify:
```bash
ls assets/slides/{week}/
```

Expected output: `{slug}_slides.html` and `{slug}_slides.pdf` for each niche. Poetry also gets `_social.html` and `_story.html`.

---

**Step 10 — Inject worksheet CTAs into descriptions** [SCRIPT]

Why: this **appends** the worksheet CTA (the gated `?slug=` URL) to every derivative — YouTube description, captions, IG, LinkedIn, etc. — for DS + Life (Poetry is skipped). It does NOT replace a placeholder; you left the worksheet line out in Step 7. It's manifest-gated (only injects when the slug is in `worksheets-manifest.json` from Step 8c) and idempotent (skips if the URL is already present, wrapped in a marker).

`--week-from` is a MINIMUM-week filter — it processes that week and every later one.

```bash
python3 scripts/inject_worksheet_ctas.py --week-from {week} --dry-run   # preview
python3 scripts/inject_worksheet_ctas.py --week-from {week}             # apply
```

Verify the CTA was appended:
```bash
grep "Free worksheet" content/derivatives/{week}/{ds_slug}/youtube_description.txt
grep "Free worksheet" content/derivatives/{week}/{life_slug}/youtube_description.txt
# Both should show a real /get-worksheet/<slug> URL
```

If nothing was injected: the slug isn't in `worksheets-manifest.json` — re-run Step 8c (`node scripts/build-worksheets-manifest.mjs`). The script gates on the manifest, NOT the PDF on disk.

---

### Phase 4 — Thumbnails

**Step 11 — Instagram reel briefs** [SCRIPT]

Why: generates the hook options, caption, and DM keyword for each reel. Input for Steps 16 and 21. The brief now carries the per-niche virality formula (DS = @mavgpt caption-is-product; Life/Poetry = voice formula) — injected automatically per niche.

> **W22 only:** briefs already exist — skip this step and go to Step 12.

```bash
python3 scripts/generate_ig_reel_brief.py --week {week}
# Build-in-public project (layers in pitch/DM keyword): add --project <key>
```

Verify output exists:
```bash
ls content/derivatives/{week}/{ds_slug}/ig_reel_brief.md
ls content/derivatives/{week}/{life_slug}/ig_reel_brief.md
ls content/derivatives/{week}/{poetry_slug}/ig_reel_brief.md
```

---

**Step 12 — Generate thumbnail prompts** [CLAUDE]

Why: thumbnails with a face + 3–5 word hook hit ≥5% CTR vs ~0.5% text-only. You generate the IMAGE in ChatGPT (better quality than the programmatic HTML/Canva paths) — this step produces the paste-ready prompt. (`generate_thumbnail.py` builds HTML/Remotion thumbnails, not a ChatGPT prompt — not used here.)

Paste into Claude:
```
Read content/blogs/{week}/{ds_slug}.md, content/blogs/{week}/{life_slug}.md, content/blogs/{week}/{poetry_slug}.md.
Read the per-niche thumbnail rule (the "## Engine digest" → thumbnail line):
- DS:     data/kb/reels/06_mavgpt_caption_formula.md   (thumbnail = state the OUTCOME, e.g. "[N] hidden X" / "[tool] just killed Y")
- Life:   data/kb/voice/life_formula.md                (thumbnail = a declarative text-wall claim, not a question)
- Poetry: data/kb/voice/poetry_formula.md              (thumbnail = the strongest single line of the poem)

For each niche:
1. Pick a 3–5 word hook that follows that niche's thumbnail rule — a result/claim/line, NOT a topic label, and NO series number ("Tutorial 2/10").
2. Build a paste-ready ChatGPT image-creator prompt using the canonical thumbnail template (in memory: detailed split-screen editorial composition, face-reference placeholder, color/mood, explicit negative prompts).
3. Output one fenced prompt block per niche, ready to paste into ChatGPT.
```

---

**Step 13 — Generate thumbnails in ChatGPT + export** [YOU]

For each niche:
1. Open ChatGPT → image creator
2. Paste the prompt from Step 12
3. Attach your face photo
4. Generate → pick best result
5. Download PNG → save to `assets/thumbnails/{week}/{slug}_thumbnail.png`

---

### Phase 5 — Reels

**Step 14 — Find actual reel start times from captions** [SCRIPT]

Why: do not hardcode `--start 0:00`. The edited video may have a title card or B-roll before the hook line. Print the opening captions per niche (timestamp + text) and pick the second the hook actually begins.

```bash
python3 -c "
import json, glob
WEEK = '{week}'
for niche, slug in [('DS','{ds_slug}'), ('Life','{life_slug}'), ('Poetry','{poetry_slug}')]:
    files = glob.glob(f'remotion/public/captions/{WEEK}/{slug}*.json')
    print(f'\n=== {niche} ===')
    if not files:
        print('  no captions — run generate_captions.py first'); continue
    caps = json.load(open(files[0]))
    for c in caps[:8]:                       # opening ~8 lines — the hook is in here
        print(f\"  {c['startMs']/1000:5.1f}s  {c['text'][:70]}\")
"
```

Caption schema: list of `{{text, startMs, endMs, …}}`. Read the lines, pick the one that IS the hook (per the niche's hook in `ig_reel_brief.md`), and use its `startMs` as `--start` in **Step 15**.

---

**Step 15 — Clip vertical reels** [SCRIPT]

Why: Run once per viral segment found in Step 14 caption analysis. Use each clip's natural speech endpoint — NOT a fixed 60s. Clips that end cleanly at 27s should be 27s. Only ask for user confirmation if the natural endpoint exceeds 60s. **Target 2 DISTINCT clips per niche (DS/Life)** — the 2 strongest ideas, not slices of one. Poetry uses the poem-only short, not this clipper. Add 1 virality reel + 1 comment→DM tool reel separately (≈9 reels/week total, not ~56).

```bash
# Pattern — run once per clip. --start accepts seconds (from Step 14, e.g. 6.5) OR MM:SS.
# Output to the shorts/{week}/ bucket with _short_NN naming so Step 1 audit + Step 17b find it.
python3 scripts/create_vertical_reels.py \
  --slug {slug} \
  --start {start_sec_or_MMSS} \
  --duration {natural_duration_seconds} \
  --output-dir assets/video/edited/shorts/{week} \
  --output-name {slug}_short_{nn}.mp4 \
  --smart-crop          # DS screen recordings only — finds the code editor region

# Target: 2 distinct clips per niche (DS/Life). Poetry = poem-only short (not this clipper).
```

Verify clips exist:
```bash
ls assets/video/edited/shorts/{week}/ | grep short
```

---

**Step 16 — Generate overlay scene plans** [SCRIPT]

Why: Claude reads the actual spoken audio (via captions) and produces a JSON that Remotion uses to bake 3 mandatory text overlays onto the clip — hook at 0:00, shareable moment mid-video, CTA at end. 40% of Reels are watched sound-off — overlays are non-optional.

Priority order for input: `--captions` (if .json exists from Step 1) → `--reel` (Whisper transcribes the video) → `--script` (legacy, avoid).

`--slug` is REQUIRED with `--captions`/`--reel` (only `--script` mode derives it). Overlay mode auto-injects the per-niche virality formula (the cover/hook follows DS outcome / Life claim / Poetry line).

```bash
# Check which captions files exist first:
ls remotion/public/captions/{week}/ 2>/dev/null || echo "no captions — use --reel instead"

# DS — captions if present, else --reel
python3 scripts/generate_scene_plans.py \
  --captions "$(ls remotion/public/captions/{week}/*{ds_slug}*.json 2>/dev/null | head -1)" \
  --slug {ds_slug} --niche ds --week {week} --mode overlay
# If NO captions:
python3 scripts/generate_scene_plans.py \
  --reel "$(ls assets/video/edited/{week}/{ds_slug}*.mp4 | head -1)" \
  --slug {ds_slug} --niche ds --week {week} --mode overlay

# Life
python3 scripts/generate_scene_plans.py \
  --captions "$(ls remotion/public/captions/{week}/*{life_slug}*.json 2>/dev/null | head -1)" \
  --slug {life_slug} --niche life --week {week} --mode overlay
# If NO captions:
python3 scripts/generate_scene_plans.py \
  --reel "$(ls assets/video/edited/{week}/{life_slug}*.mp4 | head -1)" \
  --slug {life_slug} --niche life --week {week} --mode overlay

# Poetry
python3 scripts/generate_scene_plans.py \
  --captions "$(ls remotion/public/captions/{week}/*{poetry_slug}*.json 2>/dev/null | head -1)" \
  --slug {poetry_slug} --niche poetry --week {week} --mode overlay
# If NO captions:
python3 scripts/generate_scene_plans.py \
  --reel "$(ls assets/video/edited/{week}/{poetry_slug}*.mp4 | head -1)" \
  --slug {poetry_slug} --niche poetry --week {week} --mode overlay
```

> **W22:** captions `.json` exist for all three niches — use the `--captions` variant for each.

Verify:
```bash
ls remotion/public/scene-plans/{week}/
```

---

**Step 17 — Render long-form (overlays baked in) — Remotion `CourseLesson`** [SCRIPT]

Why: this is the proven Week 24 path. `render_week.py` renders each edit plan through the `CourseLesson` composition (= `TalkingHeadEdit`), which composites **everything in one pass** — overlay scenes (from the edit plan's `scenePlanFile`), B-roll (`brollCues`), title card, lower third, outro, color grading. There is **no separate ffmpeg bake step** (the old `bake_overlays.py` / `VerticalReel` flow is retired).

Prerequisites:
- Edit plan exists at `remotion/public/edit-plans/{week}/{slug}.json` (built by `prepare_remotion_edit.py`). If the overlay scene plan was generated *after* the edit plan, wire it in: `python3 scripts/patch_edit_plan_overlays.py --edit-plan <plan> --overlay <scene-plan>` (injects `scenePlanFile`, aligns `atSec`).
- Source video is a **real file** (not a symlink — Remotion bundles `public/` to a temp dir) at `remotion/public/videos/{week}/{slug}.mp4`.
- `brollCues[].clipFile` paths resolve under `remotion/public/` (week-bucketed: `broll/{week}/{slug}/cue-N.mp4`); prune any cue whose file is missing/corrupt.

```bash
python3 scripts/render_week.py --week {week} --concurrency 1
# Single niche (edit-plan niche field is short: ds | life | poetry):
#   python3 scripts/render_week.py --week {week} --niche ds
```

Output (PRIMARY long-form, used in Step 19): `output/animations/{week}/{slug}.mp4`

Verify:
```bash
ls -la output/animations/{week}/*.mp4 | grep -v "_s[0-9]"
```

---

**Step 17b — Render shorts (pick ONE path per piece)** [SCRIPT]

Two legitimate short formats — choose by content, they can coexist:

**Path A — clip-based vertical reels** (talking-head segments cut from the long-form). Use when the spoken delivery is the value. Produced in Step 15 via `create_vertical_reels.py`:
- Output: `assets/video/edited/shorts/{week}/{slug}_short_NN.mp4`

**Path B — Remotion motion shorts** (pure motion-graphic shorts from per-slot scene plans; the Week 24 default). Requires a `shorts_manifest.json` per slug listing `clip`/`motion` slots:
```bash
python3 scripts/render_shorts_batch.py --week {week} --niche ds --dry-run   # then life, poetry
python3 scripts/render_shorts_batch.py --week {week} --niche ds             # real
```
- Reads: `content/derivatives/{week}/{slug}/shorts_manifest.json`
- Output: `output/animations/{week}/{slug}_s{NN}.mp4`

Overlay text (hook / key line / CTA) is burned in by the composition in both paths — no separate overlay-bake step. Upload either output in Step 20.

Verify:
```bash
ls assets/video/edited/shorts/{week}/ 2>/dev/null   # Path A
ls output/animations/{week}/*_s*.mp4 2>/dev/null    # Path B
```

---

### Phase 6 — Publish

**Step 18 — Publish all three blogs to Medium** [SCRIPT + YOU]

Why: Medium is the canonical first-publish destination. No Substack. No canonical URL flag needed (Medium is the original).

Two manual touchpoints per blog — this is NOT a fire-and-forget script:
- **Status = `draft`** (default). The script creates a Medium *draft*; you review and hit Publish in the Medium UI. Pass `--status public` only if you want it live immediately.
- **Tags = interactive.** Blogs carry no `tags` front-matter, so the script auto-selects 5 tags via Claude Haiku and prompts `Confirm tags? [Y/n/edit]`. Answer at the prompt (or pre-empt with `--tags "a,b,c"`).

```bash
python3 scripts/publish_medium.py \
  --input content/blogs/{week}/{ds_slug}.md

python3 scripts/publish_medium.py \
  --input content/blogs/{week}/{life_slug}.md

python3 scripts/publish_medium.py \
  --input content/blogs/{week}/{poetry_slug}.md
```

Each run prints the draft URL and appends a record (title · url · id · tags) to `output/published/medium_posts.json` — pull the URLs from there for Step 24 (tracker update).

> ⚠️ Pre-publish content check: confirm each blog's first line is the `# H1` title (no stray generation preamble before the front-matter / H1). The W22 DS draft once carried a leftover "The file that's there is Tutorial 1…" line above the H1 — that would become the Medium title. Fix the `.md` before publishing.

---

**Step 19 — Upload long-form videos to YouTube** [SCRIPT]

Why: `--thumbnail` uploads the Canva PNG immediately after the video completes. `--publish-at` schedules the video as private and YouTube auto-publishes at the set time (so `--privacy` is ignored — no need to pass it). `--slug` drives two automatic hand-offs:
- **GitHub code comment** — for DS, if `content/derivatives/{week}/{slug}/github_code_url.txt` exists, its URL is auto-posted as a comment (pin manually in Studio — the script prints the link).
- **`long_form_url` save** — the uploaded video URL is written back into that slug's `youtube_shorts_metadata.json` as `long_form_url`. **Step 20's `--pin-longform-comment` reads it**, so run Step 19 (long-form) before Step 20 (Shorts).

```bash
# DS — breathofdatascience, Category 28 (Science & Technology)
python3 scripts/upload_youtube.py \
  --channel "breathofdatascience" \
  --video output/animations/{week}/{ds_slug}.mp4 \
  --title "Python Gave Me a Wrong Answer With No Error (Here's Why)" \
  --description "$(cat content/derivatives/{week}/{ds_slug}/youtube_description.txt)" \
  --tags "Python,Data Science,Python Tutorial,Python for beginners,data types Python,Python lists,Python dictionaries,Python functions,data science tutorial,learn Python" \
  --category 28 \
  --thumbnail assets/thumbnails/{week}/{ds_slug}_thumbnail.png \
  --slug {ds_slug} \
  --publish-at "{ds_publish_date}T08:00:00+05:30"

# Life — breathoflife_, Category 22 (People & Blogs)
python3 scripts/upload_youtube.py \
  --channel "breathoflife_" \
  --video output/animations/{week}/{life_slug}.mp4 \
  --title "I White-Knuckled Life for 3 Years. Here's What I Was Actually Running From." \
  --description "$(cat content/derivatives/{week}/{life_slug}/youtube_description.txt)" \
  --tags "Mental Health,Men's Mental Health,Self Development,Stigma,Vulnerability,therapy,strength,self improvement" \
  --category 22 \
  --thumbnail assets/thumbnails/{week}/{life_slug}_thumbnail.png \
  --slug {life_slug} \
  --publish-at "{life_publish_date}T08:00:00+05:30"

# Poetry — breathofpoetry, Category 22 (People & Blogs)
python3 scripts/upload_youtube.py \
  --channel "breathofpoetry" \
  --video output/animations/{week}/{poetry_slug}.mp4 \
  --title "The Hangover That Won't Lift | Intoxicated Senses (spoken word)" \
  --description "$(cat content/derivatives/{week}/{poetry_slug}/youtube_description.txt)" \
  --tags "Spoken word,Poetry,Love poem,Spoken word poetry,Poem reading,Poetry reading,Intoxicated senses,Breath of Poetry,love and loss,emotional poetry" \
  --category 22 \
  --thumbnail assets/thumbnails/{week}/{poetry_slug}_thumbnail.png \
  --slug {poetry_slug} \
  --publish-at "{poetry_publish_date}T20:00:00+05:30"
```

---

**Step 20 — Upload Shorts to YouTube** [SCRIPT]

Why: `--shorts` injects `#Shorts` into the description and triggers auto-loading of title/tags from `youtube_shorts_metadata.json`. `--pin-longform-comment` posts the long-form URL as a comment — **run Step 19 (long-form upload) first** so `long_form_url` is already saved into the metadata; if it's still empty the comment is skipped.

`--video` points at the short you rendered in Step 17b — use the path for whichever format you produced. The slot index for metadata lookup is parsed from the filename's trailing `_short_NN` / `_sNN`, so the metadata array entry matches the slot you upload:
- **Path A (clip-based):** `assets/video/edited/shorts/{week}/{slug}_short_NN.mp4`
- **Path B (Remotion motion):** `output/animations/{week}/{slug}_s{NN}.mp4`

To schedule all of a slug's shorts in one run instead of per-file, use the batch uploader (see `docs/weekly-operating-guide.md` → YouTube Shorts):
```bash
python3 scripts/upload_youtube_shorts_batch.py --slug {slug} --publish-week {week} [--dry-run] [--pin-comment]
```

Per-file (single short):
```bash
# DS Short — replace _short_00 with the slot you're posting (or output/animations/{week}/{ds_slug}_s00.mp4 for Path B)
python3 scripts/upload_youtube.py \
  --channel "breathofdatascience" \
  --video assets/video/edited/shorts/{week}/{ds_slug}_short_00.mp4 \
  --slug {ds_slug} \
  --shorts \
  --pin-longform-comment \
  --publish-at "{ds_publish_date}T08:00:00+05:30"

# Life Short
python3 scripts/upload_youtube.py \
  --channel "breathoflife_" \
  --video assets/video/edited/shorts/{week}/{life_slug}_short_00.mp4 \
  --slug {life_slug} \
  --shorts \
  --pin-longform-comment \
  --publish-at "{life_publish_date}T19:00:00+05:30"

# Poetry Short
python3 scripts/upload_youtube.py \
  --channel "breathofpoetry" \
  --video assets/video/edited/shorts/{week}/{poetry_slug}_short_00.mp4 \
  --slug {poetry_slug} \
  --shorts \
  --pin-longform-comment \
  --publish-at "{poetry_publish_date}T20:00:00+05:30"
```

---

**Step 21 — Post Reels to Instagram** [YOU]

For each of the 3 reels:
1. Instagram → + → Reel
2. Select the short you rendered in Step 17b: clip-based `assets/video/edited/shorts/{week}/{slug}_short_NN.mp4` or motion `output/animations/{week}/{slug}_s{NN}.mp4`
3. Add trending audio in the Instagram app (Audio button, 10–20% volume under voice)
4. Paste caption from `content/derivatives/{week}/{slug}/ig_reel_brief.md`
5. Cover image: pick the frame where the hook text overlay is visible
6. Post (do not pre-schedule Reels — post in the engagement window and reply to every comment in the first 2 hours)

| Reel | Account | Day | Time IST |
|------|---------|-----|---------|
| DS | @breathofdatascience | Wednesday | 8:00 AM |
| Life | @mistakenlyhuman | Tuesday | 7:00 PM |
| Poetry | @mistakenlyhuman | Thursday | 8:00 PM |

---

### Phase 7 — Schedule

**Step 22 — Stage derivatives → auto-publish daemon (LinkedIn · Threads · Instagram-static)** [SCRIPT]

Why: distribution is now an **auto-publish daemon**, not manual in-app posting (canonical model:
`docs/pipeline-2026.md`). One stage step queues the week; `scheduler.py` fires each row in its
engagement window. **LinkedIn is active** (employer cleared); **Threads** posts text natively;
**Instagram-static** stages only when a public media URL exists. **Twitter is dropped** — no Step 23.

```bash
# Stage the week into scheduling.db (LinkedIn + Threads now; IG-static when a media_url is present)
python3 scripts/load_posts.py --week {week}

# Start the daemon (LinkedIn + Threads fire immediately; IG needs Meta tokens — see
# docs/one-time-platform-setup.md). It logs a credential check at startup.
nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &
```

| Platform | Source | Niches | How it posts |
|----------|--------|--------|--------------|
| LinkedIn | `linkedin_post.txt` (+ `linkedin_first_comment.txt`) | DS, Life | Daemon posts the body, then the **pinned first comment** (blog link). Poetry skips LinkedIn. |
| Threads | `threads_post.txt` | all 3 | Daemon posts native text. |
| Instagram (static) | `instagram_caption.txt` | all 3 | Daemon posts **only if** a public `social.ig_media_url(s)` is in `schedule.json` (else skipped with a warning). |

> **Instagram Reels stay MANUAL for now (Step 21)** — reel auto-publish is scaffolded but not
> wired (no public video hosting yet). See the "live vs scaffolded" section in `docs/pipeline-2026.md`.

> Per-niche identities: DS → @breathofdatascience; Life + Poetry → @mistakenlyhuman. Reply to
> comments/DMs in the first 2 hours — that part is yours.

---

### Phase 8 — Close the loop

**Step 24 — Update tracker to Published** [SCRIPT]

Why: marks this week's slugs `Idea → Published` in the tracker — a human status ledger for reporting/visibility. (It is **not** what powers the 90-day angle-check; Step 2 dedups off `content/blogs/` slugs, not tracker Status, so dedup stays correct even if you skip this.) Note "Published" here is coarse: posting is manual (Step 22) and Medium may still be a draft (Step 18) — treat it as "produced + queued," not "live everywhere."

```bash
python3 -c "
from openpyxl import load_workbook

slugs = [
    '{ds_slug}',
    '{life_slug}',
    '{poetry_slug}',
]

file = 'output/trackers/annual-tracker-2026.xlsx'
wb = load_workbook(file)

updated = 0
for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    headers = [c.value for c in ws[1]]
    slug_col = headers.index('Slug') + 1
    status_col = headers.index('Status') + 1
    for row in ws.iter_rows(min_row=2):
        cell_val = row[slug_col-1].value
        if cell_val and any(s in str(cell_val) for s in slugs):
            row[status_col-1].value = 'Published'
            updated += 1

wb.save(file)
print(f'Updated {updated} rows to Published in {file}')
"
```

---

## Track B — New content (W25 and onwards)

*Nothing written yet. Follow in order:*

| Step | What | Daily doc |
|------|------|-----------|
| 1 | Write all three blogs | `docs/daily/monday.md` |
| 2 | Generate scripts, annotate `[TEXT_OVERLAY]` tags | `docs/daily/tuesday.md` |
| 3 onwards | Same as Track A Phase 0 → Phase 7 | Above |

---

## Troubleshooting index

| Problem | Where to look |
|---------|--------------|
| Captions mis-timed | `docs/daily/wednesday-poetry.md` → Troubleshooting |
| Remotion won't render | `docs/daily/thursday.md` → Troubleshooting |
| YouTube upload auth error | `scripts/upload_youtube.py --register` |
| Static post won't go out | Step 22: `load_posts.py --week` then start `scheduler.py`; check the daemon's startup credential log |
| IG didn't auto-post | IG-static needs a public `social.ig_media_url` in schedule.json; IG **reels are manual** (Step 21) until hosting lands |
| Medium publish script error | `docs/daily/wednesday-ds.md` → Troubleshooting |
