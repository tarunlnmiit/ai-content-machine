#!/usr/bin/env python3
"""HyperFrames beat project builder.

For each storyboard beat, generates a HyperFrames composition project directory
(an index.html that HyperFrames can render). Claude Haiku writes the GSAP/HTML for each
beat based on block_type + DESIGN.md constants + caption text.

Output structure per beat:
    {work_dir}/hf_beats/beat_{idx:02d}_{block_type}/
        index.html

Variable injection at render time (passed via `hyperframes render --variables`):
    - caption_text: the spoken words for this beat window
    - (block-specific): code_lines, chart_data, etc.

Usage (from hyperframes_pipeline.py — do not call directly):
    from lib.hf_beat_builder import build_beat_project
    project_dir = build_beat_project(beat, design_md, transcript_words, work_dir, niche, resolution)
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lib.niche_config import model_for
from lib.hf_templates import (
    PANEL_LAYOUTS,
    build_caption_layer,
    build_shell,
    panel_rect,
    sanitize_fragment,
    sanitize_timeline_js,
)

REPO = Path(__file__).resolve().parent.parent.parent
KB = REPO / "data" / "kb"

CLAUDE_BIN = shutil.which("claude") or "/Users/tarungupta/.local/bin/claude"
MODEL_BEAT = model_for("beat_html")   # best quality for design-rich HTML compositions

# Cache dir: reuse identical beats (same block_type + duration + caption hash)
BEAT_CACHE_DIR = REPO / ".hf_beat_cache"

# HyperFrames render resolution aliases
RESOLUTION_MAP = {
    # HyperFrames reads the HTML body dimensions and renders at that size.
    # --resolution is unusable (webm/mov reject it; mp4 requires libx264 unavailable on Apple Silicon).
    # Author at 1920×1080 / 1080×1920 and HyperFrames renders at those dimensions natively.
    "landscape": (1920, 1080),
    "portrait":  (1080, 1920),
    "square":    (1080, 1080),
}

# Which blocks render WITH alpha (need --format mov) vs full-frame (--format webm).
# Alpha blocks are composited OVER the base video; webm blocks REPLACE the frame entirely.
ALPHA_BLOCKS = {
    # ── captions / text overlays ──────────────────────────────────────────
    "matrix-decode", "editorial-emphasis", "weight-shift", "clip-wipe",
    "gradient-fill",            # DS default caption style
    "kinetic-slam", "morph-text", "vfx-text-cursor",
    "kinetic-word-pop",         # NEW: energetic word-by-word pop (all niches)
    "ethereal-word-reveal",     # NEW: gentle float-up reveal (Poetry/Life)
    "particle-burst",           # Life: keyword particle explosion
    "blend-difference",         # Poetry: invert-blend text effect
    "texture-marble",           # Poetry: marble texture mask text
    "emoji-pop",                # Life: oversized emoji burst on beats
    # ── data / code overlays ──────────────────────────────────────────────
    "code-highlight-sweep", "number-flow",
    "code-morph",               # DS: snippet-to-snippet morph comparison
    "code-shader-dissolve",     # DS: GPU dissolve reveal
    "hud-callout",              # NEW: HUD data panel (DS, panel-right)
    "bento-data-grid",          # NEW: 4-cell bento stat grid (DS, panel-right)
    # ── side panel overlays ───────────────────────────────────────────────
    "pull-quote",               # Life: large pull-quote (panel-left)
    "handwritten-annotation",   # NEW: marker-style callout (Life, panel-left)
    "spotify-card",             # Life: mood card (panel-right)
    "liquid-glass-panel",       # NEW: iOS 26 frosted glass panel (all niches)
    "ar-masking-text",          # NEW: text woven into footage (all niches)
    "neo-brutalism-card",       # NEW: thick border offset shadow card (all niches)
    # ── atmospheric / always-on ───────────────────────────────────────────
    "grain-overlay", "vignette", "light-leak", "liquid-background",
    "parallax-layers",          # Life: multi-depth background parallax
    "aurora-gradient",          # NEW: flowing aurora orbs (Life/Poetry)
    "analog-film-overlay",      # NEW: grain + vignette + colour shift combo
    "shimmer-sweep",            # DS: accent sweep on key phrase
    # ── transitions ───────────────────────────────────────────────────────
    "flash-through-white", "domain-warp-dissolve", "sdf-iris",
    "glitch", "whip-pan", "cinematic-zoom",
    # ── lower third / strip ───────────────────────────────────────────────
    "yt-lower-third", "macos-notification", "instagram-follow",
    "lower-third",              # official HF catalog block (all niches)
    "lower-third-minimal",      # NEW: clean line + text, no bar (all niches)
    # ── floating / pill / corner ──────────────────────────────────────────
    "floating-pill-badge",      # NEW: annotation pill at top (Life/DS, pill-top)
    "pill-stat",                # NEW: key metric centered pill (DS, pill-center)
}

# Full-frame blocks — replace the video frame entirely (webm, no alpha needed).
# The talking head is NOT visible underneath these — they are standalone visual segments.
FULLFRAME_BLOCKS = {
    "code-particle-assemble", "code-typing", "apple-terminal-clear-dark",
    "apple-terminal-homebrew",  # DS: Homebrew terminal variant
    "code-3d-extrude", "data-chart", "flowchart", "logo-outro",
    "aurora-title",             # NEW: aurora colourfield opening (Life/Poetry, fullscreen)
}

# Blocks that SUPPRESS the Python caption pill because they ARE the text display,
# are pure transitions, or replace the frame entirely.
# Adding the pill on top of these creates double subtitles or text-on-text clutter.
NO_CAPTION_BLOCKS: frozenset[str] = frozenset({
    # ── Caption / text style blocks — render the transcript text themselves ───
    "editorial-emphasis",   # key word 2× size — IS the caption track
    "weight-shift",         # font-weight transition — IS the caption
    "gradient-fill",        # gradient-clipped text — IS the caption track
    "matrix-decode",        # ASCII scramble reveal — IS the caption track
    "kinetic-slam",         # single word fills screen — IS the caption moment
    "kinetic-word-pop",     # word-by-word spring pop — IS the caption
    "ethereal-word-reveal", # gentle float-up — IS the caption
    "particle-burst",       # particle explosion text — IS the caption
    "clip-wipe",            # left-to-right text wipe — IS the caption
    "blend-difference",     # invert-blend text — IS the caption
    "texture-marble",       # marble texture text — IS the caption
    "morph-text",           # morphing title text
    "vfx-text-cursor",      # cursor-glow text
    "aurora-title",         # large title over aurora orbs
    # ── Pure transitions — no transcript text needed during a cut ────────────
    "glitch", "whip-pan", "cinematic-zoom",
    "flash-through-white", "domain-warp-dissolve", "sdf-iris", "light-leak",
    # ── Outro / opening assembly — have their own text systems ───────────────
    "logo-outro",
    "code-particle-assemble",
    "code-3d-extrude",
    # ── Fullscreen code / terminal — their own text; pill creates clutter ────
    "code-typing",
    "apple-terminal-clear-dark",
    "apple-terminal-homebrew",
    "code-shader-dissolve",
})


@dataclass
class BeatSpec:
    idx: int
    block_type: str
    start: float           # seconds in trimmed video timeline
    end: float             # seconds
    caption: str           # spoken words in this window
    caption_style: str     # from storyboard.caption_style
    data: dict[str, Any]   # block-specific payload (code_lines, chart_data, etc.)
    layout: str = "fullscreen"   # "fullscreen" | "panel-right" | "panel-top" | "panel-left"
    broll_keywords: list[str] | None = None


def _duration_frames(start: float, end: float, fps: int = 30) -> int:
    """Convert beat time range to frame count."""
    return max(1, round((end - start) * fps))


_CACHE_VERSION = "v10"  # bumped: global caption track — per-beat pill suppressed when global captions on

def _cache_key(beat: BeatSpec, niche: str, resolution: str, global_captions: bool = False) -> str:
    payload = f"{_CACHE_VERSION}:{niche}:{resolution}:{global_captions}:{beat.block_type}:{beat.caption}:{json.dumps(beat.data, sort_keys=True)}"
    return hashlib.md5(payload.encode()).hexdigest()[:16]


def _call_claude(prompt: str) -> str:
    # Strip ALL vars that could force API-key auth over subscription OAuth.
    _STRIP = {
        "ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY_FREE",
        "ANTHROPIC_AUTH_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN",
        "ANTHROPIC_BASE_URL", "ANTHROPIC_MODEL",
    }
    env = {k: v for k, v in os.environ.items()
           if k not in _STRIP and not k.upper().startswith("ANTHROPIC_API_KEY")}
    r = subprocess.run(
        [CLAUDE_BIN, "-p", prompt, "--model", MODEL_BEAT],
        capture_output=True, text=True, timeout=300,
        env=env,
    )
    if r.returncode != 0:
        raise RuntimeError(
            f"claude -p failed (exit {r.returncode}):\n"
            f"STDERR: {r.stderr[-400:]}\nSTDOUT: {r.stdout[-400:]}"
        )
    return r.stdout.strip()


def _extract_html(raw: str) -> str:
    """Pull raw HTML from Claude's response, stripping markdown fences if present."""
    if "```html" in raw:
        start = raw.index("```html") + 7
        end = raw.index("```", start) if "```" in raw[start:] else len(raw)
        return raw[start:end].strip()
    if "```" in raw:
        start = raw.index("```") + 3
        end = raw.index("```", start) if "```" in raw[start:] else len(raw)
        return raw[start:end].strip()
    return raw.strip()


