#!/usr/bin/env python3
"""Generate a YouTube thumbnail HTML + PNG from a blog post or topic.

Reads brand kit from data/brand/brand_kit.yaml.
Reads thumbnail_brief.json if it exists at content/derivatives/{slug}/.
Outputs a self-contained HTML to assets/thumbnails/{slug}_thumbnail.html.
Export to 1280×720 PNG via --export (requires playwright).

Usage:
  python3 scripts/generate_thumbnail.py --blog content/blogs/2026-05-21_data_science_tech_X.md
  python3 scripts/generate_thumbnail.py --blog path/to/blog.md --export
  python3 scripts/generate_thumbnail.py --topic "5 Python tricks" --niche ds --export

Niche shortcuts: ds | life | poetry
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from _console import console  # noqa: E402
from lib.claude_cli import call_claude  # noqa: E402

BRAND_KIT = REPO / "data" / "brand" / "brand_kit.yaml"
THUMBNAIL_DIR = REPO / "assets" / "thumbnails"
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

DERIVATIVES_DIR = REPO / "content" / "derivatives"

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


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:60].strip("-")


def find_thumbnail_brief(slug: str) -> dict | None:
    """Look for thumbnail_brief.json in derivatives matching the slug."""
    # Slug from blog filename — derivatives dirs use a truncated version
    for d in DERIVATIVES_DIR.iterdir():
        if not d.is_dir():
            continue
        brief_path = d / "thumbnail_brief.json"
        normalized_slug = slug.replace("_", "-")
        normalized_dir = d.name.replace("_", "-")
        if brief_path.exists() and (normalized_slug in normalized_dir or normalized_dir in normalized_slug):
            try:
                return json.loads(brief_path.read_text())
            except json.JSONDecodeError:
                return None
    return None


THUMBNAIL_SYSTEM = """You are a YouTube thumbnail design system for {brand_name} ({handle}).

## Brand Kit (pre-configured — do not ask for these)

- Handle: {handle}
- Brand name: {brand_name}
- Tone: {tone}
- Font heading: {font_heading}
- Font body: {font_body}

## Color Palette (use exactly these values)

```
BRAND_PRIMARY  = "{primary}"
BRAND_LIGHT    = "{light}"
BRAND_DARK     = "{dark_color}"
DARK_BG        = "{dark_bg}"
LIGHT_BG       = "{light_bg}"
```

Brand gradient: `linear-gradient(135deg, {dark_color} 0%, {primary} 60%, {light} 100%)`

## Output format

Generate a SINGLE, fully self-contained HTML file (no external dependencies except Google Fonts CDN).

The thumbnail must:
- Be exactly **1280px wide × 720px tall** — no scrollbars, no overflow, overflow:hidden on body
- Use a two-zone layout:
  - **LEFT ZONE (55-60% width):** Text content — main_text, sub_text, brand lockup
  - **RIGHT ZONE (40-45% width):** Decorative visual — pure CSS shapes, gradients, geometric patterns, niche-specific abstract art (NO external images)
- Dark background (DARK_BG) as base
- Bold, high-contrast typography — main_text dominates

## Text zones (left side)

1. **main_text** — ALL CAPS, very large (80-96px), {font_heading} heading font, high contrast (LIGHT_BG or white)
2. **sub_text** — Title Case, medium (22-28px), {font_body}, BRAND_LIGHT color, max 2 lines
3. **Brand lockup** — bottom-left corner: brand initial circle (BRAND_PRIMARY bg) + handle text (small, muted)
4. **Accent bar** — left edge: 6-8px vertical bar in BRAND_PRIMARY

## Right visual zone design rules

Use pure CSS only (no img tags, no external URLs). Create visual interest with:
- Overlapping geometric shapes (circles, rectangles, diagonal cuts)
- Brand gradient fills + transparency layers
- BRAND_PRIMARY / BRAND_LIGHT as accent colors against DARK_BG
- Subtle grid or dot patterns via CSS background-image repeating gradients
- For DS niche: code-block aesthetic, grid lines, data visualization shapes
- For Life niche: organic shapes, flowing curves, light rays
- For Poetry niche: typographic elements, quote marks, ink-wash style gradients

## Critical constraints

- `body {{ margin:0; padding:0; overflow:hidden; width:1280px; height:720px; }}`
- The `.thumbnail` root div must be exactly 1280×720, no bigger
- Google Fonts: load only {font_heading} and {font_body} (2 families max)
- No JavaScript needed — static image
- No `position:fixed` or viewport units that break at export viewport

