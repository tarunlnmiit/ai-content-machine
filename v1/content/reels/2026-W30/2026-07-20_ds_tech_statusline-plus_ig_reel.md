---
title: "IG Reel Script — DS/Tech · \"One line. Every number that matters.\""
type: reel
niche: data_science_tech
date: 2026-07-20
week: 2026-W30
slug: tech-statusline-plus
platform: ig
tags: [content/reel, niche/data_science_tech, week/2026-W30]
---
# IG Reel Script — DS/Tech · "One line. Every number that matters."

> **Source:** github.com/tarunlnmiit/statusline-plus — Claude Code plugin, not yet in `data/kb/projects.json` (add before scheduling a weekly cadence; this is a standalone launch reel). No source blog — news-timed build-in-public reel.
> **Formula:** `data/kb/viral_reel_formula.md` (5-beat) + `data/kb/reels/06_mavgpt_caption_formula.md` (caption IS the product).
> **Length target:** ~38s. Format: 9:16 talking-head + terminal screen-record B-roll.
> **CTA:** keyword **LINE** → auto-DM repo link (UTM-tagged, once wired). Repo link also pinned in first comment.
>
> **Production note (green screen):** Talking-head shot against a physical green screen, fixed framing, composited via `scripts/composite_greenscreen.py --input <clip> --niche ds` onto `assets/brand/backgrounds/ds_studio_portrait.png`. Shoot this and the inbox-to-action reel in the **same session, same setup** — one key calibration for both. Run a ~5s test-key through the composite script and check edges/wardrobe spill *before* the real takes. Keep framing/lighting identical across all takes, including the 5 hook re-records. Beat 3's terminal footage is captured separately (no greenscreen constraints).

---

## Hook — 5 variants (pick winner after cold rewatch)

1. ✅ **PICK (suggested)** — "I was blind to my own cost and rate limits until I built this one line." *(Personal stakes + result)*
2. "Claude Code doesn't tell you your cost, your rate limit, or your git branch — until you build this." *(Problem-first, specific gaps)*
3. "One `jq` pass. One line. Model, cost, context, rate limits, git branch — all of it." *(Data/Mechanism, concrete list)*
4. "I kept hitting my 5-hour limit blind. So I built a status line that never lets that happen again." *(Story + pain)*
5. "Three themes. One status line. Everything Claude Code hides from you by default." *(Contrarian — default is hiding info)*

**Driver:** Personal stakes + result. Honesty note: hook says "one line" — beat 3 must show the actual rendered status line on-screen (not a mockup), and the "single jq pass" claim needs the real script/theme file visible.

---

## 5-Beat Script

### BEAT 1 — HOOK (0–3s)
- **VO:** "I couldn't see my cost or rate limits — so I built this one line."
- **On-screen (burn-in):** `1 LINE → COST · LIMITS · BRANCH · CONTEXT`
- **Cue:** Face to camera, hard cut in. Deliver straight to lens — don't point or gesture at "this one line," the referent doesn't exist yet on a flat green backdrop; the burn-in carries that job. Re-record 5×, keep the sharpest.

### BEAT 2 — PROBLEM (3–8s)
- **VO:** "You're deep in a session. No idea how close you are to your limit. No idea what it's costing you. No idea which branch you're even on."
- **On-screen:** `cost? · rate limit? · branch? · ¯\_(ツ)_/¯`
- **Cue:** B-roll: default terminal, bare prompt, no status line — feels empty next to what's coming.

### BEAT 3 — REVEAL + PROOF (8–27s) — *screen-record, real terminal*
- **VO:** "So I built statusline-plus. Two commands to install. It reads the status line once and shows your model, cost, context, your 5-hour and 7-day limits, and your git branch — all on one line. Three themes: minimal, full, power. Switch with one command."
- **On-screen / B-roll sequence (3–5s clips, zoomed for mobile):**
  1. `/plugin marketplace add tarunlnmiit/statusline-plus`
  2. `/plugin install statusline-plus@statusline-plus`
  3. `/statusline-install` → status line appears live at the bottom of the terminal
  4. Close-up pan across the `full` theme: model · cost · context bar · 5h · git branch
  5. `/statusline power` → line swaps to the power theme with tokens + 7d + duration