def _extract_two_blocks(raw: str) -> tuple[str, str]:
    """Parse Claude's 2-block response into (inner_html, timeline_js).

    Expects exactly two fenced code blocks:
        ```html
        ... inner HTML fragment ...
        ```
        ```js
        ... GSAP timeline body ...
        ```
    """
    blocks = re.findall(r"```(?:html|js|javascript)?\s*\n(.*?)```", raw, re.DOTALL)
    if len(blocks) < 2:
        raise RuntimeError(
            f"Expected 2 fenced blocks (html + js), got {len(blocks)}.\n"
            f"Response preview:\n{raw[:500]}"
        )
    return blocks[0].strip(), blocks[1].strip()


def _load_design_constants(niche: str) -> str:
    """Load the compact design constants for the prompt (palette + motion + caption spec only)."""
    design_path = KB / "design" / f"{niche}_design.md"
    if not design_path.exists():
        return f"niche: {niche} — no design file found"
    text = design_path.read_text(encoding="utf-8")
    # Extract the 4 key sections (compact for prompt)
    sections = ["## PALETTE", "## TYPOGRAPHY", "## MOTION LANGUAGE", "## CAPTION SPEC"]
    short_form_override = "## SHORT-FORM OVERRIDES"
    parts: list[str] = []
    lines = text.splitlines()
    in_section = False
    for line in lines:
        if any(line.startswith(s) for s in sections + [short_form_override]):
            in_section = True
        elif line.startswith("## ") and in_section:
            in_section = False
        if in_section:
            parts.append(line)
    # Cap generously so PALETTE + TYPOGRAPHY + MOTION + CAPTION + SHORT-FORM all survive
    # (the prompt references the palette by name, so it must actually be present).
    return "\n".join(parts)[:6000]


