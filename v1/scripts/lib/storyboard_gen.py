#!/usr/bin/env python3
"""Generate a structured storyboard from a trimmed video transcript.

Called by run_video_pipeline.py as Phase 3.

Input:
    - transcript.json (word-level, remapped to trimmed timeline)
    - DESIGN.md for the niche
    - niche string ("ds" | "life" | "poetry")
    - video duration in seconds
    - optional: script_topic override (from slug or video title)

Output:
    - STORYBOARD.json  (structured, machine-parseable — the canonical form)
    - STORYBOARD.md    (human-readable version derived from JSON)

The storyboard:
    - Identifies 8–20 BEATS from the transcript (semantic / rhetorical units)
    - Every beat has: start_sec, end_sec, transcript_text, type, overlay_block, caption_style
    - Overlay beats are at most 40% of runtime (enforced post-generation)
    - Each beat with an overlay specifies ONLY blocks from the DESIGN.md allowed list
    - Caption track is always present (separate from overlay beats)

Model: claude-opus-4-8 (via `claude -p`)
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent.parent

DESIGN_DIR = REPO / "data" / "kb" / "design"

CLAUDE_MODEL = "claude-opus-4-8"

# Outro sits at the very end and lasts a few seconds — NOT a percentage of
# runtime. A percentage rule makes the outro balloon on long videos (e.g. 90%
# of a 17-min video = a 105s outro card). Keep it a short fixed sign-off.
OUTRO_TARGET_SEC = 8.0
OUTRO_MIN_SEC = 5.0
OUTRO_MAX_SEC = 10.0


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Beat:
    """One storyboard beat."""
    beat_id: int
    beat_type: str           # "talking_head" | "overlay" | "transition" | "outro"
    start_sec: float
    end_sec: float
    duration_sec: float
    transcript_excerpt: str  # ≤30 words from the transcript for this time window

    # Overlay fields (null for talking_head/outro beats)
    overlay_block: Optional[str] = None        # exact catalog block name from DESIGN.md
    overlay_layout: Optional[str] = None       # "fullscreen" | "panel-right" | "panel-top"
    overlay_content: Optional[str] = None      # what to render (stat value, code snippet, etc.)
    overlay_rationale: Optional[str] = None    # why this overlay at this moment

    # Transition fields (only for transition beats)
    transition_block: Optional[str] = None     # exact transition block name from DESIGN.md

    # Caption style (applies to caption track for this section)
    caption_style: Optional[str] = None        # from DESIGN.md allowed caption styles

    # B-roll keywords (for voiceover videos only)
    broll_keywords: Optional[list[str]] = field(default=None)


@dataclass
class Storyboard:
    """Full storyboard for one video."""
    slug: str
    niche: str
    total_duration_sec: float
    caption_style: str          # single style for entire video
    color_grade: dict           # from DESIGN.md

    beats: list[Beat] = field(default_factory=list)

    # Overlay density summary (computed after generation)
    overlay_seconds: float = 0.0
    overlay_pct: float = 0.0
    beat_count: int = 0
    overlay_beat_count: int = 0


# ---------------------------------------------------------------------------
# DESIGN.md loading
# ---------------------------------------------------------------------------

def load_design(niche: str) -> str:
    """Return the niche DESIGN.md + the shared layout catalogue."""
    design_path = DESIGN_DIR / f"{niche}_design.md"
    if not design_path.exists():
        raise FileNotFoundError(f"DESIGN.md not found: {design_path}")
    text = design_path.read_text()

    catalogue_path = DESIGN_DIR / "layout_catalogue.md"
    if catalogue_path.exists():
        text += "\n\n---\n## FULL LAYOUT CATALOGUE (canonical block↔zone reference)\n\n"
        text += catalogue_path.read_text()

    return text


# ---------------------------------------------------------------------------
# Transcript loading
# ---------------------------------------------------------------------------

def load_transcript(transcript_json: Path) -> list[dict]:
    """Load word-level transcript from transcript.json."""
    return json.loads(transcript_json.read_text())


def transcript_excerpt(
    words: list[dict],
    start_sec: float,
    end_sec: float,
    max_words: int = 30,
) -> str:
    """Extract transcript text for a time window."""
    window = [w for w in words if w.get("start", 0) >= start_sec and
              w.get("end", 0) <= end_sec]
    text = " ".join(w.get("text", w.get("word", "")).strip() for w in window[:max_words])
    return text.strip()


def group_into_segments(
    words: list[dict],
    target_segment_count: int = 15,
) -> list[tuple[float, float]]:
    """Divide the transcript into N roughly equal time segments.

    Returns list of (start_sec, end_sec) pairs.
    These are CANDIDATE beat boundaries — Claude merges / splits them.
    """
    if not words:
        return []

    total_duration = words[-1].get("end", 0)
    seg_duration = total_duration / target_segment_count

    segments: list[tuple[float, float]] = []
    cursor = 0.0
    while cursor < total_duration:
        seg_end = min(cursor + seg_duration, total_duration)
        # Snap to nearest word boundary (prefer a pause)
        words_in_window = [w for w in words if cursor <= w.get("start", 0) <= seg_end]
        if words_in_window:
            seg_end = words_in_window[-1].get("end", seg_end)
        segments.append((cursor, seg_end))
        cursor = seg_end

    return segments


# ---------------------------------------------------------------------------
# Storyboard generation via Claude Opus
# ---------------------------------------------------------------------------

def build_storyboard_prompt(
    niche: str,
    design_md: str,
    transcript_words: list[dict],
    total_duration: float,
    slug: str,
    is_reel: bool = False,
) -> str:
    """Build the prompt for Claude to generate the storyboard."""

    # Build readable transcript with timestamps
    tx_lines: list[str] = []
    current_seg_text: list[str] = []
    current_seg_start = transcript_words[0]["start"] if transcript_words else 0.0
    SEGMENT_PAUSE = 0.4  # seconds — group words into readable lines

    for i, w in enumerate(transcript_words):
        current_seg_text.append(w.get("text", w.get("word", "")).strip())
        is_last = (i == len(transcript_words) - 1)
        next_gap = (
            transcript_words[i + 1]["start"] - w["end"]
            if not is_last else SEGMENT_PAUSE + 1
        )
        if next_gap > SEGMENT_PAUSE or is_last:
            line_text = " ".join(current_seg_text)
            tx_lines.append(f"[{current_seg_start:.1f}s] {line_text}")
            if not is_last:
                current_seg_start = transcript_words[i + 1]["start"]
                current_seg_text = []

    transcript_readable = "\n".join(tx_lines)

    fmt_label = "SHORT-FORM REEL (portrait 9:16, ~45s)" if is_reel else "LONG-FORM (landscape)"
    overlay_cap_pct = 70 if is_reel else 40
    overlay_cap_sec = total_duration * overlay_cap_pct / 100

    reel_beat_instruction = ""
    if is_reel:
        reel_beat_instruction = """
