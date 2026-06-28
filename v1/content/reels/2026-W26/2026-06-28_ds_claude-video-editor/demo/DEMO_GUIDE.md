# Demo Guide — the dummy clip Remotion edits (for the reel)

Goal: a ~5-second dummy clip + an animated text overlay that **Claude adds in Remotion**.
You screen-record this editing happening; that footage is the "proof" B-roll in your reel.

Two ready-made files live next to this guide:
- `OverlayDemo.tsx` — the overlay composition (animated title + subtitle over your clip)
- `Root.tsx` — registers the composition

You can either (A) let Claude write the overlay live on camera, or (B) drop these files in as a
safety net so the demo always renders. Recommended: rehearse with B, record with A.

---

## STEP 1 — Record the dummy clip (~5 min)

You just need a short, visually simple clip for the overlay to sit on. Don't overthink it.

**Specs**
- Orientation: **vertical** (matches the reel)
- Resolution: 1080×1920, **30 fps** (any modern phone default is fine)
- Length: **4–6 seconds** (keep it short — the overlay is the star)
- Sound: doesn't matter, the overlay clip is silent B-roll

**What to film (pick one):**
- You waving / giving a thumbs up to camera, then holding still
- Pouring coffee, typing on a laptop, walking toward the camera
- Even just a slow pan across your desk

**Tips:** lock the phone on a stand or against books, good light on your face/subject, leave the
bottom third of the frame fairly empty — that's where the overlay text lands.

**Export & name it:** transfer to your computer and rename the file exactly:
```
clip.mp4
```
(If your phone exports `.mov`, convert or just rename — Remotion reads both; keep the name `clip`.)

---

## STEP 2 — Set up Remotion (the on-camera "3 steps")

> This is the part you show on screen. Have the Claude desktop app open with Code on.

In a terminal, create a fresh blank Remotion project:
```
npm create video@latest -- --blank claude-edit-demo
cd claude-edit-demo
```
Choose the **Blank** template when prompted (TypeScript). Then start the studio:
```
npm run dev
```
Remotion Studio opens in your browser at http://localhost:3000 — this is "Claude's own video
editor" you reference in the script.

---

## STEP 3 — Put your clip in the project

Copy your recorded file into the project's `public/` folder:
```
cp /path/to/clip.mp4 public/clip.mp4
```
(Anything in `public/` is reachable via `staticFile("clip.mp4")`.)

---

## STEP 4 — Add the overlay (this is "the edit")

### Option A — let Claude do it live (best for the reel)
In the Claude desktop app (Code on, pointed at the `claude-edit-demo` folder), type a prompt like:

> "In this Remotion project, add a new composition called OverlayDemo that plays public/clip.mp4
> and animates a big white title 'Edited by Claude' with a cyan subtitle 'in Remotion' sliding up
> from the bottom third. Register it in Root.tsx, 1080×1920, 30fps, 5 seconds."

Claude writes the files; the Studio hot-reloads and the overlay appears. Then show a revision:

> "Make the title bigger and change the subtitle to 'one prompt, no timeline'."

It re-renders instantly — that's your beat-4 payoff ("just ask, it re-renders").

### Option B — safety net (drop-in files)
If you'd rather not depend on a live edit while filming, copy the two provided files in:
```
cp OverlayDemo.tsx  claude-edit-demo/src/OverlayDemo.tsx
cp Root.tsx         claude-edit-demo/src/Root.tsx
```
Then in `src/Root.tsx` set `durationInFrames` to **your clip's seconds × 30** (5s → 150).
The Studio reloads and shows `OverlayDemo`. Edit the `title` / `subtitle` defaults to taste.

> Filming plan: pre-load Option B so it always works, but on camera type the Option A prompt so
> viewers see Claude doing the edit. If the live edit stalls, you already have the rendered result.

---

## STEP 5 — Preview, then render to MP4

Preview in the Studio (scrub the timeline). When happy, render:
```
npx remotion render OverlayDemo out/clip-edited.mp4
```
Output lands at `out/clip-edited.mp4` — the before (`clip.mp4`) vs after (`clip-edited.mp4`)
contrast is great to flash on screen.

---

## STEP 6 — Capture the screen-recording for the reel

While doing Steps 4–5, **screen-record** (macOS: Cmd+Shift+5):
- the terminal command running
- the Studio with the overlay appearing
- the revision updating live

Trim to 3–5s zoomed-for-mobile clips. These are your beat-3 proof B-roll in `reel_brief.md`.

---

## Quick reference

| Thing | Value |
|---|---|
| Clip file | `public/clip.mp4`, vertical 1080×1920, 30fps, 4–6s |
| Composition id | `OverlayDemo` |
| Duration | clip seconds × 30 (5s = 150 frames) |
| Render command | `npx remotion render OverlayDemo out/clip-edited.mp4` |
| Studio | `npm run dev` → http://localhost:3000 |

**Honesty guardrail:** setup touches the terminal once (`npm create video`), then the edits are
plain-English prompts. Say exactly that on camera — don't imply zero setup.
