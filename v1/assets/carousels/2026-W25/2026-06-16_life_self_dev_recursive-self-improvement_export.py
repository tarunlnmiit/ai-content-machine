"""
Export carousel slides → 1080×1350 PNG files.

Usage:
    python assets/carousels/2026-W25/2026-06-16_life_self_dev_recursive-self-improvement_export.py
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SLUG       = "2026-06-16_life_self_dev_recursive-self-improvement"
WEEK       = "2026-W25"
HTML_FILE  = Path(f"assets/carousels/{WEEK}/{SLUG}_carousel.html")
OUT_DIR    = Path(f"assets/carousels/slides/{SLUG}")
TOTAL      = 7
SCALE      = 1080 / 420  # 2.5714…  →  420×2.57 = 1080px,  525×2.57 = 1350px


async def export() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page    = await browser.new_page(
            viewport={"width": 420, "height": 525},
            device_scale_factor=SCALE,
        )
        await page.goto(f"file://{HTML_FILE.resolve()}")
        await page.wait_for_load_state("networkidle")

        for i in range(TOTAL):
            await page.evaluate(f"goTo({i})")
            await page.wait_for_timeout(450)          # wait for CSS transition
            out = OUT_DIR / f"slide_{i + 1}.png"
            await page.locator(".carousel-viewport").screenshot(path=str(out))
            print(f"  ✓ slide_{i + 1}.png  →  {out}")

        await browser.close()

    print(f"\nDone — {TOTAL} slides at 1080×1350 px in {OUT_DIR}")


if __name__ == "__main__":
    asyncio.run(export())