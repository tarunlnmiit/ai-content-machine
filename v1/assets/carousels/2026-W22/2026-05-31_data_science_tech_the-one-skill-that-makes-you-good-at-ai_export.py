"""Export each carousel slide to 1080x1350 PNG via Playwright."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HTML_PATH = Path("carousel.html")  # save the HTML above to this path
OUT_DIR = Path("assets/carousels/slides")
SLIDE_COUNT = 8
SLIDE_W_CSS = 420
EXPORT_W = 1080
EXPORT_H = 1350
SCALE = EXPORT_W / SLIDE_W_CSS  # 1080/420

async def export_slides():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": SLIDE_W_CSS, "height": 525},
            device_scale_factor=SCALE,
        )
        await page.goto(HTML_PATH.resolve().as_uri())

        for i in range(SLIDE_COUNT):
            # advance track to slide i and bake its own progress-bar fill
            await page.evaluate(
                """(i) => {
                    const track = document.getElementById('track');
                    track.style.transition = 'none';
                    track.style.transform = `translateX(${-i * 420}px)`;
                    document.querySelectorAll('.slide').forEach((s, si) => {
                        s.querySelectorAll('.progress-seg .fill').forEach((f, segIdx) => {
                            f.style.width = segIdx <= i ? '100%' : '0%';
                        });
                    });
                    document.querySelector('.follow-tag')?.parentElement; // no-op, keep DOM settled
                }""",
                i,
            )
            slide = page.locator(".slide").nth(i)
            await slide.screenshot(path=str(OUT_DIR / f"slide_{i+1:02d}.png"))

        await browser.close()

if __name__ == "__main__":
    asyncio.run(export_slides())