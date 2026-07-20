---
title: "Reel Brief — \"Claude can now edit your videos\" (DS)"
type: reel
niche: data_science_tech
week: 2026-W26
slug: reel-brief
tags: [content/reel, niche/data_science_tech, week/2026-W26]
---
# Reel Brief — "Claude can now edit your videos" (DS)

**Slug:** `2026-06-28_ds_claude-video-editor`
**Week:** 2026-W26 · **Niche:** DS · **Format:** Reel (IG Reels + YouTube Shorts only)
**Keyword:** `EDIT` · **DM payload:** the full setup guide
**Status:** brief ready → record → run pipeline

> Inspired by the *structure* of a @mavgpt reel (talking-head + caption-IS-product). This is an
> **original** script in Tarun's voice — not a copy. Your unfair advantage: you actually run a
> Remotion video pipeline, so you can show your **real** workflow instead of a generic demo.
> That's the honesty guardrail working in your favor.

---

## Why this works for you (don't skip)

The original is a generic "look what Claude can do" demo. You can beat it because the tool it
talks about — Claude Code driving Remotion — **is literally your production stack**. So your reel
isn't a hot take, it's a build-in-public proof: "here's the thing actually editing the video
you're watching." That's a stronger, more honest hook and it's defensible in the comments.

Tracker check (last 90 days, DS): no "Claude / video editing / Remotion-as-editor" angle has
been published — only placeholder rows. **Clear to publish.**

---

## Structural breakdown of the source (what to copy = format, not words)

| Element | Source | Your version |
|---|---|---|
| Format | Talking head, vertical, captions burned in | Same |
| Hook (on-screen) | "[Tool] just killed [job] 🥊", word "KILLED" drops in | "Claude just replaced my video editor" — keep the kill/replace pattern |
| Body | 3 numbered setup steps, spoken fast | 3 steps, but show **your** terminal/Remotion doing it |
| Proof | (implied) | Screen-record your real pipeline rendering this clip |
| CTA | "Comment 'Edit' → full guide" | "Comment 'EDIT' → full guide" |
| Caption | The steps live in the caption (caption-IS-product) | Same — full steps in caption |

---

## ORIGINAL SCRIPT (5 beats · ~40s spoken · 140–160 wpm)

> Record talking-head. Re-record the hook 5× and keep the best — first 3s decide everything.
> Cut on every sentence, no clip > 4s. Burned-in word-by-word captions.

**Beat 1 — Hook (0–3s)** · *face, hard cut, point at camera*
> "Claude just replaced the video editor I've used for ten years."

On-screen text: **Claude just replaced my video editor** → word **REPLACED** drops/scales in.

**Beat 2 — Problem (3–8s)** · *face*
> "Editing one short used to be an evening of cutting, captioning, and re-rendering. I was the bottleneck."

On-screen: **THE BOTTLENECK**

**Beat 3 — Reveal + proof (8–28s)** · *cut to screen-recording of your terminal + Remotion*
> "Now I describe the edit in plain English and Claude Code drives a real video editor. Three steps to set it up:
> one — open the Claude desktop app and turn on Code.
> two — point it at Remotion, the code-based video tool, and let it install.
> three — tell it the cut you want. It opens its own editor and does it."

On-screen per line: **PLAIN ENGLISH** / **1 CODE** / **2 REMOTION** / **3 DESCRIBE THE CUT**
*Proof B-roll: show the actual render of THIS clip happening on screen.*

**Beat 4 — Payoff (28–35s)** · *back to face, confident*
> "Want a change? You just ask, and it re-renders. The clip you're watching was cut this way."

On-screen: **JUST ASK** → **RE-RENDERS**

**Beat 5 — CTA (35–42s)** · *point down*
> "I wrote up the full setup. Comment 'EDIT' and I'll send it to you."

On-screen: **COMMENT "EDIT"**

> Loop ending: end on the result/screen, not "bye" — invites the rewatch.

**Honesty guardrail:** say it *drives* Remotion / *describes edits in English* — true. Don't say
"fully autonomous" or "no code at all"; setup touches the terminal once. State exactly that.

