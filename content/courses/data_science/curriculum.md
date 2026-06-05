# Data Science from the Inside: A Practitioner's Mindset

**Niche flag:** `ds` · **Audience:** Engineering/CS students + freshers, 18–25
**Format:** Video (10–15 min) + original code walkthrough + original worksheet · **Certificate:** Yes
**Funnel:** @breathofdatascience → course · **Launch price:** ₹299 (later ₹999–₹1,499)

**Angle:** Not "learn Python from scratch." How a 10-year practitioner actually
thinks about data, problems, and career — what no college or YouTube tutorial teaches.

> All lessons ORIGINAL. No repurposing of blogs/YouTube scripts. Separate product line.

## Modules (8–10 lessons — Tarun owns final list)

| # | Lesson | Key points (seed for `draft_lesson_script.py`) | Worksheet objective |
|---|--------|-----------------------------------------------|---------------------|
| 1 | How DS practitioners actually frame problems | Business ask ≠ modelling question · define the target before the model · frame for the decision | Translate a vague business ask into a testable target variable |
| 2 | Dirty data realities (not clean Kaggle sets) | Real data is missing/wrong/late · cleaning is the job · trust nothing | Audit a messy dataset and document its failure modes |
| 3 | Building intuition before building models | Look before you fit · baselines first · what "good" looks like | Set a baseline and a sanity check before any model |
| 4 | Career navigation — what interviews actually test | Reasoning > recall · communicate tradeoffs · the project that gets you hired | Draft the one project story you tell in interviews |
| 5 | Your first real project approach | Scope small · ship end-to-end · iterate | Plan a 1-week end-to-end project |
| 6 | Communicating results to non-technical people | The decision, not the model · story over metrics · one chart that lands | Turn a model result into a 3-sentence decision brief |
| 7 | When NOT to use ML | Rules/heuristics beat models often · cost of complexity · the boring solution wins | Decide ML-or-not for 3 real problems with reasons |
| 8 | Working in a real codebase & team | Notebooks → production · git, reviews, reading others' code · don't be the lone hero | Take one notebook cell and make it reusable, tracked code |
| 9 | Staying current without drowning | Ignore hype · learn deep not wide · a 10-yr filter for what matters | Build your own "learn this / ignore this" filter list |
| 10 | Working with AI as a practitioner (capstone) | AI = fast junior analyst · you own the what/should-we · supervising AI is the 2026 hireable skill | Decide when to trust AI output vs override, with reasons |

> Curriculum complete (10 lessons). Draft each with `draft_lesson_script.py`,
> personalise, then generate worksheets via `generate_course_worksheet.py`.
>
> **Signature differentiators** (baked into the outline): 🎥 "Inside the Work" raw
> problem-solving sessions (L2/5/8/10) · 🔑 real dirty datasets + answer key (L2/3/7/10) ·
> AI-as-practitioner capstone (L10). These are the moats — see outline for detail.
>
> **Full per-lesson outline** (hooks, stories, companion material, social
> repurpose hooks, runnable commands): `content/courses/data_science/outline.md`.

## Production

- Draft: `python3 scripts/draft_lesson_script.py --niche ds --title "…" --point "…" --point "…" --point "…" --story "…"`
- Worksheet: `python3 scripts/generate_course_worksheet.py --niche ds --topic "…" --objective "…"`
- See `docs/course-production-guide.md` for the full recording → Graphy workflow.
