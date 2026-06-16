# 05 — Pipeline Map

Where this KB plugs into your blog-first repurposing pipeline. The patterns are source intelligence, so they enter **upstream at the blog** and propagate to every derivative — not bolted on only at the reel step.

## Your pipeline (as described)
```
Blog  →  YouTube long-form (from blog)  →  Social posts (carousels + worksheets)
      →  Clips (reels/shorts cut from the long-form)
      →  Remotion reels (generated from the YouTube script)
```

## Stage-by-stage wiring

### Stage 0 — Blog (the source of truth) ← biggest leverage
- Load `01_hook_library.md` + `02_idea_bank.md` when choosing the **post angle and title**. The 8 archetypes are title patterns (roadmap for pillar posts; secret/number for tactical ones).
- Load `04_honesty_guardrail.md` at draft review. Catching overclaims here means every downstream format inherits clean claims.
- If the topic is a Tier-1 build idea, flag "capture B-roll" in the blog draft so the demo footage exists for the clip + reel steps.

### Stage 1 — YouTube long-form
- The blog's hook archetype carries into the **YouTube title + thumbnail text** (same archetype, same big-text legibility rule).
- Structure the script so it contains at least one self-contained **5-beat segment** (`00_playbook.md`) — that segment is what Stages 3 and 4 will harvest.

### Stage 2 — Social posts (carousels + worksheets)
- Carousel-native archetypes are #3 listicle, #5 free-vs-paid, #7 roadmap (`01_hook_library.md`). The data shows these earn the most saves/shares — make at least one carousel per blog from a listicle/roadmap angle.
- Worksheets pair naturally with the roadmap/idea-bank entries (e.g. a "weekend to master X" checklist).

### Stage 3 — Clips (reels/shorts from long-form) ← key new wiring
- Your clip-finder (`scripts/find_best_reel_moment.py` or equivalent) should score moments against the **5 beats** and the **hook archetypes**, not just audio energy. A clip wins if its first 3s match an archetype and it contains a problem→proof→payoff arc.
- Feed `01_hook_library.md` to the moment-selection prompt so it knows what a strong hook *looks like* when scanning the transcript.

### Stage 4 — Remotion reels (from the YouTube script)
- This is where `viral_reel_formula.md`'s beat→scene map already lives. Inject `01_hook_library.md` at the script→scene step so the WordReveal/TitleCard hook is drawn from a proven archetype.
- Map: Hook→`WordReveal`/`TitleCard`; Problem→`LineReveal`; Reveal+proof→screen-record B-roll + `CodeAnnotation`/`CounterReveal`; Payoff→`ImageTextReveal`/`NumberedTips`; CTA→`OutroCard`/`LowerThird`.

## Prompt/script touch-points (summary)
| File to edit | Add |
|---|---|
| blog ideation prompt | load `01`, `02`; title from an archetype |
| blog/script QA step | load `04`; run the pass/fail checklist |
| YouTube title/thumbnail prompt | reuse the blog's archetype |
| carousel generation prompt | pull archetypes #3/#5/#7 from `01` |
| `find_best_reel_moment.py` prompt | score against 5 beats + `01` |
| Remotion script→scene step / `prompts/repurposing_agent.md` | load `01`; apply beat→scene map |
| `collect_analytics.py` | append results to `03`'s results table |

## The feedback loop
`collect_analytics.py` writes each piece's outcome into the results table in `03_swipe_file.md`. Periodically re-rank `01_hook_library.md` by *your* numbers so the library converges on what works for your account, across all formats — not just the borrowed inspiration set.
