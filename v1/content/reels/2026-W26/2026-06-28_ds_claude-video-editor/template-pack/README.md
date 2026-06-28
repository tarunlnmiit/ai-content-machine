# Claude + Remotion Template Pack

Four drop-in video overlays you control by editing one line — or by asking Claude. Built to work
with the "edit videos by typing" setup. No design or coding needed.

## What's inside

| Composition | What it does |
|---|---|
| **WordPopCaption** | Pops each word of a caption in, one at a time |
| **LowerThird** | A name/title tag that slides in from the left |
| **ProgressBar** | A bar across the bottom that fills as the clip plays |
| **FollowBadge** | A "Follow for more" badge that bounces in near the end |

## Install (2 minutes)

1. Set up the Remotion project (from the free guide: Claude desktop app → install Remotion).
2. Copy the four `.tsx` files from `src/` into your project's `src/` folder.
3. Replace your project's `src/Root.tsx` with the one in this pack (it registers all four).
4. Put your video in the project's `public/` folder and name it `clip.mp4`
   (or change `src` in `Root.tsx`).

That's it. Open the Remotion preview and you'll see all four templates in the sidebar.

## Use it (two ways)

**Edit one line.** Open `src/Root.tsx` and change the `defaultProps` — the caption text, the name,
the accent color, when things appear. Save and the preview updates live.

**Or just ask Claude.** In the Claude desktop app:
> "Use the WordPopCaption template. Change the text to 'NEW VIDEO' and make it yellow at the top.
> Render it."

> "Use the LowerThird template with my name and title, then render an MP4."

## Render

Ask Claude: *"Render the [composition name] to an MP4 I can post."* It outputs a finished vertical
(1080×1920) clip ready for Reels and Shorts.

## Tips

- Clip longer than 5s? Change `DURATION` in `Root.tsx` (e.g. `8 * FPS`).
- Want two overlays at once (e.g. caption + progress bar)? Ask Claude:
  *"Combine WordPopCaption and ProgressBar into one composition."*
- Fonts: uses Inter/Arial by default — ask Claude to load a Google Font if you want a specific one.

---

Made by Tarun · [@breathofdatascience](https://instagram.com/breathofdatascience) — DS & AI workflows weekly.
