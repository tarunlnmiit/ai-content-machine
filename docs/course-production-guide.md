# Course Production Guide — Draft → Record → Graphy

Separate product line from blogs/videos. **All course content is ORIGINAL** — no
repurposing of published blogs or YouTube scripts. Content is drafted with **Claude
Sonnet 4.6** (`claude-sonnet-4-6`).

Platform: **Graphy** (Indian — UPI/net-banking/cards, INR native). Config + pricing:
`data/courses/graphy_config.yaml`. Curriculum per niche: `content/courses/<niche>/curriculum.md`.

**Each lesson ships three layers:** (1) the **video** (drafted → personalised → recorded),
(2) **companion material** the student practises with (worksheet / code notebook /
template / checklist), and (3) **repurpose hooks** — free social teasers (YT Short, IG
carousel, X thread) derived from the recorded lesson to sell the course. A full
per-lesson outline carrying all three layers lives at
`content/courses/<niche>/outline.md` (all three niches done).

**DS signature differentiators (market moats).** Research showed the field is full of
no-depth syntax tutorials, clean Kaggle data, and zero feedback. The DS course answers
that with three assets nobody else offers — record/build these once:
- **🎥 "Inside the Work" raw sessions** — unedited, unscripted screen recordings of Tarun
  solving a real messy problem start-to-finish (L2/5/8/10). One-take, NO editing, no
  hyperframes — the rawness *is* the value. Show the dead ends.
- **🔑 Real dirty datasets + failure-mode answer key** — anonymise a genuinely messy real
  dataset, write a key of everything wrong with it (L2, reused L3/7/10).
- **AI-as-practitioner capstone** — L10, plus light "would I trust AI here?" checkpoints.

