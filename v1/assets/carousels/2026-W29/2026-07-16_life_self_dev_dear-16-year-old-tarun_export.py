"""Export carousel slides to 1080x1350 PNGs via Playwright.

Usage: python export.py <path/to/carousel.html>
Assumes __LIFE_BG__ placeholder has already been resolved to a real asset path/data-URI.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

SLIDE_W, SLIDE_H = 420, 525
TARGET_W = 1080
SCALE = TARGET_W / SLIDE_W  # 1080/420

OUT_DIR = Path("assets/carousels/slides")


def bake_progress(page, slide_index, total):
    page.evaluate(
        """([idx, total]) => {
            const slides = document.querySelectorAll('.slide');
            const segs = slides[idx].querySelectorAll('.progress-seg .fill');
            segs.forEach((fill, i) => { fill.style.width = i <= idx ? '100%' : '0%'; });
        }""",
        [slide_index, total],
    )


def main():
    html_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("carousel.html")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": SLIDE_W, "height": SLIDE_H},
            device_scale_factor=SCALE,
        )
        page.goto(html_path.resolve().as_uri())

        slides = page.locator(".slide")
        total = slides.count()

        for i in range(total):
            bake_progress(page, i, total)
            slide = slides.nth(i)
            out_path = OUT_DIR / f"slide_{i+1:02d}.png"
            slide.screenshot(path=str(out_path))
            print(f"Saved {out_path} ({TARGET_W}x{int(SLIDE_H*SCALE)})")

        browser.close()


if __name__ == "__main__":
    main()