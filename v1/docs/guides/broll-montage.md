# B-roll Ken Burns montage renderer (`lib/broll_montage.py`)

Renders a voiceover-lane EditPlan's `brollCues` into a finished montage MP4 with
**ffmpeg** — a standalone replacement for the (currently absent) Remotion
`VoiceoverEdit` composition. Created 2026-07-01.

## Why

`render_week.py` renders `VoiceoverShort` / `VoiceoverLong` from `remotion/`, but that
Remotion project/composition is **not present in the repo** — so the voiceover B-roll
montage never actually rendered. `prepare_voiceover_edit.py` still writes a valid
EditPlan (`brollCues` + `audioFile` + `outputSize`); this renderer consumes that same
plan and produces the montage directly, no Remotion dependency.

## What it does

For each cue (in order), it:

1. **Cover-crops** the clip to the target frame (`scale=…:force_original_aspect_ratio=increase,crop`) — always full-bleed, never letterboxed, for any source aspect.
2. Applies a subtle **Ken Burns punch-in** (`zoompan`, 12% depth), alternating zoom-in / zoom-out per slot so consecutive clips don't feel identical.
3. **Cross-dissolves** between slots (`xfade`, 0.4s) — offsets derived from each cue's `startSec` so the montage length stays equal to the audio.
4. **Muxes** the voiceover (`audioFile`) and trims to audio length.

Output sizes: `9x16 → 1080×1920`, `16x9 → 1920×1080`, `1x1 → 1080×1080` (from the plan's `outputSize`).

## Usage

CLI (consumes the EditPlan that `prepare_voiceover_edit.py` writes):

```bash
python3 -m lib.broll_montage \
  --plan   remotion/public/edit-plans/2026-W27/<slug>.json \
  --public-root remotion/public \
  --out    assets/hyperframes/2026-W27/<slug>/montage.mp4
```

Library:

```python
from lib.broll_montage import render_montage_from_plan
render_montage_from_plan(plan_path, public_root, out_path)
```

## Wiring into the voiceover lane

**Wired (2026-07-01).** `run_voiceover_week.py`'s `render()` now calls
`render_montage_from_plan()` instead of `npx remotion render` (the Remotion project is
absent). It produces the montage base for both long-form (`VoiceoverLong` → 16x9) and
shorts (`VoiceoverShort` → 9x16); the output size comes from the plan's `outputSize`.
Captions and overlays are still layered on afterward by `hyperframes()`.

Caveat: Remotion overlay *scenes* (`scenePlanFile`) are not applied by the montage
renderer — that was the Remotion composition's job. Captions and the hyperframes
overlays still render. If you want the animated scene overlays back, add them to the
montage step or reinstate a Remotion project.

## Validated

2-clip montage (Eiffel + Louvre, the real W25 clips) → `1080×1920`, `6.0s`, AAC audio
muxed, full-bleed cover confirmed, Ken Burns + crossfade applied. `py_compile` clean.

## Tunables

`CROSSFADE_SEC` (0.4), `ZOOM_MAX` (1.12), `FPS` (30) at the top of the module.
