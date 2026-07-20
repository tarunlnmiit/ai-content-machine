---
title: "Instagram Reel Brief — The Hangover That Won't Lift (Intoxicated Senses)"
type: derivative
niche: poetry_quotes
week: 2026-W22
slug: ig-reel-brief
tags: [content/derivative, niche/poetry_quotes, week/2026-W22]
---
# Instagram Reel Brief — The Hangover That Won't Lift (Intoxicated Senses)

**Week:** 2026-W22
**Account:** @mistakenlyhuman
**Format:** spoken-word (read the poem over the hyperframe video, or text-reveal reel)

---

## Hooks (pick one — use as on-screen text or opening spoken line)

**Option 1:** There's a specific kind of madness that doesn't announce itself. One day you're fine. The next, someone's laugh is living rent-free in your head.
> _From the blog hook — already perfect. Specific, relatable, impossible to scroll past._

**Option 2:** I was deep in a machine learning workflow once — multiple terminals open, coffee going cold — and a sentence she'd said days earlier replayed with cinematic clarity. Not the important parts. Just the way she laughed halfway through it.
> _The data scientist + emotional moment crossover. Uniquely yours. Nobody else can write this._

**Option 3:** Love has taken away all my senses — like that of alcohol. Effects of booze reside for a short period. But your intoxication doesn't want to go away.
> _The poem's opening lines. Works as text reveal over the video._

---

## Format: Text-reveal reel (no clip needed)

Use the existing hyperframe video (`assets/hyperframes/archive/poetry_when_dreams_60s_captioned.mp4` or the W22 poetry video) as B-roll background.

**Reel structure (60 seconds):**
1. **0–5s:** Hook line as text over dark/moody B-roll — "There's a specific kind of madness that doesn't announce itself."
2. **5–35s:** Spoken word reading of the poem (your voice, calm, no rushing) OR text-reveal of stanzas
3. **35–50s:** The reflection line: "When love starts feeling like physics instead of a decision, you're somewhere new."
4. **50–60s:** End card — @breathofpoetry | Save this 🤍

---

## Instagram caption

```
There's a specific kind of madness that doesn't announce itself.

One day you're fine.

The next — someone's laugh is living rent-free in your head. Your morning coffee tastes different. And the part of your brain that's supposed to run the show has quietly handed over the keys.

The trouble isn't the feeling.

It's realising you've been running on a hangover you didn't consent to.

And it refuses to lift.

— Intoxicated Senses

Save this if it found you at the right time. 🤍

#poetry #poetrylovers #lovepoetry #poem #breathofpoetry
```

---

## DM keyword

`POEM` — links to the full Substack post (breathofpoetry.substack.com).

---

## Production command

```bash
# Use existing poetry video — no clip_shorts.py needed
# Source: assets/video/edited/2026-W22/2026-05-29_2026-05-27-poetry-quotes-intoxicated-senses_yt.mp4

# Option A: Use as-is if already vertical (hyperframe format)
# Option B: Extract best 60s moment:
python3 scripts/create_vertical_reels.py \
  --slug 2026-05-29_2026-05-27-poetry-quotes-intoxicated-senses_yt \
  --start 0:00 \
  --duration 60

# Add text overlays manually in CapCut:
# - Hook text at 0s
# - Poem stanzas as text reveal
# - End card at 50s
```

---

## Posting note

Poetry performs best when it feels discovered, not promoted. No "here's my new poem" framing — just open with the hook line and let the poem do the work. The reflection line ("When love starts feeling like physics instead of a decision") is the most shareable moment — consider using it as the caption opener if the hook feels too long.

---

_Edit hooks/caption to match your voice before posting._