def _validate_composition_html(html: str, duration_frames: int, beat_idx: int) -> list[str]:
    """Return list of validation errors in generated HTML. Empty list = OK.

    Called after meta auto-injection so only catches issues that couldn't be auto-fixed.
    """
    errors: list[str] = []
    if html.startswith("```"):
        errors.append("Claude returned markdown fences instead of raw HTML")
    if "<!DOCTYPE html>" not in html and "<!doctype html>" not in html.lower():
        errors.append("missing <!DOCTYPE html>")
    if "data-composition-fps" not in html:
        errors.append("missing data-composition-fps meta attribute")
    if "data-composition-duration" not in html:
        errors.append("missing data-composition-duration meta attribute")
    if "gsap" not in html.lower():
        errors.append("missing GSAP import — animation will not run")
    m = re.search(r'data-composition-duration=["\'](\d+)["\']', html)
    if m:
        actual_frames = int(m.group(1))
        tolerance = max(10, round(0.2 * duration_frames))
        if abs(actual_frames - duration_frames) > tolerance:
            errors.append(
                f"duration mismatch: expected ~{duration_frames}f, got {actual_frames}f"
            )
    return errors


def _compose_prompt(
    beat: BeatSpec,
    niche: str,
    resolution: str,
    is_reel: bool,
) -> str:
    """Build the prompt for Claude to generate INNER CONTENT only (2 fenced blocks).

    Python owns the full HTML shell, panel positioning, and caption layer via hf_templates.py.
    Claude's job is ONLY:
      1. An inner HTML fragment (no <html>/<head>/<body>, no panel/main div)
      2. A GSAP timeline body (adds tweens to `tl` which is already in scope)
    """
    width, height = RESOLUTION_MAP.get(resolution, (1920, 1080))
    duration_sec = beat.end - beat.start
    design_constants = _load_design_constants(niche)

    # Give Claude the BOX dimensions only (not the full canvas)
    # so it cannot accidentally anchor to canvas coordinates.
    x1, y1, x2, y2 = panel_rect(beat.layout, width, height)
    box_w = x2 - x1
    box_h = y2 - y1
    is_panel = beat.layout in PANEL_LAYOUTS  # True for all non-fullscreen zones

    block_context = ""
    if beat.data:
        block_context = f"\nCONTENT DATA:\n{json.dumps(beat.data, indent=2)}"

    panel_note = (
        "Your content overlays a live speaker video. The speaker is visible outside your box."
        if is_panel else
        "This is a fullscreen segment — fill the box with a rich layered background."
    )

    # For life/poetry fullscreen overlays meant to co-exist with a talking head,
    # use frosted/liquid-glass styling so the subject stays visible underneath.
    # weight-shift and logo-outro intentionally keep a dark/opaque background.
    glass_note = ""
    if (
        niche in ("life", "poetry")
        and beat.layout == "fullscreen"
        and beat.block_type not in ("weight-shift", "logo-outro")
    ):
        glass_note = (
            f"\nBACKGROUND RULE for {niche} fullscreen overlay: Do NOT use a solid dark or opaque background.\n"
            "Use a semi-transparent dark background: background rgba(10,8,5,0.55) on your root container — "
            "NO backdrop-filter, NO -webkit-backdrop-filter (these cause severe render timeouts in headless Chrome).\n"
            "The talking head remains visible through the alpha channel — FFmpeg composites the video underneath. "
            "All text must still be legible — use text-shadow or strong font-weight to compensate for the reduced contrast.\n"
        )

    reel_note = ""
    if is_reel:
        reel_note = (
            "\nVERTICAL REEL (1080×1920): keep everything inside the central safe zone — nothing in the\n"
            "top 14% or bottom 20% (platform UI covers it). Go BIG and phone-legible: hero text ≥ 90px,\n"
            "heavy weight, high contrast; ONE idea on screen at a time; faster motion (entrances ≤ 0.4s).\n"
        )

    return f"""You are generating visual content for a premium motion-graphics video beat.

NICHE: {niche.upper()}
BLOCK TYPE: {beat.block_type}
YOUR BOX: {box_w}×{box_h}px  ← this is your entire world. (0,0) = top-left of your box.
DURATION: {duration_sec:.1f}s
{panel_note}
{glass_note}{reel_note}
DESIGN CONSTANTS — follow exactly:
{design_constants}
{block_context}

═══ YOUR OUTPUT (TWO CODE BLOCKS, IN ORDER) ═══

BLOCK 1 — Inner HTML fragment. Rules:
• No <html>, <head>, <body>, no data-composition-* attributes, no <script> tags.
• Your content fills a {box_w}×{box_h}px container. Use position:absolute with px values 0..{box_w} / 0..{box_h}.
{"• The glass panel background is already drawn for you — do NOT add backdrop-filter to your top-level div." if is_panel else "• If a BACKGROUND RULE above tells you to use frosted glass, apply that backdrop-filter on your root container; otherwise do not add backdrop-filter."}
• NEVER: position:fixed, inset:0, width:100vw, height:100vh, white-space:nowrap.
• Text: max-width:{box_w - 60}px, word-wrap:break-word, overflow-wrap:break-word always.
• Max 24 DOM elements total.
• ⛔ STRICTLY FORBIDDEN — ZERO TOLERANCE:
  - Do NOT add corner info panels, tooltip boxes, annotation labels, or any secondary text element.
  - Do NOT add subtitle text, caption text, or any element that shows the spoken transcript.
  - Do NOT repeat the caption in a small secondary element (corner, bottom, side).
  - ONE visual composition only. One design statement. No supporting annotation boxes.

BLOCK 2 — GSAP timeline body. Rules:
• `tl` (the timeline) and `root` (your container element) are already in scope — use them.
• Scope selectors: root.querySelector('.card'), NOT document.querySelector('.card').
• Add tweens to `tl` only. Do NOT create a new gsap.timeline(). Do NOT register window.__timelines.
• ONLY animate: x, y, scale, opacity, rotation, filter, clip-path, color, backgroundColor.
• NEVER animate: left, top, width, height, margin, padding, font-size.
• Use gsap.set() for initial states. Animation must finish within {duration_sec:.1f}s.
• Easing: cubic-bezier(0.34,1.56,0.64,1) for entries, cubic-bezier(0.4,0,1,1) for exits.
• READABILITY (hard rule — overlapping text is the #1 defect). When you render two or
  more text lines:
  — Stack them at distinct y with a real gap: each line's box is ~1.2×font-size tall,
    so the next line's `top` must be ≥ previous line's `top` + 1.3×(previous font-size px).
    A 160px line followed by a line 130px lower OVERLAPS — push it down.
  — Never leave a previous line dimmed-but-visible (opacity 0.2–0.5) underneath or over
    another line. Either keep BOTH lines fully visible on their own non-overlapping rows
    (preferred for complementary phrases like "axis 0 ↓ rows" / "axis 1 → columns"),
    OR if one line truly REPLACES another, animate the outgoing line to opacity 0.
  — Two DIFFERENT strings must never share the same top/left and crossfade — that reads
    as garbled half-rendered text.

VISUAL QUALITY — pick the style that fits best:
{"Panel: the glass surface is already drawn. Design the content that lives INSIDE it." if is_panel else "Fullscreen: use 3+ layered radial gradients as background, never flat single color."}
• Primary text > 48px: gradient fill using 2–3 ACCENT colours FROM THE DESIGN CONSTANTS PALETTE ABOVE (linear-gradient(135deg, <accent1>, <accent2>, <accent3>)) + -webkit-background-clip:text; -webkit-text-fill-color:transparent — OR a glow filter. NEVER hardcode a colour that is not in the palette.
• Entrance: scale 0.92→1, opacity 0→1, y 20→0, duration 0.5s, elastic ease.
• Use ≥3 colours from the palette. Glow: text-shadow 0 0 30px <a palette accent colour at ~0.6 alpha> on hero text.
• Neo-brutalist terminal style for code blocks: hard border, JetBrains Mono, scanlines.
• Aurora / kinetic typography for conceptual reveals: gradient text, weight animation, depth.

BLOCK TYPE SPEC — {beat.block_type}:
• weight-shift: Render EXACTLY the text from CONTENT DATA (overlay_content), nothing else.
  MAX 2 lines × 8 words each. Font 60–80px, Cormorant Garamond for poetry/life or Inter for ds.
  Lines reveal ONE AT A TIME — line 1 fades in at t=0.1s, line 2 fades in at t=1.8s (line 1 dims).
  Dark full-canvas background (NOT transparent). No corner panels. No secondary text. One phrase, one reveal.
• code-highlight-sweep: code snippet visible, glowing scan bar sweeps left→right across it
• code-typing: monospace text appears char-by-char with blinking cursor
• number-flow: large KPI number fills the box, counts from 0 to target, accent-colored
• logo-outro: channel handle + subscribe pill + glowing accent, fullscreen only
• editorial-emphasis: stacked text, one key word at 2× size, gradient-colored
• kinetic-slam: one word slams to center, scale 3→1 with motion blur settle
• matrix-decode: ASCII scramble resolves into the caption text
• glitch: RGB split + scanline flash, then stabilizes
• liquid-glass-panel: iOS 26-style frosted glass; content inside; subtle border highlight + inner glow
• hud-callout: HUD data panel — scan-line texture, corner brackets, monospace readout
• bento-data-grid: 2×2 grid of metric tiles, each with label + large number + accent colour per cell
• neo-brutalism-card: 3px solid border, 6px offset box-shadow in accent colour, no border-radius
• lower-third: dark pill/bar slides up from bottom with name + title; accent rule above text
• lower-third-minimal: thin accent line + text slides up; NO background bar (transparent —
  the glass panel is already drawn); clean and airy. Render overlay_content as ONE strip
  exactly as authored. If it contains two halves (split on "·" / "/"), put each half on its
  OWN row, both fully visible for the whole beat — never overlap them at the same position.
• floating-pill-badge: small rounded pill with icon + short annotation text; fade-in scale entrance
• pill-stat: centered pill showing one large number + small unit/label below; glow edge
• kinetic-word-pop: each word pops in scale 0.6→1.1→1 with fast stagger; accent colour on key word
• ethereal-word-reveal: words fade from y+20 at opacity 0→1; gentle glow; blur-to-clear
• aurora-title: large title over animated aurora orbs (slow radial-gradient animation); fullscreen
• aurora-gradient: 3–4 large colour orbs animating slowly; fullscreen atmospheric layer
• analog-film-overlay: grain noise texture + heavy vignette + slight colour desaturation; layered
• handwritten-annotation: slightly-rotated hand-drawn font; underline squiggle; warm ink colour
• ar-masking-text: text clipped to a gradient mask that reveals it progressively; woven into frame
• (all others): create an appropriate visual matching the name)

Return EXACTLY two fenced code blocks and nothing else:
```html
<!-- your inner fragment here -->
```
```js
// your GSAP timeline body here
```"""


