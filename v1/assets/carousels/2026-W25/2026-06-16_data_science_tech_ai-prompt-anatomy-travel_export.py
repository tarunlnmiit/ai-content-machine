#!/usr/bin/env python3
"""
Export carousel slides as 1080x1350px PNGs.
Usage: python export_carousel.py <path_to_html>
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

SLIDE_COUNT   = 7
SLIDE_WIDTH   = 420          # logical px
SLIDE_HEIGHT  = 525          # logical px
SCALE         = 1080 / 420   # ≈ 2.571 → output 1080×1350

async def export(html_path: str):
    src   = Path(html_path).resolve()
    slug  = src.stem  # e.g. 2026-06-16_tech_ds_ai-prompt-travel
    out   = Path("assets/carousels/slides") / slug
    out.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page    = await browser.new_page(
            viewport={"width": SLIDE_WIDTH, "height": SLIDE_HEIGHT},
            device_scale_factor=SCALE,
        )
        await page.goto(src.as_uri())
        await page.wait_for_load_state("networkidle")

        track = await page.query_selector(".carousel-track")

        for i in range(SLIDE_COUNT):
            # snap to slide i
            await page.evaluate(f"""
                (() => {{
                    const t = document.querySelector('.carousel-track');
                    t.style.transition = 'none';
                    t.style.transform  = 'translateX(-{i * SLIDE_WIDTH}px)';
                }})()
            """)
            await page.wait_for_timeout(80)

            clip = {
                "x": i * SLIDE_WIDTH,
                "y": 0,
                "width":  SLIDE_WIDTH,
                "height": SLIDE_HEIGHT,
            }
            out_file = out / f"slide_{i + 1}.png"
            await page.screenshot(path=str(out_file), clip=clip, scale="device")
            print(f"  ✓ slide_{i + 1}.png → {int(SLIDE_WIDTH * SCALE)}×{int(SLIDE_HEIGHT * SCALE)}px")

        await browser.close()
    print(f"\nExported {SLIDE_COUNT} slides → {out}/")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python export_carousel.py <carousel.html>")
        sys.exit(1)
    asyncio.run(export(sys.argv[1]))