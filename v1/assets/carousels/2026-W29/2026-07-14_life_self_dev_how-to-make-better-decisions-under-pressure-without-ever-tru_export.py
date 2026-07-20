"""
Export the Breath of Life carousel HTML to 1080x1350 PNG slides.
Run: python3 export_carousel.py
Requires: pip install playwright && playwright install chromium
"""
import os
from playwright.sync_api import sync_playwright

HTML_PATH = "carousel.html"  # save the HTML above to this path
OUTPUT_DIR = "assets/carousels/slides/"
SLIDE_COUNT = 8
SLIDE_WIDTH_PX = 420
SLIDE_HEIGHT_PX = 525
EXPORT_WIDTH = 1080
DEVICE_SCALE_FACTOR = EXPORT_WIDTH / SLIDE_WIDTH_PX  # 1080/420

def export_slides():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_url = f"file://{os.path.abspath(HTML_PATH)}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": SLIDE_WIDTH_PX, "height": SLIDE_HEIGHT_PX},
            device_scale_factor=DEVICE_SCALE_FACTOR,
        )
        page.goto(file_url)

        for i in range(SLIDE_COUNT):
            page.evaluate(f"goTo({i})")
            page.wait_for_timeout(200)  # allow transform transition to settle
            slide = page.locator(f'.slide[data-index="{i}"]')
            out_path = os.path.join(OUTPUT_DIR, f"slide_{i+1:02d}.png")
            slide.screenshot(path=out_path)
            print(f"Exported {out_path}")

        browser.close()

if __name__ == "__main__":
    export_slides()