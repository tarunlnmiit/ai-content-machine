---
title: "Recording + Demo Guide — Claude (desktop app) edits a dummy video with Remotion"
type: reel
niche: data_science_tech
week: 2026-W26
slug: recording-demo-guide
tags: [content/reel, niche/data_science_tech, week/2026-W26]
---
# Recording + Demo Guide — Claude (desktop app) edits a dummy video with Remotion

Goal: a clean screen-recording where you **type a request in the Claude desktop app**, Claude adds
an overlay to a short dummy clip, and you ask for one change and it re-renders. No terminal on
screen — everything stays inside the Claude Code panel of the desktop app.

> Honesty note: this is a *real* edit on a *throwaway* clip. That's fine and honest — you're
> demoing the capability, not faking it. Don't say "no code involved"; say "I describe the edit
> in plain English." (Setup runs a couple of install/render commands inside Claude's panel.)

---

## Prerequisites (one-time, 5 min)

1. **Claude desktop app** installed, signed in, with **Code** enabled.
2. **Node.js** (LTS) installed — Remotion needs it. Quick check: if you've never installed it,
   download the LTS from nodejs.org first. If you skip this, Claude will hit an error and ask you
   to install it — better to have it done before you hit record.
3. A folder to work in. Suggest: `~/Desktop/claude-remotion-demo`. Keep it empty for now.

---

## Part A — Make the dummy clip (2 min)

Shoot something generic and short — it's a throwaway, so anything visually simple works:

- **Length:** 4–6 seconds.
- **Subject:** a coffee cup, a plant, your desk, you waving, a street — anything with a bit of
  motion so the overlay clearly sits *on top of real video*.
- **Orientation:** vertical (portrait) if you can — it matches the reel. 1080×1920 ideal.
- **File:** trim to ~5s, name it `dummy.mp4`. Put it on your Desktop for now.

That's all the "video to be edited" you need.

---

## Part B — The 4 on-screen setup beats (this is what you film for the "how-to")

These four beats mirror the setup sequence viewers expect from this style of reel. They're real,
functional steps — record each one. Everything stays inside the Claude desktop app + a browser
tab; no terminal window.

**Beat 1 — Show Claude Code (desktop app).**
Open the Claude desktop app and turn on **Code**. Click into your empty demo folder
(`~/Desktop/claude-remotion-demo`) so the Code panel is pointed at it. Film this — the app, the
Code mode, the empty project.

**Beat 2 — Google "Remotion."**
Open a browser tab, search **Remotion**, land on **remotion.dev**. Film the search result + the
homepage for a beat (this is the "what is this tool" visual).

**Beat 3 — Copy the install command, paste it into Claude, hit Enter.**
On remotion.dev under **Get Started**, copy the install command shown there (currently
`npx create-video@latest` — copy whatever the site shows so it's never stale). Paste it into the
Claude Code panel and send. Claude runs it **inside its own panel** and scaffolds the project. Film
the paste → Enter → Claude installing.
> When it asks for a template, tell Claude: *"Pick the blank/Hello World template, 1080×1920
> vertical, 5 seconds."*

**Beat 4 — Invoke the `/remotion-video` command and describe the edit.**
Type **`/remotion-video`** in the Claude Code panel (I'm giving you this command below so it
actually exists), then describe the edit. This is the "magic" beat — film it.

**Before you hit record on the real take:** do a dry run of Beats 1–4 once so the install is
cached and `dummy.mp4` is already sitting in the project's `public/` folder (drag it in, or tell
Claude *"move dummy.mp4 from my Desktop into public/"*). On the recorded take the install is then
fast and clean.

> The `/remotion-video` command is a real Claude Code slash command — file:
> `remotion-video-command.md` in this folder. Copy it to
> `~/Desktop/claude-remotion-demo/.claude/commands/remotion-video.md` and `/remotion-video` will
> work in the desktop app.

---

## Part C — The two prompts you'll film (the actual demo)

These are the on-screen moments. Record the app while you type them.

**Prompt 2 — the edit (run via the `/remotion-video` command — your reel's "reveal" beat):**
Type `/remotion-video` then:
> "Play `dummy.mp4` full-screen and add a text overlay that says **'Claude edited this 🎬'** near
> the top. Fade it in over the first second, bold white text with a soft shadow. Then render it to
> an MP4 I can preview."

Claude writes the composition and renders. A preview MP4 appears — open it on screen so the viewer
sees the overlay actually on your clip. **That's your proof shot.**

**Prompt 3 — the revision (your reel's "payoff" beat):**
> "Make the text bigger, move it to the bottom, and change the color to yellow. Re-render."

Claude updates and re-renders. Show the new version. The story the viewer sees: *type → it edits →
type again → it changes.* No timeline, no scrubbing.

> Optional 3rd beat if you want more: *"Add my handle @breathofdatascience in small text in the
> corner."* Keep total screen-record tight — you'll trim heavily.

---

## Part D — Screen-recording settings

- **Mac:** QuickTime (File → New Screen Recording) or `Cmd+Shift+5`. Record just the Claude window
  region, not the whole desktop, so it reads on mobile.
- Hide anything personal: other chats, your sidebar, notifications (turn on Do Not Disturb).
- Record at the **highest resolution** you can — you'll crop to vertical and zoom into the
  prompt + the preview video, so you want pixels to spare.
- Capture three things: (1) you typing prompt 2, (2) the preview with the overlay, (3) the
  re-rendered version after prompt 3.
- Keep each captured moment short — 3–5s usable each. Zoom/crop tight for mobile legibility.

---

## Part E — The talking-head (films separately)

Record your face delivering the script from `reel_brief.md` (5 beats, ~40s). You'll intercut:

| Reel beat | What's on screen |
|---|---|
| Hook (0–3s) | Your face. "Claude just replaced the video editor I've used for ten years." |
| Problem (3–8s) | Your face. The editing-was-a-bottleneck line. |
| Reveal (8–28s) | **Screen-record the 4 setup beats:** Claude Code → Google Remotion → paste install command → `/remotion-video` + the edit → overlay preview appears. |
| Payoff (28–35s) | **Screen-record:** prompt 3 → it re-renders. Then back to your face. |
| CTA (35–42s) | Your face, point down. "Comment 'EDIT'." |

Re-record the **hook 5×**, keep the best. Cut on every sentence, captions burned in.

---

## Part F — Putting it together

You have two ways to assemble:

- **Manual (fastest for one reel):** drop talking-head + the three screen-record snippets into any
  editor (CapCut, Premiere, even the Remotion project itself), burn captions, add low trending
  audio. ~30–45s, end on the result (loop-friendly), no "bye."
- **Your pipeline (if you want it automated):** save the talking-head raw as
  `assets/raw/2026-06-28_ds_claude-video-editor.mov`, the screen snippets as B-roll, then run
  `run_video_pipeline.py` per `reel_brief.md`. The screen-record snippets become the proof B-roll.

---

## Quick checklist

- [ ] Node installed; Claude desktop app + Code ready
- [ ] `dummy.mp4` shot (~5s, vertical) and moved into `public/`
- [ ] Remotion project scaffolded (Prompt 1) BEFORE recording
- [ ] Screen-record: Prompt 2 (overlay) → preview shown
- [ ] Screen-record: Prompt 3 (revision) → re-render shown
- [ ] Talking-head recorded, hook done 5×
- [ ] Assembled ≤45s, captions burned in, end on the result
- [ ] Caption + thumbnail + "EDIT" keyword from `reel_brief.md`
