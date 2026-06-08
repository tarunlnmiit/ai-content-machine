import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SLIDE_COUNT = 7
SLIDE_W = 420
SLIDE_H = 525
EXPORT_W = 1080
EXPORT_H = 1350
SCALE = EXPORT_W / SLIDE_W  # 2.5714...

HTML_FILE  = Path("assets/carousels/2026-05-21_life_self_dev_how-i-turned-my-habits-into-an-engine_carousel.html")
OUTPUT_DIR = Path("assets/carousels/slides")


async def export_slides():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": SLIDE_W, "height": SLIDE_H},
            device_scale_factor=SCALE,
        )

        await page.goto(HTML_FILE.resolve().as_uri())
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1800)  # fonts settle

        for i in range(SLIDE_COUNT):
            await page.evaluate(f"goTo({i})")
            await page.wait_for_timeout(450)  # wait for transition

            slide = page.locator(".slide").nth(i)
            out   = OUTPUT_DIR / f"slide_{i+1:02d}.png"
            await slide.screenshot(path=str(out))
            print(f"✓ {out}")

        await browser.close()
    print(f"\nExported {SLIDE_COUNT} slides → {OUTPUT_DIR}/")


asyncio.run(export_slides())