#!/usr/bin/env python3
"""
Export "Waking Up to What We've Built" story HTML to 7 PNGs + MP4.

Uses the new HTML's window.__seek / window.__frames API (not section-based).

Steps:
  1. Map existing images to the new slot IDs
  2. Fetch any missing images (story-hand) via Pexels/Pixabay
  3. Patch src= into a copy of the HTML
  4. Export 7 PNGs (one per frame at 1.5s into each) + MP4 (30fps full animation)
"""

import asyncio
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO = Path(__file__).parent.parent
load_dotenv(REPO / ".env")

PEXELS_KEY  = os.getenv("PEXELS_API_KEY", "")
PIXABAY_KEY = os.getenv("PIXABAY_API_KEY", "")

SLUG = "2026-06-01_poetry_quotes_looking-at-the-world-through-a-reflective-lens"

HTML_SRC  = REPO / "assets/slides/waking-up-slide-project/Waking Up to What We've Built.html"
IMG_DIR   = REPO / "assets/slides/waking-up-slide-project/images"
PATCHED   = REPO / "assets/slides/waking-up-slide-project/patched_v2.html"
OUT_DIR   = REPO / "assets/stories"
OUT_MP4   = OUT_DIR / f"{SLUG}.mp4"
OUT_PNG   = lambda i: OUT_DIR / f"{SLUG}_story_slide_{i:02d}.png"

# Map new slot IDs → existing images where available
EXISTING_MAP = {
    "story-crowd":       IMG_DIR / "s2-crowd.jpg",
    "story-mask":        IMG_DIR / "s1-mask.jpg",
    "story-mirror-fig":  IMG_DIR / "s4-mirror.jpg",
    "story-mirror-empty": IMG_DIR / "s4-mirror.jpg",
    "story-window":      IMG_DIR / "s6-window.jpg",
}

# Slots that need fresh Pexels fetch
FETCH_MAP = {
    "story-hand": "open palm hand extended offering dark background",
}


# ── Image fetch ───────────────────────────────────────────────────────────────

def _fetch(query: str, out: Path) -> bool:
    if out.exists():
        print(f"  cached  {out.name}")
        return True
    if PEXELS_KEY:
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": query[:80], "per_page": 3, "orientation": "portrait"},
                timeout=20,
            )
            r.raise_for_status()
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                img = requests.get(url, timeout=30)
                img.raise_for_status()
                out.write_bytes(img.content)
                print(f"  Pexels  {out.name}")
                return True
        except Exception as e:
            print(f"  Pexels error: {e}")
    if PIXABAY_KEY:
        try:
            r = requests.get(
                "https://pixabay.com/api/",
                params={"key": PIXABAY_KEY, "q": query[:80], "image_type": "photo",
                        "per_page": 3, "safesearch": "true"},
                timeout=20,
            )
            r.raise_for_status()
            hits = r.json().get("hits", [])
            if hits:
                url = hits[0].get("largeImageURL", hits[0].get("webformatURL", ""))
                img = requests.get(url, timeout=30)
                img.raise_for_status()
                out.write_bytes(img.content)
                print(f"  Pixabay {out.name}")
                return True
        except Exception as e:
            print(f"  Pixabay error: {e}")
    return False


# ── HTML patching ─────────────────────────────────────────────────────────────

SLOT_RE = re.compile(r'<image-slot\s([^>]*?)>', re.DOTALL)
ID_RE   = re.compile(r'\bid="([^"]+)"')


def patch_html(html: str, slot_images: dict[str, Path], html_dir: Path) -> str:
    def inject(m: re.Match) -> str:
        attrs = m.group(1)
        id_m = ID_RE.search(attrs)
        if not id_m:
            return m.group(0)
        sid = id_m.group(1)
        if sid not in slot_images or "src=" in attrs:
            return m.group(0)
        rel = slot_images[sid].relative_to(html_dir)
        return f'<image-slot {attrs.rstrip()} src="{rel}">'
    return SLOT_RE.sub(inject, html)


# ── Playwright export ─────────────────────────────────────────────────────────

