"""
Export each carousel slide to a 1080x1350 PNG.
Requires: pip install playwright && playwright install chromium
"""
import os
from playwright.sync_api import sync_playwright

HTML_PATH = "carousel.html"  # path to the saved HTML file above
OUTPUT_DIR = "assets/carousels/slides/"
SLIDE_COUNT = 8
SLIDE_W = 420
SLIDE_H = 525
SCALE = 1080 / SLIDE_W  # 1080x1350 output at device_scale_factor

os.makedirs(OUTPUT_DIR, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(
        viewport={"width": SLIDE_W, "height": SLIDE_H},
        device_scale_factor=SCALE,
    )
    page.goto(f"file://{os.path.abspath(HTML_PATH)}")

    for i in range(SLIDE_COUNT):
        # move track to slide i
        page.evaluate(f"document.getElementById('track').style.transition='none';"
                       f"document.getElementById('track').style.transform='translateX({-i * SLIDE_W}px)';")

        # bake this slide's progress-bar fill (segments 0..i filled)
        page.evaluate(f"""
            const slide = document.querySelector('.slide[data-index="{i}"]');
            const segs = slide.querySelectorAll('.progress-seg .fill');
            segs.forEach((f, idx) => {{ f.style.width = idx <= {i} ? '100%' : '0%'; }});
        """)

        # hide IG chrome (header/dots/icons/caption) so only the slide exports
        page.evaluate("""
            document.querySelector('.ig-header').style.display='none';
            document.querySelector('.ig-dotsrow').style.display='none';
            document.querySelector('.ig-icons').style.display='none';
            document.querySelector('.ig-likes').style.display='none';
            document.querySelector('.ig-caption').style.display='none';
        """)

        slide = page.query_selector(f'.slide[data-index="{i}"]')
        slide.screenshot(path=os.path.join(OUTPUT_DIR, f"slide_{i+1:02d}.png"))

    browser.close()

print(f"Exported {SLIDE_COUNT} slides to {OUTPUT_DIR}")