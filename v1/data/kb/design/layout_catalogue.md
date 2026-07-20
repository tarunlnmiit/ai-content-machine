---
title: "Layout Catalogue — HyperFrames Beat Library"
type: kb
slug: layout-catalogue
tags: [content/kb]
---
# Layout Catalogue — HyperFrames Beat Library
# Version: v4 (52 blocks · 9 position zones)
# Machine-readable. Storyboard generator reads this at runtime.
# DO NOT PARAPHRASE. Block names are exact — used verbatim in JSON storyboards.

---

## OVERVIEW

Every beat is defined by TWO choices:
1. **block_type** — what the visual looks like (the 52 blocks below)
2. **layout** — where on screen it appears (the 9 zones below)

Alpha blocks (most) overlay the talking head with transparency (MOV).
Full-frame blocks replace the video frame entirely for their duration (WebM).

---

## POSITION ZONES

| Zone | Pixel rect (1920×1080) | Description |
|---|---|---|
| `fullscreen` | (0, 0, 1920, 1080) | Entire canvas — opening beats, transitions, outro |
| `panel-right` | (980, 60, 1880, 1020) | Right 50% — code/data alongside talking head |
| `panel-left` | (40, 60, 940, 1020) | Left 50% — pull-quotes, annotations alongside speaker |
| `panel-top` | (60, 40, 1860, 520) | Top 50% — charts, cards above talking head |
| `panel-bottom` | (60, 560, 1860, 1040) | Bottom 50% — rarely used; prefer lower-third |
| `lower-third` | (0, 810, 1920, 1080) | Full-width bottom strip (~270px) — name bars, titles |
| `pill-top` | (560, 20, 1360, 120) | Floating narrow pill at top-center (~800×100px) |
| `pill-center` | (192, 480, 1728, 600) | Floating narrow pill at vertical center (~1536×120px) |
| `corner-pip` | (1440, 830, 1880, 1040) | Small box at bottom-right corner (~440×210px) |

For portrait (1080×1920) reels all coordinates are re-computed proportionally at runtime.

---

## BLOCK CATALOGUE

### Opening / Title  (choose ONE per video)

| Block | Layout | Type | Niches | Description |
|---|---|---|---|---|
| `code-particle-assemble` | fullscreen | full-frame | DS | GPU particles assemble into title/key stat |
| `code-3d-extrude` | fullscreen | full-frame | DS | Syntax-highlighted code on lit 3D slab |
| `apple-terminal-clear-dark` | fullscreen | full-frame | DS | macOS dark terminal block |
| `apple-terminal-homebrew` | fullscreen | full-frame | DS | macOS Homebrew terminal block |
| `aurora-title` | fullscreen | full-frame | Life, Poetry | Large title over animated aurora colour orbs |
| `morph-text` | fullscreen | alpha | Life | Title word cycles (discipline→freedom) then lands |
| `kinetic-slam` | fullscreen | alpha | Life, DS | Single powerful word slams to centre, scale 3→1 |
| `vfx-text-cursor` | fullscreen | alpha | DS, Poetry | Cursor glow types out text, chromatic shadow rays |

### Caption / Text Overlay  (choose ONE style for the ENTIRE video — do not mix)

| Block | Layout | Type | Niches | Description |
|---|---|---|---|---|
| `editorial-emphasis` | fullscreen | alpha | Life | Key insight words 2–3× bigger, dual-font blend. Life DEFAULT |
| `weight-shift` | fullscreen | alpha | Poetry | Elegant font-weight transition between lines. Poetry DEFAULT |
| `gradient-fill` | fullscreen | alpha | DS | Gradient-clipped text, elastic bounce. DS DEFAULT |
| `matrix-decode` | fullscreen | alpha | DS | ASCII scramble resolves into caption text. DS/AI topics |
| `clip-wipe` | fullscreen | alpha | Poetry | Left-to-right clip-path wipe reveals each word |
| `kinetic-word-pop` | fullscreen | alpha | DS, Life, Poetry | Each word pops in scale 0.6→1.1→1 with fast stagger |
| `ethereal-word-reveal` | fullscreen | alpha | Poetry, Life | Words float up y+20, opacity 0→1, gentle glow |
| `particle-burst` | fullscreen | alpha | Life | Keyword words trigger coloured particle explosions |
| `blend-difference` | fullscreen | alpha | Poetry | Invert-blend text (black/white flip) — dramatic contrast |
| `texture-marble` | fullscreen | alpha | Poetry | Uppercase text masked with marble/paper texture |
| `emoji-pop` | fullscreen | alpha | Life | Oversized stroked emoji bursts punctuate beats |

