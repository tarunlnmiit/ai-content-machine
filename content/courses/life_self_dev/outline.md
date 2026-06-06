# Life Course Outline — "Systems for Humans: Build a Life That Doesn't Exhaust You"

**Niche flag:** `life` · **Funnel:** @breathoflife_ + Substack → course
**Audience:** All students, 16–25 (Indian market)
**Format:** Talking-head video (8–12 min) — front cam, look at camera.
**Launch price:** ₹149 (early-bird first 50; later ₹499–₹799).
**Promise:** A data scientist applies analytical thinking to his own life. Not productivity
hacks. Not therapy. Systems that actually stick — built for the pressure you're under.

> Every lesson is ORIGINAL (no repurposing of published blogs/YT scripts into the paid
> product). Repurposing flows the OTHER way: paid lessons → free social teasers that sell
> the course.

## Each lesson ships three layers

1. **Video** — the spoken lesson (drafted via `draft_lesson_script.py`, then personalised + recorded).
2. **Companion material** — a tracker/template/reflection the student keeps and works in
   (drafted via `generate_course_worksheet.py --niche life` + any extra asset noted per lesson).
3. **Repurpose hooks** — free social content derived from the lesson to drive course sales:
   a YT Short, an IG carousel, an X thread. Free Lesson 1 is the email-gated lead magnet.

## Signature differentiators — what nobody else offers

Self-help is flooded with motivational fluff, generic habit advice, and Western
productivity that ignores academic + family pressure. Three moats make this different —
each leans on Tarun's real edge (a data scientist who measures his own life):

1. **🎥 Real systems teardown sessions.** Tarun shows his *actual* habit tracker, weekly
   review, and journal on screen — real data, real misses, no highlight reel. Bundled with
   **L1, L3, L5**. Vulnerable and concrete where everyone else is inspirational and vague.
2. **📊 "Your life as a dataset" tracker kit.** Real, ready-to-use trackers (energy,
   habits, weekly review) — measurement tools no self-help course ships. Powers the
   companion material for **L1, L2, L5, L6**.
3. **Built for Indian student reality.** Academic + family + career pressure, and
   mental-health-upkeep without stigma — named honestly, not abstracted into life-coach
   generalities. Runs through the whole course, sharpest in **L3, L4**.

These answer the market's real gaps: fluff → real teardowns with real data; no tools →
the tracker kit; one-size-fits-all → built for the pressure a 16–25 Indian student is under.

## Course arc

L1–2 = **measure, then design** (audit energy, build one habit). L3–4 = **stay upright
under load** (mental-health upkeep, pressure). L5–7 = **make it self-sustaining** (review
loops, attention, systems over goals). The arc takes a student from "I keep starting over"
→ "I have a system that runs without me white-knuckling it."

## Funnel logic

- **Free:** Lesson 1 full video (email gate) + 2–3 social teasers per lesson.
- **Paid:** Lessons 2–7 + all companion trackers + the 3 teardown sessions + certificate
  + WhatsApp group with weekly check-in prompts.
- **Pre-sell:** record Lessons 1–2 only, pre-sell at 50% off. 20+ buyers → record the rest.

---

## Lesson 1 — Self-audit: where is your energy going?

- **Outcome:** Student maps a week's energy and names the top 2 drains.
- **Cold-open hook:** "You don't have a time problem. You have an energy problem — and
  you've never once measured it."
- **Key points (→ `--point`):**
  1. Measure before you fix — you can't manage what you never tracked
  2. Energy is not time — a full day can leave you empty or full depending on what filled it
  3. Find the leaks — a few specific drains usually cost most of your week
