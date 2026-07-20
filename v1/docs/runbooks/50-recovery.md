---
title: "Runbook 50 — Recovery (tier: Sonnet)"
type: doc
slug: 50-recovery
tags: [content/doc]
---
# Runbook 50 — Recovery (tier: Sonnet)

Standard fixes for known failure classes. Fix the NAMED cause; never flail
parameters. Two failed fix attempts on the same issue = stop + human status.

## Scheduler / scheduling.db
1. `tail -20 scheduler.error.log` (repo root of v1) — read the actual error.
2. Stale/duplicate jobs: inspect `data/scheduling.db` (`sqlite3`, read first!).
   Only mark rows failed/cancelled — never delete rows.
3. Daemon not running: restart under pm2/launchd per `docs/guides/pipeline-2026.md`.
4. Meta token expired (IG/FB/Threads errors) → human task, see
   `docs/one-time-platform-setup.md`. Note and stop.

## claude CLI failures
- Timeout/429/529: retry max 2 (5s, 15s backoff). Persistent → smaller prompt.
- 401 / INVALID_ACCESS_TOKEN: STOP. Strip `ANTHROPIC_API_KEY*`,
  `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN`, `ANTHROPIC_BASE_URL` from
  the subprocess env (subscription OAuth). Pattern: `hf_beat_builder._call_claude`.
- Empty/garbage output with cache=True: delete the entry in `.cache/claude/` and
  re-run once.

## Whisper / transcription
- openai-whisper CLI segfault (OMP #15): expected on this machine — code already
  uses faster-whisper API. If a script shells out to `whisper`, that's the bug.
- Hinglish/heavy-accent mismatches in the slicer: the slicer keys on ENGLISH
  spoken questions; if matches fail wholesale, extract 30s audio and check the
  transcript sidecar in `content/sessions/{week}/work/` before touching thresholds.

## ffmpeg / renders
- Homebrew ffmpeg (`/opt/homebrew/bin/`) has NO libass — caption burns need the
  conda ffmpeg (content_engine_env), encoder h264_videotoolbox (not libx264).
- Silent output: HyperFrames renders have no audio — mux from source, then
  ffprobe BOTH streams (video-edit-playbook gate).
- No GNU `timeout` on macOS: use the bash watchdog pattern from `headless_claude.sh`.

## Greenscreen
- Subject transparent/ghosted → blend too high; cap 0.05 (`composite_greenscreen.py`
  default 0.03). Green haze → similarity up in 0.02 steps.
- Calibration won't converge → lighting problem; run `/greenscreen-composite`
  interactively for full gates. Never use Palmier key.chroma.

## Scene validation
- Any "Scene validation failed" → `scene-validation-autofix` skill. Standard fix
  per error class, re-validate, only then re-render. No iterating blind.

## Analytics
- `collect_analytics.py` summary unavailable → check `claude -p` works at all
  (`claude -p "say ok"`); then re-run. YT quota errors → note, retry tomorrow.

## When to wake the human
Meta/Google token expiry · anything wanting a KB/strategy edit · data loss risk
· the same failure after 2 distinct, correct fixes.
