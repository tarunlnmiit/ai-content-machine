---
title: "IG Reel Script — DS · \"Python added 28 and 35. It got 2835.\""
type: reel
niche: data_science_tech
date: 2026-05-25
week: 2026-W22
slug: python-for-data-science-tutorial-210
platform: ig
tags: [content/reel, niche/data_science_tech, week/2026-W22]
---
# IG Reel Script — DS · "Python added 28 and 35. It got 2835."

> **Source blog:** `content/blogs/2026-W22/2026-05-25_data_science_tech_python-for-data-science-tutorial-210.md`
> **Formula:** `data/kb/reels/08_carousel_reel_formula.md` (AUTHORITATIVE — governs hook/structure/tone/CTA; CLAUDE.md VOICE/BANNED-WORDS overridden where they conflict; honesty guardrail holds). **LOCAL ONLY — do not commit.**
> **Length target:** ~30s (a few seconds over is fine). Format: 9:16 talking-head + screen recording (terminal/Python REPL).
> **Worksheet CTA:** keyword **AUDIT** → auto-DM. Link pinned in first comment (never caption body).

---

## Hook — 5 variants (08 §hook-polish: write 5, pick best)

1. ✅ **PICK** — "I asked Python to add 28 and 35. It gave me 2835 — and never once complained." *(Curiosity + open loop: how does that not error out?)*
2. "Your analysis will give you a wrong answer someday. Not a crash. A perfectly confident wrong number." *(Storytelling / dread — straight from the blog's hook)*
3. "Nobody tells beginners this: Python's most dangerous bug never throws an error." *("Nobody tells you" driver)*
4. "Stop trusting `sum()` on a CSV column until you've run one check first." *(Contrarian / warning)*
5. "The bug that quietly ruins data science reports looks exactly like correct code." *(Curiosity)*

**Driver:** Curiosity + open loop, closed at the payoff. First frame = hook caption burned in over the `2835` output, hard cut, no intro.

---

## 4-Beat Script

### BEAT 1 — HOOK (0–4s)
- **VO:** "I asked Python to add 28 and 35. It gave me 2835 — and never once complained."
- **On-screen (burn-in):** `"28" + "35" = "2835"` — no error
- **Cue:** Face to camera, hard cut in. No "hey guys."

### BEAT 2 — PROBLEM (4–10s)
- **VO:** "Your analysis will give you a wrong answer someday. Not a crash — a perfectly confident wrong number. It happens the moment a number column gets loaded as text."
- **On-screen:** `Wrong answer ≠ error message`
- **Cue:** Quick B-roll — a CSV with an `age` column, values that look numeric but are quoted strings.

### BEAT 3 — VALUE / PROOF (10–22s) — *show it, don't tell*
- **VO:** "Watch: two strings, `'28'` plus `'35'`, Python concatenates them — twenty-eight thirty-five. It's not adding, it's gluing text. One line fixes it: `int()` converts the string to a real number first. Same values, `int("28") + int("35")`, now it's sixty-three."
- **On-screen (screen recording):** Python REPL — `print("28" + "35")` → `2835` highlighted red, then `print(int("28") + int("35"))` → `63` highlighted green.
- **Cue:** SCREEN capture is the proof beat. Real output, no mockup.

### BEAT 4 — PAYOFF + CTA (22–30s)
- **VO (payoff):** "Any number from a CSV, an API, or a form is a string until you convert it. Check the type before you trust the sum."
- **On-screen:** `type() before you trust the total`
- **VO (CTA):** "I put this exact type-check habit — plus the list, dict, and function patterns that make it stick — in a free worksheet. Comment **AUDIT** and I'll DM it to you."
- **On-screen:** `Comment "AUDIT" → free worksheet in your DMs`

---

## Caption (side-notes live here, VO stays lean)

Every silent bug in data analysis traces back to the same root: not knowing what kind of thing you're actually holding.

I've watched a numeric-looking CSV column get summed as text and hand back a confident, wrong answer — no error, no warning, just a number that looked plausible enough to ship.

The fix is one habit: `type()` before you trust anything, `int()` / `float()` / `str()` to convert deliberately instead of hoping Python guessed right.

This is tutorial 2 of a Python-for-data-science series — types, lists, dicts, and functions, the four things every pipeline is actually built on, before you ever touch Pandas.

Comment **AUDIT** for the free worksheet — run this type-check on your own last analysis. 👇

**Keyword:** AUDIT
**Pinned first comment:** Free worksheet — "The Silent Bug Audit: Catch Type Errors Before They Poison Your Analysis": https://worksheets-thebreathnetwork.vercel.app/get-worksheet/python-for-data-science-tutorial-210

#datascience #python #learntocode #dataanalysis

## Retention devices used (08 §retention)
- Open loop in hook ("never once complained" — how does that not error?) → closed in Beat 3's fix.
- One idea per beat; hard cut between problem and proof.
- Proof beat = real screen recording (REPL output), not narration.
- CTA references the exact thing just watched (the type-check habit), not a vague offer to help.
- Honesty guardrail: every claim matches the blog — real Python behavior, no invented feature; worksheet delivers what's promised, nothing more.

## Checklist
- [ ] Hook recorded 5×, pick the clearest/flattest delivery
- [ ] Screen recording: REPL showing `"28"+"35"` → `2835` then `int()` fix → `63`, high-contrast burn-in captions
- [ ] Comment→DM tool armed with keyword AUDIT + worksheet link; keyword pinned in first comment only
- [ ] No overclaim: worksheet covers type-check + list/dict/function habits, not a full course