- **Cue:** `CodeAnnotation` over the three install commands; burn-in single words: `1 JQ PASS` · `3 THEMES` · `MERGE-SAFE`.

### BEAT 4 — PAYOFF (27–33s)
- **VO:** "Same terminal. Same session. Now you can see exactly what you're spending, and how close you are to the wall."
- **On-screen:** `Every number, one glance.`
- **Cue:** Back to face, confident close.

### BEAT 5 — CTA (33–38s)
- **VO:** "It's free and open source. Comment LINE and I'll DM you the repo and the install steps."
- **On-screen:** `Comment "LINE" → repo in your DMs · install steps in caption ↓`
- **Loop:** end frame = the rendered `full` theme status line (result, not "bye") → invites rewatch.

---

## Caption (06 formula — the caption IS the product)

Comment "LINE" and I'll send you the repo + install steps 👆

Claude Code doesn't show you your cost, your rate limits, or your git branch by default. This free plugin puts all of it on one line — read in a single `jq` pass, not once per segment.

Install (Claude Code):
1. /plugin marketplace add tarunlnmiit/statusline-plus
2. /plugin install statusline-plus@statusline-plus
3. /statusline-install

3 themes, switch anytime with `/statusline <name>`:
1. minimal — model · context · folder
2. full — + cost, git branch, 5-hour limit, reset time (daily driver)
3. power — + tokens, 7-day limit, duration, PR state, everything

Merge-safe install — patches your settings.json without touching anything else. Uninstall anytime with `/statusline-uninstall`.

Free · open source · MIT.

#claude #claudecode #ai #devtools #datascience

**Keyword:** LINE
**DM payload:** https://github.com/tarunlnmiit/statusline-plus (add UTM params once registered in `data/kb/projects.json`)
**Pinned first comment:** Repo (free, MIT): same link + "Comment LINE if the DM tool misses you."

## Thumbnail text (06 formula — outcome, not topic)

`Claude Code was hiding my cost & limits 😳 1 line fixes it`
Alt: `I built the status line Claude Code should've shipped with 🤯`

## YT Shorts delta

Same footage. CTA line swap: "Repo's in the description — it's free. Subscribe for the next build." Link = first line of description + pinned comment. `#Shorts` in title.

## Checklist (viral_reel_formula §per-reel)
- [ ] Hook recorded 5×, winner picked
- [ ] Terminal B-roll captured: 3 install/wire commands, live status line appearing, theme close-up, `/statusline power` switch (zoomed)
- [ ] Captions burned in word-by-word; no clip > 4s; ~150 wpm
- [ ] Honesty guardrail: it's read-only display of Claude Code's own status-line JSON — doesn't send data anywhere, doesn't control the model; never imply it "monitors" or "controls" Claude
- [ ] Before scheduling a recurring cadence: add `statusline_plus` to `data/kb/projects.json` (dm_keyword, UTM template, honesty_guardrail) — this reel is a one-off launch, not yet wired into the weekly project rotation
- [ ] Comment→DM tool armed with keyword LINE + UTM link (once repo entry exists)
- [ ] Loop ends on the rendered `full` theme frame
- [ ] **Green screen:** test-key clip composited (`composite_greenscreen.py --niche ds`) and edges/spill inspected *before* real takes
- [ ] **Green screen:** wardrobe has no green/teal/yellow-green; check hair/shoulder edges in the test composite
- [ ] **Green screen:** this reel and inbox-to-action shot in the same session/setup — no framing/lighting change across any take, including hook re-records
- [ ] Beat 3's `full`/`power` theme close-ups show real cost + rate-limit numbers — confirm with Tarun he's fine with those being legible at zoom before recording
- [ ] Screen-record B-roll captured in a separate sitting — not coupled to the greenscreen session
