---
title: "Thumbnail Replacement Backlog"
type: doc
slug: thumbnail-replacement-backlog
tags: [content/doc]
---
# Thumbnail Replacement Backlog

Generated: 2026-06-18 (YouTube audit)
Priority: highest-impression videos with text-only / branded thumbnails first.

## How to replace a thumbnail

1. Generate a new thumbnail via Canva MCP:
   ```bash
   python3 scripts/generate_thumbnail.py \
     --niche {ds|life|poetry} \
     --hook "3-5 word hook" \
     --week {current-week} \
     --slug {video-slug} \
     --canva
   ```
2. Open the returned Canva edit URL, add your face reaction photo
3. Export as PNG 1280×720
4. Go to YouTube Studio → Content → click video → Details → Thumbnail → upload new
5. Update status in this file

---

## @breathofdatascience — Priority queue

| Priority | Video | ID | Impressions (28d) | CTR | Current thumbnail | Hook to use | Status |
|----------|-------|-----|-------------------|----|-------------------|------------|--------|
| 🔴 1 | Python for Data Science Beginners 2026 — Stop Setting Up Wrong | XBw0vuzACuA | 5,700 | 0.3% | Text diagram "4-Pillar Framework" | "Setup That Breaks Everything" | **Canva design ready — [open to edit](https://www.canva.com/d/FSgkDOR7TLRF3UH)** |
| 🔴 2 | Any video with "Pandas" in title (copyright flagged) | — | — | — | Check Studio | Relevant pandas hook | Check copyright status first |
| 🟡 3 | DS Tutorial 2–10 (if any are live) | — | — | — | Likely text-only | Hook from video content | Do after Tutorial 1 thumbnail proves CTR lift |

### DS thumbnail rules
- Background: dark navy #1E1B2E
- Face: surprised/confused (technical failure expression)
- Accent: slate blue #6B8FA8 or orange #f97316 for error/warning energy
- Font: Space Grotesk bold

---

## @breathoflife_ — Priority queue

| Priority | Video | Hook | Status |
|----------|-------|------|--------|
| 🔴 1 | Any "Breath of Poetry & Life" green-bg branded thumbnail (audit 3+ in Studio) | Personal incident from video title | Generate command below |
| 🔴 2 | "How to Turn Your Habits Into a System That Actually Works" | "I Relied on Discipline for 3 Years" | Command ready ↓ |
| 🔴 3 | "Why Humans Need Closure to Move On?" (remove series number from title too) | "Closure Doesn't Come When You Expect It" | Command ready ↓ |
| 🔴 4 | "Mental Health Openness and Breaking Stigmas" | "I Stopped Saying I'm Fine" | Command ready ↓ |
| 🔴 5 | "The Cost of Carrying Things Nobody Sees" | "The Weight Nobody Can See" | Command ready ↓ |
| 🟡 6 | Any video >500 lifetime impressions, no face | Check Studio → Analytics → Reach | Monthly audit |

### Life thumbnail rules
- Background: dark navy #1E1B2E
- Face: warm, natural reaction (not posed)
- Accent: coral #E8705A
- Font: Lora + Nunito Sans
- Hook: specific personal incident — NOT self-help category label

### Ready commands — run each, open Canva link, add face, export, upload to Studio

```bash
# 🔴 2 — Habits video
python3 scripts/generate_thumbnail.py \
  --niche life --hook "I Relied on Discipline for 3 Years" \
  --slug the-simple-habit-that-changed-my-productivity \
  --week 2026-W24 --canva

# 🔴 3 — Closure video (also rename in Studio: remove series number)
python3 scripts/generate_thumbnail.py \
  --niche life --hook "Closure Doesn't Come When You Expect It" \
  --slug why-humans-need-closure-to-move-on \
  --week 2026-W25 --canva

# 🔴 4 — Mental health video
python3 scripts/generate_thumbnail.py \
  --niche life --hook "I Stopped Saying I'm Fine" \
  --slug mental-health-openness-and-breaking-stigmas \
  --week 2026-W22 --canva

# 🔴 5 — Cost of carrying things video
python3 scripts/generate_thumbnail.py \
  --niche life --hook "The Weight Nobody Can See" \
  --slug the-cost-of-carrying-things-nobody-sees \
  --week 2026-W23 --canva
```

---

## @breathofpoetry — Priority queue

| Priority | Video | Hook | Status |
|----------|-------|------|--------|
| 🔴 1 | "Safe and Alive: A Poetry Essay on Real Love" | "Love Doesn't Announce Itself" | Command ready ↓ |
| 🔴 2 | "Intoxicated Senses" / "The Hangover That Won't Lift" | "Love Has Taken Away My Senses" | Command ready ↓ |
| 🔴 3 | "Waking Up to What We've Built" / reflective lens | "The Night I Stopped Performing" | Command ready ↓ |
| 🔴 4 | "Poetry Dips Its Fingers in Every Colour" | "Every Colour Has a Feeling" | Command ready ↓ |
| 🔴 5 | "You Have to Dance Like There's Nobody Watching" | "Dance When the Playlist Ends" | Command ready ↓ |
| 🔴 6 | All remaining "Breath of Poetry" branded thumbnails (no face) | First emotionally resonant line from each poem | Audit Studio — generate per video |
| 🔴 7 | Any video with `\|\|` in title | Remove separators, clean title in Studio | Rename before new thumbnail |

### Poetry thumbnail rules
- Background: dark navy #1E1B2E
- Face: contemplative, lyrical expression OR atmospheric AI portrait (editorial style if no face photo yet)
- Accent: golden #B89850
- Font: Playfair Display
- Hook: the most emotionally resonant line FROM the poem — not the poem title

### Ready commands

```bash
# 🔴 1 — Safe and Alive
python3 scripts/generate_thumbnail.py \
  --niche poetry --hook "Love Doesn't Announce Itself" \
  --slug safe-and-alive-a-poetry-essay-on-real-love \
  --week 2026-W25 --canva

# 🔴 2 — Intoxicated Senses
python3 scripts/generate_thumbnail.py \
  --niche poetry --hook "Love Has Taken Away My Senses" \
  --slug intoxicated-senses \
  --week 2026-W22 --canva

# 🔴 3 — Waking Up / Reflective Lens
python3 scripts/generate_thumbnail.py \
  --niche poetry --hook "The Night I Stopped Performing" \
  --slug looking-at-the-world-through-a-reflective-lens \
  --week 2026-W23 --canva

# 🔴 4 — Poetry Dips Its Fingers
python3 scripts/generate_thumbnail.py \
  --niche poetry --hook "Every Colour Has a Feeling" \
  --slug poetry-dips-its-fingers-in-every-colour \
  --week 2026-W24 --canva

# 🔴 5 — Dance Like Nobody's Watching
python3 scripts/generate_thumbnail.py \
  --niche poetry --hook "Dance When the Playlist Ends" \
  --slug you-have-gotta-dance-like-there-is-nobody-watching \
  --week 2026-W25 --canva
```

---

## Done

| Date | Video | Channel | Old CTR | New thumbnail | Result |
|------|-------|---------|---------|---------------|--------|
| — | — | — | — | — | — |

*(update this table after each replacement — track whether CTR improves within 7 days)*

---

## Monthly thumbnail audit (add to Sunday routine)

```bash
# Pull CTR data for all videos
python3 scripts/fetch_youtube_analytics.py --metric ctr --days 28 --all-channels

# Flag videos with CTR < 3% and impressions > 500 (replacement candidates)
python3 scripts/fetch_youtube_analytics.py --metric ctr --days 28 --all-channels \
  | grep -E "^[^|]+" | awk -F'|' '$3 < 3 && $2 > 500'
```

Any video with >500 impressions and <3% CTR in the last 28 days is a replacement candidate.