## SHORT-FORM REEL — MANDATORY 5-BEAT STRUCTURE

This is a short-form reel. You MUST produce exactly 5 beats in this order:
  Beat 1 (HOOK):         0s – first ~3s   — grab attention immediately
  Beat 2 (PROBLEM):      ~3s – ~8s        — establish the tension / pain point
  Beat 3 (REVEAL+PROOF): ~8s – ~28s       — deliver the value, show the solution
  Beat 4 (PAYOFF):       ~28s – ~35s      — the transformative moment / emotional hit
  Beat 5 (CTA):          ~35s – end       — one call to action

Map the transcript timestamps to these 5 beats as best as possible.
ALL beats must be overlay type — no talking_head beats in a reel.
Use the SHORT-FORM OVERRIDES section of the DESIGN.md above (portrait canvas, allowed blocks only).

"""

    # DS-specific layout assignment rules (injected only for DS niche)
    ds_layout_rule = ""
    if niche == "ds":
        ds_layout_rule = """
## DS MANDATORY LAYOUT ASSIGNMENTS (non-negotiable)

These rules override anything else when there is a conflict:

1. `code-highlight-sweep`, `code-morph`, `number-flow`, `hud-callout`,
   `bento-data-grid`, `liquid-glass-panel`, `neo-brutalism-card`,
   `ar-masking-text`, `kinetic-word-pop` → ALWAYS `panel-right`

