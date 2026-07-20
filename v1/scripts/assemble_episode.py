#!/usr/bin/env python3
"""Assemble a podcast-style long-form episode from sliced session clips.

Reads content/sessions/{week}/session_manifest.json (from slice_raw_session.py),
concatenates the selected clips in order, and emits:

    output/review/{week}/episode_{niche}.mp4         — the episode
    output/review/{week}/episode_{niche}_meta.md     — title options, description,
                                                        YouTube chapters, channel

Clips should already be trimmed (video_trim.py) and composited
(composite_greenscreen.py) — this script only orders, concatenates, and
writes metadata. Per-niche episodes route to that niche's channel.

Usage:
    python3 scripts/assemble_episode.py --week 2026-W29 --niche life
    python3 scripts/assemble_episode.py --week 2026-W29 --niche life \\
        --clips content/sessions/2026-W29/clips/q01_composited.mp4 ...   # explicit order
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.claude_cli import call_claude      # noqa: E402
from lib.niche_config import model_for      # noqa: E402
from lib.video_utils import probe_duration  # noqa: E402

FFMPEG = "/opt/homebrew/bin/ffmpeg"
SESSIONS_DIR = REPO / "content" / "sessions"
REVIEW_DIR = REPO / "output" / "review"

CHANNELS = {
    "life": "Breath of Life (@breathoflife_)",
    "poetry": "Breath of Poetry (@breathofpoetry)",
    "ds": "Breath of Data Science (@breathofdatascience)",
}


def _fmt_ts(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def resolve_clips(week: str, niche: str, explicit: list[str] | None) -> list[dict]:
    """[{path, question}] in episode order."""
    manifest_path = SESSIONS_DIR / week / "session_manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"No manifest at {manifest_path} — run slice_raw_session.py first.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    by_stem = {Path(c["clip"]).stem: c for c in manifest.get("clips", [])}

    if explicit:
        out = []
        for p in explicit:
            path = Path(p).resolve()
            qid = path.stem.split("_")[0]
            entry = by_stem.get(qid) or by_stem.get(path.stem)
            out.append({"path": path, "question": entry["question"] if entry else path.stem})
        return out

    pack_path = SESSIONS_DIR / week / "prompt_pack.json"
    pack = json.loads(pack_path.read_text(encoding="utf-8")) if pack_path.exists() else {"questions": []}
    niche_qids = {q["id"] for q in pack["questions"] if q["niche"] == niche} or set(by_stem)

    out = []
    for c in manifest.get("clips", []):
        if c["qid"] not in niche_qids:
            continue
        base = REPO / c["clip"]
        # prefer the most-processed variant that exists
        for candidate in (base.with_name(f"{base.stem}_trimmed_composited.mp4"),
                          base.with_name(f"{base.stem}_composited.mp4"),
                          base.with_name(f"{base.stem}_trimmed.mp4"),
                          base):
            if candidate.exists():
                out.append({"path": candidate, "question": c["question"]})
                break
    return out


def concat(clips: list[dict], out: Path) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        for c in clips:
            f.write(f"file '{c['path']}'\n")
        list_path = f.name
    out.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [FFMPEG, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", list_path,
         "-c:v", "libx264", "-crf", "18", "-preset", "medium",
         "-c:a", "aac", "-b:a", "192k", str(out)],
        capture_output=True, text=True)
    Path(list_path).unlink(missing_ok=True)
    if r.returncode != 0:
        raise SystemExit(f"concat failed: {r.stderr[-500:]}")


def build_meta(clips: list[dict], niche: str, week: str) -> str:
    chapters, t = [], 0.0
    for c in clips:
        chapters.append(f"{_fmt_ts(t)} {c['question']}")
        t += probe_duration(c["path"])
    questions = "\n".join(f"- {c['question']}" for c in clips)
    prompt = f"""A creator recorded a raw, unscripted Q&A episode ({niche} niche) answering these questions:
{questions}

Write, in this exact format with these exact headers. Output NOTHING before the first header:

## Title options
Three YouTube title options, each under 60 chars, curiosity-driven, no clickbait words like "SHOCKING". State the OUTCOME or tension, not the topic.

## Description
2 short paragraphs, conversational, first line hooks (it shows in search). No hashtags.

Banned words: "In conclusion", "Dive into", "Leverage", "Game-changer", "Synergy"."""
    try:
        meta = call_claude(prompt, cache=True, timeout=120, model=model_for("shorts_meta")).strip()
    except Exception as e:
        meta = f"## Title options\n(generation failed: {e})\n\n## Description\n(write manually)"
    chapter_block = "\n".join(chapters)
    return f"""# Episode — {week} · {niche}

**Channel:** {CHANNELS.get(niche, niche)}
**Total length:** {_fmt_ts(t)}

{meta}

## Chapters (paste into description)
{chapter_block}
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Concat session clips into a long-form episode.")
    ap.add_argument("--week", required=True)
    ap.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    ap.add_argument("--clips", nargs="*", help="explicit clip paths in order (default: manifest order)")
    args = ap.parse_args()

    clips = resolve_clips(args.week, args.niche, args.clips)
    if not clips:
        print(f"No {args.niche} clips found for {args.week}.")
        return 1
    print(f"[episode] {len(clips)} clips:")
    for c in clips:
        print(f"  • {c['path'].name} — {c['question'][:60]}")

    out = REVIEW_DIR / args.week / f"episode_{args.niche}.mp4"
    concat(clips, out)
    dur = probe_duration(out)
    print(f"[episode] ✓ {out.relative_to(REPO)} ({_fmt_ts(dur)})")

    meta_path = out.with_name(f"episode_{args.niche}_meta.md")
    meta_path.write_text(build_meta(clips, args.niche, args.week), encoding="utf-8")
    print(f"[episode] ✓ {meta_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
