# Remotion Prompt-to-Motion-Graphics — Setup & Pipeline Guide

Remotion's official AI-powered motion graphics generator. Takes a text prompt and produces
a full Remotion composition. Used as an **alternative to `generate_custom_scene.py`** when
you need visually complex scenes (particle systems, 3D-adjacent effects, data flows) that
are hard to describe as component props.

## First-Time Setup

```bash
cd prompt-to-motion-graphics
npx create-video@latest .
# Choose: Prompt to Motion Graphics SaaS Starter Kit
npm install
```

Set your API key in `.env.local`:
```
OPENAI_API_KEY=sk-...
# or ANTHROPIC_API_KEY= if the template supports it
```

## Daily Use

```bash
cd prompt-to-motion-graphics && npm run dev   # http://localhost:3000
```

Enter a prompt describing the scene → the app generates a Remotion composition → preview it → export the TSX.

## Pipeline Integration — Two Paths

### Path A: Use as one-off scene (recommended)

1. Generate the scene in the app
2. Copy the generated `.tsx` to `remotion/src/compositions/scenes/MyScene.tsx`
3. Register it:
   ```bash
   python3 scripts/generate_custom_scene.py --name MyScene --prompt "description" --no-register
   # then manually verify the TSX, register in SceneRenderer.tsx
   ```
4. Add to `remotion/public/templates-map.json` `scene_components` so `generate_scene_plans.py` picks it up

### Path B: Use instead of generate_custom_scene.py

When `generate_scene_plans.py` outputs a `CUSTOM_SCENE_SLOT`, fill it using this app instead of the CLI:
1. Read the `CUSTOM_SCENE_SLOT` entry in the scene plan for context
2. Write a prompt based on that context, generate in the app
3. Follow Path A step 2–4

## When to Use This vs generate_custom_scene.py

| Scenario | Use |
|----------|-----|
| Need a scene matching chronixel design tokens | `generate_custom_scene.py` (Claude knows the tokens) |
| Need complex generative visuals (particle system, data flow, procedural animation) | Prompt-to-Motion-Graphics |
| Need fast iteration with visual preview | Prompt-to-Motion-Graphics |
| Need the scene auto-registered in SceneRenderer | `generate_custom_scene.py` |
