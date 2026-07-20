---
title: "DESIGN.md — Life & Self-Development Niche"
type: kb
niche: life_self_dev
slug: design
tags: [content/kb, niche/life_self_dev]
---
# DESIGN.md — Life & Self-Development Niche
# Version: V2 (HyperFrames + Remotion pipeline)
# Purpose: Machine-consumable look bible. Every beat builder reads this verbatim.
# DO NOT PARAPHRASE. Use exact values as specified.

---

## IDENTITY

Channel: @breathoflife_ (YouTube) / @mistakenlyhuman (Instagram)
Niche: Self-development, habits, mindset, honest personal take. Hinglish raw takes (4×/week additive lane).
Feel: Intimate + warm + honest. Casey Neistat vlog energy meets Notion thought journal.
Never: Motivational-poster clichés, hustle-culture tone, empty affirmations.

---

## PALETTE

Use ONLY these colors. No improvisation.

| Role | Hex | Usage |
|---|---|---|
| Background warm | `#1a1208` | Default canvas (when no video) |
| Background mid | `#231a0e` | Card backgrounds |
| Primary text | `#fdf8f0` | All body text, captions |
| Accent amber | `#f59e0b` | Highlights, emotional peak words |
| Accent warm red | `#ef4444` | Strong emphasis, kinetic slams |
| Accent sage | `#86efac` | Calm moments, resolution beats |
| Muted text | `#a0856a` | Labels, secondary info |
| Overlay tint | `rgba(245, 158, 11, 0.05)` | Warm amber cast over video |
| Glass card bg | `rgba(35, 26, 14, 0.85)` | Overlay card backgrounds |
| Glass card border | `rgba(245, 158, 11, 0.18)` | Card borders |

---

## TYPOGRAPHY

Use ONLY these fonts. Verify they are available in the renderer.

| Role | Font | Weight | Size (1080p) |
|---|---|---|---|
| Display / hook title | `Playfair Display` | 700 (Bold) | 72–96px |
| Body / subtitle | `Inter` | 400 (Regular) | 32–40px |
| Emphasis word (kinetic) | `Playfair Display` | 900 (Black) | 120–200px |
| Caption text | `Inter` | 500 (Medium) | 28–34px |
| Pull-quote | `Playfair Display` | 400 (Italic) | 44–60px |

Letter-spacing: `-0.01em` for display, `0.02em` for body.
Line-height: `1.3` for display, `1.6` for body.

Fallback display: `'Georgia', 'Times New Roman', serif`
Fallback body: `'SF Pro Text', 'Helvetica Neue', Arial, sans-serif`

---

## MOTION LANGUAGE

GSAP easing — use EXACT cubic-bezier values.

| Name | Value | Use case |
|---|---|---|
| Gentle settle | `cubic-bezier(0.25, 0.46, 0.45, 0.94)` | Text fades, default enter |
| Warm bounce | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Emotional peaks, kinetic slam |
| Slow breathe | `cubic-bezier(0.0, 0.0, 0.2, 1)` | Contemplative transitions |
| Sharp reveal | `cubic-bezier(0.16, 1, 0.3, 1)` | Fast cuts, point-by-point reveal |

Default durations:
- Element enter: `0.6s` (slower than DS — more breathing room)
- Element exit: `0.4s`
- Kinetic slam: `0.3s` in, `2.0s` hold
- Transition between beats: `0.8s`
- Pull-quote: `1.0s` fade in

---

## COLOR GRADE

Applied as a CSS filter on the base video layer.

```css
filter: contrast(1.05) saturate(1.22) brightness(1.03) hue-rotate(-5deg);
```

Additional amber overlay: `rgba(245, 158, 11, 0.05)` at full frame, `mix-blend-mode: screen`.

Remotion EditPlan fields:
```json
{
  "look": "cinematic",
  "colorGrading": {
    "contrast": 1.05,
    "saturate": 1.22,
    "brightness": 1.03,
    "hueRotate": -5
  }
}
```

---

## ALLOWED CATALOG BLOCKS

ONLY use blocks from this list. Do not invent block names. If a block name is not on this list, do not use it.

