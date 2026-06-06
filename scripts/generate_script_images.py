#!/usr/bin/env python3
"""Generate infographic images for [IMAGE_INSERT:] and non-IDE [SCREEN:] markers in YT scripts.

Reads markers from a script, generates branded HTML infographics via Claude,
exports each as a 1080x1080 PNG using Playwright.

Skip logic for [SCREEN:] markers:
  - Skip if description mentions: IDE, code editor, terminal, file, jupyter, notebook
  - Generate if conceptual: diagram, comparison, framework, visual, chart, etc.

Usage:
  python3 scripts/generate_script_images.py --script content/scripts/my_script.md --niche ds
  python3 scripts/generate_script_images.py --script content/scripts/my_script.md --niche ds --dry-run
  python3 scripts/generate_script_images.py --script content/scripts/my_script.md --niche ds --no-export
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.claude_cli import call_claude  # noqa: E402

BRAND_KIT = REPO / "data" / "brand" / "brand_kit.yaml"
OUT_DIR = REPO / "assets" / "script_images"

NICHE_MAP = {
    "ds": "data_science_tech",
    "life": "life_self_dev",
    "poetry": "poetry_quotes",
}

# Keywords that indicate a [SCREEN:] is IDE/terminal — skip generation
IDE_KEYWORDS = re.compile(
    r"\b(code editor|IDE|terminal|command line|jupyter|notebook|"
    r"file manager|file listing|\.py|\.json|KeyError|output|stdout|"
    r"import |def |class |function|variable|syntax|error message|traceback)\b",
    re.IGNORECASE,
)


def load_brand(niche: str) -> dict:
    kit = yaml.safe_load(BRAND_KIT.read_text())
    niche_key = NICHE_MAP.get(niche, "data_science_tech")
    n = kit["niches"][niche_key]
    c = kit["colors"]
    return {
        "brand_name": n["brand_name"],
        "handle": kit["handle"],
        "primary": n["primary_color"],
        "light": n["light_color"],
        "dark_color": n["dark_color"],
        "light_bg": c["cream"],
        "dark_bg": c["background"],
        "font_heading": n["font_heading"],
        "font_body": n["font_body"],
        "tone": n["tone"],
        "temperature": n["claude_temperature"],
    }


def extract_markers(text: str) -> list[dict]:
    """Return list of {type, description, raw, line_idx} for qualifying markers."""
    markers = []
    for i, line in enumerate(text.splitlines()):
        stripped = line.strip()

        m = re.match(r'\[IMAGE_INSERT:\s*([^\]]+)\]', stripped, re.IGNORECASE)
        if m:
            markers.append({"type": "image", "description": m.group(1).strip(),
                            "raw": stripped, "line": i + 1})
            continue

        m = re.match(r'\[SCREEN:\s*([^\]]+)\]', stripped, re.IGNORECASE)
        if m:
            desc = m.group(1).strip()
            if not IDE_KEYWORDS.search(desc):
                markers.append({"type": "screen", "description": desc,
                                "raw": stripped, "line": i + 1})
    return markers


from lib.slug import slugify as _slugify

def slugify(text: str) -> str:
    return _slugify(text, max_length=50)


IMAGE_PROMPT = """<!DOCTYPE html>
<html>
<!-- YOU MUST START YOUR RESPONSE WITH THIS EXACT LINE ABOVE -->

You are a visual designer. Output a COMPLETE, VALID HTML FILE for a branded infographic.

CRITICAL RULES:
1. Your ENTIRE response must be valid HTML starting with <!DOCTYPE html>
2. NO explanations, NO descriptions, NO markdown, NO preamble
3. Just the raw HTML file. Nothing else.

Brand specs to use:
- Name: {brand_name} | Handle: {handle}
- Colors: primary={primary}, light={light}, dark={dark_color}, bg={dark_bg}
- Fonts: {font_heading} (heading), {font_body} (body) — load from Google Fonts
- Gradient: linear-gradient(135deg, {dark_color} 0%, {primary} 60%, {light} 100%)

