# Voiceover-First Runner (additive lane)

*Added 2026-06-21. This is an **additional** way to make videos — the talking-head pipeline
([weekly-runner.md](weekly-runner.md)) is unchanged and still the default. Pick per week.*

## What it is

You write the 3 blogs as usual, then record an **audio-only voiceover** per niche (no face on
camera). From each voiceover the pipeline produces, fully automatically:

- **1 long-form LANDSCAPE video** = full-screen B-roll montage + your voiceover + Remotion
  overlay scenes, then **hyperframes** (which also burns the captions).
- **N portrait SHORTS** from auto-detected self-complete sections — each with its own portrait
  B-roll + that audio slice + overlays + hyperframes.

Captions: rendered by **hyperframes**, not Remotion. The filler word **"so"** is dropped, and
captions sit **raised off the bottom** (`--caption-y`, default 0.70). Captions are optional
(`--no-captions`).

## One command per niche

```bash
python3 scripts/run_voiceover_week.py \
  --audio assets/audio/2026-W26/2026-06-22_ds_slug_voiceover.wav \
  --niche ds --week 2026-W26 --slug 2026-06-22_ds_slug
```

Flags: `--no-captions`, `--caption-y 0.70`, `--skip-shorts`, `--dry-run`.

Run it once per niche (ds / life / poetry). Outputs land in
`output/animations/{week}/{slug}.mp4` (long-form) and `…/{slug}_sNN.mp4` (shorts), then the
hyperframes versions under `assets/hyperframes/`.

## What it runs under the hood (in order)

1. `generate_captions.py` → `remotion/public/captions/{week}/{slug}.captions.json` (Whisper).
2. `generate_yt_script.py` → `content/scripts/{week}/{slug}_yt.md` (deliverable doc; NOT a B-roll source).
3. `generate_scene_plans.py --mode voiceover` → `scene-plans/{week}/{slug}_voiceover.json`
   (fullscreen / lower-third overlays only; keeps hook + shareable + CTA beats and virality).
4. `fetch_videos.py --captions … --orientation landscape --target-clips N` → landscape B-roll
   (keywords come from the **transcript**; clip count scales with duration).
5. `prepare_voiceover_edit.py … --output-size 16x9` → `edit-plans/{week}/{slug}.json`
   (`kind:"voiceover"`, audio + tiled B-roll montage + scene plan; no captions baked).
6. Render `VoiceoverLong` → hyperframes (captions burned here).
7. `detect_short_sections.py` → `content/derivatives/{week}/{slug}/short_sections.json`
   (variable count, 15–90s each, self-complete).
8. Per section: cut WAV + section captions subset → portrait B-roll (`--orientation portrait`)
   → voiceover scene plan → `prepare_voiceover_edit.py --output-size 9x16` → render
   `VoiceoverShort` → hyperframes.

## After the videos

Publishing is unchanged — continue with the normal pipeline (Medium publish, LinkedIn DS+Life
derivatives, `load_posts.py` → `scheduler.py`). This runner only builds the video assets.

## Key pieces

| Concern | File |
|---|---|
| Remotion composition (audio + montage + overlays) | `remotion/src/compositions/VoiceoverEdit.tsx` (`VoiceoverLong` / `VoiceoverShort`) |
| Render routing (`kind:"voiceover"`) | `scripts/render_week.py` |
| B-roll: transcript keywords + portrait | `scripts/fetch_videos.py` (`--captions`, `--orientation`, `--out-suffix`, `--target-clips`) |
| Overlay scene plans | `scripts/generate_scene_plans.py --mode voiceover` |
| YT script deliverable | `scripts/generate_yt_script.py` |
| Short-section detector | `scripts/detect_short_sections.py` |
| Montage + EditPlan builder | `scripts/prepare_voiceover_edit.py` |
| Captions (drop "so", raised y, toggle) | `scripts/hyperframes_render.py` (`--no-captions`, `--caption-y`) |
| Orchestrator | `scripts/run_voiceover_week.py` |