### Opening beat (choose ONE per video)
- `morph-text` — title cycles through related words before landing (e.g., "discipline" → "consistency" → "freedom")
- `aurora-title` — large title over animated aurora colour orbs; for high-energy or aspiration-themed content
- Atmospheric full-bleed: vignette + grain-overlay + slow fade-in title (built from grain-overlay + vignette blocks)

### Caption styles (choose ONE for the ENTIRE video — do not mix)
- `editorial-emphasis` — key insight words 2–3× bigger, dual-font blend. DEFAULT for Life.
- `particle-burst` — keyword words trigger colored particle explosions at emotional peaks. Use ONLY for high-energy raw takes.
- `kinetic-word-pop` — each word pops in with fast scale spring; use for punchy motivational content.
- `ethereal-word-reveal` — words float up gently with soft glow; use for contemplative or quiet moments.

### Emotional peak moments
- `kinetic-slam` — single powerful word fills full screen. Maximum 3 times per video.
- `parallax-layers` — behind-subject 3D text for strong pull-quotes
- `emoji-pop` — stroked text + emoji integration. Use for lighter moments only.
- `spotify-card` — if referencing a specific mood or song

### Side panel overlays (talking head remains visible alongside)
- `pull-quote` — large pull-quote text with attribution (`panel-right`) ← RIGHT so speaker face stays visible on left
- `handwritten-annotation` — marker-style hand-drawn callout, slight rotation (`panel-right`); for personal annotations and aside thoughts
- `liquid-glass-panel` — iOS 26-style frosted glass panel for stat or context (`panel-right`)
- `ar-masking-text` — text revealed via gradient mask, woven into footage (`panel-right`)
- `neo-brutalism-card` — thick bordered card for bold life assertions (`panel-top`)

### Atmospheric overlays (ALWAYS ON throughout video — no exceptions)
- `grain-overlay` — film grain, opacity `0.05`. Must be present for entire duration.
- `vignette` — edge darkening, pulls focus inward. Must be present for entire duration.

### Atmospheric (optional — add when thematically appropriate)
- `aurora-gradient` — 3–4 flowing colour orbs; use for aspirational or transformational content
- `analog-film-overlay` — grain + vignette + colour desaturation in one layer; enhances cinematic feel for emotional pieces

### Transitions
- `light-leak` — warm cinematic leak. DEFAULT between thoughts.
- `whip-pan` — fast pan cut. Use between section breaks.
- `domain-warp-dissolve` — fractal noise, meditative. Use for contemplative closing.
- `flash-through-white` — energy shift. Use for before/after moments or mindset shifts.

### Lower third / floating callouts
- `lower-third` — dark bar + name/title slides up; use when introducing a quote source or speaker context
- `lower-third-minimal` — thin accent line + text; use for subtle contextual labels
- `floating-pill-badge` — floating annotation pill at top-center (`pill-top`); for callouts that don't block the face

### Outro
- `instagram-follow` — animated profile + follow button card
- `morph-text` landing on CTA word (use the same morph-text block as opening, different text)

---

## OVERLAY DENSITY RULES

- Maximum overlay coverage: **40% of total video runtime**
- `grain-overlay` and `vignette` are atmospheric constants — they do NOT count toward the 40% cap
- `kinetic-slam`: maximum **3 uses per video**, only at genuinely powerful emotional peaks
- `editorial-emphasis` captions: ALWAYS active
- Minimum gap between non-atmospheric overlays: **8 seconds** of bare (grained/vignetted) talking head
- No overlay should last longer than **6 seconds** (except grain/vignette/captions)

---

## LAYOUT

All overlays: 1920×1080 @ 30fps.

- `fullscreen`: Default for atmospheric overlays, opening beat, kinetic slams.
- `panel-right`: RIGHT half (~900×960px). DEFAULT for ALL side panels — pull-quote, handwritten-annotation,
  liquid-glass-panel, ar-masking-text, neo-brutalism-card. Speaker face visible on left. Never use panel-left
  (it hides the centered camera subject behind the panel).
- `panel-left`: DO NOT USE for talking-head content — it covers the speaker's face when camera is centered.

New position zones (v4):
- `lower-third`: full-width bottom strip (1920×270px). Use with `lower-third` and `lower-third-minimal` blocks.
- `pill-top`: floating pill near top-center (~800×100px). Use with `floating-pill-badge`.

Captions: `editorial-emphasis` style, lower 25% of frame, never covering face.

