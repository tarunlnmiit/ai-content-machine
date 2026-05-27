#!/usr/bin/env python3
"""Generate an Instagram carousel HTML from a blog post or topic.

Reads brand kit from data/brand/brand_kit.yaml.
Outputs a self-contained HTML to assets/carousels/{slug}_carousel.html.
Export to 1080×1350 PNGs via --export (requires playwright).

Usage:
  python3 scripts/generate_carousel.py --blog content/blogs/2026-05-21_data_science_tech_X.md
  python3 scripts/generate_carousel.py --topic "5 Python tricks for data scientists" --niche ds
  python3 scripts/generate_carousel.py --blog path/to/blog.md --export
  python3 scripts/generate_carousel.py --blog path/to/blog.md --slides 7

Niche shortcuts: ds | life | poetry
"""

import argparse
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from _console import console  # noqa: E402
from lib.claude_cli import call_claude  # noqa: E402

BRAND_KIT = REPO / "data" / "brand" / "brand_kit.yaml"
CAROUSEL_DIR = REPO / "assets" / "carousels"
CAROUSEL_DIR.mkdir(parents=True, exist_ok=True)

NICHE_MAP = {
    "ds": "data_science_tech",
    "life": "life_self_dev",
    "poetry": "poetry_quotes",
    "data_science_tech": "data_science_tech",
    "life_self_dev": "life_self_dev",
    "poetry_quotes": "poetry_quotes",
}


def load_brand(niche_key: str) -> dict:
    kit = yaml.safe_load(BRAND_KIT.read_text())
    niche = kit["niches"][niche_key]
    colors = kit["colors"]
    return {
        "creator": kit["creator"],
        "handle": kit["handle"],
        "brand_name": niche["brand_name"],
        "primary": niche["primary_color"],
        "light": niche["light_color"],
        "dark_color": niche["dark_color"],
        "light_bg": colors["cream"],
        "light_border": "#D6D0C4",
        "dark_bg": colors["background"],
        "font_heading": niche["font_heading"],
        "font_body": niche["font_body"],
        "font_style": niche["font_style"],
        "tone": niche["tone"],
        "temperature": niche["claude_temperature"],
        "label": niche["label"],
    }


def detect_niche_from_path(path: Path) -> str:
    name = path.stem.lower()
    if "data_science_tech" in name or "_ds_" in name:
        return "data_science_tech"
    if "life_self_dev" in name or "_life_" in name:
        return "life_self_dev"
    if "poetry_quotes" in name or "_poetry_" in name:
        return "poetry_quotes"
    return "data_science_tech"


CAROUSEL_SYSTEM = """You are an Instagram carousel design system for {brand_name} ({handle}).

## Brand Kit (pre-configured — do not ask for these)

- Handle: {handle}
- Brand name: {brand_name}
- Tone: {tone}
- Font heading: {font_heading}
- Font body: {font_body}
- Font style: {font_style}

## Color Palette (6-token — use exactly these values)

```
BRAND_PRIMARY  = "{primary}"
BRAND_LIGHT    = "{light}"
BRAND_DARK     = "{dark_color}"
LIGHT_BG       = "{light_bg}"
LIGHT_BORDER   = "{light_border}"
DARK_BG        = "{dark_bg}"
```

Brand gradient: `linear-gradient(165deg, {dark_color} 0%, {primary} 50%, {light} 100%)`

## Output format

Generate a single, fully self-contained HTML file (no external dependencies except Google Fonts CDN).

## REQUIRED CSS class names (export pipeline depends on these — DO NOT rename)

- Outer Instagram frame:    `class="ig-frame"`
- Carousel viewport:        `class="carousel-viewport"`
- Sliding track (flex row): `class="carousel-track"`
- Each individual slide:    `class="slide"` (add modifiers as extra classes, e.g. `class="slide dark"`)

JS must translate `.carousel-track` by `translateX(-N * 420px)` where N is slide index.

The carousel must:
- Be exactly 420px wide (ig-frame width)
- Use 4:5 aspect ratio slides (420×525px viewport)
- Alternate LIGHT_BG and DARK_BG backgrounds for visual rhythm
- Include progress bar on every slide (fills as slides progress)
- Include swipe arrow on every slide EXCEPT the last
- Last slide: no arrow, full progress bar, CTA button
- Include Instagram frame wrapper with header, dots, action icons, caption
- Include pointer/touch drag interaction for preview

## Required slide sequence ({slides} slides)

| # | Type | Background | Purpose |
|---|------|------------|---------|
| 1 | Hero | LIGHT_BG | Hook — stop-scroll statement, brand logo lockup |
| 2 | Problem | DARK_BG | Pain point or what's broken |
| 3 | Solution | Brand gradient | The answer |
| 4 | Content | LIGHT_BG | Key points / features / tips |
| 5 | Details | DARK_BG | Depth / specifics |
| 6 | How-to | LIGHT_BG | Numbered steps or process |
| 7 | CTA | Brand gradient | Call to action — no arrow |

Adapt sequence to the content. 5-10 slides acceptable, 7 ideal.

## Components to use

Progress bar, swipe arrow, tag labels, logo lockup (use brand initial '{initial}' in circle),
feature list rows, numbered steps, prompt/quote boxes — exactly as specified in standard carousel design patterns.

Content padding: `0 36px`. Bottom-aligned slides: `0 36px 52px` (clear progress bar).

## Export script

After the HTML, output a fenced Python code block with the Playwright export script
that exports each slide as 1080×1350px PNG using device_scale_factor=1080/420.
Output to: assets/carousels/slides/

## Task

Create a {slides}-slide Instagram carousel based on the content below.
Generate the complete, copy-pasteable HTML immediately. No preamble, no asking questions.
"""