## Task

{brief_section}

Create the complete thumbnail HTML immediately. No preamble, no questions. Output only the HTML.
"""


def build_prompt(brand: dict, content: str, brief: dict | None) -> str:
    if brief:
        brief_section = f"""## Thumbnail brief (use these exact values)

main_text: {brief.get('main_text', '')}
sub_text: {brief.get('sub_text', '')}
background_mood: {brief.get('background_mood', '')}
colour_palette: {', '.join(brief.get('colour_palette', []))}

Create the thumbnail using this brief. The main_text and sub_text are final — do not rewrite them."""
    else:
        brief_section = """## Source content (derive thumbnail copy from this)

Derive:
- main_text: 4-6 words, ALL CAPS, punchy hook or outcome
- sub_text: 8-12 words, clarifies the main promise

Use the content below."""

    system = THUMBNAIL_SYSTEM.format(**brand, brief_section=brief_section)

    return f"""{system}

---

## Source content

{content}

---

Generate the complete thumbnail HTML now.
"""


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate YouTube thumbnail HTML + PNG")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--blog", type=Path, help="Path to existing blog markdown file")
    src.add_argument("--topic", type=str, help="Topic string (no existing blog)")
    ap.add_argument("--niche", choices=list(NICHE_MAP.keys()), help="Niche (auto-detected from blog path)")
    ap.add_argument("--export", action="store_true", help="Run Playwright export to PNG after generation")
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

    # Load content + slug
    if args.blog:
        if not args.blog.exists():
            sys.exit(f"Blog not found: {args.blog}")
        content = args.blog.read_text(encoding="utf-8")
        slug = args.blog.stem
    else:
        content = f"Topic: {args.topic}\n\nGenerate thumbnail content based on this topic."
        slug = slugify(args.topic)

    out_path = THUMBNAIL_DIR / f"{slug}_thumbnail.html"
    if out_path.exists() and not args.force:
        console.print(f"[warn]Exists (use --force to overwrite): {out_path.relative_to(REPO)}[/warn]")
        if args.export:
            _run_playwright_export(out_path, slug)
        return

    # Load thumbnail brief if available
    brief = find_thumbnail_brief(slug)
    if brief:
        console.print(f"  Brief found: {brief.get('main_text', '')} / {brief.get('sub_text', '')}")
    else:
        console.print("  No thumbnail brief found — Claude will derive copy from content")

    console.print(f"[bold]Generating thumbnail[/bold] — {brand['label']}")
    console.print(f"  Niche: {niche_key} | Temp: {brand['temperature']}")

    prompt = build_prompt(brand, content, brief)

    console.print(f"  Prompt: {len(prompt):,} chars")
    html = call_claude(
        prompt,
        cache=True,
        timeout=300,
        temperature=brand["temperature"],
        normalize=False,
        stream=True,
        progress_label=f"Generating thumbnail HTML ({brand['label']})",
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

    if args.export:
        _run_playwright_export(out_path, slug)


def _run_playwright_export(html_path: Path, slug: str) -> None:
    try:
        import asyncio
        from playwright.async_api import async_playwright
    except ImportError:
        console.print("[warn]playwright not installed — run: pip install playwright && playwright install chromium[/warn]")
        return

    VIEW_W, VIEW_H = 1280, 720

    async def _export() -> None:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(
                viewport={"width": VIEW_W, "height": VIEW_H},
                device_scale_factor=1.0,
            )
            await page.set_content(html_path.read_text(encoding="utf-8"), wait_until="networkidle")
            await page.wait_for_timeout(2000)

            # Ensure no scrollbars / overflow
            await page.evaluate("""() => {
                document.body.style.cssText = 'margin:0;padding:0;overflow:hidden;width:1280px;height:720px;';
                const root = document.querySelector('.thumbnail');
                if (root) root.style.cssText = 'width:1280px;height:720px;overflow:hidden;';
            }""")
            await page.wait_for_timeout(300)

            out_file = THUMBNAIL_DIR / f"{slug}_thumbnail.png"
            await page.screenshot(
                path=str(out_file),
                clip={"x": 0, "y": 0, "width": VIEW_W, "height": VIEW_H},
            )
            console.print(f"[green]Exported:[/green] {out_file.relative_to(REPO)}")
            await browser.close()

    import asyncio
    asyncio.run(_export())


if __name__ == "__main__":
    main()
