---
title: "IG Reel Script — DS/Tech · \"I Deleted Three Weeks of Content\""
type: reel
niche: data_science_tech
date: 2026-06-08
week: 2026-W24
slug: i-deleted-three-weeks-of-content
platform: ig
tags: [content/reel, niche/data_science_tech, week/2026-W24]
---
# IG Reel Script — DS/Tech · "I Deleted Three Weeks of Content"

> **Source:** blog `content/blogs/2026-W24/2026-06-08_data_science_tech_i-deleted-three-weeks-of-content.md` · published Medium (ILLUMINATION): https://medium.com/illumination/i-deleted-three-weeks-of-content-88965e127aec
> **Formula:** `data/kb/viral_reel_formula.md` (5-beat) + `data/kb/reels/08_carousel_reel_formula.md` hook rules. Caption per `data/kb/reels/06_mavgpt_caption_formula.md` (caption IS the product). **LOCAL ONLY — do not commit.**
> **Length target:** ~40s. Format: 9:16 talking-head + optional terminal screen-record B-roll for beat 3.
> **CTA:** keyword **REFLOG** → DM the 3-command recovery sequence verbatim (from `cheat_sheet.md` in this folder). Same content pinned in first comment.

---

## Hook — 5 variants (08 §hook-polish: write 5, pick best)

1. ✅ **PICK** — "I deleted three weeks of work with one git command. Twenty minutes later, all of it was back." *(Social proof inversion — disaster, then resolved, in one breath)*
2. "One git command wiped 188 megabytes of my content history. Here's how I got every byte back." *(Number-first, concrete stakes)*
3. "Ten years as a data scientist. I still nuked my own repo. Here's what saved me." *(Authority undercut, humility hook)*
4. "git status showed nothing wrong. My entire assets folder was already gone." *(Dread-first, technical specificity)*
5. "Everyone knows git log. Almost nobody runs the command that actually saves you." *(Curiosity gap, sets up reveal)*

**Driver:** Social proof inversion + concrete stakes. Honesty note: no claim that git recovery always works — this is what worked for this specific failure mode (rewritten history, not a hard reset of tracked files). Hard cut, face to camera, no warm-up.

---

## 5-Beat Script

### BEAT 1 — HOOK (0–3s)
- **VO:** "I deleted three weeks of work with one git command. Twenty minutes later, all of it was back."
- **On-screen (burn-in):** `188MB DELETED → 186MB RECOVERED`
- **Cue:** Face to camera, hard cut in. Re-record 5×, keep the sharpest.

### BEAT 2 — PROBLEM (3–9s)
- **VO:** "I ran filter-branch to strip binaries out of history. Misread the path — wiped my entire assets folder from every commit. git status showed nothing wrong."
- **On-screen:** `git status: clean ✅` *(strikethrough on the fake checkmark)*
- **Cue:** Face to camera; optional quick cut to a blank/empty folder shot.

### BEAT 3 — REVEAL + PROOF (9–27s) — *screen-record, real terminal*
- **VO:** "Everyone knows git log. Almost nobody runs git reflog — it shows every place HEAD has ever been, filter-branch included. One checkout got back 186 of the 188 megabytes. The last two files came out of git fsck --dangling."
- **On-screen / B-roll sequence (3–5s clips, zoomed for mobile):**
  1. `git reflog` → scrolling HEAD@{N} history
  2. `git checkout <hash> -- assets/` → files reappear
  3. `git fsck --dangling` → orphaned commit found
- **Cue:** `CodeAnnotation` over each command; burn-in single words: `REFLOG` · `DANGLING COMMITS` · `NOT GONE`.

### BEAT 4 — PAYOFF (27–33s)
- **VO:** "Ten years as a data scientist, and I still nuked my own repo. The difference wasn't knowing more git — it was knowing git almost never actually deletes anything."
- **On-screen:** `Git rarely deletes. It just forgets where to look.`
- **Cue:** Back to face, confident, slight pause before CTA.

### BEAT 5 — CTA (33–38s)
- **VO:** "Comment REFLOG and I'll DM you the exact three-command recovery sequence."
- **On-screen:** `Comment "REFLOG" → recovery commands in your DMs`
- **Loop:** end frame = the `git fsck --dangling` terminal shot → invites rewatch.

---

## Caption (06 formula — the caption IS the product)

Comment "REFLOG" and I'll send you the exact recovery commands 👆

One `git filter-branch` command wiped 188MB from every commit in my repo's history. 20 minutes later I had 186MB of it back, byte-perfect.

The 3-command sequence (verbatim — copy, paste, swap in your own hashes):

1. Reflog —
```
git reflog
# find the last good commit hash before things broke, then:
git checkout <good-commit-hash> -- <path>
```
Shows every place HEAD has ever been (resets, rebases, filter-branch, all of it).

2. Dangling objects —
```
git fsck --dangling
git show <dangling-commit-hash>
```
Surfaces commits/blobs that are unreachable from any branch but not yet garbage-collected — for files deleted *before* the disaster.

3. Blob extraction —
```
git cat-file blob <blob-hash> > recovered_file.ext
```
Pulls back one exact file by its content hash. Byte-perfect.

Full write-up (with the prevention steps I added after — LFS, a guard hook, recovery tags) linked in bio.

#git #github #devtools #datascience #claude

**Keyword:** REFLOG
**DM payload:** the 3-command sequence above, pasted in full (no hosted link — this is a direct-paste deliverable, see `cheat_sheet.md` in this folder for the source copy).
**Pinned first comment:** the 3-command sequence (same text as DM payload) + "Comment REFLOG if the DM tool misses you."

## Thumbnail text (06 formula — outcome, not topic)

`188MB deleted. 186MB back in 20 min 🤯`
Alt: `I nuked my own repo. Git had already saved me.`

## YT Shorts delta

Same footage. CTA line swap: "The exact commands are in the description — comment if you want the prevention steps too." Commands = first block of description + pinned comment. `#Shorts` in title.

## Checklist (viral_reel_formula §per-reel)
- [ ] Hook recorded 5×, winner picked
- [ ] Terminal B-roll captured: `git reflog`, `git checkout`, `git fsck --dangling` (zoomed, ≤5s per clip)
- [ ] Captions burned in word-by-word; no clip > 4s; ~150 wpm
- [ ] Honesty guardrail: no "this always works" claim — scoped to this specific failure mode (rewritten history via filter-branch)
- [ ] Comment→DM tool armed with keyword REFLOG + the 3-command text payload
- [ ] Loop ends on `git fsck --dangling` frame
- [ ] VO word count checked against ~40s target before recording
