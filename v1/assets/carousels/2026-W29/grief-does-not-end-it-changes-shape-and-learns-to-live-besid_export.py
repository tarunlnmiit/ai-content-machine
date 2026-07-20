"""
Export each slide of the Breath of Poetry grief carousel to 1080x1350 PNG.
Requires: pip install playwright && playwright install chromium
"""
import os
from playwright.sync_api import sync_playwright

SLIDE_W = 420
SLIDE_H = 525
EXPORT_W = 1080
EXPORT_H = 1350
SCALE = EXPORT_W / SLIDE_W  # 1080/420

HTML_PATH = os.path.abspath("2026-07-16_poetry_grief-does-not-end-it-changes-shape_carousel.html")
OUT_DIR = "assets/carousels/slides"
SLIDE_COUNT = 7

def export():
    os.makedirs(OUT_DIR, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": SLIDE_W, "height": SLIDE_H + 260},
            device_scale_factor=SCALE,
        )
        page.goto(f"file://{HTML_PATH}")
        track = page.locator("#track")

        for i in range(SLIDE_COUNT):
            page.evaluate(
                """(i) => {
                    const track = document.getElementById('track');
                    track.style.transition = 'none';
                    track.style.transform = `translateX(${-i * 420}px)`;
                    document.querySelectorAll('.progress-row .fill').forEach((f, idx) => {
                        f.style.width = idx <= i ? '100%' : '0%';
                    });
                }""",
                i,
            )
            viewport = page.locator(".carousel-viewport")
            viewport.screenshot(path=f"{OUT_DIR}/slide_{i+1}.png")

        browser.close()
        print(f"Exported {SLIDE_COUNT} slides to {OUT_DIR}/")

if __name__ == "__main__":
    export()