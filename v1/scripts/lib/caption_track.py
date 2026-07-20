#!/usr/bin/env python3
"""Continuous, word-synced caption track (burned across the ENTIRE timeline).

Why this exists
---------------
The per-beat caption pill (`hf_templates.build_caption_layer`) only rendered on
overlay beats — `build_all_beats` skips `talking_head` beats entirely, so plain
talking-head stretches (the bulk of a reel) had NO captions at all. The reel
formula requires "captions burned in (85% watch muted)". This module builds one
continuous caption track from the word-level `transcript.json` and burns it over
the final composite, so every segment is captioned.

Style: "karaoke active-word pop" — up to three short lines, primary white, the
currently-spoken word enlarged and tinted with the niche accent. Suppressed only
inside beats whose block IS the text (NO_CAPTION_BLOCKS) to avoid double subtitles.

Layout safety
-------------
Lines are packed by *estimated pixel width* (not word count) so text never spills
past the mobile-safe zone. The packer reserves room for the enlarged active word,
auto-shrinks a group's font if a single word is too wide, and the ASS `WrapStyle: 0`
smart-wrap is a final backstop.

Usage (from hyperframes_pipeline.run_hf_pipeline, after build_ffmpeg_composite):
    from lib.caption_track import build_caption_ass, burn_caption_track
    ass = build_caption_ass(transcript_words, storyboard, niche, resolution, work_dir / "captions.ass")
    burn_caption_track(final_output, ass, captioned, ffmpeg_bin)
"""

from __future__ import annotations

import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

# Reuse the single source of truth for "this block already shows the text".
try:
    from lib.hf_beat_builder import NO_CAPTION_BLOCKS
except Exception:  # pragma: no cover - fallback if import path differs
    NO_CAPTION_BLOCKS = frozenset()


# ── ffmpeg capability resolution ───────────────────────────────────────────
# Burning an ASS track needs an ffmpeg built with libass. The pipeline's
# default binary (/opt/homebrew/bin/ffmpeg) is a stripped build WITHOUT libass,
# so the `ass` filter is absent and the burn fails. Resolve at runtime to a
# binary that actually has the filter, and pick an H.264 encoder that binary
# ships (the libass-capable conda ffmpeg has h264_videotoolbox, not libx264).

@lru_cache(maxsize=None)
def _ffmpeg_listing(ffmpeg_bin: str, what: str) -> str:
    """Return `ffmpeg -{what}` stdout ('' if the binary is missing/errors)."""
    try:
        r = subprocess.run(
            [ffmpeg_bin, "-hide_banner", f"-{what}"],
            capture_output=True, text=True,
        )
        return r.stdout or ""
    except (OSError, subprocess.SubprocessError):
        return ""


def _ffmpeg_has(ffmpeg_bin: str, what: str, name: str) -> bool:
    """True if `name` is listed in the `-filters`/`-encoders` output.

    Listing rows are `<flags> <name> <io> <desc>`; match the name column
    exactly so a substring in a description (e.g. "ASS" inside a blurb)
    never counts.
    """
    for line in _ffmpeg_listing(ffmpeg_bin, what).splitlines():
        toks = line.split()
        if len(toks) >= 2 and toks[1] == name:
            return True
    return False


def resolve_ass_ffmpeg(preferred: str = "ffmpeg") -> str:
    """First ffmpeg with the libass `ass` filter.

    Order: the caller's binary → the ffmpeg sibling of the running python
    (the conda env is libass-capable) → whatever `ffmpeg` is on PATH.
    """
    candidates = [
        preferred,
        str(Path(sys.executable).parent / "ffmpeg"),
        "ffmpeg",
    ]
    tried: list[str] = []
    for c in candidates:
        if c in tried:
            continue
        tried.append(c)
        if _ffmpeg_has(c, "filters", "ass"):
            return c
    raise RuntimeError(
        "No ffmpeg with the libass 'ass' filter found (tried: "
        + ", ".join(tried)
        + "). Install an ffmpeg built with --enable-libass "
        "(the content_engine_env conda ffmpeg has it)."
    )

# ── Style constants (ASS colours are &HAABBGGRR) ────────────────────────────
PRIMARY = "&H00FFF4F0"          # #f0f4ff — design-spec caption white
OUTLINE = "&H00000000"          # black
BORDER = 6                      # outline px for base words
BORDER_ACTIVE = 8               # outline px for the active word
# Active-word highlight. Gold reads with the highest contrast on video, so it's used
# across all niches for a consistent caption identity. To differentiate per niche,
# give life/poetry their own hex (e.g. amber &H000B9EF5 / violet &H00FEB4D8).
NICHE_ACCENT = {
    "ds":     "&H0000D4FF",     # #FFD400 gold
    "life":   "&H000B9EF5",
    "poetry": "&H0000D4FF",     # #FFD400 gold
}

