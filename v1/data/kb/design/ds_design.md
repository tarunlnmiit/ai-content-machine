---
title: "DESIGN.md — Data Science / Tech Niche"
type: kb
niche: data_science_tech
slug: design
tags: [content/kb, niche/data_science_tech]
---
# DESIGN.md — Data Science / Tech Niche
# Version: V2 (HyperFrames + Remotion pipeline)
# Purpose: Machine-consumable look bible. Every beat builder reads this verbatim.
# DO NOT PARAPHRASE. Use exact values as specified.

---

## IDENTITY

Channel: @breathofdatascience (YouTube) / @mistakenlyhuman (Instagram)
Niche: Data Science, Python, AI/ML tooling, build-in-public
Feel: Technical + authoritative + high-information-density. Fireship speed, 3Blue1Brown clarity, personal voice.
Never: Tutorial-dump, overwhelming, jargon without context.

---

## PALETTE

Use ONLY these colors. No improvisation.

| Role | Hex | Usage |
|---|---|---|
| Background dark | `#0a0e1a` | Default canvas when no video |
| Background mid | `#111827` | Card backgrounds, overlays |
| Primary text | `#f0f4ff` | All body text, captions |
| Accent blue | `#3b82f6` | Highlights, CTA buttons, number callouts |
| Accent cyan | `#06b6d4` | Code syntax, stat accents |
| Accent purple | `#8b5cf6` | Secondary accents, gradients |
| Muted text | `#64748b` | Labels, secondary info |
| Code green | `#22c55e` | Terminal output, success states |
| Code red | `#ef4444` | Errors, warnings |
| Overlay tint | `rgba(59, 130, 246, 0.04)` | Subtle blue cast over video |
| Glass card bg | `rgba(17, 24, 39, 0.85)` | Overlay card backgrounds |
| Glass card border | `rgba(59, 130, 246, 0.2)` | Card borders |

---

## TYPOGRAPHY

Use ONLY these fonts. Verify they are available in the renderer.

| Role | Font | Weight | Size (1080p) |
|---|---|---|---|
| Display / hook title | `Inter` | 800 (ExtraBold) | 72–96px |
| Body / stat label | `Inter` | 500 (Medium) | 32–40px |
| Caption text | `Inter` | 600 (SemiBold) | 28–34px |
| Code (inline) | `JetBrains Mono` | 400 | 28–36px |
| Code (block) | `JetBrains Mono` | 400 | 22–28px |
| Number / KPI | `Inter` | 900 (Black) | 80–120px |

Letter-spacing: `-0.02em` for display, `0` for code.
Line-height: `1.2` for display, `1.5` for body.

Fallback stack if Inter unavailable: `'SF Pro Display', 'Helvetica Neue', Arial, sans-serif`
Fallback code: `'Fira Code', 'Roboto Mono', monospace`

---

## MOTION LANGUAGE

GSAP easing — use EXACT cubic-bezier values. No shorthand aliases (different renderers interpret them differently).

| Name | Value | Use case |
|---|---|---|
| Fast snap | `cubic-bezier(0.16, 1, 0.3, 1)` | Element enters |
| Elastic settle | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Number counters, emphasis |
| Smooth exit | `cubic-bezier(0.4, 0, 1, 1)` | Element exits |
| Linear | `cubic-bezier(0, 0, 1, 1)` | Progress bars, sweeps |

Default durations:
- Element enter: `0.4s`
- Element exit: `0.25s`
- Transition between beats: `0.6s`
- Number count-up: `1.2s`
- Sweep/scan effect: `0.8s`

---

## COLOR GRADE

Applied as a CSS filter on the base video layer (or passed to EditPlan.colorGrading).

```css
filter: contrast(1.12) saturate(0.95) brightness(1.02) hue-rotate(8deg);
```

Additional blue overlay: `rgba(59, 130, 246, 0.04)` at full frame, `mix-blend-mode: screen`.

Remotion EditPlan fields:
```json
{
  "look": "none",
  "colorGrading": {
    "contrast": 1.12,
    "saturate": 0.95,
    "brightness": 1.02,
    "hueRotate": 8
  }
}
```

---

## ALLOWED CATALOG BLOCKS

