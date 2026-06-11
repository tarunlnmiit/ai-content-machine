#!/usr/bin/env python3
"""
Export each slide of the Pandas carousel as 1080x1350px PNG.
Output: assets/carousels/slides/
Usage: python export_carousel.py
"""

import asyncio
import os
from pathlib import Path

HTML_FILE = Path(__file__).parent / "pandas_carousel.html"
OUTPUT_DIR = Path("assets/carousels/slides")
SLIDE_COUNT = 7
SCALE = 1080 / 420          # ≈ 2.571
VIEWPORT_W = 420
VIEWPORT_H = 525

async def export_slides():
    from playwright.async_api import async_playwright

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    file_url = f"file://{HTML_FILE.resolve()}"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            viewport={"width": VIEWPORT_W, "height": 900},
            device_scale_factor=SCALE,
        )
        page = await context.new_page()
        await page.goto(file_url, wait_until="networkidle")
        await page.wait_for_timeout(600)          # let fonts settle

        # ── isolate just the carousel track for clean captures ──
        track = page.locator(".carousel-track")

        for i in range(SLIDE_COUNT):
            # navigate to slide i via JS
            await page.evaluate(f"""
                (function() {{
                    const track = document.getElementById('carouselTrack');
                    const dots  = document.querySelectorAll('.ig-dot');
                    track.style.transition = 'none';
                    track.style.transform  = 'translateX(-{i * VIEWPORT_W}px)';
                    dots.forEach((d, idx) => d.classList.toggle('active', idx === {i}));
                }})();
            """)
            await page.wait_for_timeout(120)

            # grab just the visible slide
            slide = page.locator(f".slide[data-index='{i}']")
            out_path = OUTPUT_DIR / f"slide_{i + 1:02d}.png"
            await slide.screenshot(path=str(out_path))
            print(f"  ✓ slide_{i + 1:02d}.png → {out_path}")

        await browser.close()
    print(f"\nDone. {SLIDE_COUNT} slides → {OUTPUT_DIR}/")

if __name__ == "__main__":
    asyncio.run(export_slides())