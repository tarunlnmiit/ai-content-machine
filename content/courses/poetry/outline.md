# Poetry Course Outline — "Write Like You Mean It: Poetry for People Who Think They Can't"

**Niche flag:** `poetry` · **Funnel:** @breathofpoetry → course
**Audience:** Creative students, 16–25 (Indian market)
**Format:** Video with Tarun reading + writing on camera (6–10 min).
**Launch price:** ₹99 (early-bird first 50; later ₹299–₹399). Lowest-effort course — launch last.
**Promise:** Poetry isn't for literature students. It's for anyone who feels things and
doesn't know how to say them. Tarun's personal voice is the differentiator.

> Every lesson is ORIGINAL (no repurposing of published blogs/YT scripts into the paid
> product). Repurposing flows the OTHER way: paid lessons → free social teasers that sell
> the course.

## Each lesson ships three layers

1. **Video** — the spoken lesson (drafted via `draft_lesson_script.py`, then personalised + recorded).
2. **Companion material** — a writing prompt sheet the student writes into (drafted via
   `generate_course_worksheet.py --niche poetry`, which saves to `content/courses/poetry/prompts/`).
3. **Repurpose hooks** — free social content derived from the lesson to drive course sales:
   a YT Short, an IG carousel/reel, an X thread. Free Lesson 1 is the email-gated lead magnet.

## Signature differentiators — what nobody else offers

Poetry courses are either academic (meter, form, dead poets) or absent. Nothing exists for
the person who feels a lot and is scared to write. Three moats make this different — each
leans on Tarun's real voice:

1. **🎥 Write-along sessions.** Tarun writes a poem from a blank page on camera — thinking
   aloud, crossing out lines, choosing the honest word over the clever one. Bundled with
   **L3, L4, L6**. Every other course shows finished poems; nobody shows the ugly draft.
   This *is* the demystification.
2. **📝 Original prompt deck.** Tarun's own starter lines and prompts — a deck students
   keep and return to whenever the page is blank. Powers the companion material across
   **all lessons**, anchored in **L1, L6**.
3. **Share-without-shame ritual.** A structured, safe weekly poem-share (WhatsApp) where
   feedback is never a verdict. The emotional safety is the product — built into **L5** and
   the community. Nobody sells the *courage*, only the technique.

These answer the gap: intimidating/academic → write-along shows it's messy and human;
blank-page fear → the prompt deck; too-scared-to-share → the share-without-shame ritual.

## Course arc

L1–2 = **permission + seeing** (why write at all, learn to observe). L3–4 = **make
something true** (first honest poem, find your own voice). L5–6 = **keep going** (share
without shame, build a lasting practice). The arc takes a student from "I can't write" →
"I have a voice and a practice I'll keep."

## Funnel logic

- **Free:** Lesson 1 full video (email gate) + 2–3 social teasers per lesson.
- **Paid:** Lessons 2–6 + the full prompt deck + the 3 write-along sessions + certificate
  + WhatsApp group for weekly poem sharing.
- **Pre-sell:** record Lessons 1–2 only, pre-sell at 50% off. 20+ buyers → record the rest.

---

## Lesson 1 — Why expressing yourself matters now

- **Outcome:** Student writes 3 honest lines with no editing.
- **Cold-open hook:** "You don't need to be a poet to write a poem. You just need to have
  felt something — and you have."
- **Key points (→ `--point`):**
  1. Naming a feeling changes it — the page is where the weight comes off
  2. You don't need permission, training, or talent to start
  3. Start ugly — the honest mess beats the polished nothing