ONLY use blocks from this list. Do not invent block names. If a block name is not on this list, do not use it.

### Opening beat (choose ONE per video)
- `code-particle-assemble` — GPU particles fly to form title/key stat
- `code-3d-extrude` — syntax-highlighted code on lit 3D slab
- `vfx-text-cursor` — cursor glow + chromatic shadow rays (use for AI/tool topics)

### Caption styles (choose ONE for the ENTIRE video — do not mix)
- `gradient-fill` — gradient-clipped text, elastic bounce. DEFAULT for DS.
- `matrix-decode` — character scramble before word reveals. Use for AI/security topics.

### Code + terminal moments
- `code-morph` — one snippet transforms to another (comparing approaches)
- `code-highlight-sweep` — highlight band sweeps across a specific line
- `code-typing` — token-streamed reveal for dramatic intro to solution
- `apple-terminal-homebrew` — macOS Homebrew terminal block
- `apple-terminal-clear-dark` — dark terminal block
- `code-shader-dissolve` — GPU dissolve reveal for dramatic code drops

### Data + stats moments
- `data-chart` — animated bar+line chart, NYT-style typography, staggered reveal
- `flowchart` — animated decision tree with sticky-note nodes
- `number-flow` — animated counter for KPIs / stat callouts
- `hud-callout` — HUD-style data panel with scan lines and corner brackets (`panel-right`)
- `bento-data-grid` — 2×2 metric tile grid, label + large number per cell (`panel-right`)
- `pill-stat` — single KPI in a floating centered pill; great for punchy stat delivery (`pill-center`)

### Enhanced overlays (modern UI treatments)
- `liquid-glass-panel` — iOS 26-style frosted glass panel alongside speaker (`panel-right`)
- `neo-brutalism-card` — thick bordered offset card for bold assertions (`panel-top`)
- `ar-masking-text` — text revealed via gradient mask, woven into footage (`panel-right`)
- `kinetic-word-pop` — energetic word-by-word pop with accent on key word; alternative caption style for fast punchy beats

### Lower third / floating callouts
- `lower-third` — dark bar + name/title slides up from bottom; use when introducing a concept or speaker role
- `lower-third-minimal` — thin accent line + text, no background bar; for subtle contextual labels
- `floating-pill-badge` — floating annotation pill at top-center; context callout without blocking face (`pill-top`)

### Transitions (between sections)
- `glitch` — digital glitch cut (use between fast-paced sections)
- `whip-pan` — fast pan cut (use between consecutive points)
- `cinematic-zoom` — slow push-in (use for intro to main content)

### Outro
- `logo-outro` — piece-by-piece assembly, glow bloom, URL pill
- `yt-lower-third` — subscribe overlay, animated
- `macos-notification` — CTA notification banner; use `corner-pip` layout (ONLY for DM-funnel reels)

### Atmospheric (optional, use sparingly)
- `shimmer-sweep` — accent sweep on key phrase in title
- `analog-film-overlay` — grain + vignette + colour shift combined; use ONLY for cinematic B-roll moments (NOT standard DS long-form)

---

## OVERLAY DENSITY RULES

- Maximum overlay coverage: **35% of total video runtime** (not every moment needs decoration)
- No overlay should last longer than **8 seconds** (except caption track which is always on)
- Minimum gap between overlays: **5 seconds** of bare talking head
- Code overlays: trigger ONLY when you are actively discussing code or a terminal command
- Data overlays: trigger ONLY when citing a specific number, stat, or architecture decision
- Caption track: ALWAYS active throughout the full video

---

## LAYOUT

All overlays: 1920×1080 @ 30fps.

Panel layouts when overlay shares screen with talking head:
- `panel-right`: right ~900×960px. Use for code blocks, data panels, liquid-glass overlays.
- `panel-top`: top ~1860×480px. Use for data charts and bold assertion cards.
- `fullscreen`: entire canvas. Use for opening beat, transitions, fullframe code blocks, outro only.

New position zones (v4):
- `lower-third`: full-width bottom strip (1920×270px). Use with `lower-third` and `lower-third-minimal` blocks.
- `pill-top`: floating pill near top-center (~800×100px). Use with `floating-pill-badge`.
- `pill-center`: floating pill at vertical center (~1536×120px). Use with `pill-stat`.
- `corner-pip`: small box at bottom-right (~440×210px). Use with `macos-notification`.

