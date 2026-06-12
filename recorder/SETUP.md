# Remotion Recorder — Setup Guide

Remotion Recorder is a standalone Next.js app for recording talking-head videos with
built-in webcam capture, Whisper transcription, and caption export. Used for Life and
Poetry niche videos where a personal, face-to-camera delivery is the format.

## First-Time Setup

Run this once inside `recorder/` to scaffold the app:

```bash
cd recorder
npx create-video@latest .
# Choose: Recorder
```

Then install dependencies:

```bash
npm install
```

## Daily Use

```bash
cd recorder
npm run dev        # Opens at http://localhost:3000
```

Record your talking head → export footage + captions from the Recorder UI.

## Pipeline Integration

After recording, move files to the standard pipeline locations:

| Recorder output | Destination |
|----------------|-------------|
| Exported `.mp4` | `assets/raw/YYYY-MM-DD_<slug>_raw.mp4` |
| Whisper captions (`.json`) | `remotion/public/captions/YYYY-Wnn/<slug>.captions.json` |

The captions file from Recorder uses Whisper's word-level JSON format.
`prepare_remotion_edit.py` expects this shape in `remotion/public/captions/{week}/{slug}.captions.json`.
Verify keys match: `words[].start`, `words[].end`, `words[].word` — rename fields if the
Recorder version differs.

Once files are in place, the existing edit pipeline takes over:
1. `scripts/prepare_remotion_edit.py` — builds edit plan from captions
2. `scripts/render_week.py` — renders the final video with overlays

## Niche Usage

| Niche | Use Recorder? |
|-------|--------------|
| Life | Yes — talking head is primary format |
| Poetry | Yes — reading to camera with intimate delivery |
| DS/Tech | No — use screen recording + voiceover (`assets/raw/`) |
