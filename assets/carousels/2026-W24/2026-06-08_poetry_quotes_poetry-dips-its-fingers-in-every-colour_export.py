# Export carousel slides as PNG files
# Usage: python3 export_carousel.py

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def export_slides():
    output_dir = Path("assets/carousels/slides/2026-06-08_poetry_quotes_poetry-dips-its-fingers-in-every-colour")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    html_file = Path(__file__).parent / "carousel.html"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Load HTML
        await page.goto(f"file://{html_file.absolute()}")
        
        # Export each slide (7 total)
        for i in range(7):
            # Navigate to slide
            await page.evaluate(f"goToSlide({i})")
            await page.wait_for_timeout(300)
            
            # Screenshot carousel viewport at Instagram aspect ratio
            # 1080×1350px (scaling from 420×525px design)
            await page.screenshot(
                path=output_dir / f"slide_{i+1:02d}.png",
                clip={"x": 0, "y": 60, "width": 420, "height": 525},
                device_scale_factor=1080 / 420
            )
            
            print(f"✓ Exported slide {i+1}/7")
        
        await browser.close()
        print(f"\nAll slides exported to: {output_dir}")

if __name__ == "__main__":
    asyncio.run(export_slides())