import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def export_carousel_slides(html_file: str, output_dir: str = "assets/carousels/slides/"):
    """
    Export each carousel slide as 1080×1350px PNG.
    
    Args:
        html_file: Path to the carousel HTML file
        output_dir: Directory to save PNG slides
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(device_scale_factor=1080 / 420)
        
        # Load HTML
        html_path = Path(html_file).resolve()
        await page.goto(f"file://{html_path}")
        
        # Export 7 slides
        for slide_num in range(1, 8):
            # Navigate to slide
            await page.evaluate(f"""
                const track = document.querySelector('.carousel-track');
                track.style.transition = 'none';
                track.style.transform = 'translateX(-{(slide_num - 1) * 420}px)';
            """)
            
            # Screenshot viewport only
            await page.screenshot(
                path=f"{output_dir}slide_{slide_num:02d}.png",
                clip={
                    "x": 0,
                    "y": 48,  # Below Instagram header
                    "width": 420,
                    "height": 525  # Carousel viewport height
                }
            )
            
            print(f"✓ Exported slide {slide_num}/7")
        
        await browser.close()
        print(f"\n✓ All slides exported to {output_dir}")

if __name__ == "__main__":
    asyncio.run(export_carousel_slides("carousel.html"))