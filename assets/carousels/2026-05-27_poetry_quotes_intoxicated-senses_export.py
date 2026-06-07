"""
Export each slide of the Breath of Poetry carousel as 1080×1350 PNG.
Run: python export_carousel.py
Requires: pip install playwright && playwright install chromium
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

HTML_FILE    = Path(__file__).parent / "carousel.html"
OUTPUT_DIR   = Path(__file__).parent / "assets" / "carousels" / "slides"
TOTAL_SLIDES = 7
SLIDE_W      = 420    # logical px in browser
SLIDE_H      = 525    # logical px (4:5 ratio)
EXPORT_W     = 1080   # target px
EXPORT_H     = 1350   # target px
SCALE        = EXPORT_W / SLIDE_W   # ≈ 2.5714


async def export_slides():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    url = HTML_FILE.as_uri()

    async with async_playwright() as p:
        browser = await p.chromium.launch()

        for idx in range(TOTAL_SLIDES):
            page = await browser.new_page(
                viewport={"width": SLIDE_W, "height": SLIDE_H},
                device_scale_factor=SCALE,
            )
            await page.goto(url, wait_until="networkidle")

            # Navigate carousel to target slide
            if idx > 0:
                await page.evaluate(f"goToSlide({idx})")
                await page.wait_for_timeout(450)   # let transition settle

            # Clip to just the carousel viewport (exclude IG chrome)
            carousel = await page.query_selector(".carousel-viewport")
            bbox     = await carousel.bounding_box()

            out_path = OUTPUT_DIR / f"slide_{idx + 1:02d}.png"
            await page.screenshot(
                path=str(out_path),
                clip={
                    "x":      bbox["x"],
                    "y":      bbox["y"],
                    "width":  SLIDE_W,
                    "height": SLIDE_H,
                },
            )
            print(f"  ✓  slide {idx + 1:02d} → {out_path}")
            await page.close()

        await browser.close()
        print(f"\n7 slides exported to {OUTPUT_DIR}")


if __name__ == "__main__":
    asyncio.run(export_slides())