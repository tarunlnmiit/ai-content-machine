"""Export the "one question" carousel slides to 1080x1350 PNGs."""
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML_PATH = Path(__file__).parent / "2026-07-16_life_self_dev_the-one-question-i-ask-before-every-big-decision_carousel.html"
OUT_DIR = Path(__file__).parent.parent.parent / "assets" / "carousels" / "slides"
SLUG = "2026-07-16_life_self_dev_the-one-question-i-ask-before-every-big-decision"
SLIDE_COUNT = 7
SLIDE_W = 420
SLIDE_H = 525
SCALE = 1080 / SLIDE_W  # 2.5714286 -> 1080x1350 output

def export():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": SLIDE_W, "height": SLIDE_H},
            device_scale_factor=SCALE,
        )
        page.goto(f"file://{HTML_PATH.resolve()}")
        viewport = page.locator("#viewport")

        for i in range(SLIDE_COUNT):
            page.evaluate(
                """(i) => {
                    const track = document.getElementById('viewport').querySelector('.carousel-track');
                    track.style.transition = 'none';
                    track.style.transform = 'translateX(-' + (i*420) + 'px)';
                    const slide = track.children[i];
                    slide.querySelectorAll('.progress-seg .fill').forEach((fill, idx) => {
                        fill.style.width = idx <= i ? '100%' : '0%';
                    });
                }""",
                i,
            )
            page.wait_for_timeout(80)
            out_path = OUT_DIR / f"{SLUG}_slide{i+1}.png"
            viewport.screenshot(path=str(out_path))
            print(f"exported {out_path}")

        browser.close()

if __name__ == "__main__":
    export()