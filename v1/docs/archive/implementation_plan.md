# Implementation Plan: Professional Video Pipeline V2

**Goal:** Record → fully automated, unattended pipeline → MP4 output at 10-year experienced video editor quality for all three niches (DS, Life, Poetry).  
**Status:** Awaiting approval before execution.

---

## Current State → Target State

| Axis | Current | Target |
|---|---|---|
| Trimming | ffmpeg silence detection (crude — cuts silence only) | video-use skill (word-level: filler words, retakes, pauses) |
| Overlay generation | Custom Python glass-card HTML (`hyperframes_render.py`) | HyperFrames V2 compositions via skills (50+ catalog blocks) |
| Overlay quality | 15 element types, no catalog, no GSAP | Full catalog: Code Morph, Code Particle Assemble, Shader transitions, Liquid Glass, 15 caption styles |
| Creative pipeline | Transcript → overlays in one Claude call | 7-step: DESIGN → SCRIPT → STORYBOARD → VO+TIMING → BUILD (sub-agents/beat) → VALIDATE |
| Remotion | Custom compositions generated from training data | Remotion skill installed; Claude writes correct React with API knowledge |
| Per-niche quality | Shared element types across all niches | Distinct per-niche quality spec (DS: code + data; Life: editorial + emotional; Poetry: cinematic + texture) |
| Assembly | Remotion handles everything (TalkingHeadEdit) | video-use trim → HyperFrames overlays → Remotion title/outro → Palmier final composite |

---

## New Pipeline Architecture

```
Raw Recording (talking head MOV or voiceover WAV)
         ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 1: TRIM  (video-use skill)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Whisper word-level transcript (on raw, unedited)
• Filler word removal: "um", "uh", "so" (sentence-start only), "like" (filler), "you know"
• Retake detection: visual filmstrip composite — auto-select latest clean take
• Silence removal: gaps > 300ms trimmed to 80ms (natural breathing retained)
• 30ms audio cross-fades at every cut
• Output: trimmed.mp4 (talking head) or trimmed.wav (voiceover)
         ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 2: TRANSCRIBE (on trimmed output)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Whisper large-v3 → transcript.json (word-level timestamps on trimmed output)
• Extract SCRIPT.md from transcript (hook, story, proof, CTA structure)
         ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 3: DESIGN + STORYBOARD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Load pre-built DESIGN.md for niche (data/kb/design/{niche}_design.md)
• Claude generates STORYBOARD.md:
    - Identifies beats from transcript (topic shifts, emphasis moments, key stats)
    - Selects HyperFrames catalog blocks per beat (niche-specific — see specs below)
    - Assigns caption style for entire video
    - Specifies transition between each beat
    - Selects B-roll keywords for voiceover videos
         ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 4: BUILD (sub-agents per beat)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• One focused sub-agent per storyboard beat
• Each writes a valid HyperFrames HTML composition:
    - data-composition-id, data-width/height, data-start, data-duration, data-track-index
    - GSAP timeline registered on window.__timelines
    - Catalog blocks installed via: npx hyperframes install <block>
• Embedded-captions composition (synchronized to transcript.json, niche caption style)
• Remotion compositions: title card, chapter markers, outro (transparent background)
         ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 5: VALIDATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• npx hyperframes lint (structure checks, missing attributes, GSAP conflicts)
• npx hyperframes validate (headless Chrome: runtime errors, missing assets)
• npx hyperframes snapshot --at [beat midpoints] (visual verification PNGs)
• Auto-fix loop: if lint/validate fails → targeted sub-agent repair pass (max 2 retries)
         ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 6: RENDER + ASSEMBLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• npx hyperframes render → overlays.mp4 (1920×1080 @ 30fps)
• Remotion render → titlecard.mp4, outro.mp4 (transparent via greenscreen flag)
• Final assembly (ffmpeg or Palmier MCP):
    - Talking head: trimmed.mp4 + overlays.mp4 composite + titlecard + outro
    - Voiceover: B-roll montage + narration.wav + overlays.mp4 + titlecard + outro
• Output: assets/video/{week}/{slug}_final.mp4
```

---

## Per-Niche Quality Specifications (10-Year Editor Standard)

### DS Niche
**Feel:** Technical, authoritative, high-information-density. Like Fireship or 3Blue1Brown but personal.

**Caption style:** `gradient-fill` (gradient-clipped text, elastic bounce) or `matrix-decode` (character scramble before reveal — signals technical content)

**Opening beat:**
- `code-particle-assemble` (GPU particles fly to form the title/key stat)
- OR `code-3d-extrude` (syntax-highlighted code on lit 3D slab)
- `shimmer-sweep` accent on key phrase

**Code moments (whenever code/terminal is discussed):**
- `code-morph` — one snippet transforms into another when comparing approaches
- `code-highlight-sweep` — highlight band sweeps to specific line as you discuss it
- `code-typing` — token-streamed reveal for dramatic intro to a solution
- Terminal blocks: `apple-terminal-homebrew` or `apple-terminal-clear-dark`
- `code-shader-dissolve` — GPU dissolve for dramatic code reveals

