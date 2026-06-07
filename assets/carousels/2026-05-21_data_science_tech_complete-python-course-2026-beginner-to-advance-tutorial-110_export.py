import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HTML_PATH = Path(__file__).parent.parent / "assets/slides/2026-05-21_data_science_tech_complete-python-course-2026-beginner-to-advance-tutorial-110.html"
OUT_DIR   = Path(__file__).parent.parent / "assets/carousels/slides"
SLUG      = "2026-05-21_data_science_tech_complete-python-course-2026-beginner-to-advance-tutorial-110"

SLIDE_W   = 420
SLIDE_H   = 525
SCALE     = 1080 / 420   # ≈ 2.571  →  1080×1350 output
TOTAL     = 7

async def export_slides():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    url = HTML_PATH.resolve().as_uri()

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": SLIDE_W, "height": SLIDE_H},
            device_scale_factor=SCALE,
        )
        await page.goto(url, wait_until="networkidle")
        # Let fonts settle
        await page.wait_for_timeout(800)

        for i in range(TOTAL):
            # Navigate carousel via keyboard
            if i > 0:
                await page.keyboard.press("ArrowRight")
                await page.wait_for_timeout(450)

            out_path = OUT_DIR / f"{SLUG}_slide_{i+1:02d}.png"
            # Clip to carousel area only (skip IG phone chrome)
            carousel = page.locator("#carouselWrap")
            await carousel.screenshot(path=str(out_path))
            print(f"  ✓ slide {i+1:02d} → {out_path.name}")

        await browser.close()
    print(f"\nExported {TOTAL} slides to {OUT_DIR}")

if __name__ == "__main__":
    asyncio.run(export_slides())