### Data / Code Panels  (trigger ONLY when actively discussing code/data)

| Block | Layout | Type | Niches | Description |
|---|---|---|---|---|
| `code-highlight-sweep` | panel-right | alpha | DS | Syntax-highlighted code with glowing sweep bar |
| `code-typing` | panel-right | full-frame | DS | Token-streamed typewriter code reveal |
| `code-morph` | panel-right | alpha | DS | One snippet morphs/transforms into another |
| `code-shader-dissolve` | fullscreen | alpha | DS | GPU dissolve reveal for dramatic code drops |
| `flowchart` | panel-right | full-frame | DS | Animated decision tree with path-traced nodes |
| `data-chart` | panel-top | full-frame | DS | NYT-style animated bar/line chart with stagger |
| `number-flow` | panel-right | alpha | DS | Large KPI counter rolls from 0 to target value |
| `hud-callout` | panel-right | alpha | DS | HUD data panel — scan lines, corner brackets, monospace |
| `bento-data-grid` | panel-right | alpha | DS | 2×2 grid of metric tiles (label + large number per cell) |

### Side Panel Overlays  (talking head remains visible alongside)

| Block | Layout | Type | Niches | Description |
|---|---|---|---|---|
| `pull-quote` | panel-left | alpha | Life | Large pull-quote text with attribution line |
| `handwritten-annotation` | panel-left | alpha | Life | Marker-style hand-drawn callout, slight rotation |
| `spotify-card` | panel-right | alpha | Life | Spotify-style mood card with track/vibe info |
| `liquid-glass-panel` | panel-right | alpha | DS, Life, Poetry | iOS 26 frosted glass panel — subtle blur + border glow |
| `ar-masking-text` | panel-right | alpha | DS, Life, Poetry | Text revealed via gradient mask, appears woven into footage |
| `neo-brutalism-card` | panel-top | alpha | DS, Life, Poetry | Thick solid border + offset box-shadow card, bold mono labels |

### Atmospheric  (always-on overlays — do not count toward density cap)

| Block | Layout | Type | Niches | Description |
|---|---|---|---|---|
| `grain-overlay` | fullscreen | alpha | Poetry, Life | Film grain texture, opacity 0.05–0.12 (always-on) |
| `vignette` | fullscreen | alpha | Poetry, Life | Dark edge vignette (always-on — pulls focus inward) |
| `light-leak` | fullscreen | alpha | Life | Warm organic light leak flash between thoughts |
| `liquid-background` | fullscreen | alpha | Poetry | Abstract slow ripple behind text (voiceover-only frames) |
| `parallax-layers` | fullscreen | alpha | Life | Multi-depth background layers shift on motion |
| `aurora-gradient` | fullscreen | alpha | Life, Poetry | 3–4 large colour orbs animating slowly in background |
| `analog-film-overlay` | fullscreen | alpha | DS (sparingly), Life, Poetry | Grain + vignette + colour desaturation in one layer |
| `shimmer-sweep` | fullscreen | alpha | DS | Accent light sweep across key phrase in title |

### Transitions  (short, between beats or sections)