def build_prompt(brand: dict, content: str, slides: int) -> str:
    system = CAROUSEL_SYSTEM.format(
        **brand,
        slides=slides,
        initial=brand["brand_name"][0].upper(),
    )
    return f"""{system}

---

## Source content

{content}

---

Generate the complete carousel HTML now.
"""


def slugify(text: str) -> str:
    import re
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:60].strip("-")


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate Instagram carousel HTML")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--blog", type=Path, help="Path to existing blog markdown file")
    src.add_argument("--topic", type=str, help="Topic string (no existing blog)")
    ap.add_argument("--niche", choices=list(NICHE_MAP.keys()), help="Niche (auto-detected from blog path)")
    ap.add_argument("--slides", type=int, default=7, help="Number of slides (default 7)")
    ap.add_argument("--export", action=argparse.BooleanOptionalAction, default=True, help="Run Playwright export after generation (default: on, use --no-export to skip)")
    ap.add_argument("--force", action="store_true", help="Overwrite existing output")
    args = ap.parse_args()

    # Resolve niche
    if args.niche:
        niche_key = NICHE_MAP[args.niche]
    elif args.blog:
        niche_key = detect_niche_from_path(args.blog)
    else:
        ap.error("--niche required when using --topic")

    brand = load_brand(niche_key)

    # Load content
    if args.blog:
        if not args.blog.exists():
            sys.exit(f"Blog not found: {args.blog}")
        content = args.blog.read_text(encoding="utf-8")
        slug = args.blog.stem
    else:
        content = f"Topic: {args.topic}\n\nGenerate carousel content based on this topic."
        slug = slugify(args.topic)

    out_path = CAROUSEL_DIR / f"{slug}_carousel.html"
    if out_path.exists() and not args.force:
        console.print(f"[warn]Exists (use --force to overwrite): {out_path.relative_to(REPO)}[/warn]")
        return

    console.print(f"[bold]Generating carousel[/bold] — {brand['label']}")
    console.print(f"  Niche: {niche_key} | Slides: {args.slides} | Temp: {brand['temperature']}")

    prompt = build_prompt(brand, content, args.slides)

    console.print(f"  Prompt: {len(prompt):,} chars")
    html = call_claude(
        prompt,
        cache=True,
        timeout=600,
        temperature=brand["temperature"],
        normalize=False,  # HTML — don't normalize
        stream=True,
        progress_label=f"Generating carousel HTML ({brand['label']})",
    )

    # Extract HTML block if Claude wraps in markdown
    if "```html" in html:
        start = html.index("```html") + 7
        end = html.index("```", start)
        html_content = html[start:end].strip()
    elif "<!DOCTYPE" in html or "<html" in html:
        html_content = html.strip()
    else:
        html_content = html.strip()

    out_path.write_text(html_content, encoding="utf-8")
    console.print(f"[green]Saved:[/green] {out_path.relative_to(REPO)}")

    # Extract and save export script if present
    if "```python" in html:
        try:
            py_start = html.index("```python") + 9
            py_end = html.index("```", py_start)
            export_script = html[py_start:py_end].strip()
            export_path = CAROUSEL_DIR / f"{slug}_export.py"
            export_path.write_text(export_script, encoding="utf-8")
            console.print(f"[green]Export script:[/green] {export_path.relative_to(REPO)}")
        except ValueError:
            pass

    if args.export:
        _run_playwright_export(out_path, slug, args.slides)


