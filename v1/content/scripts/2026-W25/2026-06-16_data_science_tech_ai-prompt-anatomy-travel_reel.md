# Reel Script — "I interrogated an AI for travel secrets" (Prompt Anatomy)

**Niche:** Data Science / Tech · **Format:** talking-head reel + screen-record proof
**Source blog:** `content/blogs/2026-W25/2026-06-16_data_science_tech_ai-prompt-anatomy-travel.md`
**Slug:** `2026-06-16_data_science_tech_ai-prompt-anatomy-travel`
**Length target:** 38–45s (trims to 30s) · **Pace:** 140–160 wpm
**Formula:** `data/kb/viral_reel_formula.md` (5 beats) · **Hooks:** `data/kb/twitter_hook_patterns.json`

> Non-negotiables (from the formula): captions burned in (85% watch muted), cut on every sentence
> (no clip > ~4s), hard cut at 0–3s, trending audio low under voice, end on the result (loop bait).
> **Honesty guardrail:** this is a real prompt technique — show the actual output. No overclaim.

---

## HOOK — 0–3s (record 5×, keep the winner)

Hard cut. Face to camera, big burned-in caption. Test these 3, ship the strongest:

1. **Contrarian Mirror (lead):**
   > "I stopped Googling travel guides. I interrogated an AI instead."
   *Caption:* `I STOPPED GOOGLING TRAVEL GUIDES.`

2. **Bold Declaration:**
   > "I turned ChatGPT into a Parisian historian with one prompt."
   *Caption:* `ONE PROMPT = A PRIVATE HISTORIAN`

3. **Data / Mechanism:**
   > "5 lines. That's the difference between a postcard and the real Paris."
   *Caption:* `5 LINES → THE REAL PARIS`

---

## PROBLEM — 3–8s

Face to camera, quick.

> "Ask it 'best things to do in Paris,' you get the Eiffel Tower and the Louvre — the same
> ten things on every list. The model isn't failing you. Your prompt is."

*Caption:* `THE MODEL ISN'T FAILING YOU — YOUR PROMPT IS.`

---

## REVEAL + PROOF — 8–28s

VO over **screen-record B-roll** of the real ChatGPT session (zoomed for mobile). One cut per part,
≤4s each. Build the prompt on screen line by line, then reveal the output table.

> "So I gave it a job in 5 parts.
> **Role** — historian, not chatbot.
> **Task** — three lesser-known sites, with the era and the address.
> **Exclude** — no Eiffel Tower, no top-10 lists.
> **Format** — a table, not a wall of text.
> **Verify** — two sources each, flag conflicts, no making things up."

*Captions (sequential):* `1 ROLE` · `2 TASK` · `3 EXCLUDE` · `4 FORMAT` · `5 VERIFY`

**Shot list (beat 3):**
- 3a: paste the role line → screen
- 3b: task line appears
- 3c: exclusion line appears (highlight "No Eiffel Tower")
- 3d: format line appears
- 3e: verify line appears
- 3f: **payoff shot** — the hidden-gems markdown table renders (the proof). Zoom the rows.

---

## PAYOFF — 28–35s

Back to face, confident.

> "It stopped being a chatbot and started being a guide. Same model everyone has —
> I just stopped asking like a tourist."

*Caption:* `STOP ASKING LIKE A TOURIST.`

---

## CTA — 35–45s (ONE action)

Face, point-down framing, handle on screen.

> "Comment **PROMPT** and I'll DM you the whole thing — copy-paste ready."

*Caption:* `COMMENT "PROMPT" 👇  @mistakenlyhuman`

**End on the table still on screen (loop bait) — not on "bye."**

---

## CTA wiring (lead magnet + UTM)

- **Keyword:** `PROMPT` → comment→DM via **SuperProfile** / **CreatorFlow** (free comment→DM, ManyChat
  replacements). Pin a comment with the keyword prompt.
- **DM payload:** the full assembled prompt (verbatim, below) **+** one UTM link.
- **UTM links** (built with `scripts/lib/utm.py`; campaign `prompt-anatomy`, content
  `2026-06-16_prompt-anatomy`). ⚠️ `BASE_URL` is a **placeholder** until the Medium blog publishes —
  swap the base, keep the params.
  - **IG DM:** `…/ai-prompt-anatomy-travel?utm_source=instagram&utm_medium=dm&utm_campaign=prompt-anatomy&utm_content=2026-06-16_prompt-anatomy`
  - **YT Shorts (desc line 1):** `…?utm_source=youtube&utm_medium=short&utm_campaign=prompt-anatomy&utm_content=2026-06-16_prompt-anatomy`
  - **TikTok (bio):** `…?utm_source=tiktok&utm_medium=reel&…`
  - **X (final tweet):** `…?utm_source=twitter&utm_medium=thread&…`

### Per-platform CTA delta (same footage)
| Platform | CTA | Link mechanic |
|---|---|---|
| **IG Reel** | "Comment PROMPT — I'll DM it." | comment→DM + pinned comment |
| **YT Shorts** | "Full prompt in the description." | link line 1 of desc + pinned comment, `#Shorts` in title |
| **TikTok** | "Link in bio / comment PROMPT." | link-in-bio |
| **X** | hook tweet → 5-part thread → link in final tweet | native link |

---

## DM payload — full assembled prompt (paste verbatim)

```
You are an expert architectural historian and Paris travel guide with
decades of experience uncovering overlooked historical sites. You know
the hidden streets, palaces, chapels, and mansions that most tourists
ignore. Provide context about each site's architectural significance,
era, and historical anecdotes. Think like a local historian who also
loves storytelling.

Identify and recommend three lesser-known historical sites in Paris.
Include palaces, mansions, small chapels, or minor museums that rarely
appear in mainstream travel guides. For each site, provide its official
name, location (district/arrondissement), architectural style, era of
construction, and one unique feature that makes it worth visiting.
Include links to official sources, Wikipedia, or heritage databases
for verification.

Do not include extremely popular landmarks such as Notre-Dame,
the Eiffel Tower, Sacré-Cœur, the Louvre, or Musée d'Orsay.
Exclude sites that appear in the top 10 tourist lists or are
heavily photographed on social media. Focus on hidden gems with
historical, architectural, or cultural significance that tourists
regularly miss. Prioritize publicly accessible and verifiable sites.

Return all results in a Markdown table with columns:
Name (linked to source) | Location (arrondissement and street)
| Style/Era | Key Feature | Historical Anecdote | Why it's unique.
Include concise explanations for each column. Limit text to
practical, informative summaries while keeping it engaging.

Verify each recommended site against at least two reliable sources
such as Wikipedia, official heritage websites, or local historical
records. Provide links. If sources conflict, note discrepancies
and mention the most widely accepted details. Avoid unverified
or speculative entries.
```

---

## Post-film checklist
- [ ] Hook recorded 5×, winner picked
- [ ] Screen-record proof captured (5 part-lines + the table render, zoomed)
- [ ] 5 beats present, ≤45s, captions burned in
- [ ] Honesty held (real technique, real output shown)
- [ ] CTA = one keyword `PROMPT`; comment→DM armed
- [ ] UTM base swapped to live blog URL on publish
- [ ] Derivatives → Metricool CSV (`prompts/repurposing_agent.md` → `scripts/derivatives_to_metricool.py`)
- [ ] Shorts meta (`scripts/generate_shorts_meta.py --slug <clips-slug>`)

**Banned words check:** no "Dive into / Leverage / Game-changer / Synergy / In conclusion." ✅
