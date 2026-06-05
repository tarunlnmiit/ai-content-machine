# DS Course Outline — "Data Science from the Inside: A Practitioner's Mindset"

**Niche flag:** `ds` · **Funnel:** @breathofdatascience → course
**Audience:** Engineering/CS students + freshers, 18–25 (Indian market)
**Format:** Video lessons (10–15 min) — talking-head intro/outro + screen-share for code.
**Launch price:** ₹299 (early-bird first 50; later ₹999–₹1,499).
**Promise:** Not "learn Python." How a 10-year practitioner actually thinks about data,
problems, and a career — the part no college or YouTube tutorial teaches.

> Every lesson is ORIGINAL (no repurposing of published blogs/YT scripts into the
> paid product). Repurposing flows the OTHER way: paid lessons → free social teasers
> that sell the course.

## Each lesson ships three layers

1. **Video** — the spoken lesson (drafted via `draft_lesson_script.py`, then personalised + recorded).
2. **Companion material** — a practice/use-along asset the student keeps and works in
   (worksheet, code notebook, template, or checklist). Drafted via
   `generate_course_worksheet.py` + any extra asset noted per lesson.
3. **Repurpose hooks** — free social content derived from the lesson to drive course
   sales: a YT Short, an IG carousel, an X thread. Free Lesson 1 is the email-gated
   lead magnet. Teasers point to the paid course.

## Signature differentiators — what nobody else offers

The market is full of syntax tutorials with no depth, clean Kaggle data, and zero
feedback. Three moats make this course unmistakably different — and each reinforces the
"from the inside" promise:

1. **"Inside the Work" raw sessions.** Unedited screen recordings of Tarun solving a
   real, messy problem start-to-finish — think-aloud, dead ends, debugging, the ugly
   middle every other course edits out. Bundled with **L2, L5, L8**. This is the
   signature asset: the 10-year practitioner's process made *visible*. Zero ongoing
   cost (record once), near-impossible for tutorial channels to fake.
2. **Real dirty datasets + failure-mode answer key.** Anonymised genuinely-messy
   datasets (missing, wrong, late, timezone-broken) shipped with a key documenting
   *everything wrong with them*. Students practise on real chaos, not Kaggle. Powers the
   companion material for **L2, L3, L7**.
3. **AI-as-practitioner layer.** Honest teaching on when to trust AI and when judgment
   must override — AI as a junior analyst you supervise, not an oracle. Its own capstone
   (**L10**) plus light "would I trust AI here?" checkpoints woven through earlier lessons.

These answer the exact complaints the market research surfaced: no depth → raw sessions
show the depth; clean-data fantasy → real dirty datasets; "DS is dying to AI" fear →
the AI-as-practitioner layer reframes judgment as the durable, human, hireable skill.

## Course arc

L1–3 = **how practitioners think** (frame, distrust data, build intuition). L4–5 =
**get hired + ship** (interviews, first project). L6–9 = **operate like a senior**
(communicate, judgment to skip ML, work in a real team, stay current). L10 =
**capstone: supervise AI like a practitioner**. Each lesson stands alone but the arc
takes a student from "I know syntax" → "I think like someone with 10 years in."

## Funnel logic

- **Free:** Lesson 1 full video (email gate) + 2–3 social teasers per lesson.
- **Paid:** Lessons 2–10 + all companion material + the 4 "Inside the Work" raw sessions +
  the real dirty dataset + certificate + WhatsApp/Telegram group.
- **Pre-sell:** record Lessons 1–2 only, pre-sell at 50% off. 20+ buyers → record the rest.

---

## Lesson 1 — How practitioners actually frame problems

- **Outcome:** Student can turn a vague business ask into a testable target variable.
- **Cold-open hook:** "The model is the easy part. The job is deciding what to predict —
  and most people get that wrong before they write a line of code."
- **Key points (→ `--point`):**
  1. The business ask is not the modelling question
  2. Define the target before you touch a model
  3. Frame for the decision, not the metric
- **Story (→ `--story`):** The churn project where the real question was the retention budget, not "who will churn."
- **Companion material:** Worksheet — *Problem-Framing Canvas*: take a vague ask, write
  the decision it serves, the target variable, and the unit of prediction.
