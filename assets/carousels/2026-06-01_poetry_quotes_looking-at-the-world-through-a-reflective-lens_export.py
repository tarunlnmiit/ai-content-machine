import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SLIDE_COUNT  = 7
HTML_PATH    = Path("assets/carousels/2026-06-01_poetry_quotes_waking-up-to-what-weve-built_carousel.html")
OUTPUT_DIR   = Path("assets/carousels/slides")
SCALE        = 1080 / 420   # → 1080×1350 output


async def export_slides():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": 420, "height": 525},
            device_scale_factor=SCALE,
        )

        await page.goto(f"file://{HTML_PATH.resolve()}")
        await page.wait_for_load_state("networkidle")

        vp = page.locator(".carousel-viewport")

        for i in range(SLIDE_COUNT):
            await page.evaluate(f"goTo({i})")
            await page.wait_for_timeout(600)   # let transition settle
            slug = "2026-06-01_poetry_waking-up"
            out  = OUTPUT_DIR / f"{slug}_slide_{i+1:02d}.png"
            await vp.screenshot(path=out, scale="device")
            print(f"✓ slide {i+1}/{SLIDE_COUNT} → {out}")

        await browser.close()
        print(f"\nDone. {SLIDE_COUNT} slides in {OUTPUT_DIR}/")


asyncio.run(export_slides())