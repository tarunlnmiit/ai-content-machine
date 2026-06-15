#!/usr/bin/env python3
"""Cached Claude CLI subprocess wrapper.

Why: ~8 scripts shell out to `claude -p <prompt>`. Re-runs cost 5-30s each.
Cache by prompt hash → instant on repeat.

Usage:
    from lib.claude_cli import call_claude
    out = call_claude("write a haiku about X", cache=True, timeout=60)

Cache lives at <repo>/.cache/claude/<sha1>.txt. Delete to bust.
"""

import hashlib
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent.parent
CACHE_DIR = REPO / ".cache" / "claude"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CACHE_TTL_DAYS = 30

# Retry policy for transient claude CLI failures (non-zero exit / timeout).
MAX_RETRIES = 3
RETRY_BACKOFF_SEC = (2, 4, 8)

TEMP_DIRECTIVES = {
    "low":  "Respond with analytical precision. Prefer concrete, factual phrasing. Use specific numbers and examples. Avoid metaphor.",
    "mid":  "Respond warmly and conversationally with personal voice. Mix concrete examples with reflective insight. Vary sentence length.",
    "high": "Respond with lyrical, exploratory voice. Vary rhythm and structure. Lean into metaphor, imagery, and emotional resonance.",
}


def _temp_directive(temperature: float) -> str:
    if temperature <= 0.5:
        return TEMP_DIRECTIVES["low"]
    elif temperature <= 1.0:
        return TEMP_DIRECTIVES["mid"]
    else:
        return TEMP_DIRECTIVES["high"]


def _cache_key(prompt: str) -> Path:
    h = hashlib.sha1(prompt.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{h}.txt"


def _cache_fresh(path: Path, ttl_days: int = CACHE_TTL_DAYS) -> bool:
    if not path.exists():
        return False
    age_days = (time.time() - path.stat().st_mtime) / 86400
    return age_days <= ttl_days


def _heartbeat(stop: threading.Event, label: str) -> None:
    """Print elapsed time + spinner to stderr while subprocess runs."""
    frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    t0 = time.time()
    i = 0
    while not stop.is_set():
        elapsed = int(time.time() - t0)
        sys.stderr.write(f"\r  {frames[i % len(frames)]} {label} — {elapsed}s elapsed   ")
        sys.stderr.flush()
        i += 1
        stop.wait(0.1)
    sys.stderr.write("\r" + " " * 60 + "\r")
    sys.stderr.flush()


def _run_cmd(cmd: list[str], timeout: int, stream: bool, progress_label: str) -> str:
    """Run the claude subprocess once. Returns stdout.

    Raises RuntimeError on non-zero exit, subprocess.TimeoutExpired on timeout.
    """
    if not stream:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if res.returncode != 0:
            raise RuntimeError(f"claude CLI failed (exit {res.returncode}): {res.stderr[-300:]}")
        return res.stdout

    stop = threading.Event()
    hb = threading.Thread(target=_heartbeat, args=(stop, progress_label), daemon=True)
    hb.start()
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            out, err = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            raise
        if proc.returncode != 0:
            raise RuntimeError(f"claude CLI failed (exit {proc.returncode}): {err[-300:]}")
    finally:
        stop.set()
        hb.join(timeout=1)
    sys.stderr.write(f"  ✓ {progress_label} — {len(out):,} chars received\n")
    sys.stderr.flush()
    return out


def call_claude(
    prompt: str,
    cache: bool = True,
    timeout: int = 120,
    model: Optional[str] = None,
    ttl_days: int = CACHE_TTL_DAYS,
    temperature: Optional[float] = None,
    normalize: bool = False,
    stream: bool = False,
    progress_label: str = "Claude thinking",
    retries: int = MAX_RETRIES,
) -> str:
    """Invoke claude CLI, optionally cached. Returns stdout text.

    Args:
        temperature:    AutoTune param — 0.4 DS, 0.85 Life, 1.15 Poetry.
        normalize:      Run STM text normalization on output (strip filler/hedges).
        stream:         Show live progress (elapsed timer + bytes received) on stderr.
        progress_label: Label shown next to spinner when stream=True.
    Raises RuntimeError on non-zero exit if cache miss.
    """
    key = _cache_key(f"{model or ''}:{temperature if temperature is not None else ''}:{prompt}")
    if cache and _cache_fresh(key, ttl_days):
        if stream:
            sys.stderr.write(f"  [cache hit] {progress_label}\n")
        return key.read_text()

    cmd = ["claude", "-p", prompt]
    if model:
        cmd += ["--model", model]
    if temperature is not None:
        cmd += ["--append-system-prompt", _temp_directive(temperature)]

    last_err: Optional[Exception] = None
    out = ""
    for attempt in range(retries):
        try:
            out = _run_cmd(cmd, timeout, stream, progress_label)
            break
        except (RuntimeError, subprocess.TimeoutExpired) as e:
            last_err = e
            if attempt < retries - 1:
                wait = RETRY_BACKOFF_SEC[min(attempt, len(RETRY_BACKOFF_SEC) - 1)]
                sys.stderr.write(
                    f"  ⚠ claude attempt {attempt + 1}/{retries} failed: "
                    f"{str(e)[-120:]} — retrying in {wait}s\n"
                )
                sys.stderr.flush()
                time.sleep(wait)
    else:
        raise RuntimeError(f"claude CLI failed after {retries} attempts: {last_err}")

    if normalize:
        from lib.text_normalizer import normalize as _normalize
        out = _normalize(out)
    if cache:
        try:
            key.write_text(out)
        except OSError:
            pass
    return out


def bust_cache() -> int:
    """Delete all cache entries. Returns count."""
    n = 0
    for f in CACHE_DIR.glob("*.txt"):
        f.unlink()
        n += 1
    return n


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--bust", action="store_true", help="Clear cache")
    ap.add_argument("--stats", action="store_true", help="Show cache stats")
    args = ap.parse_args()

    if args.bust:
        print(f"removed {bust_cache()} entries")
    elif args.stats:
        files = list(CACHE_DIR.glob("*.txt"))
        total = sum(f.stat().st_size for f in files)
        print(f"{len(files)} entries, {total/1024:.1f} KB")
    else:
        print(f"Cache dir: {CACHE_DIR}")
