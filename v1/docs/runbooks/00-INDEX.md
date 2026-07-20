---
title: "Runbook Index — Content Machine Weekly Operations"
type: doc
slug: 00-index
tags: [content/doc]
---
# Runbook Index — Content Machine Weekly Operations

Operating manual for running the machine WITHOUT Fable. Each runbook names the
cheapest model tier allowed to run it. Read `GUARDRAILS.md` first — it applies
to every runbook and every model.

All commands run from `/Users/tarungupta/Making It Big/Claude/content-machine/v1/`
(quote paths — repo has spaces; never `cd` inside compound commands).

## Routing table

| Task | Runbook | Minimum tier | When |
|---|---|---|---|
| Weekly menu prep (analytics → ideas → prompt pack) | `10-monday-menu.md` | Haiku (Sonnet if anything errors) | Sun night / Mon AM |
| Process a recorded session → clips, reels, episode | `20-process-session.md` | Sonnet | After each recording lands in `assets/raw/inbox/` |
| Publish approved outputs (thumbnails, uploads, staging) | `30-publish.md` | Haiku | After human ticks ✅ in review |
| Weekly blog + derivatives | `40-weekly-blog.md` | Opus | Per blog slot |
| Anything broken (scheduler, Whisper, ffmpeg, DB) | `50-recovery.md` | Sonnet | On failure |

## Tier policy

- **Opus** — editorial judgment inside a blog (word choice, structure). Nothing else.
- **Sonnet** — pipeline execution; may choose among machine-scored options
  (e.g. which 3 clips become reels, using virality scores). Never invents new
  formats, cadence, or strategy.
- **Haiku** — deterministic commands only, in the exact order written. If a
  command fails twice or output doesn't match the runbook's success criteria:
  STOP, write a one-line status, escalate to Sonnet.

## Escalation ladder

Haiku → Sonnet → human (leave status in `output/review/{week}/STATUS.md`).
Never escalate by improvising. A skipped step is reported, not silently absorbed.
