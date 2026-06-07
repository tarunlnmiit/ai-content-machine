"""
Export carousel slides as 1080x1350px PNGs.
Usage: python export_carousel.py assets/carousels/python-tutorial-2-carousel.html
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

SLIDE_COUNT   = 7
SLIDE_W       = 420
SLIDE_H       = 525
SCALE         = 1080 / 420          # ≈ 2.5714  →  output 1080×1350px
SETTLE_MS     = 420                 # wait after goTo() for transition to finish


async def export_carousel(html_path: str) -> None:
    src = Path(html_path).resolve()
    if not src.exists():
        sys.exit(f"File not found: {src}")

    out_dir = Path("assets/carousels/slides")
    out_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(
            viewport={"width": SLIDE_W, "height": SLIDE_H},
            device_scale_factor=SCALE,
        )
        page = await ctx.new_page()
        await page.goto(f"file://{src}")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(600)       # allow Google Fonts to render

        for i in range(SLIDE_COUNT):
            await page.evaluate(f"window.goTo({i})")
            await page.wait_for_timeout(SETTLE_MS)

            out_path = out_dir / f"slide_{i + 1:02d}.png"
            await page.locator(".carousel-viewport").screenshot(path=str(out_path))
            print(f"  ✓ slide {i + 1}/{SLIDE_COUNT}  →  {out_path}")

        await browser.close()

    print(f"\nDone. {SLIDE_COUNT} slides written to {out_dir}/")


if __name__ == "__main__":
    html = sys.argv[1] if len(sys.argv) > 1 else "assets/carousels/python-tutorial-2-carousel.html"
    asyncio.run(export_carousel(html))