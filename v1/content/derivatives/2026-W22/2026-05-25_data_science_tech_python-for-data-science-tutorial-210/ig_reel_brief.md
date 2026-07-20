---
title: "Instagram Reel Brief — Python Tutorial 2/10: Variables & Data Types"
type: derivative
niche: data_science_tech
week: 2026-W22
slug: ig-reel-brief
tags: [content/derivative, niche/data_science_tech, week/2026-W22]
---
# Instagram Reel Brief — Python Tutorial 2/10: Variables & Data Types

**Week:** 2026-W22
**Account:** @breathofdatascience
**Format:** tutorial-clip (screen recording + code walkthrough)

---

## Hooks (pick one — use as first spoken line AND as text overlay)

**Option 1:** Python gave me a perfectly confident wrong number. No error. No crash. I trusted it for a week.
> _The "silent bug" angle — specific consequence, no exaggeration. Strongest for DS audience._

**Option 2:** Your CSV loads fine. Python sums the column. You trust the number. Except it added "28" + "35" + "42" as text — and got "283542".
> _Concrete, reproducible scenario. Viewers who've seen this will share it immediately._

**Option 3:** I've never seen a Python error cause more damage than when it gave no error at all.
> _Irony-based hook. Works well as a text overlay over a terminal screen recording._

---

## Best clip timestamps

_Run clip_shorts.py to auto-identify. Manually, aim for:_
- `0:00 → 0:50` — Hook + the string concatenation demo (highest-value 50 seconds)
- `2:00 → 2:45` — The `type()` + `isinstance()` explanation with code
- `4:30 → 5:15` — The type conversion section (`int()`, `str()`, `float()`) as a "the fix" payoff

---

## Instagram caption

```
Python gave me a wrong answer once.

Not an error. Not a red squiggly line. A perfectly calculated, completely wrong number — and I trusted it in a report.

The column was labeled "age." Python loaded it as strings. When I summed it, it didn't add 28 + 35 + 42.

It concatenated them: "283542."

No warning. No crash. A number plausible enough to fool anyone.

This is Tutorial 2/10 of my Python for Data Science series. It covers the one concept every beginner skips that bites every data scientist eventually: types.

Comment TYPES and I'll send you the full post. 👇

#python #datascience #learnpython #pythontutorial #breathofdatascience
```

---

## DM keyword

`TYPES` — set this in SuperProfile/CreatorFlow as the trigger word.

---

## Production command

```bash
# 1. Cut clips from the edited W22 video
python3 scripts/clip_shorts.py \
  --slug 2026-05-25_data_science_tech_python-for-data-science-tutorial-210 \
  --count 3 \
  --smart-crop

# SRT already exists at:
# assets/video/edited/2026-W22/2026-05-25_data_science_tech_python-for-data-science-tutorial-210.srt

# 2. Clips output to:
#    assets/video/edited/shorts/2026-05-25_data_science_tech_python-for-data-science-tutorial-210_short_00.mp4

# 3. Add trending audio in CapCut or Instagram native editor before posting
```

---

## Posting note

Post the "string concatenation bug" clip first — it's the most relatable scenario and will earn the most saves from DS students. Use the "TYPES" keyword CTA to drive comments → algorithm signal.

---

_Edit hooks/caption to match your voice before posting._