---

## CAPTION SPEC

Sync captions to word timestamps from transcript.json.

Style: `editorial-emphasis` (default) — key words rendered at 2× normal size, mixed sans+humanist
Position: bottom center, 100px from bottom edge
Max line length: 6 words per line
Default font: Inter 500, 30px, `#fdf8f0`
Emphasis word font: Playfair Display 700, 60px, `#f59e0b` (amber)
Background: `rgba(26, 18, 8, 0.80)` pill, 10px border-radius, 14px padding
Do NOT show more than 2 lines simultaneously.

Emphasis trigger: words that are:
- Quantified (numbers, percentages, time spans)
- Emotionally loaded (shame, fear, love, pride, freedom, failure)
- The single most important word in the sentence (editor judgment)

---

## SHORT-FORM OVERRIDES
# These settings apply INSTEAD OF the sections above when manifest.format = "reel".
# Base identity, palette, typography, and motion language stay the same.

### Canvas
- Width: 1080px, Height: 1920px (9:16 vertical)
- fps: 30
- Duration: 30–90 seconds (45s target; 60s for emotional stories)

### Platform safe zones
- Top: y > 120px
- Bottom: y < 1620px
- Left: x > 120px
- Right: x < 960px
- Caption safe zone: y 900px–1500px

### Beat structure (LOCKED)
Exactly 5 beats:
1. **HOOK** (0–3s): Vulnerable or provocative opener. "I used to think discipline meant suffering."
2. **PROBLEM** (3–8s): The feeling they're in right now. Specific and honest.
3. **TURN** (8–28s): What changed. The insight or shift. Personal example, not advice.
4. **PAYOFF** (28–35s): How it feels on the other side. Earned, not preachy.
5. **CTA** (35–45s): ONE action. "Comment 'SYSTEM' and I'll send you the template."

### Overlay density (short-form)
- Up to **65%** of runtime may have overlays
- Captions: ALWAYS burned in — emotional content hits harder when the words are visible
- `grain-overlay` and `vignette`: KEEP for short-form Life — they're the brand feel even in Reels
- Keep grain at opacity 0.05 (slightly lower than long-form for small screens)

### Allowed blocks for short-form (fullscreen only)
- `morph-text` — opening hook only (morph 2–3 words before landing)
- `kinetic-slam` — maximum 2 uses; single word at emotional peak (fullscreen)
- `editorial-emphasis` — captions (key words 2× size)
- `grain-overlay` — always on, full duration, opacity 0.05
- `vignette` — always on, full duration
- `light-leak` — between beats 2→3 (the turn moment)
- `flash-through-white` — between beats 3→4 only
- `instagram-follow` — final CTA beat (animated follow button)
- `morph-text` — outro CTA landing word

**DROP for short-form:** `parallax-layers`, `spotify-card`, `emoji-pop`, `pull-quote`,
`domain-warp-dissolve` (too slow), `whip-pan` (wrong energy for Life), all `panel-*` layouts.

### Motion pacing (short-form)
- Element enter: `0.45s` (Life stays slower than DS even in short-form)
- Element exit: `0.30s`
- Between beats: `0.5s`
- `kinetic-slam`: `0.25s` in, `1.5s` hold (shorter than long-form)
- The emotional quality of Life content requires slightly more breathing room than DS reels

### Caption spec (short-form — editorial-emphasis, center-screen)
- Style: `editorial-emphasis` (key words 2× size, sans + humanist mix)
- Position: y 1000–1450px, horizontally centered
- Default font: Inter 500, 40px, `#fdf8f0`
- Emphasis word font: Playfair Display 700, 80px, `#f59e0b`
- Background: `rgba(26, 18, 8, 0.82)` pill, 12px radius
- Max line length: 5 words per line
- 1 line at a time for beats 1–3; up to 2 lines for beats 4–5
- Emphasis trigger: emotionally loaded words AND any word the user stresses vocally (Whisper confidence spike)

---

## BANNED IN LIFE CONTENT

- Cold blue tones — that's DS niche
- Code blocks or terminal windows
- Data charts / flowcharts
- Technical jargon without explanation
- Heavy glitch transitions — that's DS niche
- Matrix-decode captions
- Bullet lists as overlays (Life content is narrative, not informational)
