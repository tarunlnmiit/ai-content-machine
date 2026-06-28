---
description: Edit or create a Remotion video from a plain-English description
---

You are driving a Remotion project in this folder to edit video from plain-English instructions.

The user's request: $ARGUMENTS

Do the following:

1. If a Remotion project isn't set up yet in this folder, scaffold one (1080×1920 vertical, 30fps).
   Ensure there is a `public/` folder and that the user's source clip (e.g. `public/dummy.mp4`)
   is referenced via `staticFile()`.

2. Create or update a composition that plays the source clip full-screen using `<OffthreadVideo>`
   and adds the overlay / edit the user described. Use `interpolate` + `spring` for any fades or
   motion. Keep text high-contrast and large enough to read on a phone.

3. Render the composition to an MP4 in this folder (e.g. `out/preview.mp4`) and tell the user the
   exact output path so they can open and preview it.

4. If the user asks for a revision, update the same composition and re-render — don't start over.

Constraints:
- Match the duration of the source clip unless told otherwise.
- Don't add audio unless asked.
- After rendering, report what you changed in one short line.
