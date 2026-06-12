#!/usr/bin/env python3
"""Generate branded social post images for a week's content.

For each slug, reads claude_design_brief.json + instagram_caption.txt,
generates a multi-frame HTML (4 platform frames) via Claude, and exports 4 PNGs.

Outputs:
  assets/social_posts/{week}/{slug}_instagram.png
  assets/social_posts/{week}/{slug}_linkedin.png
  assets/social_posts/{week}/{slug}_threads.png
  assets/social_posts/{week}/{slug}_twitter.png
  assets/slides/{week}/{slug}_social.html  (HTML source)

Also invokes generate_carousel.py per slug.

Usage:
  python3 scripts/generate_social_images.py --week 2026-W24
  python3 scripts/generate_social_images.py --slug 2026-06-08_data_science_tech_python-for-data-science-tutorial-410
  python3 scripts/generate_social_images.py --week 2026-W24 --no-export
  python3 scripts/generate_social_images.py --week 2026-W24 --force
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from _console import console  # noqa: E402
from lib.claude_cli import call_claude  # noqa: E402
from lib.schedule_calc import get_iso_week  # noqa: E402

BRAND_KIT = REPO / "data" / "brand" / "brand_kit.yaml"
DERIVATIVES_DIR = REPO / "content" / "derivatives"
SOCIAL_DIR = REPO / "assets" / "social_posts"
SLIDES_DIR = REPO / "assets" / "slides"

NICHE_MAP = {
    "data_science_tech": "data_science_tech",
    "life_self_dev": "life_self_dev",
    "poetry_quotes": "poetry_quotes",
}

PLATFORMS = ["instagram", "linkedin", "threads", "twitter"]

# (css_class, width_px, height_px)
PLATFORM_FRAME = {
    "instagram": ("ig",  1080, 1080),
    "linkedin":  ("li",  1200,  628),
    "threads":   ("th",  1080, 1080),
    "twitter":   ("tw",  1200,  675),
}


def load_brand(niche_key: str) -> dict:
    kit = yaml.safe_load(BRAND_KIT.read_text())
    niche = kit["niches"][niche_key]
    colors = kit["colors"]
    _decorative = {
        "data_science_tech": "faint grid lines and circuit traces",
        "life_self_dev": "soft organic curves and warm bokeh glow",
        "poetry_quotes": "ink-wash brushstrokes and golden halos",
    }
    return {
        "creator": kit["creator"],
        "handle": kit["handle"],
        "brand_name": niche["brand_name"],
        "niche_label": niche["label"],
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
        "decorative_cue": _decorative[niche_key],
    }


def detect_niche(slug: str) -> str:
    if "data_science_tech" in slug:
        return "data_science_tech"
    if "life_self_dev" in slug:
        return "life_self_dev"
    if "poetry_quotes" in slug:
        return "poetry_quotes"
    return "life_self_dev"


def extract_hook(caption_text: str) -> str:
    """Pull hook line from instagram_caption.txt (first non-meta non-blank line)."""
    for line in caption_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("Format:", "Why:", "Slides:", "#")):
            continue
        if len(stripped) >= 20:
            return stripped
    return ""


def find_slug_dir(slug: str) -> Path | None:
    """Find derivative dir for slug, searching all week subfolders."""
    date_str = slug[:10]
    try:
        week = get_iso_week(date_str)
        direct = DERIVATIVES_DIR / week / slug
        if direct.exists():
            return direct
    except Exception:
        pass
    # Fallback: scan all week dirs
    for week_dir in DERIVATIVES_DIR.iterdir():
        if not week_dir.is_dir():
            continue
        candidate = week_dir / slug
        if candidate.exists():
            return candidate
    return None


def find_week_slugs(week: str) -> list[str]:
    week_dir = DERIVATIVES_DIR / week
    if not week_dir.exists():
        return []
    return sorted(
        d.name for d in week_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )


SOCIAL_SYSTEM = """You are a social media visual design system for {brand_name} ({handle}).

## Brand Kit

