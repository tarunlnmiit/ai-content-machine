# Saturday — Edit Life + Poetry + Reels + Upload + Publish (~2 hrs)

## Saturday at a glance

| Time | Action | Output goes live |
|------|--------|------------------|
| 10:00 AM | Edit Life + Poetry videos (Friday recordings) | — |
| 12:00 PM | Render Life + Poetry shorts + HyperFrames | — |
| 2:00 PM | Upload Life + Poetry long-form to YouTube (scheduled for next Tue/Fri) | Videos queued (publish **next Tue 2 PM** / **next Fri 3 PM**) |
| 3:00 PM | Upload all shorts for Mon–Sun (14 slots × 3 niches) | Shorts queued for **next week** (Mon–Sun) |
| 4:00 PM | Weekly review + Notion sync | — |
| 5:00 PM | Buffer depth check + replenish if needed | — |

---

---

## Step 1 — Prepare edit metadata: Life (~5 min)

Reference: `docs/video-production-guide.md`

Record raw front-cam → `assets/raw/[life_slug].MOV`, then:

```bash
python3 scripts/prepare_remotion_edit.py \
  --raw assets/raw/[life_slug].MOV \
  --script content/scripts/YYYY-MM-DD-life-self-dev-[life_slug]_yt.md \
  --niche life \
  --slug life_[slug]
```

Outputs:
- `remotion/public/edit-plans/[slug].json` — silence trim boundaries + clap cut segments + b-roll cue timings
- `remotion/public/captions/[slug].json` — word-level timestamps for manual caption burning
- `assets/videos/[slug]/` — downloaded stock b-roll clips

### Step 1b — Render animation overlays: Life

```bash
python3 scripts/generate_animation_prompts.py \
  content/scripts/YYYY-MM-DD-life-self-dev-[life_slug]_yt.md \
  --render
```

Output: `output/animations/[life_slug]_{n}_{type}.mp4` — title card + lower thirds + outro card. Layer as overlay tracks in DaVinci during manual edit.

Then manually edit in DaVinci (see video-production-guide.md Step 3 for full checklist). Export final to `assets/video/edited/[slug].mp4`.

### HyperFrames augmentation (mandatory)

Apply Claude-powered visual overlay (glass cards, flow arrows, charts, etc.) to the edited MP4:

```bash
python3 scripts/hyperframes_render.py assets/video/edited/[life_slug].mp4 \
  --slug life-[slug]-aug
# → assets/hyperframes/<date>_life-[slug]-aug.mp4
```

Or inspect before rendering:
```bash
python3 scripts/hyperframes_render.py assets/video/edited/[life_slug].mp4 --no-render
# edit /tmp/hf_*/index.html if needed
cd /tmp/hf_*/ && npm run render
```

Reference: `docs/video-production-guide.md` → HyperFrames section.

---

## Step 2 — Prepare edit metadata: Poetry (~5 min)

```bash
python3 scripts/prepare_remotion_edit.py \
  --raw assets/raw/[poetry_slug].MOV \
  --script content/scripts/YYYY-MM-DD-poetry-quotes-[poetry_slug]_yt.md \
  --niche poetry \
  --slug poetry_[slug]
```

Same output structure as Step 1. Poetry-specific: heavier b-roll (abstract/nature). `[PAUSE]` markers preserved — silence detector keeps intentional pauses intact.

### Step 2b — Render animation overlays: Poetry

```bash
python3 scripts/generate_animation_prompts.py \
  content/scripts/YYYY-MM-DD-poetry-quotes-[poetry_slug]_yt.md \
  --render
```

Output: `output/animations/[poetry_slug]_{n}_{type}.mp4` — title card (poem title) + lower thirds (key stanza lines) + outro card. Layer as overlay tracks in DaVinci during manual edit.

Then manually edit in DaVinci. Export final to `assets/video/edited/[slug].mp4`.

### HyperFrames augmentation (mandatory)

