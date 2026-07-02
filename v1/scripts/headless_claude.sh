#!/usr/bin/env bash
# headless_claude.sh — reliability wrapper for headless `claude -p` calls.
#
# Why (session audit 2026-07): headless claude calls timed out at 30/120/300/600s
# across 10 sessions, and one session burned 16 retries on
# {"status":401,"INVALID_ACCESS_TOKEN"} because retry logic treated an auth
# failure as transient. This wrapper:
#   1. Credential preflight  — cheap "Say ok" ping (short timeout) before the real call
#   2. Configurable timeout  — CLAUDE_TIMEOUT env or -t flag (default 300s)
#   3. Retry ×2 w/ backoff   — ONLY on timeout / 429 / 529 / overloaded (5s, 15s)
#   4. NO retry on 401       — fail fast with a clear message (exit 2)
#   5. Env tag               — CLAUDE_HEADLESS_TAG marks programmatic sessions in logs
#   6. Auth-env strip        — drops ANTHROPIC_API_KEY* / stale OAuth token vars so the
#                              CLI uses subscription OAuth (same fix as
#                              v1/scripts/lib/hf_beat_builder.py:_call_claude)
#
# Usage:
#   v1/scripts/headless_claude.sh [-t seconds] [-m model] [--no-preflight] [--keep-auth-env] "PROMPT"
#   echo "PROMPT" | v1/scripts/headless_claude.sh -t 120
#
# Exit codes: 0 ok · 1 failed after retries · 2 auth (401) — do NOT retry · 3 usage
#
# NOTE: macOS has no GNU `timeout` by default — a bash watchdog is used instead.
# Python callers should keep using v1/scripts/lib/claude_cli.py (caching); this
# wrapper is for shell/cron/pipeline glue and new callers.

set -u

TIMEOUT="${CLAUDE_TIMEOUT:-300}"
MODEL=""
PREFLIGHT=1
STRIP_AUTH_ENV=1
PREFLIGHT_TIMEOUT="${CLAUDE_PREFLIGHT_TIMEOUT:-20}"
MAX_RETRIES=2                 # retries AFTER the first attempt (3 attempts total)
BACKOFF=(5 15)
export CLAUDE_HEADLESS_TAG="${CLAUDE_HEADLESS_TAG:-headless-pipeline}"

PROMPT=""
while [ $# -gt 0 ]; do
  case "$1" in
    -t) TIMEOUT="$2"; shift 2 ;;
    -m) MODEL="$2"; shift 2 ;;
    --no-preflight) PREFLIGHT=0; shift ;;
    --keep-auth-env) STRIP_AUTH_ENV=0; shift ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) PROMPT="$1"; shift ;;
  esac
done
if [ -z "$PROMPT" ] && [ ! -t 0 ]; then PROMPT="$(cat)"; fi
if [ -z "$PROMPT" ]; then
  echo "[headless_claude] ERROR: no prompt given (arg or stdin)" >&2
  exit 3
fi

CLAUDE_BIN="$(command -v claude || echo "$HOME/.local/bin/claude")"
if [ ! -x "$CLAUDE_BIN" ]; then
  echo "[headless_claude] ERROR: claude CLI not found on PATH" >&2
  exit 1
fi

# Strip vars that force API-key auth over subscription OAuth (source of the
# INVALID_ACCESS_TOKEN 401 loop). Mirrors hf_beat_builder._call_claude.
if [ "$STRIP_AUTH_ENV" -eq 1 ]; then
  unset ANTHROPIC_API_KEY ANTHROPIC_API_KEY_FREE ANTHROPIC_AUTH_TOKEN \
        CLAUDE_CODE_OAUTH_TOKEN ANTHROPIC_BASE_URL ANTHROPIC_MODEL 2>/dev/null || true
fi

TAG="[headless_claude:${CLAUDE_HEADLESS_TAG}]"
OUTFILE="$(mktemp)"; ERRFILE="$(mktemp)"
trap 'rm -f "$OUTFILE" "$ERRFILE"' EXIT

# run_with_timeout <seconds> <args...>  — bash watchdog (macOS lacks GNU timeout).
# Writes stdout->$OUTFILE stderr->$ERRFILE. Returns 124 on timeout, else exit code.
run_with_timeout() {
  local secs="$1"; shift
  "$@" >"$OUTFILE" 2>"$ERRFILE" &
  local pid=$!
  local waited=0
  while kill -0 "$pid" 2>/dev/null; do
    if [ "$waited" -ge "$secs" ]; then
      kill -TERM "$pid" 2>/dev/null; sleep 2; kill -KILL "$pid" 2>/dev/null
      wait "$pid" 2>/dev/null
      return 124
    fi
    sleep 1; waited=$((waited + 1))
  done
  wait "$pid"
}

is_auth_error() {  # 401 / invalid token → never retry
  grep -qiE '"status" *: *401|INVALID_ACCESS_TOKEN|authentication_error|OAuth token (is )?(invalid|expired)|401' "$OUTFILE" "$ERRFILE" 2>/dev/null
}
is_transient_error() {  # 429 / 529 / overloaded → retry with backoff
  grep -qiE '"status" *: *(429|529)|overloaded_error|rate.limit|too many requests' "$OUTFILE" "$ERRFILE" 2>/dev/null
}

# ── 1. Credential preflight ────────────────────────────────────────────────
if [ "$PREFLIGHT" -eq 1 ]; then
  run_with_timeout "$PREFLIGHT_TIMEOUT" "$CLAUDE_BIN" -p "Say ok" --model haiku
  rc=$?
  if [ $rc -ne 0 ]; then
    if is_auth_error; then
      echo "$TAG FATAL: credential preflight got 401/invalid token. Fix auth (claude login /" >&2
      echo "$TAG        remove stale ANTHROPIC_*/CLAUDE_CODE_OAUTH_TOKEN from env) — NOT retrying." >&2
      exit 2
    fi
    echo "$TAG WARN: preflight failed (rc=$rc, not auth) — continuing to real call." >&2
    sed 's/^/    /' "$ERRFILE" | tail -3 >&2
  fi
fi

# ── 2-4. Real call with timeout + bounded retry ────────────────────────────
CMD=("$CLAUDE_BIN" -p "$PROMPT")
[ -n "$MODEL" ] && CMD+=(--model "$MODEL")

attempt=0
while :; do
  attempt=$((attempt + 1))
  run_with_timeout "$TIMEOUT" "${CMD[@]}"
  rc=$?

  if [ $rc -eq 0 ]; then
    cat "$OUTFILE"
    exit 0
  fi

  if is_auth_error; then
    echo "$TAG FATAL: 401/invalid token on attempt $attempt — NOT retrying. Fix credentials first." >&2
    tail -3 "$ERRFILE" >&2
    exit 2
  fi

  if [ $rc -eq 124 ]; then
    reason="timeout after ${TIMEOUT}s"
  elif is_transient_error; then
    reason="transient API error (429/529/overloaded)"
  else
    echo "$TAG FATAL: non-retryable failure (rc=$rc) on attempt $attempt:" >&2
    tail -5 "$ERRFILE" >&2
    exit 1
  fi

  if [ $attempt -gt $MAX_RETRIES ]; then
    echo "$TAG FATAL: still failing after $attempt attempts ($reason)." >&2
    exit 1
  fi
  wait_s="${BACKOFF[$((attempt - 1))]:-15}"
  echo "$TAG attempt $attempt failed ($reason) — retrying in ${wait_s}s" >&2
  sleep "$wait_s"
done