2. `lower-third`, `lower-third-minimal` → ALWAYS `lower-third` layout
   `floating-pill-badge` → ALWAYS `pill-top`
   `pill-stat` → ALWAYS `pill-center`
   `macos-notification` → ALWAYS `corner-pip`

3. Opening beat (`code-particle-assemble`, `code-3d-extrude`, `vfx-text-cursor`),
   transitions (`glitch`, `whip-pan`, `cinematic-zoom`), and outro → `fullscreen`

4. SCREEN-RECORDING RULE: When the transcript implies the speaker is demonstrating
   code or terminal output on screen (e.g. "you can see", "here's the code",
   "this command", "run this", "in the terminal", "let me show", "look at this"),
   PREFER `code-highlight-sweep` on `panel-right` over `apple-terminal-clear-dark`
   (fullscreen). `apple-terminal-clear-dark` hides the screen recording behind it.
   Use fullscreen terminal blocks ONLY when the speaker is on-camera only
   (no screen recording visible behind them).

"""

    # Outro is a short sign-off at the very end — last OUTRO_TARGET_SEC seconds,
    # NOT a fraction of runtime (that balloons on long videos).
    outro_start = max(0.0, total_duration - OUTRO_TARGET_SEC)

    return f"""You are a professional video editor creating a storyboard for a {fmt_label}.
Your job: read the transcript, identify semantic beats, and specify HyperFrames overlays for the most impactful moments.

## VIDEO METADATA
- Niche: {niche.upper()}
- Slug: {slug}
- Format: {fmt_label}
- Duration: {total_duration:.1f} seconds
{reel_beat_instruction}{ds_layout_rule}
## DESIGN SPEC (follow exactly — use ONLY blocks listed in ALLOWED CATALOG BLOCKS)
{design_md}

---

## TRANSCRIPT (with timestamps)
{transcript_readable}

---

## YOUR TASK

Produce a storyboard as a JSON object with this exact schema:

```json
{{
  "caption_style": "<string — one value from DESIGN.md allowed caption styles>",
  "beats": [
    {{
      "beat_id": 1,
      "beat_type": "<talking_head|overlay|transition|outro>",
      "start_sec": <number>,
      "end_sec": <number>,
      "transcript_excerpt": "<up to 30 words from transcript in this window>",
      "overlay_block": "<exact block name from DESIGN.md allowed list, or null>",
      "overlay_layout": "<fullscreen|panel-right|panel-left|panel-top|panel-bottom|lower-third|pill-top|pill-center|corner-pip, or null>",
      "overlay_content": "<what to render: stat value, code text, word, etc. or null>",
      "overlay_rationale": "<1 sentence: why this overlay at this exact moment, or null>",
      "transition_block": "<exact transition block from DESIGN.md, or null>",
      "broll_keywords": ["<keyword1>", "<keyword2>"] or null
    }}
  ]
}}
```

## RULES (non-negotiable)

1. **Every beat must have a start_sec and end_sec that is within [0, {total_duration:.1f}].**
   Beats must be contiguous — no gaps, no overlaps.

2. **Overlay beats must NOT exceed {overlay_cap_pct}% of total runtime.**
   Sum of (end_sec - start_sec) for all overlay beats ≤ {overlay_cap_sec:.1f} seconds.

3. **Use ONLY catalog block names from the DESIGN.md "ALLOWED CATALOG BLOCKS" section.**
   Do not invent block names. If you're unsure whether a block exists, use a simpler one from the list.

