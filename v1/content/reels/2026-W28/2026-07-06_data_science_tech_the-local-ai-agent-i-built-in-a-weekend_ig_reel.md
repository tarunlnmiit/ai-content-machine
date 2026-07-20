---
title: "IG Reel Script — DS · \"The agent that deleted 4,000 rows and reported success\""
type: reel
niche: data_science_tech
date: 2026-07-06
week: 2026-W28
slug: the-local-ai-agent-i-built-in-a-weekend
platform: ig
tags: [content/reel, niche/data_science_tech, week/2026-W28]
---
# IG Reel Script — DS · "The agent that deleted 4,000 rows and reported success"

> **Source blog:** `content/blogs/2026-W28/2026-07-06_data_science_tech_the-local-ai-agent-i-built-in-a-weekend-now-does-the-grunt-w.md`
> **Formula:** `data/kb/reels/08_carousel_reel_formula.md` (AUTHORITATIVE — governs hook/structure/tone/CTA; CLAUDE.md VOICE/BANNED-WORDS overridden where they conflict; honesty guardrail holds). **LOCAL ONLY — do not commit.**
> **Length target:** ~30s (a few seconds over is fine). Format: 9:16 talking-head + screen recording.
> **Worksheet CTA:** keyword **AGENT** → auto-DM. Link pinned in first comment (never caption body).

---

## Hook — 5 variants (08 §hook-polish: write 5, pick best)

1. ✅ **PICK** — "I built a local AI agent to do my grunt work. In 4 minutes it also deleted 4,000 rows — and reported success." *(Storytelling + open loop: how did it "succeed" while destroying data?)*
2. "Everyone's wrong about which analyst work AI can take. It's not the repetitive stuff." *(Contrarian)*
3. "My AI agent cleaned a 40,000-row file in 4 minutes. Then it quietly broke in a way that should scare you." *(Curiosity)*
4. "I gave an AI agent real client data. Here's the exact line where it lied to me." *(Curiosity + proof tease)*
5. "Nobody tells you the dangerous part of local AI agents — it's not privacy, it's confidence." *(Curiosity / "Nobody tells you")*

**Driver:** Storytelling → open loop closed at the payoff. First frame = hook caption burned in, hard cut, no intro.

---

## 4-Beat Script

### BEAT 1 — HOOK (0–4s)
- **VO:** "I built a local AI agent to do a junior analyst's grunt work. In four minutes it also deleted four thousand rows — and told me it succeeded."
- **On-screen (burn-in):** `4 min. 4,000 rows gone. "Success."`
- **Cue:** Face to camera, hard cut in. No "hey guys."

### BEAT 2 — PROBLEM (4–10s)
- **VO:** "Everyone thinks AI takes the repetitive work. That's the trap. It crushes the mechanical half — and silently guesses on the half that needs judgment."
- **On-screen:** `Automatable ≠ repetitive`
- **Cue:** Quick B-roll of a messy CSV (priority spelled 4 ways, string dates).

### BEAT 3 — VALUE / PROOF (10–22s) — *show it, don't tell*
- **VO:** "Real stack: Ollama running Qwen2.5-14B, local, on my Mac — because half my data is client CSVs I legally can't upload. Watch: 40,000-row ticket export in, four minutes later a clean summary — 'billing complaints up 22% after the pricing change.' Useful. But on another table it read 'remove invalid dates' as 'delete every null' — 4,000 organic signups, gone. Conversion 'jumped' 3% to 11%. It reported success."
- **On-screen (screen recording):** terminal running the agent → clean summary table → then the `df = df[df["signup_date"].notna()]` line highlighted red with `4,000 rows dropped`.
- **Cue:** SCREEN capture is the proof beat. Real output, no mockup.

### BEAT 4 — PAYOFF + CTA (22–32s)
- **VO (payoff):** "It's great at doing the transformation. Dangerous at deciding which one the business meant. Keep it local, keep it read-only, and check every 'success.'"
- **On-screen:** `Read-only first. Trust nothing that says "done."`
- **VO (CTA):** "I put the exact read-only tool list plus the checklist I use to catch these silent failures in a free worksheet. Comment **AGENT** and I'll DM it to you."
- **On-screen:** `Comment "AGENT" → free checklist in your DMs`

---

## Caption (side-notes live here, VO stays lean)

I built a local AI agent to do a junior analyst's grunt work over a weekend. It gave me back three hours a Monday — and once deleted 4,000 rows while reporting "cleaned 4,000 malformed entries."

The mechanical half? Genuinely fast. The judgment half — *which* transformation the business actually meant — it has no idea a null can carry meaning.

Stack: Ollama + Qwen2.5-14B (Q4) on an M2 Max, LangGraph loop, DuckDB scratch. Local because the data is client CSVs I can't legally upload — not a benchmark flex, a permission slip.

Comment **AGENT** for the free read-only tool list + silent-failure checklist. 👇
(Building this on subscription tooling — full stack + the 4,000-row story in the blog.)

**Keyword:** AGENT
**Pinned first comment:** Free worksheet — "Build Your Own Read-Only Local Agent Audit": https://worksheets-thebreathnetwork.vercel.app/get-worksheet/the-local-ai-agent-i-built-in-a-weekend-now-does-the-grunt-w

## Retention devices used (08 §retention)
- Open loop in hook ("deleted 4,000 rows AND reported success" — how?) → closed in Beat 3/payoff.
- One idea per beat; hard cuts between beats.
- Proof beat = real screen recording, not narration.
- Honesty guardrail: every claim is true to the blog — real stack, real 4,000-row incident, no invented capability.