def _run_playwright_export(html_path: Path, slug: str, total_slides: int) -> None:
    try:
        import asyncio
        from playwright.async_api import async_playwright
    except ImportError:
        console.print("[warn]playwright not installed — run: pip install playwright && playwright install chromium[/warn]")
        return

    slides_dir = CAROUSEL_DIR / "slides" / slug
    slides_dir.mkdir(parents=True, exist_ok=True)

    VIEW_W, VIEW_H = 420, 525
    SCALE = 1080 / 420

    async def _export() -> None:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(
                viewport={"width": VIEW_W, "height": VIEW_H},
                device_scale_factor=SCALE,
            )
            await page.set_content(html_path.read_text(encoding="utf-8"), wait_until="networkidle")
            await page.wait_for_timeout(3000)

            track_info = await page.evaluate("""() => {
                document.querySelectorAll('.ig-header,.ig-dots,.ig-dots-nav,.ig-actions,.ig-caption,.ig-follow,.ig-meta,.ig-sub,.bottom-strip')
                    .forEach(el => el.style.display='none');

                // Find Instagram frame
                const frame = document.querySelector('.ig-frame, .ig-phone, [class*="ig-frame"], [class*="phone"]');
                if (frame) frame.style.cssText = 'width:420px;height:525px;max-width:none;border-radius:0;box-shadow:none;overflow:hidden;margin:0;padding:0;';

                // Find viewport
                const vp = document.querySelector('.carousel-viewport, .carousel-wrap, .slides-viewport, [class*="viewport"], [class*="carousel-wrap"]');
                if (vp) vp.style.cssText = 'width:420px;height:525px;aspect-ratio:unset;overflow:hidden;cursor:default;position:relative;';

                document.body.style.cssText = 'padding:0;margin:0;display:block;overflow:hidden;';

                // Find track: try common names, then generic — any parent of multiple .slide children
                let track = document.querySelector('.carousel-track, .slides-track, .track');
                if (!track) {
                    const slides = document.querySelectorAll('[class*="slide"]:not([class*="slide-num"])');
                    if (slides.length > 1) track = slides[0].parentElement;
                }
                if (track) {
                    track.dataset.__exportTrack = '1';
                    return { found: true, tag: track.tagName, cls: track.className, children: track.children.length };
                }
                return { found: false };
            }""")
            if not track_info.get("found"):
                console.print("[warn]Could not locate carousel track — slides will be duplicates[/warn]")
            else:
                console.print(f"  Track: <{track_info['tag'].lower()} class=\"{track_info['cls']}\"> ({track_info['children']} children)")
            await page.wait_for_timeout(500)

            for i in range(total_slides):
                await page.evaluate("""(idx) => {
                    const track = document.querySelector('[data-__export-track="1"]');
                    if (track) {
                        track.style.transition='none';
                        track.style.transform='translateX('+(-idx*420)+'px)';
                    }
                }""", i)
                await page.wait_for_timeout(400)
                out_file = slides_dir / f"slide_{i+1}.png"
                await page.screenshot(
                    path=str(out_file),
                    clip={"x": 0, "y": 0, "width": VIEW_W, "height": VIEW_H},
                )
                console.print(f"  [green]Exported slide {i+1}/{total_slides}[/green]")

            await browser.close()

    asyncio.run(_export())
    console.print(f"[bold]Slides at:[/bold] {slides_dir.relative_to(REPO)}/")


if __name__ == "__main__":
    main()
