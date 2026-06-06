#!/usr/bin/env python3
"""
hyperframes_render.py — Fully automated Whisper → Claude → HyperFrames → MP4

Claude CLI semantically analyzes the transcript and generates ALL visual
augmentation elements automatically. Zero manual steps.

Element types (auto-chosen by LLM):
  glass-card, paradox-pair, progress-bars, question-flip, flow-arrow,
  icon-card, bar-chart, line-chart, stat-card, flowchart, code-snippet,
  comparison-table, notification-card,
  donut-chart, number-flow, kinetic-stat, pull-quote, word-highlight, callout-banner,
  tweet-card, youtube-lower-third, spotify-card

Usage:
  python3 scripts/hyperframes_render.py <video> [--duration N] [--slug name]
                                                 [--model base] [--no-render]
                                                 [--intensity minimal|light|standard|dense]
                                                 [--output-dir assets/hyperframes/]

Overlay density is controlled by --intensity (default: light). minimal/light give
human-editor restraint (sparse, calm motion); dense is the legacy maximal coverage.
Elements are cached per-slug in elements.json — pass --fresh to regenerate after
changing --intensity.
"""

import argparse, html, json, math, os, re, shutil, subprocess, sys, tempfile, threading, time, warnings
from datetime import datetime
from pathlib import Path

# Conda ffmpeg lacks libx264 encoder; prefer Homebrew build when available.
FFMPEG_BIN = "/opt/homebrew/bin/ffmpeg" if Path("/opt/homebrew/bin/ffmpeg").exists() else "ffmpeg"

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

def _spin(label, stop):
    frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    t0 = time.time()
    i = 0
    while not stop.is_set():
        print(f"\r  {frames[i % len(frames)]}  {label}  {time.time()-t0:.0f}s", end="", flush=True)
        i += 1; time.sleep(0.12)
    print(f"\r  ✓  {label}  {time.time()-t0:.0f}s")

# ── Caption grouping config ─────────────────────────────────────────────────
MAX_WORDS   = 6
PAUSE_THR   = 0.45
PUNCT_BREAK = {".", "!", "?", ","}

# ── SVG icon paths  (viewBox "0 0 100 100") ─────────────────────────────────
ICONS = {
    "heart":  "M50 84 C28 66 4 52 4 30 C4 14 16 4 30 4 C40 4 48 12 50 20 C52 12 60 4 70 4 C84 4 96 14 96 30 C96 52 72 66 50 84Z",
    "shield": "M50 8 L88 26 L88 52 C88 72 70 86 50 94 C30 86 12 72 12 52 L12 26Z",
    "eye":    "M8 50 C8 50 25 20 50 20 C75 20 92 50 92 50 C92 50 75 80 50 80 C25 80 8 50 8 50Z M50 35 A15 15 0 1 1 50 65 A15 15 0 1 1 50 35",
    "star":   "M50 8 L62 36 L92 36 L69 56 L78 84 L50 66 L22 84 L31 56 L8 36 L38 36Z",
    "lock":   "M30 46 L30 28 A20 20 0 0 1 70 28 L70 46 M18 46 L82 46 L82 88 L18 88Z",
    "unlock": "M30 46 L30 22 A20 20 0 0 1 70 22 L70 14 M18 46 L82 46 L82 88 L18 88Z",
    "chart":  "M10 90 L10 20 M10 90 L90 90 M25 60 L25 90 M45 40 L45 90 M65 50 L65 90 M85 25 L85 90",
    "brain":  "M35 75 C25 75 10 65 10 50 C10 35 20 28 30 28 C30 18 40 10 50 10 C60 10 70 18 70 28 C80 28 90 35 90 50 C90 65 75 75 65 75 C65 80 60 85 50 85 C40 85 35 80 35 75Z",
    "check":  "M15 50 L35 70 L85 25",
    "warning":"M50 10 L90 85 L10 85Z M50 35 L50 60 M50 70 L50 75",
}

# ── Helpers ─────────────────────────────────────────────────────────────────

_SIZE_W = {"sm": 240, "md": 360, "lg": 480, "xl": 600}

def _is_right(pos: str) -> bool:
    return pos.startswith("right")

def _pos_style(pos: str, top: int, width: int = 360) -> str:
    side = "right: 80px" if _is_right(pos) else "left: 80px"
    return f"{side}; top: {top}px; width: {width}px; padding: 28px 34px;"

def _x_init(pos: str) -> int: return 60 if _is_right(pos) else -60
def _x_out(pos: str)  -> int: return 40 if _is_right(pos) else -40

def _elem_width(el: dict, default: int = 360) -> int:
    return _SIZE_W.get(el.get("size", "md"), default)

def _style_class(el: dict) -> str:
    s = el.get("style", "glass")
    base = f"glass-card card-{s}" if s != "glass" else "glass-card"
    return f"{base} card-shimmer" if el.get("shimmer") else base

def _anim_entry(eid: str, pos: str, s: float, anim: str = "slide") -> str:
    xi = _x_init(pos)
    if anim == "scale":
        return (f'      gsap.set("#{eid}",{{scale:0.72,opacity:0}});\n'
                f'      tl.to("#{eid}",{{opacity:1,scale:1,duration:0.65,ease:"back.out(1.5)"}},{s});\n')
    if anim == "blur":
        return (f'      gsap.set("#{eid}",{{filter:"blur(14px)",opacity:0}});\n'
                f'      tl.to("#{eid}",{{opacity:1,filter:"blur(0px)",duration:0.75,ease:E_CIN}},{s});\n')
    if anim == "bounce":
        return (f'      gsap.set("#{eid}",{{x:{int(xi*1.6)},opacity:0}});\n'
                f'      tl.to("#{eid}",{{opacity:1,x:0,duration:0.80,ease:"back.out(2.2)"}},{s});\n')
    if anim == "springy":
        return (f'      gsap.set("#{eid}",{{x:{xi},opacity:0}});\n'
                f'      tl.to("#{eid}",{{opacity:1,x:0,duration:0.90,ease:"elastic.out(1,0.5)"}},{s});\n')
    if anim == "dramatic":
        return (f'      gsap.set("#{eid}",{{x:{int(xi*2)},opacity:0}});\n'
                f'      tl.to("#{eid}",{{opacity:1,x:0,duration:0.70,ease:"expo.out"}},{s});\n')
    return (f'      gsap.set("#{eid}",{{x:{xi},opacity:0}});\n'
            f'      tl.to("#{eid}",{{opacity:1,x:0,duration:0.65,ease:E_CIN}},{s});\n')

def _anim_exit(eid: str, pos: str, e: float, anim: str = "slide") -> str:
    xo = _x_out(pos)
    if anim in ("scale", "blur"):
        return f'      tl.to("#{eid}",{{opacity:0,duration:0.40,ease:"power2.in"}},{e});\n'
    return f'      tl.to("#{eid}",{{opacity:0,x:{xo},duration:0.45,ease:"power2.in"}},{e});\n'

def _lp(path: list[tuple]) -> str:
    return "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in path)

def _path_len(coords: list[tuple]) -> int:
    return int(sum(
        math.sqrt((coords[i+1][0]-coords[i][0])**2 + (coords[i+1][1]-coords[i][1])**2)
        for i in range(len(coords)-1)
    )) + 20


# ═══════════════════════════════════════════════════════════════════════════
# ELEMENT RENDERERS — each returns (html_str, js_str)
# ═══════════════════════════════════════════════════════════════════════════

def elem_glass_card(el):
    eid, c = el["id"], el["content"]
    pos, top = el.get("position","right"), el.get("top", 300)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    w = _elem_width(el, 360)
    anim = el.get("anim", "slide")
    cls = _style_class(el)
    html_ = f"""      <div class="{cls}" id="{eid}" style="{_pos_style(pos,top,w)}">
        <div class="gc-eyebrow">{c.get('eyebrow','')}</div>
        <div class="gc-label">{c.get('label','')}</div>
        <div class="gc-sub">{c.get('sub','')}</div>
      </div>"""
    js = _anim_entry(eid, pos, s, anim) + _anim_exit(eid, pos, e, anim)
    return html_, js


def elem_paradox_pair(el):
    eid, c = el["id"], el["content"]
    top = el.get("top", 350)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    lid, rid = f"{eid}_L", f"{eid}_R"
    svgid, lineid = f"{eid}_svg", f"{eid}_ln"
    ly = top + 22
    html_ = f"""      <div class="glass-card" id="{lid}" style="left:60px;top:{top}px;padding:16px 28px;">
        <span class="paradox-chip dim">{c.get('left','')}</span>
      </div>
      <svg id="{svgid}" style="position:absolute;top:{ly}px;left:0;width:100%;height:2px;z-index:5;overflow:visible;" xmlns="http://www.w3.org/2000/svg">
        <line id="{lineid}" x1="330" y1="1" x2="1590" y2="1" stroke="rgba(212,162,72,0.22)" stroke-width="1.5" stroke-dasharray="1260" stroke-dashoffset="1260"/>
      </svg>
      <div class="glass-card" id="{rid}" style="right:60px;top:{top}px;padding:16px 28px;">
        <span class="paradox-chip em">{c.get('right','')}</span>
      </div>"""
    js = (f'      gsap.set("#{lid}",{{x:-40}});gsap.set("#{rid}",{{x:40}});\n'
          f'      tl.to(["#{lid}","#{rid}"],{{opacity:1,x:0,duration:0.55,ease:E_CIN}},{s});\n'
          f'      tl.to("#{lineid}",{{strokeDashoffset:0,duration:0.80,ease:E_CIN}},{round(s+0.6,2)});\n'
          f'      tl.to(["#{lid}","#{rid}","#{svgid}"],{{opacity:0,duration:0.40,ease:"power2.in"}},{e});\n')
    return html_, js


def elem_progress_bars(el):
    eid, c = el["id"], el["content"]
    pos, top = el.get("position","left"), el.get("top", 300)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    xi, xo = _x_init(pos), _x_out(pos)
    b1, b2 = f"{eid}_b1", f"{eid}_b2"
    snap_at = round(s + el["duration"] * 0.55, 2)
    html_ = f"""      <div class="glass-card" id="{eid}" style="{_pos_style(pos,top,410)}">
        <div class="tc-title">{c.get('title','HOW IT HAPPENS')}</div>
        <div class="time-row"><span class="time-lbl dim">{c.get('slow_label','gradually')}</span>
          <div class="time-track"><div class="time-fill" id="{b1}"></div></div></div>
        <div class="time-row"><span class="time-lbl em">{c.get('snap_label','all at once')}</span>
          <div class="time-track"><div class="time-fill snap-fill" id="{b2}"></div></div></div>
      </div>"""
    js = (f'      gsap.set("#{eid}",{{x:{xi}}});\n'
          f'      tl.to("#{eid}",{{opacity:1,x:0,duration:0.60,ease:E_CIN}},{s});\n'
          f'      tl.to("#{b1}",{{width:"74%",duration:{round(el["duration"]*0.44,2)},ease:"power1.out"}},{round(s+0.3,2)});\n'
          f'      tl.to("#{b2}",{{width:"100%",duration:0.08,ease:E_SNAP}},{snap_at});\n'
          f'      tl.to("#{eid}",{{opacity:0,x:{xo},duration:0.45,ease:"power2.in"}},{e});\n')
    return html_, js


