#!/usr/bin/env python3
"""
Fix <image-slot> placeholders in slide HTML files.

For each HTML with empty image-slots (no src=):
  1. Extract placeholder text as Pexels search query
  2. Download image → local dir
  3. Patch src= into HTML
  4. Re-export: PDF for slides, MP4 for story

Targets:
  - intoxicated-senses_slides.html → PDF
  - mental-health_slides.html      → PDF
  - waking-up/Waking Up...html     → patched.html → MP4
"""

import asyncio
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO = Path(__file__).parent.parent
load_dotenv(REPO / ".env")

PEXELS_KEY  = os.getenv("PEXELS_API_KEY", "")
PIXABAY_KEY = os.getenv("PIXABAY_API_KEY", "")

SLIDES_DIR  = REPO / "assets" / "slides"
STORIES_DIR = REPO / "assets" / "stories"

TARGETS = [
    {
        "name": "intoxicated-senses",
        "html": SLIDES_DIR / "2026-05-27_poetry_quotes_intoxicated-senses_slides.html",
        "img_dir": SLIDES_DIR / "photos" / "intoxicated-senses",
        "out_pdf": SLIDES_DIR / "2026-05-27_poetry_quotes_intoxicated-senses_slides.pdf",
        "canvas": "#canvas",
        "type": "pdf",
    },
    {
        "name": "mental-health",
        "html": SLIDES_DIR / "2026-05-26_life_self_dev_mental-health-openness-and-breaking-stigmas_slides.html",
        "img_dir": SLIDES_DIR / "photos" / "mental-health",
        "out_pdf": SLIDES_DIR / "2026-05-26_life_self_dev_mental-health-openness-and-breaking-stigmas_slides.pdf",
        "canvas": "deck-stage",
        "type": "pdf",
    },
    {
        "name": "reflective-lens (story)",
        "html": SLIDES_DIR / "waking-up-slide-project" / "Waking Up to What Weve Built.html",
        "img_dir": SLIDES_DIR / "waking-up-slide-project" / "images",
        "patched": SLIDES_DIR / "waking-up-slide-project" / "patched.html",
        "out_mp4": STORIES_DIR / "2026-06-01_poetry_quotes_looking-at-the-world-through-a-reflective-lens.mp4",
        "slug": "2026-06-01_poetry_quotes_looking-at-the-world-through-a-reflective-lens",
        "type": "mp4",
    },
]

# ── Image fetching ─────────────────────────────────────────────────────────

def _fetch_pexels(query: str, out: Path) -> bool:
    if not PEXELS_KEY:
        return False
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": query[:80], "per_page": 3, "orientation": "landscape"},
            timeout=20,
        )
        r.raise_for_status()
        photos = r.json().get("photos", [])
        if not photos:
            return False
        url = photos[0]["src"]["large2x"]
        img = requests.get(url, timeout=30)
        img.raise_for_status()
        out.write_bytes(img.content)
        print(f"    ✓ Pexels → {out.name}")
        return True
    except Exception as e:
        print(f"    ✗ Pexels [{query[:30]}]: {e}")
        return False


def _fetch_pixabay(query: str, out: Path) -> bool:
    if not PIXABAY_KEY:
        return False
    try:
        r = requests.get(
            "https://pixabay.com/api/",
            params={"key": PIXABAY_KEY, "q": query[:80], "image_type": "photo",
                    "orientation": "horizontal", "per_page": 3},
            timeout=20,
        )
        r.raise_for_status()
        hits = r.json().get("hits", [])
        if not hits:
            return False
        url = hits[0].get("largeImageURL", hits[0].get("webformatURL", ""))
        if not url:
            return False
        img = requests.get(url, timeout=30)
        img.raise_for_status()
        out.write_bytes(img.content)
        print(f"    ✓ Pixabay → {out.name}")
        return True
    except Exception as e:
        print(f"    ✗ Pixabay [{query[:30]}]: {e}")
        return False


# ── HTML parsing & patching ────────────────────────────────────────────────

SLOT_RE = re.compile(
    r'<image-slot\s([^>]*?)>',
    re.DOTALL,
)
ID_RE          = re.compile(r'\bid="([^"]+)"')
PLACEHOLDER_RE = re.compile(r'\bplaceholder="([^"]+)"')
SRC_RE         = re.compile(r'\bsrc="[^"]*"')


def parse_empty_slots(html: str) -> list[tuple[str, str]]:
    """Return list of (slot_id, placeholder_text) for slots without src=."""
    slots = []
    for m in SLOT_RE.finditer(html):
        attrs = m.group(1)
        if "src=" in attrs:
            continue
        id_m = ID_RE.search(attrs)
        ph_m = PLACEHOLDER_RE.search(attrs)
        if id_m and ph_m:
            slots.append((id_m.group(1), ph_m.group(1)))
    return slots


