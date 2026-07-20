import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SLUG = "your-overloaded-self-improvement-schedule-is-slowly-making-y"
HTML_PATH = Path(f"assets/carousels/{SLUG}_carousel.html")
OUT_DIR = Path(f"assets/carousels/slides/{SLUG}")
SLIDE_COUNT = 8
VIEWPORT_W = 420
VIEWPORT_H = 525
SCALE = 1080 / VIEWPORT_W  # 1080x1350 export


async def export_slides():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": VIEWPORT_W + 40, "height": VIEWPORT_H + 200},
            device_scale_factor=SCALE,
        )
        await page.goto(f"file://{HTML_PATH.resolve()}")
        await page.wait_for_timeout(300)

        viewport_el = page.locator("#viewport")

        for i in range(SLIDE_COUNT):
            await page.evaluate(f"""() => {{
                current = {i};
                render();
            }}""")
            await page.wait_for_timeout(250)
            out_path = OUT_DIR / f"slide_{i+1:02d}.png"
            await viewport_el.screenshot(path=str(out_path))
            print(f"Exported {out_path}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(export_slides())