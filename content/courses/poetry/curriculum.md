# Write Like You Mean It: Poetry for People Who Think They Can't

**Niche flag:** `poetry` · **Audience:** Creative students, 16–25
**Format:** Video with Tarun reading + original writing prompts · **Certificate:** Yes
**Funnel:** @breathofpoetry → course · **Launch price:** ₹99 (later ₹299–₹399)

**Angle:** Poetry isn't for literature students. It's for anyone who feels things
and doesn't know how to say them. Tarun's personal voice is the differentiator.

> All lessons ORIGINAL. No repurposing of blogs/YouTube scripts. Separate product line.
> Lowest-effort course (6 lessons) — launch last.

## Modules (5–7 lessons — Tarun owns final list)

| # | Lesson | Key points (seed for `draft_lesson_script.py`) | Prompt-sheet objective |
|---|--------|-----------------------------------------------|------------------------|
| 1 | Why expressing yourself matters now | Naming a feeling changes it · you don't need permission · start ugly | Write 3 honest lines, no editing |
| 2 | Observation — the poet's first skill | Notice small things · concrete > abstract · the detail carries the feeling | Capture one scene in 5 concrete images |
| 3 | Writing your first honest poem | Truth over rhyme · cut to the real line · short is fine | Turn one observation into a short poem |
| 4 | Finding your voice (not copying anyone) | Your words, your rhythm · steal structure not soul · sound like you | Rewrite a poem in only your own words |
| 5 | Sharing without shame | Fear is normal · share to one person first · feedback ≠ verdict | Share one poem and note what you felt |
| 6 | Keeping the practice alive | Beat the blank page · a tiny daily ritual · where to go from here | Set a 5-minute daily writing ritual you'll actually keep |

## Production

- Draft: `python3 scripts/draft_lesson_script.py --niche poetry --title "…" --point "…" --point "…" --point "…" --story "…"`
- Prompt sheet: `python3 scripts/generate_course_worksheet.py --niche poetry --topic "…" --objective "…"`
  (poetry sheets save to `content/courses/poetry/prompts/`)
- See `docs/course-production-guide.md` for the full recording → Graphy workflow.
