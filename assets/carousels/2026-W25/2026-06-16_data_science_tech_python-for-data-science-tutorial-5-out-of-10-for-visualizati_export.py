import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SLUG = "2026-06-17_data_science_tech_python-for-data-science-tutorial-510"
HTML_FILE = Path(__file__).parent / f"{SLUG}_carousel.html"
OUT_DIR = Path(__file__).parent.parent / "slides" / SLUG
TOTAL_SLIDES = 7
SLIDE_W = 420
SCALE = 1080 / 420  # device_scale_factor → exports at 1080×1350px

async def export():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": SLIDE_W, "height": 525},
            device_scale_factor=SCALE,
        )
        await page.goto(HTML_FILE.as_uri())
        await page.wait_for_load_state("networkidle")

        for i in range(TOTAL_SLIDES):
            # Navigate to slide i
            await page.evaluate(f"goTo({i})")
            await page.wait_for_timeout(450)  # let transition settle

            # Crop to viewport only (exclude IG chrome)
            vp = await page.query_selector(".carousel-viewport")
            box = await vp.bounding_box()
            clip = {
                "x": box["x"], "y": box["y"],
                "width": box["width"], "height": box["height"],
            }
            out_path = OUT_DIR / f"slide_{i + 1}.png"
            await page.screenshot(path=str(out_path), clip=clip)
            print(f"  ✓ slide_{i + 1}.png")

        await browser.close()
    print(f"\nExported {TOTAL_SLIDES} slides → {OUT_DIR}")

if __name__ == "__main__":
    asyncio.run(export())