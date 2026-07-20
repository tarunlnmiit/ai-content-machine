---
title: "Reel Playbook — \"Claude can now edit your videos\" (DS)"
type: reel
niche: data_science_tech
week: 2026-W26
slug: playbook
tags: [content/reel, niche/data_science_tech, week/2026-W26]
---
# Reel Playbook — "Claude can now edit your videos" (DS)

Everything to make this reel, end to end: the angle, the original script, the exact desktop-app
recording steps, the `/remotion-video` slash command, the caption/thumbnail, and how to publish.
Follow top to bottom.

**Slug:** `2026-06-28_ds_claude-video-editor` · **Week:** 2026-W26 · **Niche:** DS
**Format:** Reel (Instagram Reels + YouTube Shorts only) · **Keyword:** `EDIT`
**Status:** brief ready → record → assemble → publish

> Inspired by the *structure* of a @mavgpt reel (talking-head + caption-IS-product). This is an
> **original** script in your voice — not a copy. The setup steps it shows (Claude Code, Remotion,
> install, the editor command) are functional, so it's fine to mirror that sequence.

---

## 0. Why this works + the guardrail

The viral version is a generic "look what Claude can do" demo. Yours is a clean, honest how-to:
Claude Code drives Remotion (a real, code-based video tool) to edit a clip from a plain-English
request — no timeline scrubbing. You'll demo it on a **throwaway clip** so setup stays simple.

**Honesty guardrail (do not break):** say Claude *drives* the editor and you *describe edits in
plain English* — true. Setup pastes one install command and runs a render **inside Claude's own
panel** (not a terminal). Don't say "no code at all" or "fully autonomous." State exactly that.

**Tracker check (last 90 days, DS):** no Claude / video-editing / Remotion-as-editor angle has
been published — only placeholder rows. **Clear to publish.**

---

## 1. The original script (5 beats · ~40s spoken · 140–160 wpm)

Record talking-head, vertical. Re-record the **hook 5×**, keep the best — the first 3s decide
everything. Cut on every sentence (no clip > 4s). Captions burned in, word-by-word.

**Beat 1 — Hook (0–3s)** · *face, hard cut, point at camera*
> "Claude just replaced the video editor I've used for ten years."

On-screen: **Claude just replaced my video editor** → word **REPLACED** scales in.

**Beat 2 — Problem (3–8s)** · *face*
> "Editing one short used to be an evening of cutting, captioning, and re-rendering. I was the bottleneck."

On-screen: **THE BOTTLENECK**

**Beat 3 — Reveal + proof (8–28s)** · *cut to screen-recording (the 4 setup beats in §3)*
> "Now I describe the edit in plain English and Claude Code drives a real video editor. Three steps to set it up:
> one — open the Claude desktop app and turn on Code.
> two — point it at Remotion, the code-based video tool, and let it install.
> three — tell it the cut you want. It opens its own editor and does it."

On-screen per line: **PLAIN ENGLISH** / **1 CODE** / **2 REMOTION** / **3 DESCRIBE THE CUT**

**Beat 4 — Payoff (28–35s)** · *back to face, confident*
> "Want a change? You just ask, and it re-renders. The clip you're watching was cut this way."

On-screen: **JUST ASK** → **RE-RENDERS**

**Beat 5 — CTA (35–42s)** · *point down*
> "I wrote up the full setup. Comment 'EDIT' and I'll send it to you."

On-screen: **COMMENT "EDIT"**

> Loop ending: end on the result/screen, not "bye" — invites the rewatch.

**Burned-in caption beats** (one word/phrase per beat, not sentences):
`REPLACED` → `BOTTLENECK` → `PLAIN ENGLISH` → `1 · 2 · 3` → `JUST ASK` → `COMMENT "EDIT"`

---

## 2. Prerequisites (one-time, ~5 min)

1. **Claude desktop app** installed, signed in, with **Code** enabled.
2. **Node.js (LTS)** installed — Remotion needs it. If you've never installed it, get the LTS from
   nodejs.org first. Skip this and Claude will stall mid-demo asking for it.