def elem_question_flip(el):
    eid, c = el["id"], el["content"]
    top = el.get("top", 260)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    newid = f"{eid}_new"
    html_ = f"""      <div class="glass-card" id="{eid}" style="left:60px;top:{top}px;width:480px;padding:32px 40px;">
        <div class="q-eyebrow">{c.get('eyebrow','the shift')}</div>
        <div class="q-old">{html.escape(c.get('old',''))}</div>
        <div class="q-divider"></div>
        <div class="q-new" id="{newid}">{html.escape(c.get('new',''))}</div>
      </div>"""
    js = (f'      gsap.set("#{eid}",{{x:-60}});\n'
          f'      tl.to("#{eid}",{{opacity:1,x:0,duration:0.65,ease:E_CIN}},{s});\n'
          f'      tl.to("#{newid}",{{opacity:1,duration:0.55,ease:E_CIN}},{round(s+1.8,2)});\n'
          f'      tl.to("#{eid}",{{opacity:0,x:-40,duration:0.45,ease:"power2.in"}},{e});\n')
    return html_, js


def elem_flow_arrow(el):
    eid, c = el["id"], el["content"]
    pos, top = el.get("position","right"), el.get("top", 320)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    xi, xo = _x_init(pos), _x_out(pos)
    lineid, tipid = f"{eid}_ln", f"{eid}_tip"
    html_ = f"""      <div class="glass-card" id="{eid}" style="{_pos_style(pos,top,320)}">
        <div class="gc-eyebrow">{c.get('eyebrow','')}</div>
        <div class="gc-label dim" style="font-size:28px;">{c.get('from','')}</div>
        <svg style="display:block;margin:14px 0;" width="248" height="28" viewBox="0 0 248 28" fill="none" xmlns="http://www.w3.org/2000/svg">
          <line id="{lineid}" x1="0" y1="14" x2="235" y2="14" stroke="#d4a248" stroke-width="1.5" stroke-dasharray="235" stroke-dashoffset="235"/>
          <polygon id="{tipid}" points="228,8 248,14 228,20" fill="#d4a248" opacity="0"/>
        </svg>
        <div class="gc-label em" style="font-size:28px;">{c.get('to','')}</div>
      </div>"""
    draw_at = round(s+0.65, 2)
    js = (f'      gsap.set("#{eid}",{{x:{xi}}});\n'
          f'      tl.to("#{eid}",{{opacity:1,x:0,duration:0.65,ease:E_CIN}},{s});\n'
          f'      tl.to("#{lineid}",{{strokeDashoffset:0,duration:0.60,ease:E_CIN}},{draw_at});\n'
          f'      tl.to("#{tipid}",{{opacity:1,duration:0.20,ease:E_CIN}},{round(draw_at+0.62,2)});\n'
          f'      tl.to("#{eid}",{{opacity:0,x:{xo},duration:0.45,ease:"power2.in"}},{e});\n')
    return html_, js


def elem_icon_card(el):
    eid, c = el["id"], el["content"]
    pos, top = el.get("position","right"), el.get("top", 300)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    xi, xo = _x_init(pos), _x_out(pos)
    iconid = f"{eid}_ic"
    path = ICONS.get(c.get("icon","heart"), ICONS["heart"])
    sw = "3" if c.get("icon") not in ("check","warning") else "4"
    html_ = f"""      <div class="glass-card" id="{eid}" style="{_pos_style(pos,top,280)};text-align:center;padding:36px 48px;">
        <svg id="{iconid}" width="64" height="64" viewBox="0 0 100 100" fill="none" style="display:block;margin:0 auto 16px;" xmlns="http://www.w3.org/2000/svg">
          <path d="{path}" stroke="#d4a248" stroke-width="{sw}" fill="none" stroke-linejoin="round" stroke-linecap="round"/>
        </svg>
        <div class="gc-label em" style="font-size:28px;letter-spacing:0.08em;">{c.get('label','')}</div>
      </div>"""
    pulse = round(e - 1.2, 2)
    js = (f'      gsap.set("#{eid}",{{x:{xi}}});\n'
          f'      tl.to("#{eid}",{{opacity:1,x:0,duration:0.80,ease:E_CIN}},{s});\n'
          f'      tl.to("#{iconid}",{{scale:1.12,duration:0.38,ease:E_BREATH}},{pulse});\n'
          f'      tl.to("#{iconid}",{{scale:1.0,duration:0.55,ease:E_BREATH}},{round(pulse+0.40,2)});\n'
          f'      tl.to("#{eid}",{{opacity:0,x:{xo},duration:0.45,ease:"power2.in"}},{e});\n')
    return html_, js


