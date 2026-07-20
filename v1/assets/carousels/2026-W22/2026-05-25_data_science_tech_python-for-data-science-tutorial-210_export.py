"""Export each carousel slide to 1080x1350 PNG via Playwright."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HTML_PATH = "carousel.html"  # save the HTML above to this path
OUT_DIR = Path("assets/carousels/slides")
SLIDE_W, SLIDE_H = 420, 525
SCALE = 1080 / SLIDE_W  # 1080x1350 output at scale 2.571...

async def export_slides():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": SLIDE_W, "height": SLIDE_H},
            device_scale_factor=SCALE,
        )
        await page.goto(f"file://{Path(HTML_PATH).resolve()}")

        track = page.locator("#track")
        slides = page.locator(".slide")
        count = await slides.count()

        for i in range(count):
            # jump the track directly to slide i (bypass drag/transition)
            await page.evaluate(
                "(i) => { window.goTo ? goTo(i) : null; "
                "document.getElementById('track').style.transition='none'; "
                "document.getElementById('track').style.transform = `translateX(${-i * 420}px)`; }",
                i,
            )
            await page.wait_for_timeout(80)

            frame_box = await page.locator(".carousel-viewport").bounding_box()
            await page.screenshot(
                path=str(OUT_DIR / f"slide_{i+1:02d}.png"),
                clip={
                    "x": frame_box["x"],
                    "y": frame_box["y"],
                    "width": SLIDE_W,
                    "height": SLIDE_H,
                },
            )

        await browser.close()

if __name__ == "__main__":
    asyncio.run(export_slides())