# Grouping heuristics
MAX_WORDS_PER_GROUP = 4         # words shown together (packed into <= MAX_LINES rows)
GAP_BREAK_SEC = 0.6            # a silence longer than this starts a new caption group
SENTENCE_END = (".", "!", "?", "…")

# Layout / width model (approximate, portable — no font metrics needed)
SAFE_FRACTION = 0.86            # captions live within this fraction of the frame width
AVG_CHAR_W = 0.62              # advance width of a bold UPPERCASE glyph as a fraction of fontsize
SPACE_FRAC = 0.30             # inter-word space as a fraction of fontsize
ACTIVE_SCALE = 1.15            # the active word is enlarged by this factor
MIN_FONTSIZE = 40             # never shrink a group's font below this


def _fmt_time(sec: float) -> str:
    sec = max(0.0, sec)
    cs = int(round(sec * 100))
    h, rem = divmod(cs, 360000)
    m, rem = divmod(rem, 6000)
    s, c = divmod(rem, 100)
    return f"{h}:{m:02d}:{s:02d}.{c:02d}"


def _dims(resolution: str) -> tuple[int, int, int, int, int]:
    """Return (play_w, play_h, base_fontsize, margin_v, max_lines)."""
    if resolution == "portrait":       # reels / shorts
        return 1080, 1920, 76, 470, 3
    if resolution == "square":
        return 1080, 1080, 64, 150, 2
    return 1920, 1080, 60, 150, 2      # landscape / long-form (lower third)


def _accent(niche: str) -> str:
    return NICHE_ACCENT.get(niche, NICHE_ACCENT["ds"])


def _resolve_block_type(raw_beat: dict[str, Any]) -> str:
    """Mirror hf_beat_builder.build_all_beats block-type resolution."""
    bt = raw_beat.get("beat_type", "overlay")
    if bt == "transition":
        return raw_beat.get("transition_block") or "clip-wipe"
    if bt == "outro":
        return "logo-outro"
    return raw_beat.get("overlay_block") or "editorial-emphasis"


def _suppression_windows(storyboard: dict) -> list[tuple[float, float]]:
    """Windows where a beat already displays the transcript text itself."""
    windows: list[tuple[float, float]] = []
    for rb in storyboard.get("beats", []):
        if rb.get("beat_type") == "talking_head":
            continue
        if _resolve_block_type(rb) in NO_CAPTION_BLOCKS:
            windows.append((float(rb["start_sec"]), float(rb["end_sec"])))
    return windows


def _in_windows(t: float, windows: list[tuple[float, float]]) -> bool:
    return any(a <= t < b for a, b in windows)


def _group_words(words: list[dict], suppress: list[tuple[float, float]]) -> list[list[dict]]:
    """Chunk words into caption groups by max-length, sentence end, and pauses.

    Words whose midpoint falls inside a suppression window are dropped.
    """
    groups: list[list[dict]] = []
    cur: list[dict] = []
    prev_end: float | None = None
    for w in words:
        try:
            start = float(w["start"]); end = float(w["end"])
        except (KeyError, TypeError, ValueError):
            continue
        text = str(w.get("word", "")).strip()
        if not text:
            continue
        if _in_windows((start + end) / 2.0, suppress):
            if cur:
                groups.append(cur); cur = []
            prev_end = end
            continue
        big_gap = prev_end is not None and (start - prev_end) > GAP_BREAK_SEC
        if cur and (len(cur) >= MAX_WORDS_PER_GROUP or big_gap):
            groups.append(cur); cur = []
        cur.append({"word": text, "start": start, "end": end})
        if text.endswith(SENTENCE_END) and len(cur) >= 2:
            groups.append(cur); cur = []
        prev_end = end
    if cur:
        groups.append(cur)
    return groups


# ── Width-aware line packing ────────────────────────────────────────────────

def _word_w(word: str, fontsize: float) -> float:
    return len(word) * AVG_CHAR_W * fontsize


def _line_w(words: list[str], fontsize: float) -> float:
    if not words:
        return 0.0
    return sum(_word_w(w, fontsize) for w in words) + SPACE_FRAC * fontsize * (len(words) - 1)


def _pack(words: list[str], fontsize: float, usable: float) -> list[list[str]]:
    """Greedy left-to-right packing into lines that each fit `usable` px."""
    lines: list[list[str]] = []
    cur: list[str] = []
    for w in words:
        if cur and _line_w(cur + [w], fontsize) > usable:
            lines.append(cur); cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(cur)
    return lines


