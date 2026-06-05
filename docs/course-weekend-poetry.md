# Weekend Guide — Poetry Course

**Course:** Write Like You Mean It: Poetry for People Who Think They Can't
**Niche flag:** `poetry` · **Funnel:** @breathofpoetry · **Launch price:** ₹99 (first 50 seats)
**Lessons:** 5 · **Recording:** talking-head, Tarun reading (lowest-effort course)
**Plan:** 2 weekends. Pre-sell after Weekend 1 — only record the rest if 15+ buy.

Model: all drafting uses Sonnet 4.6 (`claude-sonnet-4-6`). Curriculum + module
seeds: `content/courses/poetry/curriculum.md`. Pricing: `data/courses/graphy_config.yaml`.
Note: poetry prompt-sheets save to `content/courses/poetry/prompts/` (not `worksheets/`).

Tick boxes as you go. Edit each command's text before running.

---

## Weekend 1 — Setup + Lessons 1–2 + Pre-sell

Goal by Sunday night: Lessons 1–2 recorded, course shell live, pre-sell posted.

### Saturday (~3–4 hrs) — draft & personalise

- [ ] **Lock the curriculum (30 min).** `content/courses/poetry/curriculum.md` — confirm the
      5 lesson titles + key points. You own this list.
- [ ] **Draft Lesson 1 (10 min run + 30 min edit).**
  ```bash
  python3 scripts/draft_lesson_script.py \
    --niche poetry \
    --title "Why expressing yourself matters now" \
    --point "Naming a feeling changes it" \
    --point "You do not need anyone's permission" \
    --point "Start ugly — the first lines are meant to be bad" \
    --story "The first poem I wrote when I had no words for what I felt"
  ```
- [ ] **Personalise Lesson 1 (30 min).** `grep -n 'PERSONAL' content/courses/poetry/lesson_scripts/*matters*.md`
- [ ] **Draft + personalise Lesson 2 (45 min)** — observation lesson.
- [ ] **Generate prompt-sheets for L1–L2 (30 min).**
  ```bash
  python3 scripts/generate_course_worksheet.py --niche poetry \
    --topic "Why expressing yourself matters" \
    --objective "write 3 honest lines without editing"
  ```
  Repeat for Lesson 2. Saves to `content/courses/poetry/prompts/`.

### Sunday (~3–4 hrs) — record & ship pre-sell

- [ ] **Record Lessons 1–2 (2 hrs).** Talking head, you reading. Warm, slow delivery.
      Masters → `assets/raw/` + Google Drive.
- [ ] **Edit (30 min) — your pipeline, minimal effort.** Trim → pre-lined B-roll drops in →
      light overlay pass. Keep it intimate, not polished:
  ```bash
  python3 scripts/prepare_remotion_edit.py --raw "assets/raw/<lesson>.MOV" --script "<script>.md" --niche poetry --slug <slug>
  cd remotion && npx remotion render CourseLesson ../assets/video/edited/<slug>.mp4 --props="{\"editPlanFile\":\"edit-plans/<slug>.json\"}" && cd ..
  python3 scripts/hyperframes_render.py assets/video/edited/<slug>.mp4 --slug <slug> --intensity minimal
  ```
  Poetry especially wants restraint — `--intensity minimal`, or skip overlays entirely.
- [ ] **Graphy shell (45 min).** Title, description, cover, price ₹99. Connect UPI. **Test ₹1.**
      Lesson 1 = free preview (email gate).
- [ ] **Pre-sell post (30 min).** Announce to @breathofpoetry: *"A tiny course for people who
      think they can't write. First 30 get 50% off. Lesson 1 free."*
- [ ] Fill `graphy_course_id` + `enrol_url` into `data/courses/graphy_config.yaml`.

**Gate:** 15+ pre-sales → continue. 0 → rethink positioning.

---

## Weekend 2 — Lessons 3–5 + Launch

Whole back half of the course + launch in one weekend — it's only 3 short lessons.

### Saturday (~4 hrs) — draft, personalise, record L3–L5

- [ ] Draft L3–L5 with `draft_lesson_script.py --niche poetry` (first honest poem,
      finding your voice, sharing without shame). Pull text from the curriculum table.
- [ ] Personalise: `grep -n 'PERSONAL' content/courses/poetry/lesson_scripts/*.md`
- [ ] Generate the 3 prompt-sheets.
- [ ] Record L3–L5 (~30 min each). Masters → Google Drive.

### Sunday (~3 hrs) — launch

- [ ] Upload all 5 lessons to Graphy in order. L1 free-preview gate confirmed.
- [ ] **Certificate (30 min).** Canva template + logo. Enable on completion.
- [ ] **Sales page + launch (1 hr).** Your hook/story in the builder. Price rises to ₹299 after
      first 50. Post to @breathofpoetry. WhatsApp group where students share weekly poems.
- [ ] **Backups (30 min).** Masters on Google Drive. Export student emails from Graphy.
- [ ] Update `students` + URLs in `data/courses/graphy_config.yaml`.

---

## Quick reference

| Step | Command |
|------|---------|
| Draft lesson | `python3 scripts/draft_lesson_script.py --niche poetry --title "…" --point "…" --point "…" --point "…" --story "…"` |
| Find markers | `grep -n 'PERSONAL' content/courses/poetry/lesson_scripts/<file>.md` |
| Prompt-sheet | `python3 scripts/generate_course_worksheet.py --niche poetry --topic "…" --objective "…"` |

Full reference: `docs/course-production-guide.md`.