4. **caption_style applies to the ENTIRE video.** Choose ONE from DESIGN.md. Do not mix styles.

5. **The last beat must be the outro** (beat_type = "outro"). Its overlay_block must be the outro block from DESIGN.md.
   The outro is a SHORT sign-off card covering only the final {OUTRO_TARGET_SEC:.0f} seconds:
   start_sec ≈ {outro_start:.1f}s, end_sec = {total_duration:.1f}s (duration {OUTRO_MIN_SEC:.0f}–{OUTRO_MAX_SEC:.0f}s).
   The outro is NOT a percentage of runtime — never start it earlier than this. The speaker is
   on-camera (base video) up to that point; the outro just caps the very end.

6. **Overlay density — no dead zones.** Never leave more than 60 seconds of consecutive talking_head without at least one overlay beat.
   For long-form videos (> 120s), place at least one overlay every 45–60 seconds throughout the full video — including commentary sections, not just poem/peak moments.
   Good triggers for commentary overlays: a key phrase worth quoting (pull-quote), a section transition (chapter-marker), an introspective observation (thought-bubble), a striking idea worth holding on screen (weight-shift or kinetic-slam).

7. **Variety — no consecutive repeats of the same block type.** Never use the same overlay_block twice in a row.
   Across the full video, no single block type should appear more than 40% of total overlay beats.
   Mix different blocks: weight-shift, kinetic-slam, pull-quote, thought-bubble, chapter-marker, perspective-shift, ethereal-word-reveal, etc.

8. **Every overlay_block must be paired with an overlay_content** describing exactly what to render.
   "Data chart showing X" is acceptable. Leave nothing ambiguous for the beat builder.
   **A stat or number must carry a LABEL of what it measures — never a bare value.**
   The viewer reads the overlay before you explain it aloud, so "0.08s — not 12s" is
   cryptic; "NumPy: 0.08s vs 12s loop" or "50–200× faster" is self-explanatory. This is
   non-negotiable for any opening / cold-open hook overlay (a beat that starts at
   start_sec ≈ 0, before the talking_head): it must stand alone with full context
   (subject + number), because there is no spoken setup yet.

9. **broll_keywords**: include 3–5 search keywords only for talking_head beats in voiceover videos.
   For non-voiceover (talking head with camera), set to null.

10. **Minimum beat duration: 2 seconds.** Do not create beats shorter than 2s.

11. **Maximum 20 beats total.**

12. **No overlapping beats.** Beats must be strictly contiguous: each beat's start_sec
    must equal the previous beat's end_sec (no gaps, no overlaps). Sort by start_sec.