async def export_story(patched_html: Path) -> None:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        sys.exit("pip install playwright && playwright install chromium")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp_dir = Path(tempfile.mkdtemp())
    frames_dir = tmp_dir / "frames"
    frames_dir.mkdir()

    fps = 30

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        # Viewport taller than canvas so scale=1 exactly (1080 × 1964 → scale = min(1, 1920/1920) = 1)
        page = await browser.new_page(viewport={"width": 1080, "height": 1964})
        await page.goto(patched_html.as_uri(), wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Read timeline from page
        meta = await page.evaluate("""() => ({
            total: window.__total,
            frames: window.__frames
        })""")
        total = float(meta["total"])
        story_frames = meta["frames"]
        print(f"  Timeline: {total:.1f}s, {len(story_frames)} frames")

        # ── PNG stills: 1.5s into each frame (text fully faded in) ──
        print("  Capturing PNG stills...")
        for i, f in enumerate(story_frames):
            seek_t = float(f["start"]) + 1.5
            seek_t = min(seek_t, float(f["start"]) + float(f["hold"]) - 0.2)
            await page.evaluate(f"window.__seek({seek_t})")
            await page.wait_for_timeout(200)
            shot = await page.locator("#canvas").screenshot()
            dest = OUT_PNG(i + 1)
            dest.write_bytes(shot)
            print(f"    ✓ slide {i+1}: {dest.name}")

        # ── MP4: full animation at fps ──
        total_frames = int(total * fps)
        print(f"  Rendering {total_frames} frames for MP4 ({total:.1f}s @ {fps}fps)...")

        for fi in range(total_frames):
            t = fi / fps
            await page.evaluate(f"window.__seek({t})")
            if fi % 5 == 0:
                await page.wait_for_timeout(30)
            frame_path = frames_dir / f"frame_{fi:06d}.png"
            shot = await page.locator("#canvas").screenshot()
            frame_path.write_bytes(shot)
            if fi % (fps * 5) == 0:
                print(f"    {int(t)}s / {int(total)}s")

        await browser.close()

    # Encode MP4
    print(f"  Encoding MP4...")
    _encode_mp4(frames_dir, OUT_MP4, fps, total)
    shutil.rmtree(tmp_dir)


def _encode_mp4(frames_dir: Path, out: Path, fps: int, duration: float) -> None:
    # Try h264_videotoolbox first (macOS native), fall back to libx264
    for encoder, quality in [
        ("h264_videotoolbox", ["-b:v", "8M"]),
        ("libx264",           ["-preset", "fast", "-crf", "23"]),
    ]:
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", str(frames_dir / "frame_%06d.png"),
            "-c:v", encoder, *quality,
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            str(out),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            mb = out.stat().st_size / (1024 * 1024)
            print(f"  ✓ {out.name} ({mb:.1f}MB, encoder={encoder})")
            return
        print(f"  encoder {encoder} failed, trying next...")
    print(f"  ✗ all encoders failed: {result.stderr[-200:]}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Fetch missing images
    slot_images: dict[str, Path] = {}
    print("Images:")
    for sid, existing in EXISTING_MAP.items():
        if existing.exists():
            slot_images[sid] = existing
            print(f"  reuse   {existing.name} → {sid}")
        else:
            print(f"  missing {existing.name} for {sid}")

    for sid, query in FETCH_MAP.items():
        out = IMG_DIR / f"{sid}.jpg"
        ok = _fetch(query, out)
        if ok:
            slot_images[sid] = out
        else:
            print(f"  ! no image for {sid}")

    # 2. Patch HTML
    html = HTML_SRC.read_text(encoding="utf-8")
    patched = patch_html(html, slot_images, HTML_SRC.parent)
    PATCHED.write_text(patched, encoding="utf-8")
    filled = sum(1 for sid in slot_images if f'id="{sid}"' in html)
    print(f"\nPatched HTML: {len(slot_images)} slots filled → {PATCHED.name}")

    # 3. Export
    print(f"\nExporting story...")
    asyncio.run(export_story(PATCHED))

    print(f"\n✅ Done.")
    print(f"   PNGs: {OUT_DIR}/")
    print(f"   MP4:  {OUT_MP4.name}")


if __name__ == "__main__":
    main()