| Block | Layout | Type | Niches | Description |
|---|---|---|---|---|
| `domain-warp-dissolve` | fullscreen | alpha | Poetry | Fractal noise dissolve (1.2s). Poetry DEFAULT transition |
| `sdf-iris` | fullscreen | alpha | Poetry | Iris wipe via signed-distance function (use max 1×/video) |
| `flash-through-white` | fullscreen | alpha | DS, Life, Poetry | Hard white flash cut — before/after or mindset shift |
| `whip-pan` | fullscreen | alpha | DS, Life, Poetry | Motion-blur whip pan between consecutive points |
| `glitch` | fullscreen | alpha | DS | Pixel displacement + RGB split (between fast sections) |
| `cinematic-zoom` | fullscreen | alpha | DS, Life | Ken Burns push-in (for intro to main content section) |

### Lower Third / Strip  (anchored to bottom of frame — layout: lower-third)

| Block | Layout | Type | Niches | Description |
|---|---|---|---|---|
| `lower-third` | lower-third | alpha | DS, Life, Poetry | Dark bar + name + title line slides up from bottom |
| `lower-third-minimal` | lower-third | alpha | DS, Life, Poetry | Thin accent line + text; no background bar; minimal |
| `yt-lower-third` | lower-third | alpha | DS, Life | YouTube-style subscribe / channel bar animation |
| `instagram-follow` | lower-third | alpha | Life, DS | Instagram follow CTA with animated follow button |

### Floating / Corner  (small overlays that don't dominate the frame)

| Block | Layout | Type | Niches | Description |
|---|---|---|---|---|
| `floating-pill-badge` | pill-top | alpha | Life, DS | Floating annotation pill at top-center — context callout |
| `pill-stat` | pill-center | alpha | DS | Single KPI in a centered pill with glow edge |
| `macos-notification` | corner-pip | alpha | DS | macOS toast notification in bottom-right corner |

### Outro  (always the final beat)

| Block | Layout | Type | Niches | Description |
|---|---|---|---|---|
| `logo-outro` | fullscreen | full-frame | DS, Life, Poetry | Logo assembly + glow bloom + URL pill + tagline |

---

## SELECTION RULES

### Niche defaults
- **DS**: `gradient-fill` captions, `panel-right` for code, `panel-top` for charts
- **Life**: `editorial-emphasis` captions, `fullscreen` default, `panel-left` for pull-quotes
- **Poetry**: `weight-shift` captions, `fullscreen` ONLY — never split-screen

### Hard constraints
- Caption style: ONE per video. Do not mix caption block types.
- `kinetic-slam`: DS/Life max 3×/video; Poetry max 2×/video
- `sdf-iris`: max 1×/video (Poetry only)
- Atmospheric blocks (`grain-overlay`, `vignette`) are ALWAYS ON for Life and Poetry — they are not counted as overlays
- `lower-third` blocks: use `lower-third` layout only
- `pill-*` blocks: use `pill-top` or `pill-center` layout only
- `macos-notification`: use `corner-pip` layout only
- Code/chart blocks: trigger ONLY when actively discussing code, data, or architecture

### Density caps by niche
| Niche | Long-form cap | Short-form cap |
|---|---|---|
| DS | 35% of runtime | 70% of runtime |
| Life | 40% of runtime | 65% of runtime |
| Poetry | 100% of runtime (captions = content) | 100% |

---

## ZONE VISUAL REFERENCE (1920×1080)

```
┌─────────────────────────────────────────────┐  ← (0,0)
│ [pill-top ──────────────── 800×100 ──────── ]│ y=20
│                                               │
│ [panel-left 940×960]    [panel-right 900×960] │ y=60
│                   ┌────────────────────────┐  │
│                   │ pill-center 1536×120   │  │ y=480
│                   └────────────────────────┘  │
│                                               │
│                              ┌──────────────┐ │
│                              │ corner-pip   │ │ y=830
├───────────────────────────────┤ 440×210     │ │
│ lower-third 1920×270          └──────────────┘ │ y=810
└───────────────────────────────────────────────┘  ← y=1080
```