```bash
python3 scripts/hyperframes_render.py assets/video/edited/[poetry_slug].mp4 \
  --slug poetry-[slug]-aug
# → assets/hyperframes/<date>_poetry-[slug]-aug.mp4
```

---

## Step 3 — Manual edit + HyperFrames: DS (~10 min)

If editing a DS video (talking-head + screen-record composite):

```bash
python3 scripts/prepare_remotion_edit.py \
  --raw assets/raw/[ds_slug].MOV \
  --script content/scripts/YYYY-MM-DD-data-science-tech-[ds_slug]_yt.md \
  --niche ds \
  --slug ds_[slug]
```

Then manually edit in DaVinci (composite talking-head + screen-record, reference prepare script outputs). Export to `assets/video/edited/[slug].mp4`.

### HyperFrames augmentation (mandatory)

```bash
python3 scripts/hyperframes_render.py assets/video/edited/[ds_slug].mp4 \
  --slug ds-[slug]-aug
# → assets/hyperframes/<date>_ds-[slug]-aug.mp4
```

Claude picks: code-snippet, bar-chart, stat-card, flowchart, comparison-table elements per transcript.

---

## Step 5 — Auto-generate DS shorts (~3 min)

Slug format: `YYYY-MM-DD_data_science_tech_[slug]` (matches filename in `assets/video/edited/`)

Generate fresh metadata from edited video:
```bash
python3 scripts/make_shorts_meta.py \
  --slug 2026-05-21_data_science_tech_[ds_slug] \
  --video assets/video/edited/2026-05-21_data_science_tech_[ds_slug].mp4
# Optional: --whisper-model small for better accuracy
```

Then clip:
```bash
python3 scripts/clip_shorts.py --slug 2026-05-21_data_science_tech_[ds_slug] --count 4
# → assets/video/edited/shorts/2026-05-21_data_science_tech_[ds_slug]_short_NN.mp4
# Manifest: assets/video/edited/shorts/2026-05-21_data_science_tech_[ds_slug]_shorts_manifest.json
```

### HyperFrames on DS shorts (mandatory)

```bash
python3 scripts/hyperframes_render.py --shorts --slug 2026-05-21_data_science_tech_[ds_slug]
```

---

## Step 6 — Auto-generate Life shorts (~3 min)

Slug format: `YYYY-MM-DD_life_self_dev_[slug]`

Generate fresh metadata from edited video:
```bash
python3 scripts/make_shorts_meta.py \
  --slug 2026-05-21_life_self_dev_[life_slug] \
  --video assets/video/edited/2026-05-21_life_self_dev_[life_slug].mp4
# Optional: --whisper-model small for better accuracy
```

Then clip:
```bash
python3 scripts/clip_shorts.py --slug 2026-05-21_life_self_dev_[life_slug] --count 4
# → assets/video/edited/shorts/2026-05-21_life_self_dev_[life_slug]_short_NN.mp4
# Manifest: assets/video/edited/shorts/2026-05-21_life_self_dev_[life_slug]_shorts_manifest.json
```

### HyperFrames on Life shorts (mandatory)

```bash
python3 scripts/hyperframes_render.py --shorts --slug 2026-05-21_life_self_dev_[life_slug]
```

Claude CLI picks best 30-60s hook segments from transcript. Cuts + crops 9:16 + burns vertical captions.

---

## Step 7 — Auto-generate Poetry shorts (~3 min)

Slug format: `YYYY-MM-DD_poetry_quotes_[slug]`

Generate fresh metadata from edited video:
```bash
python3 scripts/make_shorts_meta.py \
  --slug 2026-05-21_poetry_quotes_[poetry_slug] \
  --video assets/video/edited/2026-05-21_poetry_quotes_[poetry_slug].mp4
```

Then clip:
```bash
python3 scripts/clip_shorts.py --slug 2026-05-21_poetry_quotes_[poetry_slug] --count 4
```