Respond with ONLY the JSON object. No prose before or after."""


def call_claude(prompt: str, model: str = CLAUDE_MODEL) -> str:
    """Call claude -p and return stdout.

    Passes the prompt as a positional argument (same pattern as video_trim.py).
    Shows both stderr and stdout on failure since Claude CLI may write errors
    to either stream.
    """
    import shutil as _shutil
    claude_bin = (
        _shutil.which("claude")
        or "/Users/tarungupta/.local/bin/claude"
    )
    if not claude_bin or not Path(claude_bin).exists():
        raise RuntimeError("claude CLI not found — cannot generate storyboard")

    print(f"[storyboard] claude bin: {claude_bin}  model: {model}  prompt_len: {len(prompt)}")

    # Strip ALL vars that could force API-key auth instead of subscription OAuth.
    # Covers: literal names, ANTHROPIC_AUTH_TOKEN, ANTHROPIC_BASE_URL, and any
    # ANTHROPIC_API_KEY* prefix variant set in the shell or a proxy env.
    _STRIP = {
        "ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY_FREE",
        "ANTHROPIC_AUTH_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN",
        "ANTHROPIC_BASE_URL", "ANTHROPIC_MODEL",
    }
    env = {k: v for k, v in os.environ.items()
           if k not in _STRIP and not k.upper().startswith("ANTHROPIC_API_KEY")}

    result = subprocess.run(
        [claude_bin, "-p", prompt, "--model", model],
        capture_output=True, text=True, timeout=300,
        env=env,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"claude -p failed (exit {result.returncode})  bin={claude_bin}\n"
            f"STDERR: {result.stderr[-800:]}\n"
            f"STDOUT: {result.stdout[-800:]}"
        )

    return result.stdout.strip()


def parse_storyboard_response(
    raw_response: str,
    niche: str,
    slug: str,
    total_duration: float,
    transcript_words: list[dict],
    design_md: str,
) -> Storyboard:
    """Parse Claude's JSON response into a Storyboard object.

    Applies post-generation enforcement:
    - Clips any beat timestamps that exceed video duration
    - Enforces overlay density cap (trims to talking_head if cap exceeded)
    - Validates block names against DESIGN.md allowed list
    """
    # Extract JSON from response (Claude sometimes wraps in ```json)
    match = re.search(r'\{[\s\S]*"beats"\s*:\s*\[[\s\S]*\]\s*\}', raw_response)
    if not match:
        raise ValueError(f"No valid JSON storyboard found in response:\n{raw_response[:500]}")

    data = json.loads(match.group())

    caption_style = data.get("caption_style", "")
    raw_beats = data.get("beats", [])

    # Extract allowed blocks from DESIGN.md (to validate against)
    allowed_blocks = extract_allowed_blocks(design_md)

    beats: list[Beat] = []
    overlay_seconds = 0.0

    for rb in raw_beats:
        start = max(0.0, float(rb.get("start_sec", 0)))
        end = min(total_duration, float(rb.get("end_sec", start + 2)))
        if end <= start:
            end = min(start + 2, total_duration)

        beat_type = rb.get("beat_type", "talking_head")
        overlay_block = rb.get("overlay_block")

        # Validate block name against allowed list
        if overlay_block and overlay_block not in allowed_blocks:
            print(f"[storyboard] WARNING: '{overlay_block}' not in allowed blocks — "
                  f"downgrading to talking_head")
            beat_type = "talking_head"
            overlay_block = None

        # Enforce density cap: if adding this overlay would exceed 40%, downgrade
        if beat_type == "overlay":
            duration = end - start
            if overlay_seconds + duration > total_duration * 0.40:
                print(f"[storyboard] Density cap reached at beat {rb.get('beat_id')} — "
                      f"downgrading to talking_head")
                beat_type = "talking_head"
                overlay_block = None
            else:
                overlay_seconds += duration

        beat = Beat(
            beat_id=int(rb.get("beat_id", len(beats) + 1)),
            beat_type=beat_type,
            start_sec=start,
            end_sec=end,
            duration_sec=end - start,
            transcript_excerpt=rb.get("transcript_excerpt", transcript_excerpt(
                transcript_words, start, end
            )),
            overlay_block=overlay_block,
            overlay_layout=rb.get("overlay_layout") if beat_type == "overlay" else None,
            overlay_content=rb.get("overlay_content") if beat_type == "overlay" else None,
            overlay_rationale=rb.get("overlay_rationale"),
            transition_block=rb.get("transition_block") if beat_type == "transition" else None,
            caption_style=caption_style,
            broll_keywords=rb.get("broll_keywords"),
        )
        beats.append(beat)

    # ── Post-generation enforcement ────────────────────────────────────────
    # 1. Sort beats by start time (Opus sometimes produces out-of-order beats)
    beats.sort(key=lambda b: b.start_sec)

    # 2. Fix overlapping beats: each beat's start must be >= previous beat's end
    for i in range(1, len(beats)):
        prev_end = beats[i - 1].end_sec
        if beats[i].start_sec < prev_end:
            print(f"[storyboard] Overlap fix: beat {beats[i].beat_id} "
                  f"start {beats[i].start_sec:.1f}s → {prev_end:.1f}s")
            beats[i].start_sec = prev_end
            if beats[i].end_sec <= prev_end:
                beats[i].end_sec = min(prev_end + 2.0, total_duration)
            beats[i].duration_sec = beats[i].end_sec - beats[i].start_sec

    # 3. Enforce outro timing: outro is a short sign-off hugging the very end.
    #    Force it to end at total_duration with duration clamped to [MIN, MAX].
    #    (A long outro from Opus — e.g. the old 90%-of-runtime rule producing a
    #    105s card on a 17-min video — gets trimmed back to a few seconds.)
    for i, b in enumerate(beats):
        if b.beat_type != "outro":
            continue
        desired = b.end_sec - b.start_sec
        if not (OUTRO_MIN_SEC <= desired <= OUTRO_MAX_SEC):
            desired = OUTRO_TARGET_SEC
        dur = min(desired, OUTRO_MAX_SEC, total_duration)
        new_start = max(0.0, total_duration - dur)
        if abs(new_start - b.start_sec) > 0.5 or abs(total_duration - b.end_sec) > 0.5:
            print(f"[storyboard] Outro clamp: {b.start_sec:.1f}–{b.end_sec:.1f}s "
                  f"({b.end_sec - b.start_sec:.1f}s) → {new_start:.1f}–{total_duration:.1f}s "
                  f"({dur:.1f}s)")
        beats[i].start_sec = new_start
        beats[i].end_sec = total_duration
        beats[i].duration_sec = total_duration - new_start

    # 3b. If the outro was pulled in, the preceding beat must not extend past it.
    for i in range(1, len(beats)):
        if beats[i].beat_type == "outro" and beats[i - 1].end_sec > beats[i].start_sec:
            beats[i - 1].end_sec = beats[i].start_sec
            beats[i - 1].duration_sec = beats[i - 1].end_sec - beats[i - 1].start_sec

    # Compute color grade from niche (hardcoded to match DESIGN.md)
    color_grade_map = {
        "ds":   {"contrast": 1.12, "saturate": 0.95, "brightness": 1.02, "hueRotate": 8},
        "life": {"contrast": 1.05, "saturate": 1.22, "brightness": 1.03, "hueRotate": -5},
        "poetry": {"contrast": 1.08, "saturate": 0.85, "brightness": 0.96, "hueRotate": 0},
    }

    overlay_beats = [b for b in beats if b.beat_type == "overlay"]
    total_overlay_sec = sum(b.duration_sec for b in overlay_beats)

    return Storyboard(
        slug=slug,
        niche=niche,
        total_duration_sec=total_duration,
        caption_style=caption_style,
        color_grade=color_grade_map.get(niche, {}),
        beats=beats,
        overlay_seconds=total_overlay_sec,
        overlay_pct=total_overlay_sec / total_duration * 100 if total_duration > 0 else 0,
        beat_count=len(beats),
        overlay_beat_count=len(overlay_beats),
    )


def extract_allowed_blocks(design_md: str) -> set[str]:
    """Parse DESIGN.md to extract the closed list of allowed catalog block names."""
    blocks: set[str] = set()
    # Match backtick-quoted names in the ALLOWED CATALOG BLOCKS section
    in_allowed_section = False
    for line in design_md.splitlines():
        if "ALLOWED CATALOG BLOCKS" in line:
            in_allowed_section = True
        elif in_allowed_section and line.startswith("## ") and "ALLOWED" not in line:
            in_allowed_section = False
        if in_allowed_section:
            # Find `block-name` patterns
            for match in re.finditer(r"`([a-z][a-z0-9-]+)`", line):
                blocks.add(match.group(1))
    return blocks


# ---------------------------------------------------------------------------
# Output: JSON + Markdown
# ---------------------------------------------------------------------------

def storyboard_to_markdown(sb: Storyboard) -> str:
    """Render Storyboard as a human-readable Markdown file."""
    lines = [
        f"# STORYBOARD: {sb.slug}",
        f"**Niche:** {sb.niche.upper()}  |  **Duration:** {sb.total_duration_sec:.1f}s  "
        f"|  **Caption style:** `{sb.caption_style}`  "
        f"|  **Overlay:** {sb.overlay_pct:.0f}% of runtime",
        "",
        "---",
        "",
    ]

    for b in sb.beats:
        ts = f"{b.start_sec:.1f}s → {b.end_sec:.1f}s ({b.duration_sec:.1f}s)"
        header = f"## Beat {b.beat_id} · `{b.beat_type}` · {ts}"
        lines.append(header)

        lines.append(f"**Transcript:** *\"{b.transcript_excerpt}\"*")

        if b.overlay_block:
            lines.append(f"**Block:** `{b.overlay_block}` · Layout: `{b.overlay_layout}`")
            lines.append(f"**Content to render:** {b.overlay_content}")
            if b.overlay_rationale:
                lines.append(f"**Rationale:** {b.overlay_rationale}")

        if b.transition_block:
            lines.append(f"**Transition:** `{b.transition_block}`")

        if b.broll_keywords:
            lines.append(f"**B-roll keywords:** {', '.join(b.broll_keywords)}")

        lines.append("")

    lines += [
        "---",
        f"**Total beats:** {sb.beat_count}  |  "
        f"**Overlay beats:** {sb.overlay_beat_count}  |  "
        f"**Overlay runtime:** {sb.overlay_seconds:.1f}s ({sb.overlay_pct:.0f}%)",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_storyboard(
    transcript_json: Path,
    niche: str,
    slug: str,
    out_dir: Path,
    is_voiceover: bool = False,
    is_reel: bool = False,
) -> tuple[Storyboard, Path, Path]:
    """Generate STORYBOARD.json and STORYBOARD.md in out_dir.

    Returns (storyboard, json_path, md_path).
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[storyboard] Loading transcript from {transcript_json}...")
    words = load_transcript(transcript_json)
    if not words:
        raise ValueError("Transcript is empty — cannot generate storyboard")

    total_duration = words[-1].get("end", words[-1].get("endMs", 0) / 1000)

    print(f"[storyboard] Loading {niche} DESIGN.md...")
    design_md = load_design(niche)

    print(f"[storyboard] Calling Claude {CLAUDE_MODEL} for storyboard generation...")
    prompt = build_storyboard_prompt(niche, design_md, words, total_duration, slug, is_reel=is_reel)
    raw_response = call_claude(prompt)

    print(f"[storyboard] Parsing response ({len(raw_response)} chars)...")
    sb = parse_storyboard_response(
        raw_response, niche, slug, total_duration, words, design_md
    )

    print(f"[storyboard] {sb.beat_count} beats, "
          f"{sb.overlay_beat_count} overlays ({sb.overlay_pct:.0f}% of runtime)")

    # Write outputs
    json_path = out_dir / "STORYBOARD.json"
    md_path = out_dir / "STORYBOARD.md"

    json_path.write_text(json.dumps(asdict(sb), indent=2))
    md_path.write_text(storyboard_to_markdown(sb))

    print(f"[storyboard] Written: {json_path}")
    print(f"[storyboard] Written: {md_path}")

    return sb, json_path, md_path


# ---------------------------------------------------------------------------
# CLI (for standalone testing)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Generate storyboard from transcript")
    ap.add_argument("--transcript", required=True, help="transcript.json path")
    ap.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    ap.add_argument("--slug", required=True, help="Content slug")
    ap.add_argument("--out-dir", required=True, help="Output directory for STORYBOARD.*")
    ap.add_argument("--voiceover", action="store_true", help="Add B-roll keyword suggestions")
    args = ap.parse_args()

    sb, json_p, md_p = generate_storyboard(
        transcript_json=Path(args.transcript),
        niche=args.niche,
        slug=args.slug,
        out_dir=Path(args.out_dir),
        is_voiceover=args.voiceover,
    )
    print(f"\nStoryboard ready: {json_p}\n{md_p}")
