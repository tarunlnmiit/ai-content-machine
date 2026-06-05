# Weekend Guide — Life / Self-Dev Course

**Course:** Systems for Humans: Build a Life That Doesn't Exhaust You
**Niche flag:** `life` · **Funnel:** @breathoflife_ + Substack · **Launch price:** ₹149 (first 50 seats)
**Lessons:** 7 · **Recording:** talking-head only (no screen share — simpler than DS)
**Plan:** 2–3 weekends. Pre-sell after Weekend 1 — only record the rest if 20+ buy.

Model: all drafting uses Sonnet 4.6 (`claude-sonnet-4-6`). Curriculum + module
seeds: `content/courses/life_self_dev/curriculum.md`. Pricing: `data/courses/graphy_config.yaml`.

Tick boxes as you go. Edit the title/points/story text in each command before running.

---

## Weekend 1 — Setup + Lessons 1–2 + Pre-sell

Goal by Sunday night: Lessons 1–2 recorded, course shell live, pre-sell posted.

### Saturday (~4–5 hrs) — draft & personalise

- [ ] **Lock the curriculum (30 min).** `content/courses/life_self_dev/curriculum.md` —
      confirm the 7 lesson titles + key points. You own this list.
- [ ] **Draft Lesson 1 (10 min run + 30 min edit).**
  ```bash
  python3 scripts/draft_lesson_script.py \
    --niche life \
    --title "Self-audit — where is your energy going?" \
    --point "Measure before you fix" \
    --point "Energy is not the same as time" \
    --point "Find the leaks before adding habits" \
    --story "The week I tracked my energy and found the real drain"
  ```
- [ ] **Personalise Lesson 1 (30 min).** `grep -n 'PERSONAL' content/courses/life_self_dev/lesson_scripts/*audit*.md`
- [ ] **Draft + personalise Lesson 2 (1 hr)** — habit design lesson.
- [ ] **Generate worksheets for L1–L2 (30 min).**
  ```bash
  python3 scripts/generate_course_worksheet.py --niche life \
    --topic "Auditing where your energy goes" \
    --objective "map a week's energy and name the top 2 drains"
  ```
  Repeat for Lesson 2.

### Sunday (~4–5 hrs) — record & ship pre-sell

- [ ] **Record Lessons 1–2 (2–3 hrs).** Talking head, front cam, look at camera. Read your
      personalised script. Save masters to `assets/raw/` + Google Drive.
- [ ] **Edit (45 min) — your pipeline, minimal effort.** Record-one-take → trim →
      pre-lined B-roll drops in → light overlay pass:
  ```bash
  python3 scripts/prepare_remotion_edit.py --raw "assets/raw/<lesson>.MOV" --script "<script>.md" --niche life --slug <slug>
  cd remotion && npx remotion render CourseLesson ../assets/video/edited/<slug>.mp4 --props="{\"editPlanFile\":\"edit-plans/<slug>.json\"}" && cd ..
  python3 scripts/hyperframes_render.py assets/video/edited/<slug>.mp4 --slug <slug> --intensity minimal
  ```
  `--intensity minimal` keeps overlays sparse + human. See "Editing" in `docs/course-production-guide.md`.
- [ ] **Graphy shell (1 hr).** Title, description, cover, price ₹149. Connect UPI. **Test ₹1.**
      Lesson 1 = free preview (email gate).
- [ ] **Pre-sell post (45 min).** Announce to @breathoflife_ + Substack (thisisbreathoflife):
      *"New course in 2 weeks. First 30 get 50% off. Lesson 1 free."*
- [ ] Fill `graphy_course_id` + `enrol_url` into `data/courses/graphy_config.yaml`.

**Gate:** 20+ pre-sales → continue. 0 → rethink positioning.

---

## Weekend 2 — Lessons 3–7 + Launch

Talking-head batch — faster than DS. You can finish the course this weekend if energy holds;
otherwise split L6–L7 + launch into a short Weekend 3.

### Saturday (~5–6 hrs) — draft, personalise, record L3–L5

- [ ] Draft L3–L5 with `draft_lesson_script.py --niche life` (mental-health maintenance,
      dealing with pressure, review loops). Pull text from the curriculum table.
- [ ] Personalise: `grep -n 'PERSONAL' content/courses/life_self_dev/lesson_scripts/*.md`
- [ ] Generate the 3 worksheets.
- [ ] Record L3–L5 (~45 min each). Masters → Google Drive.

### Sunday (~4–5 hrs) — L6–L7 + launch

- [ ] Draft + personalise + record Lessons 6–7. Generate worksheets.
- [ ] Upload all to Graphy in order. L1 free-preview gate confirmed.
- [ ] **Certificate (30 min).** Canva template + logo. Enable on completion.
- [ ] **Sales page + launch (1 hr).** Your hook/story in the Graphy builder. Announce price
      rises to ₹499 after first 50. Post to @breathoflife_ + Substack. WhatsApp group link on every lesson.
- [ ] **Backups (30 min).** Masters on Google Drive. Export student emails from Graphy.
- [ ] Update `students` + URLs in `data/courses/graphy_config.yaml`.

> Overflow → **Weekend 3:** finish whatever of L6–L7 + launch is left. Same Sunday checklist.

---

## Quick reference

| Step | Command |
|------|---------|
| Draft lesson | `python3 scripts/draft_lesson_script.py --niche life --title "…" --point "…" --point "…" --point "…" --story "…"` |
| Find markers | `grep -n 'PERSONAL' content/courses/life_self_dev/lesson_scripts/<file>.md` |
| Worksheet | `python3 scripts/generate_course_worksheet.py --niche life --topic "…" --objective "…"` |

Full reference: `docs/course-production-guide.md`.