- **Do-this-now:** Translate one real/handout business ask into a target variable.
- **Repurpose hooks:**
  - YT Short: "Stop building models. Do this first." (60s, the framing trap)
  - IG carousel: 5 slides — vague ask → testable target, worked example
  - X thread: "Juniors model. Seniors frame. Here's the difference ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche ds \
    --title "How practitioners actually frame problems" \
    --point "The business ask is not the modelling question" \
    --point "Define the target before you touch a model" \
    --point "Frame for the decision, not the metric" \
    --story "The churn project where the real question was the retention budget"
  python3 scripts/generate_course_worksheet.py --niche ds \
    --topic "Framing a problem before touching a model" \
    --objective "translate a vague business ask into a testable target variable"
  ```

---

## Lesson 2 — Dirty data realities (not clean Kaggle sets)

- **Outcome:** Student can audit a messy dataset and document its failure modes.
- **Cold-open hook:** "Kaggle lied to you. Real data shows up missing, wrong, and late —
  and cleaning it IS the job, not a chore before the job."
- **Key points:**
  1. Real data is missing, wrong, and late — assume nothing
  2. Cleaning isn't pre-work; it's most of the work
  3. Trust nothing until you've checked it yourself
- **Story (→ `--story`):** The dataset where a "timestamp" column was three timezones stitched together and silently wrecked every result.
- **Companion material:** Code notebook — *Data Audit Starter* (`.ipynb`): cells for null
  maps, type checks, range/sanity checks, duplicate + timezone traps. PLUS **🔑 real dirty
  dataset + failure-mode answer key** (signature moat #2) — anonymised messy data students
  audit, then check against the key.
- **🎥 Inside the Work session** (moat #1): unedited recording of Tarun auditing a real
  messy dataset cold — every check, every surprise, in real time.
- **Do-this-now:** Run the audit notebook on the real dirty dataset; log 3 failure modes, check the key.
- **Repurpose hooks:**
  - YT Short: "Your dataset is lying to you. 3 checks before you trust it."
  - IG carousel: the timezone-merge horror story as a 6-slide cautionary tale
  - X thread: "Clean Kaggle data ruined a generation of analysts. What real data looks like ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche ds \
    --title "Dirty data realities, not clean Kaggle sets" \
    --point "Real data is missing, wrong, and late — assume nothing" \
    --point "Cleaning is not pre-work; it is most of the work" \
    --point "Trust nothing until you have checked it yourself" \
    --story "The timestamp column that was three timezones stitched together"
  python3 scripts/generate_course_worksheet.py --niche ds \
    --topic "Auditing messy real-world data" \
    --objective "audit a messy dataset and document its failure modes"
  ```

---

## Lesson 3 — Building intuition before building models

- **Outcome:** Student sets a baseline and a sanity check before any model.
- **Cold-open hook:** "If you can't beat a guess with a one-line rule, your fancy model
  is decoration."
- **Key points:**
  1. Look before you fit — plot it, eyeball it, question it
  2. Baselines first; the model has to beat something
  3. Know what "good" looks like before you start
