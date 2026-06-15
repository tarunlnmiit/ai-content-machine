# assets/carousels/2026-W25/2026-06-15_poetry_quotes_plea-of-a-bruised-soul_export.py
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SLIDE_COUNT = 7
SCALE = 1080 / 420  # → 1080×1350px output per slide

HTML_PATH  = Path(__file__).parent / "2026-06-15_poetry_quotes_plea-of-a-bruised-soul_carousel.html"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "slides" / "2026-W25" / "2026-06-15_poetry_quotes_plea-of-a-bruised-soul"


async def export():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": 420, "height": 525},
            device_scale_factor=SCALE,
        )
        await page.goto(f"file://{HTML_PATH.resolve()}")
        await page.wait_for_load_state("networkidle")

        for i in range(SLIDE_COUNT):
            if i > 0:
                await page.evaluate(f"goTo({i})")
                await page.wait_for_timeout(420)

            out = OUTPUT_DIR / f"slide_{i + 1}.png"
            await page.locator(".carousel-viewport").screenshot(path=str(out))
            print(f"✓ {out.name}")

        await browser.close()
    print(f"\n{SLIDE_COUNT} slides → {OUTPUT_DIR}")


if __name__ == "__main__":
    asyncio.run(export())