---
title: "IG Reel Script — DS/Tech · \"It reads your inbox. It never sends anything.\""
type: reel
niche: data_science_tech
date: 2026-07-20
week: 2026-W30
slug: tech-inbox-to-action
platform: ig
tags: [content/reel, niche/data_science_tech, week/2026-W30]
---
# IG Reel Script — DS/Tech · "It reads your inbox. It never sends anything."

> **Source:** github.com/tarunlnmiit/inbox-to-action — `pip install inbox-to-action`. Build-in-public project reel (registry: `data/kb/projects.json` key `inbox_to_action`). No source blog — reel stands alone, consistent with the existing W28 carousel (`assets/carousels/2026-W28/inbox-to-action*`).
> **Formula:** `data/kb/viral_reel_formula.md` (5-beat) + `data/kb/reels/06_mavgpt_caption_formula.md` (caption IS the product).
> **Length target:** ~40s. Format: 9:16 talking-head + terminal screen-record B-roll.
> **CTA:** keyword **INBOX** → auto-DM repo link (UTM-tagged). Repo link also pinned in first comment.
> **Angle:** `angle_rotation[0]` from projects.json — a real inbox triaged live (unread mail → tasks + drafts).
>
> **Production note (green screen):** Talking-head shot against a physical green screen, fixed framing, composited via `scripts/composite_greenscreen.py --input <clip> --niche ds` onto `assets/brand/backgrounds/ds_studio_portrait.png`. Shoot this and the statusline-plus reel in the **same session, same setup** — one key calibration for both. Run a ~5s test-key through the composite script and check edges/wardrobe spill *before* the real takes. Keep framing/lighting identical across all takes, including the 5 hook re-records — the key is calibrated once and cached. Beat 3's terminal footage is captured separately (no greenscreen constraints, no need to couple it to the studio sitting).

---

## Hook — 5 variants (pick winner after cold rewatch)

