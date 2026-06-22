# IG Reel Brief — Claude + Caveman (save tokens)

**Niche:** DS · **Format:** Reel (9:16) · **Destinations:** Instagram Reel (@mistakenlyhuman) + YouTube Short
**Slug:** `2026-06-21_data_science_tech_claude-caveman-tokens` · **Week:** 2026-W25
**DM keyword:** `CAVEMAN` · **Deliverable:** public caveman-claude-skill repo
**Rides proven template:** trakin.ai "Save Claude tokens" → CAVEMAN, ~40.3K likes / 704 shares (`data/kb/reels/03_swipe_file.md`)

---

## Hook options (≤5-word burned overlay — pick one, re-record till it pops)

1. **"I made Claude a caveman"** — pattern #2 Bold Declaration. Curiosity + WTF.
2. **"Claude was burning my tokens"** — pattern #7 Data/Mechanism. Names the pain.
3. **"One command. 75% fewer tokens."** — pattern #7. Outcome-forward, specific number.

> First 3 seconds decide everything. Hard cut, no "hey guys". Overlay the hook, cut straight to the terminal.

---

## 5-beat shot list (35–45s, trims to 30s) — *show the tool, don't tell*

| # | Beat | Time | On screen | Overlay |
|---|------|------|-----------|---------|
| 1 | **Hook** | 0–3s | Your face OR terminal cold-open | Hook (≤5 words) |
| 2 | **Problem** | 3–8s | Scroll a long, fluffy Claude reply | "Every reply = paragraphs of fluff eating tokens" |
| 3 | **Reveal + proof** | 8–28s | Type `/caveman` → ask the same question → terse reply appears | "~75% shorter replies" · point at the code block still intact |
| 4 | **Payoff** | 28–35s | Side-by-side: normal reply vs caveman reply | "Same accuracy. Code untouched. Fluff gone." |
| 5 | **CTA** | 35–45s | Point down at comments | "Comment **CAVEMAN** — I'll DM the skill" |

**Proof is the whole reel.** Beat 3 must be a *real screen capture* of caveman shortening an actual reply while leaving a code block intact. Don't fake it.

**One CTA only.** Nothing else asked.

---

## Caption (DS formula — post exactly in this order)

```
Comment "CAVEMAN" and I'll send you the skill 👆

I cut Claude's replies ~75% with one command — and it never touched my code blocks.

It's a Claude Code skill called "caveman mode". It compresses Claude's OUTPUT (the replies),
not your prompts — by dropping articles, filler, and hedging while keeping code, technical
terms, and exact error strings.

How to use it:
1. Install the skill (repo link in the DM)
2. Type /caveman  →  every reply gets terse
3. Pick the level: lite (light trim) · full (default) · ultra (max squeeze)
4. Code, commands, and errors stay verbatim — only the prose shrinks
5. Say "normal mode" to turn it off

Fewer output tokens = longer sessions before you hit limits.

#claude #ai #datascience #python #aitools
```

---

## DM payload (what "CAVEMAN" sends)

> The caveman-claude-skill repo, UTM-tagged for star attribution:
> `{CAVEMAN_REPO_URL}?utm_source=instagram&utm_medium=reel&utm_campaign=reel-caveman&utm_content=ds`
>
> **TODO before posting:** drop in the real public caveman-claude-skill GitHub URL. Generate the
> per-platform tagged links with `scripts/lib/utm.py:build_utm_url(base, source="instagram",
> medium="reel", campaign="reel-caveman", content="ds")` (and `source="youtube", medium="short"`
> for the Short).

---

## Cover / thumbnail line (state the OUTCOME, not the topic)

- "Claude wasted 75% of my tokens 😳"
- "I turned Claude into a caveman 🤯"

---

## Honesty box (do NOT overclaim)

- caveman mode compresses **Claude's output prose ~75%** — it does **not** cut input/prompt tokens
  or "make Claude smarter".
- It **preserves** code blocks, technical terms, and exact error strings — say so on screen; it's
  the trust-builder.
- It's a **Claude Code (CLI) skill**, triggered by `/caveman` or "caveman mode".

---

## After posting

Add a tracker row in `output/trackers/annual-tracker-2026.xlsx` (DS · Reel · this slug · posting
date · Status=Published). Reply to "CAVEMAN" comments with the DM link in the engagement window.
