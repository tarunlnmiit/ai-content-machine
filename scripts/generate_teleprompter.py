#!/usr/bin/env python3
"""Generate a full-screen auto-scroll teleprompter HTML from a YT script .md file.

Usage:
  python3 scripts/generate_teleprompter.py --script content/scripts/my_script.md
  python3 scripts/generate_teleprompter.py --script content/scripts/my_script.md --open
  python3 scripts/generate_teleprompter.py --script content/scripts/my_script.md --speed 40 --fontsize 52

Output: assets/teleprompter/{slug}_teleprompter.html

Controls (in browser):
  Space / Click  — start / pause
  ↑ / ↓          — speed up / slow down
  R              — restart
  F              — toggle fullscreen
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def parse_script(text: str) -> list[str]:
    """Strip metadata block, BROLL/PAUSE markers, keep spoken lines."""
    # Remove fenced metadata block at top
    text = re.sub(r'^```[\s\S]*?```\s*', '', text, count=1).strip()

    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        # Skip horizontal rules and empty
        if not stripped or stripped == '---':
            continue
        # Skip BROLL cues
        if re.match(r'\[BROLL:', stripped, re.IGNORECASE):
            continue
        # Convert [PAUSE] to visual break
        if re.match(r'\[PAUSE\]', stripped, re.IGNORECASE):
            lines.append('__PAUSE__')
            continue
        # Skip PERSONAL_INSERT wrapper markers (keep content inside)
        if stripped.startswith('[PERSONAL_INSERT:'):
            # Extract the text inside the marker
            inner = re.sub(r'^\[PERSONAL_INSERT:\s*', '', stripped)
            inner = re.sub(r'\]$', '', inner).strip()
            if inner:
                lines.append(inner)
            continue
        lines.append(stripped)

    return lines


def build_html(lines: list[str], title: str, speed: int, fontsize: int) -> str:
    paragraphs_html = []
    for line in lines:
        if line == '__PAUSE__':
            paragraphs_html.append('<div class="pause-marker">👏 CLAP</div>')
        else:
            escaped = (line
                       .replace('&', '&amp;')
                       .replace('<', '&lt;')
                       .replace('>', '&gt;'))
            paragraphs_html.append(f'<p>{escaped}</p>')

    content = '\n'.join(paragraphs_html)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    background: #000;
    color: #f5f5f0;
    font-family: 'Georgia', serif;
    overflow-x: hidden;
    cursor: pointer;
  }}

  #scroll-container {{
    max-width: 900px;
    margin: 0 auto;
    padding: 60vh 3rem 80vh;
    line-height: 1.75;
    font-size: {fontsize}px;
  }}

  #scroll-container p {{
    margin-bottom: 1.6em;
    opacity: 0.35;
    transition: opacity 0.4s;
  }}

  #scroll-container p.active {{
    opacity: 1;
    color: #fff;
  }}

  .pause-marker {{
    text-align: center;
    font-size: 1.1rem;
    font-family: 'Arial', sans-serif;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin: 1.2em auto;
    padding: 0.45em 1.4em;
    color: #f5c518;
    border: 2px solid rgba(245, 197, 24, 0.5);
    border-radius: 6px;
    display: table;
  }}

  #controls {{
    position: fixed;
    bottom: 1.5rem;
    right: 1.5rem;
    display: flex;
    gap: 0.5rem;
    align-items: center;
    z-index: 100;
  }}

  #controls button {{
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    color: #fff;
    padding: 0.4rem 0.9rem;
    border-radius: 6px;
    font-size: 0.85rem;
    cursor: pointer;
    transition: background 0.2s;
  }}
  #controls button:hover {{ background: rgba(255,255,255,0.22); }}

  #speed-display {{
    color: rgba(255,255,255,0.5);
    font-size: 0.8rem;
    min-width: 60px;
    text-align: center;
  }}

  #guide-line {{
    position: fixed;
    top: 50%;
    left: 0;
    right: 0;
    height: 2px;
    background: rgba(255, 200, 0, 0.18);
    pointer-events: none;
    z-index: 50;
  }}

  #status {{
    position: fixed;
    top: 1rem;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 0.3rem 1rem;
    font-size: 0.8rem;
    color: rgba(255,255,255,0.4);
    z-index: 100;
    transition: opacity 0.5s;
  }}
</style>
</head>
<body>

<div id="guide-line"></div>
<div id="status">PAUSED — Click or Space to start</div>

<div id="scroll-container">
{content}
</div>

<div id="controls">
  <button onclick="slower()">− Slow</button>
  <span id="speed-display">speed {speed}</span>
  <button onclick="faster()">+ Fast</button>
  <button onclick="restart()">↺ Restart</button>
  <button onclick="toggleFullscreen()">⛶ Full</button>
</div>

<script>
  let scrollSpeed = {speed};
  let running = false;
  let animId = null;
  let lastTime = null;
  let accumulator = 0;

  const container = document.getElementById('scroll-container');
  const speedDisplay = document.getElementById('speed-display');
  const status = document.getElementById('status');
  const paragraphs = container.querySelectorAll('p');

  function updateSpeedDisplay() {{
    speedDisplay.textContent = 'speed ' + scrollSpeed;
  }}

  function faster() {{ scrollSpeed = Math.min(scrollSpeed + 5, 200); updateSpeedDisplay(); }}
  function slower() {{ scrollSpeed = Math.max(scrollSpeed - 5, 5); updateSpeedDisplay(); }}

  function restart() {{
    window.scrollTo({{ top: 0, behavior: 'smooth' }});
    running = false;
    status.style.opacity = '1';
    status.textContent = 'PAUSED — Click or Space to start';
    cancelAnimationFrame(animId);
    lastTime = null;
  }}

  function toggleFullscreen() {{
    if (!document.fullscreenElement) {{
      document.documentElement.requestFullscreen();
    }} else {{
      document.exitFullscreen();
    }}
  }}

  function highlightActive() {{
    const mid = window.innerHeight / 2;
    paragraphs.forEach(p => {{
      const rect = p.getBoundingClientRect();
      const pMid = rect.top + rect.height / 2;
      p.classList.toggle('active', Math.abs(pMid - mid) < rect.height);
    }});
  }}

  function tick(ts) {{
    if (!lastTime) lastTime = ts;
    const delta = ts - lastTime;
    lastTime = ts;
    accumulator += delta * scrollSpeed / 1000;
    if (accumulator >= 1) {{
      const px = Math.floor(accumulator);
      window.scrollBy(0, px);
      accumulator -= px;
    }}
    highlightActive();
    animId = requestAnimationFrame(tick);
  }}

  function toggle() {{
    running = !running;
    if (running) {{
      status.textContent = 'RECORDING';
      status.style.opacity = '0.4';
      lastTime = null;
      animId = requestAnimationFrame(tick);
    }} else {{
      cancelAnimationFrame(animId);
      status.style.opacity = '1';
      status.textContent = 'PAUSED — Click or Space to resume';
    }}
  }}

  document.addEventListener('click', e => {{
    if (!e.target.closest('#controls')) toggle();
  }});

  document.addEventListener('keydown', e => {{
    if (e.code === 'Space') {{ e.preventDefault(); toggle(); }}
    if (e.code === 'ArrowUp') {{ e.preventDefault(); faster(); }}
    if (e.code === 'ArrowDown') {{ e.preventDefault(); slower(); }}
    if (e.code === 'KeyR') restart();
    if (e.code === 'KeyF') toggleFullscreen();
  }});

  highlightActive();
</script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Generate auto-scroll teleprompter HTML from YT script")
    parser.add_argument("--script", required=True, help="YT script .md file")
    parser.add_argument("--speed", type=int, default=35, help="Initial scroll speed (default 35, range 5-200)")
    parser.add_argument("--fontsize", type=int, default=48, help="Font size px (default 48)")
    parser.add_argument("--open", action="store_true", help="Open in browser after generation")
    args = parser.parse_args()

    script_path = Path(args.script)
    if not script_path.exists():
        print(f"Error: {args.script} not found")
        sys.exit(1)

    text = script_path.read_text()
    lines = parse_script(text)

    slug = script_path.stem
    title = slug.replace('_', ' ')

    out_dir = REPO / "assets" / "teleprompter"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{slug}_teleprompter.html"

    html = build_html(lines, title, args.speed, args.fontsize)
    out_file.write_text(html)

    print(f"Teleprompter → {out_file}")
    print(f"Speed: {args.speed} | Font: {args.fontsize}px")
    print("Controls: Space=start/pause  ↑↓=speed  R=restart  F=fullscreen")

    if args.open:
        subprocess.run(["open", str(out_file)])


if __name__ == "__main__":
    main()
