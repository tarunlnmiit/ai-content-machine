# Plan: Make Use of All 22 Free Remotion Templates + Creative Unlock Rule

## Context
Two inputs drive this plan:

1. **Template coverage** — `remotion/public/templates-map.json` tracks 8 Remotion templates. Remotion offers 22 free templates. User wants every template accounted for — nothing removed, missing ones added and put to use where they can genuinely serve the pipeline.

2. **Creative Unlock Rule** (`CLAUDE REMOTION BLUEPRINT/Resources/4. CREATIVE_UNLOCK_RULE_SIMPLE.docx`) — the scene-plan generator must act like a **creative director, not a caption generator**. Core rule: "Do not just follow the words. Find the deeper visual idea." Specifically: create visual metaphors, remove unnecessary text when the visual carries the message, don't make animated subtitles unless text is genuinely needed, don't treat every line as a separate caption moment, improve weak scene ideas instead of blindly executing them.

Today's generated overlays violate this rule — heavy on WordReveal (animated subtitles) and literal text restating the script. The rule must be baked into `generate_scene_plans.py` prompts, and new components must enable visual-first scenes (counters, drawn strokes, imagery) rather than more text variants.

Honest template assessment: 8 of the 22 are project scaffolding (Blank, Hello World, JavaScript, Next.js ×4, React Router 7) — starting points for new repos, not features. Their "use" is to be catalogued as known/not-applicable. The rest yield: 3 new visual-first scene components (built in this plan), 2 future infrastructure options (Recorder, Prompt to Motion Graphics — catalogued with integration notes), and 1 desktop render option (Electron — catalogued).

## Template Audit

### Already integrated (8)
| Template | Status |
|---|---|
| Code Hike | ✅ integrated → `CodeAnnotation` |
| TikTok Captions | ✅ integrated → `WordReveal`, `LineReveal` |
| Audiogram | ✅ integrated → `AudiogramFeed`, `AudiogramStory` |
| Music Visualization | ✅ integrated → reuses Audiogram |
| 3D | ✅ integrated → `AbstractDS/Life/Poetry` |
| Render Server | ✅ integrated → infrastructure |
| Stills | ✅ integrated → `Thumbnail`, `SocialCard*` |
| Overlay | ✅ integrated → `TitleCard`, `LowerThird`, `OutroCard` |

### Scaffolding — catalogue as not-applicable (8)
- Blank, Hello World, JavaScript — dev starter repos
- Next.js, Next.js (Vercel Sandbox), Next.js (No Tailwind), Next.js (Pages dir) — SaaS app starters
- React Router 7 — SaaS starter

### Missing with real use (6)
| Template | npm pkg | Use in pipeline | Niche |
|---|---|---|---|
| **Skia** | `@remotion/skia` + `@shopify/react-native-skia` | NEW scene component `HandwrittenReveal` — text drawn stroke by stroke on canvas | life, poetry |
| **Stargazer** | `remotion` (count-up pattern) | NEW scene component `CounterReveal` — animated number count-up with label, for stats/milestones | ds, life |
| **Prompt to Video** | none needed (pattern only) | NEW scene component `ImageTextReveal` — full-screen image + animated text overlay | life, poetry |
| **Prompt to Motion Graphics** | `anthropic` (already in env) | INTEGRATE — adapt its generate→compile→self-correct loop into a `CustomScene` pipeline: bespoke Remotion scenes generated from prompts when no catalog component fits | ds, life, poetry |
| **Recorder** | Remotion Recorder (standalone app) | INTEGRATE for Life + Poetry — webcam talking-head recording with built-in Whisper transcription and captions; replaces ad-hoc camera capture for those niches. Exports footage + captions that feed the existing edit pipeline | life, poetry |
| **Electron** | `electron` | Catalogue `not_applicable` — desktop render app; render server already covers batch rendering |  |

## What to Build

### Phase 1: templates-map.json entries (all 14 missing)
Add entries for all untracked templates with correct `status` (no existing entries removed or changed):
- `"not_applicable"` for scaffolding (Blank, Hello World, JS, Next.js×4, React Router 7, Electron) — with one-line reason each
- `"integrated"` for Skia, Stargazer, Prompt to Video — backed by the 3 new scene components built in Phase 2
- `"integrated"` for Prompt to Motion Graphics — backed by the CustomScene pipeline built in Phase 5
- `"integrated"` for Recorder — backed by the recording setup in Phase 6 (Life + Poetry niches)

