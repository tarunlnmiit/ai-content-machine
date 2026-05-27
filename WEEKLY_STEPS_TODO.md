# Weekly Steps TODO — 2026-05-25 (Sunday catchup)
All content from 2026-05-21 week. Do in order.

---

## MONDAY LEFTOVERS

### [x] Fill PERSONAL_INSERT — DS blog ✅ done
### [x] Fill PERSONAL_INSERT — Life blog ✅ done

### [x] Add images — DS blog ✅ done
```bash
python3 scripts/fetch_images.py --input "content/blogs/2026-05-21_data_science_tech_complete-python-course-2026-beginner-to-advance-tutorial-110.md" --dry-run
python3 scripts/fetch_images.py --input "content/blogs/2026-05-21_data_science_tech_complete-python-course-2026-beginner-to-advance-tutorial-110.md"
```

---

## TUESDAY LEFTOVERS

### [x] Add images — Life blog ✅ done
```bash
python3 scripts/fetch_images.py --input "content/blogs/2026-05-21_life_self_dev_how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals.md" --dry-run
python3 scripts/fetch_images.py --input "content/blogs/2026-05-21_life_self_dev_how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals.md"
```

### [ ] DS Production guide (missing — Life + Poetry have it)
```bash
python3 scripts/ghostwrite.py \
  --source "content/scripts/2026-05-22_2026-05-21-data-science-tech-complete-python-course-2026-beg_yt.md" \
  --niche ds --format production-guide
# → content/scripts/..._PRODUCTION_GUIDE.md
```

### [ ] DS thumbnail brief (verify exists — then done)
```bash
cat "content/derivatives/2026-05-21-data-science-tech-complete-python-course-2026-beg/thumbnail_brief.json"
```

### [x] Generate thumbnail images — all 3 niches ✅ done
```bash
conda run -n content_engine_env python3 scripts/generate_thumbnail.py \
  --blog "content/blogs/2026-05-21_data_science_tech_complete-python-course-2026-beginner-to-advance-tutorial-110.md" --export
# → assets/thumbnails/2026-05-21_data_science_tech_*_thumbnail.png

conda run -n content_engine_env python3 scripts/generate_thumbnail.py \
  --blog "content/blogs/2026-05-21_life_self_dev_how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals.md" --export
# → assets/thumbnails/2026-05-21_life_self_dev_*_thumbnail.png

conda run -n content_engine_env python3 scripts/generate_thumbnail.py \
  --blog "content/blogs/2026-05-21_poetry_quotes_when-dreams-speak-of-love.md" --export
# → assets/thumbnails/2026-05-21_poetry_quotes_*_thumbnail.png
```
Open each `.html` first to verify design. Use `--force` to regenerate.

---

## WEDNESDAY LEFTOVERS

### [x] Life story sequence — DONE (8 images, renamed from wrong poetry slug)
`assets/stories/2026-05-21_life_self_dev_how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals_images_1-8.png`

### [x] DS story sequence ✅ done (7 slides + MP4 exported)

### [x] Carousels ✅ done (7 slides each, all 3 niches)
Export PNGs default-on. Add `--no-export` to skip, `--force` to overwrite.
```bash
conda run -n content_engine_env python3 scripts/generate_carousel.py \
  --blog "content/blogs/2026-05-21_data_science_tech_complete-python-course-2026-beginner-to-advance-tutorial-110.md"

conda run -n content_engine_env python3 scripts/generate_carousel.py \
  --blog "content/blogs/2026-05-21_life_self_dev_how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals.md"

conda run -n content_engine_env python3 scripts/generate_carousel.py \
  --blog "content/blogs/2026-05-21_poetry_quotes_when-dreams-speak-of-love.md"
# → assets/carousels/{slug}_carousel.html
# → assets/carousels/slides/{slug}/slide_N.png
```

### [x] Worksheet PDFs ✅ done (DS + Life)
- `output/worksheets/2026-05-21_data_science_tech_complete-python-course-2026-beginner-to-advance-tutorial-110_worksheet.pdf`
- `output/worksheets/2026-05-21_life_self_dev_how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals_worksheet.pdf`

---

## THURSDAY LEFTOVERS

