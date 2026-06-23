# Viral Reel Formula (project / build-in-public)

Reusable recipe for short-form product/dev reels, reverse-engineered from the
**autopilot-jobhunt** reel that hit **38,501 views, 358 follows, 1.7k comments, 1.1k saves,
794 shares**. Use this for any project reel so every one follows the proven structure instead
of starting blank.

> See also the broader pattern KB at [`data/kb/reels/`](./reels/INDEX.md) (tech/build) and
> [`data/kb/voice/`](./voice/INDEX.md) (poetry/life). The engine `scripts/lib/virality.py`
> injects these into every generator.

> Companion data: hook taxonomy in [`twitter_hook_patterns.json`](./twitter_hook_patterns.json).
> Scenes referenced live in `remotion/src/compositions/scenes/*.tsx`.

---

## The 5 beats (35–45s, trims to 30s)

| # | Beat | Time | Job | Rule |
|---|---|---|---|---|
| 1 | **Hook** | 0–3s | Stop the scroll | Bold claim + face or big text. Hard cut, no "hey guys." |
| 2 | **Problem** | 3–8s | Name the pain they feel now | Visceral, specific, relatable. |
| 3 | **Reveal + proof** | 8–28s | What it is + show it *actually working* | Screen-record real output. Proof beats claims. |
| 4 | **Payoff** | 28–35s | Why it matters / the result | Back to face, confident. |
| 5 | **CTA** | 35–45s | ONE action | "Comment 'KEYWORD' and I'll DM you the link." |

**Total spoken ≈ 40s.** If cutting to 30s, drop the weakest sub-feature in beat 3 first.

---

## Beat → Remotion scene map (reuse, don't rebuild)

| Beat | Scene component(s) | Notes |
|---|---|---|
| Hook | `WordReveal`, `TitleCard` | Big word-by-word claim; burn-in caption. |
| Problem | `LineReveal`, `AtmosphericQuote` | "130+ sites. Every. Single. Day." |
| Reveal+proof | screen-record B-roll + `CodeAnnotation`, `DataVizReveal`, `CounterReveal` | `CounterReveal` for a score ticking 0→100; `CodeAnnotation` over the terminal command. |
| Payoff | `ImageTextReveal`, `NumberedTips` | "Open source · runs locally · free." |
| CTA | `OutroCard`, `LowerThird` | Keyword + handle, point-down framing. |

Build pipeline already exists: `scripts/create_vertical_reels.py`,
`scripts/find_best_reel_moment.py`, `scripts/hyperframes_render.py`.

---

## Hook selection (test 2–3, keep the winner)

First 3 seconds decide everything — re-record/regenerate the hook 5×. Pull a pattern from
`twitter_hook_patterns.json`; for product/dev reels these map best:

- **Bold Declaration** (#2) — "I built a FREE AI agent that hunts jobs while I sleep."
- **Data / Mechanism** (#7) — "130 companies. Scored against my resume. Every night. For free."
- **Contrarian Mirror** (#1) — "I haven't opened a careers page in 30 days. Here's why."
- **Social Proof Inversion** (#8) — "Job hunting is a full-time job. So I automated mine."

Product-reel hook checklist: concrete number + a "free/open" angle + a "while you sleep / so I
stopped" twist.

---

## Honesty guardrail (do not break)

State what the tool **actually** does. Never overclaim (e.g. don't say "auto-applies" if it only
drafts). Overclaiming invites the comments to roast you and kills trust. The honest, still-
impressive pitch pre-empts "is this a scam" replies and drives saves/shares.

---

## Editing rules (the non-negotiables)

- **Captions burned in** — 85% watch muted. Big, high-contrast, word-by-word.
- **Cut on every sentence.** No clip > ~4s.
- **Hard cut at 0–3s.** No slow intro.
- **Trending audio** low under voice.
- **Loop it** — end on the result, not "bye"; invite the rewatch.
- Pacing ~140–160 wpm. Energy up, zero dead air.

---

## Platform deltas (same footage, different CTA)

| Platform | CTA | Link mechanic |
|---|---|---|
| **Instagram Reel** | "Comment 'KEYWORD' — I'll DM you the link." | Comment→DM tool: **SuperProfile** (free, unlimited comment→DM) or **CreatorFlow** (free tier) — ManyChat replacements. Pin a comment with the keyword prompt. |
| **YouTube Shorts** | "Repo's in the description. Subscribe." | Link as **first line** of description + pinned comment. `#Shorts` in title. |
| **TikTok** | "Link in bio / comment KEYWORD." | Link-in-bio; keyword DM where supported. |
| **X** | Hook tweet → thread → repo link in final tweet | Native link in last post. |

Always attach a **UTM-tagged link** so `collect_analytics.py` can attribute stars/follows to the
piece (see `data/kb/` tracking convention / `scripts/collect_analytics.py`).

---

## Per-reel checklist

- [ ] Hook recorded 5× (or regenerated), winner picked
- [ ] Screen-record proof B-roll captured (3–5s clips, zoomed for mobile)
- [ ] 5 beats present, ≤45s, captions burned in
- [ ] Honesty guardrail held (no overclaim)
- [ ] CTA = one keyword; comment→DM tool armed (SuperProfile / CreatorFlow)
- [ ] UTM link in DM/description/bio
- [ ] Derivatives generated (`prompts/repurposing_agent.md`) → posted manually (no Metricool/Publer CSV)

---

## @mavgpt caption formula (reference: 887k followers, reels hitting 3.8m views)

Reverse-engineered from @mavgpt (Maverick Maltin). The structural insight that separates their
top reels from mid performers: **the caption IS the product**. The reel hooks people into
watching; the caption is what they screenshot and save. The full value (prompts, steps, list)
lives in the caption body — not just behind the DM keyword.

### Caption structure (mandatory order)

```
Line 1:  Comment "[KEYWORD]" and I'll send you [specific deliverable] 👆
Line 2:  [One-line proof/claim — specific and verifiable-sounding]
Line 3+: [Numbered list — the full value verbatim, actionable items]
Last:    #hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5
```

**Real examples from top reels:**

3.8m reel — "Comment 'Jobs' and I'll send you all the prompts 👆 / What happens when you ask
ChatGPT to apply to 500 jobs for you? / I tried this and landed 12 interviews in 24 hours. /
Prompt 1: Upload your resume... / Prompt 2: Rewrite my resume... / [etc]"

1.1m reel — "Comment 'AI' and I'll send you my 2026 AI stack 👆 / The best AI for every task
right now. / Writing emails: Claude / Brainstorming new ideas: ChatGPT / [etc]"

104k reel — "Comment 'Settings' and I'll send you my full list 👆 / 5 hidden ChatGPT settings
most people never turn on. / 1. Memory / Settings → Personalization → [exact steps] / [etc]"

### Thumbnail text formula

The thumbnail text IS the hook — it must state the outcome/claim, not the topic:

| Works | Doesn't work |
|-------|-------------|
| "ChatGPT applied to 500 jobs for me 😳" | "How to use ChatGPT for job hunting" |
| "5 Secret Settings for ChatGPT 🤯" | "ChatGPT tips" |
| "Claude just killed personal trainers 🤯" | "Claude for fitness" |
| "Things you didn't know you could do with AI pt12" | "AI tips part 12" |

Pattern options:
- `[Number] [secret/hidden] [things] for [tool] 🤯`
- `[Tool] just [killed/replaced/changed] [industry/task] 🤯`
- `[I/tool] [did dramatic thing] to [specific outcome] 😳`
- `[BAD/GOOD/GREAT]` visual for comparisons

### Serialization pattern

Number your series ("pt1", "pt2"...) — builds returning viewers and algorithmic advantage.
Example: "Things you didn't know you could do with AI pt12" implies pt1–11 also exist.
Name your series in the thumbnail text from the first installment.

### Burned-in captions during the reel

One word or short phrase per beat — not full sentences. Confirms what he's saying verbally:
`HERE` / `THINGS` / `CHATGPT` / `WHAT` / `BEFORE` / `AFTER`

### What this means for Tarun's DS reels

- The 5-part prompt template belongs IN the caption, not DM-only. DM sends a formatted
  version; caption has it too (abbreviated is fine, but it must be there).
- Thumbnail text must state the specific data science outcome: "I gave ChatGPT 100 data
  problems. Here's the best prompt 😳" not "Better prompting for data scientists"
- Series opportunity: "Prompt Anatomy pt1" — can keep making these and pt2 gets easy views
- Keep hashtags DS-focused: #datascience #ai #chatgpt #python #dataanalyst (max 5)