def build_beat_project(
    beat: BeatSpec,
    niche: str,
    work_dir: Path,
    resolution: str = "landscape",
    is_reel: bool = False,
    use_cache: bool = True,
    global_captions: bool = False,
) -> Path:
    """Generate a HyperFrames project directory for this beat.

    Returns the project directory (contains index.html).

    global_captions: when True, the continuous caption track (caption_track.py)
    owns all transcript captions, so the per-beat caption pill is suppressed here
    to avoid double subtitles.
    """
    cache_key = _cache_key(beat, niche, resolution, global_captions)
    cached = BEAT_CACHE_DIR / cache_key

    if use_cache and cached.exists() and (cached / "index.html").exists():
        project_dir = work_dir / "hf_beats" / f"beat_{beat.idx:02d}_{beat.block_type}"
        project_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(cached / "index.html", project_dir / "index.html")
        return project_dir

    # ── Generate inner content via Claude (2 fenced blocks) ─────────────────
    prompt = _compose_prompt(beat, niche, resolution, is_reel)
    raw = _call_claude(prompt)
    inner_html, inner_js = _extract_two_blocks(raw)

    is_panel = beat.layout in PANEL_LAYOUTS  # True for all non-fullscreen zones
    is_alpha = needs_alpha(beat.block_type, beat.layout)
    width, height = RESOLUTION_MAP.get(resolution, (1920, 1080))
    fps = 30
    duration_frames = _duration_frames(beat.start, beat.end, fps)
    duration_sec = round(beat.end - beat.start, 3)

    # Sanitize Claude's fragments
    inner_html = sanitize_fragment(inner_html, is_panel)
    inner_js = sanitize_timeline_js(inner_js)

    # Python-owned caption — suppressed for blocks that ARE the caption display,
    # pure transitions, or fullscreen code/terminal renders.
    # Adding the pill on top of self-captioning blocks creates double subtitles.
    if global_captions or beat.block_type in NO_CAPTION_BLOCKS:
        # Continuous caption track owns captions (or this block IS the text) → no pill.
        caption_html, caption_js = "", ""
    else:
        caption_html, caption_js = build_caption_layer(beat.caption)

    # HyperFrames variables JSON
    variables_json = json.dumps({
        "caption_text": {"type": "string", "default": beat.caption},
        "niche_color":  {"type": "string", "default": "#3b82f6"},
    })

    # Assemble complete index.html — Python owns all geometry
    html = build_shell(
        layout=beat.layout,
        width=width,
        height=height,
        fps=fps,
        duration_frames=duration_frames,
        duration_sec=duration_sec,
        is_alpha=is_alpha,
        inner_html=inner_html,
        inner_timeline_js=inner_js,
        caption_html=caption_html,
        caption_timeline_js=caption_js,
        variables_json=variables_json,
    )

    # Write project dir
    project_dir = work_dir / "hf_beats" / f"beat_{beat.idx:02d}_{beat.block_type}"
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "index.html").write_text(html, encoding="utf-8")

    # Cache for reuse
    if use_cache:
        cache_dir = BEAT_CACHE_DIR / cache_key
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / "index.html").write_text(html, encoding="utf-8")

    return project_dir


