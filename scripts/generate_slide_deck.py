#!/usr/bin/env python3
"""Generate a branded 1920×1080 slide deck (HTML + PDF) for a week's content.

For each slug, reads slide_outline.json (title_slide + slides[]) and the optional
claude_design_brief.json, asks Claude to produce ONE self-contained multi-section
HTML deck that satisfies the export contract used by scripts/export_html_deck.py,
then renders each slide to a PNG and assembles a {slug}_slides.pdf.

Outputs:
  assets/slides/{week}/{slug}_slides.html          (HTML source)
  assets/slides/{week}/{slug}/slide_N.png          (one PNG per slide)
  assets/slides/{week}/{slug}/{slug}_slides.pdf     (assembled deck)

Usage:
  python3 scripts/generate_slide_deck.py --week 2026-W24
  python3 scripts/generate_slide_deck.py --slug 2026-06-08_data_science_tech_python-for-data-science-tutorial-410
  python3 scripts/generate_slide_deck.py --week 2026-W24 --no-export
  python3 scripts/generate_slide_deck.py --week 2026-W24 --force
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from _console import console  # noqa: E402
from lib.claude_cli import call_claude  # noqa: E402
from lib.schedule_calc import get_iso_week  # noqa: E402

# Reuse helpers from the social-image pipeline (same brand/niche/slug logic).
from generate_social_images import (  # noqa: E402
    SLIDES_DIR,
    detect_niche,
    find_slug_dir,
    find_week_slugs,
    load_brand,
)
from export_html_deck import export_frames  # noqa: E402


DECK_SYSTEM = """You are a presentation design system for {brand_name} ({handle}).

## Brand Kit

- Handle: {handle}
- Brand name: {brand_name}
- Font heading: {font_heading}
- Font body: {font_body}
- Tone: {tone}

## Color Palette

```
PRIMARY   = "{primary}"
LIGHT     = "{light}"
DARK      = "{dark_color}"
DARK_BG   = "{dark_bg}"
LIGHT_BG  = "{light_bg}"
```

## Output

Generate ONE fully self-contained HTML file (no external deps except Google Fonts CDN).
It is a 16:9 slide deck rendered at 1920×1080 per slide. Output HTML only, no preamble.

## Structure (CRITICAL — do not deviate)

```html
<body>
  <div class="slide-nav" id="nav">
    <button id="prev-btn" aria-label="Previous">&larr;</button>
    <span class="slide-counter" id="counter">1 / N</span>
    <button id="next-btn" aria-label="Next">&rarr;</button>
  </div>
  <div class="slide-canvas" id="canvas">
    <section> ... slide 1 (title) ... </section>
    <section> ... slide 2 ... </section>
    <!-- one <section> per slide, in order -->
  </div>
  <script> ... export + nav contract (see below) ... </script>
</body>
```

## Required CSS (keep these rules exactly)

```css
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width:100%; height:100%; overflow:hidden; background: DARK_BG; }}
.slide-canvas {{ position:fixed; width:1920px; height:1080px; top:50%; left:50%; transform-origin:center center; }}
.slide-canvas > section {{ position:absolute; inset:0; opacity:0; visibility:hidden;
  transition: opacity 0.25s ease, visibility 0.25s; overflow:hidden; }}
.slide-canvas > section[data-active] {{ opacity:1; visibility:visible; }}
```

## Required closing <script> (copy this contract VERBATIM — the exporter depends on it)

```html
<script>
(function () {{
  'use strict';
  var canvas  = document.getElementById('canvas');
  var slides  = Array.prototype.slice.call(canvas.querySelectorAll('section'));
  var counter = document.getElementById('counter');
  var nav     = document.getElementById('nav');
  var TOTAL   = slides.length;
  var current = 0, navTimer;
  function fit() {{
    var scale = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
    canvas.style.transform = 'translate(-50%, -50%) scale(' + scale + ')';
  }}
  function show(n) {{
    n = Math.max(0, Math.min(TOTAL - 1, n));
    slides[current].removeAttribute('data-active');
    current = n; slides[current].setAttribute('data-active', '');
    if (counter) counter.textContent = (current + 1) + ' / ' + TOTAL;
    showNav();
  }}
  function showNav() {{
    nav.setAttribute('data-visible', '');
    clearTimeout(navTimer);
    navTimer = setTimeout(function () {{ nav.removeAttribute('data-visible'); }}, 2000);
  }}
  slides[0].setAttribute('data-active', '');
  fit();
  window.addEventListener('resize', fit);
  document.getElementById('prev-btn').addEventListener('click', function () {{ show(current - 1); }});
  document.getElementById('next-btn').addEventListener('click', function () {{ show(current + 1); }});
  document.addEventListener('keydown', function (e) {{
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {{ e.preventDefault(); show(current + 1); }}
    else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {{ e.preventDefault(); show(current - 1); }}
    else if (e.key === 'Home') {{ show(0); }} else if (e.key === 'End') {{ show(TOTAL - 1); }}
  }});
  document.addEventListener('mousemove', showNav, {{ passive: true }});
  window.__exportFrames = slides.map(function (_, i) {{
    return {{ file: 'slide_' + (i + 1) + '.png', w: 1920, h: 1080 }};
  }});
  window.__showFrame = function (i) {{
    slides.forEach(function (s, j) {{ if (j === i) s.setAttribute('data-active', ''); else s.removeAttribute('data-active'); }});
    current = i; fit();
  }};
}})();
</script>
```

## Design rules

- DARK_BG base on every slide. Content layer z-index >= 2, decorative layer z-index <= 1.
- Title slide: large heading (80-96px, {font_heading}, near-white), short lede in LIGHT, the
  "Tutorial/series" eyebrow in PRIMARY if relevant.
