---
title: "Voice KB — Index (Poetry + Life)"
type: kb
slug: index
tags: [content/kb]
---
# Voice KB — Index (Poetry + Life)

Read this first. This folder is the **emotional/voice virality** knowledge base for the Poetry and Life/self-dev
niches — the counterpart to `data/kb/reels/` (which is tech/build only). It is reverse-engineered from this
creator's *own proven wins*, not borrowed tech-reel patterns. Like the reels KB, it is **format-agnostic source
intelligence**: the patterns feed the whole pipeline (blog → YouTube → social/carousels → clips → Remotion reels),
not just one format.

| File | What it is | Pull it at this pipeline stage |
|---|---|---|
| `00_playbook.md` | Strategy spine: why poetry/life pieces land, the emotional arc per niche. | Always (orientation). |
| `01_hook_library.md` | Emotional hook archetypes with real examples + performance notes. | Blog title, YouTube title, reel hook, carousel cover. |
| `02_idea_bank.md` | Emotional angle menu per niche, mapped to the arc. | Blog/topic ideation. |
| `03_swipe_file.md` | The creator's own best poetry/life pieces + a results log. | Ideation + feedback loop. |
| `04_authenticity_guardrail.md` | Anti-toxic-positivity / no-manufactured-urgency rules. | QA pass at EVERY format. |
| `05_pipeline_map.md` | Exactly where each doc wires into the blog-first pipeline. | Setup / when editing prompts & scripts. |
| `life_formula.md` | @ankurwarikoo reverse-engineered formula: thumbnail system, hook patterns, caption modes, CTA mechanics for Life niche. Its `## Engine digest (compact)` is injected by `virality.py` into Life caption generators. | Before writing any Life reel, carousel, or blog. |
| `poetry_formula.md` | @christi.steyn reverse-engineered formula: 5 reel formats, poem structure, caption table, hashtag rules for Poetry niche. Its `## Engine digest (compact)` is injected by `virality.py` into Poetry caption generators. | Before writing any poetry reel or spoken-word piece. |

> **Engine digest contract:** `scripts/lib/virality.py` reads ONLY the `## Engine digest (compact)` section of these two formula files (DS uses `../reels/06_mavgpt_caption_formula.md`) and injects it into caption content types. Edit that section to change generator behavior; the long body stays human reference. Full wiring: `docs/weekly-operating-guide.md` → Virality.

Routing: this KB serves **poetry + life**. DS/build content uses `data/kb/reels/`. Never cross them.

Conventions:
- Reference docs for agents/prompts to load. Keep them small and single-purpose.
- After a piece ships, log results into `03_swipe_file.md` (see its footer) so the library re-ranks by *your* numbers.
- The authenticity guardrail is non-negotiable and applies upstream at the blog stage so it propagates to every derivative.