### HyperFrames on Poetry shorts (mandatory)

```bash
python3 scripts/hyperframes_render.py --shorts --slug 2026-05-21_poetry_quotes_[poetry_slug]
```

Verify outputs:
```bash
ls -la assets/video/edited/
# 3 × .mp4 (long-form: DS + Life + Poetry)
ls -la assets/video/edited/shorts/
# 8-12 × _short_NN.mp4 (4 per niche × 3 niches if all run)
```

---

## Step 8 — Upload Life + Poetry to YouTube (~15 min)

Long-form:
```bash
python3 scripts/upload_youtube.py \
  --video assets/video/edited/[life_slug].mp4 \
  --slug [life_slug]

python3 scripts/upload_youtube.py \
  --video assets/video/edited/[poetry_slug].mp4 \
  --slug [poetry_slug]
```

Shorts (upload each from `shorts/` manifest, or loop):
```bash
for f in assets/video/edited/shorts/[life_slug]_short_*.mp4; do
  python3 scripts/upload_youtube.py --shorts --slug [life_slug] \
    --channel "Breath of Life" --video "$f"
done

for f in assets/video/edited/shorts/[poetry_slug]_short_*.mp4; do
  python3 scripts/upload_youtube.py --shorts --slug [poetry_slug] \
    --channel "Breath of Poetry" --video "$f"
done
```

Manifest JSON has `hook_line` per short → use for caption/title.

Or use the pre-built script for all shorts at once:
```bash
bash output/scheduled/upload_shorts.sh
```

---

## Step 9 — Publish to Medium (~15 min)

```bash
# Publish to personal profile (default)
python3 scripts/publish_medium.py \
  --input content/blogs/[monday_ds_blog].md \
  --canonical-url https://breathofdatascience.substack.com/

python3 scripts/publish_medium.py \
  --input content/blogs/[tuesday_life_blog].md \
  --canonical-url https://thisisbreathoflife.substack.com/

python3 scripts/publish_medium.py \
  --input content/blogs/[wednesday_poetry_blog].md \
  --canonical-url https://breathofpoetry.substack.com/

# Publish to a publication instead (add --publication flag)
python3 scripts/publish_medium.py \
  --input content/blogs/[monday_ds_blog].md \
  --canonical-url https://breathofdatascience.substack.com/ \
  --publication humans-are-stories
```

---

## Step 10 — Load posts into scheduler

```bash
python3 scripts/load_posts.py
# Inserts all derivative content into data/scheduling.db
# Generates Metricool CSVs (Instagram + Facebook + Threads) with blog URLs + images
```

What `load_posts.py` does:
- **LinkedIn posts** → inserted into `data/scheduling.db` (scheduler.py will fire Tue/Thu)
- **Metricool CSVs** → `output/scheduled/metricool_*.csv` for each brand
  - Instagram + Facebook captions include Medium blog link: "Full post 👉 {url}"
  - Image URLs auto-injected if available in `schedule.json`, otherwise skipped (add manually in Metricool)
  - If running interactively, prompts for missing blog URLs + image URLs, saves to `schedule.json` for re-runs

**Interactive mode** (if using CLI with TTY):
- Prompts for blog URLs per niche (Medium only — no Substack)
- Prompts for image URLs (expects public Google Drive/Dropbox links)
- Non-interactive runs skip prompts (useful for automation)

Verify scheduler running:
```bash
ps aux | grep scheduler.py | grep -v grep
# If not running:
nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &
```

Check queue:
```bash
sqlite3 data/scheduling.db \
  'SELECT platform, scheduled_at, status, substr(content_text,1,60) FROM posts ORDER BY scheduled_at LIMIT 15'
```

Import Metricool CSVs:
```bash
# Live in Metricool → Bulk Import
# File: output/scheduled/metricool_breathofds.csv (DS niche)
#       output/scheduled/metricool_mistakenlyhuman.csv (Life + Poetry)
```