3. A working folder: `~/Desktop/claude-remotion-demo` (keep it empty for now).
4. The `/remotion-video` command installed — see §5. Copy `remotion-video-command.md` (in this
   folder) to `~/Desktop/claude-remotion-demo/.claude/commands/remotion-video.md`.

---

## 3. The dummy clip + the 4 on-screen setup beats

### The dummy clip
Either:
- **Use the ready-made one:** `v1/assets/broll/dummy.mp4` (5s, 1080×1920) — already made for you. Or
- **Pull real stock b-roll on your own machine** (sandbox can't reach Pexels/Pixabay):
  ```
  cd v1
  printf '%s\n' '[BROLL: coffee cup on a desk, morning light]' > /tmp/dummy_cue.md
  python3 scripts/fetch_videos.py --script /tmp/dummy_cue.md --niche ds \
    --orientation portrait --target-clips 1 --out-suffix dummy-demo
  ```
- Or shoot your own 4–6s vertical clip (coffee cup, plant, you waving — anything with motion).

Name it `dummy.mp4` and put it in the project's `public/` folder.

### The 4 setup beats (record each — no terminal window, all inside the app + a browser tab)

**Beat 1 — Show Claude Code (desktop app).** Open the Claude desktop app, turn on **Code**, point
the Code panel at `~/Desktop/claude-remotion-demo`. Film the app + empty project.

**Beat 2 — Google "Remotion."** New browser tab → search **Remotion** → land on **remotion.dev**.
Film the search result + homepage.

**Beat 3 — Copy install command → paste into Claude → Enter.** On remotion.dev under **Get
Started**, copy the install command shown (currently `npx create-video@latest` — copy whatever the
site shows so it's never stale). Paste into the Claude Code panel and send. Claude runs it inside
its own panel and scaffolds the project. If it asks for a template, tell Claude: *"Blank/Hello
World template, 1080×1920 vertical, 5 seconds."*

**Beat 4 — Invoke `/remotion-video` and describe the edit.** Type `/remotion-video` then the edit
request (see §4). This is the "magic" beat.

> **Dry-run first.** Before the real take, run Beats 1–4 once so the install is cached and
> `dummy.mp4` already sits in `public/`. Then the recorded take is fast and clean.

---

## 4. The two prompts you film (the demo itself)

**Prompt A — the edit (run via `/remotion-video`; this is the Reveal beat):**
Type `/remotion-video` then:
> "Play `dummy.mp4` full-screen and add a text overlay that says **'Claude edited this 🎬'** near
> the top. Fade it in over the first second, bold white text with a soft shadow. Then render it to
> an MP4 I can preview."

Claude writes the composition and renders → open the preview MP4 on screen so viewers see the
overlay on your clip. **That's your proof shot.**

**Prompt B — the revision (the Payoff beat):**
> "Make the text bigger, move it to the bottom, and change the color to yellow. Re-render."

Claude updates and re-renders → show the new version. Story the viewer sees: *type → it edits →
type again → it changes.*

> Optional extra beat: *"Add my handle @breathofdatascience in small text in the corner."* Keep total
> screen-record tight — 3–5s usable per moment; you'll trim heavily.

---

## 5. The `/remotion-video` slash command

This makes Beat 4 real instead of faked. Save the file below to
`~/Desktop/claude-remotion-demo/.claude/commands/remotion-video.md` (also provided separately as
`remotion-video-command.md`):

```markdown
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
```

---

## 6. Screen-recording settings

- **Mac:** QuickTime (File → New Screen Recording) or `Cmd+Shift+5`. Record just the Claude window
  region, not the whole desktop, so it reads on mobile.
- Turn on **Do Not Disturb**; hide other chats, the sidebar, notifications.
- Record at the **highest resolution** you can — you'll crop to vertical and zoom into the prompt
  and the preview, so you want spare pixels.
- Capture: (1) the 4 setup beats, (2) typing Prompt A → overlay preview, (3) Prompt B → re-render.
- Keep each captured moment 3–5s usable. Zoom/crop tight for legibility.

---

## 7. Assemble

| Reel beat | What's on screen |
|---|---|
| Hook (0–3s) | Your face. "Claude just replaced the video editor I've used for ten years." |
| Problem (3–8s) | Your face. The bottleneck line. |
| Reveal (8–28s) | Screen-record the 4 setup beats → `/remotion-video` + Prompt A → overlay preview. |
| Payoff (28–35s) | Screen-record Prompt B → re-render. Then back to your face. |
| CTA (35–42s) | Your face, point down. "Comment 'EDIT'." |

Two ways to cut it together:
- **Manual (fastest for one reel):** drop talking-head + the screen-record snippets into CapCut /
  Premiere, burn captions, add low trending audio. ≤45s, end on the result (loop-friendly).
- **Your pipeline (automated):** save the talking-head raw as
  `assets/raw/2026-06-28_ds_claude-video-editor.mov`, the snippets as B-roll, then:
  ```
  cd v1
  python3 scripts/prepare_reel_script.py --from tool 2026-W26 --niche ds \
    --project free_tool_ds --slug 2026-06-28_ds_claude-video-editor
  # replace the generated reel_script.md with §1 above, then:
  python3 scripts/run_video_pipeline.py \
    --raw assets/raw/2026-06-28_ds_claude-video-editor.mov \
    --manifest content/reels/2026-W26/2026-06-28_ds_claude-video-editor/manifest.json
  ```
  Idempotent — re-run to resume from a failed phase; `--restart-from 4` redoes storyboard onward.

---

## 8. Caption (the caption IS the product — full value in the body)

```
Comment "EDIT" and I'll send you the full setup guide 👇

Claude can now edit videos by driving a real, code-based editor — and the clip above was cut this way.

You describe the edit in plain English; Claude Code does it in Remotion. 3 steps to set up:

1. Open the Claude desktop app and turn on Code.

2. Point Claude at Remotion (the code-based video tool) and let it install — one command.

3. Tell Claude the exact cut/caption/edit you want. It opens its own editor and makes it.

Want a revision? Just ask — it re-renders. No timeline scrubbing.

What it actually does: it drives the editor from your instructions. Setup touches one install command — after that it's plain English.

#datascience #ai #claude #claudecode #videoediting
```

DM payload = a formatted copy of the same steps + your repo link, UTM-tagged via `scripts/lib/utm.py`.

---

## 9. Thumbnail text (state the OUTCOME, not the topic)

- **Primary:** `Claude just replaced my video editor 😳`
- **Alt A:** `I edit videos by typing now 🤯`
- **Alt B / series:** `The tool that edited THIS video pt1` (brand a "Claude did my job" series — pt2+ get easy returning-viewer reach)

---

## 10. Publish + platform deltas (reels = IG + YT Shorts only)

- **Instagram Reel:** CTA "Comment 'EDIT'". Pin a first comment with the keyword prompt. Arm comment→DM.
- **YouTube Shorts:** guide link as the **first line** of the description + pinned comment. `#Shorts` in title.
- **LinkedIn / Twitter:** excluded for reels (per pipeline-2026).
- After publishing: set tracker **Status = 'Published'** for matching slug rows.

---

## 11. Final checklist

- [ ] Node installed; Claude desktop app + Code ready; `/remotion-video` command in place
- [ ] `dummy.mp4` (~5s, vertical) in `public/`
- [ ] Dry-run done (install cached) BEFORE recording
- [ ] Screen-record: 4 setup beats → `/remotion-video` + Prompt A → overlay preview
- [ ] Screen-record: Prompt B → re-render
- [ ] Talking-head recorded, hook done 5×
- [ ] Assembled ≤45s, captions burned in, end on the result
- [ ] Honesty guardrail held (no "fully autonomous" / "no code")
- [ ] CTA = one keyword ("EDIT"); comment→DM armed; UTM link in DM/description
- [ ] Caption + thumbnail set; tracker updated after publish
```
