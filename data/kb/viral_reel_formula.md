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
- [ ] Derivatives generated (`prompts/repurposing_agent.md`) → Metricool CSV
