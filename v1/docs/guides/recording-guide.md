---
title: "Recording Guide — Talking-Head Videos (Life, Poetry, DS)"
type: doc
slug: recording-guide
tags: [content/doc]
---
# Recording Guide — Talking-Head Videos (Life, Poetry, DS)

## Physical Setup

```
[MONITOR — eye level, teleprompter full-screen]
      ↑
[iPhone — tripod, between you and monitor, slightly below eye line]
      ↑
[You — 2-3 feet back, head + chest in frame, 20% headroom]
```

- iPhone 15 Pro Max on tripod, mounted between you and monitor
- Eye contact with camera = looking at monitor naturally
- Move 3-4 feet from background for natural depth separation

---

## Pre-Record Checklist (2 min)

- [ ] Generate teleprompter: `python3 scripts/generate_teleprompter.py --script content/scripts/[slug]_yt.md --open`
- [ ] Teleprompter open full-screen on monitor — adjust speed with `↑↓`, test scroll before hitting record
- [ ] Lark M2 receiver → iPhone USB-C
- [ ] iPhone: Do Not Disturb ON
- [ ] iPhone: Auto-Lock → Never (`Settings → Display & Brightness → Auto-Lock`)
- [ ] iPhone camera: 4K 30fps, standard video (not cinematic mode)
- [ ] QuickTime on Mac → New Movie Recording → select iPhone as source → confirm framing
- [ ] Speak a few words — check Lark M2 LED is green

---

## Recording

1. Hit record on iPhone
2. Pause 3 seconds silent before speaking — edit handle
3. Read at ~130 wpm, natural pace
4. Clap once at every `[PAUSE]` marker — creates visible audio spike for editor
5. `[BROLL:]` markers — keep talking, don't stop (editor handles cutaway)
6. Flub a line → clap once, pause 2s, repeat from sentence start (don't restart whole take)
7. Pause 3 seconds silent at end before stopping

---

## Post-Record

- iPhone: Auto-Lock → back to normal
- Transfer via AirDrop or USB → `assets/raw/[slug].mov`
- Record Life first, Poetry second — same session while setup is live

---

## Thumbnail Reaction Shots ⚡ Do this BEFORE breaking down your setup

While the camera, lights, and mic are still live — capture 3–4 expression photos for each video's thumbnail. **This is the face layer** that makes the difference between 0.5% and 5%+ CTR.

**Why now:** you're already framed, lit, and mic'd. Reaction shots take 2 minutes. Breaking down setup and re-creating it for a thumbnail session costs 30 minutes. Don't skip this.

### What to shoot (per video):

| Shot | Expression | Use case |
|------|-----------|----------|
| `_face_01.jpg` | Surprised / jaw drop | "I didn't expect this" moments, bugs, failures |
| `_face_02.jpg` | Confused / raised eyebrow | "This makes no sense" — contrarian hooks |
| `_face_03.jpg` | Pointing at camera | Direct address — "You're doing X wrong" |
| `_face_04.jpg` | Smiling / nodding | Positive results, validation, "it works" |

### How to shoot:

1. Have someone read the video title out loud — react naturally, don't pose
2. If alone: read the title to yourself and hold the expression for 3 seconds, then shoot
3. Shoot in burst mode (hold shutter) — keep best 1 from each burst
4. Check: face in focus, eyes sharp, expression reads at small size

### Save to:

```
assets/raw/{week}/thumbs/
  {ds_slug}_face_01.jpg
  {ds_slug}_face_02.jpg
  {ds_slug}_face_03.jpg
  {ds_slug}_face_04.jpg
  {life_slug}_face_01.jpg   # repeat pattern
  {poetry_slug}_face_01.jpg # repeat pattern
```

Create the folder if it doesn't exist:
```bash
mkdir -p assets/raw/{week}/thumbs/
```

### If you skip this:

`generate_thumbnail.py --niche ds --hook "..."` still runs (Mode A, AI-generated) — but Mode B (photo + AI composite) produces higher CTR thumbnails because the face is real. Missing shots = lower CTR ceiling. Shoot them.

---

## File Output

| Niche | Save to |
|-------|---------|
| Life | `assets/raw/[life_slug].mov` |
| Poetry | `assets/raw/[poetry_slug].mov` |
| DS (talking-head) | `assets/raw/[ds_slug].mov` |
| DS (screen) | `assets/raw/[ds_slug]_screen.mov` |

Next step after recording: `docs/saturday.md` (auto-edit + captions)
