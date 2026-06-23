import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SLUG = "2026-06-16_poetry_quotes_you-have-gotta-dance-like-there-is-nobody-watching"
HTML_FILE  = Path(__file__).parent / f"{SLUG}_carousel.html"
OUTPUT_DIR = Path("assets/carousels/slides") / SLUG

SLIDE_COUNT = 7
SLIDE_W     = 420
SCALE       = 1080 / 420  # 2.5714…  → 1080px output


async def export():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": SLIDE_W, "height": 525},
            device_scale_factor=SCALE,
        )
        await page.goto(f"file://{HTML_FILE.resolve()}")
        await page.wait_for_load_state("networkidle")

        for i in range(SLIDE_COUNT):
            await page.evaluate(f"""() => {{
                const t = document.getElementById('track');
                t.style.transition = 'none';
                t.style.transform  = 'translateX(-{i * SLIDE_W}px)';
            }}""")
            await page.wait_for_timeout(120)

            out = OUTPUT_DIR / f"slide_{i + 1}.png"
            await page.locator(".carousel-viewport").screenshot(path=str(out))
            print(f"  ✓ slide_{i + 1}.png")

        await browser.close()

    print(f"\nDone — {SLIDE_COUNT} slides → {OUTPUT_DIR}")


if __name__ == "__main__":
    asyncio.run(export())