### Phase 2: New scene components (3 new TSX files)

#### `HandwrittenReveal.tsx`
- Uses `@remotion/skia` canvas to draw text paths frame-by-frame
- Props: `lines: string[], niche: Niche`
- Layout: fullscreen (requires full width for legible canvas)
- Niche: life, poetry
- Duration: 5–8s per line
- File: `remotion/src/compositions/scenes/HandwrittenReveal.tsx`
- Package install: `npm install @remotion/skia @shopify/react-native-skia` in remotion/

#### `CounterReveal.tsx`
- Animated integer count-up from 0 to target value with label
- Uses `interpolate` + `spring` — no new package needed
- Props: `value: number, label: str, prefix?: str, suffix?: str, niche: Niche`
- Layout: fullscreen
- Niche: ds, life
- Duration: 4–6s
- File: `remotion/src/compositions/scenes/CounterReveal.tsx`

#### `ImageTextReveal.tsx`
- Full-screen background image (URL) + animated headline text overlay
- Uses Remotion's `<Img>` component — no new package needed
- Props: `imageUrl: str, headline: str, subtext?: str, niche: Niche`
- Layout: fullscreen
- Niche: life, poetry
- Duration: 5–8s
- File: `remotion/src/compositions/scenes/ImageTextReveal.tsx`

### Phase 3: Register new scene_components in templates-map.json
Add entries for `HandwrittenReveal`, `CounterReveal`, `ImageTextReveal` to `scene_components` array with correct props, niche_affinity, duration_hint.

### Phase 4: Register new components in SceneRenderer
`remotion/src/compositions/SceneRenderer.tsx` has the component registry — a `switch (plan.componentName)` block with one import + one case per component. New components need both an `import` at the top and a `case` in the switch.

### Phase 5: CustomScene pipeline (Prompt to Motion Graphics, adapted headless)
The Remotion template's core loop is: prompt → LLM generates Remotion/React code → compile → on compile error, feed error back to LLM and retry. Adapt this server-side for the pipeline:

**New script `scripts/generate_custom_scene.py`:**
- Input: `--prompt "visual description"`, `--scene-id`, `--niche`, `--week`, `--slug`
- Calls Claude API (`ANTHROPIC_API_KEY_FREE` from `.env`, model `claude-sonnet-4-6`) with a system prompt containing: chronixel style tokens (`COLORS`, `FONTS`, `nicheAccent`), the Creative Unlock Rule, Remotion constraints (use `useCurrentFrame`/`spring`/`interpolate`, no external assets, `AbsoluteFill` root, default export named `CustomScene_{sceneId}`)
- Writes generated TSX to `remotion/src/compositions/scenes/generated/{week}/{slug}/{sceneId}.tsx`
- Regenerates barrel file `remotion/src/compositions/scenes/generated/index.ts` mapping `"{slug}/{sceneId}"` → lazy component
- **Self-correction loop**: runs `npx tsc --noEmit` on the generated file; on errors, feeds compiler output back to Claude and retries (max 3 attempts) — same pattern as the template
- Errors after 3 attempts: scene is skipped with a clear warning, never crashes the render

**SceneRenderer support:**
- New `componentName: "CustomScene"` case in `SceneRenderer.tsx` — looks up `props.customSceneKey` in the generated barrel registry and renders it
- Generated registry imported statically (barrel regenerated before render, so bundling works)

**generate_scene_plans.py integration:**
- Catalog gains a virtual entry: `CustomScene` — "when NO catalog component can express the visual idea, describe the bespoke scene in props.prompt (visual description, not script text)"
- New post-processing step in `write_overlay()`: for each `CustomScene` scene, shell out to `generate_custom_scene.py` to materialize the component before the plan is saved
- Cap: max 2–3 CustomScenes per video (each costs an API call + compile loop)