- Handle: {handle}
- Brand name: {brand_name}
- Font heading: {font_heading}
- Font body: {font_body}

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

The file contains **4 platform frames**, each a `<div class="frame {{cls}}">` with its own exact dimensions and layout. All frames start `display:none` — Playwright shows one at a time for export.

## Frame specs

| Class | Size       | Layout |
|-------|------------|--------|
| `ig`  | 1080×1080  | Square — full-bleed, vertically centered content |
| `li`  | 1200×628   | Landscape — left text zone 55%, right decorative zone 45% |
| `th`  | 1080×1080  | Square — same as ig (can share CSS) |
| `tw`  | 1200×675   | Landscape — left text zone 55%, right decorative zone 45% |

## HTML skeleton

```html
<body>
  <div class="frame ig"> ... </div>
  <div class="frame li"> ... </div>
  <div class="frame th"> ... </div>
  <div class="frame tw"> ... </div>
</body>
```

## CSS rules (CRITICAL — do not deviate)

```css
body {{ margin:0; padding:0; background:#000; position:relative; }}
.frame {{ display:none; position:relative; overflow:hidden; }}
.frame.ig {{ width:1080px; height:1080px; }}
.frame.th {{ width:1080px; height:1080px; }}
.frame.li {{ width:1200px; height:628px; }}
.frame.tw {{ width:1200px; height:675px; }}
```

## Design rules (apply to all frames)

- Dark background (DARK_BG) base
- Background layer: pure CSS only — no img tags, no external URLs
  Geometric shapes, gradients, grid lines using brand colors
  Niche cues: DS=grid/circuit lines · Life=organic curves/bokeh · Poetry=ink-wash/halos
- Content layer (z-index ≥ 10):
  - **hook_text**: {font_heading}, bold, near-white — 70–80px on squares, 52–64px on landscape
  - **sub_text**: {font_body}, LIGHT color, 20–26px, 1–2 lines below hook
  - **brand bar**: bottom edge — handle ({handle}) left · brand name right · 14–16px muted
- Left-edge accent bar: 6px wide, PRIMARY color, full height

## Constraints

- Each frame's internal elements must use px values matching THAT frame's dimensions
- No `transform`, no `vw/vh`, no `position:fixed`
- Google Fonts: load only {font_heading} and {font_body}
- **REQUIRED:** Add a `<script>` at the end of `<body>` that shows the first frame (`.frame.ig`) on page load. This allows viewing in browsers while remaining compatible with Playwright export.
- Text containers: `overflow:hidden` to prevent bleed
- Z-index: decorative ≤ 2, content ≥ 10

## Task

{content_section}

Generate the complete HTML immediately. No preamble. Output HTML only.
"""


def build_prompt(brand: dict, slug: str, brief: dict | None, hook: str) -> str:
    if brief:
        emotional_core = brief.get("emotional_core", "")
        quotes = brief.get("key_quotes", [])
        best_quote = quotes[0] if quotes else hook
        content_section = f"""## Design brief

emotional_core: {emotional_core}
hook_text: {best_quote}
sub_text: {hook if hook != best_quote else (quotes[1] if len(quotes) > 1 else '')}

Use hook_text as the dominant headline. Use sub_text as supporting line below."""
    else:
        content_section = f"""## Content

slug: {slug}
hook_text: {hook}