- **Story (→ `--story`):** The week Tarun tracked his own energy and found the real drain wasn't work — it was the thing he'd never have guessed.
- **Companion material:** 📊 *Energy Audit Tracker* (tracker kit, moat #2) — a real
  one-week sheet: log energy by block, surface the drains.
- **🎥 Real systems teardown** (moat #1): Tarun walks through his *own* filled-in energy
  audit on screen — what it actually looked like, what surprised him.
- **Do-this-now:** Track energy for one week in the sheet; circle the top 2 drains.
- **Repurpose hooks:**
  - YT Short: "You don't have a time problem. Watch this."
  - IG carousel: "How to audit your energy in one week (free tracker)"
  - X thread: "I tracked my energy like a dataset for a week. The biggest drain shocked me ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche life \
    --title "Self-audit: where is your energy actually going" \
    --point "Measure before you fix — you can't manage what you never tracked" \
    --point "Energy is not time — what fills the day decides how you end it" \
    --point "Find the leaks — a few specific drains cost most of your week" \
    --story "The week I tracked my own energy and the real drain wasn't what I expected"
  python3 scripts/generate_course_worksheet.py --niche life \
    --topic "Auditing where your energy goes in a week" \
    --objective "map a week's energy and name the top 2 drains"
  ```

---

## Lesson 2 — Habit design: the science and the feeling

- **Outcome:** Student designs one keystone habit with a trigger.
- **Cold-open hook:** "Motivation is a feeling. It leaves. A habit is a design — and you
  can engineer it so it doesn't need you to feel like it."
- **Key points:**
  1. Cue → routine → reward — every habit is a loop you can build on purpose
  2. Make it small — embarrassingly small beats ambitiously abandoned
  3. Design the environment — willpower loses; surroundings win
- **Story (→ `--story`):** The tiny habit Tarun engineered with one trigger that quietly held for years when big resolutions didn't.
- **Companion material:** 📊 *Keystone Habit Designer* (tracker kit, moat #2) — fill the
  cue, the smallest routine, the reward, and the environment change.
- **Do-this-now:** Design one keystone habit; set its trigger today.
- **Repurpose hooks:**
  - YT Short: "Stop relying on motivation. Design this instead."
  - IG carousel: "Build one habit that sticks — the cue/routine/reward template"
  - X thread: "Big resolutions died. One embarrassingly small habit held for years. Here's the design ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche life \
    --title "Habit design: the science and the feeling" \
    --point "Cue, routine, reward — every habit is a loop you can build on purpose" \
    --point "Make it small — embarrassingly small beats ambitiously abandoned" \
    --point "Design the environment — willpower loses, surroundings win" \
    --story "The tiny habit with one trigger that held for years when big resolutions didn't"
  python3 scripts/generate_course_worksheet.py --niche life \
    --topic "Designing one keystone habit that sticks" \
    --objective "design one keystone habit with a trigger"
  ```

---

## Lesson 3 — Mental health maintenance, not crisis management

- **Outcome:** Student builds a 2-minute daily check-in.
- **Cold-open hook:** "Nobody waits for the building to burn before checking the smoke
  alarm. So why do we wait for a breakdown to check on ourselves?"
- **Key points:**
  1. Daily upkeep beats rescue — small maintenance prevents big crises
  2. Catch the early signals before they become emergencies
  3. Openness over stigma — naming it is strength, not weakness
- **Story (→ `--story`):** The early signal Tarun learned to read in himself, and the 2-minute check that now catches it before it grows.
- **Companion material:** 📊 *2-Minute Daily Check-In Card* (tracker kit, moat #2) — a few
  honest questions to run each day.
- **🎥 Real systems teardown** (moat #1): Tarun shows his *own* check-in practice — what he
  actually asks himself, how it sounds when he's honest.
- **Do-this-now:** Run the 2-minute check-in tonight; note one early signal.
- **Repurpose hooks:**
  - YT Short: "Mental health is maintenance, not rescue. 2 minutes a day."
  - IG carousel: "A 2-minute daily check-in (the questions)"
  - X thread: "We wait for the breakdown to check on ourselves. The daily upkeep nobody teaches ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche life \
    --title "Mental health maintenance, not crisis management" \
    --point "Daily upkeep beats rescue — small maintenance prevents big crises" \
    --point "Catch the early signals before they become emergencies" \
    --point "Openness over stigma — naming it is strength, not weakness" \
    --story "The early signal I learned to read in myself and the 2-minute check that catches it"
  python3 scripts/generate_course_worksheet.py --niche life \
    --topic "Daily mental-health upkeep for students" \
    --objective "build a 2-minute daily check-in"
  ```

---

## Lesson 4 — Dealing with pressure (academic + family + career)

- **Outcome:** Student sorts current pressures into control / no-control.
- **Cold-open hook:** "Half of what's crushing you, you can't change. The other half you
  can. Most people spend all their energy on the wrong half."
- **Key points:**
  1. Separate signal from noise — not every pressure deserves your energy
  2. Spend effort only on what you control — the rest is weather
  3. Boundaries are a system, not a confrontation
- **Story (→ `--story`):** The family/academic pressure Tarun stopped fighting once he sorted what was actually his to control — built for the Indian student reality (moat #3).
- **Companion material:** *Control / No-Control Sorter* — list every current pressure, sort
  it, decide one action for the controllables.
- **Do-this-now:** Sort your current pressures; pick one controllable to act on.
- **Repurpose hooks:**
  - YT Short: "Half your stress isn't yours to fix. Sort it like this."
  - IG carousel: "Academic + family + career pressure — the control/no-control sort"
  - X thread: "Indian student pressure is real. The sort that stopped me drowning in it ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche life \
    --title "Dealing with academic, family and career pressure" \
    --point "Separate signal from noise — not every pressure deserves your energy" \
    --point "Spend effort only on what you control — the rest is weather" \
    --point "Boundaries are a system, not a confrontation" \
    --story "The family and academic pressure I stopped fighting once I sorted what was mine to control"
  python3 scripts/generate_course_worksheet.py --niche life \
    --topic "Sorting pressure into what you control and what you don't" \
    --objective "sort current pressures into control / no-control"
  ```

---

## Lesson 5 — Building review loops (weekly, monthly)

- **Outcome:** Student sets up a 10-minute weekly review.
- **Cold-open hook:** "What gets reviewed gets better. What doesn't, drifts. A life with no
  review loop is just hoping."
- **Key points:**
  1. What gets reviewed gets better — attention is the upgrade
  2. Keep the cadence light — a heavy review is a review you'll skip
  3. Adjust, don't restart — tune the system instead of scrapping it
- **Story (→ `--story`):** The 10-minute weekly review Tarun has actually kept for years, and the one question that does most of the work.
- **Companion material:** 📊 *10-Minute Weekly Review Template* (tracker kit, moat #2) — the
  few prompts, the cadence, where it lives.
- **🎥 Real systems teardown** (moat #1): Tarun runs his *real* weekly review on screen —
  the actual entries, the messy honest version.
- **Do-this-now:** Run your first 10-minute weekly review this week.
- **Repurpose hooks:**
  - YT Short: "10 minutes a week beats every productivity app. Here's the review."
  - IG carousel: "The 10-minute weekly review (template inside)"
  - X thread: "I've kept a 10-minute weekly review for years. The one question that does the work ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche life \
    --title "Building review loops that keep your life on track" \
    --point "What gets reviewed gets better — attention is the upgrade" \
    --point "Keep the cadence light — a heavy review is one you'll skip" \
    --point "Adjust, don't restart — tune the system instead of scrapping it" \
    --story "The 10-minute weekly review I've kept for years and the one question that does the work"
  python3 scripts/generate_course_worksheet.py --niche life \
    --topic "A light weekly review loop" \
    --objective "set up a 10-minute weekly review"
  ```

---

## Lesson 6 — Attention in a distracting world

- **Outcome:** Student builds one distraction-free block into their day.
- **Cold-open hook:** "Your focus isn't weak. It's outgunned. You're fighting apps built by
  thousands of engineers to win — so stop fighting and redesign the field."
- **Key points:**
  1. Design the environment, not the willpower — remove the fight before it starts
  2. Your phone and feeds are systems — beat them with systems, not guilt
  3. Protect one deep block — one real hour beats a scattered day
- **Story (→ `--story`):** The single change to Tarun's environment that bought back one focused hour a day without any extra discipline.
- **Companion material:** 📊 *Deep-Block Planner* (tracker kit, moat #2) — pick the block,
  the environment changes, the phone rule.
- **Do-this-now:** Build one distraction-free block into tomorrow.
- **Repurpose hooks:**
  - YT Short: "Your focus isn't weak. It's outgunned. Fix the field."
  - IG carousel: "Protect one deep hour a day (the setup)"
  - X thread: "Apps built by thousands of engineers beat your willpower. Beat them with a system ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche life \
    --title "Holding attention in a world built to distract you" \
    --point "Design the environment, not the willpower — remove the fight before it starts" \
    --point "Your phone and feeds are systems — beat them with systems, not guilt" \
    --point "Protect one deep block — one real hour beats a scattered day" \
    --story "The single environment change that bought back one focused hour a day"
  python3 scripts/generate_course_worksheet.py --niche life \
    --topic "Designing attention in a distracting world" \
    --objective "build one distraction-free block into your day"
  ```

---

## Lesson 7 — Systems over goals: the long game

- **Outcome:** Student rewrites one goal as a repeatable system.
- **Cold-open hook:** "Goals are a finish line you cross once. A system is who you become.
  Bet on the second one."
- **Key points:**
  1. Identity over outcome — become the kind of person, don't just chase the win
  2. Build systems that survive bad days — motivation won't be there; the system will
  3. Play the long game — small repeatable beats big and brief
- **Story (→ `--story`):** The goal Tarun kept failing until he rewrote it as a system, and how the result showed up almost by accident.
- **Companion material:** *Goal → System Rewriter* — take one goal, convert it to a
  repeatable practice with a cadence and an identity statement.
- **Do-this-now:** Rewrite one current goal as a system you can repeat on a bad day.
- **Repurpose hooks:**
  - YT Short: "Stop setting goals. Become the system instead."
  - IG carousel: "Turn any goal into a system (the rewrite)"
  - X thread: "I kept failing the same goal. Rewriting it as a system changed everything ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche life \
    --title "Systems over goals: playing the long game" \
    --point "Identity over outcome — become the kind of person, don't just chase the win" \
    --point "Build systems that survive bad days — the system shows up when motivation won't" \
    --point "Play the long game — small repeatable beats big and brief" \
    --story "The goal I kept failing until I rewrote it as a system, and the result that showed up almost by accident"
  python3 scripts/generate_course_worksheet.py --niche life \
    --topic "Turning goals into repeatable systems" \
    --objective "rewrite one goal as a repeatable system"
  ```

---

## Companion material — production notes

| Type | Lessons | How to make | Status |
|------|---------|-------------|--------|
| 📊 Tracker / template (kit, moat #2) | 1, 2, 5, 6 | hand-authored CSV masters in `templates/` | ✓ 4 built (`templates/`) |
| Reflection / sorter worksheet | 3, 4, 7 | `generate_course_worksheet.py --niche life` | ✓ 7 built (`worksheets/`) |
| **🎥 Real systems teardown** (moat #1) | 1, 3, 5 | Screen-record Tarun's *own* tracker/check-in/review — real, unpolished | ⏳ record-only |

**Produced asset masters** (editable, in repo, bundle into the Graphy *Systems Kit*):
- `templates/energy_audit_tracker.csv` (L1, daily) · `keystone_habit_designer.csv` (L2, weekly) ·
  `weekly_review_template.csv` (L5, weekly) · `deep_block_planner.csv` (L6, weekly).
- `templates/systems_kit_guide.md` — column meanings, the worksheet rule each tracker encodes,
  and how to import to Google Sheets / Notion.

The 3 real systems-teardown sessions are the one remaining moat — they cost recording time once
and can't be faked from stock advice. Keep the CSV masters in repo; link one polished live
Sheet/Notion copy in Graphy.

## Repurposing — paid lesson → free funnel

Per lesson: 3 teaser formats (Short / carousel / thread) = **21 free assets** across 7
lessons feeding @breathoflife_ + Substack + IG + X. Rules:
- Teasers give the hook and one insight, never the full system — they sell the depth.
- Every teaser ends with a soft CTA to the course (link in bio / description / pinned).
- Free Lesson 1 video is the email-gated lead magnet; teasers route cold → Lesson 1 → paid.
- Generate teasers with the existing derivative pipeline once a lesson is recorded.

## Next actions

1. Tarun: review/edit this outline — swap hooks, stories, moats.
2. Draft Lessons 1–2 scripts + trackers (pre-sell pair). Commands above.
3. Personalise `[PERSONAL_*]` markers, record, edit (see `docs/course-production-guide.md`).
4. ✓ DONE — *Systems Kit* trackers (L1/2/5/6) built as CSV masters + guide in `templates/`.
   Polish one into a live Notion/Sheet and link it in Graphy.
5. Record the 3 real systems-teardown sessions (moat #1: L1, L3, L5).
6. Create Graphy shell; fill `graphy_course_id` + `enrol_url` into `data/courses/graphy_config.yaml`.
7. After recording, generate per-lesson social teasers to drive sales.