- **Story (→ `--story`):** The first honest lines Tarun wrote that weren't "good" but changed something in him anyway.
- **Companion material:** 📝 *First Lines* prompt sheet (prompt deck, moat #2) — three
  openers that pull an honest line out of you.
- **Do-this-now:** Write 3 honest lines right now. Don't edit. Don't show anyone yet.
- **Repurpose hooks:**
  - YT Short: "You don't need to be a poet to write a poem. Try this."
  - IG carousel/reel: "Write 3 honest lines (no editing) — start here"
  - X thread: "Naming a feeling changes it. The 3 lines that started everything for me ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche poetry \
    --title "Why expressing yourself matters now" \
    --point "Naming a feeling changes it — the page is where the weight comes off" \
    --point "You don't need permission, training, or talent to start" \
    --point "Start ugly — the honest mess beats the polished nothing" \
    --story "The first honest lines I wrote that weren't good but changed something anyway"
  python3 scripts/generate_course_worksheet.py --niche poetry \
    --topic "Permission to write your first honest lines" \
    --objective "write 3 honest lines with no editing"
  ```

---

## Lesson 2 — Observation: the poet's first skill

- **Outcome:** Student captures one scene in 5 concrete images.
- **Cold-open hook:** "Poets aren't people who feel more. They're people who notice more.
  And noticing is a skill you can practise."
- **Key points:**
  1. Notice small things — the poem lives in the detail you almost walked past
  2. Concrete beats abstract — "chipped blue cup" not "sadness"
  3. The detail carries the feeling — show the thing, not the emotion
- **Story (→ `--story`):** The ordinary object Tarun noticed on a bad day that held the whole feeling without ever naming it.
- **Companion material:** 📝 *Five Images* prompt sheet (prompt deck, moat #2) — capture
  one scene as five concrete, sensory details.
- **Do-this-now:** Pick one scene around you; write 5 concrete images, no feelings named.
- **Repurpose hooks:**
  - YT Short: "Poets don't feel more. They notice more. Practise this."
  - IG carousel/reel: "Turn a feeling into 5 concrete images"
  - X thread: "'Sadness' is weak on the page. 'A chipped blue cup' isn't. Why detail carries feeling ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche poetry \
    --title "Observation: the poet's first skill" \
    --point "Notice small things — the poem lives in the detail you almost walked past" \
    --point "Concrete beats abstract — a chipped blue cup, not sadness" \
    --point "The detail carries the feeling — show the thing, not the emotion" \
    --story "The ordinary object I noticed on a bad day that held the whole feeling without naming it"
  python3 scripts/generate_course_worksheet.py --niche poetry \
    --topic "Observation and concrete imagery" \
    --objective "capture one scene in 5 concrete images"
  ```

---

## Lesson 3 — Writing your first honest poem

- **Outcome:** Student turns one observation into a short poem.
- **Cold-open hook:** "Forget rhyme. Forget rules. A real poem is just one true thing,
  said as plainly as you can bear."
- **Key points:**
  1. Truth over rhyme — never bend the honest line to make it rhyme
  2. Cut to the real line — find the one line that matters and trust it
  3. Short is fine — four true lines beat forty padded ones
- **Story (→ `--story`):** The poem Tarun cut from twenty lines to four, and how the four said everything the twenty couldn't.
- **Companion material:** 📝 *One True Thing* prompt sheet (prompt deck, moat #2) — take a
  Lesson-2 observation and shape it into a short poem.
- **🎥 Write-along session** (moat #1): Tarun writes a short poem from blank page on
  camera — thinking aloud, crossing lines out, choosing the honest word.
- **Do-this-now:** Turn one of your 5 images into a 4-line poem. Cut everything that isn't true.
- **Repurpose hooks:**
  - YT Short: "Watch me write a poem from nothing (and cross half of it out)."
  - IG carousel/reel: "Turn one observation into a 4-line poem"
  - X thread: "I cut this poem from 20 lines to 4. The 4 said everything ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche poetry \
    --title "Writing your first honest poem" \
    --point "Truth over rhyme — never bend the honest line to make it rhyme" \
    --point "Cut to the real line — find the one line that matters and trust it" \
    --point "Short is fine — four true lines beat forty padded ones" \
    --story "The poem I cut from twenty lines to four, and how the four said everything"
  python3 scripts/generate_course_worksheet.py --niche poetry \
    --topic "Shaping an observation into a short honest poem" \
    --objective "turn one observation into a short poem"
  ```

---

## Lesson 4 — Finding your voice (not copying anyone)

- **Outcome:** Student rewrites a poem in only their own words.
- **Cold-open hook:** "You already have a voice. It's the way you text your closest friend
  at 2am. Bring *that* to the page."
- **Key points:**
  1. Your words, your rhythm — write how you actually talk, not how poems "sound"
  2. Steal structure, not soul — borrow a shape, fill it with you
  3. Sound like you — the goal isn't impressive, it's unmistakably yours
- **Story (→ `--story`):** The moment Tarun stopped imitating poets he admired and a line came out that finally sounded like him.
- **Companion material:** 📝 *In Your Own Words* prompt sheet (prompt deck, moat #2) — take
  a poem (yours or a model's shape) and rewrite it in only your own language.
- **🎥 Write-along session** (moat #1): Tarun reworks a stiff, borrowed-sounding draft into
  his own voice on camera — the before and after, live.
- **Do-this-now:** Rewrite one poem using only words you'd actually say.
- **Repurpose hooks:**
  - YT Short: "Your voice is how you text at 2am. Bring that to the page."
  - IG carousel/reel: "Find your voice — steal structure, not soul"
  - X thread: "I spent years imitating poets I admired. The line that finally sounded like me ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche poetry \
    --title "Finding your voice without copying anyone" \
    --point "Your words, your rhythm — write how you actually talk, not how poems sound" \
    --point "Steal structure, not soul — borrow a shape, fill it with you" \
    --point "Sound like you — the goal isn't impressive, it's unmistakably yours" \
    --story "The moment I stopped imitating poets I admired and a line finally sounded like me"
  python3 scripts/generate_course_worksheet.py --niche poetry \
    --topic "Finding and trusting your own voice" \
    --objective "rewrite a poem in only your own words"
  ```

---

## Lesson 5 — Sharing without shame

- **Outcome:** Student shares one poem and notes what they felt.
- **Cold-open hook:** "The scariest part isn't writing it. It's letting one person read it.
  So let's make that one person safe."
- **Key points:**
  1. Fear is normal — every writer feels it; it never fully leaves, and that's fine
  2. Share to one person first — not the internet, not a crowd — one safe reader
  3. Feedback is not a verdict — a reaction is information, not a sentence on your worth
- **Story (→ `--story`):** The first time Tarun showed someone a poem, what he was terrified of, and what actually happened.
- **Companion material:** *Share-Without-Shame* guide (moat #3) — how to pick a safe first
  reader, what to ask for, and a note-card for what you felt after.
- **Do-this-now:** Share one poem with one safe person; write down what you felt.
- **Repurpose hooks:**
  - YT Short: "The scariest part of poetry isn't writing it. It's this."
  - IG carousel/reel: "How to share your first poem without the shame"
  - X thread: "The first time I showed someone a poem, I was terrified. What actually happened ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche poetry \
    --title "Sharing your writing without shame" \
    --point "Fear is normal — every writer feels it and it never fully leaves" \
    --point "Share to one person first — one safe reader, not a crowd" \
    --point "Feedback is not a verdict — a reaction is information, not a sentence on your worth" \
    --story "The first time I showed someone a poem, what I feared, and what actually happened"
  python3 scripts/generate_course_worksheet.py --niche poetry \
    --topic "Sharing your work without shame" \
    --objective "share one poem and note what you felt"
  ```

---

## Lesson 6 — Keeping the practice alive

- **Outcome:** Student sets a 5-minute daily writing ritual they'll actually keep.
- **Cold-open hook:** "The blank page wins when you treat writing as an event. Beat it by
  making it small, daily, and almost too easy to skip."
- **Key points:**
  1. Beat the blank page — a prompt and five minutes removes the excuse
  2. A tiny daily ritual beats rare bursts of inspiration
  3. Know where to go from here — keep the deck, keep the share, keep showing up
- **Story (→ `--story`):** The five-minute writing ritual Tarun kept on the days he had nothing, and how it carried him to the days he did.
- **Companion material:** 📝 *Daily Ritual* prompt deck (prompt deck, moat #2) — a stack of
  starters to pull from every day, plus a simple streak tracker.
- **🎥 Write-along session** (moat #1): Tarun does a real 5-minute write from a deck prompt
  on camera — proof that small and daily is enough.
- **Do-this-now:** Set your 5-minute daily writing ritual; do today's from the deck.
- **Repurpose hooks:**
  - YT Short: "Beat the blank page in 5 minutes a day. Watch."
  - IG carousel/reel: "A 5-minute daily writing ritual (with prompts)"
  - X thread: "I wrote 5 minutes a day even with nothing to say. It carried me to the days I did ↓"
- **Run:**
  ```bash
  python3 scripts/draft_lesson_script.py --niche poetry \
    --title "Keeping the writing practice alive" \
    --point "Beat the blank page — a prompt and five minutes removes the excuse" \
    --point "A tiny daily ritual beats rare bursts of inspiration" \
    --point "Know where to go from here — keep the deck, keep the share, keep showing up" \
    --story "The five-minute ritual I kept on the days I had nothing, and how it carried me to the days I did"
  python3 scripts/generate_course_worksheet.py --niche poetry \
    --topic "Building a daily writing ritual that lasts" \
    --objective "set a 5-minute daily writing ritual you'll actually keep"
  ```

---

## Companion material — production notes

| Type | Lessons | How to make | Status |
|------|---------|-------------|--------|
| 📝 Prompt sheet (prompt deck, moat #2) | 1, 2, 3, 4, 6 | `generate_course_worksheet.py --niche poetry` → `prompts/` | ✓ 7 built (`prompts/`) |
| Share-without-shame guide (moat #3) | 5 | `generate_course_worksheet.py --niche poetry` (guide form) | ✓ built (`prompts/`) |
| **🎥 Write-along session** (moat #1) | 3, 4, 6 | Screen/cam-record Tarun writing from blank page — unedited, crossing out lines | ⏳ record-only |

**Produced asset masters** (editable, in repo, one download in Graphy):
- `prompts/*_worksheet.md` — the 6 lesson sheets + a 40+-line `starter-lines-deck` sheet.
- `prompts/prompt_deck.md` — all sheets compiled into one deck with a title page + TOC.
  Rebuild any time: `python scripts/compile_prompt_deck.py --niche poetry`.

The 3 write-along sessions + the original deck are the moats — record once, can't be faked.

## Repurposing — paid lesson → free funnel

Per lesson: 3 teaser formats (Short / carousel-reel / thread) = **18 free assets** across 6
lessons feeding @breathofpoetry + IG + X — plus clips from the write-along sessions ("watch
a poem get written and half of it crossed out") as their own teaser class. Rules:
- Teasers give the hook and one insight, never the full lesson — they sell the depth.
- Every teaser ends with a soft CTA to the course (link in bio / description / pinned).
- Free Lesson 1 video is the email-gated lead magnet; teasers route cold → Lesson 1 → paid.
- Generate teasers with the existing derivative pipeline once a lesson is recorded.

## Next actions

1. Tarun: review/edit this outline — swap hooks, stories, moats.
2. Draft Lessons 1–2 scripts + prompt sheets (pre-sell pair). Commands above.
3. Personalise `[PERSONAL_*]` markers, record, edit (see `docs/course-production-guide.md`).
4. ✓ DONE — *Prompt Deck* built: 7 prompt sheets compiled into `prompts/prompt_deck.md`.
   Rebuild with `python scripts/compile_prompt_deck.py` after adding sheets.
5. Record the 3 write-along sessions (moat #1: L3, L4, L6).
6. Create Graphy shell; fill `graphy_course_id` + `enrol_url` into `data/courses/graphy_config.yaml`.
7. After recording, generate per-lesson social teasers to drive sales.
