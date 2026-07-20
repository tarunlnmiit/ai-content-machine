---
title: "Raw-Session Lane — record once, everything else automated"
type: doc
slug: raw-session-lane
tags: [content/doc]
---
# Raw-Session Lane — record once, everything else automated

Added 2026-07-12. The primary video lane: unscripted Q&A on green screen →
per-question clips → composited → trimmed → reels + long-form episode.
Replaces scripted-talking-head-from-blog (robotic, killed watch time).

## Recording protocol (the whole trick)

1. Open `content/sessions/{week}/teleprompter.html` (arrow keys, one question per slide).
2. Per question: **pause ~3 seconds → read the question aloud, word for word → answer raw.**
   The spoken question is BOTH the slice marker and the reel hook.
3. Answer raw: **one thought per answer, aim 60–120s.** One spoken question = one
   clip = one self-contained short (the question is the hook) — don't chain
   multiple thoughts onto one question.
4. Redo an answer: pause ~2s, re-read the question, start over. Last take wins.
5. Questions are read **verbatim in English** — non-negotiable, it's the slicer
   marker. Answers may **freely code-switch English/Hinglish** — say it as it
   actually comes out (amends the 2026-07-12 "all English" decision: English-only
   applies to question markers + captions/metadata, not answer speech). Whisper
   stays `language="en"` (`video_trim.py:213`) — Hinglish transcribes romanized,
   English markers stay matchable. Green screen, fixed framing, same setup weekly.
6. Batch sitting (60–90 min, 6–8 questions) or ad-hoc single questions — same rule.
   Drop recordings in `assets/raw/inbox/`.

## Topic sources

Topics feed the prompt pack from four sources, in priority order (highest first):

1. **Inbox** — `data/ideas/thought_inbox.md` has three sections: `## thoughts`
   (your own raw thoughts, one bullet/line, append anytime) and `## audience`
   (pasted IG/YT comments) feed a single Sonnet call that converts them into
   English spoken-question hooks and assigns each a niche (life/ds). Used
   bullets move to `## consumed / ### {week}` on a successful pack generation;
   unused bullets stay for next week.
2. **Provocations** — 2-3 Claude-generated thought-provoking questions seeded
   by the thesis "I debug life like I debug systems" + `data/analytics/weekly_insights.md`.
3. **Rotation** — `data/kb/raw_take_questions.json` (`q_en` field, week-rotated).
4. **Generated** — niche sections of `data/ideas/weekly_ideas.md`.

Sources 3–4 fill remaining slots after 1–2 are placed. Duplicates (`SequenceMatcher`
similarity > 0.85) are dropped, then the pack is truncated to `--pack-size`
(default 8). Every question in `prompt_pack.json` carries a `source` field:
`inbox` / `audience` / `provocation` / `rotation` / `generated`.

New flags on `generate_prompt_pack.py`: `--pack-size` (max questions in the
final pack) and `--inbox` (path to `thought_inbox.md`, defaults to the repo location).

**Gotcha:** default `--pack-size 8` means rotation/generated fill questions
(poetry/DS) often get truncated when the inbox is full. Bump `--pack-size` or
lower `--n-life` when the DS episode needs more DS questions.

## Pipeline

| Step | Command | Output |
|---|---|---|
| 0. Prompt pack (Sunday, automated) | `python3 scripts/generate_prompt_pack.py` | `content/sessions/{week}/prompt_pack.json` + `teleprompter.html` |
| 1. Slice | `python3 scripts/slice_raw_session.py --input "assets/raw/inbox/<f>" --week <W>` | `clips/qNN.mp4` + `session_manifest.json` |
| 2. Composite | `python3 scripts/composite_greenscreen.py --input <clip> --niche <n>` | `qNN_composited.mp4` (key params cached per background) |
| 3. Trim | `python3 scripts/video_trim.py --raw <clip> --niche <n> --out <...>` | silences/retakes/fillers removed |
| 4. Reels (3–4 best) | `run_video_pipeline.py` phases 3–6 + `embedded-captions` (anchor, English) | `output/review/{week}/reels/` |
| 5. Episode | `python3 scripts/assemble_episode.py --week <W> --niche <n>` | `output/review/{week}/episode_{niche}.mp4` + `_meta.md` (titles, chapters, channel) |
| 6. Thumbnails | `generate_thumbnail.py` (face+outcome text) | `output/review/{week}/thumbnails/` |

Nothing publishes from this lane — human approves in `output/review/{week}/`,
then runbook `30-publish.md` ships it.

## Assets

- Studio backgrounds: `assets/brand/backgrounds/{ds,life,poetry}_studio[_portrait].png`
  (graded stock stills, sources in `sources.json`; key params cache in `*.keyparams.json`).
- Question bank: `data/kb/raw_take_questions.json` (28 questions, `q_en` English field,
  theme-tagged, week-rotated).

## Episode routing

life → Breath of Life (@breathoflife_) · poetry → Breath of Poetry (@breathofpoetry) ·
ds → Breath of Data Science (@breathofdatascience).

## Failure notes

- Slicer matches <50% of questions → protocol drift (question not read verbatim);
  don't lower `--min-score` below 0.6, fix the recording habit.
- Greenscreen gates in `composite_greenscreen.py`; interactive diagnosis via the
  `/greenscreen-composite` command. blend ≤0.05 always; ffmpeg keys, never Palmier key.chroma.
- Runbooks for non-Fable models: `docs/runbooks/` (20-process-session covers this lane).

## Operate via dashboard

`python3 scripts/dashboard.py` → http://localhost:8765 — the whole lane (prep →
menu → record protocol → slice/composite/trim → episode → review/approve) as one
self-explanatory page. Publishing intentionally excluded (runbook 30 after approval).
