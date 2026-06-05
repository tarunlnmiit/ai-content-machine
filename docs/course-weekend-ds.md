# Weekend Guide — Data Science Course

**Course:** Data Science from the Inside: A Practitioner's Mindset
**Niche flag:** `ds` · **Funnel:** @breathofdatascience · **Launch price:** ₹299 (first 50 seats)
**Lessons:** 9 · **Recording:** screen-share (code) + talking-head intro/outro
**Plan:** 3 weekends. Pre-sell after Weekend 1 — only record the rest if 20+ buy.

Model: all drafting uses Sonnet 4.6 (`claude-sonnet-4-6`). Curriculum + module
seeds: `content/courses/data_science/curriculum.md`. Pricing: `data/courses/graphy_config.yaml`.

Tick boxes as you go. Each command is copy-paste — edit the title/points/story text first.

---

## Weekend 1 — Setup + Lessons 1–2 + Pre-sell

Goal by Sunday night: Lessons 1–2 recorded, course shell live on Graphy, pre-sell
announcement posted. **Do not record the rest until pre-sell validates.**

### Saturday (~5–6 hrs) — draft & personalise

- [ ] **Lock the curriculum (45 min).** Open `content/courses/data_science/curriculum.md`.
      Confirm/rewrite the 9 lesson titles + key points. You own this list.
- [ ] **Draft Lesson 1 (10 min run + 30 min edit).**
  ```bash
  python3 scripts/draft_lesson_script.py \
    --niche ds \
    --title "How practitioners actually frame problems" \
    --point "Business ask is not the modelling question" \
    --point "Define the target before the model" \
    --point "Frame for the decision, not the metric" \
    --story "The project where the real question was budget, not accuracy"
  ```
  → saves to `content/courses/data_science/lesson_scripts/`.
- [ ] **Personalise Lesson 1 (45 min).** Fill every marker with YOUR real detail:
  ```bash
  grep -n 'PERSONAL' content/courses/data_science/lesson_scripts/*framing*.md
  ```
- [ ] **Draft + personalise Lesson 2 (1.5 hr)** — same two steps, dirty-data lesson.
- [ ] **Generate worksheets for L1–L2 (30 min).**
  ```bash
  python3 scripts/generate_course_worksheet.py --niche ds \
    --topic "Framing a problem before touching a model" \
    --objective "translate a vague business ask into a testable target variable"
  ```
  Repeat for Lesson 2. Review for originality + fit.

### Sunday (~5–7 hrs) — record & ship pre-sell

- [ ] **Record Lessons 1–2 (3–4 hrs).** Talking-head intro → screen-share for code →
      talking-head close. Read your personalised script. One retake per lesson max —
      done beats perfect. Save masters to `assets/raw/` AND Google Drive.
- [ ] **Edit (1 hr).** Trim dead air / fumbles. Screen-share body: just trim. Talking-head
      intro/outro can run the Remotion pipeline. Optional overlays: `hyperframes_render.py
      <edited>.mp4 --slug <slug> --intensity minimal` — keep it calm, this is teaching.
      See "Editing" in `docs/course-production-guide.md`.
- [ ] **Graphy shell (1 hr).** Create course: title, description, cover, price ₹299.
      Connect Razorpay/UPI. **Test a ₹1 transaction.** Set Lesson 1 = free preview (email gate).
- [ ] **Pre-sell post (45 min).** Announce to @breathofdatascience (community tab + a short
      video) + Twitter + Substack: *"Course drops in 2 weeks. First 30 students get 50% off.
      Here's Lesson 1 free."* Pin course link in channel About + video descriptions.
- [ ] **Fill back the config.** Put `graphy_course_id` + `enrol_url` into `data/courses/graphy_config.yaml`.

**Gate:** 20+ pre-sales by next weekend → continue. 0 buy → rethink positioning before recording more.

---

## Weekend 2 — Lessons 3–6 (bulk)

Goal: 4 more lessons drafted, personalised, recorded, worksheets done.

### Saturday (~5–6 hrs) — draft & personalise L3–L6

- [ ] Draft each with `draft_lesson_script.py --niche ds` (intuition/baselines,
      interviews, first project, + one more from your curriculum). Pull the
      `--title`/`--point`/`--story` text straight from the curriculum table.
- [ ] Personalise every script: `grep -n 'PERSONAL' content/courses/data_science/lesson_scripts/*.md`
- [ ] Generate the 4 worksheets with `generate_course_worksheet.py --niche ds`.

### Sunday (~5–7 hrs) — record L3–L6

- [ ] Batch-record all four (same studio setup — keep lighting/cam fixed). ~1 hr each.
- [ ] Edit (trim + optional `--intensity minimal` overlays). Save masters to `assets/raw/` + Google Drive.
- [ ] Upload to Graphy as you finish. Notify pre-sale buyers in the WhatsApp group.

---

## Weekend 3 — Lessons 7–9 + Launch

### Saturday (~5–6 hrs) — final lessons

- [ ] Draft + personalise + record Lessons 7–9. Generate their worksheets.
- [ ] Upload all to Graphy. Confirm lesson order + free-preview gate on L1.

### Sunday (~4–5 hrs) — launch

- [ ] **Certificate (45 min).** Canva template + your logo + course/student name. Enable on completion.
- [ ] **Sales page copy (1 hr).** Use Graphy builder; hook + story in your own words.
- [ ] **Full launch (1 hr).** Announce price goes to ₹999 after first 50. YouTube video +
      community + Twitter + Substack. WhatsApp group link on every lesson.
- [ ] **Backups (30 min).** All masters on Google Drive. Export student email list from Graphy.
- [ ] Mark course rows complete in `data/courses/graphy_config.yaml` (`students`, URLs).

---

## Quick reference

| Step | Command |
|------|---------|
| Draft lesson | `python3 scripts/draft_lesson_script.py --niche ds --title "…" --point "…" --point "…" --point "…" --story "…"` |
| Find markers | `grep -n 'PERSONAL' content/courses/data_science/lesson_scripts/<file>.md` |
| Worksheet | `python3 scripts/generate_course_worksheet.py --niche ds --topic "…" --objective "…"` |

Full reference: `docs/course-production-guide.md`.
