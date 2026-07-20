"""Export carousel slides to 1080x1350 PNGs via Playwright."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HTML_PATH = Path(__file__).parent / "2026-07-16_life_self_dev_ten-years-of-independence_carousel.html"
OUT_DIR = Path(__file__).parents[2] / "assets" / "carousels" / "slides"
SLIDE_W = 420
SLIDE_H = 525
SCALE = 1080 / SLIDE_W  # 2.5714...
TOTAL_SLIDES = 7
SLUG = "2026-07-16_life_self_dev_ten-years-of-independence"

async def export():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": SLIDE_W, "height": SLIDE_H},
            device_scale_factor=SCALE,
        )
        await page.goto(f"file://{HTML_PATH.resolve()}")
        track = page.locator("#track")
        for i in range(TOTAL_SLIDES):
            await page.evaluate(f"document.getElementById('track').style.transition='none'; document.getElementById('track').style.transform='translateX({-i * SLIDE_W}px)';")
            await page.wait_for_timeout(80)
            viewport = page.locator(".carousel-viewport")
            out_path = OUT_DIR / f"{SLUG}_slide{i+1}.png"
            await viewport.screenshot(path=str(out_path))
            print(f"Saved {out_path}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(export())