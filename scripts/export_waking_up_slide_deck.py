#!/usr/bin/env python3
"""
Export "Waking Up to What We've Built" slide deck to PDF.

Pipeline:
  1. Fetch one stock image per image-slot from Pexels (Pixabay fallback)
  2. Patch image-slot src= attributes into the HTML
  3. Render each of the 6 slides at 1920×1080 via Playwright
  4. Assemble PNG frames into PDF via Pillow

Output:
  assets/slides/2026-06-01_poetry_quotes_looking-at-the-world-through-a-reflective-lens_slide_deck.pdf
"""

import asyncio
import os
import re
import shutil
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO = Path(__file__).parent.parent
load_dotenv(REPO / ".env")

HTML_SRC = REPO / "assets/slides/waking-up-slide-project/Waking Up to What Weve Built.html"
WORK_DIR = REPO / "assets/slides/waking-up-slide-project"
IMG_DIR  = WORK_DIR / "images"
OUT_PDF  = REPO / "assets/slides/2026-06-01_poetry_quotes_looking-at-the-world-through-a-reflective-lens_slide_deck.pdf"

SLOT_QUERIES: dict[str, str] = {
    "s1-mask":   "cracked porcelain white mask concrete dark",
    "s2-crowd":  "crowd blur one face sharp portrait monochrome",
    "s4-mirror": "mirror reflection dark room empty shadow",
    "s5-desk":   "desk night lamp notebook writing dark moody",
    "s6-window": "person silhouette window grey light back",
}

PEXELS_KEY  = os.getenv("PEXELS_API_KEY", "")
PIXABAY_KEY = os.getenv("PIXABAY_API_KEY", "")


def fetch_pexels(query: str, out_path: Path) -> bool:
    if not PEXELS_KEY:
        return False
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": query, "per_page": 3, "orientation": "landscape"},
            timeout=20,
        )
        r.raise_for_status()
        photos = r.json().get("photos", [])
        if not photos:
            return False
        url = photos[0]["src"]["large2x"]
        img_r = requests.get(url, timeout=30)
        img_r.raise_for_status()
        out_path.write_bytes(img_r.content)
        print(f"  ✓ Pexels  → {out_path.name}")
        return True
    except Exception as e:
        print(f"  ✗ Pexels  [{query[:30]}]: {e}")
        return False


def fetch_pixabay(query: str, out_path: Path) -> bool:
    if not PIXABAY_KEY:
        return False
    try:
        r = requests.get(
            "https://pixabay.com/api/",
            params={
                "key": PIXABAY_KEY,
                "q": query,
                "image_type": "photo",
                "orientation": "horizontal",
                "per_page": 3,
            },
            timeout=20,
        )
        r.raise_for_status()
        hits = r.json().get("hits", [])
        if not hits:
            return False
        url = hits[0].get("largeImageURL", hits[0].get("webformatURL", ""))
        if not url:
            return False
        img_r = requests.get(url, timeout=30)
        img_r.raise_for_status()
        out_path.write_bytes(img_r.content)
        print(f"  ✓ Pixabay → {out_path.name}")
        return True
    except Exception as e:
        print(f"  ✗ Pixabay [{query[:30]}]: {e}")
        return False


def fetch_images() -> dict[str, str]:
    """Return slot_id → relative URL for each successfully fetched image."""
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    result: dict[str, str] = {}
    for slot_id, query in SLOT_QUERIES.items():
        ext = ".jpg"
        out_path = IMG_DIR / f"{slot_id}{ext}"
        if out_path.exists():
            print(f"  ✓ cached  → {out_path.name}")
            result[slot_id] = f"images/{out_path.name}"
            continue
        ok = fetch_pexels(query, out_path) or fetch_pixabay(query, out_path)
        if ok:
            result[slot_id] = f"images/{out_path.name}"
        else:
            print(f"  ! no image for {slot_id} — slot will show placeholder")
    return result


def patch_html(src_path: Path, slot_images: dict[str, str]) -> Path:
    """Inject src= into each image-slot and return path to patched HTML."""
    html = src_path.read_text(encoding="utf-8")

    for slot_id, rel_url in slot_images.items():
        # Match the opening tag of the image-slot with this id
        pattern = rf'(<image-slot\s[^>]*id="{re.escape(slot_id)}"[^>]*)'
        def inject_src(m: re.Match) -> str:
            tag = m.group(1)
            if "src=" not in tag:
                tag = tag.rstrip() + f' src="{rel_url}"'
            return tag
        html = re.sub(pattern, inject_src, html)

    patched = WORK_DIR / "patched.html"
    patched.write_text(html, encoding="utf-8")
    return patched


async def render_slides(html_path: Path, out_dir: Path) -> list[Path]:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        sys.exit("Playwright not installed: pip install playwright && playwright install chromium")

    out_dir.mkdir(parents=True, exist_ok=True)
    pngs: list[Path] = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.goto(html_path.as_uri(), wait_until="networkidle")

        # Wait for fonts
        await page.wait_for_timeout(1200)

        # Inject show-frame helper (works with the deck's own show() internals)
        await page.evaluate("""() => {
            window.__gotoSlide = function(n) {
                const canvas = document.getElementById('canvas');
                const slides = Array.from(canvas.querySelectorAll('section'));
                slides.forEach((s, i) => {
                    if (i === n) s.setAttribute('data-active', '');
                    else s.removeAttribute('data-active');
                });
                // force opacity immediately (skip transition for screenshots)
                slides.forEach((s, i) => {
                    s.style.transition = 'none';
                    s.style.opacity = i === n ? '1' : '0';
                    s.style.visibility = i === n ? 'visible' : 'hidden';
                });
            };
        }""")

        n_slides = await page.evaluate("document.getElementById('canvas').querySelectorAll('section').length")
        print(f"  Found {n_slides} slides")

        for i in range(n_slides):
            await page.evaluate(f"window.__gotoSlide({i})")
            await page.wait_for_timeout(400)
            out_path = out_dir / f"slide_{i+1:02d}.png"
            await page.screenshot(path=str(out_path), full_page=False)
            pngs.append(out_path)
            print(f"  ✓ slide {i+1}/{n_slides} → {out_path.name}")

        await browser.close()

    return pngs


def assemble_pdf(pngs: list[Path], pdf_path: Path) -> None:
    try:
        from reportlab.lib.pagesizes import landscape
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas as rl_canvas
    except ImportError:
        sys.exit("reportlab not installed: pip install reportlab")

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    # 1920×1080 at 72 dpi = 1920×1080 pts → scale to fit A-landscape-ish page
    W, H = 1920, 1080
    c = rl_canvas.Canvas(str(pdf_path), pagesize=(W, H))
    for png in pngs:
        c.setPageSize((W, H))
        c.drawImage(str(png), 0, 0, width=W, height=H)
        c.showPage()
    c.save()
    print(f"\n  📄 {pdf_path.name} ({len(pngs)} pages, {pdf_path.stat().st_size // 1024}KB)")


def main() -> None:
    print("1/4  Fetching images...")
    slot_images = fetch_images()

    print("\n2/4  Patching HTML...")
    patched = patch_html(HTML_SRC, slot_images)
    print(f"  → {patched.name}")

    print("\n3/4  Rendering slides...")
    png_dir = WORK_DIR / "frames"
    pngs = asyncio.run(render_slides(patched, png_dir))

    print("\n4/4  Assembling PDF...")
    assemble_pdf(pngs, OUT_PDF)

    print(f"\n✅  Done → {OUT_PDF}")


if __name__ == "__main__":
    main()
