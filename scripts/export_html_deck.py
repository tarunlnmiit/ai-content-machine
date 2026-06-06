#!/usr/bin/env python3
"""Render a self-contained Claude Design HTML to PNG frames via Playwright.

Generic exporter for the bespoke "Claude Design" HTML artifacts (slide decks,
social post sets, reel covers). The HTML must expose two globals:

    window.__exportFrames = [{ "file": "slide_1.png", "w": 1920, "h": 1080 }, ...]
    window.__showFrame(i)   // activate frame i (hide the rest), pin it top-left

For each frame the exporter sets the viewport to the frame's native size, calls
__showFrame(i), waits for fonts/layout, and screenshots the viewport 1:1.

Story animations use scripts/export_story_animation.py instead (they need
frame-by-frame time scrubbing + ffmpeg encoding).

Usage:
    python3 scripts/export_html_deck.py \
        --html assets/slides/{slug}_social.html \
        --out-dir assets/social_posts
"""

import argparse
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright
    import asyncio
except ImportError:
    print("Error: Playwright not installed. Install with: pip install playwright && playwright install chromium")
    sys.exit(1)

SETTLE_MS = 450


def _frames_to_pdf(png_paths: list[Path], pdf_path: Path) -> None:
    """Assemble rendered PNG frames into a single multi-page PDF (one slide/page)."""
    from PIL import Image

    pages = [Image.open(p).convert("RGB") for p in png_paths]
    if not pages:
        return
    pages[0].save(pdf_path, save_all=True, append_images=pages[1:], resolution=150.0)
    print(f"  📄 {pdf_path.name} ({len(pages)} pages)")


async def export_frames(html_path: Path, out_dir: Path, pdf_name: str | None = None) -> list[str]:
    html_path = html_path.resolve()
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"🖼  Exporting frames: {html_path.name}")
    print(f"📁 Output: {out_dir}")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(html_path.as_uri(), wait_until="networkidle")
        await page.wait_for_load_state("domcontentloaded")

        frames = await page.evaluate("window.__exportFrames || []")
        if not frames:
            await browser.close()
            sys.exit(f"No window.__exportFrames found in {html_path}")

        written: list[str] = []
        for i, frame in enumerate(frames):
            w, h = int(frame["w"]), int(frame["h"])
            out_path = out_dir / frame["file"]

            await page.set_viewport_size({"width": w, "height": h})
            await page.evaluate(f"window.__showFrame({i})")
            try:
                await page.evaluate("document.fonts && document.fonts.ready")
            except Exception:
                pass
            await page.wait_for_timeout(SETTLE_MS)

            await page.screenshot(path=str(out_path), full_page=False)
            written.append(out_path)
            print(f"  ✓ {out_path.name} ({w}×{h})")

        await browser.close()

    if pdf_name:
        _frames_to_pdf(written, out_dir / pdf_name)

    print(f"\n✅ {len(written)} frame(s) → {out_dir}")
    return [p.name for p in written]


def main() -> None:
    ap = argparse.ArgumentParser(description="Render Claude Design HTML frames to PNG.")
    ap.add_argument("--html", required=True, help="Path to the self-contained HTML file")
    ap.add_argument("--out-dir", required=True, help="Directory to write PNG frames into")
    ap.add_argument("--pdf", metavar="NAME", help="Also assemble the frames into this PDF file (in out-dir)")
    args = ap.parse_args()

    html_path = Path(args.html)
    if not html_path.exists():
        sys.exit(f"Error: HTML file not found: {html_path}")

    asyncio.run(export_frames(html_path, Path(args.out_dir), args.pdf))


if __name__ == "__main__":
    main()
