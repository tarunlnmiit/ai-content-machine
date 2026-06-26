#!/usr/bin/env python3
"""Python-owned HTML shells for HyperFrames beat compositions.

Claude generates ONLY:
  1. An inner HTML fragment (no <html>/<body>/<head>)
  2. A GSAP timeline body (adds tweens to `tl`, scoped to `root`)

Python owns all spatial geometry:
  - The <html>/<body>/<head> wrapper
  - The positioned panel div (overflow:hidden hard-clips Claude's content)
  - The caption layer
  - The window.__timelines registration

This means Claude CANNOT accidentally:
  - Paint a full-canvas background that destroys alpha transparency
  - Center content on the full 1920×1080 canvas instead of the panel
  - Use position:fixed for captions
  - Oversize elements that escape the panel

Panel structure (for panel-* layouts):
    #main (1920×1080, transparent or dark bg)
    └── #panel  ← Python-positioned, overflow:hidden HARD CLIP, glass bg
        └── #content  ← Claude's content lives here, (0,0) = panel top-left
    └── #caption-layer  ← Python-owned, sibling of #panel, not clipped by it
"""
from __future__ import annotations

import html as _html
import re

GSAP_CDN = "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"

# All layouts that use glass-panel rendering (NOT fullscreen full-canvas).
# Exported so hf_beat_builder.py can import and use the same source of truth.
PANEL_LAYOUTS: frozenset[str] = frozenset({
    "panel-right", "panel-left", "panel-top", "panel-bottom",
    "lower-third", "pill-top", "pill-center", "corner-pip",
})

