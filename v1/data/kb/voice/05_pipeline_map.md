# 05 — Pipeline Map (voice KB → blog-first pipeline)

Where this KB plugs into the pipeline for **poetry + life**. Patterns are source intelligence, so they enter
**upstream at the blog** and propagate to every derivative. Mirrors `data/kb/reels/05_pipeline_map.md` (tech), but
routes the voice niches. The engine `scripts/lib/virality.py` picks this KB when `niche in {poetry, life}`.

## Pipeline
```
Blog → YouTube long-form → Social (carousels + worksheets) → Clips (reels/shorts from long-form) → Remotion reels
```

## Stage-by-stage wiring
### Stage 0 — Blog (source of truth) ← biggest leverage
- Load `01_hook_library.md` + `02_idea_bank.md` when choosing the post angle/title (emotional archetypes, not tech).
- Load `04_authenticity_guardrail.md` at draft review — catching performed emotion here keeps every derivative clean.

### Stage 1 — YouTube long-form
- Carry the blog's emotional archetype into the title (e.g. Specific Loss for grief poems; Bold Declaration for life).
- Poetry: ensure a self-contained, recitable passage exists (Stages 3-4 harvest it).

### Stage 2 — Social (carousels + worksheets)
- Life: carousel from a confession→mechanism→framework angle (one idea per slide) — the proven save-bait shape.
- Poetry: quote-card / single strong stanza for the cover; full piece in the reel.

### Stage 3 — Clips (reels/shorts from long-form)
- The clip-finder scores moments against the **emotional arc** + hook archetypes: a clip wins if its first 3s match
  an archetype and it lands a specific-feeling → recognition beat. Feed `01` to the moment-selection prompt.

### Stage 4 — Remotion reels (from the YouTube script)
- Inject `01` at the script→scene step so the opening WordReveal/AtmosphericQuote is a proven emotional hook.
- Poetry uses AtmosphericQuote/HandwrittenReveal for thesis lines (never WordReveal for a poem's core line).

## Prompt/script touch-points
| File to edit | Add |
|---|---|
| blog ideation/title prompt | load `01`, `02`; title from an emotional archetype |
| blog/script QA step | load `04`; run the pass/fail checklist |
| carousel prompt | life: confession→mechanism→permission slides |
| clip-finder prompt | score against emotional arc + `01` |
| scene-plan / repurposing prompt | load `01`; emotional hook first, permission close |
| `collect_analytics.py` | append results to `03`'s table |

## Feedback loop
`collect_analytics.py` writes each shipped poetry/life piece's outcome into `03_swipe_file.md`. Periodically re-rank
`01_hook_library.md` by your own numbers so the library converges on what works for *this* audience.