Captions: always at bottom center, never covering face.

---

## CAPTION SPEC

Sync captions to word timestamps from transcript.json.

Style: `gradient-fill` (default) or `matrix-decode` (see above)
Position: bottom center, 80px from bottom edge
Max line length: 7 words per line
Font: Inter 600, 30px, `#f0f4ff`
Background: `rgba(10, 14, 26, 0.75)` pill, 8px border-radius, 12px padding
Do NOT show more than 2 lines simultaneously.

---

## SHORT-FORM OVERRIDES
# These settings apply INSTEAD OF the sections above when manifest.format = "reel".
# The base identity, palette, typography, and motion language stay the same.
# Only the layout, timing, density, and caption rules change.

### Canvas
- Width: 1080px, Height: 1920px (9:16 vertical)
- fps: 30
- Duration: 30–90 seconds (45s target; maximum 90s)

### Platform safe zones (do NOT place content outside these bounds)
- Top: y > 120px (status bar)
- Bottom: y < 1620px (Instagram CTA strip, YouTube subscribe button)
- Left: x > 120px (Instagram like/comment column)
- Right: x < 960px (safe margin)
- Caption safe zone: y 900px–1500px (lower-center, above platform UI)

### Beat structure (LOCKED — do not deviate for short-form)
Exactly 5 beats. No more, no less.
1. **HOOK** (0–3s): Bold claim or question. Hard cut. No slow intro.
2. **PROBLEM** (3–8s): Name the pain the viewer feels right now.
3. **REVEAL + PROOF** (8–28s): What it is + show it working. Screen-record or code block.
4. **PAYOFF** (28–35s): Why it matters / the result.
5. **CTA** (35–45s): ONE action. "Comment 'FLOW' and I'll DM you."

### Overlay density (short-form)
- Up to **70%** of runtime may have overlays (viewers expect visual density in Reels)
- Captions: ALWAYS burned in — 85% of Reels are watched muted, no exceptions
- Grain and atmospheric overlays: NOT used in DS short-form (too slow-feeling)

### Allowed blocks for short-form (fullscreen only — NO panel layouts)
- `code-particle-assemble` — opening hook only
- `code-typing` — for revealing a command or key line
- `apple-terminal-clear-dark` — screen-record replacement for terminal output
- `code-highlight-sweep` — sweep over the key line as you say it
- `data-chart` — single stat or chart, fullscreen
- `number-flow` — KPI counter for big numbers
- `matrix-decode` — captions (replaces gradient-fill at short-form speed)
- `glitch` — between beats only
- `whip-pan` — between beats only
- `yt-lower-third` — final CTA beat
- `macos-notification` — DM-funnel CTA at end (DM keyword callout)

**DROP for short-form:** `flowchart`, `code-3d-extrude`, `code-shader-dissolve`, `logo-outro`,
all `panel-*` layouts, `shimmer-sweep`, `cinematic-zoom`.

### Motion pacing (short-form — faster than long-form)
- Element enter: `0.25s` (not 0.4s)
- Element exit: `0.15s` (not 0.25s)
- Between beats: `0.3s` (not 0.6s)
- Number count-up: `0.8s` (not 1.2s)
- Hard cuts preferred over transitions in beats 1–3

### Caption spec (short-form — burned in, center-screen)
- Style: `matrix-decode` (character-scramble reveal, fast — 0.15s per word)
- Position: center of safe zone — y 1100–1400px, horizontally centered
- Font: Inter 700 (Bold), 46px, `#f0f4ff`
- Background: `rgba(10, 14, 26, 0.85)` pill, 10px radius, 16px padding
- Max line length: 5 words per line
- Display: word-by-word sync to voice timestamps
- NEVER more than 1 line at a time for beats 1–3; up to 2 lines for beats 4–5

---

## BANNED IN DS CONTENT

- Warm color tones (orange, red gradients) — that's Life niche
- Heavy grain overlay — that's Poetry niche
- Emoji in captions
- All-caps body text (titles/KPIs only)
- Comic Sans, Papyrus, Courier New
- Anything that looks like a Google Slides default