---

## On-screen caption beats (one word/phrase per beat, not sentences)
`REPLACED` → `BOTTLENECK` → `PLAIN ENGLISH` → `1 · 2 · 3` → `JUST ASK` → `COMMENT "EDIT"`

---

## Thumbnail text (state the OUTCOME, not the topic)
**Primary:** `Claude just replaced my video editor 😳`
**Alt A:** `I edit videos by typing now 🤯`
**Alt B:** `The tool that edited THIS video pt1` (opens a series)

Series option: brand it **"Claude did my job pt1"** so pt2+ get easy returning-viewer reach.

---

## CAPTION (the caption IS the product — full value in the body)

```
Comment "EDIT" and I'll send you the full setup guide 👇

Claude can now edit videos by driving a real, code-based editor — and the clip above was cut this way.

You describe the edit in plain English; Claude Code does it in Remotion. 3 steps to set up:

1. Open the Claude desktop app and turn on Code.

2. Point Claude at Remotion (the code-based video tool) and let it install — one command.

3. Tell Claude the exact cut/caption/edit you want. It opens its own editor and makes it.

Want a revision? Just ask — it re-renders. No timeline scrubbing.

What it actually does: it drives the editor from your instructions. Setup touches the terminal once — after that it's plain English.

#datascience #ai #claude #claudecode #videoediting
```

(DM payload = a formatted copy of the same steps + your repo link, UTM-tagged via `scripts/lib/utm.py`.)

---

## Platform deltas (reels = IG + YT Shorts only, per pipeline)
- **Instagram Reel:** CTA "Comment 'EDIT'". Pin a first comment with the keyword prompt. Arm comment→DM.
- **YouTube Shorts:** put the guide link as the **first line** of the description + pinned comment. `#Shorts` in title.
- **LinkedIn/Twitter:** excluded for reels (per pipeline-2026).

---

## END-TO-END PRODUCTION STEPS

### 0. Pre-flight
- Confirm clear: tracker checked ✅ (done). KB voice + formula read ✅.

### 1. Generate the script + manifest (optional — this brief already has the script)
```
cd v1
python3 scripts/prepare_reel_script.py \
  --from tool 2026-W26 \
  --niche ds \
  --project free_tool_ds \
  --slug 2026-06-28_ds_claude-video-editor
```
This writes `reel_script.md` + `manifest.json` into `content/reels/2026-W26/2026-06-28_ds_claude-video-editor/`.
You can replace the generated `reel_script.md` with the script above (it's already tuned).

### 2. Record
- Talking-head, vertical. Record the **hook 5×**, pick the best.
- Capture **proof B-roll**: screen-record your terminal + Remotion actually rendering. 3–5s clips, zoomed for mobile.
- Save raw to `assets/raw/2026-06-28_ds_claude-video-editor.mov`.

### 3. Run the pipeline (trim → storyboard → HyperFrames → composite → MP4)
```
cd v1
python3 scripts/run_video_pipeline.py \
  --raw assets/raw/2026-06-28_ds_claude-video-editor.mov \
  --manifest content/reels/2026-W26/2026-06-28_ds_claude-video-editor/manifest.json
```
Idempotent — re-run to resume from a failed phase; `--restart-from 4` to redo storyboard onward.
Final MP4 lands at the canonical output path printed at the end.

### 4. Stage + publish
- Derivatives + scheduling handled by the auto-publish path (`load_posts.py` → `scheduler.py`).
- Manual steps that remain: record, ~10-min approval, reply to comments/DMs.
- After publishing: set tracker Status = 'Published' for matching slug rows.

### 5. Per-reel checklist (from viral_reel_formula.md)
- [ ] Hook recorded 5×, winner picked
- [ ] Proof B-roll captured (real render on screen)
- [ ] 5 beats present, ≤45s, captions burned in
- [ ] Honesty guardrail held (no "fully autonomous" overclaim)
- [ ] CTA = one keyword ("EDIT"); comment→DM armed
- [ ] UTM link in DM/description
- [ ] Thumbnail states the outcome
```