def _fit_group(words: list[str], base_fs: int, usable: float, max_lines: int) -> tuple[list[list[str]], int, int]:
    """Pack words into <= max_lines rows, shrinking the font if needed.

    Packs using the ENLARGED (active) size so that whichever word is currently
    highlighted, the line still fits. Returns (lines, base_fs, active_fs).
    """
    fs = float(base_fs)
    for _ in range(14):
        active = fs * ACTIVE_SCALE
        widest = max((_word_w(w, active) for w in words), default=0.0)
        lines = _pack(words, active, usable)
        if len(lines) <= max_lines and widest <= usable:
            return lines, int(round(fs)), int(round(active))
        if fs <= MIN_FONTSIZE:
            break
        fs = max(MIN_FONTSIZE, fs * 0.92)
    active = fs * ACTIVE_SCALE
    return _pack(words, active, usable), int(round(fs)), int(round(active))


def build_caption_ass(
    transcript_words: list[dict],
    storyboard: dict,
    niche: str,
    resolution: str,
    out_path: Path,
) -> Path:
    """Write a karaoke active-word caption track to `out_path` (ASS). Returns it."""
    play_w, play_h, base_fs, margin_v, max_lines = _dims(resolution)
    margin_h = int(round((1.0 - SAFE_FRACTION) / 2.0 * play_w))
    usable = play_w - 2 * margin_h
    accent = _accent(niche)
    suppress = _suppression_windows(storyboard)
    groups = _group_words(transcript_words, suppress)

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {play_w}
PlayResY: {play_h}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter,{base_fs},{PRIMARY},{PRIMARY},{OUTLINE},{OUTLINE},-1,0,0,0,100,100,1,0,1,{BORDER},3,2,{margin_h},{margin_h},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events: list[str] = []
    for group in groups:
        gwords = [g["word"].upper() for g in group]
        lines, fs, fs_active = _fit_group(gwords, base_fs, usable, max_lines)
        # Fixed word→line map for the whole group (only the active word restyles).
        order = [w for line in lines for w in line]
        # Guard: if packing reordered nothing (it never should), fall back to sequence.
        g_end = group[-1]["end"]
        base_prefix = "{\\fs" + str(fs) + "}"
        active_open = "{\\fs" + str(fs_active) + "\\1c" + accent + "\\bord" + str(BORDER_ACTIVE) + "}"
        active_close = "{\\fs" + str(fs) + "\\1c" + PRIMARY + "\\bord" + str(BORDER) + "}"
        for j, active in enumerate(group):
            ev_start = active["start"]
            ev_end = group[j + 1]["start"] if j + 1 < len(group) else g_end
            if ev_end <= ev_start:
                ev_end = ev_start + 0.08
            gi = 0
            disp_lines: list[str] = []
            for line in lines:
                parts: list[str] = []
                for _w in line:
                    W = order[gi]
                    parts.append(active_open + W + active_close if gi == j else W)
                    gi += 1
                disp_lines.append(" ".join(parts))
            text = base_prefix + "\\N".join(disp_lines)
            events.append(
                f"Dialogue: 0,{_fmt_time(ev_start)},{_fmt_time(ev_end)},Cap,,0,0,0,,{{\\fad(30,0)}}{text}"
            )

    out_path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")
    return out_path


def burn_caption_track(
    video_in: Path,
    ass_path: Path,
    video_out: Path,
    ffmpeg_bin: str = "ffmpeg",
) -> Path:
    """Burn the ASS caption track onto `video_in` → `video_out` (audio copied)."""
    # The passed binary may lack libass; resolve to one that has the `ass` filter.
    ff = resolve_ass_ffmpeg(ffmpeg_bin)
    # Escape the ASS path for the ffmpeg filtergraph (colons/backslashes/quotes).
    escaped = str(ass_path).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    # Encoder must exist on the SAME binary. Prefer libx264 (crf-stable); the
    # libass-capable conda ffmpeg has no libx264, so fall back to VideoToolbox
    # (which rejects -crf/-preset — use a fixed bitrate instead).
    if _ffmpeg_has(ff, "encoders", "libx264"):
        venc = ["-c:v", "libx264", "-preset", "medium", "-crf", "18"]
    elif _ffmpeg_has(ff, "encoders", "h264_videotoolbox"):
        venc = ["-c:v", "h264_videotoolbox", "-b:v", "10M"]
    else:
        raise RuntimeError(
            f"{ff} has no usable H.264 encoder (libx264 or h264_videotoolbox)."
        )
    cmd = [
        ff, "-nostdin", "-v", "error", "-y",
        "-i", str(video_in),
        "-vf", f"ass='{escaped}'",
        *venc,
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        str(video_out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not video_out.exists():
        raise RuntimeError(f"caption burn failed:\n{r.stderr[-800:]}")
    return video_out
