import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SLUG = "2026-06-15_life_self_dev_unnecessary-repeated-success-advice"
WEEK = "2026-W25"
TOTAL_SLIDES = 7
SCALE = 1080 / 420  # → 1080×1350px output


async def export_carousel_slides(
    html_file: str,
    output_dir: str = f"assets/carousels/slides/{WEEK}/{SLUG}",
) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(device_scale_factor=SCALE)

        html_path = Path(html_file).resolve()
        await page.goto(f"file://{html_path}")
        await page.wait_for_load_state("networkidle")

        for n in range(1, TOTAL_SLIDES + 1):
            await page.evaluate(f"""
                const track = document.querySelector('.carousel-track');
                track.style.transition = 'none';
                track.style.transform = 'translateX(-{(n - 1) * 420}px)';
            """)
            await page.wait_for_timeout(80)

            await page.screenshot(
                path=str(out / f"slide_{n:02d}.png"),
                clip={"x": 0, "y": 48, "width": 420, "height": 525},
            )
            print(f"✓ slide {n}/{TOTAL_SLIDES}")

        await browser.close()
    print(f"\n✓ all slides → {out}")


if __name__ == "__main__":
    import sys
    html = sys.argv[1] if len(sys.argv) > 1 else f"assets/carousels/{WEEK}/{SLUG}_carousel.html"
    asyncio.run(export_carousel_slides(html))