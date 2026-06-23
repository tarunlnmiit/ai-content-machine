# Canva Thumbnail Prompt — 2026-05-27_poetry_quotes_intoxicated-senses

Niche: Breath of Poetry | Hook: LOVE HAS TAKEN AWAY MY SENSES

Paste into Claude Cowork or run via `claude --print`:

```
Generate a YouTube thumbnail using the Canva MCP.

CANVA QUERY:
YouTube thumbnail for 'Breath of Poetry' channel (@breathofpoetry). Hook text (DOMINANT — must fill ≥35% of canvas width, bold, huge): "LOVE HAS TAKEN AWAY MY SENSES". Background: #1E1B2E dark navy. Accent: #B89850. Pop color: #a78bfa. Font: Playfair Display, extra-bold. Visual style: editorial, premium, literary — poetry book cover. Leave a prominent clear zone (40–60% of frame, left or right) with contrasting bg for a face photo to be added manually. Left/right split composition: face one side, giant hook text other side. NO diagrams. NO charts. NO framework boxes. NO 'Tutorial X/Y' numbering. Hook text readable at 120px wide (mobile thumbnail size). Modern, high-contrast, 5%+ CTR design.

EXECUTE these steps in order:
1. Call generate-design with:
   - design_type: "youtube_thumbnail"
   - brand_kit_id: "kAHIa-g_t3o"
   - query: the CANVA QUERY above
   (do NOT use generate-design-structured — that is presentations only)

2. From the returned candidates, pick the one that best shows:
   - Dark navy background
   - Large bold hook text dominating one side
   - Clear face zone on the other side

3. Call create-design-from-candidate with the chosen candidate_id and job_id.

4. Call export-design with:
   - design_id from step 3
   - format: {"type": "png", "width": 1280, "height": 720, "export_quality": "pro"}

5. Output:
   - PNG download URL → user saves to: /Users/tarungupta/Making It Big/Claude/content-machine/output/visuals/2026-W22/2026-05-27_poetry_quotes_intoxicated-senses_thumb_canva.png
   - Canva edit URL → user opens to swap in reaction face photo
   - Design ID for future edits

```
