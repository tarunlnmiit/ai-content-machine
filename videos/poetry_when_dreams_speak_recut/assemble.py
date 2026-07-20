#!/usr/bin/env python3
"""Assemble public/index.html from storyboard.json + public/cards/*.html.

Compiles data-anim-* declarations into one paused GSAP master timeline and
emits #video-wrap framing tweens between layout changes.
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).parent
SB = json.loads((BASE / "storyboard.json").read_text())
COMP = SB["composition"]
FPS = COMP["fps"]
TARGETS = SB["videoTargets"]

def q(t):
    return round(round(t * FPS) / FPS, 4)

# ---------------- parse cards, inject ids where missing ----------------
ANIM_TAG = re.compile(r"<(\w+)([^>]*?data-anim=\"[^\"]+\"[^>]*)>", re.S)

def attr(s, name):
    m = re.search(rf'{name}="([^"]*)"', s)
    return m.group(1) if m else None

cards = []
for card in SB["cards"]:
    cid = card["id"]
    html = (BASE / "public" / "cards" / f"{cid}.html").read_text()
    anims = []
    counter = [0]

    def repl(m):
        tag, attrs = m.group(1), m.group(2)
        el_id = attr(attrs, "id")
        if not el_id:
            counter[0] += 1
            el_id = f"{cid}-a{counter[0]}"
            attrs_new = attrs + f' id="{el_id}"'
        else:
            attrs_new = attrs
        anims.append({
            "id": el_id,
            "kind": attr(attrs, "data-anim"),
            "at": float(attr(attrs, "data-anim-at") or 0),
            "dur": float(attr(attrs, "data-anim-duration") or 0.5),
            "from": attr(attrs, "data-anim-from"),
            "dist": float(attr(attrs, "data-anim-distance") or 60),
            "tw": attr(attrs, "data-anim-target-w"),
            "th": attr(attrs, "data-anim-target-h"),
            "dir": attr(attrs, "data-anim-direction") or "left",
            "stagger": float(attr(attrs, "data-anim-stagger") or 0.04),
        })
        return f"<{tag}{attrs_new}>"

    html = ANIM_TAG.sub(repl, html)
    cards.append({**card, "html": html, "anims": anims})

# ---------------- GSAP statements ----------------
def sel(cid, el_id):
    return f'.card[data-card-id="{cid}"] #{el_id}'

stmts = []
for c in cards:
    cid, s0, s1 = c["id"], c["startSec"], c["endSec"]
    host = f'.card-host[data-card-id="{cid}"]'
    stmts.append(f"// ── {cid} [{s0}, {s1}] video={c['video']} ──")
    stmts.append(f"tl.set('{host}', {{ visibility: 'visible' }}, {q(s0)});")
    stmts.append(f"tl.fromTo('{host}', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: 'power2.out' }}, {q(s0)});")
    for a in c["anims"]:
        S = sel(cid, a["id"])
        T = q(s0 + a["at"])
        D = a["dur"]
        k = a["kind"]
        if k == "fade-in":
            stmts.append(f"tl.fromTo('{S}', {{ opacity: 0 }}, {{ opacity: 1, duration: {D}, ease: 'power2.out' }}, {T});")
        elif k == "blur-in":
            stmts.append(f"tl.fromTo('{S}', {{ opacity: 0, filter: 'blur(14px)' }}, {{ opacity: 1, filter: 'blur(0px)', duration: {D}, ease: 'power2.out' }}, {T});")
        elif k == "slide-in":
            dx, dy = 0, 0
            if a["from"] == "left": dx = -a["dist"]
            elif a["from"] == "right": dx = a["dist"]
            elif a["from"] == "top": dy = -a["dist"]
            elif a["from"] == "bottom": dy = a["dist"]
            stmts.append(f"tl.fromTo('{S}', {{ opacity: 0, x: {dx}, y: {dy} }}, {{ opacity: 1, x: 0, y: 0, duration: {D}, ease: 'power2.out' }}, {T});")
        elif k == "grow-x":
            stmts.append(f"tl.fromTo('{S}', {{ width: 0 }}, {{ width: {a['tw']}, duration: {D}, ease: 'power2.out' }}, {T});")
        elif k == "grow-y":
            stmts.append(f"tl.fromTo('{S}', {{ height: 0 }}, {{ height: {a['th']}, duration: {D}, ease: 'power2.out' }}, {T});")
        elif k == "scale-pop":
            stmts.append(f"tl.fromTo('{S}', {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: {D}, ease: 'back.out(1.6)' }}, {T});")
        elif k == "mask-reveal":
            ins = {"left": "inset(0 100% 0 0)", "right": "inset(0 0 0 100%)",
                   "top": "inset(100% 0 0 0)", "bottom": "inset(0 0 100% 0)"}[a["dir"]]
            stmts.append(f"tl.fromTo('{S}', {{ clipPath: '{ins}' }}, {{ clipPath: 'inset(0 0 0 0)', duration: {D}, ease: 'power2.inOut' }}, {T});")
        elif k == "kinetic-chars":
            stmts.append(f"tl.from('{S} .char', {{ opacity: 0, y: 8, scale: 0.8, duration: {D}, ease: 'power2.out', stagger: {a['stagger']} }}, {T});")
        else:
            raise SystemExit(f"unhandled anim kind {k} in {cid}")
    fade_at = q(max(s0, s1 - 0.35))
    stmts.append(f"tl.to('{host}', {{ opacity: 0, duration: 0.35, ease: 'power2.in' }}, {fade_at});")
    stmts.append(f"tl.set('{host}', {{ visibility: 'hidden' }}, {q(s1)});")

# video framing tweens
stmts.append("// ── video framing transitions ──")
prev_key = cards[0]["video"]
prev_end = cards[0]["endSec"]
for c in cards[1:]:
    key = c["video"]
    if key != prev_key:
        t = q(max(prev_end - 0.1, c["startSec"] - 0.7))
        tgt = TARGETS[key]
        cls = "video-wrapper"
        if tgt["framed"]:
            cls = "video-wrapper framed"
        if tgt["pip"]:
            cls = "video-wrapper pip-pill"
        z = 10 if tgt["pip"] else 0
        stmts.append(f"tl.set('#video-wrap', {{ className: '{cls}', zIndex: {z} }}, {t});")
        stmts.append(
            f"tl.to('#video-wrap', {{ left: {tgt['left']}, top: {tgt['top']}, width: {tgt['width']}, height: {tgt['height']}, duration: 0.6, ease: 'power2.inOut' }}, {t});"
        )
        prev_key = key
    prev_end = c["endSec"]

gsap_body = "\n          ".join(stmts)

# ---------------- card hosts ----------------
hosts = []
for c in cards:
    b = c["hostBounds"]
    dur = round(c["endSec"] - c["startSec"], 4)
    hosts.append(
        f'<div class="card-host clip" data-card-id="{c["id"]}" data-start="{c["startSec"]:.4f}" '
        f'data-duration="{dur:.4f}" data-track-index="2" '
        f'style="left:{b["x"]}px;top:{b["y"]}px;width:{b["w"]}px;height:{b["h"]}px;visibility:hidden;opacity:0;">\n'
        f'{c["html"]}\n</div>'
    )
hosts_html = "\n\n".join(hosts)

DUR = COMP["durationSeconds"]
W, H = COMP["width"], COMP["height"]

index = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<style>
@font-face {{ font-family: 'Caveat'; src: url('fonts/Caveat-400-latin.woff2') format('woff2'); font-weight: 400; font-display: block; }}
@font-face {{ font-family: 'Caveat'; src: url('fonts/Caveat-700-latin.woff2') format('woff2'); font-weight: 700; font-display: block; }}
@font-face {{ font-family: 'Inter'; src: url('fonts/Inter-400-latin.woff2') format('woff2'); font-weight: 400; font-display: block; }}
@font-face {{ font-family: 'Inter'; src: url('fonts/Inter-700-latin.woff2') format('woff2'); font-weight: 700; font-display: block; }}
@font-face {{ font-family: 'LXGW WenKai TC'; src: url('fonts/LXGWWenKaiTC-400-latin.woff2') format('woff2'); font-weight: 400; font-display: block; }}
@font-face {{ font-family: 'Virgil'; src: url('fonts/Virgil.woff2') format('woff2'); font-display: block; }}

:root {{
  --bg: #f6efe1; --text: #2d2d2d;
  --accent-0: #bf5700; --accent-1: #d62728; --accent-2: #6c757d;
  --accent-3: #e9b54a; --accent-4: #3d5a80;
}}
* {{ box-sizing: border-box; }}
html, body {{
  margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden;
  background: #000;
  font-family: 'Inter', 'Caveat', 'LXGW WenKai TC', ui-sans-serif, system-ui, sans-serif;
}}
#stage {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}

.video-wrapper {{
  position: absolute; left: 0; top: 0; width: {W}px; height: {H}px;
  overflow: hidden; border-radius: 0; box-shadow: none;
}}
.video-wrapper video {{ width: 100%; height: 100%; object-fit: cover; }}
.video-wrapper.framed {{ border-radius: 16px; box-shadow: 0 12px 40px rgba(0,0,0,0.35); }}
.video-wrapper.pip-pill {{
  border-radius: 18px; border: 4px solid rgba(255,255,255,0.92);
  box-shadow: 0 16px 48px rgba(0,0,0,0.45);
}}

.card-host {{ position: absolute; pointer-events: none; overflow: hidden; }}
.card-host .card {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
.card-host .char {{ display: inline-block; visibility: visible; }}
</style>
</head>
<body>
<div id="stage" data-composition-id="talking-head-recut" data-start="0" data-duration="{DUR}" data-fps="{FPS}" data-width="{W}" data-height="{H}">

  <div class="video-wrapper" id="video-wrap">
    <video id="bg-video" src="input-video.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="1"></video>
  </div>

{hosts_html}

  <script src="vendor/gsap.min.js"></script>
  <script>
    (function () {{
      const tl = window.gsap.timeline({{ paused: true }});
          {gsap_body}
      window.__timelines = window.__timelines || {{}};
      window.__timelines['talking-head-recut'] = tl;
    }})();
  </script>
</div>
</body>
</html>
"""

out = BASE / "public" / "index.html"
out.write_text(index)
n_lines = index.count("\n")
print(f"wrote {out} ({n_lines} lines, {len(cards)} cards, {sum(len(c['anims']) for c in cards)} anims)")
