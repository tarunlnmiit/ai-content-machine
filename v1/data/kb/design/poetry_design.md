# DESIGN.md — Poetry / Quotes Niche
# Version: V2 (HyperFrames + Remotion pipeline)
# Purpose: Machine-consumable look bible. Every beat builder reads this verbatim.
# DO NOT PARAPHRASE. Use exact values as specified.

---

## IDENTITY

Channel: @breathofpoetry (YouTube) / @mistakenlyhuman (Instagram)
Niche: Poetry, spoken word, contemplative quotes. Original poems by Tarun Gupta.
Feel: Cinematic + deliberate + contemplative. Every word earns its frame. A24 production values for spoken word.
Never: Rushed, information-dense, decorative-for-decoration's-sake, Instagram poetry template aesthetics.

---

## PALETTE

Use ONLY these colors. No improvisation.

| Role | Hex | Usage |
|---|---|---|
| Background void | `#080808` | Default canvas — near-black, not pure black |
| Background mid | `#0f0f12` | Secondary surfaces |
| Primary text | `#f5f0eb` | Poetry text — slightly warm white |
| Accent purple | `#7c3aed` | Chromatic edges, spectral highlights |
| Accent silver | `#c8c8d4` | Subtitles, secondary text |
| Atmospheric fog | `rgba(80, 60, 120, 0.06)` | Subtle purple cast over video |
| Glass card bg | `rgba(15, 15, 18, 0.92)` | Card backgrounds (used rarely) |

Avoid bright saturated colors. Poetry palette should feel desaturated and withdrawn.

---

## TYPOGRAPHY

Use ONLY these fonts. Verify they are available in the renderer.

| Role | Font | Weight | Size (1080p) |
|---|---|---|---|
| Poem lines | `Cormorant Garamond` | 400 (Regular) | 56–80px |
| Poem lines (emphasis) | `Cormorant Garamond` | 600 (SemiBold Italic) | 60–84px |
| Kinetic slam word | `Cormorant Garamond` | 700 (Bold) | 180–260px |
| Title / opening | `Cormorant Garamond` | 300 (Light) | 64–80px |
| Attribution / byline | `Inter` | 300 (Light) | 24–28px |

Letter-spacing: `0.05em` for poem lines (open, breathable), `-0.01em` for kinetic slams.
Line-height: `1.8` for poem lines (poetry breathes), `1.0` for kinetic slams.

Fallback: `'Garamond', 'Georgia', 'Times New Roman', serif`
Attribution fallback: `'Helvetica Neue', Arial, sans-serif`

---

## MOTION LANGUAGE

GSAP easing — use EXACT cubic-bezier values. Poetry moves slowly.

| Name | Value | Use case |
|---|---|---|
| Breath in | `cubic-bezier(0.0, 0.0, 0.58, 1.0)` | Poem line enters |
| Breath out | `cubic-bezier(0.42, 0, 1.0, 1.0)` | Poem line exits |
| Deep settle | `cubic-bezier(0.16, 1, 0.3, 1)` | Opening title settle |
| Linear | `cubic-bezier(0, 0, 1, 1)` | Grain, warp, continuous effects |

Default durations — SLOWER than DS and Life:
- Poem line enter: `1.0s`
- Poem line exit: `0.8s`
- Hold between lines: `2.0–3.0s` (let the line breathe before revealing next)
- Kinetic slam: `0.4s` in, `2.5s` hold, `0.6s` exit
- Transition: `1.2s`
- Opening title: `2.0s` fade in

---

## COLOR GRADE

Applied as a CSS filter on the base video layer.

```css
filter: contrast(1.08) saturate(0.85) brightness(0.96) hue-rotate(0deg);
```

Additional purple overlay: `rgba(120, 80, 200, 0.04)` at full frame, `mix-blend-mode: screen`.

Remotion EditPlan fields:
```json
{
  "look": "poetry",
  "colorGrading": {
    "contrast": 1.08,
    "saturate": 0.85,
    "brightness": 0.96,
    "hueRotate": 0
  }
}
```

Note: `"look": "poetry"` activates the existing Remotion letterbox + duotone in TalkingHeadEdit.

---

## ALLOWED CATALOG BLOCKS

