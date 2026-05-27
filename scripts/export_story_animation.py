#!/usr/bin/env python3
"""
Export animated story HTML to MP4 video + individual PNG slides.
Uses Playwright to render the HTML and FFmpeg to encode the video.
"""

import os
import sys
import json
import time
import shutil
import subprocess
import tempfile
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

try:
    from playwright.async_api import async_playwright
    import asyncio
except ImportError:
    print("Error: Playwright not installed. Install with: pip install playwright")
    sys.exit(1)


async def export_story_animation(html_path, output_dir, slug):
    """
    Export HTML story animation to MP4 + PNG slides.

    Args:
        html_path: Path to the HTML file
        output_dir: Output directory for assets
        slug: Slug for file naming
    """
    html_path = Path(html_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"📼 Exporting story: {slug}")
    print(f"📁 Output: {output_dir}")

    # Parse animation timing from HTML
    # TOTAL = (N-1) * SLIDE_GAP + SLIDE_DUR = 6*3.7 + 4.0 = 26.2s
    # We'll capture at 30fps
    total_duration = 26.2
    fps = 30
    total_frames = int(total_duration * fps)

    # Create temp directory for frames
    temp_dir = Path(tempfile.mkdtemp())
    frames_dir = temp_dir / "frames"
    frames_dir.mkdir()

    try:
        # Start local HTTP server
        class QuietHandler(SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

        os.chdir(html_path.parent)
        server = HTTPServer(('127.0.0.1', 8765), QuietHandler)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        time.sleep(0.5)  # Let server start

        url = f"file://{html_path}"
        print(f"🌐 Rendering animation ({total_duration}s @ {fps}fps = {total_frames} frames)...")

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={"width": 1080, "height": 1920})

            # Load the HTML
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_load_state("domcontentloaded")

            # Get reference timestamps for slide transitions
            # Slides at: 0s, 3.7s, 7.4s, 11.1s, 14.8s, 18.5s, 22.2s
            # Duration each: 4.0s
            slide_starts = [0, 3.7, 7.4, 11.1, 14.8, 18.5, 22.2]

            # Capture frames
            for frame_idx in range(total_frames):
                frame_time = frame_idx / fps
                progress = int((frame_idx / total_frames) * 100)

                # Set time via closure setter and render
                await page.evaluate(f"""
                    window._setStoryTime({frame_time});
                    window._storyRender();
                """)

                # Wait for DOM updates to render
                await page.wait_for_timeout(50)

                # Screenshot
                frame_path = frames_dir / f"frame_{frame_idx:06d}.png"
                await page.screenshot(path=str(frame_path), full_page=False)

                if frame_idx % 30 == 0:
                    print(f"  ⏳ {progress}% ({frame_time:.1f}s)")

            # Extract individual slide frames (0.5s into each slide for full fade-in)
            print(f"📸 Extracting {len(slide_starts)} slide frames...")
            for slide_idx, slide_start in enumerate(slide_starts):
                slide_time = slide_start + 0.5  # Capture 0.5s into slide (after fade-in)
                slide_frame_idx = int(slide_time * fps)
                frame_path = frames_dir / f"frame_{slide_frame_idx:06d}.png"
                slide_output = output_dir / f"{slug}_story_slide_{slide_idx+1:02d}.png"
                shutil.copy(frame_path, slide_output)
                print(f"  ✓ Slide {slide_idx+1}: {slide_output.name}")

            await browser.close()

        # Encode video with FFmpeg
        print(f"🎬 Encoding MP4 video ({total_duration}s)...")
        mp4_path = output_dir / f"{slug}_story.mp4"

        # Use FFmpeg to encode frames to MP4
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", str(frames_dir / "frame_%06d.png"),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-t", str(total_duration),
            str(mp4_path)
        ]

        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            sys.exit(1)

        print(f"  ✓ Video: {mp4_path.name} ({mp4_path.stat().st_size / 1024 / 1024:.1f}MB)")

        # Create metadata
        metadata = {
            "slug": slug,
            "duration_seconds": total_duration,
            "fps": fps,
            "total_frames": total_frames,
            "slides": len(slide_starts),
            "output_files": {
                "video": mp4_path.name,
                "slides": [f"{slug}_story_slide_{i+1:02d}.png" for i in range(len(slide_starts))]
            }
        }

        metadata_path = output_dir / f"{slug}_story_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"\n✅ Export complete!")
        print(f"   📂 {output_dir}")
        print(f"   🎬 {mp4_path.name}")
        print(f"   📸 {len(slide_starts)} slides")

        return str(output_dir)

    finally:
        # Cleanup
        server.shutdown()
        shutil.rmtree(temp_dir)


def main():
    if len(sys.argv) < 4:
        print("Usage: python export_story_animation.py <html_file> <output_dir> <slug>")
        sys.exit(1)

    html_file = sys.argv[1]
    output_dir = sys.argv[2]
    slug = sys.argv[3]

    if not Path(html_file).exists():
        print(f"Error: HTML file not found: {html_file}")
        sys.exit(1)

    asyncio.run(export_story_animation(html_file, output_dir, slug))


if __name__ == "__main__":
    main()