def elem_bar_chart(el):
    eid, c = el["id"], el["content"]
    pos, top = el.get("position","left"), el.get("top", 240)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    xi, xo = _x_init(pos), _x_out(pos)
    bars = (c.get("bars") or [])[:5]
    if not bars: bars = [{"label":"A","value":80},{"label":"B","value":60},{"label":"C","value":90}]
    title = c.get("title","")
    n = len(bars)
    max_v = max(b["value"] for b in bars) or 100
    svg_w, bottom_y, chart_h = 300, 110, 90
    bar_w = max(24, (svg_w - 20) // (n * 2))
    gap = max(8, (svg_w - 20 - n * bar_w) // (n + 1))
    rects, lbls, js_bars = [], [], ""
    for i, bar in enumerate(bars):
        x = 10 + gap + i * (bar_w + gap)
        h = max(2, int((bar["value"] / max_v) * chart_h))
        op = round(0.55 + 0.45 * (bar["value"] / max_v), 2)
        bid = f"{eid}_b{i}"
        stagger = round(s + 0.7 + i * 0.13, 2)
        rects.append(f'<rect id="{bid}" x="{x}" y="{bottom_y}" width="{bar_w}" height="0" fill="#d4a248" rx="2" opacity="{op}"/>')
        lbls.append(f'<text x="{x+bar_w//2}" y="{bottom_y+14}" text-anchor="middle" fill="rgba(255,255,255,0.30)" font-size="10" font-family="Georgia,serif">{html.escape(str(bar["label"])[:8])}</text>')
        js_bars += f'      tl.to("#{bid}",{{attr:{{y:{bottom_y-h},height:{h}}},duration:0.55,ease:"power2.out"}},{stagger});\n'
    rects_s = "\n          ".join(rects)
    lbls_s  = "\n          ".join(lbls)
    html_ = f"""      <div class="glass-card" id="{eid}" style="{_pos_style(pos,top,380)}">
        <div class="gc-eyebrow">{title}</div>
        <svg viewBox="0 0 {svg_w} {bottom_y+18}" style="width:100%;margin-top:10px;overflow:visible;" xmlns="http://www.w3.org/2000/svg">
          {rects_s}
          {lbls_s}
          <line x1="10" y1="{bottom_y}" x2="{svg_w-10}" y2="{bottom_y}" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
        </svg>
      </div>"""
    js = (f'      gsap.set("#{eid}",{{x:{xi}}});\n'
          f'      tl.to("#{eid}",{{opacity:1,x:0,duration:0.60,ease:E_CIN}},{s});\n'
          + js_bars +
          f'      tl.to("#{eid}",{{opacity:0,x:{xo},duration:0.45,ease:"power2.in"}},{e});\n')
    return html_, js


def elem_line_chart(el):
    eid, c = el["id"], el["content"]
    pos, top = el.get("position","left"), el.get("top", 240)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    xi, xo = _x_init(pos), _x_out(pos)
    points = (c.get("points") or [20,50,70,85,90])[:8]
    labels = (c.get("labels") or [str(i+1) for i in range(len(points))])
    title = c.get("title","")
    n, svg_w, bottom_y, chart_h, x_pad = len(points), 300, 105, 85, 20
    max_v = max(points) or 100
    coords = [(x_pad + i*(svg_w-2*x_pad)/max(n-1,1), bottom_y-(v/max_v)*chart_h) for i,v in enumerate(points)]
    path = _lp(coords)
    area = path + f" L {coords[-1][0]:.1f},{bottom_y} L {x_pad},{bottom_y} Z"
    dashlen = _path_len(coords)
    lineid, areaid = f"{eid}_ln", f"{eid}_ar"
    dot_html = "".join(f'<circle id="{eid}_d{i}" cx="{cx:.1f}" cy="{cy:.1f}" r="3.5" fill="#d4a248" opacity="0"/>' for i,(cx,cy) in enumerate(coords))
    lbl_html = "".join(f'<text x="{coords[i][0]:.1f}" y="{bottom_y+14}" text-anchor="middle" fill="rgba(255,255,255,0.28)" font-size="10" font-family="Georgia,serif">{html.escape(str(labels[i])[:5])}</text>' for i in range(n))
    draw_end = round(s + min(el["duration"]*0.55, 1.4), 2)
    dot_js = "".join(f'      tl.to("#{eid}_d{i}",{{opacity:1,duration:0.25,ease:E_CIN}},{round(s+0.6+i*0.12,2)});\n' for i in range(n))
    html_ = f"""      <div class="glass-card" id="{eid}" style="{_pos_style(pos,top,380)}">
        <div class="gc-eyebrow">{title}</div>
        <svg viewBox="0 0 {svg_w} {bottom_y+18}" style="width:100%;margin-top:10px;overflow:visible;" xmlns="http://www.w3.org/2000/svg">
          <path id="{areaid}" d="{area}" fill="rgba(212,162,72,0.07)" opacity="0"/>
          <path id="{lineid}" d="{path}" stroke="#d4a248" stroke-width="2.5" fill="none" stroke-dasharray="{dashlen}" stroke-dashoffset="{dashlen}"/>
          {dot_html}
          {lbl_html}
          <line x1="{x_pad}" y1="{bottom_y}" x2="{svg_w-x_pad}" y2="{bottom_y}" stroke="rgba(255,255,255,0.10)" stroke-width="1"/>
        </svg>
      </div>"""
    js = (f'      gsap.set("#{eid}",{{x:{xi}}});\n'
          f'      tl.to("#{eid}",{{opacity:1,x:0,duration:0.60,ease:E_CIN}},{s});\n'
          f'      tl.to("#{lineid}",{{strokeDashoffset:0,duration:{round(draw_end-s,2)},ease:"power1.inOut"}},{s});\n'
          f'      tl.to("#{areaid}",{{opacity:1,duration:0.40,ease:E_CIN}},{draw_end});\n'
          + dot_js +
          f'      tl.to("#{eid}",{{opacity:0,x:{xo},duration:0.45,ease:"power2.in"}},{e});\n')
    return html_, js


def elem_stat_card(el):
    eid, c = el["id"], el["content"]
    pos, top = el.get("position","right"), el.get("top", 300)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    xi, xo = _x_init(pos), _x_out(pos)
    numid = f"{eid}_n"
    pct = c.get("percent", None)
    bar_html = ""
    bar_js = ""
    if pct is not None:
        bid = f"{eid}_bar"
        bar_html = f'<div style="margin-top:14px;height:3px;background:rgba(255,255,255,0.08);border-radius:2px;overflow:hidden;"><div id="{bid}" style="height:100%;width:0%;background:#d4a248;border-radius:2px;"></div></div>'
        bar_js = f'      tl.to("#{bid}",{{width:"{pct}%",duration:0.80,ease:"power1.out"}},{round(s+0.5,2)});\n'
    html_ = f"""      <div class="glass-card" id="{eid}" style="{_pos_style(pos,top,300)};text-align:center;">
        <div class="gc-eyebrow" style="text-align:center;">{c.get('label','')}</div>
        <div id="{numid}" style="font-size:76px;font-family:Georgia,serif;color:#d4a248;line-height:1.1;opacity:0;transform:scale(0.85);will-change:transform,opacity;letter-spacing:-0.02em;">{html.escape(str(c.get('number','0')))}</div>
        <div style="font-size:19px;color:rgba(255,255,255,0.32);margin-top:8px;font-style:italic;">{c.get('sub','')}</div>
        {bar_html}
      </div>"""
    js = (f'      gsap.set("#{eid}",{{x:{xi}}});\n'
          f'      tl.to("#{eid}",{{opacity:1,x:0,duration:0.65,ease:E_CIN}},{s});\n'
          f'      tl.to("#{numid}",{{opacity:1,scale:1,duration:0.50,ease:"back.out(1.4)"}},{round(s+0.35,2)});\n'
          + bar_js +
          f'      tl.to("#{eid}",{{opacity:0,x:{xo},duration:0.45,ease:"power2.in"}},{e});\n')
    return html_, js


def elem_flowchart(el):
    eid, c = el["id"], el["content"]
    pos, top = el.get("position","left"), el.get("top", 220)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    xi, xo = _x_init(pos), _x_out(pos)
    steps = (c.get("steps") or ["Step 1","Step 2","Step 3"])[:4]
    title = c.get("title","")
    steps_html = ""
    js_steps = ""
    for i, step in enumerate(steps):
        sid = f"{eid}_s{i}"
        aid = f"{eid}_a{i}"
        steps_html += f'        <div class="fc-step" id="{sid}">{html.escape(str(step))}</div>\n'
        if i < len(steps)-1:
            steps_html += f'        <div class="fc-arr" id="{aid}">↓</div>\n'
        st = round(s + 0.55 + i * 0.30, 2)
        js_steps += f'      tl.to("#{sid}",{{opacity:1,y:0,duration:0.40,ease:E_CIN}},{st});\n'
        if i < len(steps)-1:
            js_steps += f'      tl.to("#{aid}",{{opacity:1,duration:0.25,ease:E_CIN}},{round(st+0.32,2)});\n'
    html_ = f"""      <div class="glass-card" id="{eid}" style="{_pos_style(pos,top,380)};padding:26px 32px;">
        <div class="gc-eyebrow">{title}</div>
        <div style="margin-top:14px;">
{steps_html}        </div>
      </div>"""
    js = (f'      gsap.set("#{eid}",{{x:{xi}}});\n'
          f'      gsap.set(".fc-step,.fc-arr",{{y:8}});\n'
          f'      tl.to("#{eid}",{{opacity:1,x:0,duration:0.65,ease:E_CIN}},{s});\n'
          + js_steps +
          f'      tl.to("#{eid}",{{opacity:0,x:{xo},duration:0.45,ease:"power2.in"}},{e});\n')
    return html_, js


def elem_code_snippet(el):
    eid, c = el["id"], el["content"]
    pos, top = el.get("position","left"), el.get("top", 230)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    xi, xo = _x_init(pos), _x_out(pos)
    code_raw = c.get("code","# code here")
    highlight_line = c.get("highlight_line", None)
    lang = c.get("language","python")
    lines = code_raw.split("\n")
    lines_html = ""
    for i, ln in enumerate(lines):
        escaped = html.escape(ln)
        # simple syntax: comments gray, strings green-ish, keywords amber
        escaped = re.sub(r'(#.*)$', r'<span style="color:rgba(150,160,140,0.70);">\1</span>', escaped)
        escaped = re.sub(r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')',
                         r'<span style="color:rgba(180,210,140,0.80);">\1</span>', escaped)
        escaped = re.sub(r'\b(def|class|import|from|return|if|else|elif|for|in|while|True|False|None|and|or|not|with|as|lambda)\b',
                         r'<span style="color:rgba(212,162,72,0.90);">\1</span>', escaped)
        bg = "rgba(212,162,72,0.08)" if (highlight_line is not None and i == highlight_line) else "transparent"
        lines_html += f'<div style="background:{bg};padding:1px 4px;border-radius:3px;">{escaped}</div>\n'
    html_ = f"""      <div class="glass-card" id="{eid}" style="{_pos_style(pos,top,440)};padding:22px 26px;">
        <div class="gc-eyebrow">{html.escape(lang)}</div>
        <pre style="font-family:'Courier New',monospace;font-size:15px;line-height:1.55;color:rgba(255,255,255,0.78);margin-top:12px;overflow:hidden;">{lines_html}</pre>
      </div>"""
    js = (f'      gsap.set("#{eid}",{{x:{xi}}});\n'
          f'      tl.to("#{eid}",{{opacity:1,x:0,duration:0.65,ease:E_CIN}},{s});\n'
          f'      tl.to("#{eid}",{{opacity:0,x:{xo},duration:0.45,ease:"power2.in"}},{e});\n')
    return html_, js


def elem_comparison_table(el):
    eid, c = el["id"], el["content"]
    top = el.get("top", 240)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    left_c, right_c = c.get("left",{}), c.get("right",{})
    l_items = left_c.get("items",[])
    r_items = right_c.get("items",[])
    def items_html(items, color):
        return "".join(f'<div style="font-size:20px;color:{color};margin-bottom:7px;font-style:italic;">{html.escape(str(it))}</div>' for it in items)
    html_ = f"""      <div class="glass-card" id="{eid}" style="left:60px;top:{top}px;width:500px;padding:28px 34px;">
        <div class="gc-eyebrow">{c.get('title','comparison')}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:16px;">
          <div>
            <div style="font-size:15px;letter-spacing:0.12em;text-transform:uppercase;color:rgba(255,255,255,0.26);margin-bottom:12px;">{html.escape(left_c.get('header','Before'))}</div>
            {items_html(l_items,'rgba(255,255,255,0.38)')}
          </div>
          <div>
            <div style="font-size:15px;letter-spacing:0.12em;text-transform:uppercase;color:rgba(212,162,72,0.65);margin-bottom:12px;">{html.escape(right_c.get('header','After'))}</div>
            {items_html(r_items,'rgba(212,162,72,0.85)')}
          </div>
        </div>
      </div>"""
    js = (f'      gsap.set("#{eid}",{{x:-60}});\n'
          f'      tl.to("#{eid}",{{opacity:1,x:0,duration:0.65,ease:E_CIN}},{s});\n'
          f'      tl.to("#{eid}",{{opacity:0,x:-40,duration:0.45,ease:"power2.in"}},{e});\n')
    return html_, js


def elem_notification_card(el):
    eid, c = el["id"], el["content"]
    pos, top = el.get("position","right"), el.get("top", 200)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    html_ = f"""      <div class="glass-card" id="{eid}" style="{_pos_style(pos,top,380)};padding:18px 24px;">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
          <div style="width:26px;height:26px;border-radius:6px;background:#d4a248;opacity:0.70;flex-shrink:0;"></div>
          <span style="font-size:14px;letter-spacing:0.11em;text-transform:uppercase;color:rgba(255,255,255,0.32);">{html.escape(c.get('app',''))}</span>
          <span style="margin-left:auto;font-size:13px;color:rgba(255,255,255,0.22);">now</span>
        </div>
        <div style="font-size:22px;color:rgba(255,255,255,0.80);margin-bottom:5px;">{html.escape(c.get('title',''))}</div>
        <div style="font-size:17px;color:rgba(255,255,255,0.38);font-style:italic;">{html.escape(c.get('body',''))}</div>
      </div>"""
    xi, xo = _x_init(pos), _x_out(pos)
    js = (f'      gsap.set("#{eid}",{{x:{xi},y:-20}});\n'
          f'      tl.to("#{eid}",{{opacity:1,x:0,y:0,duration:0.55,ease:"back.out(1.2)"}},{s});\n'
          f'      tl.to("#{eid}",{{opacity:0,y:-16,duration:0.40,ease:"power2.in"}},{e});\n')
    return html_, js


def elem_donut_chart(el):
    eid, c = el["id"], el["content"]
    pos, top = el.get("position","right"), el.get("top", 260)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    w = _elem_width(el, 360)
    cls = _style_class(el)
    segs = (c.get("segments") or [{"label":"value","value":65,"color":"#d4a248"},{"label":"rest","value":35}])[:4]
    title = c.get("title","")
    total = sum(sg.get("value",0) for sg in segs) or 100
    CX, CY, R, SW = 80, 80, 62, 14
    circ = round(2 * math.pi * R, 2)
    FALLBACK_COLORS = ["#d4a248","rgba(212,162,72,0.40)","rgba(255,255,255,0.22)","rgba(255,255,255,0.10)"]
    arcs_html, arcs_js, cum_angle = [], [], 0.0
    for i, sg in enumerate(segs):
        arc_id = f"{eid}_a{i}"
        frac = sg.get("value", 0) / total
        arc_len = round(frac * circ, 2)
        gap_len = round(circ - arc_len, 2)
        rot = round(-90 + cum_angle, 1)
        color = sg.get("color") or FALLBACK_COLORS[i % len(FALLBACK_COLORS)]
        arcs_html.append(
            f'<circle id="{arc_id}" cx="{CX}" cy="{CY}" r="{R}" fill="none" '
            f'stroke="{color}" stroke-width="{SW}" stroke-dasharray="0 {circ}" '
            f'stroke-linecap="butt" transform="rotate({rot} {CX} {CY})"/>'
        )
        stagger = round(s + 0.50 + i * 0.20, 2)
        arcs_js.append(f'      tl.to("#{arc_id}",{{attr:{{strokeDasharray:"{arc_len} {gap_len}"}},duration:0.70,ease:"power2.out"}},{stagger});\n')
        cum_angle += frac * 360
    center_val = str(c.get("center_value", f"{int(segs[0].get('value',0))}%"))
    center_lbl = str(segs[0].get("label",""))[:10]
    legend = "".join(
        f'<div style="margin-bottom:7px;display:flex;align-items:center;gap:7px;">'
        f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{sg.get("color") or FALLBACK_COLORS[i%4]};flex-shrink:0;"></span>'
        f'<span style="font-size:14px;color:rgba(255,255,255,0.42);">{html.escape(str(sg.get("label","")))}</span>'
        f'</div>'
        for i, sg in enumerate(segs)
    )
    xi, xo = _x_init(pos), _x_out(pos)
    arcs_html_s = "\n          ".join(arcs_html)
    html_ = f"""      <div class="{cls}" id="{eid}" style="{_pos_style(pos,top,w)}">
        <div class="gc-eyebrow">{html.escape(title)}</div>
        <div style="display:flex;align-items:center;gap:16px;margin-top:10px;">
          <svg viewBox="0 0 160 160" width="130" xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;">
            <circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="{SW}"/>
            {arcs_html_s}
            <text x="{CX}" y="{CY-4}" text-anchor="middle" fill="#d4a248" font-size="20" font-family="Georgia,serif">{html.escape(center_val)}</text>
            <text x="{CX}" y="{CY+15}" text-anchor="middle" fill="rgba(255,255,255,0.28)" font-size="10" font-family="Georgia,serif">{html.escape(center_lbl)}</text>
          </svg>
          <div style="flex:1;">{legend}</div>
        </div>
      </div>"""
    js = (f'      gsap.set("#{eid}",{{x:{xi}}});\n'
          f'      tl.to("#{eid}",{{opacity:1,x:0,duration:0.60,ease:E_CIN}},{s});\n'
          + "".join(arcs_js) +
          f'      tl.to("#{eid}",{{opacity:0,x:{xo},duration:0.45,ease:"power2.in"}},{e});\n')
    return html_, js


def elem_number_flow(el):
    eid, c = el["id"], el["content"]
    pos, top = el.get("position","right"), el.get("top", 300)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    w = _elem_width(el, 400)
    cls = _style_class(el)
    before = c.get("before", {"value": "—", "label": "before"})
    after  = c.get("after",  {"value": "—", "label": "after"})
    direction = c.get("direction", "up")
    arrow = "↑" if direction == "up" else ("↓" if direction == "down" else "→")
    arrow_color = "#4aab6d" if direction == "up" else ("#e05c5c" if direction == "down" else "#d4a248")
    before_id, after_id, arrow_id = f"{eid}_bv", f"{eid}_av", f"{eid}_ar"
    xi, xo = _x_init(pos), _x_out(pos)
    html_ = f"""      <div class="{cls}" id="{eid}" style="{_pos_style(pos,top,w)};text-align:center;">
        <div class="gc-eyebrow" style="text-align:center;">{html.escape(c.get("title","change"))}</div>
        <div style="display:flex;align-items:center;justify-content:center;gap:14px;margin-top:14px;">
          <div style="flex:1;text-align:center;">
            <div id="{before_id}" style="font-size:50px;font-family:Georgia,serif;color:rgba(255,255,255,0.32);line-height:1;opacity:0;">{html.escape(str(before.get("value","—")))}</div>
            <div style="font-size:13px;color:rgba(255,255,255,0.20);margin-top:6px;text-transform:uppercase;letter-spacing:0.10em;">{html.escape(str(before.get("label","")))}</div>
          </div>
          <div id="{arrow_id}" style="font-size:38px;color:{arrow_color};opacity:0;flex-shrink:0;">{arrow}</div>
          <div style="flex:1;text-align:center;">
            <div id="{after_id}" style="font-size:50px;font-family:Georgia,serif;color:#d4a248;line-height:1;opacity:0;">{html.escape(str(after.get("value","—")))}</div>
            <div style="font-size:13px;color:rgba(255,255,255,0.30);margin-top:6px;text-transform:uppercase;letter-spacing:0.10em;">{html.escape(str(after.get("label","")))}</div>
          </div>
        </div>
      </div>"""
    js = (f'      gsap.set("#{eid}",{{x:{xi}}});\n'
          f'      tl.to("#{eid}",{{opacity:1,x:0,duration:0.65,ease:E_CIN}},{s});\n'
          f'      tl.to("#{before_id}",{{opacity:1,duration:0.45,ease:E_CIN}},{round(s+0.35,2)});\n'
          f'      tl.to("#{after_id}",{{opacity:1,duration:0.45,ease:"back.out(1.4)"}},{round(s+0.65,2)});\n'
          f'      tl.to("#{arrow_id}",{{opacity:1,duration:0.30,ease:E_CIN}},{round(s+0.90,2)});\n'
          f'      tl.to("#{eid}",{{opacity:0,x:{xo},duration:0.45,ease:"power2.in"}},{e});\n')
    return html_, js


def elem_kinetic_stat(el):
    eid, c = el["id"], el["content"]
    pos, top = el.get("position","right"), el.get("top", 300)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    w = _elem_width(el, 300)
    cls = _style_class(el)
    anim = el.get("anim", "slide")
    number_str = str(c.get("number", "0"))
    num_digits = re.sub(r"[^\d.]", "", number_str)
    suffix = number_str.replace(num_digits, "").strip() or c.get("suffix", "")
    try:
        target = float(num_digits) if num_digits else 0.0
        snap_val = 1 if target == int(target) else 0.1
    except ValueError:
        target, snap_val = 0.0, 1
    numid, sufid = f"{eid}_n", f"{eid}_sf"
    pct = c.get("percent", None)
    bar_html, bar_js = "", ""
    if pct is not None:
        bid = f"{eid}_bar"
        bar_html = f'<div style="margin-top:14px;height:3px;background:rgba(255,255,255,0.08);border-radius:2px;overflow:hidden;"><div id="{bid}" style="height:100%;width:0%;background:#d4a248;border-radius:2px;"></div></div>'
        bar_js = f'      tl.to("#{bid}",{{width:"{pct}%",duration:0.80,ease:"power1.out"}},{round(s+0.5,2)});\n'
    count_dur = round(min(el["duration"] * 0.55, 1.6), 2)
    html_ = f"""      <div class="{cls}" id="{eid}" style="{_pos_style(pos,top,w)};text-align:center;">
        <div class="gc-eyebrow" style="text-align:center;">{html.escape(c.get("label",""))}</div>
        <div style="font-size:76px;font-family:Georgia,serif;color:#d4a248;line-height:1.1;margin-top:8px;">
          <span id="{numid}" style="opacity:0;">0</span><span id="{sufid}" style="font-size:44px;opacity:0;vertical-align:middle;">{html.escape(suffix)}</span>
        </div>
        <div style="font-size:19px;color:rgba(255,255,255,0.32);margin-top:8px;font-style:italic;">{html.escape(c.get("sub",""))}</div>
        {bar_html}
      </div>"""
    counter_obj = f"_cnt_{eid.replace('-','_')}"
    js = (_anim_entry(eid, pos, s, anim) +
          f'      var {counter_obj}={{val:0}};\n'
          f'      tl.to({counter_obj},{{val:{target},duration:{count_dur},ease:"power1.out",'
          f'onUpdate:function(){{var el=document.getElementById("{numid}");if(el)el.textContent=Math.round({counter_obj}.val*{1/snap_val}*{snap_val})/1;}}}},{round(s+0.35,2)});\n'
          f'      tl.to("#{numid}",{{opacity:1,duration:0.01}},{round(s+0.35,2)});\n'
          f'      tl.to("#{sufid}",{{opacity:1,duration:0.35,ease:E_CIN}},{round(s+0.35,2)});\n'
          + bar_js +
          _anim_exit(eid, pos, e, anim))
    return html_, js


def elem_pull_quote(el):
    eid, c = el["id"], el["content"]
    pos, top = el.get("position","right-top"), el.get("top", 80)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    w = _elem_width(el, 460)
    cls = _style_class(el)
    anim = el.get("anim", "blur")
    quote = c.get("quote", c.get("text", c.get("label", "")))
    eyebrow = c.get("eyebrow", "")
    author = c.get("author", "")
    eyebrow_html = f'<div class="gc-eyebrow">{html.escape(eyebrow)}</div>' if eyebrow else ""
    author_html = f'<div style="font-size:15px;color:rgba(255,255,255,0.26);margin-top:14px;letter-spacing:0.10em;">— {html.escape(author)}</div>' if author else ""
    html_ = f"""      <div class="{cls}" id="{eid}" style="{_pos_style(pos,top,w)};padding:32px 40px;">
        {eyebrow_html}
        <div style="font-size:34px;font-family:Georgia,serif;font-style:italic;color:#f5ede0;line-height:1.45;">{html.escape(quote)}</div>
        {author_html}
      </div>"""
    js = _anim_entry(eid, pos, s, anim) + _anim_exit(eid, pos, e, anim)
    return html_, js


def elem_word_highlight(el):
    eid, c = el["id"], el["content"]
    pos, top = el.get("position","right"), el.get("top", 300)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    w = _elem_width(el, 360)
    cls = _style_class(el)
    anim = el.get("anim", "scale")
    word = c.get("word", c.get("label", ""))
    eyebrow = c.get("eyebrow", "")
    eyebrow_html = f'<div class="gc-eyebrow" style="text-align:center;">{html.escape(eyebrow)}</div>' if eyebrow else ""
    line_id = f"{eid}_ul"
    draw_at = round(s + 0.50, 2)
    html_ = f"""      <div class="{cls}" id="{eid}" style="{_pos_style(pos,top,w)};padding:28px 36px;text-align:center;">
        {eyebrow_html}
        <div style="font-size:72px;font-family:Georgia,serif;color:#d4a248;letter-spacing:-0.02em;line-height:1;margin:8px 0;">{html.escape(word)}</div>
        <svg id="{line_id}" style="display:block;margin:8px auto 0;" width="180" height="6" viewBox="0 0 180 6" xmlns="http://www.w3.org/2000/svg">
          <line x1="0" y1="3" x2="180" y2="3" stroke="#d4a248" stroke-width="2.5" stroke-dasharray="180" stroke-dashoffset="180" stroke-linecap="round"/>
        </svg>
      </div>"""
    js = (_anim_entry(eid, pos, s, anim) +
          f'      tl.to("#{line_id} line",{{strokeDashoffset:0,duration:0.40,ease:E_SNAP}},{draw_at});\n' +
          _anim_exit(eid, pos, e, anim))
    return html_, js


def elem_callout_banner(el):
    eid, c = el["id"], el["content"]
    pos, top = el.get("position","right-bottom"), el.get("top", 700)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    w = _elem_width(el, 480)
    cls = _style_class(el)
    icon_name = c.get("icon", "check")
    path = ICONS.get(icon_name, ICONS["check"])
    sw = "4" if icon_name in ("check", "warning") else "3"
    phrase = c.get("phrase", c.get("label", ""))
    sub = c.get("sub", "")
    sub_html = f'<div style="font-size:15px;color:rgba(255,255,255,0.33);margin-top:5px;font-style:italic;">{html.escape(sub)}</div>' if sub else ""
    xi = _x_init(pos)
    html_ = f"""      <div class="{cls}" id="{eid}" style="{_pos_style(pos,top,w)};padding:20px 26px;">
        <div style="display:flex;align-items:center;gap:16px;">
          <svg width="34" height="34" viewBox="0 0 100 100" fill="none" style="flex-shrink:0;" xmlns="http://www.w3.org/2000/svg">
            <path d="{path}" stroke="#d4a248" stroke-width="{sw}" fill="none" stroke-linejoin="round" stroke-linecap="round"/>
          </svg>
          <div>
            <div style="font-size:24px;color:#f5ede0;font-family:Georgia,serif;line-height:1.25;">{html.escape(phrase)}</div>
            {sub_html}
          </div>
        </div>
      </div>"""
    js = (f'      gsap.set("#{eid}",{{x:{xi},y:28,opacity:0}});\n'
          f'      tl.to("#{eid}",{{opacity:1,x:0,y:0,duration:0.65,ease:"back.out(1.3)"}},{s});\n'
          f'      tl.to("#{eid}",{{opacity:0,y:18,duration:0.40,ease:"power2.in"}},{e});\n')
    return html_, js


def elem_tweet_card(el):
    eid, c = el["id"], el["content"]
    pos, top = el.get("position","right"), el.get("top", 280)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    w = _elem_width(el, 400)
    cls = _style_class(el)
    display_name = c.get("display_name", "")
    handle = c.get("handle", "")
    body = c.get("body", "")
    likes = c.get("likes", "")
    retweets = c.get("retweets", "")
    views = c.get("views", "")
    initials = "".join(p[0].upper() for p in display_name.split()[:2]) or "T"
    html_ = f"""      <div class="{cls}" id="{eid}" style="{_pos_style(pos,top,w)};padding:20px 24px;">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
          <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#1d9bf0,#0d7bc4);display:flex;align-items:center;justify-content:center;font-size:16px;font-family:Georgia,serif;color:#fff;flex-shrink:0;">{html.escape(initials)}</div>
          <div>
            <div style="font-size:16px;font-family:Georgia,serif;color:#f5ede0;font-weight:600;">{html.escape(display_name)}</div>
            <div style="font-size:13px;color:rgba(255,255,255,0.38);">{html.escape(handle)}</div>
          </div>
          <div style="margin-left:auto;font-size:18px;color:rgba(255,255,255,0.20);">𝕏</div>
        </div>
        <div style="font-size:20px;color:rgba(255,255,255,0.80);font-family:Georgia,serif;line-height:1.50;margin-bottom:14px;">{html.escape(body)}</div>
        <div style="display:flex;gap:20px;font-size:14px;color:rgba(255,255,255,0.28);">
          {"" if not likes else f'<span>♡ {html.escape(str(likes))}</span>'}
          {"" if not retweets else f'<span>↺ {html.escape(str(retweets))}</span>'}
          {"" if not views else f'<span>👁 {html.escape(str(views))}</span>'}
        </div>
      </div>"""
    js = (f'      gsap.set("#{eid}",{{scale:0.82,opacity:0}});\n'
          f'      tl.to("#{eid}",{{opacity:1,scale:1,duration:0.55,ease:"back.out(1.2)"}},{s});\n'
          f'      tl.to("#{eid}",{{opacity:0,scale:0.92,duration:0.35,ease:"power2.in"}},{e});\n')
    return html_, js


def elem_youtube_lower_third(el):
    eid, c = el["id"], el["content"]
    pos, top = el.get("position","left-bottom"), el.get("top", 700)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    w = _elem_width(el, 440)
    cls = _style_class(el)
    channel = c.get("channel", "")
    handle = c.get("handle", "")
    tagline = c.get("tagline", "")
    initials = "".join(p[0].upper() for p in channel.split()[:2]) or "YT"
    avatar_color = c.get("avatar_color", "#ff0000")
    xi = _x_init(pos)
    html_ = f"""      <div class="{cls}" id="{eid}" style="{_pos_style(pos,top,w)};padding:18px 22px;">
        <div style="display:flex;align-items:center;gap:14px;">
          <div style="width:44px;height:44px;border-radius:50%;background:{html.escape(avatar_color)};display:flex;align-items:center;justify-content:center;font-size:16px;font-family:Georgia,serif;color:#fff;flex-shrink:0;font-weight:700;">{html.escape(initials)}</div>
          <div style="flex:1;min-width:0;">
            <div style="font-size:18px;font-family:Georgia,serif;color:#f5ede0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{html.escape(channel)}</div>
            <div style="font-size:13px;color:rgba(255,255,255,0.36);margin-top:2px;">{html.escape(tagline or handle)}</div>
          </div>
          <div style="background:#ff0000;border-radius:4px;padding:6px 12px;font-size:13px;font-family:Georgia,serif;color:#fff;flex-shrink:0;letter-spacing:0.04em;">Subscribe</div>
        </div>
      </div>"""
    js = (f'      gsap.set("#{eid}",{{x:{xi},y:24,opacity:0}});\n'
          f'      tl.to("#{eid}",{{opacity:1,x:0,y:0,duration:0.60,ease:"back.out(1.2)"}},{s});\n'
          f'      tl.to("#{eid}",{{opacity:0,y:16,duration:0.40,ease:"power2.in"}},{e});\n')
    return html_, js


def elem_spotify_card(el):
    eid, c = el["id"], el["content"]
    pos, top = el.get("position","right-bottom"), el.get("top", 680)
    s, e = el["start_at"], round(el["start_at"] + el["duration"], 2)
    w = _elem_width(el, 340)
    cls = _style_class(el)
    track = c.get("track", "")
    artist = c.get("artist", "")
    album_color = c.get("album_color", "#1DB954")
    progress = max(0, min(100, c.get("progress", 35)))
    album_char = c.get("album_emoji", "♪")
    bar_id = f"{eid}_pb"
    xi = _x_init(pos)
    html_ = f"""      <div class="{cls}" id="{eid}" style="{_pos_style(pos,top,w)};padding:16px 20px;">
        <div style="display:flex;align-items:center;gap:14px;">
          <div style="width:48px;height:48px;border-radius:8px;background:{html.escape(album_color)};display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0;">{html.escape(album_char)}</div>
          <div style="flex:1;min-width:0;">
            <div style="font-size:17px;font-family:Georgia,serif;color:#f5ede0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{html.escape(track)}</div>
            <div style="font-size:13px;color:rgba(255,255,255,0.40);margin-top:3px;">{html.escape(artist)}</div>
            <div style="margin-top:8px;height:3px;background:rgba(255,255,255,0.12);border-radius:2px;overflow:hidden;">
              <div id="{bar_id}" style="height:100%;width:0%;background:#1DB954;border-radius:2px;"></div>
            </div>
          </div>
          <div style="font-size:20px;color:#1DB954;flex-shrink:0;">▶</div>
        </div>
      </div>"""
    js = (f'      gsap.set("#{eid}",{{x:{xi},y:20,opacity:0}});\n'
          f'      tl.to("#{eid}",{{opacity:1,x:0,y:0,duration:0.55,ease:E_CIN}},{s});\n'
          f'      tl.to("#{bar_id}",{{width:"{progress}%",duration:{round(el["duration"]*0.60,2)},ease:"power1.inOut"}},{round(s+0.40,2)});\n'
          f'      tl.to("#{eid}",{{opacity:0,y:14,duration:0.40,ease:"power2.in"}},{e});\n')
    return html_, js


RENDERERS = {
    "glass-card":       elem_glass_card,
    "paradox-pair":     elem_paradox_pair,
    "progress-bars":    elem_progress_bars,
    "question-flip":    elem_question_flip,
    "flow-arrow":       elem_flow_arrow,
    "icon-card":        elem_icon_card,
    "bar-chart":        elem_bar_chart,
    "line-chart":       elem_line_chart,
    "stat-card":        elem_stat_card,
    "flowchart":        elem_flowchart,
    "code-snippet":     elem_code_snippet,
    "comparison-table": elem_comparison_table,
    "notification-card":elem_notification_card,
    "donut-chart":          elem_donut_chart,
    "number-flow":          elem_number_flow,
    "kinetic-stat":         elem_kinetic_stat,
    "pull-quote":           elem_pull_quote,
    "word-highlight":       elem_word_highlight,
    "callout-banner":       elem_callout_banner,
    "tweet-card":           elem_tweet_card,
    "youtube-lower-third":  elem_youtube_lower_third,
    "spotify-card":         elem_spotify_card,
}


# ═══════════════════════════════════════════════════════════════════════════
# LLM ANALYSIS PROMPT
# ═══════════════════════════════════════════════════════════════════════════

# Intensity controls how often overlays appear and how animated they are.
# A real human editor is sparing — overlays land on genuinely high-value beats,
# not every passing concept. `dense` preserves the legacy maximal behavior.
# {density_directive} replaces the frequency paragraph; {coverage_directive}
# replaces the pro-density RULES lines. Both threaded via _PROMPT.format().
_DENSITY_DIRECTIVES = {
    "minimal": (
        "Be very sparing — like a restrained human editor. Add an overlay ONLY at the "
        "few highest-value moments: a hard data point, a sharp contrast, one key takeaway. "
        "Target roughly ONE element every 45–60 seconds. Hard cap: no more than "
        "{duration_min} elements total for this video (≈1 per minute). Leave long "
        "stretches with NO overlay — silence is fine. NEVER overlap elements in time. "
        "Animations must be calm: use ONLY anim \"slide\", \"blur\", or a plain fade. "
        "Do NOT use \"bounce\", \"springy\", \"scale\", or any overshoot/elastic motion."
    ),
    "light": (
        "Be selective — like a tasteful human editor, not an effects machine. Add an "
        "overlay only when it genuinely earns its place: data, a real contrast, a process, "
        "a landing takeaway. Target roughly ONE element every 30–40 seconds. Leave gaps "
        "with no overlay. Do NOT overlap elements in time. Keep motion calm: prefer anim "
        "\"slide\", \"blur\", or fade; avoid \"bounce\"/\"springy\"/elastic overshoot."
    ),
    "standard": (
        "Augment the meaningful beats — concepts, contrasts, data, processes, key insights. "
        "Aim for roughly one element every 18–25 seconds. Avoid overlapping elements in the "
        "same zone. Use overshoot animations (\"bounce\", \"springy\") only for true emphasis moments."
    ),
    "dense": (
        "Cover the ENTIRE video with visual elements — every significant concept, contrast, "
        "data point, process, metaphor, emotion, or key insight deserves one. There is no "
        "maximum count. Aim so the video never goes more than 12–15 seconds without a visual "
        "element. If the content is dense, elements may overlap in time as long as they use "
        "different positions (left vs right vs both)."
    ),
}
_COVERAGE_DIRECTIVES = {
    "minimal": "- When in doubt, SKIP it. Fewer, stronger overlays beat constant motion.",
    "light":   "- When two ideas appear close together, pick the stronger one and skip the other. Restraint reads as human.",
    "standard":"- Cover the important beats: contrasts, data mentions, process explanations, emotional peaks, key definitions.",
    "dense": (
        "- Cover ALL of: contrasts, metaphors, data mentions, process explanations, "
        "emotional peaks, definitions, examples, transitions\n"
        "- If two ideas appear close together, use left + right zones simultaneously rather than skipping one"
    ),
}


def _density_directive(intensity: str, duration: float) -> str:
    text = _DENSITY_DIRECTIVES.get(intensity, _DENSITY_DIRECTIVES["light"])
    return text.replace("{duration_min}", str(max(1, round(duration / 60))))


_PROMPT = """\
You are a senior cinematic motion graphics director and data visualization specialist.

Analyze this video transcript and generate the BEST visual augmentation elements.
Your goal: make the video feel visually alive, intelligently augmented, never a static talking head.

FULL TRANSCRIPT:
"{full_text}"

WORD TIMESTAMPS (JSON):
{words_json}

VIDEO DURATION: {duration}s

DENSITY (how often overlays should appear — follow this strictly):
{density_directive}

SAFE ZONES — face occupies center (~560–1360px), captions anchor at the bottom (~880px+).
Use ONLY the left and right strips. Six named zones:

  left-top    → left: 80px, top: 60–180px    (high up, uncrowded — use for impactful moments)
  left-mid    → left: 80px, top: 280–500px   (default mid zone)
  right-top   → right: 80px, top: 60–180px
  right-mid   → right: 80px, top: 280–500px  (default mid zone)
  left-bottom → left: 80px, top: 620–760px   (low, just above captions)
  right-bottom→ right: 80px, top: 620–760px

  "left" = alias for left-mid. "right" = alias for right-mid.
  "both" = full width (paradox-pair ONLY).

No two elements at the SAME zone overlapping in time. Different zones can run simultaneously.
VARY zones — avoid using the same zone for consecutive elements.

OPTIONAL FIELDS (add to any element):
  "style": "glass"(default) | "neon"(data/tech, blue) | "neon-green"(positive metrics, growth) | "neon-purple"(poetry, creative) | "neon-red"(tension, contrast) | "brutal"(process/flow, stripe) | "warm"(emotional/life, amber)
  "size":  "sm"(240px) | "md"(360px,default) | "lg"(480px) | "xl"(600px)
  "anim":  "slide"(default) | "scale"(zoom) | "blur"(unblur reveal) | "bounce"(overshoot) | "springy"(elastic oscillate, energetic) | "dramatic"(expo.out, fast-start long-glide)
  "shimmer": true — adds a CSS light-sweep shimmer 1.5s after entry. Use on premium stat/metric reveals.

ELEMENT TYPES — choose whichever best fits the content:

1. glass-card — floating info card. Use for concept introductions, metaphors, definitions.
   content: {{"eyebrow":"short phrase","label":"Main Idea","sub":"supporting phrase"}}

2. paradox-pair — two opposing corner chips + connecting line.
   Use ONLY when speaker juxtaposes two opposing concepts in same sentence.
   position: "both". content: {{"left":"concept A","right":"concept B"}}

3. progress-bars — two labeled fill bars (slow vs snap). Use for speed/time contrasts.
   content: {{"title":"HOW IT WORKS","slow_label":"gradually","snap_label":"instantly"}}

4. question-flip — old question strikethrough → new question reveal.
   Use when speaker explicitly shifts the question being asked. position: left-mid or left-top.
   content: {{"eyebrow":"the shift","old":"old question?","new":"new question?"}}

5. flow-arrow — from→to card with animated arrow.
   Use for before→after, cause→effect, or transformations.
   content: {{"eyebrow":"the movement","from":"starting state","to":"ending state"}}

6. icon-card — glass card with icon at emotional/key moments.
   icon options: heart, shield, eye, star, lock, unlock, chart, brain, check, warning
   content: {{"icon":"heart","label":"safe."}}

7. bar-chart — animated SVG bar chart. Use when comparing quantities/rankings.
   Provide REAL data values that match what speaker is discussing.
   content: {{"title":"chart title","bars":[{{"label":"A","value":80}},{{"label":"B","value":60}},{{"label":"C","value":90}}]}}

8. line-chart — animated line chart. Use for trends, progress over time, growth.
   Provide REAL data points (0–100 scale) matching the spoken context.
   content: {{"title":"chart title","points":[20,45,65,78,90],"labels":["1","2","3","4","5"]}}

9. stat-card — large static metric. Use when you do NOT need count-up animation.
   content: {{"label":"metric name","number":"87%","sub":"on test set","percent":87}}

10. flowchart — step-by-step process with arrows. Use for workflows, pipelines, how-to sequences.
    content: {{"title":"process name","steps":["Step 1","Step 2","Step 3","Step 4"]}}

11. code-snippet — syntax-highlighted code block. Use for technical/programming content.
    content: {{"language":"python","code":"df = pd.read_csv('data.csv')\\ndf.dropna()","highlight_line":1}}

12. comparison-table — two-column before/after. Use for contrasting two approaches/states.
    content: {{"title":"vs","left":{{"header":"Before","items":["item1","item2"]}},"right":{{"header":"After","items":["item1","item2"]}}}}

13. notification-card — macOS-style popup. Use for results, completions, achievements.
    content: {{"app":"Python","title":"Model trained","body":"Accuracy: 94.2%"}}

14. donut-chart — animated SVG donut for proportional/percentage data.
    Use when speaker mentions %, ratio, or part-of-whole breakdown. style: "neon" for data/tech.
    content: {{"title":"chart title","center_value":"65%","segments":[{{"label":"A","value":65,"color":"#d4a248"}},{{"label":"B","value":35}}]}}

15. number-flow — before→after metric comparison with count-up and directional arrow.
    Use for any before/after comparison with numbers. style: "neon" for tech, "warm" for life.
    content: {{"title":"the change","before":{{"value":"12%","label":"before"}},"after":{{"value":"87%","label":"after"}},"direction":"up"}}

16. kinetic-stat — large number with animated count-up from zero to target value.
    Use when speaker mentions a specific number that deserves dramatic reveal. style: "neon".
    content: {{"label":"metric name","number":"94","suffix":"%","sub":"accuracy on holdout","percent":94}}

17. pull-quote — large italic editorial text callout. For emotional peaks or poetry moments.
    Best at left-top or right-top. anim: "blur". style: "warm" for emotional, "glass" otherwise. size: "lg".
    content: {{"eyebrow":"the insight","quote":"the exact phrase that lands hardest"}}

18. word-highlight — single key term in large type with animated underline.
    Use for definitions, pivotal terms, punchy single-word moments. anim: "scale". style: "neon". duration: 3–5s.
    content: {{"eyebrow":"the concept","word":"Overfitting"}}

19. callout-banner — wider card with icon + phrase. Use for key takeaways at end of a point.
    Best at left-bottom or right-bottom. style: "brutal". anim: slide.
    icon options: check, brain, chart, warning, star, shield
    content: {{"icon":"check","phrase":"key takeaway phrase","sub":"optional detail"}}

20. tweet-card — X/Twitter-style post card overlay. Use when content distills to a shareable insight, quote, or stat.
    Shows: avatar circle, display name, @handle, tweet body (≤140 chars), engagement metrics.
    style: "glass" or "neon". anim: "scale" (default for this type). Duration: 5–7s.
    content: {{"display_name":"Tarun Gupta","handle":"@mistakenlyhuman","body":"the insight as a tweet","likes":"2.4K","retweets":"380","views":"18K"}}

21. youtube-lower-third — Channel identity bar. Use at credibility-establishing moments (speaker introduces expertise, cites credentials).
    Shows: colored avatar circle, channel name, tagline. Best at left-bottom or right-bottom. style: "glass" or "brutal". Duration: 5–8s.
    content: {{"channel":"Breath of Data Science","handle":"@breathofdatascience","tagline":"Data Science · 10 years","avatar_color":"#d4a248"}}

22. spotify-card — Now Playing overlay. Use at emotional/reflective moments in life or poetry content.
    Shows: colored album square, track name, artist, animated progress bar. Best at right-bottom or left-bottom. style: "glass". Duration: 6–9s.
    content: {{"track":"feeling name or concept","artist":"Tarun Gupta","album_color":"#1DB954","album_emoji":"♪","progress":42}}

CHART SELECTION RULES (ALWAYS use a chart type for quantitative content):
  % / ratio / proportion mentioned → donut-chart
  before/after numbers → number-flow
  dramatic single number → kinetic-stat
  trend over time → line-chart
  ranked comparison → bar-chart

RULES:
- start_at must match an actual spoken moment from the timestamps
- duration: 4–8 seconds each (word-highlight: 3–5s)
- For charts/data: derive values from the transcript context or reasonable defaults
- For bar/line charts: make labels short (max 8 chars)
- For code-snippet: include only 3–6 lines max
- VARY styles and positions — avoid the same style/zone for consecutive elements
- Use left-top / right-top for high-impact moments (uncrowded, visually prominent)
- Use left-bottom / right-bottom for takeaways (just above captions, grounding)
- Mix types for genre: poetry→pull-quote/word-highlight/icon-card/spotify-card/neon-purple; DS→charts/code/kinetic-stat/tweet-card/neon-green; life→comparison/flow/warm-style/youtube-lower-third
- Use "shimmer":true on kinetic-stat and number-flow for premium metric reveals
{coverage_directive}

OUTPUT ONLY VALID JSON (no markdown, no explanation):
{{"elements":[{{"id":"aug_001","type":"glass-card","start_at":10.5,"duration":6.0,"position":"right-mid","top":320,"style":"glass","size":"md","anim":"slide","content":{{...}}}}]}}"""


# ═══════════════════════════════════════════════════════════════════════════
# CSS + JS BASE
# ═══════════════════════════════════════════════════════════════════════════

_CSS = """\
      * { margin:0; padding:0; box-sizing:border-box; }
      html,body { width:__W__px; height:__H__px; overflow:hidden; background:#000; -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale; text-rendering:optimizeLegibility; }
      #bg-video { position:absolute; top:0; left:0; width:__W__px; height:__H__px; object-fit:cover; image-rendering:high-quality; z-index:0; }
      #vignette { position:absolute; inset:0; background:radial-gradient(ellipse at center,transparent 38%,rgba(0,0,0,0.62) 100%); z-index:1; animation:breathe 14s ease-in-out infinite; }
      @keyframes breathe { 0%,100%{opacity:1} 50%{opacity:0.74} }
      #dark-veil { position:absolute; inset:0; background:rgba(0,0,0,0.28); opacity:0; z-index:2; pointer-events:none; }
      #warm-bloom { position:absolute; inset:0; background:radial-gradient(ellipse 80% 60% at 50% 55%,rgba(190,130,45,0.16) 0%,rgba(160,90,20,0.08) 50%,transparent 100%); opacity:0; z-index:2; pointer-events:none; }
      #caption-bg { position:absolute; bottom:0; left:0; right:0; height:400px; background:linear-gradient(to top,rgba(0,0,0,0.82) 0%,rgba(0,0,0,0.40) 55%,transparent 100%); z-index:3; }
      #accent-bar { position:absolute; bottom:76px; left:50%; transform:translateX(-50%); height:2px; width:0; background:linear-gradient(to right,transparent,#d4a248 30%,#d4a248 70%,transparent); border-radius:1px; opacity:0; z-index:11; }
      .line { position:absolute; left:0; right:0; text-align:center; font-family:'Georgia',serif; font-weight:400; color:#f5ede0; text-shadow:0 2px 8px rgba(0,0,0,0.85),0 0 28px rgba(0,0,0,0.55); opacity:0; will-change:transform,opacity,letter-spacing; z-index:10; padding:0 200px; -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility; }
      .sz-xl{font-size:88px;bottom:72px;letter-spacing:0.025em}
      .sz-lg{font-size:80px;bottom:80px;letter-spacing:0.025em}
      .sz-md{font-size:70px;bottom:88px;letter-spacing:0.028em}
      .sz-sm{font-size:58px;bottom:96px;letter-spacing:0.03em}
      .sz-xs{font-size:50px;bottom:100px;letter-spacing:0.04em;font-style:italic}
      .em{color:#d4a248} .dim{opacity:0.50}
      .word{display:inline-block;opacity:0;will-change:transform,opacity;margin-right:0.28em}
      .word:last-child{margin-right:0}
      .glass-card{position:absolute;background:rgba(8,10,16,0.52);border:1px solid rgba(255,255,255,0.08);border-radius:14px;opacity:0;z-index:6;will-change:transform,opacity;font-family:'Georgia',serif;color:#f5ede0;backdrop-filter:blur(14px) saturate(1.1);-webkit-backdrop-filter:blur(14px) saturate(1.1);box-shadow:0 18px 50px -20px rgba(0,0,0,0.65),0 1px 0 rgba(255,255,255,0.04) inset;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
      .gc-eyebrow{font-size:17px;letter-spacing:0.14em;text-transform:uppercase;color:rgba(255,255,255,0.24);margin-bottom:12px}
      .gc-label{font-size:32px;color:rgba(255,255,255,0.55);line-height:1.3}
      .gc-label.em{color:#d4a248}
      .gc-sub{font-size:20px;color:rgba(255,255,255,0.28);margin-top:6px;font-style:italic}
      .paradox-chip{font-size:26px;letter-spacing:0.13em;text-transform:uppercase}
      .paradox-chip.dim{color:rgba(255,255,255,0.36)}
      .paradox-chip.em{color:#d4a248}
      .tc-title{font-size:17px;letter-spacing:0.13em;text-transform:uppercase;color:rgba(255,255,255,0.22);margin-bottom:22px}
      .time-row{display:flex;align-items:center;gap:18px}
      .time-row+.time-row{margin-top:20px}
      .time-lbl{font-size:24px;width:130px;flex-shrink:0;font-style:italic;color:rgba(255,255,255,0.38)}
      .time-lbl.em{color:#d4a248}
      .time-track{flex:1;height:3px;background:rgba(255,255,255,0.08);border-radius:2px;overflow:hidden}
      .time-fill{height:100%;width:0%;border-radius:2px;background:rgba(255,255,255,0.30)}
      .snap-fill{background:#d4a248}
      .q-eyebrow{font-size:17px;letter-spacing:0.14em;text-transform:uppercase;color:rgba(255,255,255,0.22);margin-bottom:16px}
      .q-old{font-size:27px;font-style:italic;line-height:1.45;color:rgba(255,255,255,0.30);text-decoration:line-through;text-decoration-color:rgba(255,255,255,0.18);margin-bottom:16px}
      .q-divider{height:1px;background:rgba(255,255,255,0.08);margin-bottom:16px}
      .q-new{font-size:29px;font-style:italic;line-height:1.45;color:#d4a248;opacity:0;will-change:opacity}
      .fc-step{border:1px solid rgba(255,255,255,0.12);border-radius:8px;padding:10px 16px;font-size:21px;color:rgba(255,255,255,0.60);text-align:center;margin-bottom:0;opacity:0;will-change:opacity,transform}
      .fc-step:last-child{border-color:rgba(212,162,72,0.40);color:#d4a248}
      .fc-arr{text-align:center;color:rgba(212,162,72,0.40);font-size:18px;padding:4px 0;opacity:0}
      .card-neon{background:rgba(4,8,20,0.84);border:1px solid rgba(80,160,255,0.30);box-shadow:0 0 22px rgba(80,160,255,0.12),inset 0 1px 0 rgba(80,160,255,0.07);}
      .card-brutal{background:rgba(14,14,14,0.93);border:none;border-left:4px solid #d4a248;border-radius:6px;}
      .card-warm{background:linear-gradient(135deg,rgba(62,28,8,0.88),rgba(38,18,5,0.82));border:1px solid rgba(212,162,72,0.26);}
      .card-neon-green{background:rgba(4,18,10,0.84);border:1px solid rgba(74,171,109,0.32);box-shadow:0 0 22px rgba(74,171,109,0.14),inset 0 1px 0 rgba(74,171,109,0.07);}
      .card-neon-purple{background:rgba(10,4,22,0.84);border:1px solid rgba(160,80,255,0.30);box-shadow:0 0 22px rgba(160,80,255,0.14),inset 0 1px 0 rgba(160,80,255,0.07);}
      .card-neon-red{background:rgba(22,4,4,0.84);border:1px solid rgba(224,92,92,0.30);box-shadow:0 0 22px rgba(224,92,92,0.12),inset 0 1px 0 rgba(224,92,92,0.07);}
      .card-shimmer{overflow:hidden;}
      .card-shimmer::after{content:'';position:absolute;inset:0;border-radius:14px;background:linear-gradient(110deg,transparent 20%,rgba(255,255,255,0.07) 50%,transparent 80%);background-size:200% 100%;animation:shimmer-pass 1.8s ease-in-out 1.4s 1 forwards;pointer-events:none;}
      @keyframes shimmer-pass{from{background-position:200% 0}to{background-position:-100% 0}}"""

_JS_HELPERS = """\
      const E_CIN="power2.out",E_SLOW="power1.inOut",E_SNAP="power4.out",E_BREATH="sine.inOut";
      gsap.set(".line",{y:24}); gsap.set(".word",{y:14});
      const lineIn=(id,at,dur=0.65)=>tl.to(id,{opacity:1,y:0,duration:dur,ease:E_CIN},at);
      const lineOut=(id,at,dur=0.24)=>tl.to(id,{opacity:0,y:-18,duration:dur,ease:"power2.in"},at);
      const wordIn=(id,at,dur=0.40)=>tl.to(id,{opacity:1,y:0,duration:dur,ease:E_CIN},at);\n"""


def build_caption_tl(lines, duration):
    js = ""
    for i, ln in enumerate(lines):
        lid = f"#l{i+1:02d}"
        s = ln["start"]
        e = round(lines[i+1]["start"] - 0.18, 3) if i+1 < len(lines) else round(min(ln["end"]+0.6, duration-0.2), 3)
        if i == 0:
            js += f'      gsap.set("{lid}",{{letterSpacing:"0.16em",y:24}});\n'
            js += f'      tl.to("{lid}",{{opacity:1,y:0,letterSpacing:"0.028em",duration:1.05,ease:E_SLOW}},{s});\n'
        else:
            js += f'      lineIn("{lid}",{s});\n'
        js += f'      lineOut("{lid}",{e});\n'
    return js


def generate_html(lines, elements, duration, video_fn, show_captions=True, width=1920, height=1080):
    cap_divs = "\n".join(f'      <div class="line sz-md" id="l{i+1:02d}">{ln["text"]}</div>' for i,ln in enumerate(lines)) if show_captions else ""
    aug_html_parts, aug_js_parts = [], []
    for el in elements:
        fn = RENDERERS.get(el.get("type","glass-card"))
        if not fn: continue
        try:
            h, j = fn(el)
            aug_html_parts.append(h)
            aug_js_parts.append(j)
        except Exception as ex:
            print(f"  Warning: skipping {el.get('id')} — {ex}")
    aug_html = "\n".join(aug_html_parts)
    aug_js   = "".join(aug_js_parts)
    cap_tl   = build_caption_tl(lines, duration) if show_captions else ""
    css = _CSS.replace("__W__", str(width)).replace("__H__", str(height))
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width={width}, height={height}"/>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
{css}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{int(duration)}" data-width="{width}" data-height="{height}">
      <video id="bg-video" src="assets/{video_fn}" data-start="0" data-duration="{int(duration)}" muted playsinline preload="auto"></video>
      <audio id="bg-audio" src="assets/{video_fn}" data-start="0" data-duration="{int(duration)}" data-track-index="0" data-volume="1"></audio>
      <div id="vignette"></div><div id="dark-veil"></div><div id="warm-bloom"></div>
      <div id="caption-bg"></div><div id="accent-bar"></div>
{aug_html}
{cap_divs}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{paused:true}});
{_JS_HELPERS}
{cap_tl}
{aug_js}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>"""


# ═══════════════════════════════════════════════════════════════════════════
# PIPELINE
# ═══════════════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("input_video", type=Path, nargs="?", default=None)
    p.add_argument("--slug",       default=None)
    p.add_argument("--duration",   type=float, default=None)
    p.add_argument("--model",      default="base", choices=["tiny","base","small","medium"])
    p.add_argument("--no-render",   action="store_true")
    p.add_argument("--no-captions", action="store_true", help="Omit burned-in subtitles from the render")
    p.add_argument("--output-dir",  type=Path, default=Path("assets/hyperframes"))
    p.add_argument("--shorts",      action="store_true", help="Process all shorts for --slug from assets/video/edited/shorts/")
    p.add_argument("--shorts-dir",  type=Path, default=Path("assets/video/edited/shorts"), help="Directory containing short clips")
    p.add_argument("--fresh",       action="store_true", help="Force wipe of cached /tmp/hf_<slug> project before run (ignores cached clip/audio/whisper/elements)")
    p.add_argument("--intensity",   choices=["minimal", "light", "standard", "dense"], default="light",
                   help="Overlay density. minimal/light = human-editor restraint (default light); "
                        "dense = legacy maximal coverage. Controls element frequency + animation style.")
    return p.parse_args()

def get_duration(path):
    r = subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_streams",str(path)],capture_output=True,text=True,check=True)
    for s in json.loads(r.stdout)["streams"]:
        if s.get("codec_type")=="video": return float(s.get("duration",0))
    return 0.0

def get_video_dimensions(path):
    r = subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_streams",str(path)],capture_output=True,text=True,check=True)
    for s in json.loads(r.stdout)["streams"]:
        if s.get("codec_type")=="video":
            w, h = s.get("width"), s.get("height")
            if not w or not h:
                raise RuntimeError(f"ffprobe missing width/height for {path}")
            return int(w), int(h)
    raise RuntimeError(f"ffprobe found no video stream in {path}")

def extract_audio(video, proj, dur):
    out = proj/"audio.wav"
    cmd = [FFMPEG_BIN,"-i",str(video)]
    if dur: cmd+=["-t",str(dur)]
    cmd+=["-vn","-ar","16000","-ac","1",str(out),"-y"]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print(r.stderr.decode(errors="replace")[-2000:])
        raise RuntimeError(f"ffmpeg extract_audio failed (exit {r.returncode})")
    return out

def extract_video(video, proj, dur):
    (proj/"assets").mkdir(exist_ok=True)
    out = proj/"assets"/"clip.mp4"
    vid_w, vid_h = get_video_dimensions(video)
    is_portrait = vid_h > vid_w
    base = [FFMPEG_BIN,"-i",str(video)]
    if dur: base+=["-t",str(dur)]
    # Landscape inputs: try stream copy with BSF SAR fix (no re-encode).
    # Portrait inputs: always re-encode — stream-copy under parallel load
    # produced divergent framing between worker waves.
    if not is_portrait:
        r = subprocess.run(base+["-c","copy","-bsf:v","h264_metadata=sample_aspect_ratio=1/1",
                                  "-movflags","+faststart",str(out),"-y"], capture_output=True)
        if r.returncode == 0: return out
    encode = base+[
        "-c:v","libx264","-preset","medium","-crf","17",
        "-pix_fmt","yuv420p","-profile:v","high","-level","4.1",
        "-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709",
        "-vf","setsar=1","-r","30","-g","30",
        "-movflags","+faststart",
        "-c:a","aac","-b:a","192k","-ar","48000",
        str(out),"-y",
    ]
    r2 = subprocess.run(encode, capture_output=True)
    if r2.returncode != 0:
        print(r2.stderr.decode(errors="replace")[-2000:])
        raise RuntimeError(f"ffmpeg extract_video failed (exit {r2.returncode})")
    return out

def _whisper_cli():
    # Python 3.14 + PyTorch OpenMP segfaults; prefer base conda env (Python 3.13)
    for candidate in [
        Path.home()/"miniconda3/bin/whisper",
        Path.home()/"anaconda3/bin/whisper",
    ]:
        if candidate.exists():
            return str(candidate)
    return shutil.which("whisper") or "whisper"

def transcribe(audio, model_name):
    out_dir = audio.parent/"whisper_out"
    out_dir.mkdir(exist_ok=True)
    cli = _whisper_cli()
    stop = threading.Event()
    t = threading.Thread(target=_spin, args=("whisper transcribing", stop), daemon=True)
    t.start()
    r = subprocess.run(
        [cli, str(audio), "--model", model_name, "--word_timestamps", "True",
         "--output_format", "json", "--language", "en", "--output_dir", str(out_dir)],
        capture_output=True, text=True, timeout=600,
        env={**os.environ, "KMP_DUPLICATE_LIB_OK": "TRUE"},
    )
    stop.set(); t.join()
    if r.returncode != 0:
        print(r.stderr[-2000:]); raise RuntimeError(f"Whisper CLI failed (exit {r.returncode})")
    json_file = out_dir / (audio.stem + ".json")
    data = json.loads(json_file.read_text())
    words = [{"word": w["word"].strip(), "start": round(w["start"],3), "end": round(w["end"],3)}
             for seg in data.get("segments",[]) for w in seg.get("words",[])]
    return words, data.get("text","").strip()

def group_lines(words):
    lines,cur=[],[]
    for i,w in enumerate(words):
        if cur:
            gap=w["start"]-words[i-1]["end"]; prev=words[i-1]["word"]
            if gap>=PAUSE_THR or len(cur)>=MAX_WORDS or any(prev.endswith(p) for p in PUNCT_BREAK):
                lines.append({"text":" ".join(x["word"] for x in cur),"start":cur[0]["start"],"end":cur[-1]["end"]}); cur=[]
        cur.append(w)
    if cur: lines.append({"text":" ".join(x["word"] for x in cur),"start":cur[0]["start"],"end":cur[-1]["end"]})
    return lines

CLAUDE_TIMEOUT = 1800  # 30 min — long videos can generate 60+ elements

def call_claude(prompt):
    # Pass via stdin to avoid shell arg-length limits on large prompts
    r=subprocess.run(["claude","--output-format","json"],input=prompt,capture_output=True,text=True,timeout=CLAUDE_TIMEOUT)
    if not r.stdout.strip():
        raise RuntimeError(f"Claude CLI empty stdout. stderr: {r.stderr[:500]}")
    data=json.loads(r.stdout)
    for obj in data:
        if isinstance(obj,dict) and obj.get("type")=="result": return obj["result"]
    raise RuntimeError(f"Claude CLI no result object. stdout: {r.stdout[:300]}")

def _parse_bare_objects(text: str) -> list:
    """Parse a sequence of bare JSON objects {},{},... from text."""
    objects = []
    i = text.find("{")
    while i != -1 and i < len(text):
        depth, j, in_str, escape = 0, i, False, False
        while j < len(text):
            c = text[j]
            if escape:
                escape = False
            elif c == "\\" and in_str:
                escape = True
            elif c == '"':
                in_str = not in_str
            elif not in_str:
                if c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        try:
                            objects.append(json.loads(text[i:j + 1]))
                        except json.JSONDecodeError:
                            pass
                        i = text.find("{", j + 1)
                        break
            j += 1
        else:
            break
    return objects

def _extract_elements(raw: str) -> list:
    """Extract elements list from Claude response.

    Handles three formats Claude may return:
      1. {"elements": [...]}  — standard wrapped object
      2. [...]                — bare array
      3. {obj},{obj},...      — continuation: bare sequence of element objects
    """
    cleaned = re.sub(r"```(?:json)?\s*|\s*```", "", raw).strip()

    # Case 1: wrapped {"elements": [...]}
    s, e = cleaned.find("{"), cleaned.rfind("}")
    if s != -1 and e != -1:
        try:
            parsed = json.loads(cleaned[s:e + 1])
            if isinstance(parsed, dict):
                return parsed.get("elements", [parsed] if "type" in parsed else [])
        except json.JSONDecodeError:
            pass

    # Case 2: bare array [...]
    s2, e2 = cleaned.find("["), cleaned.rfind("]")
    if s2 != -1 and e2 != -1:
        try:
            parsed = json.loads(cleaned[s2:e2 + 1])
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass

    # Case 3: sequence of bare objects (Claude continuation response)
    objects = _parse_bare_objects(cleaned)
    if objects:
        return objects

    raise ValueError(f"No elements found in Claude response. First 300: {raw[:300]!r}")

def analyze(words, duration, full_text, cache_file=None, intensity="light"):
    if cache_file and cache_file.exists():
        print("  (cached)"); return json.loads(cache_file.read_text())
    prompt=_PROMPT.format(
        full_text=full_text,
        words_json=json.dumps(words),
        duration=int(duration),
        density_directive=_density_directive(intensity, duration),
        coverage_directive=_COVERAGE_DIRECTIVES.get(intensity, _COVERAGE_DIRECTIVES["light"]),
    )
    raw=call_claude(prompt)
    try:
        elements = _extract_elements(raw)
    except Exception as e:
        raise RuntimeError(f"Failed to parse Claude response as JSON: {e}\nRaw result (first 500): {raw[:500]!r}") from e
    if cache_file: cache_file.write_text(json.dumps(elements))
    return elements

def init_project(proj):
    proj.parent.mkdir(parents=True,exist_ok=True)
    if proj.exists(): shutil.rmtree(proj)
    subprocess.run(["npx","hyperframes@0.6.56","init",proj.name],cwd=str(proj.parent),check=True,capture_output=True)
    (proj/"assets").mkdir(exist_ok=True)

def render_project(proj, output_dir, slug):
    print("  Rendering (streaming output)...")
    # Homebrew ffmpeg has libx264; conda ffmpeg doesn't — prepend so HyperFrames finds the right one
    env = {**os.environ, "PATH": "/opt/homebrew/bin:" + os.environ.get("PATH","")}
    proc = subprocess.Popen(
        ["npx","hyperframes@0.6.56","render",".",
         "--quality","high",
         "--crf","16",
         "--fps","30",
         "--browser-gpu"],
        cwd=str(proj), env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    stderr_buf = []
    for line in proc.stdout:
        line = line.rstrip()
        stderr_buf.append(line)
        print(f"  {line}")
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError("Render failed")
    mp4s=sorted((proj/"renders").glob("*.mp4"),key=lambda p:p.stat().st_mtime)
    if not mp4s: raise RuntimeError("No MP4 in renders/")
    output_dir.mkdir(parents=True,exist_ok=True)
    dest=output_dir/f"{datetime.now().strftime('%Y-%m-%d')}_{slug}.mp4"
    shutil.copy2(mp4s[-1],dest); return dest

def run_pipeline(video: Path, slug: str, args):
    proj=Path(tempfile.gettempdir())/f"hf_{slug}"

    print(f"\n── HyperFrames Auto Pipeline ─────────────────────────")
    print(f"  Input:    {video.name}  Slug: {slug}")
    dur=args.duration or get_duration(video)
    vid_w, vid_h = get_video_dimensions(video)
    print(f"  Duration: {dur:.1f}s  Resolution: {vid_w}×{vid_h}  Project: {proj}")

    # Invalidate cached project if input video newer than cached clip,
    # or if user passed --fresh. Prevents reusing stale clip/audio/whisper/elements
    # when the input file at the same slug path was re-exported.
    cached_clip = proj/"assets"/"clip.mp4"
    force_fresh = getattr(args, "fresh", False)
    if proj.exists() and (force_fresh or (cached_clip.exists() and video.stat().st_mtime > cached_clip.stat().st_mtime)):
        reason = "--fresh" if force_fresh else f"input newer than cache ({video.stat().st_mtime:.0f} > {cached_clip.stat().st_mtime:.0f})"
        print(f"  Cache invalidated ({reason}) — wiping {proj}")
        shutil.rmtree(proj)

    if not (proj/"package.json").exists():
        print("\n[1/5] Init project...")
        init_project(proj)
    else:
        print("\n[1/5] Init project... (skip)")

    audio_file = proj/"audio.wav"
    clip_file  = proj/"assets"/"clip.mp4"
    if not audio_file.exists() or not clip_file.exists():
        print("[2/5] Extracting clips...")
        if not audio_file.exists(): extract_audio(video,proj,args.duration)
        if not clip_file.exists():  extract_video(video,proj,args.duration)
    else:
        print("[2/5] Extracting clips... (skip)")

    whisper_json = proj/"whisper_out"/(audio_file.stem+".json")
    if not whisper_json.exists():
        print("[3/5] Transcribing (Whisper)...")
        words,full_text=transcribe(audio_file,args.model)
    else:
        print("[3/5] Transcribing (Whisper)... (skip)")
        data=json.loads(whisper_json.read_text())
        words=[{"word":w["word"].strip(),"start":round(w["start"],3),"end":round(w["end"],3)}
               for seg in data.get("segments",[]) for w in seg.get("words",[])]
        full_text=data.get("text","").strip()
    lines=group_lines(words)
    print(f"  {len(words)} words → {len(lines)} caption lines")

    print(f"[4/5] Analyzing transcript (Claude)... intensity={args.intensity}")
    elements=analyze(words,dur,full_text,cache_file=proj/"elements.json",intensity=args.intensity)
    print(f"  {len(elements)} elements chosen:")
    for el in elements:
        print(f"    [{el['type']:16s}] {el['id']} @ {el['start_at']}s | {json.dumps(el.get('content',{}))[:70]}")

    print("[5/5] Generating HTML...")
    html_=generate_html(lines,elements,dur,"clip.mp4",show_captions=not args.no_captions,width=vid_w,height=vid_h)
    (proj/"index.html").write_text(html_,encoding="utf-8")

    if args.no_render:
        print(f"\n── Done (--no-render) ─────────────────────────────────")
        print(f"  cd {proj} && npm run render"); return None

    out_dir=args.output_dir if args.output_dir.is_absolute() else Path.cwd()/args.output_dir
    out=render_project(proj,out_dir,slug)
    print(f"\n── Done ───────────────────────────────────────────────")
    print(f"  {out}  ({out.stat().st_size/1048576:.1f} MB)")
    return out


def main():
    args=parse_args()

    if args.shorts:
        if not args.slug:
            sys.exit("--shorts requires --slug")
        shorts_dir = args.shorts_dir if args.shorts_dir.is_absolute() else Path.cwd()/args.shorts_dir
        pattern = f"{args.slug}_short_*.mp4"
        clips = sorted(shorts_dir.glob(pattern))
        if not clips:
            sys.exit(f"No shorts found matching {shorts_dir}/{pattern}")
        print(f"Found {len(clips)} shorts for slug '{args.slug}' — running up to 3 in parallel")
        from concurrent.futures import ThreadPoolExecutor, as_completed
        def _process(clip):
            short_slug = re.sub(r"[^a-z0-9]+","-", clip.stem.lower()).strip("-")
            return run_pipeline(clip.resolve(), short_slug, args)
        outputs = []
        with ThreadPoolExecutor(max_workers=7) as pool:
            futures = {pool.submit(_process, clip): clip for clip in clips}
            for fut in as_completed(futures):
                try:
                    out = fut.result()
                    if out: outputs.append(out)
                except Exception as exc:
                    print(f"  [error] {futures[fut].name}: {exc}")
        print(f"\n═══ Shorts complete: {len(outputs)}/{len(clips)} rendered ═══")
        for o in sorted(outputs):
            print(f"  {o}")
        return

    if args.input_video is None:
        sys.exit("Provide input_video or use --shorts --slug <slug>")
    video=args.input_video.resolve()
    if not video.exists(): sys.exit(f"Error: {video} not found")
    slug=args.slug or re.sub(r"[^a-z0-9]+","-",video.stem.lower()).strip("-")
    run_pipeline(video, slug, args)

if __name__=="__main__":
    main()