ONLY use blocks from this list. Do not invent block names. If a block name is not on this list, do not use it.

### Opening beat (choose ONE per video — or use existing Remotion LineReveal)
- `vfx-text-cursor` — cursor glow, chromatic shadow rays, spectral color edges on dark stage
- `aurora-title` — title over animated aurora orbs; ONLY with desaturated muted palette (no bright colour); for energetic spoken-word content only
- Remotion `LineReveal` composition — existing, proven. Preferred for most poems.

### Caption / line delivery styles (choose ONE for the ENTIRE video)
- `weight-shift` — elegant font-weight transition between lines, slow and deliberate. DEFAULT for Poetry.
- `ethereal-word-reveal` — words float up gently with soft glow; blur-to-clear. For quiet, introspective poems.
- `texture-marble` — uppercase text with marble texture. Use for dramatic poems only.
- `clip-wipe` — left-to-right wipe reveal, word by word, synced to voice timestamps. Use for narrative poems.
- `blend-difference` — auto-inverting text (black/white flip). Use sparingly, dramatic contrast poems only.
- `kinetic-word-pop` — fast spring pop; use MAXIMUM 1 word per video for the single most forceful word ONLY; combine with `weight-shift` (not a replacement for it).

### Line-by-line moments
- Remotion `HandwrittenReveal` — existing composition, use for poem lines (proven)
- `kinetic-slam` — SINGLE word fills entire screen at emotional peak. Maximum 2 per video.

### Atmospheric overlays (ALWAYS ON throughout entire video — non-negotiable)
- `grain-overlay` — heavy film grain, opacity `0.10`. MUST be present for entire duration.
- `vignette` — heavy edge darkening, near-black at edges. MUST be present for entire duration.
- `liquid-background` — abstract slow ripple behind text. Use ONLY when no talking head (text-only frames).

### Atmospheric (optional — for thematic videos)
- `aurora-gradient` — muted colour orbs animating slowly; ONLY with desaturated Poetry palette; for cosmic or existential poems; no bright saturation
- `analog-film-overlay` — combined grain + vignette + colour shift layer; reinforces the grain/vignette already present when a deeper cinematic atmosphere is needed

### Transitions
- `domain-warp-dissolve` — fractal noise dissolve, SLOW (1.2s). **DEFAULT transition between ALL stanzas.**
- `sdf-iris` — iris reveal for dramatic stanza breaks (use maximum once per video)
- `cinematic-zoom` — slow push-in for intensity moments

### Attribution (final frame only — lower-third zone)
- `lower-third-minimal` — thin accent line + attribution text; use ONLY for final frame (poet name, collection); `lower-third` layout. No other lower-third use.

### Outro
- Slow vignette fade-to-black (vignette opacity 0 → 1 over 2s, then black hold 1s)
- Minimal `logo-outro` — no URL pill (wrong tone for poetry), just logo mark + channel name
- No subscribe animations, no notification bells

---

## OVERLAY DENSITY RULES

- Maximum overlay coverage: **100% of video runtime** — captions are the content (different from DS/Life)
- `grain-overlay`, `vignette`: constant throughout — they are the visual environment, not overlays
- `kinetic-slam`: maximum **2 uses per video**, ONLY at the single most powerful word in the poem
- No information cards (charts, stats, code) — ever
- No lower thirds except minimal logo-outro
- Poetry is the opposite of information density: one word, one image, one feeling at a time

---

## LAYOUT

All overlays: 1920×1080 @ 30fps.

- `fullscreen`: Default for ALL poetry overlays. The text IS the frame.
- Never panel-left, panel-right, panel-top, panel-bottom — poetry is never split-screen.
- Never pill-top, pill-center, corner-pip — these add UI elements that conflict with the poetry aesthetic.
- `lower-third`: ONLY for `lower-third-minimal` attribution text on the final frame.
- The talking head (if present) is the background; text floats over it.

If voiceover-only: liquid-background behind text for full duration.

---

## CAPTION SPEC

Sync captions to word timestamps from transcript.json. In poetry, captions ARE the visual content.