Derive a punchy 2–5 word visual headline from the hook. Use hook as sub_text."""

    system = SOCIAL_SYSTEM.format(**brand, content_section=content_section)
    return system


def generate_html(brand: dict, slug: str, brief: dict | None, hook: str) -> str:
    prompt = build_prompt(brand, slug, brief, hook)
    html = call_claude(
        prompt,
        cache=True,
        timeout=300,
        temperature=brand["temperature"],
        normalize=False,
        stream=True,
        progress_label=f"Generating social HTML ({brand['label']})",
    )
    # Strip markdown fences if present
    if "```html" in html:
        start = html.index("```html") + 7
        end = html.index("```", start)
        return html[start:end].strip()
    if "<!DOCTYPE" in html or "<html" in html:
        return html.strip()
    return html.strip()


def export_pngs(html_path: Path, slug: str, week: str) -> list[Path]:
    try:
        import asyncio
        from playwright.async_api import async_playwright
    except ImportError:
        console.print("[warn]playwright not installed — run: pip install playwright && playwright install chromium[/warn]")
        return []

    out_dir = SOCIAL_DIR / week
    out_dir.mkdir(parents=True, exist_ok=True)

    html_content = html_path.read_text(encoding="utf-8")
    exported = []

    async def _export() -> None:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            for platform in PLATFORMS:
                cls, w, h = PLATFORM_FRAME[platform]
                page = await browser.new_page(
                    viewport={"width": w, "height": h},
                    device_scale_factor=1.0,
                )
                await page.set_content(html_content, wait_until="networkidle")
                await page.wait_for_timeout(1500)
                # Show only the target frame; hide all others
                await page.evaluate(f"""() => {{
                    document.querySelectorAll('.frame').forEach(f => f.style.display = 'none');
                    const target = document.querySelector('.frame.{cls}');
                    if (target) target.style.display = 'block';
                }}""")
                await page.wait_for_timeout(300)
                out_file = out_dir / f"{slug}_{platform}.png"
                await page.screenshot(
                    path=str(out_file),
                    clip={"x": 0, "y": 0, "width": w, "height": h},
                )
                exported.append(out_file)
                console.print(f"  [green]✓[/green] {out_file.relative_to(REPO)}")
                await page.close()
            await browser.close()

    import asyncio
    asyncio.run(_export())
    return exported


def run_carousel(slug: str, slug_dir: Path, niche_key: str, force: bool) -> None:
    """Generate carousel HTML + PNGs + PDF."""
    date_str = slug[:10]
    week = get_iso_week(date_str)
    # Detect blog path
    blog_candidates = list((REPO / "content" / "blogs" / week).glob(f"{slug}*.md")) if (REPO / "content" / "blogs" / week).exists() else []
    if not blog_candidates:
        # Try flat
        blog_candidates = list((REPO / "content" / "blogs").glob(f"{slug}*.md"))
    if not blog_candidates:
        console.print(f"  [warn]No blog found for {slug} — skipping carousel[/warn]")
        return

    blog_path = blog_candidates[0]
    niche_short = {"data_science_tech": "ds", "life_self_dev": "life", "poetry_quotes": "poetry"}.get(niche_key, "life")
    cmd = [
        sys.executable, str(REPO / "scripts" / "generate_carousel.py"),
        "--blog", str(blog_path),
        "--niche", niche_short,
    ]
    if force:
        cmd.append("--force")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        console.print(f"  [green]✓[/green] carousel generated (HTML + PNG slides)")
        # Export carousel HTML as PDF
        _export_carousel_pdf(slug, week, niche_short)
    else:
        console.print(f"  [warn]carousel failed: {result.stderr.strip()[:120]}[/warn]")


def _export_carousel_pdf(slug: str, week: str, niche: str) -> None:
    """Export carousel HTML to PDF."""
    try:
        from playwright.async_api import async_playwright
        import asyncio
    except ImportError:
        console.print("[warn]playwright not installed — skipping PDF export[/warn]")
        return

    carousel_html = REPO / "assets" / "carousels" / f"{slug}_carousel.html"
    if not carousel_html.exists():
        return

    pdf_out = REPO / "assets" / "carousels" / f"{slug}_carousel.pdf"

    async def _pdf() -> None:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={"width": 420, "height": 2975})  # 7 slides × 425px height
            await page.goto(f"file://{carousel_html.resolve()}", wait_until="networkidle")
            await page.wait_for_timeout(1000)
            await page.pdf(path=str(pdf_out), format="A4")
            await browser.close()

    asyncio.run(_pdf())
    console.print(f"  [green]✓[/green] PDF → {pdf_out.relative_to(REPO)}")


def process_carousel_only(slug: str, force: bool) -> bool:
    """Generate carousel + PDF only (skip social images)."""
    slug_dir = find_slug_dir(slug)
    if not slug_dir:
        console.print(f"[red]Slug dir not found: {slug}[/red]")
        return False

    date_str = slug[:10]
    niche_key = detect_niche(slug)

    console.print(f"\n[bold]{slug}[/bold] (carousel only)")
    console.print(f"  Niche: {niche_key}")

    run_carousel(slug, slug_dir, niche_key, force)
    return True


def process_slug(slug: str, export: bool, force: bool) -> bool:
    slug_dir = find_slug_dir(slug)
    if not slug_dir:
        console.print(f"[red]Slug dir not found: {slug}[/red]")
        return False

    date_str = slug[:10]
    week = get_iso_week(date_str)
    niche_key = detect_niche(slug)
    brand = load_brand(niche_key)

    # Output paths
    slides_week_dir = SLIDES_DIR / week
    slides_week_dir.mkdir(parents=True, exist_ok=True)
    html_out = slides_week_dir / f"{slug}_social.html"

    if html_out.exists() and not force:
        # Check if PNGs also exist
        social_week_dir = SOCIAL_DIR / week
        all_pngs_exist = all(
            (social_week_dir / f"{slug}_{p}.png").exists() for p in PLATFORMS
        )
        if all_pngs_exist:
            console.print(f"[dim]Skip (use --force): {slug}[/dim]")
            return True

    console.print(f"\n[bold]{slug}[/bold]")
    console.print(f"  Niche: {niche_key} | Week: {week}")

    # Read inputs
    brief: dict | None = None
    brief_path = slug_dir / "claude_design_brief.json"
    if brief_path.exists():
        try:
            brief = json.loads(brief_path.read_text())
        except json.JSONDecodeError:
            pass

    hook = ""
    caption_path = slug_dir / "instagram_caption.txt"
    if caption_path.exists():
        hook = extract_hook(caption_path.read_text(encoding="utf-8"))

    if not hook and not brief:
        console.print(f"  [warn]No design brief or caption found — using slug title[/warn]")
        hook = slug.replace("_", " ").replace("-", " ")

    # Generate HTML
    html_content = generate_html(brand, slug, brief, hook)
    html_out.write_text(html_content, encoding="utf-8")
    console.print(f"  [green]✓[/green] HTML → {html_out.relative_to(REPO)}")

    # Export PNGs
    if export:
        export_pngs(html_out, slug, week)

    # Carousel
    run_carousel(slug, slug_dir, niche_key, force)

    return True


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate social post images for a week")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--week", help="ISO week (e.g. 2026-W24)")
    src.add_argument("--slug", help="Full slug (e.g. 2026-06-08_data_science_tech_...)")
    ap.add_argument("--carousel-only", action="store_true", help="Generate carousels + PDFs only (skip social images)")
    ap.add_argument("--no-export", dest="export", action="store_false", default=True,
                    help="Skip Playwright PNG export (HTML only)")
    ap.add_argument("--force", action="store_true", help="Overwrite existing outputs")
    args = ap.parse_args()

    slugs = [args.slug] if args.slug else find_week_slugs(args.week)

    if not slugs:
        target = args.slug or args.week
        sys.exit(f"No slugs found for: {target}")

    mode = "carousel-only" if args.carousel_only else ("social" if args.export else "social-html")
    console.print(f"[bold]generate_social_images[/bold] — {len(slugs)} slug(s), mode={mode}")

    ok = 0
    for slug in slugs:
        if args.carousel_only:
            if process_carousel_only(slug, args.force):
                ok += 1
        else:
            if process_slug(slug, args.export, args.force):
                ok += 1

    console.print(f"\n[bold]Done[/bold] — {ok}/{len(slugs)} slugs processed")
    if args.carousel_only:
        console.print(f"Carousels → assets/carousels/{{slug}}/")
        console.print(f"PDFs → assets/carousels/{{slug}}_carousel.pdf")
    else:
        if args.export:
            console.print(f"PNGs → assets/social_posts/{{week}}/")
        console.print(f"HTML → assets/slides/{{week}}/")


if __name__ == "__main__":
    main()
