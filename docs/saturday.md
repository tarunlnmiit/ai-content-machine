# Saturday — Edit Life + Poetry + Reels + Upload + Publish (~2 hrs)

---

## Step 1 — Prepare Remotion edit: Life (~8 min)

Reference: `docs/video-production-guide.md`

Record raw front-cam → `assets/raw/[life_slug].MOV`, then:

```bash
python3 scripts/prepare_remotion_edit.py \
  --raw assets/raw/[life_slug].MOV \
  --script content/scripts/YYYY-MM-DD-life-self-dev-[life_slug]_yt.md \
  --niche life \
  --slug life_[slug]
```

Pipeline: Whisper transcribe → adaptive silence detect → fetch stock b-roll (Pexels/Pixabay) → write `remotion/public/edit-plans/[slug].json` + `remotion/public/captions/[slug].json`.

Then preview + render:
```bash
cd remotion && npx remotion studio
# Select LifeHabits composition → scrub through, check captions + broll timing

npx remotion render LifeHabits --output ../assets/video/edited/[slug].mp4
```

Output: `assets/video/edited/[slug].mp4` with animated word-by-word captions + stock b-roll overlay.

---

## Step 2 — Prepare Remotion edit: Poetry (~8 min)

```bash
python3 scripts/prepare_remotion_edit.py \
  --raw assets/raw/[poetry_slug].MOV \
  --script content/scripts/YYYY-MM-DD-poetry-quotes-[poetry_slug]_yt.md \
  --niche poetry \
  --slug poetry_[slug]

cd remotion
npx remotion render PoetryLove --output ../assets/video/edited/[slug].mp4
```

Poetry-specific: heavier b-roll (abstract/nature). `[PAUSE]` markers preserved — silence detector keeps intentional pauses.

---

## Step 3 — Auto-generate DS shorts (~3 min)

Slug format: `YYYY-MM-DD_data_science_tech_[slug]` (matches filename in `assets/video/edited/`)

If you hand-edited the rendered video after Remotion, run this first to re-transcribe and generate fresh metadata:
```bash
python3 scripts/make_shorts_meta.py \
  --slug 2026-05-21_data_science_tech_[ds_slug] \
  --video assets/video/edited/2026-05-21_data_science_tech_[ds_slug].mp4
# Optional: --whisper-model small for better accuracy
```

```bash
python3 scripts/clip_shorts.py --slug 2026-05-21_data_science_tech_[ds_slug] --count 4
# → assets/video/edited/shorts/2026-05-21_data_science_tech_[ds_slug]_short_NN.mp4
# Manifest: assets/video/edited/shorts/2026-05-21_data_science_tech_[ds_slug]_shorts_manifest.json
```

---

## Step 4 — Auto-generate Life shorts (~3 min)

Slug format: `YYYY-MM-DD_life_self_dev_[slug]`

If you hand-edited the rendered video after Remotion, run this first to re-transcribe and generate fresh metadata:
```bash
python3 scripts/make_shorts_meta.py \
  --slug 2026-05-21_life_self_dev_[life_slug] \
  --video assets/video/edited/2026-05-21_life_self_dev_[life_slug].mp4
# Optional: --whisper-model small for better accuracy
```

```bash
python3 scripts/clip_shorts.py --slug 2026-05-21_life_self_dev_[life_slug] --count 4
# → assets/video/edited/shorts/2026-05-21_life_self_dev_[life_slug]_short_NN.mp4
# Manifest: assets/video/edited/shorts/2026-05-21_life_self_dev_[life_slug]_shorts_manifest.json
```

Claude CLI picks best 30-60s hook segments from transcript. Cuts + crops 9:16 + burns vertical captions.

---

## Step 5 — Auto-generate Poetry shorts (~3 min)

Slug format: `YYYY-MM-DD_poetry_quotes_[slug]`

If hand-edited after Remotion:
```bash
python3 scripts/make_shorts_meta.py \
  --slug 2026-05-21_poetry_quotes_[poetry_slug] \
  --video assets/video/edited/2026-05-21_poetry_quotes_[poetry_slug].mp4
```

```bash
python3 scripts/clip_shorts.py --slug 2026-05-21_poetry_quotes_[poetry_slug] --count 4
```

Verify outputs:
```bash
ls -la assets/video/edited/
# 3 × .mp4 (long-form: DS + Life + Poetry)
ls -la assets/video/edited/shorts/
# 8-12 × _short_NN.mp4 (4 per niche × 3 niches if all run)
```

Legacy reel script (`find_best_reel_moment.py` + `create_vertical_reels.py`) still works for single-clip workflow.

---

## Step 6 — Upload Life + Poetry to YouTube (~15 min)

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

## Step 7 — Publish to Medium (~15 min)

```bash
python3 scripts/publish_medium.py \
  --input content/blogs/[monday_ds_blog].md \
  --canonical-url https://breathofdatascience.substack.com/

python3 scripts/publish_medium.py \
  --input content/blogs/[tuesday_life_blog].md \
  --canonical-url https://thisisbreathoflife.substack.com/

python3 scripts/publish_medium.py \
  --input content/blogs/[wednesday_poetry_blog].md \
  --canonical-url https://breathofpoetry.substack.com/
```

---

## Step 8 — Load posts into scheduler

```bash
python3 scripts/load_posts.py
# Inserts all derivative content into data/scheduling.db
```

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