def needs_alpha(block_type: str, layout: str = "fullscreen") -> bool:
    """True if this beat requires alpha channel (render as MOV).

    Two conditions trigger alpha:
    1. The block type is inherently a transparent overlay (ALPHA_BLOCKS).
    2. The layout is a panel (panel-right, panel-top, panel-left) — the talking head
       must show through the empty regions of the canvas.
    Only truly fullscreen, speaker-replacing beats (logo-outro, transitions) stay opaque.
    """
    if layout in PANEL_LAYOUTS:
        return True
    return block_type in ALPHA_BLOCKS


def get_render_format(block_type: str, layout: str = "fullscreen") -> str:
    """Return 'mov' (alpha) or 'webm' (opaque) for this beat.

    mp4 is unusable: HyperFrames hardwires x264-params into its encode command,
    and neither its bundled FFmpeg nor Homebrew's FFmpeg ships libx264 on Apple Silicon.
    webm (VP9) works fine and FFmpeg accepts it as composite input.
    --resolution is NOT passed for either format (HyperFrames rejects it for both webm and mov).
    Both formats render at HyperFrames' default viewport: 1280×720 (landscape) / 720×1280 (portrait).
    """
    return "mov" if needs_alpha(block_type, layout) else "webm"


def build_all_beats(
    storyboard: dict,
    transcript_words: list[dict],
    niche: str,
    work_dir: Path,
    is_reel: bool = False,
    global_captions: bool = False,
) -> list[tuple[BeatSpec, Path]]:
    """Build project dirs for all beats in a storyboard.

    Returns list of (BeatSpec, project_dir) pairs in order.
    """
    resolution = "portrait" if is_reel else "landscape"
    caption_style = storyboard.get("caption_style", "matrix-decode")
    results: list[tuple[BeatSpec, Path]] = []

    for raw_beat in storyboard["beats"]:
        # Bug 3 fix: Beat JSON uses start_sec/end_sec/beat_id (from dataclasses.asdict)
        start = float(raw_beat["start_sec"])
        end = float(raw_beat["end_sec"])
        beat_type = raw_beat.get("beat_type", "overlay")

        # talking_head beats have no overlay composition — skip them
        if beat_type == "talking_head":
            continue

        # Derive block_type from beat_type + overlay_block/transition_block
        if beat_type == "overlay":
            block_type = raw_beat.get("overlay_block") or "editorial-emphasis"
        elif beat_type == "transition":
            block_type = raw_beat.get("transition_block") or "clip-wipe"
        elif beat_type == "outro":
            block_type = "logo-outro"
        else:
            block_type = raw_beat.get("overlay_block") or "editorial-emphasis"

        # Collect words spoken during this beat window
        beat_words = [
            w["word"] for w in transcript_words
            if w.get("start", 0) >= start and w.get("end", 0) <= end + 0.1
        ]
        # Fallback to transcript_excerpt from storyboard (not "caption" — wrong key)
        caption_text = " ".join(beat_words) if beat_words else raw_beat.get("transcript_excerpt", "")

        # overlay_content is a string in Beat JSON; wrap in dict for BeatSpec.data
        overlay_content = raw_beat.get("overlay_content") or ""
        data = {"content": overlay_content} if overlay_content else {}

        # Layout: outro is always fullscreen; overlays use storyboard's overlay_layout
        layout = "fullscreen"
        if beat_type == "overlay":
            raw_layout = raw_beat.get("overlay_layout") or "fullscreen"
            layout = raw_layout if raw_layout in (
                {"fullscreen"} | PANEL_LAYOUTS
            ) else "fullscreen"

        beat = BeatSpec(
            idx=raw_beat.get("beat_id", 0),
            block_type=block_type,
            start=start,
            end=end,
            caption=caption_text,
            caption_style=caption_style,
            data=data,
            layout=layout,
            broll_keywords=raw_beat.get("broll_keywords"),
        )

        print(f"  [hf-builder] Beat {beat.idx:02d} {beat.block_type} "
              f"({start:.1f}s–{end:.1f}s, {_duration_frames(start, end)}f)")

        project_dir = build_beat_project(beat, niche, work_dir, resolution, is_reel,
                                         global_captions=global_captions)
        results.append((beat, project_dir))

    return results
