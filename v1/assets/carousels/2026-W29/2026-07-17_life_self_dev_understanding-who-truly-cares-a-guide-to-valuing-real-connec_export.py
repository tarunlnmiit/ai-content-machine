"""Export carousel slides to 1080x1350 PNGs via Playwright."""
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

SELF = Path(__file__).resolve()
HTML_PATH = SELF.with_suffix(".html")
OUT_DIR = Path("assets/carousels/slides")
SLIDE_W, SLIDE_H = 420, 525
SCALE = 1080 / SLIDE_W

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"_export$", "", SELF.stem)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": SLIDE_W, "height": SLIDE_H},
            device_scale_factor=SCALE,
        )
        page.goto(HTML_PATH.as_uri())
        page.wait_for_timeout(400)

        slides = page.query_selector_all(".slide")
        n = len(slides)

        for i, slide in enumerate(slides):
            # bake this slide's progress-bar fill before capture
            page.evaluate(
                """(i) => {
                    document.querySelectorAll('.progress-row').forEach(row => {
                        row.querySelectorAll('.progress-seg .fill').forEach((fill, j) => {
                            fill.style.width = j <= i ? '100%' : '0%';
                        });
                    });
                }""",
                i,
            )
            out_path = OUT_DIR / f"{slug}_slide{i+1:02d}.png"
            slide.screenshot(path=str(out_path))
            print(f"saved {out_path}")

        browser.close()

if __name__ == "__main__":
    main()