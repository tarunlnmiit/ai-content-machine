#!/usr/bin/env python3
"""Slice a raw recording session into per-question clips.

Recording protocol (see generate_prompt_pack.py): the creator pauses ~3s, reads
the question ALOUD VERBATIM from the teleprompter, then answers raw. The spoken
question is the delimiter — one Whisper pass, fuzzy-match each question's text
against the word stream, cut at silence-snapped boundaries. The question stays
in the clip (it's the hook).

Retake rule: if the same question is spoken more than once, the LAST occurrence
wins (protocol: to redo an answer, re-read the question and start over).
Within-answer retakes/fillers are handled downstream by video_trim.py.

Usage:
    python3 scripts/slice_raw_session.py --input assets/raw/inbox/session.mov --week 2026-W29
    python3 scripts/slice_raw_session.py --input clip.mov --week 2026-W29 --dry-run

Outputs (content/sessions/{week}/):
    clips/{qid}.mp4          — one clip per matched question
    session_manifest.json    — match scores, source timecodes, unmatched questions
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
from difflib import SequenceMatcher
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from video_trim import (  # noqa: E402
    FFMPEG_BIN,
    WordStamp,
    detect_silences_adaptive,
    snap_to_silence,
    transcribe_raw,
)
from lib.video_utils import probe_duration  # noqa: E402

SESSIONS_DIR = REPO / "content" / "sessions"

MATCH_THRESHOLD = 0.72   # SequenceMatcher ratio on normalized token strings
SUPPRESS_WINDOW_SEC = 10.0  # collapse overlapping candidate matches
PRE_PAD_SEC = 0.35       # breathing room kept before the spoken question
END_MARGIN_SEC = 0.25    # trim this off before the next question starts


def _tokens(text: str) -> list[str]:
    return [t for t in re.sub(r"[^\w\s']", " ", text.lower()).split() if t]


def find_question_matches(
    words: list[WordStamp], questions: list[dict], threshold: float
) -> list[dict]:
    """Return [{qid, question, score, start, end}] for every spoken-question hit."""
    hits: list[dict] = []
    stream = [w.word for w in words]
    for q in questions:
        qtok = _tokens(q["text"])
        if len(qtok) < 3:
            continue
        target = " ".join(qtok)
        win = len(qtok)
        best_local: list[tuple[float, int, int]] = []  # (score, i, j)
        for i in range(len(words)):
            # allow the window to flex ±2 words around the question length
            for j in (i + win - 1, i + win, i + win + 2):
                if j > len(words):
                    break
                score = SequenceMatcher(None, target, " ".join(stream[i:j])).ratio()
                if score >= threshold:
                    best_local.append((score, i, min(j, len(words)) - 1))
        # non-max suppression: keep the best hit per SUPPRESS_WINDOW_SEC region
        best_local.sort(key=lambda t: -t[0])
        kept: list[tuple[float, int, int]] = []
        for score, i, j in best_local:
            t0 = words[i].start
            if any(abs(words[ki].start - t0) < SUPPRESS_WINDOW_SEC for _, ki, _ in kept):
                continue
            kept.append((score, i, j))
        for score, i, j in kept:
            hits.append({
                "qid": q["id"], "question": q["text"], "score": round(score, 3),
                "start": words[i].start, "q_end": words[j].end,
            })
    hits.sort(key=lambda h: h["start"])
    return hits


def resolve_takes(hits: list[dict]) -> list[dict]:
    """Consecutive hits of the same question = retakes → keep the last one."""
    resolved: list[dict] = []
    for h in hits:
        if resolved and resolved[-1]["qid"] == h["qid"]:
            resolved[-1] = h  # later take supersedes
        else:
            resolved.append(h)
    return resolved


def cut_clip(src: Path, out: Path, start: float, end: float) -> None:
    """Re-encode cut (frame-accurate; stream copy would snap to keyframes)."""
    base = [FFMPEG_BIN, "-y", "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", str(src)]
    for vcodec in (["h264_videotoolbox", "-b:v", "12M"], ["libx264", "-crf", "18"]):
        cmd = base + ["-c:v", *vcodec, "-c:a", "aac", "-b:a", "192k", str(out)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0 and out.exists() and out.stat().st_size > 0:
            return
    raise RuntimeError(f"ffmpeg failed cutting {out.name}: {r.stderr[-400:]}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Slice a raw session into per-question clips.")
    ap.add_argument("--input", required=True, help="raw session recording")
    ap.add_argument("--week", help="ISO week like 2026-W29 (default: from pack path)")
    ap.add_argument("--pack", help="prompt_pack.json (default: content/sessions/{week}/)")
    ap.add_argument("--out-dir", help="clip output dir (default: content/sessions/{week}/clips)")
    ap.add_argument("--min-score", type=float, default=MATCH_THRESHOLD)
    ap.add_argument("--dry-run", action="store_true", help="report matches, cut nothing")
    args = ap.parse_args()

    src = Path(args.input).resolve()
    if not src.exists():
        print(f"Input not found: {src}")
        return 1
    if not args.week and not args.pack:
        print("Need --week or --pack.")
        return 1

    week = args.week or Path(args.pack).parent.name
    pack_path = Path(args.pack) if args.pack else SESSIONS_DIR / week / "prompt_pack.json"
    if not pack_path.exists():
        print(f"Prompt pack not found: {pack_path} — run generate_prompt_pack.py first.")
        return 1
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    out_dir = Path(args.out_dir) if args.out_dir else SESSIONS_DIR / week / "clips"
    work_dir = SESSIONS_DIR / week / "work"

    words = transcribe_raw(src, work_dir)
    if not words:
        print("Transcription produced no words — check the recording.")
        return 1
    silences = detect_silences_adaptive(src)
    duration = probe_duration(src)

    hits = find_question_matches(words, pack["questions"], args.min_score)
    takes = resolve_takes(hits)
    print(f"[slice] {len(hits)} question hits → {len(takes)} takes "
          f"(retakes collapsed) of {len(pack['questions'])} questions")

    clips = []
    for k, take in enumerate(takes):
        clip_start = max(0.0, snap_to_silence(take["start"], silences) - PRE_PAD_SEC)
        next_start = takes[k + 1]["start"] if k + 1 < len(takes) else duration
        clip_end = snap_to_silence(next_start, silences) - (END_MARGIN_SEC if k + 1 < len(takes) else 0.0)
        clip_end = min(max(clip_end, clip_start + 1.0), duration)
        out = out_dir / f"{take['qid']}.mp4"
        entry = {
            **take,
            "src_start": round(clip_start, 3),
            "src_end": round(clip_end, 3),
            "clip": str(out.relative_to(REPO)),
        }
        if not args.dry_run:
            out_dir.mkdir(parents=True, exist_ok=True)
            cut_clip(src, out, clip_start, clip_end)
            print(f"  ✓ {out.name}  [{clip_start:.1f}s → {clip_end:.1f}s]  "
                  f"score {take['score']}  {take['question'][:50]}")
        else:
            print(f"  ~ {take['qid']}  [{clip_start:.1f}s → {clip_end:.1f}s]  "
                  f"score {take['score']}  {take['question'][:50]}")
        clips.append(entry)

    matched_ids = {c["qid"] for c in clips}
    unmatched = [q["id"] for q in pack["questions"] if q["id"] not in matched_ids]
    manifest = {
        "week": week,
        "source": str(src),
        "sliced": datetime.datetime.now().isoformat(timespec="seconds"),
        "duration_sec": round(duration, 1),
        "min_score": args.min_score,
        "clips": clips,
        "unmatched_questions": unmatched,
    }
    if not args.dry_run:
        manifest_path = SESSIONS_DIR / week / "session_manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        # append-friendly: ad-hoc sessions merge into the same week's manifest
        if manifest_path.exists():
            prev = json.loads(manifest_path.read_text(encoding="utf-8"))
            prev_clips = [c for c in prev.get("clips", []) if c["qid"] not in matched_ids]
            manifest["clips"] = prev_clips + clips
            manifest["unmatched_questions"] = [
                q["id"] for q in pack["questions"]
                if q["id"] not in {c["qid"] for c in manifest["clips"]}
            ]
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"✓ {manifest_path}")
    if unmatched:
        print(f"[slice] unmatched: {', '.join(unmatched)} (not spoken, or below --min-score)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
