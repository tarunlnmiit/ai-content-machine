# Terminal prompt — bake @mavgpt caption formula into the pipeline

Paste this into Claude Code CLI (`claude` in terminal, inside the content-machine repo).

---

## THE PROMPT (copy everything below this line)

Update the content-machine pipeline to bake in the @mavgpt Instagram caption formula. 
Here is the full context so you don't need to browse.

**@mavgpt (Maverick Maltin | AI & ChatGPT) — 887k followers.**

Top reel view counts analyzed: 3.8m, 1.3m, 1.1m, 168k, 130k, 116k, 104k, 72.2k, 56.6k, 51.8k

**The formula (reverse-engineered from their highest-performing reels):**

The key insight: **the caption IS the product**. The reel gets people to stop scrolling; 
the caption is what they screenshot and save. Full value (prompts, steps, list) lives 
in the caption body — not just behind a DM keyword.

**Caption structure (invariant across all their top reels):**
```
Line 1: Comment "[KEYWORD]" and I'll send you [specific deliverable] 👆
Line 2: [One-line proof/claim — specific, verifiable-sounding]
Lines 3+: [Numbered list — full value verbatim, immediately actionable]
Last: #hashtag1 #hashtag2 #hashtag3 #hashtag4 (max 5, niche-specific)
```

**Thumbnail text formula:** State the outcome, not the topic.
- ✅ "ChatGPT applied to 500 jobs for me 😳"
- ✅ "5 Secret Settings for ChatGPT 🤯"
- ❌ "How to use ChatGPT for productivity"
Pattern: `[Number] [secret/hidden] X for [tool] 🤯` or `[X] just [killed/changed] [Y] 🤯`

**One keyword per reel** matching the DM payload.

**Serialization:** pt1/pt2 numbering builds returning viewers — "Things you didn't know 
you could do with AI pt12" creates habit. Establish a series name from pt1.

---

**What to update (Mode C — large task):**

**1. `data/kb/viral_reel_formula.md`**
The `## @mavgpt caption formula` section already exists (added in a prior session). 
Verify it is present. No edit needed if it's there.

**2. `prompts/repurposing_agent.md`**
Find the section that generates Instagram captions. Update it to use mavgpt structure:
- Caption line 1 MUST be the comment→DM CTA
- Caption body MUST include the full value (prompts/list) verbatim — not a teaser
- Hashtags: 4–5 max, niche-specific (DS: #datascience #ai #chatgpt #python #dataanalyst)
- If no IG caption section exists, add one

**3. `scripts/lib/virality.py`** (DS niche path)
After the existing virality block is built, also construct a `mavgpt_caption` field:
```python
mavgpt_caption = {
    "cta_line": f'Comment "{keyword}" and I\'ll send you {payload_description} 👆',
    "claim_line": claim,          # one-line proof/specific result
    "value_items": value_list,    # list of strings — the actual prompts/steps/items
    "hashtags": niche_hashtags,   # 4-5 tags
}
```
Return this alongside the existing virality block. Generators can use it for IG caption output.

**4. CREATE `data/kb/reels/mavgpt_formula.md`** (reference file)
Document the formula with real examples from their reels:
- The 3 caption structures (list / prompt set / tool recommendation)
- Thumbnail text formulas that work
- Serialization pattern
- Their hashtag clusters by topic
- What makes the caption save-worthy (complete, actionable, screenshottable)

**Voice & guardrails for Tarun's content:**
- Never "In conclusion / Dive into / Leverage / Game-changer / Synergy"
- Never "until last week / including me" — Tarun is a 10-year data scientist; frame from 
  expertise ("I've seen", "I teach", "I reviewed"), not personal ignorance
- Caption value must be UNIVERSALLY APPLICABLE (not situation-specific)
- Honesty guardrail: state what the tool/template actually does, never overclaim
- Serialization: DS reel series should be named "Prompt Anatomy pt1", "DS Tools pt1", etc.

**After completing the edits:**
- Run a quick diff to confirm changes
- Update docs/ if any pipeline behavior changed
- Do NOT update the annual tracker — this is a pipeline change, not a content publish
