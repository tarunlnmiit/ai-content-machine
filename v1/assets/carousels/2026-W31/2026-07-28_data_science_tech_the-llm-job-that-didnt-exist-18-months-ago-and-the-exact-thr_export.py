"""Export each carousel slide as a 1080x1350 PNG via Playwright."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HTML_PATH = Path(__file__).parent / "2026-07-21_data_science_tech_what-interviewers-actually-write-in-the-feedback-doc-after-y_carousel.html"
OUT_DIR = Path("assets/carousels/slides/2026-W31/2026-07-28_data_science_tech_the-llm-job-that-didnt-exist-18-months-ago-and-the-exact-thr")
SLIDE_W, SLIDE_H = 420, 525
SCALE = 1080 / SLIDE_W  # -> 1080x1350 output
NUM_SLIDES = 8

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

        for i in range(NUM_SLIDES):
            await page.evaluate(
                """(i) => {
                    const track = document.querySelector('.carousel-track');
                    track.style.transition = 'none';
                    track.style.transform = `translateX(-${i * 420}px)`;
                    document.querySelectorAll('.slide').forEach((slide, idx) => {
                        slide.querySelectorAll('.progress-seg .fill').forEach(fill => {
                            fill.style.width = idx <= i ? '100%' : '0%';
                        });
                    });
                }""",
                i,
            )
            await page.wait_for_timeout(80)
            await viewport.screenshot(path=str(OUT_DIR / f"slide_{i+1:02d}.png"))

        await browser.close()
    print(f"Exported {NUM_SLIDES} slides to {OUT_DIR}")

if __name__ == "__main__":
    asyncio.run(export())