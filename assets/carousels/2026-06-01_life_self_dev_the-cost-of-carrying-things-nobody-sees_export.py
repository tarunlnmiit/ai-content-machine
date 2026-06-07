"""
Export carousel slides as 1080×1350 PNG files.
Run from project root: python scripts/export_carousel_slides.py

Requires: playwright (pip install playwright && playwright install chromium)
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HTML_FILE   = Path("assets/carousels/the-cost-of-carrying.html").resolve()
OUTPUT_DIR  = Path("assets/carousels/slides")
SLIDE_COUNT = 7
SCALE       = 1080 / 420   # 420 * scale = 1080px output width


async def export_slides():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(
            viewport={"width": 560, "height": 760},
            device_scale_factor=SCALE,
        )
        page = await ctx.new_page()
        await page.goto(f"file://{HTML_FILE}")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(900)  # let fonts and layout settle

        viewport_el = page.locator(".carousel-viewport")

        for i in range(SLIDE_COUNT):
            await page.evaluate(f"goTo({i})")
            await page.wait_for_timeout(480)  # transition + settle

            out = OUTPUT_DIR / f"slide_{i + 1:02d}.png"
            await viewport_el.screenshot(path=str(out))
            print(f"  ✓  slide {i + 1:02d}  →  {out}")

        await browser.close()

    print(f"\nDone. {SLIDE_COUNT} slides in {OUTPUT_DIR}/")


if __name__ == "__main__":
    asyncio.run(export_slides())