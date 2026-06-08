import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HTML_PATH = Path("assets/carousels/safe_and_alive_carousel.html").resolve()
OUTPUT_DIR = Path("assets/carousels/slides")
SLIDE_COUNT = 7
SLIDE_WIDTH_PX = 420
VIEWPORT_HEIGHT = 525
SCALE = 1080 / 420  # ≈ 2.571 → 1080×1350 output

async def export_slides():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": SLIDE_WIDTH_PX, "height": VIEWPORT_HEIGHT},
            device_scale_factor=SCALE,
        )
        await page.goto(f"file://{HTML_PATH}")
        await page.wait_for_load_state("networkidle")

        # Find carousel track
        track = await page.query_selector(".carousel-track")
        if not track:
            # fallback selectors
            for sel in [".slides-track", ".track"]:
                track = await page.query_selector(sel)
                if track:
                    break
        if not track:
            print("ERROR: carousel-track not found")
            await browser.close()
            return

        for i in range(SLIDE_COUNT):
            # Translate to slide i
            await page.evaluate(
                f"document.querySelector('.carousel-track').style.transform = 'translateX(-{i * SLIDE_WIDTH_PX}px)'"
            )
            await page.wait_for_timeout(120)

            # Screenshot the viewport (ig-frame clip)
            ig_frame = await page.query_selector(".ig-frame")
            if ig_frame:
                box = await ig_frame.bounding_box()
                clip = {
                    "x": box["x"],
                    "y": box["y"] + 54,  # skip IG header (≈54px)
                    "width": SLIDE_WIDTH_PX,
                    "height": VIEWPORT_HEIGHT,
                }
            else:
                clip = {"x": 0, "y": 54, "width": SLIDE_WIDTH_PX, "height": VIEWPORT_HEIGHT}

            out_path = OUTPUT_DIR / f"safe_and_alive_slide_{i+1:02d}.png"
            await page.screenshot(path=str(out_path), clip=clip)
            print(f"  Exported slide {i+1}/{SLIDE_COUNT} → {out_path}")

        await browser.close()
        print(f"\nDone. {SLIDE_COUNT} slides in {OUTPUT_DIR}/")

asyncio.run(export_slides())