1. ✅ **PICK (suggested)** — "One command just read my inbox, drafted four replies, and sent none of them." *(Result + tension: what it did vs. what it withheld)*
2. "I built a tool that triages my Gmail inbox. It's not allowed to hit send. Literally — there's no send code." *(Bold Declaration + honesty hook)*
3. "Six unread emails. One command. Four drafts, two calendar flags, zero sent." *(Data/Mechanism, concrete count)*
4. "Stop touching the same email four times. One command reads it, drafts it, and flags your calendar." *(Problem-first, carries the carousel's opening line)*
5. "I gave an AI agent read access to my inbox. Here's the one thing it's not allowed to do." *(Curiosity gap, safety-forward)*

**Driver:** Result + honesty tension. Honesty note: hook 2's "no send code" claim must land on-screen in beat 3 as the actual proof (grep or test output), not just spoken. First frame = hook burned in, hard cut, no warm-up.

---

## 5-Beat Script

### BEAT 1 — HOOK (0–3s)
- **VO:** "One command read my inbox, drafted 4 replies, and sent zero."
- **On-screen (burn-in):** `1 COMMAND → 4 DRAFTS, 0 SENT`
- **Cue:** Face to camera, hard cut in. Re-record 5×, keep the sharpest.

### BEAT 2 — PROBLEM (3–8s)
- **VO:** "You open the email. Read it again. Half-remember what it's asking. Close the tab. Come back later and do it all over."
- **On-screen:** `open · re-read · forget · re-open` *(each word strikes through in sequence)*
- **Cue:** B-roll: a seeded/decoy inbox (not real personal mail), cursor clicking the same thread open and closed twice.

### BEAT 3 — REVEAL + PROOF (8–28s) — *screen-record, real terminal*
- **VO:** "So I built inbox-to-action. One command sorts your inbox: tells you what matters, sums up long threads, pulls out tasks with deadlines, drafts the replies. It never hits send — there's no send code, a test checks that. And you pick the AI, six options, even a fully local one."
- **On-screen / B-roll sequence (3–5s clips, zoomed for mobile):**
  1. `pip install inbox-to-action`
  2. `inbox-to-action run --since 24h` on a **seeded demo inbox with 6 unread that genuinely yields 4 drafts + 2 calendar flags** — must match the hook's numbers on-screen, not just in the VO
  3. Gmail Drafts folder — the 4 drafts sitting unsent (same demo inbox, no real mail)
  4. `grep -r "send" src/` or test file scroll — proving no send scope
  5. Provider list: OpenRouter · Claude · Ollama (local) flash by
- **Cue:** `CodeAnnotation` over the command; burn-in single words: `CLASSIFY` · `SUMMARIZE` · `DRAFT` · `NEVER SEND`.

### BEAT 4 — PAYOFF (28–34s)
- **VO:** "Your inbox, actually handled — minus the one thing you never wanted an AI touching."
- **On-screen:** `Drafts ready. Nothing sent. You decide.`
- **Cue:** Back to face, confident close.

### BEAT 5 — CTA (34–40s)
- **VO:** "It's free and open source. Comment INBOX and I'll DM you the repo and the setup."
- **On-screen:** `Comment "INBOX" → repo in your DMs · pip install in caption ↓`
- **Loop:** end frame = Drafts folder shot (result, not "bye") → invites rewatch.

---

## Caption (06 formula — the caption IS the product)

Comment "INBOX" and I'll send you the repo + setup 👆

One command triages your inbox in a single pass — classifies what matters, extracts tasks with deadlines, drafts replies, flags what needs calendar time.

It never sends anything. No send scope in the codebase — enforced by a test, not a promise.

BYOK across 6 LLM providers, including fully-local Ollama — nothing has to leave your machine.

1. Classify unread mail
2. Extract tasks + deadlines
3. Draft the replies (never sent)
4. Flag what needs calendar time

pip install inbox-to-action · open source

#claude #claudecode #ai #python #datascience #opensource #devproductivity #aitools #buildinpublic

**Keyword:** INBOX
**DM payload:** https://github.com/tarunlnmiit/inbox-to-action?utm_source=instagram&utm_medium=dm&utm_campaign=inbox_to_action
**Pinned first comment:** Repo (free, open source): same UTM link + "Comment INBOX if the DM tool misses you."

## Thumbnail text (06 formula — outcome, not topic)

`It read my inbox and drafted 4 replies. Sent 0 🤯`
Alt: `1 command. 4 drafts. 0 sent 😳`

## YT Shorts delta

Same footage. CTA line swap: "Repo's in the description — free, `pip install inbox-to-action`. Subscribe for the next build." Link = first line of description + pinned comment. `#Shorts` in title.

## Checklist (viral_reel_formula §per-reel)
- [ ] Hook recorded 5×, winner picked
- [ ] Terminal B-roll captured: install, `run --since 24h` live output, Drafts folder, no-send-scope proof, provider list (zoomed)
- [ ] Captions burned in word-by-word; no clip > 4s; ~150 wpm
- [ ] Honesty guardrail: "never sends anything" backed on-screen by the no-send-scope grep/test shot in beat 3; default provider (OpenRouter) is cloud — only ollama/claude keep mail local, don't imply local-only by default
- [ ] Comment→DM tool armed with keyword INBOX + UTM link
- [ ] Loop ends on Drafts-folder frame
- [ ] **Green screen:** test-key clip composited (`composite_greenscreen.py --niche ds`) and edges/spill inspected *before* real takes
- [ ] **Green screen:** wardrobe has no green/teal/yellow-green; check hair/shoulder edges in the test composite
- [ ] **Green screen:** this reel and statusline-plus shot in the same session/setup — no framing/lighting change across any take, including hook re-records
- [ ] **Demo inbox:** seeded to match hook numbers (6 unread → 4 drafts, 2 calendar flags) before recording beat 3; no real personal mail visible anywhere on screen
- [ ] Screen-record B-roll captured in a separate sitting — not coupled to the greenscreen session
