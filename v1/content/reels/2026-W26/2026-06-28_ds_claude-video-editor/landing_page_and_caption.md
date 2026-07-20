---
title: "Landing Page Copy + Reel Caption"
type: reel
niche: data_science_tech
week: 2026-W26
slug: landing-page-and-caption
tags: [content/reel, niche/data_science_tech, week/2026-W26]
---
# Landing Page Copy + Reel Caption

## A. Email-gated landing page (the upgrade = the Template Pack)

> Goal: free guide goes out in the DM; this page captures the email for the **Template Pack**.
> Put the email form here. Deliver the pack zip on submit (and/or email it).

---

**Headline:**
Edit videos by typing — now with ready-made overlays.

**Subhead:**
You already got the setup guide. This is the shortcut: 4 drop-in templates — animated captions,
a name tag, a progress bar, and a follow badge — that you control with one line or a quick ask to
Claude. Drop them in, swap your clip, post.

**What you get (bullets):**
- 🎬 WordPopCaption — words that pop in one at a time
- 🪪 LowerThird — a sliding name/title tag
- 📊 ProgressBar — a bar that fills as the video plays
- 🔔 FollowBadge — a bouncing "Follow for more" sting
- A 2-minute install README + copy-paste prompts

**Form:**
First name (optional) · Email · [ Send me the Template Pack ]

**Microcopy under the button:**
No spam. Just the pack + the occasional DS/AI workflow. Unsubscribe anytime.

**Confirmation / thank-you state:**
Check your inbox — the Template Pack is on its way. Reply to that email with the clip you make;
I feature the best ones.

---

## B. Reel caption (post this with the video)

```
Comment "EDIT" and I'll send you the full setup guide 👇

Claude can now edit videos by driving a real, code-based editor — and the clip above was cut this way.

You describe the edit in plain English; Claude Code does it in Remotion. 3 steps to set up:

1. Open the Claude desktop app and turn on Code.

2. Point Claude at Remotion (the code-based video tool) and let it install — one command.

3. Tell Claude the exact cut/caption/edit you want. It opens its own editor and makes it.

Want a revision? Just ask — it re-renders. No timeline scrubbing.

What it actually does: it drives the editor from your instructions. Setup is one install command — after that it's plain English.

Comment "EDIT" for the full guide. (I'll also point you to a free pack of drop-in templates.)

#datascience #ai #claude #claudecode #videoediting
```

---

## C. The funnel (how the pieces connect)

1. **Reel** → CTA: comment **"EDIT"**.
2. **Auto-DM** → sends the free `GUIDE_for_followers.md` (no gate) + one line: *"Want ready-made
   overlays too? Free template pack here 👉 [landing page link]"*.
3. **Landing page** (this file, section A) → email → delivers the **Template Pack** zip.
4. Tag the landing-page link with UTM via `scripts/lib/utm.py` so `collect_analytics.py` attributes
   signups to this reel.

Keep links out of the IG post body (suppresses reach) — links live in the DM + pinned comment only.
```
