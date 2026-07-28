"""
Export each carousel slide as a 1080x1350 PNG for Instagram.
Targets: assets/carousels/slides/slide-01.png .. slide-08.png
Requires: playwright (pip install playwright && playwright install chromium)
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HTML_PATH = Path("carousel.html")            # save the HTML above to this path first
OUT_DIR = Path("assets/carousels/slides")
SLIDE_W = 420
SLIDE_H = 525
TOTAL_SLIDES = 8
SCALE = 1080 / SLIDE_W  # 1080x1350 output at scale factor

async def export_slides():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": SLIDE_W, "height": SLIDE_H},
            device_scale_factor=SCALE,
        )
        await page.goto(f"file://{HTML_PATH.resolve()}")

        for i in range(TOTAL_SLIDES):
            # bake progress fill for this slide index, hide the frame chrome around it
            await page.evaluate(
                """(idx) => {
                    document.querySelectorAll('.slide').forEach((s, si) => {
                        s.style.display = si === idx ? 'block' : 'none';
                        s.querySelectorAll('.progress-seg .fill').forEach((f, j) => {
                            f.style.width = j <= idx ? '100%' : '0%';
                        });
                    });
                    document.getElementById('track').style.transform = 'translateX(0px)';
                    document.getElementById('track').style.width = '420px';
                    document.querySelector('.ig-header').style.display = 'none';
                    document.querySelector('.ig-actions').style.display = 'none';
                    document.querySelector('.ig-likes').style.display = 'none';
                    document.querySelector('.ig-caption').style.display = 'none';
                    document.querySelector('.ig-frame').style.boxShadow = 'none';
                    document.querySelector('.ig-frame').style.border = 'none';
                }""",
                i,
            )
            slide = page.locator(".slide").nth(i)
            out_path = OUT_DIR / f"slide-{i + 1:02d}.png"
            await slide.screenshot(path=str(out_path))
            print(f"exported {out_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(export_slides())