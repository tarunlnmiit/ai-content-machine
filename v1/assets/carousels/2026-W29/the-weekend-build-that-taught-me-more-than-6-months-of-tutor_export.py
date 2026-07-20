"""
Export carousel slides to 1080x1350 PNG via Playwright.
Run: python export_carousel.py
"""
from playwright.sync_api import sync_playwright
import os

HTML_PATH = "assets/carousels/2026-07-16_data_science_tech_weekend-build-taught-more-than-tutorials_carousel.html"
OUT_DIR = "assets/carousels/slides"
SLIDE_W = 420
SLIDE_H = 525
SCALE = 1080 / SLIDE_W  # 1080x1350 output
N_SLIDES = 8

os.makedirs(OUT_DIR, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(
        viewport={"width": SLIDE_W, "height": SLIDE_H},
        device_scale_factor=SCALE,
    )
    page.goto(f"file://{os.path.abspath(HTML_PATH)}")
    page.wait_for_timeout(300)

    track = page.query_selector(".carousel-track")

    for i in range(N_SLIDES):
        # bake progress-bar fill for this slide index into every slide instance
        page.evaluate(f"""
            document.querySelectorAll('.slide').forEach((slide, idx) => {{
                const segs = slide.querySelectorAll('.progress-seg .fill');
                segs.forEach((fill, segIdx) => {{
                    fill.style.width = segIdx <= {i} ? '100%' : '0%';
                }});
            }});
        """)
        page.evaluate(f"document.getElementById('track').style.transition='none';")
        page.evaluate(f"document.getElementById('track').style.transform='translateX({-i * SLIDE_W}px)';")
        page.wait_for_timeout(120)

        slide_el = page.query_selector(f".slide:nth-child({i+1})")
        slide_el.screenshot(path=f"{OUT_DIR}/slide_{i+1:02d}.png")

    browser.close()

print(f"Exported {N_SLIDES} slides to {OUT_DIR}/")