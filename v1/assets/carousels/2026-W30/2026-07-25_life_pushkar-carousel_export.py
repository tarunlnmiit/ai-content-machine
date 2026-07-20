"""
Pushkar carousel — Playwright PNG export.
Exports each of the 7 slides at 1080x1350 (4:5) into assets/carousels/slides/.
"""
from playwright.sync_api import sync_playwright
import os

WEEK = "2026-W30"          # set to actual publish week
DATE = "2026-07-XX"        # set to actual publish date
NICHE = "life_self_dev"
SLUG = "pushkar-trip"

HTML_PATH = f"assets/carousels/{WEEK}/{DATE}_{NICHE}_{SLUG}_carousel.html"
OUT_DIR = f"assets/carousels/slides/{WEEK}/{DATE}_{NICHE}_{SLUG}"

SLIDE_W, SLIDE_H = 420, 525
SCALE = 1080 / SLIDE_W
TOTAL_SLIDES = 7

def export():
    os.makedirs(OUT_DIR, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": SLIDE_W, "height": SLIDE_H},
            device_scale_factor=SCALE,
        )
        page.goto(f"file://{os.path.abspath(HTML_PATH)}")

        for i in range(TOTAL_SLIDES):
            # bake this slide's progress fill (segments 0..i filled)
            page.evaluate(
                """(idx) => {
                    document.querySelectorAll('.slide').forEach((slide, sIdx) => {
                        const segs = slide.querySelectorAll('.progress-seg .fill');
                        segs.forEach((seg, segIdx) => {
                            seg.style.width = segIdx <= idx ? '100%' : '0%';
                        });
                    });
                    window.goTo(idx);
                }""",
                i,
            )
            page.wait_for_timeout(150)  # let transform transition settle
            viewport_el = page.query_selector(".carousel-viewport")
            viewport_el.screenshot(path=f"{OUT_DIR}/slide_{i+1}.png")

        browser.close()
    print(f"Exported {TOTAL_SLIDES} slides to {OUT_DIR}/")

if __name__ == "__main__":
    export()