def fetch_slot_images(slots: list[tuple[str, str]], img_dir: Path) -> dict[str, Path]:
    """Fetch image for each slot; return slot_id → local Path."""
    img_dir.mkdir(parents=True, exist_ok=True)
    result: dict[str, Path] = {}
    for slot_id, placeholder in slots:
        # Use first sentence / phrase as search query (trim at · or comma)
        query = re.split(r'[·,]', placeholder)[0].strip()[:80]
        ext = ".jpg"
        out = img_dir / f"{slot_id}{ext}"
        if out.exists():
            print(f"    ✓ cached → {out.name}")
            result[slot_id] = out
            continue
        ok = _fetch_pexels(query, out) or _fetch_pixabay(query, out)
        if ok:
            result[slot_id] = out
        else:
            print(f"    ! no image for {slot_id} ({query[:40]})")
    return result


def patch_html(html: str, slot_images: dict[str, Path], img_dir: Path,
               html_dir: Path) -> str:
    """Inject src= into image-slot tags."""
    def inject(m: re.Match) -> str:
        attrs = m.group(1)
        id_m = ID_RE.search(attrs)
        if not id_m:
            return m.group(0)
        slot_id = id_m.group(1)
        if slot_id not in slot_images or "src=" in attrs:
            return m.group(0)
        rel = slot_images[slot_id].relative_to(html_dir)
        return f'<image-slot {attrs.rstrip()} src="{rel}">'
    return SLOT_RE.sub(inject, html)


# ── PDF rendering ──────────────────────────────────────────────────────────

async def render_pdf(html_path: Path, out_pdf: Path, canvas_sel: str) -> None:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        sys.exit("pip install playwright && playwright install chromium")

    print(f"  Rendering slides from {html_path.name}...")
    pngs: list[Path] = []
    tmp_dir = html_path.parent / "_tmp_slides"
    tmp_dir.mkdir(exist_ok=True)

    is_deck_stage = "deck-stage" in canvas_sel

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.goto(html_path.as_uri(), wait_until="networkidle")
        await page.wait_for_timeout(1500)

        if is_deck_stage:
            # Hide thumbnail rail and tapzone arrows
            await page.evaluate("""() => {
                const st = document.querySelector('deck-stage');
                if (!st) return;
                st.setAttribute('no-rail', '');
                // Inject into shadow DOM to hide tapzones & overlay
                if (st.shadowRoot) {
                    const s = document.createElement('style');
                    s.textContent = '.tapzones,.overlay,.rail,.rail-resize{display:none!important}';
                    st.shadowRoot.appendChild(s);
                }
            }""")
            await page.wait_for_timeout(200)

            # deck-stage: navigate() method
            n = await page.evaluate("""() => {
                const st = document.querySelector('deck-stage');
                return st ? st.length : 0;
            }""")
            print(f"    {n} slides (deck-stage)")
            for i in range(n):
                await page.evaluate(f"""() => {{
                    const st = document.querySelector('deck-stage');
                    if (st && st.goTo) st.goTo({i});
                }}""")
                await page.wait_for_timeout(600)
                out = tmp_dir / f"slide_{i+1:02d}.png"
                await page.screenshot(path=str(out), full_page=False)
                pngs.append(out)
                print(f"    ✓ slide {i+1}/{n}")
        else:
            # #canvas sections approach
            await page.evaluate("""() => {
                window.__gotoSlide = function(n) {
                    const secs = Array.from(
                        document.querySelectorAll('#canvas section')
                    );
                    secs.forEach((s, i) => {
                        s.style.transition = 'none';
                        s.style.opacity = i === n ? '1' : '0';
                        s.style.visibility = i === n ? 'visible' : 'hidden';
                        if (i === n) s.setAttribute('data-active', '');
                        else s.removeAttribute('data-active');
                    });
                };
            }""")
            n = await page.evaluate(
                "document.querySelectorAll('#canvas section').length"
            )
            print(f"    {n} slides (#canvas)")
            for i in range(n):
                await page.evaluate(f"window.__gotoSlide({i})")
                await page.wait_for_timeout(500)
                out = tmp_dir / f"slide_{i+1:02d}.png"
                await page.screenshot(path=str(out), full_page=False)
                pngs.append(out)
                print(f"    ✓ slide {i+1}/{n}")

        await browser.close()

    assemble_pdf(pngs, out_pdf)
    shutil.rmtree(tmp_dir)


def assemble_pdf(pngs: list[Path], pdf_path: Path) -> None:
    try:
        from reportlab.pdfgen import canvas as rl_canvas
    except ImportError:
        sys.exit("pip install reportlab")

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    W, H = 1920, 1080
    c = rl_canvas.Canvas(str(pdf_path), pagesize=(W, H))
    for png in pngs:
        c.setPageSize((W, H))
        c.drawImage(str(png), 0, 0, width=W, height=H)
        c.showPage()
    c.save()
    size_kb = pdf_path.stat().st_size // 1024
    print(f"  📄 {pdf_path.name} ({len(pngs)} pages, {size_kb}KB)")


# ── MP4 export ─────────────────────────────────────────────────────────────

