"""
Export script — Tutorial 05 Data Viz carousel
Outputs 1080×1350px PNGs per slide (device_scale_factor = 1080/420)
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

HTML_FILE = Path(__file__).parent / "2026-06-15_data_science_tech_python-for-data-science-tutorial-510_carousel.html"
OUT_DIR   = Path("assets/carousels/slides/2026-W24/2026-06-15_data_science_tech_python-for-data-science-tutorial-510")
SCALE     = 1080 / 420      # ≈ 2.5714 → gives 1080×1350 at 420×525 viewport
TOTAL     = 7

async def export():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page    = await browser.new_page(
            viewport            = {"width": 420, "height": 525},
            device_scale_factor = SCALE,
        )

        await page.goto(HTML_FILE.resolve().as_uri())
        await page.wait_for_load_state("networkidle")
        # Let Google Fonts settle
        await page.wait_for_timeout(1500)

        track   = page.locator(".carousel-track")
        vp      = page.locator(".carousel-viewport")

        for i in range(TOTAL):
            # Snap to slide via JS (skips transition delay)
            await page.evaluate(
                f"""
                const t = document.querySelector('.carousel-track');
                t.style.transition = 'none';
                t.style.transform  = 'translateX(-{i * 420}px)';
                // sync dots
                document.querySelectorAll('#dots .ig-dot').forEach((d, idx) =>
                    d.classList.toggle('active', idx === {i}));
                """
            )
            await page.wait_for_timeout(80)

            out = OUT_DIR / f"slide_{i + 1}.png"
            await vp.screenshot(path=str(out))
            print(f"  ✓ slide_{i + 1}.png  →  {out}")

        await browser.close()
    print(f"\nDone — {TOTAL} slides in {OUT_DIR}")

if __name__ == "__main__":
    asyncio.run(export())