---
title: "IG Reel Script — DS/Tech · \"117 tokens bring back Fable 5\""
type: reel
niche: data_science_tech
date: 2026-07-13
week: 2026-W29
slug: tech-fable-mode-plugin
platform: ig
tags: [content/reel, niche/data_science_tech, week/2026-W29]
---
# IG Reel Script — DS/Tech · "117 tokens bring back Fable 5"

> **Source:** github.com/tarunlnmiit/fable-mode (shipped 2026-07-12) — no source blog; news-timed build-in-public reel.
> **Formula:** `data/kb/viral_reel_formula.md` (5-beat) + `data/kb/reels/08_carousel_reel_formula.md` hook rules. Caption per `data/kb/reels/06_mavgpt_caption_formula.md` (caption IS the product). **LOCAL ONLY — do not commit.**
> **Length target:** ~38s. Format: 9:16 talking-head + terminal screen-record B-roll.
> **CTA:** keyword **FABLE** → auto-DM repo link (UTM-tagged). Repo link also pinned in first comment.
> **News peg:** Fable 5 leaves Claude subscriptions 2026-07-13 — post same day, morning slot.

---

## Hook — 5 variants (08 §hook-polish: write 5, pick best)

1. ✅ **PICK (user-locked)** — "117 tokens bring back Fable 5. Anthropic just pulled it from subscriptions." *(Number-first two-punch: cost-curiosity + live news inside 3s)*
2. "Fable 5 just vanished from Claude subscriptions. I distilled its behavior into 117 tokens." *(News-first, authority)*
3. "117 tokens. That's all it takes to keep Fable 5's behavior — even after it leaves your plan."
4. "The real reason Fable 5 felt smarter wasn't raw intelligence. It was discipline — and discipline survives the paywall."
5. "Anthropic pulled Fable 5 from subscriptions. 117 tokens make Claude behave like it never left."

**Driver:** Number/Result + News. Honesty note: hook says "bring back Fable 5" — beat 3 immediately scopes it to *behavior*, on-screen hook text says BEHAVIOR explicitly. First frame = hook burned in, hard cut, no warm-up.

---

## 5-Beat Script

### BEAT 1 — HOOK (0–3s)
- **VO:** "One hundred seventeen tokens bring back Fable 5. Anthropic just pulled it from subscriptions."
- **On-screen (burn-in):** `117 TOKENS → FABLE 5 BEHAVIOR, BACK`
- **Cue:** Face to camera, hard cut in. Re-record 5×, keep the sharpest.

### BEAT 2 — PROBLEM (3–9s)
- **VO:** "If you code with Claude, your plan just lost its smartest model. And the answers you get now feel wordier, more timid, and half-checked."
- **On-screen:** `wordy · asks permission · "should work" ✅` *(strikethrough on the fake checkmark)*
- **Cue:** B-roll: side-by-side chat — rambling preamble answer vs. one-line fix answer.

### BEAT 3 — REVEAL + PROOF (9–27s) — *screen-record, real terminal*
- **VO:** "Here's the thing: most of what made Fable feel different wasn't raw intelligence. It was discipline. Lead with the answer. Cover the whole request. Act instead of asking permission. Never claim untested code works. So I distilled that into a free open-source plugin: fable-mode. Two commands. It injects the ruleset into every session — one hundred seventeen tokens — and Sonnet, Opus, even Haiku pick up the habits."
- **On-screen / B-roll sequence (3–5s clips, zoomed for mobile):**
  1. `/plugin marketplace add tarunlnmiit/fable-mode`
  2. `/plugin install fable-mode@fable-mode`
  3. New session → `FABLE MODE ACTIVE` visible in context
  4. Before/after answer: "Would you like me to fix it?" → "Fixed. Root cause was X. Tests pass."
- **Cue:** `CodeAnnotation` over the two commands; burn-in single words: `DISCIPLINE` · `2 COMMANDS` · `117 TOKENS`.

### BEAT 4 — PAYOFF (27–33s)
- **VO:** "Same subscription. Same models. Fable-class answers. And on the hard problems, it even offers to pull in a stronger model for advice."
- **On-screen:** `Same plan. Fable-class discipline.`
- **Cue:** Back to face, confident.

### BEAT 5 — CTA (33–38s)
- **VO:** "It's free, open source, no catch. Comment FABLE and I'll DM you the repo. The install commands are in the caption too."
- **On-screen:** `Comment "FABLE" → repo in your DMs · commands in caption ↓`
- **Loop:** end frame = the `FABLE MODE ACTIVE` terminal shot (result, not "bye") → invites rewatch.

---

## Caption (06 formula — the caption IS the product)

Comment "FABLE" and I'll send you the plugin link 👆

Fable 5 left Claude subscriptions today — this free 117-token plugin keeps its behavior on Sonnet, Opus, and Haiku.

Install (Claude Code):
1. /plugin marketplace add tarunlnmiit/fable-mode
2. /plugin install fable-mode@fable-mode

The 5 Fable habits it installs:
1. Lead with the outcome — answer first, reasoning after
2. Cover the whole request — trace every consumer before calling it done
3. Act, don't ask — no "shall I proceed?" on reversible work
4. Simplest solution that works — no over-engineering
5. Never claim untested code works — "written, not run" honesty

Bonus: on hard problems, Sonnet/Haiku offer to consult a stronger model, then do the work themselves.

Free · open source · MIT. Not the model's raw intelligence — its discipline. That part was always copyable.

#claude #ai #claudecode #anthropic #datascience

**Keyword:** FABLE
**DM payload:** https://github.com/tarunlnmiit/fable-mode?utm_source=instagram&utm_medium=reel&utm_campaign=fable-mode-launch
**Pinned first comment:** Repo (free, MIT): same UTM link + "Comment FABLE if the DM tool misses you."

## Thumbnail text (06 formula — outcome, not topic)

`Fable 5 just LEFT Claude 😳 117 tokens keep its behavior`
Alt: `Anthropic pulled its best model. I kept its brain's habits — 117 tokens 🤯`

## YT Shorts delta

Same footage. CTA line swap: "Repo's in the description — it's free. Subscribe for the follow-up." Link = first line of description + pinned comment. `#Shorts` in title.

## Checklist (viral_reel_formula §per-reel)
- [ ] Hook recorded 5×, winner picked
- [ ] Terminal B-roll captured: 2 install commands, FABLE MODE ACTIVE, before/after answer (zoomed)
- [ ] Captions burned in word-by-word; no clip > 4s; ~150 wpm
- [ ] Honesty guardrail: hook's "bring back Fable 5" scoped to BEHAVIOR on-screen + in beat 3; "117 tokens" is the measured `claude plugin details` number; no intelligence-parity claim
- [ ] Comment→DM tool armed with keyword FABLE + UTM link
- [ ] Loop ends on FABLE MODE ACTIVE frame