async def render_slides_mp4(html_path: Path, out_mp4: Path) -> None:
    """Render slide deck as PNG frames then encode to MP4 via ffmpeg."""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        sys.exit("pip install playwright && playwright install chromium")

    tmp_dir = html_path.parent / "_tmp_mp4_frames"
    tmp_dir.mkdir(exist_ok=True)
    pngs: list[Path] = []

    print(f"  Rendering slides for MP4 from {html_path.name}...")
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        # Story format: portrait 1080×1920
        page = await browser.new_page(viewport={"width": 1080, "height": 1920})
        await page.goto(html_path.as_uri(), wait_until="networkidle")
        await page.wait_for_timeout(1500)

        # Inject navigator for #canvas sections
        await page.evaluate("""() => {
            window.__gotoSlide = function(n) {
                const secs = Array.from(
                    document.querySelectorAll('#canvas section')
                );
                secs.forEach((s, i) => {
                    s.style.transition = 'none';
                    s.style.opacity = i === n ? '1' : '0';
                    s.style.visibility = i === n ? 'visible' : 'hidden';
                    if (i === n) s.setAttribute('data-active', '');
                    else s.removeAttribute('data-active');
                });
            };
        }""")

        n = await page.evaluate(
            "document.querySelectorAll('#canvas section').length"
        )
        print(f"    {n} slides")

        for i in range(n):
            await page.evaluate(f"window.__gotoSlide({i})")
            await page.wait_for_timeout(600)
            out = tmp_dir / f"slide_{i+1:02d}.png"
            await page.screenshot(path=str(out), full_page=False)
            pngs.append(out)
            print(f"    ✓ slide {i+1}/{n}")

        await browser.close()

    # Copy to stories dir as story_slide_NN.png
    slug = out_mp4.stem
    stories_dir = out_mp4.parent
    for idx, png in enumerate(pngs):
        dest = stories_dir / f"{slug}_story_slide_{idx+1:02d}.png"
        shutil.copy(png, dest)

    # Assemble MP4: each slide shown for 3.7s
    secs_per_slide = 3.7
    _encode_slideshow_mp4(pngs, out_mp4, secs_per_slide)
    shutil.rmtree(tmp_dir)


def _encode_slideshow_mp4(pngs: list[Path], out_mp4: Path, secs_per_slide: float) -> None:
    """Use ffmpeg to assemble PNG stills into MP4."""
    import tempfile

    # Write concat list
    tmp = Path(tempfile.mktemp(suffix=".txt"))
    lines = []
    for png in pngs:
        lines.append(f"file '{png}'")
        lines.append(f"duration {secs_per_slide}")
    # Add last frame again (ffmpeg concat demuxer needs trailing entry)
    lines.append(f"file '{pngs[-1]}'")
    tmp.write_text("\n".join(lines))

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(tmp),
        "-vf", "fps=30,format=yuv420p",
        "-c:v", "h264_videotoolbox",
        "-b:v", "6M",
        str(out_mp4),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    tmp.unlink(missing_ok=True)

    if result.returncode != 0:
        # Fallback encoder
        cmd[cmd.index("h264_videotoolbox")] = "libx264"
        cmd[cmd.index("-b:v") + 1] = "4M"
        result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and out_mp4.exists():
        mb = out_mp4.stat().st_size / (1024 * 1024)
        print(f"  ✓ {out_mp4.name} ({mb:.1f}MB)")
    else:
        print(f"  ✗ ffmpeg failed: {result.stderr[-300:]}")


# ── Main ───────────────────────────────────────────────────────────────────

def main() -> None:
    for target in TARGETS:
        name = target["name"]
        html_path: Path = target["html"]
        img_dir: Path = target["img_dir"]
        print(f"\n{'='*60}")
        print(f"  {name}")
        print(f"{'='*60}")

        html = html_path.read_text(encoding="utf-8")
        slots = parse_empty_slots(html)
        print(f"  {len(slots)} empty image-slot(s) found")
        if not slots:
            print("  Nothing to fetch.")
        else:
            for sid, ph in slots:
                print(f"    #{sid}: {ph[:60]}...")

            print(f"\n  Fetching images...")
            slot_images = fetch_slot_images(slots, img_dir)

            print(f"\n  Patching HTML...")
            patched_html_str = patch_html(html, slot_images, img_dir, html_path.parent)
            out_html = target.get("patched", html_path)
            out_html.write_text(patched_html_str, encoding="utf-8")
            print(f"  → {out_html.name}")

        if target["type"] == "pdf":
            print(f"\n  Exporting PDF...")
            asyncio.run(render_pdf(
                out_html if slots else html_path,
                target["out_pdf"],
                target["canvas"],
            ))

        elif target["type"] == "mp4":
            patched = target.get("patched", html_path)
            if not slots:
                patched = html_path
            print(f"\n  Exporting MP4...")
            asyncio.run(render_slides_mp4(patched, target["out_mp4"]))

    print("\n\n✅ All done.")


if __name__ == "__main__":
    main()
