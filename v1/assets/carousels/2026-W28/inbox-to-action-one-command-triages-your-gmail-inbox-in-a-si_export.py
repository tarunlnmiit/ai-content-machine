"""Export inbox-to-action carousel slides to 1080x1350 PNGs via Playwright."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HTML_PATH = Path("assets/carousels/inbox-to-action-one-command-triages-your-gmail-inbox-in-a-si_carousel.html")
OUTPUT_DIR = Path("assets/carousels/slides/inbox-to-action-one-command-triages-your-gmail-inbox-in-a-si")

SLIDE_WIDTH = 420
SLIDE_HEIGHT = 525
DEVICE_SCALE_FACTOR = 1080 / SLIDE_WIDTH  # -> 1080x1350 output


async def export_slides():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": SLIDE_WIDTH, "height": SLIDE_HEIGHT},
            device_scale_factor=DEVICE_SCALE_FACTOR,
        )
        await page.goto(f"file://{HTML_PATH.resolve()}")

        slide_count = await page.eval_on_selector_all(".slide", "els => els.length")

        for index in range(slide_count):
            await page.evaluate(
                """(i) => {
                    const track = document.getElementById('track');
                    track.style.transition = 'none';
                    track.style.transform = `translateX(${-i * 420}px)`;
                    document.querySelectorAll('.ig-dot').forEach((d, idx) => {
                        d.classList.toggle('active', idx === i);
                    });
                    document.querySelectorAll('.slide').forEach(slide => {
                        const fills = slide.querySelectorAll('.progress-seg .fill');
                        fills.forEach((f, idx) => {
                            f.style.width = idx <= i ? '100%' : '0%';
                        });
                    });
                }""",
                index,
            )
            await page.wait_for_timeout(120)

            viewport_el = await page.query_selector(".carousel-viewport")
            out_path = OUTPUT_DIR / f"slide_{index + 1:02d}.png"
            await viewport_el.screenshot(path=str(out_path))
            print(f"Exported {out_path}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(export_slides())