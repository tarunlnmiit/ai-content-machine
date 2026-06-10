import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def export_carousel_slides():
    """Export Instagram carousel slides as 1080×1350px PNGs."""
    
    html_file = Path("carousel.html").resolve()
    output_dir = Path("assets/carousels/slides/2026-06-08_life_self_dev_the-simple-habit-that-changed-my-productivity")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    scale_factor = 1080 / 420
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": 420, "height": 525},
            device_scale_factor=scale_factor
        )
        
        await page.goto(f"file://{html_file}")
        await page.wait_for_selector(".carousel-track")
        
        for i in range(7):
            await page.click(f".dot[data-slide='{i}']")
            await page.wait_for_timeout(350)
            
            output_path = output_dir / f"slide_{i+1:02d}.png"
            await page.locator(".carousel-viewport").screenshot(path=str(output_path))
            print(f"✓ Exported slide {i+1}/7")
        
        await browser.close()
    
    print(f"\n✓ All slides exported to {output_dir}")


if __name__ == "__main__":
    asyncio.run(export_carousel_slides())