Style: `weight-shift` (default) — one line at a time, font-weight transitions as new line enters
Position: vertical center of frame (not bottom) for full-screen delivery; bottom-center for talking head
Line display: ONE LINE AT A TIME — never two simultaneous lines
Max line length: 5 words per line (poetry lines are short)
Font: Cormorant Garamond 400, 60px, `#f5f0eb`
Emphasis: Cormorant Garamond 600 Italic for emotional peak words
Background: no background pill — text floats against the video/grain
Text shadow: `0 2px 20px rgba(0, 0, 0, 0.9)` for legibility
Hold time per line: match voice timestamp (Whisper word-end) + 800ms breathing pause

---

## SHORT-FORM OVERRIDES
# These settings apply INSTEAD OF the sections above when manifest.format = "reel".
# Base identity, palette, typography stay the same.
# Poetry short-form = the most deliberate reel on the platform. One image. One feeling.

### Canvas
- Width: 1080px, Height: 1920px (9:16 vertical)
- fps: 30
- Duration: 30–60 seconds (a short poem; 45s is ideal)

### Platform safe zones
- Top: y > 120px
- Bottom: y < 1620px
- Caption zone: y 600px–1400px (more centered than DS/Life — poetry is the whole frame)

### Beat structure (LOCKED — poetry uses a modified 5-beat)
1. **OPENING LINE** (0–5s): First line of the poem. No titles, no intro. Poem starts immediately.
2. **BODY — first half** (5–20s): Middle stanzas. One line at a time. Long holds.
3. **BODY — second half / turn** (20–35s): The emotional turn or reversal. Pacing slows further.
4. **CLOSING LINE** (35–42s): The final line. 3-second hold before next beat.
5. **SILENCE + LOGO** (42–50s): 2 seconds of near-silence with fading vignette, then minimal logo.

### Overlay density (short-form)
- Up to **100%** of runtime — captions ARE the visual content in poetry reels
- `grain-overlay` and `vignette`: ALWAYS ON, even heavier than long-form (opacity 0.12)
- This is the one niche where captions are not supplementary — they ARE the message

### Allowed blocks for short-form (fullscreen only — poetry is never split-screen)
- `weight-shift` — captions, full duration (default)
- `clip-wipe` — line-by-line left-to-right reveal (use for narrative poems)
- `grain-overlay` — always on, opacity 0.12
- `vignette` — always on, heavy (near-black at edges)
- `liquid-background` — behind text if voiceover-only (no talking head)
- `kinetic-slam` — MAXIMUM 1 use per reel; the single most powerful word only
- `vfx-text-cursor` — opening title if poem has a title card before first line
- `domain-warp-dissolve` — between stanzas (slow, 1.0s)
- `sdf-iris` — ONE dramatic stanza break maximum
- Existing Remotion `LineReveal` — preferred for most poem lines (proven, works)

**DROP for short-form:** anything not in the list above. Poetry reels are minimalist.

### Motion pacing (short-form — deliberately slower than DS and Life)
- Line enter: `0.8s` (same as long-form — poetry never rushes even in short-form)
- Line exit: `0.6s`
- Between stanzas: `1.0s` transition
- `kinetic-slam`: `0.35s` in, `2.0s` hold (a full moment)
- Hold between lines: at minimum match the voice timestamp + 600ms breathing pause
  (poetry is one of the few content types where silence is content)

### Caption spec (short-form — centered, one line at a time)
- Style: `weight-shift` (weight-transition as each line enters)
- Position: vertically centered between y 700–1300px
- Font: Cormorant Garamond 400, 68px, `#f5f0eb`
- Emphasis: Cormorant Garamond 600 Italic at emotional peak words
- Background: NONE — text floats against grain/video (text-shadow only)
- Text shadow: `0 2px 24px rgba(0, 0, 0, 0.95)`
- ONE LINE at a time. No exceptions in short-form.
- Max line length: 4 words (even shorter than long-form — small screen, big impact)

---

## BANNED IN POETRY CONTENT

- Blue color tones (DS niche color)
- Warm amber tones (Life niche color)
- Code blocks, terminal windows, data charts
- Bullet lists, numbered lists
- Fast glitch transitions
- Multiple words on screen simultaneously (one word/line at a time is the rule)
- Emoji
- Notification banners, subscribe animations
- Comic sans, any novelty fonts
- Bright, saturated backgrounds
