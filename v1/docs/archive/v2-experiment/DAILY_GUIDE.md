---
title: "Daily Content Guide"
type: doc
slug: daily-guide
tags: [content/doc]
---
# Daily Content Guide

> Open this every morning. Follow the steps for today. Close the laptop.

---

## Weekly Overview

| Day | Niche | Blog | Reel | Est. Time |
|-----|-------|------|------|-----------|
| **Monday** | Data Science | ✅ Publish | 🎥 Life Reel (record) | ~40 min |
| **Tuesday** | Life | ✅ Publish | 🎥 DS Reel (record) | ~40 min |
| **Wednesday** | Poetry | ✅ Publish | — | ~20 min |
| **Thursday** | Data Science | ✅ Publish | 🎥 Life Reel (record) | ~40 min |
| **Friday** | Life | ✅ Publish | 🎥 DS Reel (record) | ~40 min |
| **Saturday** | Poetry | ✅ Publish | — | ~20 min |
| **Sunday** | — | — | — | ~15 min |

**Legend:** ✅ scripted · 🎥 manual (record your face/voiceover)

---

## Status: What's Automated vs Manual

| Task | Status |
|------|--------|
| Blog research + generation | ✅ `generate_blog.py` |
| Title selection (5 options) | ✅ built into `generate_blog.py` |
| Worksheet (DS + Life only) | ✅ `generate_worksheet.py` |
| LinkedIn post from blog | 🔜 coming next |
| IG carousel from blog | 🔜 coming next |
| Reel caption + brief | 🔜 coming next |
| Reel recording | 🎥 always manual |
| Posting to Medium | 📋 manual (5 min) |

---

## MONDAY · Data Science Blog + Life Reel

**Channel:** @breathofdatascience

### Step 1 — Generate the blog `(5–8 min)`
```bash
cd ~/content-machine
python v2/scripts/generate_blog.py --niche ds
```
The script will:
1. Fetch research signals (Google + Medium)
2. Show you 5 topic options → you pick one
3. Ask for your personal thoughts on the topic (add them or press Enter to skip)
4. Show you 5 title options across different tension levers → you pick one
5. Write the blog and save it

File saved to: `v2/content/blogs/YYYY-Wnn/`

### Step 1b — Generate the worksheet `(2 min, optional but recommended)`
```bash
python v2/scripts/generate_worksheet.py --blog v2/content/blogs/YYYY-Wnn/<filename>.md
```
Creates a printable HTML worksheet at `v2/output/worksheets/YYYY-Wnn/`.
Deploy to Vercel (`vercel deploy --prod`) → get the URL → use it as the CTA in derivatives.

### Step 2 — Review + edit `(10–15 min)`
Open the file. Check four things:
- **Title:** Specific, curiosity-triggering, not generic
- **Opening line:** Does it hook within 2–3 sentences?
- **One quotable line:** Bold it — this becomes your social post
- **Ending:** Ends with a question or follow prompt

### Step 3 — Publish to Medium `(5 min)`
- medium.com → New story → paste content → add tags → Publish

### Step 4 — Share on LinkedIn `(5 min, manual until derivatives are ready)`
- Take the bolded quotable line from the blog
- Write 2–3 sentences of context around it
- Add the Medium link in the first comment (not the post body)

### Step 5 — Record Life Reel `(15–20 min)`
Format: vertical, 30–60 sec, no face required (voiceover ok)

Open `data/kb/raw_take_questions.json` → find this week's Life question

Script structure:
```
"Someone asked me: [question]"
→ your honest take in 3–4 sentences
→ landing line (the thing that sticks)
```

Upload to: **IG Reels @mistakenlyhuman** + **YouTube Shorts @breathoflife_**

---

## TUESDAY · Life Blog + DS Reel

**Channel:** @breathoflife_

### Step 1 — Generate the blog `(5–8 min)`
```bash
python v2/scripts/generate_blog.py --niche life
```
Same interactive flow as Monday: 5 topics → pick → your thoughts → 5 titles → pick → generate.

### Step 1b — Generate the worksheet `(2 min, optional but recommended)`
```bash
python v2/scripts/generate_worksheet.py --blog v2/content/blogs/YYYY-Wnn/<filename>.md
```

### Step 2 — Review + edit `(10–15 min)`
Same four checks as Monday. Life niche extra check:
- Does it feel personal, not generic? If it could've been written by anyone, rewrite the opening with a specific moment from your own life.

