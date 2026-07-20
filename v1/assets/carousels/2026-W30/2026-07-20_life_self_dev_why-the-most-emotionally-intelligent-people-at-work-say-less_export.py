import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HTML_PATH = Path(__file__).parent / "2026-07-20_life_self_dev_emotional-intelligence-at-work_carousel.html"
OUT_DIR = Path("assets/carousels/slides/2026-W29/2026-07-20_life_self_dev_emotional-intelligence-at-work")
SLIDE_COUNT = 8
SLIDE_W, SLIDE_H = 420, 525
SCALE = 1080 / SLIDE_W  # 1080x1350 output

async def export():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": SLIDE_W, "height": SLIDE_H},
            device_scale_factor=SCALE,
        )
        await page.goto(f"file://{HTML_PATH.resolve()}")
        viewport = page.locator(".carousel-viewport")
        track = page.locator(".carousel-track")
        for i in range(SLIDE_COUNT):
            await track.evaluate(
                "(el, i) => { el.style.transition = 'none'; el.style.transform = `translateX(${-i * 420}px)`; }",
                i,
            )
            await page.wait_for_timeout(60)
            await viewport.screenshot(path=str(OUT_DIR / f"slide_{i+1}.png"))
        await browser.close()

if __name__ == "__main__":
    asyncio.run(export())