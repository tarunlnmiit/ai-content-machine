---
title: "Content Pipeline 2026 — \"Subtract to Focus\" (canonical)"
type: doc
slug: pipeline-2026
tags: [content/doc]
---
# Content Pipeline 2026 — "Subtract to Focus" (canonical)

*Adopted 2026-06-20. This is the source of truth. Where any older guide disagrees, this wins.*

> **Additive lane (2026-06-21):** A **voiceover-first / audio-only** video path exists alongside
> the talking-head lane — record an audio voiceover (no face) and the pipeline builds a full-screen
> B-roll-montage long-form + auto-detected portrait shorts, with captions burned by hyperframes.
> It does NOT replace anything here. See **[voiceover-runner.md](voiceover-runner.md)**.

> **One-command blog pipeline (2026-06-21):** `scripts/run_blog_pipeline.py --input <blog.md>`
> (or `--topic … --niche …`) produces ALL non-video derivatives + media in one idempotent run
> (text, social images, carousel, slide deck, IG reel brief, thumbnail, worksheet outline → stage).
> Videos stay separate. See **[blog-pipeline.md](blog-pipeline.md)**.

## Why this changed

Analytics said the effort was pouring into dead surfaces and starving the live one:
Instagram was the only channel with real engagement (300+ likes / 120+ comments per week),
while YouTube long-form (5–24% retention) and ~56 shorts/week and Twitter (3 likes/week) ate
most of the production budget. Two diseases: an **open loop** (make blind, upload all, repeat)
and **one idea cut 14 ways**. The fix is subtraction + a feedback loop + auto-publishing.

## Weekly output (target)

| Niche | Blog | Long-form YT | Reels/shorts |
|---|---|---|---|
| DS | 1 (Medium) | 1 full long-form | 2 core-idea reels + 1 virality reel + 1 comment→DM tool reel |
| Life | 1 (Medium) | 1 full long-form | 2 core-idea reels + 1 virality reel + 1 comment→DM tool reel |
| Poetry | 1 (Medium, poem + 150–350w essay) | 1 landscape (poem + couple lines before/after) | 1 poem short = **poem only** |

≈9 reels/week (down from ~56), each a **distinct idea**, not a slice of the long-form.

## Per-platform format (stop spraying the same asset)

- **Instagram (Reels)** — primary for all shorts; Facebook auto-mirrors. Static posts/carousels too.
- **YouTube** — 3 long-form (1/niche) + Shorts (same reel cuts). Tool-reel link in pinned comment.
- **LinkedIn** — 1 text post/blog + **DS & Life slide deck (PDF/document)**. Blog link in the
  **pinned first comment**, never the body. No vertical shorts on LinkedIn.
- **Threads** — native text mirror (cheap).
- **Twitter** — dropped entirely.
- **Medium** — blogs + worksheet email-capture CTA (DS/Life).

## Automation — minimal manual

One stage step → the daemon fires everything:

```
repurpose_blog.py → load_posts.py (stages LinkedIn/Threads/Instagram) → scheduler.py daemon
```

- **LinkedIn** — active (employer cleared), `post_linkedin.py`.
- **Instagram / Threads** — Meta Graph API (`post_instagram.py`, `post_threads.py`, `lib/meta_graph.py`).
  IG ingests from a **public media URL**; host the asset first (Drive). Stories stay manual.
- **Facebook** — mirrors from Instagram (optional direct `post_facebook.py`).
- **YouTube** — `upload_youtube.py`, `upload_youtube_shorts_batch.py`.
- **Comment→DM** — SuperProfile / CreatorFlow (keyword → DM).
- **One-time setup** — Meta Business account, IG↔FB Page link, long-lived tokens, Threads API:
  see `docs/one-time-platform-setup.md`.

**Manual, and only this (honesty guardrail — "minimal manual", not "zero"):**
record the talking-head video · ~10-min content approval · reply to comments/DMs in the window.

### What is actually live today vs scaffolded (honesty guardrail)

**Live now (verified to stage + dispatch):**
- **LinkedIn** text post + **pinned first comment** (blog link), via `post_linkedin.py`. ✅
- **Threads** native text post, via `post_threads.py`. ✅
- **YouTube** long-form + Shorts uploads. ✅

**Wired — needs only a Vercel Blob token + one smoke test:**
- **Instagram Reels auto-publish.** Full chain exists: render reels →
  `scripts/upload_reels_blob.py --week <Wnn>` hosts each at a public URL and writes
  `data/reel_media_urls.json` → `load_posts.py` stages them → `scheduler.py` →
  `post_instagram.post_reel()`. Caption is the post-ready `instagram_caption_clean.txt` (no
  brief header). **Gate:** set `BLOB_READ_WRITE_TOKEN` in `.env` and verify one upload; until
  then IG reels stay manual.
- **Instagram static (image/carousel).** Clean caption now generated
  (`instagram_caption_clean.txt`). Still needs a step to write `social.ig_media_url(s)` into
  `schedule.json` (host the static image) before it auto-fires.

**Still manual:**
- **Facebook** direct publish (mirrors from IG in practice — no action needed).
- IG Stories (not API-publishable).

## Close the loop (run before producing)

`python3 scripts/weekly_winners.py` reads `data/analytics/weekly_insights.md` and prints last
week's IG/YT winners. Pick this week's 2 core ideas to RHYME with the winner; if a niche has no
winner, give it the maintenance minimum and push the niche that IS winning (stagger, don't spread).

## Owned audience

Substack is retired. The **worksheet email list** (DS/Life, via the Vercel/Kit app) is the only
channel you own — everything else is rented from an algorithm. Treat it as core, not a footnote.

---

## v2 cadence addendum (2026-07-12) — Raw-First Reboot

Supersedes the ~9-reel weekly target above. Diagnosis: decision overload broke the loop
(analytics stalled W24 → stale ideas → nothing produced). Fix = fewer outputs, one decision
surface, raw unscripted recording (scripted talking-head killed watch time).

**Weekly output:**
- 1 long-form raw Q&A episode (niche rotates; routes to that niche's channel)
- 3–4 reels (per-question clips from the session), IG + YT Shorts, ALL ENGLISH
- 1 blog per niche + Medium + worksheets (DS/Life) — spine unchanged
- DS build-in-public reel only when a session naturally yields one

**Paused:** carousels, quote cards, slide decks, faceless-voiceover lane,
scripted-talking-head-from-blog, the 9-reel target. Worksheets STAY.

**Human touchpoints (~2–2.5 hrs/wk):** Mon menu check (15 min) · optional Wed ad-hoc clip ·
weekend batch sitting (60–90 min, greenscreen, teleprompter prompt pack) · Sun review (20 min).

**Lane doc:** `docs/guides/raw-session-lane.md`. **Runbooks (Opus/Sonnet/Haiku):**
`v1/docs/runbooks/00-INDEX.md`.
