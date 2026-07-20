"""Export carousel slides to 1080x1350 PNGs via Playwright."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HTML_PATH = Path("v1/assets/carousels/2026-07-06_data_science_tech_the-local-ai-agent-i-built-in-a-weekend-now-does-the-grunt-w_carousel.html")
OUT_DIR = Path("v1/assets/carousels/slides/2026-W28_the-local-ai-agent-i-built-in-a-weekend-now-does-the-grunt-w")
SLIDE_COUNT = 7
DEVICE_SCALE = 1080 / 420  # target 1080x1350 from 420x525 viewport

async def export_slides():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": 420, "height": 525},
            device_scale_factor=DEVICE_SCALE,
        )
        await page.goto(f"file://{HTML_PATH.resolve()}")
        await page.wait_for_timeout(300)

        viewport_el = page.locator("#viewport")

        for i in range(SLIDE_COUNT):
            await page.evaluate(f"goTo({i})")
            await page.wait_for_timeout(400)  # let transition settle
            out_path = OUT_DIR / f"slide_{i+1:02d}.png"
            await viewport_el.screenshot(path=str(out_path))
            print(f"Exported {out_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(export_slides())