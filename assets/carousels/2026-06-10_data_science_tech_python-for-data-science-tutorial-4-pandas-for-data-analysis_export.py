"""
Export carousel slides as 1080×1350px PNGs.
Output: assets/carousels/slides/
"""
import asyncio, os
from pathlib import Path
from playwright.async_api import async_playwright

HTML_FILE   = "assets/carousels/2026-W25/2026-06-10_data_science_tech_python-for-data-science-tutorial-4-pandas-for-data-analysis_carousel.html"
OUTPUT_DIR  = Path("assets/carousels/slides")
TOTAL       = 7
SCALE       = 1080 / 420  # 2.5714...

async def export():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": 420, "height": 525},
            device_scale_factor=SCALE,
        )
        url = f"file://{Path(HTML_FILE).resolve()}"
        await page.goto(url)
        await page.wait_for_load_state("networkidle")

        for i in range(TOTAL):
            await page.evaluate(f"goTo({i})")
            await page.wait_for_timeout(420)
            el   = await page.query_selector(".carousel-viewport")
            path = OUTPUT_DIR / f"slide_{i+1:02d}.png"
            await el.screenshot(path=str(path))
            print(f"✓ slide {i+1:02d} → {path}")

        await browser.close()

asyncio.run(export())