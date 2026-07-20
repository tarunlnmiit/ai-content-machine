"""
Export Breath of Life carousel slides to 1080x1350 PNGs.
Usage: python export_carousel.py <input.html> <output_dir>
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

SLIDE_W, SLIDE_H = 420, 525
SCALE = 1080 / SLIDE_W  # 1080x1350 output
TOTAL_SLIDES = 7

def export(html_path: str, out_dir: str):
    html_path = Path(html_path).resolve()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": 500, "height": 700},
            device_scale_factor=SCALE,
        )
        page.goto(f"file://{html_path}")
        page.wait_for_timeout(300)

        viewport = page.locator("#viewport")

        for i in range(TOTAL_SLIDES):
            # move track to slide i and bake that slide's own progress fill
            page.evaluate(
                """([i, w]) => {
                    const track = document.getElementById('track');
                    track.style.transition = 'none';
                    track.style.transform = `translateX(-${i * w}px)`;
                    const slide = track.children[i];
                    slide.querySelectorAll('.progress-seg .fill').forEach((f, idx) => {
                        f.style.width = idx <= i ? '100%' : '0%';
                    });
                }""",
                [i, SLIDE_W],
            )
            page.wait_for_timeout(120)
            viewport.screenshot(path=str(out_dir / f"slide_{i+1}.png"))

        browser.close()

if __name__ == "__main__":
    export(sys.argv[1], sys.argv[2])