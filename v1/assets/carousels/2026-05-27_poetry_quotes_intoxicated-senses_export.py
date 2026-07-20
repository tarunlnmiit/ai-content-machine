"""
Export carousel slides as 1080x1350 PNGs via Playwright.
Usage: python export_carousel.py path/to/carousel.html
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

SLIDE_W = 420
SLIDE_H = 525
SCALE = 1080 / SLIDE_W  # 2.5714286
TOTAL_SLIDES = 7

OUT_DIR = Path(
    "assets/carousels/slides/2026-W22/"
    "2026-05-27_poetry_quotes_intoxicated-senses"
)

def export(html_path: str):
    html_path = Path(html_path).resolve()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": SLIDE_W, "height": SLIDE_H},
            device_scale_factor=SCALE,
        )
        page.goto(f"file://{html_path}")
        page.wait_for_timeout(400)  # let fonts settle

        for i in range(TOTAL_SLIDES):
            page.evaluate(f"""() => {{
                const track = document.getElementById('track');
                track.style.transition = 'none';
                track.style.transform = 'translateX(-{i * SLIDE_W}px)';
                document.querySelectorAll('.slide').forEach((slide, idx) => {{
                    slide.querySelectorAll('.progress-seg .fill').forEach((fill, segIdx) => {{
                        fill.style.width = segIdx <= {i} ? '100%' : '0%';
                    }});
                }});
            }}""")
            page.wait_for_timeout(150)
            slide_el = page.query_selector(f".slide:nth-child({i + 1})")
            out_path = OUT_DIR / f"slide_{i + 1}.png"
            slide_el.screenshot(path=str(out_path))
            print(f"Saved {out_path}")

        browser.close()

if __name__ == "__main__":
    export(sys.argv[1] if len(sys.argv) > 1 else "carousel.html")