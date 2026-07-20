---
title: "Raw Thoughts Weekly — Operator Runbook"
type: doc
slug: raw-thoughts-weekly
tags: [content/doc]
---
# Raw Thoughts Weekly — Operator Runbook

Goal: 1 Life episode + 1 DS episode + 3-4 shorts each week, from ONE recording
session — raw thinking-out-loud, not scripted.

### Anytime (0 min)

- [ ] Thought strikes → append one bullet under `## thoughts` in `data/ideas/thought_inbox.md`.
- [ ] Good IG/YT comment → paste under `## audience`.

This is the engine — the week's videos are literally your week's thoughts.

### Monday — pick topics (~15 min)

1. [ ] Dashboard `http://localhost:8765` (`python3 scripts/dashboard.py`) →
      analytics → fetch_ideas → score buttons.
2. [ ] Paste any new comments into inbox `## audience`.
3. [ ] Pack button (or `python3 scripts/generate_prompt_pack.py --week <W>`;
      add `--pack-size 10` when DS needs more questions than the default 8 leaves room for).
4. [ ] Open `content/sessions/{W}/teleprompter.html` → keep only questions you
      actually feel like riffing on. Feeling like it IS the selection
      criterion — that's what makes it raw. Regenerate with `--force` (+ `--theme <filter>`
      if the pack feels dead).

### Recording day — one session (~30-45 min)

Greenscreen, fixed framing, teleprompter open. Per question:

- [ ] Pause ~3s → read the question word-for-word **in English**.
- [ ] Answer raw — code-switch English/Hinglish freely, **one thought per
      answer, 60-120s**.
- [ ] Botched take: pause ~2s, re-read the question, restart (slicer keeps the
      last take).
- [ ] Both niches in one session.
- [ ] Drop the file in `assets/raw/inbox/`.

### Processing (~20 min of clicking, via dashboard)

- [ ] Slice → per-clip composite (life bg for life questions, ds bg for ds
      questions) → trim.
- [ ] Captions on the 3-4 best shorts (`embedded-captions`, anchor identity).
- [ ] Episode (life) → episode (ds).
- [ ] Thumbnails (`python3 scripts/generate_thumbnail.py`).

Outputs land in `output/review/{W}/`.

### Publish (~20 min, manual by design)

1. [ ] Review `output/review/{W}/`, approve.
2. [ ] Long-form:
   ```
   python3 scripts/upload_youtube.py --channel "Breath of Life" --video <episode_life.mp4> --title <t> --description <d> --tags <tags> --publish-at <ISO datetime>
   python3 scripts/upload_youtube.py --channel "Breath of Data Science" --video <episode_ds.mp4> --title <t> --description <d> --tags <tags> --publish-at <ISO datetime>
   ```
   Spread `--publish-at` times across the week.
3. [ ] Shorts: `python3 scripts/load_posts.py` generates `output/scheduled/upload_shorts.sh`
      — run it (`bash output/scheduled/upload_shorts.sh`); IG reels ship via the
      `load_posts.py` → `scheduler.py` path.

## Rules that make it work

- 80% good = publish. No re-records for polish.
- Question read verbatim = non-negotiable — it's the slice marker AND the hook.
- One thought per answer = the short is self-contained for free.