### [ ] Record DS video (screen recording)
- Script: `content/scripts/2026-05-22_2026-05-21-data-science-tech-complete-python-course-2026-beg_yt.md`
- Production guide: `content/scripts/2026-05-22_2026-05-21-data-science-tech-*_PRODUCTION_GUIDE.md` (generate first — see Tuesday)
- Save raw to: `assets/raw/complete-python-course-2026-beginner-to-advance-tutorial-110.mov`

### [ ] Auto-edit DS video
```bash
python3 scripts/auto_edit.py \
  --raw "assets/raw/complete-python-course-2026-beginner-to-advance-tutorial-110.mov" \
  --script "content/scripts/2026-05-22_2026-05-21-data-science-tech-complete-python-course-2026-beg_yt.md" \
  --niche ds \
  --slug "complete-python-course-2026-beginner-to-advance-tutorial-110"
# → assets/video/edited/complete-python-course-2026-beginner-to-advance-tutorial-110.mp4
```

### [ ] Clip DS reel
```bash
python3 scripts/clip_shorts.py \
  --video "assets/video/edited/complete-python-course-2026-beginner-to-advance-tutorial-110.mp4" \
  --slug "complete-python-course-2026-beginner-to-advance-tutorial-110"
# → assets/video/edited/complete-python-course-2026-beginner-to-advance-tutorial-110_reel.mp4
```

---

## FRIDAY LEFTOVERS

### [ ] Record Life voiceover
- Script: `content/scripts/2026-05-22_2026-05-21-life-self-dev-how-i-turned-my-habits-into-an-engi_yt.md`
- Save to: `assets/audio/how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals_voiceover.wav`

### [ ] Record Poetry voiceover
- Script: `content/scripts/2026-05-22_2026-05-21-poetry-quotes-when-dreams-speak-of-love_yt.md`
- Save to: `assets/audio/when-dreams-speak-of-love_voiceover.wav`

### [ ] Fetch B-roll — Life
```bash
python3 scripts/fetch_videos.py \
  --script "content/scripts/2026-05-22_2026-05-21-life-self-dev-how-i-turned-my-habits-into-an-engi_yt.md" \
  --niche life
```

### [ ] Fetch B-roll — Poetry
```bash
python3 scripts/fetch_videos.py \
  --script "content/scripts/2026-05-22_2026-05-21-poetry-quotes-when-dreams-speak-of-love_yt.md" \
  --niche poetry
```

---

## SATURDAY LEFTOVERS

### [ ] Auto-edit Life video
```bash
python3 scripts/auto_edit.py \
  --raw "assets/raw/how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals.mov" \
  --script "content/scripts/2026-05-22_2026-05-21-life-self-dev-how-i-turned-my-habits-into-an-engi_yt.md" \
  --niche life \
  --slug "how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals"
```

### [ ] Auto-edit Poetry video
```bash
python3 scripts/auto_edit.py \
  --raw "assets/raw/when-dreams-speak-of-love.mov" \
  --script "content/scripts/2026-05-22_2026-05-21-poetry-quotes-when-dreams-speak-of-love_yt.md" \
  --niche poetry \
  --slug "when-dreams-speak-of-love"
```

### [ ] Clip reels — Life + Poetry
```bash
python3 scripts/clip_shorts.py --video "assets/video/edited/how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals.mp4" --slug "how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals"
python3 scripts/clip_shorts.py --video "assets/video/edited/when-dreams-speak-of-love.mp4" --slug "when-dreams-speak-of-love"
```

### [ ] Publish to Medium
```bash
python3 scripts/publish_medium.py --input "content/blogs/2026-05-21_data_science_tech_complete-python-course-2026-beginner-to-advance-tutorial-110.md" --canonical-url https://breathofdatascience.substack.com/
python3 scripts/publish_medium.py --input "content/blogs/2026-05-21_life_self_dev_how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals.md" --canonical-url https://thisisbreathoflife.substack.com/
python3 scripts/publish_medium.py --input "content/blogs/2026-05-21_poetry_quotes_when-dreams-speak-of-love.md" --canonical-url https://breathofpoetry.substack.com/
```

### [ ] Load posts to scheduler
```bash
python3 scripts/load_posts.py
sqlite3 data/scheduling.db "SELECT platform, scheduled_at, substr(content_text,1,60) FROM posts ORDER BY scheduled_at LIMIT 15"
```

---

## SUNDAY TASKS (TODAY)