**Data / stats moments:**
- `data-chart` — animated bar+line chart with NYT-style typography, staggered reveal
- `flowchart` — animated decision tree for architecture diagrams, sticky-note nodes
- Counter animation for numbers (kinetic stat callout tied to word timestamp)
- `us-map` or `world-map` if geographic data is referenced

**Transitions between sections:**
- `glitch` or `chromatic-radial-split` (technical energy)
- `cinematic-zoom` (intro to content)
- `whip-pan` (fast cut between points)

**Outro:**
- `logo-outro` (piece-by-piece assembly, glow bloom, URL pill with UTM link)
- `yt-lower-third` (subscribe overlay, animated)
- `macos-notification` (CTA notification banner if DM-funnel reel)

**Color grade:** High contrast, cold-blue. `contrast(1.12) saturate(0.95) brightness(1.02) hue-rotate(8deg)`. Overlay: `rgba(80, 140, 255, 0.04)`.

**B-roll keywords:** terminal, code editor, data visualization, dark screen, programming, laptop screen, neural network, pipeline, dashboard, algorithm

---

### Life Niche
**Feel:** Intimate, warm, honest. Casey Neistat vlog meets Notion thought journal.

**Caption style:** `editorial-emphasis` (key insight words 2–3× bigger, dual-font — sans + humanist) or `particle-burst` (keyword words trigger colored particle explosions at emotional peaks)

**Opening beat:**
- `morph-text` — title cycles through related words before landing (e.g., "discipline" → "consistency" → "freedom")
- OR atmospheric full-bleed with `vignette` + `grain-overlay` + slow fade-in title

**Key emotional moments:**
- `parallax-layers` — behind-subject 3D text for strong pull-quotes
- `kinetic-slam` — single powerful word full-screen at emotional peak
- `emoji-pop` — lighter moments, stroked text with emoji integration
- `spotify-card` — if referencing a mood or song

**Transitions:**
- Between thoughts: `light-leak` (cinematic, warm) or `flash-through-white` (energy shift)
- Section breaks: `whip-pan`
- Contemplative closing: `domain-warp-dissolve` (fractal noise, meditative)

**Atmospheric overlays (always on):**
- `grain-overlay` throughout (opacity 0.04–0.06)
- `vignette` (edges darkened, pulls focus inward)

**Outro:**
- `instagram-follow` card (animated profile + follow button)
- `morph-text` landing on CTA word

**Color grade:** Warm, cinematic. `contrast(1.05) saturate(1.22) brightness(1.03) hue-rotate(-5deg)`. Overlay: `rgba(255, 160, 80, 0.05)`.

**B-roll keywords:** sunrise, journal, coffee, walking, hands writing, city street, quiet room, books, window light, person thinking, morning routine

---

### Poetry Niche
**Feel:** Cinematic, deliberate, contemplative. Every word earns its frame. Like spoken word produced by A24.

**Caption style:** `weight-shift` (elegant font-weight transition between lines, slow and deliberate) or `texture` with `marble` texture mask over large uppercase text

**Opening beat:**
- `vfx-text-cursor` (cursor glow, chromatic shadow rays, spectral color edges on black stage)
- OR existing Remotion `LineReveal` composition (keep — it works well for poetry)

**Line-by-line delivery:**
- `clip-wipe` — left-to-right wipe reveal, word by word, synced to voice timestamps
- `blend-difference` — auto-inverting text (black/white flip against background)
- `handwritten-reveal` (existing Remotion scene — keep for poem lines)
- Long holds: 2–3s between lines; poetry breathes

**Full-screen moments:**
- `kinetic-slam` — single key word fills the entire screen
- No information clutter; one word or one line at a time

**Atmospheric overlays (always on):**
- `grain-overlay` heavy (opacity 0.08–0.12)
- `vignette` heavy (near-black at edges)
- `liquid-background` for abstract floating feel behind text (slow ripple)

**Transitions:**
- `domain-warp-dissolve` (fractal noise — slow, meditative — DEFAULT)
- `sdf-iris` (iris reveal — for dramatic stanza breaks)
- `cinematic-zoom` for intensity moments

**Outro:**
- Slow `vignette` fade-to-black
- Minimal `logo-outro` (no URL pill for poetry — wrong tone)

**Color grade:** Cinematic, desaturated. `contrast(1.08) saturate(0.85) brightness(0.96) hue-rotate(0deg)`. Overlay: `rgba(120, 80, 200, 0.04)` (subtle purple). `look: "poetry"` activates existing letterbox + duotone.

**B-roll keywords:** rain, candle, empty street, fog, hands, sky at dusk, reflection in water, old books, solitude, autumn leaves, silence

---

## Files to Create / Modify