- Content slides: an eyebrow/section label in PRIMARY, an {font_heading} heading 56-64px, then
  bullets ({font_body}, ~30px) — one <li> per provided bullet, with a small PRIMARY tick marker.
- Niche decorative cues, pure CSS only (no <img>, no external URLs):
  DS = faint grid / circuit lines · Life = soft organic curves / bokeh glow · Poetry = ink-wash / halos.
- Brand bar: handle ({handle}) discreetly in a corner of each slide, muted.
- Use only px values (canvas is fixed 1920×1080). No vw/vh inside slides.
- Google Fonts: load only {font_heading} and {font_body}.
- If a bullet contains code (backticks or `=`/`()`), render it in a monospace code chip/panel.

## Deck content

Title slide: {title_slide}

Slides (in order):
{slides_block}

Tone hint: {tone_hint}

Build exactly {n_slides} content <section>s after the title section ({total_sections} sections total).
Generate the complete HTML immediately. Output HTML only.
"""


def _slides_block(slides: list[dict]) -> str:
    lines: list[str] = []
    for s in slides:
        heading = s.get("heading", "")
        bullets = s.get("bullet_points", []) or []
        lines.append(f"### Slide {s.get('slide_number', len(lines) + 1)}: {heading}")
        for b in bullets:
            lines.append(f"- {b}")
        lines.append("")
    return "\n".join(lines).strip()


def build_prompt(brand: dict, outline: dict, brief: dict | None) -> str:
    slides = outline.get("slides", []) or []
    tone_hint = ""
    if brief:
        tone_hint = brief.get("emotional_core", "") or ""
    return DECK_SYSTEM.format(
        **brand,
        title_slide=outline.get("title_slide", ""),
        slides_block=_slides_block(slides),
        tone_hint=tone_hint or brand["tone"],
        n_slides=len(slides),
        total_sections=len(slides) + 1,
    )


def generate_html(brand: dict, outline: dict, brief: dict | None) -> str:
    prompt = build_prompt(brand, outline, brief)
    html = call_claude(
        prompt,
        cache=True,
        timeout=300,
        temperature=brand["temperature"],
        normalize=False,
        stream=True,
        progress_label=f"Generating slide deck ({brand['label']})",
    )
    if "```html" in html:
        start = html.index("```html") + 7
        end = html.index("```", start)
        return html[start:end].strip()
    if "<!DOCTYPE" in html or "<html" in html:
        return html.strip()
    return html.strip()


def process_slug(slug: str, export: bool, force: bool) -> bool:
    slug_dir = find_slug_dir(slug)
    if not slug_dir:
        console.print(f"[red]Slug dir not found: {slug}[/red]")
        return False

    outline_path = slug_dir / "slide_outline.json"
    if not outline_path.exists():
        console.print(f"[red]slide_outline.json not found: {slug}[/red]")
        return False

    week = get_iso_week(slug[:10])
    niche_key = detect_niche(slug)
    brand = load_brand(niche_key)

    slides_week_dir = SLIDES_DIR / week
    slides_week_dir.mkdir(parents=True, exist_ok=True)
    html_out = slides_week_dir / f"{slug}_slides.html"
    # PNGs live in a per-slug subdir; the PDF sits at week level where
    # list_week_content.py tracks it: assets/slides/{week}/{slug}_slides.pdf
    pdf_name = f"{slug}_slides.pdf"
    png_dir = slides_week_dir / slug
    pdf_out = slides_week_dir / pdf_name

    if html_out.exists() and pdf_out.exists() and not force:
        console.print(f"[dim]Skip (use --force): {slug}[/dim]")
        return True

    console.print(f"\n[bold]{slug}[/bold]")
    console.print(f"  Niche: {niche_key} | Week: {week}")

    outline = json.loads(outline_path.read_text(encoding="utf-8"))
    brief: dict | None = None
    brief_path = slug_dir / "claude_design_brief.json"
    if brief_path.exists():
        try:
            brief = json.loads(brief_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    html_content = generate_html(brand, outline, brief)
    html_out.write_text(html_content, encoding="utf-8")
    console.print(f"  [green]✓[/green] HTML → {html_out.relative_to(REPO)}")

    if export:
        asyncio.run(export_frames(html_out, png_dir, pdf_name=pdf_name))
        # export_frames writes the PDF alongside the PNGs; lift it to week level.
        produced = png_dir / pdf_name
        if produced.exists():
            produced.replace(pdf_out)
        console.print(f"  [green]✓[/green] PDF → {pdf_out.relative_to(REPO)}")

    return True


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate branded slide decks for a week")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--week", help="ISO week (e.g. 2026-W24)")
    src.add_argument("--slug", help="Full slug (e.g. 2026-06-08_data_science_tech_...)")
    ap.add_argument("--no-export", dest="export", action="store_false", default=True,
                    help="Skip Playwright PNG/PDF export (HTML only)")
    ap.add_argument("--force", action="store_true", help="Overwrite existing outputs")
    args = ap.parse_args()

    slugs = [args.slug] if args.slug else find_week_slugs(args.week)
    if not slugs:
        sys.exit(f"No slugs found for: {args.slug or args.week}")

    console.print(f"[bold]generate_slide_deck[/bold] — {len(slugs)} slug(s)")

    ok = 0
    for slug in slugs:
        if process_slug(slug, args.export, args.force):
            ok += 1

    console.print(f"\n[bold]Done[/bold] — {ok}/{len(slugs)} slugs processed")
    console.print("Decks → assets/slides/{week}/{slug}_slides.html + {slug}/{slug}_slides.pdf")


if __name__ == "__main__":
    main()