# CSS border-radius per panel layout (pill shapes need large radius)
_PANEL_RADIUS: dict[str, str] = {
    "panel-right":  "20px",
    "panel-left":   "20px",
    "panel-top":    "0 0 20px 20px",   # flush at top screen edge
    "panel-bottom": "20px 20px 0 0",   # flush at bottom screen edge
    "lower-third":  "20px 20px 0 0",   # rounded top, flush at bottom
    "pill-top":     "50px",             # fully rounded pill
    "pill-center":  "60px",             # fully rounded pill
    "corner-pip":   "14px",             # modest corner rounding
}


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def panel_rect(layout: str, width: int, height: int) -> tuple[int, int, int, int]:
    """Return (x1, y1, x2, y2) content rect for this layout.

    Single source of truth — used for panel positioning AND the prompt.
    """
    rects = {
        # ── Original five zones ────────────────────────────────────────────
        "fullscreen":   (0, 0, width, height),
        "panel-right":  (width // 2 + 20,  60, width - 40, height - 60),
        "panel-left":   (40, 60, width // 2 - 20, height - 60),
        "panel-top":    (60, 40, width - 60, height // 2 - 20),
        "panel-bottom": (60, height // 2 + 20, width - 60, height - 40),
        # ── New zones (v4) ────────────────────────────────────────────────
        # Full-width bottom strip (~25% of height — name/title bar area)
        "lower-third":  (0, height * 3 // 4, width, height),
        # Narrow floating pill near top-center (800×100px at 1920×1080)
        "pill-top":     (width // 2 - 400, 20, width // 2 + 400, 120),
        # Narrow floating pill at vertical center (1536×120px at 1920×1080)
        "pill-center":  (width // 10, height // 2 - 60, width * 9 // 10, height // 2 + 60),
        # Small overlay anchored to bottom-right corner (~440×220px at 1920×1080)
        "corner-pip":   (width * 3 // 4, height * 3 // 4 + 20, width - 40, height - 40),
    }
    return rects.get(layout, rects["fullscreen"])


# ---------------------------------------------------------------------------
# Caption layer (Python-owned, never Claude's job)
# ---------------------------------------------------------------------------

def build_caption_layer(caption: str) -> tuple[str, str]:
    """Return (html_fragment, js_body) for the word-by-word caption.

    The HTML lives at #main level (sibling of #panel), never inside #content.
    The JS body adds tweens to the shared `tl` timeline.
    """
    words = caption.strip().split()
    if not words:
        return "", ""
    escaped = [_html.escape(w) for w in words]
    spans = "".join(f'<span class="w">{w}</span>' for w in escaped)
    html_frag = f'  <div id="caption-layer"><div id="caption-pill">{spans}</div></div>'
    js_body = (
        "    var cw = document.querySelectorAll('#caption-pill .w');\n"
        "    gsap.set(cw, { opacity: 0, y: 8 });\n"
        "    tl.to(cw, { opacity: 1, y: 0, duration: 0.25, stagger: 0.1, "
        "ease: 'power2.out' }, 0.2);\n"
    )
    return html_frag, js_body


# ---------------------------------------------------------------------------
# Fragment safety pass
# ---------------------------------------------------------------------------

# Banned patterns in Claude's fragment. Applied ONLY for panel beats.
_PANEL_BANS: list[tuple[str, str]] = [
    (r'position\s*:\s*fixed',              'position: absolute'),
    (r'\binset\s*:\s*0\b',                 'inset: auto'),
    (r'(width|height)\s*:\s*100v[wh]',     r'\1: 100%'),
]

_ALL_BANS: list[tuple[str, str]] = [
    (r'white-space\s*:\s*nowrap\s*;?',     'white-space: normal;'),
    (r'position\s*:\s*fixed',              'position: absolute'),
    (r'(width|height)\s*:\s*100v[wh]',     r'\1: 100%'),
]

# Wrapper elements that should never appear in a fragment
_FORBIDDEN_TAGS = ('<html', '<body', '<!doctype', 'data-composition-id',
                   'data-composition-fps', '<head')


def sanitize_fragment(frag: str, is_panel: bool) -> str:
    """Apply safety replacements to Claude's inner HTML fragment."""
    bans = _PANEL_BANS + _ALL_BANS if is_panel else _ALL_BANS
    for pat, repl in bans:
        frag = re.sub(pat, repl, frag, flags=re.IGNORECASE)
    # Hard fail if Claude leaked wrapper elements
    low = frag.lower()
    for tag in _FORBIDDEN_TAGS:
        if tag in low:
            raise RuntimeError(
                f"Fragment contains forbidden wrapper element '{tag}'. "
                f"Claude returned a full document instead of an inner fragment."
            )
    return frag


def sanitize_timeline_js(js: str) -> str:
    """Strip any rogue timeline creation or __timelines registration from Claude's JS body."""
    js = re.sub(r'window\.__timelines\b.*?;', '', js)
    js = re.sub(
        r'(?:const|let|var)\s+tl\s*=\s*gsap\.timeline\s*\([^)]*\)\s*;?',
        '', js
    )
    return js.strip()


# ---------------------------------------------------------------------------
# Shell builder
# ---------------------------------------------------------------------------

def build_shell(
    *,
    layout: str,
    width: int,
    height: int,
    fps: int,
    duration_frames: int,
    duration_sec: float,
    is_alpha: bool,
    inner_html: str,
    inner_timeline_js: str,
    caption_html: str,
    caption_timeline_js: str,
    variables_json: str,
) -> str:
    """Build the complete index.html for one beat.

    inner_html and inner_timeline_js come from Claude.
    Everything else is Python-owned.
    """
    x1, y1, x2, y2 = panel_rect(layout, width, height)
    rect_w = x2 - x1
    rect_h = y2 - y1
    is_panel = layout in PANEL_LAYOUTS
    body_bg = "transparent" if is_alpha else "#0a0e1a"
    panel_border_radius = _PANEL_RADIUS.get(layout, "20px")

    if is_panel:
        # Glass panel, hard-clipped. Claude's content cannot escape it.
        panel_css = f"""
    /* === Python-owned panel geometry === */
    #panel {{
      position: absolute;
      left: {x1}px; top: {y1}px;
      width: {rect_w}px; height: {rect_h}px;
      overflow: hidden;
      border-radius: {panel_border_radius};
      background: rgba(17,24,39,0.88);
      backdrop-filter: blur(20px) saturate(160%);
      -webkit-backdrop-filter: blur(20px) saturate(160%);
      border: 1px solid rgba(255,255,255,0.08);
      box-shadow: 0 8px 40px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.06);
    }}
    /* Specular highlight at panel top edge */
    #panel::before {{
      content: '';
      position: absolute;
      top: 0; left: 10%; right: 10%;
      height: 1px;
      background: linear-gradient(to right, transparent, rgba(255,255,255,0.14), transparent);
      z-index: 100;
    }}
    /* Claude's content is scoped here. (0,0) = panel top-left. */
    #content {{
      position: absolute;
      inset: 0;
      overflow: hidden;
    }}"""
        fullscreen_ambient = ""
    else:
        # Fullscreen: panel fills the canvas. Full-canvas ambient backgrounds allowed.
        panel_css = """
    /* === Fullscreen layout === */
    #panel {
      position: absolute;
      inset: 0;
      overflow: hidden;
    }
    #content {
      position: absolute;
      inset: 0;
      overflow: hidden;
    }"""
        # Subtle ambient gradient for fullscreen dark beats
        if not is_alpha:
            fullscreen_ambient = f"""
    /* Fullscreen ambient background */
    #ambient {{
      position: absolute; inset: 0;
      background:
        radial-gradient(ellipse 70% 50% at 15% 30%, rgba(59,130,246,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 50% 70% at 85% 75%, rgba(139,92,246,0.09) 0%, transparent 60%),
        {body_bg};
    }}"""
        else:
            fullscreen_ambient = ""

    # Caption: sibling of #panel, never clipped by it.
    # Position depends on layout type:
    #   - lower-third: caption goes ABOVE the panel (the panel IS the caption band)
    #   - pill-*/corner-pip: caption stays at standard fullscreen bottom (panel floats elsewhere)
    #   - panel-*: caption is adjacent to the panel's bottom edge
    if is_panel:
        if layout in ("pill-top", "pill-center", "corner-pip"):
            # Floating panels — caption stays at fullscreen bottom position
            cap_bottom = 80
            cap_left = 0
            cap_width = width
        elif layout == "lower-third":
            # Lower-third IS the caption band — place transcript caption above it
            cap_bottom = height - y1 + 12
            cap_left = 0
            cap_width = width
        else:
            # panel-right / panel-left / panel-top / panel-bottom:
            # Caption stays at fullscreen bottom-center so it's always visible
            # and consistent with the Poetry position the creator prefers.
            # (Positioning it beside the panel caused it to be clipped and
            # visually disconnected from the speaker.)
            cap_bottom = 80
            cap_left = 0
            cap_width = width
        caption_css = f"""
    /* === Python-owned caption (sibling of #panel, never clipped) === */
    #caption-layer {{
      position: absolute;
      left: {cap_left}px; width: {cap_width}px;
      bottom: {cap_bottom}px;
      display: flex; justify-content: center; align-items: flex-end;
      pointer-events: none;
    }}"""
    else:
        caption_css = """
    /* === Python-owned caption (fullscreen) === */
    #caption-layer {
      position: absolute;
      left: 0; right: 0;
      bottom: 80px;
      display: flex; justify-content: center; align-items: flex-end;
      pointer-events: none;
    }"""

    # Indent Claude's content for readability
    inner_indented = "\n".join(f"      {line}" for line in inner_html.splitlines())
    inner_js_indented = "\n".join(f"      {line}" for line in inner_timeline_js.splitlines())
    caption_js_indented = "\n".join(f"      {line}" for line in caption_timeline_js.splitlines())

    ambient_div = '  <div id="ambient"></div>' if fullscreen_ambient else ""

    return f"""<!DOCTYPE html>
<html data-composition-fps="{fps}" data-composition-duration="{duration_frames}" data-composition-variables='{variables_json}'>
<head>
<meta charset="utf-8">
<style>
  /* === Python-owned base === */
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{
    width: {width}px; height: {height}px;
    background: {body_bg};
    overflow: hidden;
  }}
  #main {{
    position: relative;
    width: {width}px; height: {height}px;
    overflow: hidden;
  }}
  {panel_css}
  {fullscreen_ambient}
  {caption_css}
  /* Caption pill */
  #caption-pill {{
    max-width: {(width - 120) if layout in ('pill-top', 'pill-center', 'corner-pip', 'lower-third') else (rect_w - 60)}px;
    padding: 12px 24px;
    border-radius: 10px;
    background: rgba(10,14,26,0.75);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    color: #f0f4ff;
    font: 600 30px/1.4 'Inter', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
    text-align: center;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }}
  #caption-pill .w {{
    display: inline-block;
    margin: 0 3px;
    opacity: 0;
  }}
</style>
</head>
<body>
<div id="main" data-composition-id="main" data-duration="{duration_sec:.3f}" data-width="{width}" data-height="{height}">
  {ambient_div}
  <div id="panel">
    <div id="content">
{inner_indented}
    </div>
  </div>
{caption_html}
</div>
<script src="{GSAP_CDN}"></script>
<script>
(function () {{
  var vars = window.__hyperframes && window.__hyperframes.getVariables
    ? window.__hyperframes.getVariables() : {{}};
  var tl = gsap.timeline();
  var root = document.getElementById('content');

  /* ── Claude's content timeline (scoped to #content) ── */
  (function (tl, root, vars) {{
{inner_js_indented}
  }})(tl, root, vars);

  /* ── Caption timeline (Python-owned) ── */
  (function (tl) {{
{caption_js_indented}
  }})(tl);

  window.__timelines = window.__timelines || {{}};
  window.__timelines["main"] = tl;
}})();
</script>
</body>
</html>"""