Every niche has its own moats (full detail in each `outline.md`), but all three share one
brand thread — a **"watch me actually do it" raw session**:
- **Life:** 🎥 real systems-teardown (Tarun's own tracker/check-in/review on screen) · 📊
  "your life as a dataset" tracker kit · built for Indian student pressure.
- **Poetry:** 🎥 write-along (Tarun drafting from a blank page, crossing out lines) · 📝
  original prompt deck · share-without-shame ritual.

**Building a course on weekends?** Follow the per-niche weekend guides — hour-blocked,
checkbox, copy-paste commands, each splits one course across 2–3 weekends:
`docs/course-weekend-ds.md` · `docs/course-weekend-life.md` · `docs/course-weekend-poetry.md`.

## TL;DR

```bash
# 1. Draft a lesson script (Sonnet). Repeat --point ~3x.
python3 scripts/draft_lesson_script.py \
  --niche ds \
  --title "How practitioners actually frame a problem" \
  --point "Business ask is not the modelling question" \
  --point "Define the target before the model" \
  --point "Frame for the decision, not the metric" \
  --story "The churn project where the real question was retention budget"
# → content/courses/data_science/lesson_scripts/YYYY-MM-DD_<slug>.md

# 2. Generate the matching worksheet (Sonnet, original — no blog ingested).
python3 scripts/generate_course_worksheet.py \
  --niche ds \
  --topic "Framing a problem before touching a model" \
  --objective "translate a vague business ask into a testable target variable"
# → content/courses/data_science/worksheets/YYYY-MM-DD_<slug>_worksheet.md
#   (poetry → content/courses/poetry/prompts/)

# 2b. (DS only) Generate the seeded dirty datasets the worksheets read + answer keys.
#     Always use the project conda env. --all builds every ds dataset; --name <one> for one.
conda run -n content_engine_env python scripts/generate_course_dataset.py --niche ds --all
# → content/courses/data_science/datasets/{loan_applications,transactions,
#   student_engagement,orders,users}.csv + *_answer_key.md
#   NOTE: baselines + L7 worksheets run sklearn → students need: pip install scikit-learn

# 2c. (DS only) Build the companion notebooks (needs nbformat: pip install nbformat).
conda run -n content_engine_env python scripts/build_course_notebooks.py --niche ds --which both
# → content/courses/data_science/notebooks/{data_audit_starter,
#   notebook_to_module_refactor_kit}.ipynb
#   data_audit_starter loads ../datasets/loan_applications.csv — run it from the notebooks/ folder.

# 3. Personalise: fill every [PERSONAL_INSERT] / [PERSONAL_STORY] with real detail.
grep -n 'PERSONAL' content/courses/<niche>/lesson_scripts/<file>.md

# 4. Record (see Recording below). 5. Upload to Graphy. 6. Back up masters.
```

## Niche flags & destinations

| Flag | Course | Lesson dir | Worksheet dir | Video |
|------|--------|-----------|---------------|-------|
| `ds` | Data Science from the Inside | `content/courses/data_science/lesson_scripts/` | `…/data_science/worksheets/` | screen-share + talking head |
| `life` | Systems for Humans | `content/courses/life_self_dev/lesson_scripts/` | `…/life_self_dev/worksheets/` | talking head |
| `poetry` | Write Like You Mean It | `content/courses/poetry/lesson_scripts/` | `…/poetry/prompts/` | talking head, Tarun reading |

## The two scripts

Both call `claude -p --model claude-sonnet-4-6` and load `data/kb/master_brief.md` +
`prompts/writing_agent.md` so output carries Tarun's voice and respects the
banned-words list in CLAUDE.md.

- **`draft_lesson_script.py`** — `lesson title + ~3 key points + 1 story prompt`
  → 10–15 min spoken script (cold open → why → teach → story → do-this-now →
  close). Marks `[PERSONAL_INSERT]` / `[PERSONAL_STORY]` for real detail.
- **`generate_course_worksheet.py`** — `topic + learning objective` →
  original worksheet. Type adapts: ds = code+exercise, life = reflection/journaling,
  poetry = writing prompts. **Ingests no published content** (unlike
  `scripts/generate_worksheet_outline.py`, which derives from a blog).

A third script backs the DS **dirty-dataset moat** (no Claude call — pure seeded numpy/pandas):

- **`generate_course_dataset.py`** — `--niche ds [--name <one> | --all]` → seeded synthetic
  dirty CSVs the DS worksheets `read_csv`, each with a failure-mode `*_answer_key.md`. A frozen
  registry per dataset is the single source of truth; every count in the key is re-measured from
  the **re-read** CSV, and an in-script `verify` enforces each worksheet's binding constraints
  (e.g. `loan_applications` keeps `age/income/loan_amount` numeric so Task 3 doesn't `TypeError`;
  `student_engagement` locks the 84/16 split and makes `completion_pct` the unique leakage feature).
  Deterministic: same `--seed` (default 42) → byte-identical CSV. Run via `conda run -n
  content_engine_env`. Datasets: loan_applications, transactions, student_engagement, orders, users.
- **`build_course_notebooks.py`** — `--niche ds [--which audit|refactor|both]` → the two DS
  companion notebooks (`nbformat.v4`, validated before writing; no Claude call). `data_audit_starter`
  pairs with the L2 worksheet and loads `../datasets/loan_applications.csv` (**run it from
  `notebooks/`**); `notebook_to_module_refactor_kit` is self-contained. Needs `pip install nbformat`.

## Recording

- Record **yourself**, not AI voiceover — Indian students connect with a real
  person; Indian English is fine.
- Life/Poetry: talking head, front cam, look at camera. DS: screen-share for code
  walkthrough + talking-head intro/outro.
- Length targets: DS 10–15 min, Life 8–12 min, Poetry 6–10 min.
- **Pre-sell first:** record only Lessons 1–2 per course, pre-sell at 50% off. If
  20+ buy → record the rest. Free Lesson 1 as the email-gated lead magnet.

## Editing — your existing pipeline, minimal effort

Same muscle as your YouTube videos: **record in one take, trim what you don't need,
let pre-lined B-roll/animations drop in, then a light overlay pass.** Do NOT hand-edit.

**Life & Poetry lessons (talking head)** — full pipeline:

```bash
# 1. Trim + map [BROLL:] cues + captions → Remotion edit-plan
python3 scripts/prepare_remotion_edit.py \
  --raw "assets/raw/<lesson>.MOV" --script "<lesson-script>.md" --niche life --slug <slug>
# 2. Assemble in Remotion (cuts + b-roll + captions + grading)
cd remotion && npx remotion render CourseLesson ../assets/video/edited/<slug>.mp4 \
  --props="{\"editPlanFile\":\"edit-plans/<slug>.json\"}" && cd ..
# 3. Light overlay pass — RESTRAINED so it reads human-edited, not machine-made
python3 scripts/hyperframes_render.py assets/video/edited/<slug>.mp4 --slug <slug> --intensity minimal
```

**Key for course feel:** always run hyperframes at `--intensity minimal` (or skip it).
Courses want a calm human editor — sparse overlays on genuine high-value beats, not an
effects reel. `minimal` ≈ one overlay per minute, calm slide/fade motion. (`--intensity`
default is `light`; `dense` is the old maximal look — wrong for teaching.)

**DS lessons (screen-share):** the talking-head Remotion pipeline fits only the
talking-head intro/outro. For the screen-share body, just trim the recording and, if
you want any overlays, run `hyperframes_render.py … --intensity minimal` on it. Keep it clean.

Outsourceable, but the pipeline above means you usually don't need to.

## Distribution channels — Graphy course vs YouTube Membership

Don't conflate two different money models. Config: `data/courses/graphy_config.yaml` → `distribution`.

| Channel | Role | Model | Owns emails? |
|---------|------|-------|--------------|
| **Graphy** | Paid course host | One-time ₹INR (UPI) — lessons + worksheets + dirty dataset + certificate + group | **Yes** (export monthly) |
| **YouTube (free)** | Funnel | Free teasers + free Lesson 1 → Graphy | n/a |
| **YouTube Membership** | *Recurring* side-product | Monthly tier — members-only **🎥 Inside the Work** sessions + monthly live Q&A | No (YouTube does) |

**Why Graphy stays the course host, not YouTube:** YouTube can't gate worksheets/datasets,
can't issue a certificate, can't take one-time UPI, takes a ~30% cut, and **you don't own
the student emails**. Membership is *recurring monthly* — a different product from the
one-time course, so it complements, never replaces, Graphy.

**The moat does double duty:** the "Inside the Work" raw sessions are both a paid-course
asset AND the best YouTube Membership perk — recurring revenue plus a live advert for the
course's depth.

**YouTube "Courses" (paid product):** US-first, limited rollout, being wound down — treat
as **unavailable for India**. Don't plan around it.

**Sequencing:** Membership needs monetization eligibility (1k subs + 4k watch-hours).
Launch the Graphy course now; add the Membership tier once the channel qualifies.

## Graphy upload checklist (per course)

1. Create course shell: title, description, cover, price (from `graphy_config.yaml`).
2. Connect Razorpay / direct UPI. **Test a ₹1 transaction before launch.**
3. Upload lessons; gate Lesson 1 as free preview (email capture).
4. Certificate on completion (Canva template + logo + course/student name).
5. WhatsApp/Telegram group link added; students join on first sale.
6. Link course in the matching YouTube channel "About" + video descriptions.
7. Fill `graphy_course_id` + `enrol_url` back into `data/courses/graphy_config.yaml`.

## Backups & ownership (do not skip)

- Keep video masters on Google Drive / own storage — **never Graphy-only**.
- Export the student email list from Graphy **monthly** — own your audience.
- Refund policy: 7-day refund if no more than 2 lessons watched.

## Launch order (staggered, not simultaneous)

DS (₹299) → Life (₹149) → Poetry (₹99) → Bundle ₹449. Announce one at a time to
avoid splitting attention; all can be live on Graphy at once. First 50 students per
course get launch price, then it auto-raises.
