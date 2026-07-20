"""
Export each carousel slide to a 1080x1350 PNG using Playwright.
Targets assets/carousels/slides/.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HTML_FILE = Path(__file__).parent / "carousel.html"
OUT_DIR = Path(__file__).parent.parent.parent / "assets" / "carousels" / "slides"
SLIDE_W = 420
SLIDE_H = 525
SCALE = 1080 / SLIDE_W  # 2.5714...
TOTAL_SLIDES = 7
SLUG = "2026-07-16_life_self_dev_write-decisions-before-you-make-them"

async def export_slides():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": SLIDE_W, "height": SLIDE_H},
            device_scale_factor=SCALE,
        )
        await page.goto(f"file://{HTML_FILE.resolve()}")

        for i in range(TOTAL_SLIDES):
            await page.evaluate(f"""
                (() => {{
                    const track = document.getElementById('track');
                    track.style.transition = 'none';
                    track.style.transform = 'translateX({-i * SLIDE_W}px)';

                    document.querySelectorAll('.slide').forEach((slide, idx) => {{
                        const fills = slide.querySelectorAll('.progress-seg .fill');
                        fills.forEach((fill, segIdx) => {{
                            fill.style.width = segIdx <= {i} ? '100%' : '0%';
                        }});
                    }});
                }})();
            """)
            await page.wait_for_timeout(150)

            viewport_el = await page.query_selector("#viewport")
            out_path = OUT_DIR / f"{SLUG}_slide{i+1:02d}.png"
            await viewport_el.screenshot(path=str(out_path))
            print(f"Exported {out_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(export_slides())