"""Export each .slide of the carousel HTML as a 1080x1350 PNG."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SLUG = Path(__file__).stem.removesuffix("_export")
HTML_PATH = Path(__file__).parent / f"{SLUG}_carousel.html"
WEEK = Path(__file__).parent.name
OUT_DIR = Path(__file__).parent.parent / "slides" / WEEK / SLUG
SLIDE_W = 420
SLIDE_H = 525
SCALE = 1080 / SLIDE_W  # 2.5714...

async def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": SLIDE_W, "height": SLIDE_H},
            device_scale_factor=SCALE,
        )
        await page.goto(f"file://{HTML_PATH.resolve()}")

        slide_count = await page.eval_on_selector_all(".slide", "els => els.length")
        track = page.locator("#track")

        for i in range(slide_count):
            await page.evaluate(
                "i => { const t = document.getElementById('track'); "
                "t.style.transition = 'none'; "
                "t.style.transform = `translateX(${-i * 420}px)`; }",
                i,
            )
            await page.wait_for_timeout(80)
            slide = page.locator(".slide").nth(i)
            out_path = OUT_DIR / f"slide_{i + 1:02d}.png"
            await slide.screenshot(path=str(out_path))
            print(f"Saved {out_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
