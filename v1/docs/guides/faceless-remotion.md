# Faceless reel (Remotion) — `v1/remotion/`

Fully-generated, faceless reel rendered with **Remotion** (React → video). No talking
head, no stock footage — every visual is invented (animated background + typographic /
code / motion-graphic beats), driven by a **voiceover** and the reel's storyboard +
word-level transcript.

Built 2026-07-01 to turn the talking-head reel
`2026-06-16_..._ai-prompt-anatomy-travel` into a faceless version using only the recorded
voice.

## What it is

- Project: `v1/remotion/` (Remotion 4.x, React 19, TypeScript). `npm install` already run.
- One composition: **`FacelessReel`** (1080×1920, 30fps, 1382 frames ≈ 46.1s).
- Registered in `src/Root.tsx`; entry `src/index.ts`.

## Structure

```
v1/remotion/
  package.json  remotion.config.ts  tsconfig.json
  public/voice.m4a            # the extracted voiceover (audio track)
  src/
    index.ts  Root.tsx        # registerRoot + <Composition id="FacelessReel">
    theme.ts                  # DS palette, FPS/W/H, DURATION_IN_FRAMES, CAPTION_Y
    AnimatedBg.tsx            # generated bg: drifting spotlights + grid + grain + vignette
    Captions.tsx             # word-synced karaoke captions from data/transcript.json
    FacelessReel.tsx         # assembles bg + <Audio> + per-beat <Sequence> + captions
    data/storyboard.json     # beat list (RE-TIMED to the voice — see below)
    data/transcript.json     # word-level timings (start/end/text)
    scenes/                  # one component per beat block type
      util.ts SceneHook SceneMatrix SceneCode ScenePill SceneLowerThird SceneOutro
```

## Beat → scene mapping (`FacelessReel.tsx: sceneFor`)

`code-particle-assemble`→Hook · `matrix-decode`→Matrix (char-scramble decode) ·
`code-typing`→Code (5-part editor card) · `floating-pill-badge`→Pill ·
`lower-third-minimal`→LowerThird · outro/`macos-notification`/`logo-outro`→Outro
(comment-CTA only, **no logo/subscribe**).

## Beat timing = aligned to the VOICE

The storyboard's original `start_sec`/`end_sec` were approximate and did NOT match the
actual speech, so visuals led the audio by several seconds. `data/storyboard.json` here is
**re-timed**: each beat is anchored to when its `transcript_excerpt` is actually spoken
(matched against `transcript.json` word times). Re-derive with the excerpt-matching snippet
used on 2026-07-01 if the voice/transcript changes.

## Render

```bash
cd v1/remotion
npx remotion still src/index.ts FacelessReel /tmp/still.png --frame=50   # quick check
npx remotion render src/index.ts FacelessReel <out>.mp4                  # full (h264 + voice)
```
Output used: `v1/assets/reels_video/2026-W25/..._faceless_remotion.mp4`.

## Notes / caveats

- Captions are baked in the Remotion composition (word-synced, always on). To burn them via
  HyperFrames instead, render without the `<Captions>` layer and post-process.
- Font falls back to system sans (Inter not installed) — add `@remotion/google-fonts/Inter`
  for exact Inter.
- This is separate from the **stock B-roll montage** voiceover lane
  (`run_voiceover_week.py`, ffmpeg Ken Burns) — see `voiceover-runner.md`. The repo's
  `VoiceoverLong`/`VoiceoverShort` compositions are still not implemented; only `FacelessReel`
  exists here.
