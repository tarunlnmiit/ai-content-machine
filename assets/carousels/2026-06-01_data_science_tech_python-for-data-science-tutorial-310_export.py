"""
Export carousel slides as 1080x1350px PNGs.
Requires: pip install playwright && playwright install chromium
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

HTML_PATH = Path(__file__).parent / "2026-06-01_data_science_tech_python-for-data-science-tutorial-310_carousel.html"
OUT_DIR   = Path(__file__).parent / "slides" / "2026-06-01_data_science_tech_python-for-data-science-tutorial-310"
SLIDE_W   = 420
SLIDE_H   = 525
TOTAL     = 7
SCALE     = 1080 / 420  # ≈ 2.571 → 1080×1350 output

async def export_slides():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    file_url = HTML_PATH.resolve().as_uri()

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": SLIDE_W, "height": SLIDE_H},
            device_scale_factor=SCALE,
        )
        await page.goto(file_url, wait_until="networkidle")
        await page.add_style_tag(content="body { padding: 0 !important; }")
        await page.wait_for_timeout(100)

        carousel_vp = await page.query_selector(".carousel-viewport")
        if not carousel_vp:
            print("ERROR: carousel-viewport not found")
            await browser.close()
            return

        for i in range(TOTAL):
            await page.evaluate(f"""
                const t = document.querySelector('.carousel-track');
                t.style.transition = 'none';
                t.style.transform = 'translateX(-{i * SLIDE_W}px)';
            """)
            await page.wait_for_timeout(50)

            box = await carousel_vp.bounding_box()
            out_path = OUT_DIR / f"slide_{i+1:02d}.png"
            await page.screenshot(path=str(out_path), clip=box)
            print(f"✓ slide_{i+1:02d}.png → {out_path}")

        await browser.close()
    print(f"\nAll {TOTAL} slides exported to {OUT_DIR}")

if __name__ == "__main__":
    asyncio.run(export_slides())