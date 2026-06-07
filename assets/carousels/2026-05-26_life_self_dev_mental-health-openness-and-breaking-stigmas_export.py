"""
Export carousel slides as 1080×1350px PNGs.
Usage: python export_carousel_slides.py
Output: assets/carousels/slides/slide_01.png … slide_07.png
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HTML_FILE   = Path("assets/carousels/the-lie-we-inherited-about-strength.html").resolve()
OUT_DIR     = Path("assets/carousels/slides")
SLIDE_COUNT = 7
SLIDE_W     = 420
SLIDE_H     = 525
IG_HEADER_H = 54          # px — header height at 1× scale
SCALE       = 1080 / 420  # ≈ 2.571  →  1080×1350 output


async def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(
            viewport={"width": SLIDE_W, "height": SLIDE_H + IG_HEADER_H + 120},
            device_scale_factor=SCALE,
        )
        await page.goto(f"file://{HTML_FILE}")
        await page.wait_for_load_state("networkidle")

        for i in range(SLIDE_COUNT):
            await page.evaluate(f"goTo({i})")
            await page.wait_for_timeout(450)  # let transition settle

            clip = {
                "x": 0,
                "y": IG_HEADER_H,   # skip IG chrome header
                "width": SLIDE_W,
                "height": SLIDE_H,
            }
            out = OUT_DIR / f"slide_{i+1:02d}.png"
            await page.screenshot(path=str(out), clip=clip)
            print(f"✓  slide_{i+1:02d}.png  ({int(SLIDE_W*SCALE)}×{int(SLIDE_H*SCALE)}px)")

        await browser.close()

    print(f"\n✅  {SLIDE_COUNT} slides → {OUT_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())