### [ ] Publish Substack — DS
Substack MCP or manual: `content/blogs/2026-05-21_data_science_tech_complete-python-course-2026-beginner-to-advance-tutorial-110.md`
→ breathofdatascience.substack.com

### [ ] Publish Substack — Life
`content/blogs/2026-05-21_life_self_dev_how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals.md`
→ thisisbreathoflife.substack.com

### [ ] Publish Substack — Poetry
`content/blogs/2026-05-21_poetry_quotes_when-dreams-speak-of-love.md`
→ breathofpoetry.substack.com

### [ ] Social scheduling via Publer
Generate CSVs first (if not done):
```bash
python3 scripts/generate_publer_csv.py 2>/dev/null || echo "check script name"
```
Then import `output/scheduled/publer_ig_fb.csv` + `output/scheduled/publer_threads.csv` into Publer.

### [ ] Twitter threads (manual paste)
```bash
cat "content/derivatives/2026-05-21-data-science-tech-complete-python-course-2026-beg/twitter_thread.txt"
cat "content/derivatives/2026-05-21-life-self-dev-how-i-turned-my-habits-into-an-engi/twitter_thread.txt"
cat "content/derivatives/2026-05-21-poetry-quotes-when-dreams-speak-of-love/twitter_thread.txt"
```

### [ ] Upload YouTube — all 3 long-form + 3 shorts (after videos done above)
```bash
cat output/scheduled/upload_shorts.sh 2>/dev/null
```

### [!] CRITICAL — Fill content buffer (all niches at 1/4)
**Step 1:** Open `data/buffer/topics.yaml` — fill weeks 2, 3, 4 for all 3 niches (9 slots)
Check Notion Published first — no repeat angles from last 90 days.

**Step 2:** Push this week's content into week-2
```bash
python3 scripts/push_to_buffer.py --auto --date 2026-05-21 --dry-run
python3 scripts/push_to_buffer.py --auto --date 2026-05-21
```

**Step 3:** Generate weeks 3–4
```bash
conda run -n content_engine_env python3 scripts/generate_buffer.py --dry-run
conda run -n content_engine_env python3 scripts/generate_buffer.py
```

**Step 4:** Verify
```bash
for niche in data_science_tech life_self_dev poetry_quotes; do
  count=$(ls content/buffer/week-*/${niche}/*_meta.md 2>/dev/null | wc -l | tr -d ' ')
  echo "$niche: $count / 4"
done
```

### [ ] Read KB + pick next Monday's DS topic
```bash
cat data/kb/master_brief.md
cat data/ideas/weekly_ideas.md
# Pick top DS idea → Notion Contents DB → Status = In Progress
```

### [ ] Notion ideas sync (cron ran 6am — verify)
```bash
python3 scripts/sync_ideas_to_notion.py --dry-run
```

---

## STATUS SUMMARY

| Step | Status |
|------|--------|
| Blogs × 3 | ✅ done |
| YT scripts × 3 | ✅ done |
| Production guides | ✅ Life + Poetry · ❌ DS missing |
| Derivatives/repurpose × 3 | ✅ done |
| Thumbnail briefs × 3 | ✅ done |
| Thumbnail images × 3 | ✅ done |
| Claude Design prompts × 3 | ✅ done |
| Slides PDFs × 3 | ✅ done |
| Social post images × 3 | ✅ done |
| Reel covers × 3 | ✅ done |
| Story sequences | ✅ Poetry (mp4) · ✅ DS (7 slides + mp4) · ✅ Life (8 imgs) |
| Worksheet JSON | ✅ DS + Life |
| Worksheet Canva prompts | ✅ DS + Life |
| Worksheet PDFs | ✅ DS + Life |
| Carousels (replaces social post set) | ✅ done (7 slides × 3 niches) |
| PERSONAL_INSERT filled | ✅ DS + Life done |
| Images added to blogs | ✅ done |
| Audio recorded | ❌ nothing |
| Videos edited | ❌ nothing |
| Reels clipped | ❌ nothing |
| Medium published | ❌ |
| Substack published | ❌ |
| Social scheduled (Publer) | ❌ |
| Twitter threads posted | ❌ |
| YouTube uploaded | ❌ |
| load_posts.py run | ❌ DB has 0 posts |
| Content buffer | ❌ 1/4 all niches |