Design requirements:
- body {{ margin:0; width:1080px; height:1080px; overflow:hidden; background:{dark_bg}; }}
- Clean modern infographic — diagram, comparison, or framework visual
- Light text on dark background
- No photos, no faces — pure graphic/typographic design
- Use unicode symbols/emoji for icons

Concept to visualize: "{description}"

START YOUR RESPONSE NOW WITH <!DOCTYPE html> — NO OTHER TEXT BEFORE IT:
"""


def generate_image_html(description: str, brand: dict) -> str:
    prompt = IMAGE_PROMPT.format(description=description, **brand)
    print("  Calling Claude...", flush=True)
    html = call_claude(prompt, cache=True, timeout=300, temperature=brand["temperature"], normalize=False)
    print("  Claude done. Processing HTML...", flush=True)
    # Strip markdown wrapper if present
    if "```html" in html:
        start = html.index("```html") + 7
        end = html.index("```", start)
        html = html[start:end].strip()
    else:
        html = html.strip()
    # Ensure body has id="infographic" for Playwright selector
    if 'id="infographic"' not in html and "id='infographic'" not in html:
        html = html.replace("<body", '<body id="infographic"', 1)
    return html


def export_png(html_path: Path, out_png: Path) -> bool:
    """Export #infographic (or body fallback) at 1080×1080 via Playwright."""
    script = f"""
import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={{"width": 1080, "height": 1080}})
        await page.goto("file://{html_path.resolve()}")
        await page.wait_for_load_state("networkidle")
        elem = page.locator("#infographic")
        count = await elem.count()
        if count > 0:
            await elem.screenshot(path="{out_png}")
        else:
            await page.screenshot(path="{out_png}", full_page=False)
        await browser.close()

asyncio.run(run())
"""
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    Export error: {result.stderr[:200]}")
        return False
    return True


def main():
    ap = argparse.ArgumentParser(description="Generate infographic images for script IMAGE_INSERT and non-IDE SCREEN markers")
    ap.add_argument("--script", required=True, type=Path)
    ap.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    ap.add_argument("--dry-run", action="store_true", help="List markers, skip generation")
    ap.add_argument("--no-export", action="store_true", help="Generate HTML only, skip PNG export")
    ap.add_argument("--force", action="store_true", help="Overwrite existing outputs")
    args = ap.parse_args()

    if not args.script.exists():
        sys.exit(f"Script not found: {args.script}")

    text = args.script.read_text()
    markers = extract_markers(text)

    if not markers:
        print("No qualifying IMAGE_INSERT or non-IDE SCREEN markers found.")
        return

    slug = args.script.stem
    out_dir = OUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Found {len(markers)} marker(s) to generate:")
    for m in markers:
        print(f"  line {m['line']:3d} [{m['type'].upper()}] {m['description'][:70]}")

    if args.dry_run:
        return

    brand = load_brand(args.niche)

    for i, m in enumerate(markers):
        img_slug = slugify(m["description"])
        html_path = out_dir / f"{i+1:02d}_{img_slug}.html"
        png_path = out_dir / f"{i+1:02d}_{img_slug}.png"

        if png_path.exists() and not args.force:
            print(f"\n[{i+1}/{len(markers)}] Skip (exists): {png_path.name}")
            continue

        print(f"\n[{i+1}/{len(markers)}] Generating: {m['description'][:60]}")

        html = generate_image_html(m["description"], brand)
        html_path.write_text(html)
        print(f"  HTML → {html_path.name}")

        if not args.no_export:
            print(f"  Exporting PNG...", flush=True)
            ok = export_png(html_path, png_path)
            if ok:
                print(f"  PNG  → {png_path.name}")
            else:
                print(f"  PNG  ✗ (open HTML manually to debug)")

    print(f"\nDone. Output: {out_dir.relative_to(REPO)}")


if __name__ == "__main__":
    main()