### Step 3 — Publish to Medium `(5 min)`
- medium.com → New story → paste content → add tags → Publish

### Step 4 — Share on IG + Threads `(5 min, manual)`
- Pull the quotable line
- Post it as a standalone caption on IG @mistakenlyhuman
- Mirror to Threads

### Step 5 — Record DS Reel `(15–20 min)`
Format: vertical, 60–90 sec, teach one specific thing

Pick from `data/ideas/weekly_ideas.md` → DS reel for this week

Upload to: **IG Reels @mistakenlyhuman** + **YouTube Shorts @breathofdatascience**

---

## WEDNESDAY · Poetry Blog

**Channel:** @breathofpoetry

### Step 1 — Generate the blog `(3–5 min)`
```bash
python v2/scripts/generate_blog.py --niche poetry
```

Poetry blog = a poem + 150–300 words of personal context (what triggered it, what it cost to write).
Edit the output so it reads like your voice, not generated text.

### Step 2 — Review + edit `(10 min)`
- Does the poem feel finished, not drafted?
- Is the context personal, not explanatory?

### Step 3 — Publish to Medium `(3 min)`
- medium.com → New story → paste content → Publish

### Step 4 — Share one stanza on IG `(5 min)`
Pick the strongest 2–4 lines. Post as image (dark background, light text) on @mistakenlyhuman.

---

## THURSDAY · Data Science Blog + Life Reel

Same as Monday — different topic, same process.

```bash
python v2/scripts/generate_blog.py --niche ds
python v2/scripts/generate_worksheet.py --blog v2/content/blogs/YYYY-Wnn/<filename>.md
```

If you want a specific angle instead of letting the script pick:
```bash
python v2/scripts/generate_blog.py --niche ds --topic "your angle here"
```

---

## FRIDAY · Life Blog + DS Reel

Same as Tuesday — different topic, same process.

```bash
python v2/scripts/generate_blog.py --niche life
python v2/scripts/generate_worksheet.py --blog v2/content/blogs/YYYY-Wnn/<filename>.md
```

---

## SATURDAY · Poetry Blog

Same as Wednesday.

```bash
python v2/scripts/generate_blog.py --niche poetry
```

---

## SUNDAY · Plan the Week `(15 min)`

No content creation. Just prep.

1. **Check the tracker** — open `output/trackers/annual-tracker-2026.xlsx`
   - What went out this week? Mark it Published.
   - Any gaps?

2. **Note your angles** — if you have strong topic ideas for any niche next week, add them to `data/ideas/weekly_ideas.md`
   - If not, leave it blank — the script will research and pick on its own.

3. **Check reel questions** — open `data/kb/raw_take_questions.json`
   - Do you know which Life question you'll answer Mon + Thu?

That's it. Batch-recording reels on Sunday is optional but saves time during the week.

---

## If You're Short on Time

**15 min day:** Run the script, do a quick scan, publish to Medium. Skip social until later.

**30 min day:** Full blog day (Steps 1–3). Skip the reel — do it later in the week.

**No time at all:** Skip the day. Two blogs/week per niche is the target, not the minimum.

---

## Quick Reference: Script Commands

```bash
# Blog generation (interactive: topics → personal input → titles → write)
python v2/scripts/generate_blog.py --niche ds
python v2/scripts/generate_blog.py --niche life
python v2/scripts/generate_blog.py --niche poetry

# With a forced topic (skips topic selection; still shows title options)
python v2/scripts/generate_blog.py --niche ds --topic "your angle"

# Dry run (see the prompt without calling Claude)
python v2/scripts/generate_blog.py --niche ds --dry-run

# Worksheet (DS + Life only)
python v2/scripts/generate_worksheet.py --blog <path/to/blog.md>
python v2/scripts/generate_worksheet.py --blog <path> --blog-url https://medium.com/@tarun-gupta/your-post
```

---

## Quick Reference: Where Each Niche Goes

| Niche | Medium | IG | LinkedIn | YouTube |
|-------|--------|----|----------|---------|
| DS | ✅ | Reel only | ✅ post | Shorts + Long |
| Life | ✅ | Post + Reel | — | Shorts + Long |
| Poetry | ✅ | Stanza image | — | @breathofpoetry |

---

*Last updated: 2026-06-23 · Next to build: `generate_derivatives.py` (LinkedIn post + IG carousel + reel caption from blog)*
