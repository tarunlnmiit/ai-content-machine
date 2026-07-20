"""
Export each carousel slide as a 1080x1350px PNG.
Usage: python export.py path/to/carousel.html
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

SLIDE_W = 420
SLIDE_H = 525
SCALE = 1080 / SLIDE_W  # 1080x1350 output at 420x525 source
OUT_DIR = Path("assets/carousels/slides")
TOTAL_SLIDES = 7

def export(html_path):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = Path(html_path).stem

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": SLIDE_W, "height": SLIDE_H},
            device_scale_factor=SCALE,
        )
        page.goto(f"file://{Path(html_path).resolve()}")

        for i in range(TOTAL_SLIDES):
            page.evaluate(f"goTo({i})")
            page.wait_for_timeout(500)  # let the 0.45s transition settle
            slide = page.query_selector(".carousel-viewport")
            out_path = OUT_DIR / f"{slug}_slide_{i+1:02d}.png"
            slide.screenshot(path=str(out_path))
            print(f"Saved {out_path}")

        browser.close()

if __name__ == "__main__":
    export(sys.argv[1])