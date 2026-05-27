#!/usr/bin/env python3
"""Auto-generate AI B-roll for any YT script that doesn't have a VIDEO_MAP.json yet.

Designed to run unattended at 1 AM via launchd. Skips scripts already processed.

Usage:
  python3 scripts/auto_generate_broll.py
  python3 scripts/auto_generate_broll.py --dry-run
  python3 scripts/auto_generate_broll.py --backend muapi
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO / "content" / "scripts"
VIDEOS_DIR = REPO / "assets" / "videos"

NICHE_PATTERNS = [
    (re.compile(r"data.science.tech|data-science", re.IGNORECASE), "ds"),
    (re.compile(r"life.self.dev|life-self", re.IGNORECASE), "life"),
    (re.compile(r"poetry.quotes|poetry-quotes", re.IGNORECASE), "poetry"),
]


def detect_niche(script_path: Path) -> str | None:
    for pattern, niche in NICHE_PATTERNS:
        if pattern.search(script_path.name):
            return niche
    return None


def has_video_map(script_path: Path) -> bool:
    slug = script_path.stem
    return (VIDEOS_DIR / slug / "VIDEO_MAP.json").exists()


def has_broll_cues(script_path: Path) -> bool:
    text = script_path.read_text()
    return bool(re.search(r'\[BROLL:', text, re.IGNORECASE))


def find_pending_scripts() -> list[tuple[Path, str]]:
    pending = []
    for script in sorted(SCRIPTS_DIR.glob("*_yt.md")):
        niche = detect_niche(script)
        if not niche:
            continue
        if not has_broll_cues(script):
            continue
        if has_video_map(script):
            continue
        pending.append((script, niche))
    return pending


def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Auto-generate B-roll for scripts missing VIDEO_MAP.json")
    parser.add_argument("--dry-run", action="store_true", help="Show pending scripts, skip generation")
    parser.add_argument("--backend", default="muapi", choices=["muapi"])
    parser.add_argument("--model", default="seedance-lite-t2v")
    args = parser.parse_args()

    pending = find_pending_scripts()

    if not pending:
        log("All scripts have B-roll. Nothing to do.")
        return

    log(f"Found {len(pending)} script(s) missing B-roll:")
    for script, niche in pending:
        log(f"  [{niche}] {script.name}")

    if args.dry_run:
        log("Dry-run — skipping generation.")
        return

    python = sys.executable
    generate_script = str(REPO / "scripts" / "generate_video_ai.py")

    for script, niche in pending:
        log(f"Generating B-roll: [{niche}] {script.name}")
        cmd = [
            python, generate_script,
            "--script", str(script),
            "--niche", niche,
            "--backend", args.backend,
        ]
        if args.backend == "muapi":
            cmd += ["--model", args.model]

        result = subprocess.run(cmd, cwd=str(REPO))
        if result.returncode == 0:
            log(f"  Done: {script.stem}")
        else:
            log(f"  Failed (exit {result.returncode}): {script.stem}")

    log("Auto B-roll generation complete.")


if __name__ == "__main__":
    main()
