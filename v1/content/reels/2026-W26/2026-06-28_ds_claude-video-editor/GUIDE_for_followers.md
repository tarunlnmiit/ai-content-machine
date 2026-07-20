---
title: "Edit Videos by Typing: The Claude + Remotion Setup"
type: reel
niche: data_science_tech
week: 2026-W26
slug: guide-for-followers
tags: [content/reel, niche/data_science_tech, week/2026-W26]
---
# Edit Videos by Typing: The Claude + Remotion Setup

You don't open a timeline. You don't scrub clips. You tell Claude what you want in plain English,
and it edits the video for you using a real, code-based video tool called Remotion — right inside
the Claude desktop app.

This guide gets you from zero to your first edited clip in about 20 minutes. No editing experience
needed. Copy-paste the prompts as you go.

— Tarun ([@breathofdatascience](https://instagram.com/breathofdatascience))

---

## What you're about to build

A setup where you drop a video file in a folder, type something like *"add a caption that fades
in,"* and Claude renders a finished clip. Want it bigger, lower, a different color? You just ask
again and it re-renders. That's the whole loop.

**Honest version of what's happening:** Claude *drives* Remotion (a video tool that's built in
code). You describe edits in plain English. Setup involves pasting one install command and letting
Claude run a render — all inside Claude's own panel, not a scary terminal. After that, it really is
just typing.

---

## Before you start (one-time, ~5 minutes)

You need three things installed:

1. **The Claude desktop app** — download it, sign in, and make sure **Code** is turned on. (Code is
   what lets Claude work inside a folder on your computer and run tools.)
2. **Node.js** — Remotion runs on it. Go to **nodejs.org**, download the **LTS** version, install
   it with all the defaults. If you skip this, the setup stops halfway and complains, so do it now.
3. **A folder to work in** — make an empty folder on your Desktop called `claude-video`. That's
   where everything will live.

> On Windows or Mac, the steps are identical — Claude handles the OS differences for you.

---

## Step 1 — Point Claude at your folder

Open the Claude desktop app, turn on **Code**, and open your `claude-video` folder. You should see
an empty project. That's correct — Claude will fill it.

## Step 2 — Get Remotion

Open your browser and search for **Remotion**. Open the official site, **remotion.dev**, and find
the **Get Started** section. Copy the install command shown there (right now it's
`npx create-video@latest`, but always copy whatever the site shows — it stays current).

## Step 3 — Let Claude install it

Paste that command into the Claude desktop app and send it. Claude runs it for you and sets up the
project. If it asks which template you want, reply:

> Use the blank / Hello World template. Make it 1080×1920 vertical, 30 fps, 5 seconds long.

Wait for it to finish — you'll see it confirm the project is ready.

## Step 4 — Add your video

Put the video you want to edit into the project's `public` folder (Claude created it). Easiest way:
just tell Claude where your file is —

> My video is on my Desktop, it's called clip.mp4. Move it into the public folder for me.

Don't have a clip handy? Any short phone video works — a few seconds of you talking, your desk,
anything. Vertical (portrait) looks best for Reels and Shorts.

## Step 5 — Install the "edit by typing" command (optional but worth it)

This gives you a shortcut: type `/edit-video` and Claude knows exactly what to do. Create a file at
`claude-video/.claude/commands/edit-video.md` and paste in the text from the
**"/edit-video command"** section at the bottom of this guide. (Or just skip this and use the plain
prompts in Step 6 — both work.)

## Step 6 — Make your first edit

Now the fun part. Type your request (with `/edit-video` first if you set it up):

> Play clip.mp4 full screen and add a text overlay that says "Made with Claude" near the top. Fade
> it in over the first second. Bold white text with a soft shadow. Then render it to an MP4 I can
> preview.

Claude writes the edit and renders it. It'll tell you the file path — open it and watch your
overlay sitting on your real video.

## Step 7 — Change anything, instantly

Don't like it? Just say so in plain words:

> Make the text bigger, move it to the bottom, and change the color to yellow. Re-render.

It updates the same video and renders again. Keep going until it's right.

---

## Copy-paste prompts that work

Use these as-is or mix and match:

- **Caption that animates in:** *"Add a caption at the bottom that says 'WATCH THIS' — make each
  word pop in one at a time, big and bold."*
- **Lower-third name tag:** *"Add a name tag in the bottom-left: 'Tarun' on the first line, 'Data
  Scientist' smaller underneath. Slide it in from the left."*
- **Progress bar:** *"Add a thin progress bar across the bottom that fills up as the video plays."*
- **Zoom for emphasis:** *"Slowly zoom into the center of the video over the 5 seconds."*
- **Subscribe sting:** *"At the 4-second mark, pop up a 'Follow for more' badge in the top-right
  that bounces in."*
- **Trim:** *"Cut the first 1 second and the last half-second, then re-render."*

---

## If something goes wrong

- **"node / npx not found"** → Node.js isn't installed (or needs a restart). Install the LTS from
  nodejs.org, fully close and reopen the Claude app, try Step 3 again.
- **Install seems stuck** → first installs download a lot; give it a couple of minutes. If it truly
  hangs, tell Claude: *"That seems stuck — cancel and try the install again."*
- **The render is black / no video shows** → tell Claude: *"The video isn't showing — make sure
  the clip is loaded from the public folder with staticFile() and played with OffthreadVideo."*
- **Text is too small on my phone** → *"Make the text much larger — assume it's being watched on a
  phone."*
- **I want a different length** → *"Make the whole video [N] seconds and re-render."*

---

## Why this is worth your time

Once it's set up, editing is just describing what you want — and every change is one sentence away.
It's reusable: keep the same folder, swap in a new clip, and you're editing again in seconds. It's
especially good for captions, lower-thirds, and quick social cuts where opening a full editor is
overkill.

---

## The `/edit-video` command (paste into `.claude/commands/edit-video.md`)

```markdown
---
description: Edit or create a Remotion video from a plain-English description
---

You are driving a Remotion project in this folder to edit video from plain-English instructions.

The user's request: $ARGUMENTS

Do the following:

1. If a Remotion project isn't set up yet in this folder, scaffold one (1080x1920 vertical, 30fps).
   Ensure there is a `public/` folder and that the user's source clip is referenced via
   `staticFile()`.

2. Create or update a composition that plays the source clip full-screen using `<OffthreadVideo>`
   and adds the overlay / edit the user described. Use `interpolate` + `spring` for fades or motion.
   Keep text high-contrast and large enough to read on a phone.

3. Render the composition to an MP4 in this folder (e.g. `out/preview.mp4`) and tell the user the
   exact output path so they can open and preview it.

4. If the user asks for a revision, update the same composition and re-render — don't start over.

Constraints:
- Match the duration of the source clip unless told otherwise.
- Don't add audio unless asked.
- After rendering, report what you changed in one short line.
```

---

*Found this useful? Follow [@breathofdatascience](https://instagram.com/breathofdatascience) — I share data
science and AI workflows like this every week.*