### Phase 6: Recorder setup for Life + Poetry
Install Remotion Recorder as a sibling tool and wire it to the existing pipeline:
- `npx create-video@latest --recorder` into `recorder/` at repo root
- Configure output folder convention: recordings land in `assets/raw/` (existing convention), Whisper captions exported alongside
- Captions from Recorder (Whisper JSON) are compatible with the `captions/{week}/{slug}.captions.json` format used by `prepare_remotion_edit.py` — add a small conversion note/step if shape differs
- Document the Life/Poetry recording workflow: record talking head in Recorder → footage to `assets/raw/` → captions to `remotion/public/captions/{week}/` → existing edit pipeline takes over
- `niche_affinity: ["life", "poetry"]` in templates-map entry

### Phase 7: Embed Creative Unlock Rule in generate_scene_plans.py
Modify both `OVERLAY_INSTRUCTIONS` and `SHORT_INSTRUCTIONS` in `scripts/generate_scene_plans.py`:

Add a CREATIVE DIRECTION block (condensed from the docx) at the top of both prompts:
- "You are a creative director, not a caption generator. Do not just follow the words — find the deeper visual idea."
- Think per moment: What is this line really saying? What should the viewer feel? What visual makes it easier to understand? What motion makes it satisfying?
- Create visual metaphors when they explain the idea better than text.
- Remove unnecessary text when the visual carries the message.
- AVOID: recreating the script word-for-word on screen; animated subtitles unless text is genuinely needed; treating every line as a caption moment; cluttered over-explanation.
- Improve weak scene ideas instead of blindly executing them.

Concrete enforcement (so the rule has teeth, not just vibes):
- Cap WordReveal at ~20% of scenes per video — it is the "animated subtitle" the rule warns against.
- Prefer visual-first components (DataVizReveal, CounterReveal, HabitLoop, TransformationArc, ToolComparison, ImageTextReveal, HandwrittenReveal) for any moment that has structure, numbers, change, or comparison behind it.
- Keep the existing MIX REQUIREMENT (≥25% fullscreen, ≥25% panel) — it complements this.

### Phase 8: Update docs
Per project rule "UPDATE GUIDES ALWAYS": note new components, CustomScene pipeline, Recorder workflow (Life/Poetry), and creative rule in `docs/video-production-guide.md` (component catalog section) and `docs/daily/wednesday.md` if the overlay generation step gains the CustomScene flag.

## Files to Modify
1. `remotion/public/templates-map.json` — add 14 missing template entries + 4 new scene_components (3 fixed + CustomScene)
2. `remotion/src/compositions/scenes/HandwrittenReveal.tsx` — new file
3. `remotion/src/compositions/scenes/CounterReveal.tsx` — new file
4. `remotion/src/compositions/scenes/ImageTextReveal.tsx` — new file
5. `remotion/src/compositions/scenes/generated/index.ts` — new barrel (auto-regenerated)
6. `remotion/src/compositions/SceneRenderer.tsx` — add import + switch case for each new component + CustomScene case
7. `scripts/generate_custom_scene.py` — new script (prompt → TSX → tsc check → self-correct loop)
8. `scripts/generate_scene_plans.py` — embed Creative Unlock Rule, WordReveal cap, CustomScene virtual catalog entry + materialization step
9. `recorder/` — new Remotion Recorder install (Life + Poetry recording)
10. `docs/video-production-guide.md` — document new components + CustomScene + Recorder workflow + creative rule

## Verification (updated)
1. `cd remotion && npx tsc --noEmit` — no TypeScript errors
2. Remotion Studio preview of 3 new fixed components with sample props
3. `python3 scripts/generate_custom_scene.py --prompt "a clock dissolving into particles" --scene-id test-01 --niche life --week 2026-W24 --slug test` — verify TSX generated, compiles, appears in barrel
4. `generate_scene_plans.py --mode overlay` on a test script — verify new components + CustomScene appear, WordReveal share drops
5. Render a short test composition through render server

## Key Reuse
- `COLORS`, `FONTS`, `nicheAccent`, `nicheGrid` from `remotion/src/styles/chronixel.ts` — use for all new components (same as existing components)
- `spring`, `interpolate`, `useCurrentFrame`, `useVideoConfig` from `remotion` — standard animation hooks
- `Niche` type from `chronixel.ts`

## Verification
1. `cd remotion && npm run build` — verify no TypeScript errors
2. Open Remotion Studio (`npm run dev`) and preview each new component with sample props
3. Run `generate_scene_plans.py --mode overlay` on a test script and verify new components appear in generated overlays
