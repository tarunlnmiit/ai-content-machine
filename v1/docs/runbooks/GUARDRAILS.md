---
title: "GUARDRAILS — apply to every runbook, every model tier"
type: doc
slug: guardrails
tags: [content/doc]
---
# GUARDRAILS — apply to every runbook, every model tier

## NEVER (no exceptions, no matter how reasonable it seems)

1. **Never publish, upload, post, or schedule content the human has not approved**
   via the weekly menu (`data/ideas/weekly_menu.md`) or the review folder
   (`output/review/{week}/`). "It looks ready" is not approval.
2. **Never edit strategy KB files**: `data/kb/master_brief.md`,
   `data/kb/viral_reel_formula.md`, `data/kb/reels/*`, `data/kb/voice/*`,
   `data/kb/raw_take_questions.json`. Read-only. Changes are a human+Fable decision.
3. **Never change model routing** (`scripts/lib/niche_config.py:MODEL_BY_TASK`),
   brand assets configs, or `.env`.
4. **Never delete or overwrite anything under `assets/raw/`** — raw recordings
   are irreplaceable. Slicer/trimmer outputs go to new files, always.
5. **Never invent new content formats, hooks outside the KB, or cadence changes.**
   The formats are: raw-session episode, per-question reels, blogs, worksheets.
6. **Never retry a failing publish more than 2×.** Two failures = stop + status note.
7. **Never claim done without the runbook's verification step passing** (probe
   output streams, file exists + nonzero size, etc.). "Should have worked" = not done.
8. **On 401 / INVALID_ACCESS_TOKEN from claude CLI: stop immediately** — strip
   `ANTHROPIC_API_KEY*`, `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN`,
   `ANTHROPIC_BASE_URL` from subprocess env (subscription OAuth). See CLAUDE.md.

## ALWAYS

1. Log what you did to `output/review/{week}/STATUS.md` — one line per action,
   append-only: `[2026-07-14 21:03] sliced session.mov → 7 clips, q05 unmatched`.
2. Leave the human a one-line summary at the end of every run: what shipped,
   what's waiting, what broke.
3. Verify renders have BOTH video and audio streams (ffprobe) — HyperFrames
   renders are silent by default; mux audio (see video-edit-playbook skill).
4. Quote all paths (spaces in repo path). Never `cd` in compound commands.
5. Max 3 parallel `claude -p` sessions. Per-stage timeouts per CLAUDE.md; a task
   that times out twice at budget needs a smaller prompt, not a bigger timeout.
6. Keep chromakey `blend` ≤ 0.05 and key in ffmpeg only — never Palmier key.chroma
   (validated failure: alpha veil).
