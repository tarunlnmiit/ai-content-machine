# Content Pipeline 2026 — "Subtract to Focus" (canonical)

*Adopted 2026-06-20. This is the source of truth. Where any older guide disagrees, this wins.*

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

**Scaffolded but NOT yet fully wired — stays MANUAL until the plumbing lands:**
- **Instagram Reels auto-publish.** `post_instagram.post_reel()` works, but: (a) reels are not
  staged by `load_posts.py` yet (only YouTube Shorts are), and (b) IG ingests from a **public
  video URL** that nothing hosts yet. → **Post reels to IG manually for now.**
- **Instagram static (image/carousel).** `insert_instagram` only stages when
  `schedule.json` carries `social.ig_media_url(s)`, which no step writes yet; and
  `instagram_caption.txt` is currently a human *brief* (leads with `Format:/Why:`), not a clean
  caption. → Needs: a media-URL writer + a caption-only field before IG static auto-fires.
- **Facebook** direct publish (mirrors from IG in practice).

Closing these three is the next work item to reach true "minimal manual" on Instagram.

## Close the loop (run before producing)

`python3 scripts/weekly_winners.py` reads `data/analytics/weekly_insights.md` and prints last
week's IG/YT winners. Pick this week's 2 core ideas to RHYME with the winner; if a niche has no
winner, give it the maintenance minimum and push the niche that IS winning (stagger, don't spread).

## Owned audience

Substack is retired. The **worksheet email list** (DS/Life, via the Vercel/Kit app) is the only
channel you own — everything else is rented from an algorithm. Treat it as core, not a footnote.
