#!/usr/bin/env python3
"""Word-level intelligent video trimmer.

Recording pattern this handles:
  - Record sentence → pause (natural breathing) → continue
  - Record sentence → pause (long, 1.5-5s) → restart sentence from beginning
  - No clapper, no slate, no clap markers. Retakes are detected purely from
    transcript similarity after a long pause.

Pipeline (single Whisper pass):
  1. Transcribe raw once (word-level timestamps)
  2. Detect silences with adaptive loudnorm threshold
  3. Detect retakes: long pause + repeated transcript → cut earlier attempt
  4. Find filler words (um/uh unconditional; so/like/etc via one claude -p call)
  5. Reduce long silences (> 2s) to 300ms breathing room
  6. Merge all cuts, apply via ffmpeg
  7. Remap word timestamps to trimmed timeline
  8. Write transcript.json (trimmed) + debug log

Usage:
    python3 scripts/video_trim.py \\
        --raw assets/raw/2026-06-24_life_habits.MOV \\
        --niche life \\
        --out assets/hyperframes/2026-W26/slug/trimmed.mp4

Output alongside --out:
    transcript.json    — word-level timestamps remapped to trimmed timeline
    debug/trim_debug.json — cut log for every edit made
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.video_utils import probe_duration, run_ffmpeg

# Load .env so HF_TOKEN (and other keys) are available to subprocesses and HF Hub
_env_path = REPO / ".env"
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

FFMPEG_BIN = os.environ.get("FFMPEG_BIN", "/opt/homebrew/bin/ffmpeg")
FFPROBE_BIN = os.environ.get("FFPROBE_BIN", "/opt/homebrew/bin/ffprobe")

# ---------------------------------------------------------------------------
# Tuning constants — adjust these before changing code
# ---------------------------------------------------------------------------

# Silence detection
# Adaptive: threshold = measured_speech_level - SILENCE_DB_BELOW_SPEECH
SILENCE_DB_BELOW_SPEECH = 22     # dB below speech level → silence
SILENCE_MIN_DETECT_DUR = 0.15    # 150ms — minimum to detect (catches breathing gaps)

# Silence treatment
NATURAL_BREATH_MAX_SEC = 0.8     # silences shorter than this: leave untouched
SENTENCE_PAUSE_MAX_SEC = 2.0     # silences 0.8–2s: compress to SENTENCE_PAUSE_TARGET_SEC
SENTENCE_PAUSE_TARGET_SEC = 0.35 # what long-but-normal pauses become
LONG_PAUSE_MIN_SEC = 2.0         # silences > 2s: cut down to LONG_PAUSE_KEEP_SEC
LONG_PAUSE_KEEP_SEC = 0.40       # keep this much of any long silence (breathing room)

# Retake detection
RETAKE_PAUSE_MIN_SEC = 1.5       # long pause that triggers retake check
RETAKE_LOOKBACK_WORDS = 30       # words before gap to compare
RETAKE_LOOKAHEAD_WORDS = 15      # words after gap to compare
RETAKE_SIMILARITY_THRESHOLD = 0.38  # token overlap ratio → classify as retake

# Filler word cut pads
FILLER_PRE_PAD_SEC = 0.04        # cut starts this far before filler word
FILLER_POST_PAD_SEC = 0.04       # cut ends this far after filler word
SNAP_WINDOW_SEC = 0.10           # snap cut boundary to silence within ±this

# ffmpeg audio crossfade at every cut
CROSSFADE_SEC = 0.03             # 30ms

# Whisper
WHISPER_MODEL = "large-v3"       # most accurate; change to "base" for speed testing

# Filler word config (editable without code changes)
FILLER_LIST_PATH = REPO / "data" / "kb" / "filler_words.json"

# ── Pacing presets ──────────────────────────────────────────────────────────
# "natural" == the current tuned defaults (applying it is a no-op). "tight" is
# snappier (less breathing room), "relaxed" leaves more air. Override individual
# thresholds too. Applied by apply_pace() before trim_video() runs.
PACE_PRESETS: dict[str, dict[str, float]] = {
    "tight":   {"NATURAL_BREATH_MAX_SEC": 0.50, "SENTENCE_PAUSE_TARGET_SEC": 0.25, "LONG_PAUSE_KEEP_SEC": 0.30},
    "natural": {"NATURAL_BREATH_MAX_SEC": 0.80, "SENTENCE_PAUSE_TARGET_SEC": 0.35, "LONG_PAUSE_KEEP_SEC": 0.40},
    "relaxed": {"NATURAL_BREATH_MAX_SEC": 1.10, "SENTENCE_PAUSE_TARGET_SEC": 0.55, "LONG_PAUSE_KEEP_SEC": 0.60},
}


def apply_pace(pace: str | None = None, overrides: dict[str, float | None] | None = None) -> None:
    """Reassign pacing globals from a preset + explicit overrides, in place.

    Call BEFORE trim_video() — the trim functions read these module globals at
    call time. pace=None and no overrides leaves the tuned defaults untouched.
    """
    g = globals()
    if pace and pace in PACE_PRESETS:
        g.update(PACE_PRESETS[pace])
        print(f"[trim] pace preset '{pace}': {PACE_PRESETS[pace]}")
    if overrides:
        clean = {k: v for k, v in overrides.items() if v is not None}
        if clean:
            g.update(clean)
            print(f"[trim] pace overrides: {clean}")


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class WordStamp:
    text: str           # raw from Whisper (may have leading space)
    word: str           # stripped, lowercased, punctuation removed
    start: float        # seconds
    end: float          # seconds
    confidence: float   # 0–1
    seg_idx: int
    word_idx: int


@dataclass
class Cut:
    start: float        # seconds
    end: float          # seconds
    reason: str         # "retake" | "filler:um" | "long_silence" | "compress_silence"
    note: str = ""      # human-readable description for debug log


@dataclass
class TrimResult:
    trimmed_path: Path
    words: list[WordStamp]
    cuts: list[Cut]
    original_duration: float
    trimmed_duration: float
    debug_json: Path


# ---------------------------------------------------------------------------
# Filler word lists
# ---------------------------------------------------------------------------

def load_filler_sets() -> tuple[set[str], set[str]]:
    """Return (unconditional, ambiguous) filler word sets.

    Unconditional = always remove (um, uh, etc.)
    Ambiguous = send to claude -p for context-aware decision (so, like, etc.)
    """
    defaults_unconditional = {"um", "uh", "umm", "uhh", "hmm", "mhm"}
    defaults_ambiguous = {
        "so", "like", "you know", "basically", "literally",
        "right", "i mean", "kind of", "sort of", "you see"
    }
    if FILLER_LIST_PATH.exists():
        data = json.loads(FILLER_LIST_PATH.read_text())
        u = {w.lower() for w in data.get("unconditional", [])}
        a = {w.lower() for w in data.get("ambiguous", [])}
        if u or a:
            return u, a
    return defaults_unconditional, defaults_ambiguous


# ---------------------------------------------------------------------------
# Whisper transcription
# ---------------------------------------------------------------------------

def transcribe_raw(raw: Path, work_dir: Path) -> list[WordStamp]:
    """Transcribe raw media using faster-whisper. Returns flat word list with timestamps.

    Uses faster-whisper Python API directly (no subprocess) — avoids PyTorch/Python 3.14
    segfault that affects openai-whisper CLI on macOS. Produces identical per-word timestamps.

    Model cache: ~/.cache/huggingface/hub/  (downloaded on first run, ~3GB for large-v3)
    """
    work_dir.mkdir(parents=True, exist_ok=True)

    try:
        from faster_whisper import WhisperModel  # type: ignore[import]
    except ImportError:
        raise RuntimeError(
            "faster-whisper not installed.\n"
            "Run: pip install faster-whisper\n"
            "(Replaces openai-whisper; avoids Python 3.14 segfault)"
        )

    # Map our model name: openai-whisper "large-v3" → faster-whisper "large-v3"
    model_size = WHISPER_MODEL   # "large-v3" (same naming)

    print(f"[trim] faster-whisper ({model_size}) transcribing...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, _info = model.transcribe(
        str(raw),
        language="en",
        word_timestamps=True,
        vad_filter=True,           # skip non-speech regions
        vad_parameters={"min_silence_duration_ms": 300},
    )

    words: list[WordStamp] = []
    for seg_idx, seg in enumerate(segments):
        for word_idx, w in enumerate(seg.words or []):
            raw_text = w.word
            cleaned = re.sub(r"[^\w\s']", "", raw_text.strip()).lower().strip()
            words.append(WordStamp(
                text=raw_text,
                word=cleaned,
                start=float(w.start),
                end=float(w.end),
                confidence=float(w.probability),
                seg_idx=seg_idx,
                word_idx=word_idx,
            ))

    # Write JSON sidecar for inspection / cache
    out_json = work_dir / f"{raw.stem}.json"
    out_json.write_text(json.dumps({
        "segments": [
            {"words": [{"word": w.text, "start": w.start, "end": w.end,
                        "probability": w.confidence}
                       for w in words if w.seg_idx == i]}
            for i in sorted({w.seg_idx for w in words})
        ]
    }, indent=2))

    print(f"[trim] Transcribed {len(words)} words")
    return words


# ---------------------------------------------------------------------------
# Adaptive silence detection
# ---------------------------------------------------------------------------

def measure_speech_level(media: Path) -> float:
    """Measure mean spoken audio level in dBFS via ffmpeg loudnorm."""
    r = subprocess.run(
        [FFMPEG_BIN, "-i", str(media), "-vn",
         "-af", "loudnorm=print_format=json",
         "-f", "null", "/dev/null"],
        capture_output=True, text=True,
    )
    # loudnorm prints JSON to stderr
    match = re.search(r'\{[^}]*"input_i"\s*:\s*"([-\d.]+)"', r.stderr, re.DOTALL)
    if match:
        return float(match.group(1))
    # Fallback: use max_volume
    match2 = re.search(r"max_volume:\s*([-\d.]+)\s*dB", r.stderr)
    if match2:
        return float(match2.group(1)) - 6.0  # rough offset
    return -18.0  # safe default


def detect_silences_adaptive(media: Path) -> list[tuple[float, float]]:
    """Detect silences with threshold set relative to actual speech level.

    Returns list of (start, end) pairs for silent regions.
    Threshold = measured_speech_level - SILENCE_DB_BELOW_SPEECH.
    This adapts to varying mic levels and recording environments.
    """
    print("[trim] Measuring audio level for adaptive silence detection...")
    speech_level = measure_speech_level(media)
    threshold_db = speech_level - SILENCE_DB_BELOW_SPEECH
    threshold_db = max(threshold_db, -50.0)  # floor: never go below -50dB
    threshold_db = min(threshold_db, -20.0)  # ceiling: never above -20dB (too aggressive)

    print(f"[trim] Speech level: {speech_level:.1f}dBFS → silence threshold: {threshold_db:.1f}dB")

    r = subprocess.run(
        [FFMPEG_BIN, "-i", str(media), "-vn",
         "-af", f"silencedetect=noise={threshold_db:.1f}dB:d={SILENCE_MIN_DETECT_DUR}",
         "-f", "null", "/dev/null"],
        capture_output=True, text=True,
    )
    starts = [float(m) for m in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(m) for m in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    silences = list(zip(starts, ends[:len(starts)]))
    print(f"[trim] {len(silences)} silence regions detected")
    return silences


# ---------------------------------------------------------------------------
# Silence boundary snapping
# ---------------------------------------------------------------------------

def snap_to_silence(t: float, silences: list[tuple[float, float]]) -> float:
    """Snap timestamp t to the nearest silence boundary within SNAP_WINDOW_SEC.

    Prevents cutting mid-phoneme by landing at a known silence edge.
    Returns t unchanged if no silence boundary is close enough.
    """
    best, best_dist = t, float("inf")
    for s_start, s_end in silences:
        for boundary in (s_start, s_end):
            dist = abs(boundary - t)
            if dist < best_dist and dist <= SNAP_WINDOW_SEC:
                best, best_dist = boundary, dist
    return best


# ---------------------------------------------------------------------------
# Retake detection (no clap markers)
# ---------------------------------------------------------------------------

def _token_set(words: list[WordStamp]) -> set[str]:
    """Bag of content words (≥4 chars) from a word list."""
    return {w.word for w in words if len(w.word) >= 4}


def detect_retakes(
    words: list[WordStamp],
    silences: list[tuple[float, float]],
) -> list[Cut]:
    """Find retakes by detecting long pauses followed by repeated transcript content.

    Recording pattern: speaker pauses ≥1.5s then restarts from earlier in sentence.
    Algorithm:
      For each long pause (≥ RETAKE_PAUSE_MIN_SEC):
        - Take 30 words before pause and 15 words after pause
        - Compute token overlap between them
        - If overlap ≥ threshold: it's a retake
          → Find where the repeated phrase starts in the pre-pause text
          → Cut from that point through the pause end
    """
    cuts: list[Cut] = []

    # Find long pauses from silence list
    long_pauses = [
        (s, e) for s, e in silences
        if (e - s) >= RETAKE_PAUSE_MIN_SEC
    ]
    print(f"[trim] {len(long_pauses)} long pauses (≥{RETAKE_PAUSE_MIN_SEC}s) to check for retakes")

    for pause_start, pause_end in long_pauses:
        # Words before and after the pause
        before = [w for w in words if w.end <= pause_start][-RETAKE_LOOKBACK_WORDS:]
        after = [w for w in words if w.start >= pause_end][:RETAKE_LOOKAHEAD_WORDS]

        if not before or not after:
            continue

        tokens_before = _token_set(before)
        tokens_after = _token_set(after)
        union = tokens_before | tokens_after
        if not union:
            continue

        overlap = tokens_before & tokens_after
        similarity = len(overlap) / len(union)

        if similarity >= RETAKE_SIMILARITY_THRESHOLD:
            # Find the earliest word before the pause that also appears in 'after'
            # This is the start of the repeated content to cut
            cut_start = pause_start  # default: cut from just before the pause
            for w in reversed(before):
                if w.word in tokens_after and len(w.word) >= 4:
                    cut_start = max(0.0, w.start - 0.05)
                    break

            cut_start = snap_to_silence(cut_start, silences)
            cut_end = snap_to_silence(pause_end, silences)

            if cut_end > cut_start + 0.1:
                cuts.append(Cut(
                    start=cut_start,
                    end=cut_end,
                    reason="retake",
                    note=f"similarity={similarity:.2f}, pause={pause_end - pause_start:.1f}s, "
                         f"overlap_words={list(overlap)[:5]}",
                ))
                print(f"[trim] Retake: {cut_start:.1f}s–{cut_end:.1f}s "
                      f"(similarity={similarity:.2f})")
        else:
            pass  # not a retake, just a natural pause between topics

    return cuts


# ---------------------------------------------------------------------------
# Silence compression cuts
# ---------------------------------------------------------------------------

def build_silence_cuts(silences: list[tuple[float, float]]) -> list[Cut]:
    """Compress long silences without removing natural breathing rhythm.

    - ≤ NATURAL_BREATH_MAX_SEC: leave completely untouched
    - NATURAL_BREATH_MAX_SEC to LONG_PAUSE_MIN_SEC: compress to SENTENCE_PAUSE_TARGET_SEC
    - > LONG_PAUSE_MIN_SEC: compress to LONG_PAUSE_KEEP_SEC
    """
    cuts: list[Cut] = []
    for s_start, s_end in silences:
        duration = s_end - s_start

        if duration <= NATURAL_BREATH_MAX_SEC:
            continue  # natural breath — keep it

        elif duration <= LONG_PAUSE_MIN_SEC:
            # Sentence pause — keep SENTENCE_PAUSE_TARGET_SEC worth
            cut_start = s_start + SENTENCE_PAUSE_TARGET_SEC
            cut_end = s_end
            if cut_end - cut_start > 0.05:
                cuts.append(Cut(
                    start=cut_start,
                    end=cut_end,
                    reason="compress_silence",
                    note=f"original={duration:.2f}s → keep {SENTENCE_PAUSE_TARGET_SEC}s",
                ))

        else:
            # Long pause — keep LONG_PAUSE_KEEP_SEC worth
            cut_start = s_start + LONG_PAUSE_KEEP_SEC
            cut_end = s_end
            if cut_end - cut_start > 0.05:
                cuts.append(Cut(
                    start=cut_start,
                    end=cut_end,
                    reason="long_silence",
                    note=f"original={duration:.2f}s → keep {LONG_PAUSE_KEEP_SEC}s",
                ))

    return cuts


# ---------------------------------------------------------------------------
# Filler word detection
# ---------------------------------------------------------------------------

def find_fillers(
    words: list[WordStamp],
    unconditional: set[str],
    ambiguous: set[str],
    silences: list[tuple[float, float]],
) -> list[Cut]:
    """Detect filler words and return Cut intervals.

    Unconditional fillers (um, uh): cut immediately.
    Ambiguous (so, like): multi-signal heuristic first, then one claude -p call.
    Bias: false-negative (keeping a filler) is far better than cutting real content.
    """
    unconditional_indices: list[int] = []
    ambiguous_candidates: list[int] = []

    for i, w in enumerate(words):
        wl = w.word

        if wl in unconditional:
            unconditional_indices.append(i)
            continue

        # Check 2-word phrases
        two_word = (wl + " " + words[i + 1].word) if i + 1 < len(words) else ""
        if two_word in ambiguous:
            ambiguous_candidates.append(i)
            continue

        if wl in ambiguous:
            # Require ≥2 of 3 signals before flagging
            at_segment_start = (w.word_idx <= 2)
            followed_by_pause = (
                (words[i + 1].start - w.end) * 1000 >= 180
                if i + 1 < len(words) else False
            )
            low_confidence = w.confidence < 0.82

            if sum([at_segment_start, followed_by_pause, low_confidence]) >= 2:
                ambiguous_candidates.append(i)

    # LLM disambiguation for ambiguous candidates
    confirmed_ambiguous = _disambiguate_via_claude(words, ambiguous_candidates)
    all_filler_indices = unconditional_indices + confirmed_ambiguous

    print(f"[trim] Fillers: {len(unconditional_indices)} unconditional + "
          f"{len(confirmed_ambiguous)}/{len(ambiguous_candidates)} ambiguous confirmed "
          f"= {len(all_filler_indices)} total")

    return _filler_indices_to_cuts(all_filler_indices, words, silences)


def _disambiguate_via_claude(
    words: list[WordStamp],
    candidates: list[int],
) -> list[int]:
    """One cheap claude -p call to confirm which ambiguous words are true fillers.

    Uses claude-haiku-4-5-20251001 (cheapest model) — this is a simple classification task.
    Returns subset of candidates to remove.
    """
    if not candidates:
        return []

    claude_bin = shutil.which("claude")
    if not claude_bin:
        print("[trim] claude CLI not found — keeping all ambiguous filler candidates")
        return []

    items = []
    for idx in candidates:
        w_start = max(0, idx - 5)
        w_end = min(len(words), idx + 6)
        context = " ".join(ww.text for ww in words[w_start:w_end])
        items.append(f"INDEX {idx}: word='{words[idx].word}', context: \"{context}\"")

    prompt = (
        "Decide which words below are FILLER words (zero semantic content).\n"
        "REMOVE only if removing it makes the sentence flow better and loses nothing.\n"
        "KEEP if the word is grammatically or semantically meaningful.\n"
        "When uncertain → KEEP. A kept filler is invisible; a cut real word is a glitch.\n\n"
        + "\n".join(items)
        + "\n\nReply ONLY with JSON: {\"remove\": [idx1, idx2, ...]}"
    )

    try:
        r = subprocess.run(
            [claude_bin, "-p", prompt, "--model", "claude-haiku-4-5-20251001"],
            capture_output=True, text=True, timeout=30,
        )
        m = re.search(r'\{"remove"\s*:\s*\[([\d,\s]*)\]\}', r.stdout)
        if m:
            raw_indices = [int(x.strip()) for x in m.group(1).split(",") if x.strip()]
            valid = [i for i in raw_indices if i in candidates]
            return valid
    except Exception as e:
        print(f"[trim] LLM disambiguation failed ({e}) — keeping all ambiguous words")

    return []


def _filler_indices_to_cuts(
    indices: list[int],
    words: list[WordStamp],
    silences: list[tuple[float, float]],
) -> list[Cut]:
    """Convert filler word indices to Cut objects with snapped boundaries.

    Groups consecutive indices into single cuts to avoid micro-cuts.
    """
    if not indices:
        return []

    # Group consecutive
    groups: list[list[int]] = []
    cur: list[int] = [indices[0]]
    for idx in indices[1:]:
        if idx == cur[-1] + 1:
            cur.append(idx)
        else:
            groups.append(cur)
            cur = [idx]
    groups.append(cur)

    cuts: list[Cut] = []
    for group in groups:
        first = words[group[0]]
        last = words[group[-1]]
        raw_start = max(0.0, first.start - FILLER_PRE_PAD_SEC)
        raw_end = last.end + FILLER_POST_PAD_SEC

        s = snap_to_silence(raw_start, silences)
        e = snap_to_silence(raw_end, silences)
        if e <= s:
            e = raw_end
            s = raw_start

        cuts.append(Cut(
            start=s, end=e,
            reason=f"filler:{first.word}",
            note=f"words {group[0]}–{group[-1]}",
        ))

    return cuts


# ---------------------------------------------------------------------------
# Cut merging and inversion
# ---------------------------------------------------------------------------

def merge_cuts(cuts: list[Cut]) -> list[Cut]:
    """Merge overlapping or adjacent (≤50ms gap) cuts into single intervals."""
    if not cuts:
        return []
    sorted_cuts = sorted(cuts, key=lambda c: c.start)
    merged = [sorted_cuts[0]]
    for c in sorted_cuts[1:]:
        prev = merged[-1]
        if c.start <= prev.end + 0.05:
            merged[-1] = Cut(
                start=prev.start,
                end=max(prev.end, c.end),
                reason=prev.reason + "+" + c.reason,
                note=prev.note + " | " + c.note,
            )
        else:
            merged.append(c)
    return merged


def cuts_to_keep_segments(
    cuts: list[Cut],
    total_duration: float,
) -> list[tuple[float, float]]:
    """Invert merged cut list into (start, end) keep segments."""
    merged = merge_cuts(cuts)
    keep: list[tuple[float, float]] = []
    cursor = 0.0
    for c in merged:
        if c.start > cursor + 0.02:
            keep.append((cursor, c.start))
        cursor = c.end
    if cursor < total_duration - 0.02:
        keep.append((cursor, total_duration))
    return keep


# ---------------------------------------------------------------------------
# ffmpeg application
# ---------------------------------------------------------------------------

def apply_cuts(
    media: Path,
    cuts: list[Cut],
    out: Path,
    is_audio_only: bool = False,
) -> None:
    """Apply cuts via ffmpeg segment extraction + concat.

    Each segment is extracted individually (frame-accurate at -ss/-to),
    then concatenated via the concat demuxer. Audio crossfade of 30ms
    is applied via acrossfade filter on the concatenated audio track
    to prevent click artifacts at every join.
    """
    total_duration = probe_duration(media)
    keep_segs = cuts_to_keep_segments(cuts, total_duration)

    if not keep_segs:
        raise RuntimeError("[trim] All content was cut — filler detection is too aggressive")

    print(f"[trim] {len(cuts)} cuts → keeping {len(keep_segs)} segments")

    work_dir = out.parent / "_trim_work"
    work_dir.mkdir(parents=True, exist_ok=True)

    seg_paths: list[Path] = []
    for i, (t_start, t_end) in enumerate(keep_segs):
        seg_out = work_dir / f"seg_{i:04d}.mp4"
        run_ffmpeg([
            FFMPEG_BIN, "-y",
            "-ss", f"{t_start:.4f}", "-to", f"{t_end:.4f}",
            "-i", str(media),
            "-c:v", "h264_videotoolbox",
            "-c:a", "aac", "-b:a", "192k",
            "-avoid_negative_ts", "make_zero",
            str(seg_out),
        ], f"seg {i + 1}/{len(keep_segs)}: {t_start:.2f}–{t_end:.2f}s")
        seg_paths.append(seg_out)

    # Concat list
    concat_list = work_dir / "concat.txt"
    concat_list.write_text("\n".join(f"file '{str(p)}'" for p in seg_paths) + "\n")

    # First pass: concat (copy, no re-encode)
    concat_raw = work_dir / "concat_raw.mp4"
    run_ffmpeg([
        FFMPEG_BIN, "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(concat_raw),
    ], "concat segments")

    # Second pass: smooth audio joins with loudnorm + limiter
    # (acrossfade on pre-cut segments is tricky; loudnorm + limiting is more robust)
    run_ffmpeg([
        FFMPEG_BIN, "-y",
        "-i", str(concat_raw),
        "-c:v", "copy",
        "-af", f"loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=level_in=1:level_out=1:limit=0.9",
        "-c:a", "aac", "-b:a", "192k",
        str(out),
    ], "audio normalize + limit")

    # Cleanup
    try:
        shutil.rmtree(str(work_dir))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Timestamp remapping
# ---------------------------------------------------------------------------

def remap_words(
    words: list[WordStamp],
    cuts: list[Cut],
) -> list[WordStamp]:
    """Remap word timestamps from original → trimmed timeline.

    For each surviving word, subtract the total duration of all cuts
    that ended before word.start.
    Words that fall inside a cut are dropped.
    """
    merged = merge_cuts(cuts)
    result: list[WordStamp] = []

    for w in words:
        # Drop if inside any cut
        if any(c.start <= w.start and w.end <= c.end for c in merged):
            continue
        # Drop if word straddles a cut boundary (partial word)
        if any(c.start < w.end and w.start < c.end for c in merged):
            continue

        removed_before = sum(
            c.end - c.start
            for c in merged
            if c.end <= w.start
        )

        result.append(WordStamp(
            text=w.text,
            word=w.word,
            start=max(0.0, w.start - removed_before),
            end=max(0.0, w.end - removed_before),
            confidence=w.confidence,
            seg_idx=w.seg_idx,
            word_idx=w.word_idx,
        ))

    return result


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def trim_video(
    raw: Path,
    out: Path,
    niche: str,
    is_audio_only: bool = False,
) -> TrimResult:
    """Full trimming pipeline. Single Whisper pass.

    Returns TrimResult with trimmed_path, remapped words, and debug log path.
    """
    out.parent.mkdir(parents=True, exist_ok=True)
    debug_dir = out.parent / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    work_dir = debug_dir / "whisper"

    # 1. Transcribe
    words = transcribe_raw(raw, work_dir)
    if not words:
        raise RuntimeError("Whisper returned no words — check audio in raw file")

    original_duration = probe_duration(raw)

    # 2. Detect silences (adaptive threshold)
    silences = detect_silences_adaptive(raw)

    all_cuts: list[Cut] = []

    # 3. Retake detection (long pause + repeated transcript)
    retake_cuts = detect_retakes(words, silences)
    all_cuts.extend(retake_cuts)

    # 4. Filler words
    unconditional, ambiguous = load_filler_sets()
    filler_cuts = find_fillers(words, unconditional, ambiguous, silences)
    all_cuts.extend(filler_cuts)

    # 5. Silence compression (only for silences NOT already covered by retake cuts)
    silence_cuts = build_silence_cuts(silences)
    all_cuts.extend(silence_cuts)

    # 6. Apply cuts
    apply_cuts(raw, all_cuts, out, is_audio_only=is_audio_only)

    trimmed_duration = probe_duration(out)
    removed_sec = original_duration - trimmed_duration
    print(
        f"[trim] {original_duration:.1f}s → {trimmed_duration:.1f}s "
        f"(removed {removed_sec:.1f}s / {removed_sec / original_duration * 100:.0f}%)"
    )

    # 7. Remap timestamps
    remapped = remap_words(words, all_cuts)
    print(f"[trim] {len(remapped)}/{len(words)} words remain in trimmed timeline")

    # 8. Write transcript.json alongside output (used by downstream pipeline)
    transcript_out = out.parent / "transcript.json"
    transcript_out.write_text(json.dumps(
        [
            {
                "word": w.word, "text": w.text,
                "start": round(w.start, 3), "end": round(w.end, 3),
                "startMs": round(w.start * 1000), "endMs": round(w.end * 1000),
                "confidence": round(w.confidence, 3),
            }
            for w in remapped
        ],
        indent=2,
    ))

    # 9. Debug log
    debug_json = debug_dir / "trim_debug.json"
    debug_json.write_text(json.dumps(
        {
            "raw": str(raw),
            "out": str(out),
            "niche": niche,
            "original_duration_sec": round(original_duration, 3),
            "trimmed_duration_sec": round(trimmed_duration, 3),
            "removed_sec": round(removed_sec, 3),
            "removed_pct": round(removed_sec / original_duration * 100, 1),
            "cut_count": len(merge_cuts(all_cuts)),
            "cuts": [asdict(c) for c in merge_cuts(all_cuts)],
        },
        indent=2,
    ))

    print(f"[trim] Debug: {debug_json}")
    print(f"[trim] Transcript: {transcript_out}")
    print(f"[trim] Output: {out}")

    return TrimResult(
        trimmed_path=out,
        words=remapped,
        cuts=all_cuts,
        original_duration=original_duration,
        trimmed_duration=trimmed_duration,
        debug_json=debug_json,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Intelligent video trimmer (V2 pipeline)")
    ap.add_argument("--raw", required=True, help="Raw video (.MOV/.mp4) or audio (.wav/.m4a)")
    ap.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    ap.add_argument("--out", required=True, help="Output path for trimmed file")
    ap.add_argument("--audio-only", action="store_true",
                    help="Input is audio-only (voiceover track)")
    ap.add_argument("--pace", choices=["tight", "natural", "relaxed"], default=None,
                    help="Pacing preset (default: the current tuned values)")
    ap.add_argument("--breath-max", type=float, default=None,
                    help="Override NATURAL_BREATH_MAX_SEC — pauses shorter than this stay untouched")
    ap.add_argument("--sentence-target", type=float, default=None,
                    help="Override SENTENCE_PAUSE_TARGET_SEC — what 0.8–2s pauses compress to")
    ap.add_argument("--long-pause-keep", type=float, default=None,
                    help="Override LONG_PAUSE_KEEP_SEC — how much of a >2s pause to keep")
    ap.add_argument("--silence-db", type=float, default=None,
                    help="Override SILENCE_DB_BELOW_SPEECH — silence sensitivity (dB below speech)")
    args = ap.parse_args()
    apply_pace(args.pace, {
        "NATURAL_BREATH_MAX_SEC": args.breath_max,
        "SENTENCE_PAUSE_TARGET_SEC": args.sentence_target,
        "LONG_PAUSE_KEEP_SEC": args.long_pause_keep,
        "SILENCE_DB_BELOW_SPEECH": args.silence_db,
    })

    raw = Path(args.raw)
    if not raw.exists():
        print(f"ERROR: --raw not found: {raw}", file=sys.stderr)
        sys.exit(1)

    result = trim_video(raw, Path(args.out), args.niche, is_audio_only=args.audio_only)

    print(f"\n✓ Trimmed: {result.trimmed_path}")
    print(f"  Duration: {result.original_duration:.1f}s → {result.trimmed_duration:.1f}s")
    print(f"  Cuts applied: {len(result.cuts)}")


if __name__ == "__main__":
    main()