### New files
```
scripts/run_video_pipeline.py          # Master entry point (replaces prepare_remotion_edit.py + run_voiceover_week.py for new pipeline)
scripts/video_trim.py                  # video-use skill integration for filler/retake/silence removal
scripts/hyperframes_pipeline.py        # HyperFrames V2 orchestrator (replaces hyperframes_render.py)
scripts/lib/storyboard_gen.py          # Claude: transcript → STORYBOARD.md (beat-by-beat, niche-aware)
scripts/lib/hf_beat_builder.py         # Sub-agent per beat → valid HyperFrames HTML composition
scripts/lib/hf_validator.py            # npx hyperframes lint/validate/snapshot wrapper + auto-fix loop
data/kb/design/ds_design.md            # DS niche DESIGN.md (brand cheat sheet, reused every video)
data/kb/design/life_design.md          # Life niche DESIGN.md
data/kb/design/poetry_design.md        # Poetry niche DESIGN.md
```

### Modified files
```
scripts/prepare_remotion_edit.py       # Add deprecation notice; keep as legacy fallback
scripts/hyperframes_render.py          # Add deprecation notice; keep as legacy fallback
docs/video-production-guide.md         # Update to reflect V2 pipeline
docs/voiceover-runner.md               # Update to use run_video_pipeline.py
docs/weekly-operating-guide.md         # Update tool commands section
CLAUDE.md                              # Update pipeline description
```

### Directory layout changes
```
assets/hyperframes/{week}/{slug}/
  ├── DESIGN.md              (copied from data/kb/design/ for niche)
  ├── SCRIPT.md              (extracted from transcript)
  ├── STORYBOARD.md          (Claude-generated per video)
  ├── transcript.json        (word-level from Whisper on trimmed output)
  ├── trimmed.mp4            (or trimmed.wav for voiceover)
  ├── compositions/
  │   ├── beat-1-hook.html
  │   ├── beat-2-story.html
  │   ├── captions.html      (embedded-captions composition)
  │   └── ...
  ├── snapshots/             (validation PNGs from npx hyperframes snapshot)
  └── renders/
      └── overlays.mp4
```

---

## New Master Script Interface

```
python3 scripts/run_video_pipeline.py \
  --raw assets/raw/2026-06-24_life_self_dev_habits.MOV \
  --niche life \
  --slug 2026-06-24_life_self_dev_habits \
  [--voiceover]           # raw is audio-only, not talking-head
  [--intensity standard]  # overlay density: minimal | light | standard | dense
  [--force]               # overwrite existing outputs

All 6 phases run automatically. No manual stops.
Takes 10–20 minutes depending on video length and intensity level.
Final output: assets/video/{week}/{slug}_final.mp4
```

---

## One-Time Setup (manual, before running)

```bash
# In v1/ directory:
npx skills add heygen-com/hyperframes --all    # All HyperFrames skills as Claude Code slash commands
npx create-video@latest                         # Remotion Claude Code skill
pip install video-use --break-system-packages   # OR: install as Claude Code skill from browser-use/video-use
```

---

## Implementation Phases (execution order)

**Phase 1 — Foundation** (enables all downstream work)
1. Create `data/kb/design/` directory and write three DESIGN.md files (DS, Life, Poetry)
2. Write `scripts/lib/storyboard_gen.py`
3. Write `scripts/lib/hf_beat_builder.py`
4. Write `scripts/lib/hf_validator.py`
5. Write `scripts/hyperframes_pipeline.py`

**Phase 2 — Trimming**
6. Write `scripts/video_trim.py` (video-use integration)

**Phase 3 — Master Script**
7. Write `scripts/run_video_pipeline.py`

**Phase 4 — Docs**
8. Update docs (video-production-guide, voiceover-runner, weekly-operating-guide)
9. Update CLAUDE.md pipeline description

---

## What Will NOT Change

- Whisper transcription (already working)
- B-roll fetching (`fetch_videos.py` + Pexels/Pixabay)
- All content generation scripts (reel briefs, blog pipeline, idea scorer)
- Staging + scheduling (`load_posts.py`, `scheduler.py`)
- Instagram/LinkedIn auto-publish
- Existing `TalkingHeadEdit` Remotion composition (deprecated in Phase 3 only)

---

## Key Questions Before Execution

1. **video-use as Python package or Claude Code skill?**  
   It's a Claude Code skill (`browser-use/video-use`). This means it runs inside a Claude Code session, not as a standalone Python call. Alternative: wrap video-use's ffmpeg + Whisper logic in `video_trim.py` as a pure Python implementation. **Recommendation:** Python implementation for `video_trim.py` (faster, no CLI dependency) using video-use's documented approach (Whisper → word-level cuts → ffmpeg).

2. **Palmier MCP for final assembly or ffmpeg?**  
   Palmier MCP requires the app to be running. For a fully automated pipeline, ffmpeg is more reliable. **Recommendation:** use ffmpeg for compositing (overlay.mp4 over trimmed.mp4); reserve Palmier MCP for manual review/adjustment after auto-render.

3. **"so" removal:** Only "so" at sentence-start (pause before it). "So" mid-sentence is kept. Confirm filler list: `["um", "uh", "so" (sentence-start), "like" (filler), "you know", "basically", "literally", "right" (trailing)]`.

4. **Retake auto-select:** Default = pick latest clean take (the last attempt before moving on). Confirm.