- **Story (→ `--story`):** The time a `groupby` + mean beat a colleague's gradient-boosted model and saved a week.
- **Companion material:** Template — *Baseline-First Checklist* (1 page): the 5 looks +
  the dumb-baseline formula to run before modelling. Practise it on the **🔑 real dirty
  dataset** from L2 (moat #2) — set a baseline on data that fights back.
- **Do-this-now:** Set one baseline + one sanity check on a current problem.
- **Repurpose hooks:**
  - YT Short: "A `groupby` beat his ML model. Here's why."
  - IG carousel: "Baseline first" — the 5 looks before you model
  - X thread: "The most underrated DS skill isn't modelling. It's knowing what good looks like."
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche ds \
    --title "Building intuition before building models" \
    --point "Look before you fit — plot it, eyeball it, question it" \
    --point "Baselines first; the model must beat something" \
    --point "Know what good looks like before you start" \
    --story "The groupby-and-mean that beat a gradient-boosted model"
  python3 scripts/generate_course_worksheet.py --niche ds \
    --topic "Baselines and sanity checks before modelling" \
    --objective "set a baseline and a sanity check before any model"
  ```

---

## Lesson 4 — Career navigation: what interviews actually test

- **Outcome:** Student drafts the one project story they tell in interviews.
- **Cold-open hook:** "Interviews don't test what you know. They test how you think out
  loud — and whether they'd trust you with a real problem."
- **Key points:**
  1. Reasoning beats recall — they watch how you get there
  2. Communicating tradeoffs is the actual signal
  3. One project told well gets you hired
- **Story (→ `--story`):** The candidate who knew less but got the offer because they reasoned through the messy middle out loud.
- **Companion material:** Worksheet — *Project Story Builder*: situation → your decision →
  the tradeoff → the result, in a tellable arc.
- **Do-this-now:** Write the first draft of your one interview project story.
- **Repurpose hooks:**
  - YT Short: "Why the candidate who knew less got the job."
  - IG carousel: "The project story that gets you hired" — the 4-part structure
  - X thread: "10 years interviewing DS candidates. The one thing that separates offers from rejections ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche ds \
    --title "What data science interviews actually test" \
    --point "Reasoning beats recall — they watch how you think out loud" \
    --point "Communicating tradeoffs is the real signal" \
    --point "One project told well gets you hired" \
    --story "The candidate who knew less but reasoned through the messy middle and got the offer"
  python3 scripts/generate_course_worksheet.py --niche ds \
    --topic "The interview project story" \
    --objective "draft the one project story you tell in interviews"
  ```

---

## Lesson 5 — Your first real project approach

- **Outcome:** Student plans a 1-week end-to-end project.
- **Cold-open hook:** "Your tenth tutorial taught you nothing your first real project
  won't teach you in a week. Scope it small. Ship it whole."
- **Key points:**
  1. Scope small — one question, one dataset, one output
  2. Ship end-to-end before you polish any part
  3. Iterate on the whole, not the pieces
- **Story (→ `--story`):** The over-scoped first project that died half-built vs. the tiny one that actually shipped and got noticed.
- **Companion material:** Template — *1-Week Project Planner*: day-by-day scope, the
  cut-line for "good enough to ship," the one output.
- **🎥 Inside the Work session** (moat #1): Tarun scopes and starts a real 1-week project
  on camera — the messy decisions of what to cut and what to ship.
- **Do-this-now:** Fill the planner for a project you'll start this week.
- **Repurpose hooks:**
  - YT Short: "Stop doing tutorials. Build this instead (1 week)."
  - IG carousel: "Your first real DS project — day by day"
  - X thread: "Tutorials are a trap. Here's the 1-week project that replaces 10 of them ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche ds \
    --title "Your first real data project, end to end in a week" \
    --point "Scope small — one question, one dataset, one output" \
    --point "Ship end-to-end before you polish any part" \
    --point "Iterate on the whole, not the pieces" \
    --story "The over-scoped project that died vs the tiny one that shipped and got noticed"
  python3 scripts/generate_course_worksheet.py --niche ds \
    --topic "Scoping a first end-to-end project" \
    --objective "plan a 1-week end-to-end project"
  ```

---

## Lesson 6 — Communicating results to non-technical people

- **Outcome:** Student turns a model result into a 3-sentence decision brief.
- **Cold-open hook:** "Nobody in the room cares about your AUC. They care what to do
  Monday. If you can't say that, the analysis didn't happen."
- **Key points:**
  1. Lead with the decision, not the model
  2. A story beats a metric in a room full of non-technical people
  3. One chart that lands beats ten that impress
- **Story (→ `--story`):** The flawless analysis that got ignored until it was reduced to one sentence and one chart.
- **Companion material:** Template — *Decision Brief One-Pager*: headline decision →
  why → the one chart → the risk. Reusable for any result.
- **Do-this-now:** Compress one past result into a 3-sentence brief.
- **Repurpose hooks:**
  - YT Short: "Nobody cares about your AUC. Say this instead."
  - IG carousel: "Turn a model result into a decision in 3 sentences"
  - X thread: "The analysis was perfect. It got ignored. Here's what I changed ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche ds \
    --title "Communicating results to non-technical people" \
    --point "Lead with the decision, not the model" \
    --point "A story beats a metric in a non-technical room" \
    --point "One chart that lands beats ten that impress" \
    --story "The flawless analysis ignored until it became one sentence and one chart"
  python3 scripts/generate_course_worksheet.py --niche ds \
    --topic "Communicating a result as a decision" \
    --objective "turn a model result into a 3-sentence decision brief"
  ```

---

## Lesson 7 — When NOT to use ML

- **Outcome:** Student decides ML-or-not for 3 real problems, with reasons.
- **Cold-open hook:** "The senior move is often deleting the model. A rule you can
  explain beats a model you can't."
- **Key points:**
  1. Rules and heuristics beat models more often than anyone admits
  2. Every model carries a hidden cost — maintenance, drift, trust
  3. The boring solution that ships wins over the clever one that rots
- **Story (→ `--story`):** The project where a 4-line `if` rule replaced a model and ran for years untouched.
- **Companion material:** Checklist — *ML-or-Not Decision Filter*: the questions that tell
  you whether a problem actually needs ML. Test it against the **🔑 real dirty dataset**
  (moat #2) — does this messy problem even need a model?
- **Do-this-now:** Run 3 real problems through the filter; justify each call.
- **Repurpose hooks:**
  - YT Short: "A 4-line `if` statement replaced his ML model. For years."
  - IG carousel: "When NOT to use ML — the senior filter"
  - X thread: "Juniors add models. Seniors delete them. When ML is the wrong call ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche ds \
    --title "When NOT to use machine learning" \
    --point "Rules and heuristics beat models more often than anyone admits" \
    --point "Every model carries a hidden cost — maintenance, drift, trust" \
    --point "The boring solution that ships beats the clever one that rots" \
    --story "The 4-line if-rule that replaced a model and ran for years untouched"
  python3 scripts/generate_course_worksheet.py --niche ds \
    --topic "Deciding when machine learning is the wrong tool" \
    --objective "decide ML-or-not for 3 real problems with reasons"
  ```

---

## Lesson 8 — Working in a real codebase and team

- **Outcome:** Student takes one notebook cell and makes it reusable, tracked code.
- **Cold-open hook:** "Your notebook is not the job. The job is code other people can
  read, run, and trust six months from now."
- **Key points:**
  1. Notebooks are for thinking; production is for shipping — move between them
  2. Git, reviews, and reading others' code are the real day job
  3. Don't be the lone hero — the team's code outlives your cleverness
- **Story (→ `--story`):** The brilliant notebook nobody could rerun, vs. the modest function the whole team still uses.
- **Companion material:** Code notebook + template — *Notebook → Module Refactor Kit*:
  before/after of one cell turned into a tested, importable function with a git-ready structure.
- **🎥 Inside the Work session** (moat #1): Tarun refactors a real messy notebook into
  team-ready code on camera — git, structure, the judgment calls.
- **Do-this-now:** Refactor one notebook cell into reusable, version-tracked code.
- **Repurpose hooks:**
  - YT Short: "Your notebook isn't the job. This is."
  - IG carousel: "Notebook → production: one cell, refactored"
  - X thread: "Nobody could rerun his brilliant notebook. The fix that makes you a real teammate ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche ds \
    --title "Working in a real codebase and team" \
    --point "Notebooks are for thinking; production is for shipping — move between them" \
    --point "Git, reviews, and reading others' code are the real day job" \
    --point "Don't be the lone hero — the team's code outlives your cleverness" \
    --story "The brilliant notebook nobody could rerun vs the modest function the team still uses"
  python3 scripts/generate_course_worksheet.py --niche ds \
    --topic "Moving from notebooks to real team code" \
    --objective "take one notebook cell and make it reusable, tracked code"
  ```

---

## Lesson 9 — Staying current without drowning

- **Outcome:** Student builds their own "learn this / ignore this" filter.
- **Cold-open hook:** "There's a new model every week and you will burn out chasing them.
  Ten years in, the skill is knowing what to ignore."
- **Key points:**
  1. Ignore the hype cycle — most of it won't exist in a year
  2. Learn deep, not wide — fundamentals compound, tools expire
  3. A 10-year filter: does this change how I work, or just what's trending?
- **Story (→ `--story`):** The hyped tool everyone learned that vanished, vs. the fundamental that paid off for a decade.
- **Companion material:** Template — *Learn-or-Ignore Filter*: a personal one-page rubric
  for triaging new tools/papers/trends.
- **Do-this-now:** Build your filter list — 3 things to learn deep, 3 to ignore.
- **Repurpose hooks:**
  - YT Short: "Stop learning every new model. Do this instead."
  - IG carousel: "Learn this / ignore this — a 10-year filter"
  - X thread: "Everyone learned the hyped tool. It's gone. What I learned instead, and still use ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche ds \
    --title "Staying current without drowning" \
    --point "Ignore the hype cycle — most of it won't exist in a year" \
    --point "Learn deep, not wide — fundamentals compound, tools expire" \
    --point "A 10-year filter: does this change how I work, or just what's trending" \
    --story "The hyped tool everyone learned that vanished vs the fundamental that paid off for a decade"
  python3 scripts/generate_course_worksheet.py --niche ds \
    --topic "Filtering what to learn in a fast-moving field" \
    --objective "build your own learn-this / ignore-this filter list"
  ```

---

## Lesson 10 — Working with AI as a practitioner (capstone)

- **Outcome:** Student can decide when to trust AI output and when judgment must override —
  and articulate why, the way a hireable practitioner does.
- **Cold-open hook:** "AI will write the code. It won't tell you the question was wrong.
  That gap — between an answer and a *good* answer — is the whole job now."
- **Key points (→ `--point`):**
  1. Treat AI as a fast junior analyst — useful, confident, and wrong in ways you must catch
  2. AI handles the *how*; you still own the *what* and the *should we* — framing and judgment don't automate
  3. The hireable 2026 skill is supervising AI well, not competing with it
- **Story (→ `--story`):** The time AI produced a clean, confident analysis that was
  quietly answering the wrong question — and how a practitioner caught it.
- **Companion material:** Checklist — *Trust-or-Override Filter for AI Output*: the checks
  to run before you ship anything an AI helped produce. Pairs with the **🔑 real dirty
  dataset** — let AI audit it, then catch what it missed.
- **🎥 Inside the Work session** (moat #1): Tarun works a real problem *with* an AI tool —
  where he leans on it, where he overrides it, in real time.
- **Do-this-now:** Run one AI-produced result through the Trust-or-Override filter; note where it fails.
- **Repurpose hooks:**
  - YT Short: "AI gave him a perfect answer. To the wrong question."
  - IG carousel: "How to supervise AI like a 10-year data scientist"
  - X thread: "Everyone's scared AI will take DS jobs. The people who'll keep theirs do this ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche ds \
    --title "Working with AI as a data science practitioner" \
    --point "Treat AI as a fast junior analyst — useful, confident, and wrong in ways you must catch" \
    --point "AI handles the how; you own the what and the should-we — framing and judgment don't automate" \
    --point "The hireable 2026 skill is supervising AI well, not competing with it" \
    --story "The clean, confident AI analysis that was quietly answering the wrong question"
  python3 scripts/generate_course_worksheet.py --niche ds \
    --topic "Knowing when to trust or override AI output" \
    --objective "decide when to trust AI output and when judgment must override, with reasons"
  ```

---

## Companion material — production notes

| Type | Lessons | How to make |
|------|---------|-------------|
| Worksheet | 1, 2, 4 | `generate_course_worksheet.py --niche ds` |
| Code notebook (`.ipynb`) | 2, 8 | Hand-build starter; ships in the course + as repo |
| 1-page template | 3, 5, 6, 9 | Worksheet generator or Canva one-pager |
| Checklist | 7, 10 | Worksheet generator (short form) |
| **🎥 Inside the Work session** (moat #1) | 2, 5, 8, 10 | Record once — unedited real problem-solving; no script, no polish |
| **🔑 Real dirty dataset + answer key** (moat #2) | 2 (reused 3, 7, 10) | Anonymise a real messy dataset; write the failure-mode key |

Bundle all companion files into a per-lesson download in Graphy. Keep editable masters
in the repo under `content/courses/data_science/`. The 4 raw sessions + the dirty dataset
are the moats — they cost recording time once and can't be cheaply copied.

## Repurposing — paid lesson → free funnel

Per lesson there are 3 teaser formats (Short / carousel / thread). That's **30 free
assets** across 10 lessons feeding @breathofdatascience + IG + X — plus short clips from
the "Inside the Work" sessions ("watch a 10-yr DS debug live") as their own teaser class.
Rules:
- Teasers give the *hook and one insight*, never the full lesson — they sell the depth.
- Every teaser ends with a soft CTA to the course (link in bio / description / pinned).
- Free Lesson 1 video is the email-gated lead magnet; teasers route cold → Lesson 1 → paid.
- Generate teasers with the existing derivative pipeline once a lesson is recorded
  (script → clips/carousels via the social tooling already in `scripts/`).

## Next actions

1. Tarun: review/edit this outline — swap hooks, stories, companion types.
2. Draft Lessons 1–2 scripts + worksheets (pre-sell pair). Commands above.
3. Personalise `[PERSONAL_*]` markers, record, edit (see `docs/course-production-guide.md`).
4. Build companion notebooks for L2/L8; **prep the real dirty dataset + answer key** (moat #2, used across L2/3/7/10).
5. **Record the 4 "Inside the Work" raw sessions** (moat #1: L2, L5, L8, L10) — one-take, unedited.
6. Create Graphy shell; fill `graphy_course_id` + `enrol_url` into `data/courses/graphy_config.yaml`.
7. After recording, generate per-lesson social teasers + "Inside the Work" clips to drive sales.
