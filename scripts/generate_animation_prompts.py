#!/usr/bin/env python3
"""
Parse [ANIMATION: ...] tags from a YouTube script and write Remotion component
prompts to content/prompts/<script_slug>_animation_prompts.txt.

Usage:
    python3 scripts/generate_animation_prompts.py <path-to-script.md>
"""

import re
import sys
from pathlib import Path
from datetime import date


# ---------------------------------------------------------------------------
# Brand constants — per niche
# ---------------------------------------------------------------------------

BRANDS: dict[str, dict] = {
    "Breath of Data Science": {
        "show": "Breath of Data Science",
        "palette": {
            "bg": "#1E1B2E",
            "surface": "rgba(255,255,255,0.05)",
            "accent": "#6B8FA8",
            "accent2": "#3D5F75",
            "text": "#f0f0f2",
            "muted": "rgba(240,240,242,0.50)",
        },
        "fonts": {"heading": "Space Grotesk", "body": "Space Grotesk"},
        "fps": 30,
    },
    "Breath of Life": {
        "show": "Breath of Life",
        "palette": {
            "bg": "#1E1B2E",
            "surface": "rgba(255,255,255,0.05)",
            "accent": "#E8705A",
            "accent2": "#B34A38",
            "text": "#f0f0f2",
            "muted": "rgba(240,240,242,0.50)",
        },
        "fonts": {"heading": "Lora", "body": "Nunito Sans"},
        "fps": 30,
    },
    "Breath of Poetry": {
        "show": "Breath of Poetry",
        "palette": {
            "bg": "#1E1B2E",
            "surface": "rgba(255,255,255,0.05)",
            "accent": "#B89850",
            "accent2": "#8A6E30",
            "text": "#f0f0f2",
            "muted": "rgba(240,240,242,0.50)",
        },
        "fonts": {"heading": "Playfair Display", "body": "DM Sans"},
        "fps": 30,
    },
}

NICHE_TO_SHOW: dict[str, str] = {
    "ds": "Breath of Data Science",
    "life": "Breath of Life",
    "poetry": "Breath of Poetry",
}

_DEFAULT_BRAND = BRANDS["Breath of Data Science"]


def get_brand(show: str) -> dict:
    for name, brand in BRANDS.items():
        if name.lower() in show.lower():
            return brand
    return _DEFAULT_BRAND


def get_brand_by_niche(niche: str) -> dict:
    return BRANDS[NICHE_TO_SHOW[niche]]


# convenience alias used by prompt builders — resolved per-call via meta
BRAND = _DEFAULT_BRAND

# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

ANIMATION_RE = re.compile(r"\[ANIMATION:\s*(.+?)\]", re.IGNORECASE)
META_SHOW_RE = re.compile(r"^SHOW:\s*(.+)$", re.MULTILINE)
META_TITLE_RE = re.compile(r"^EPISODE TITLE.*?:\s*(.+)$", re.MULTILINE)


def parse_script(path: Path) -> tuple[dict, list[dict]]:
    """Return (meta, animations) from a script file."""
    text = path.read_text(encoding="utf-8")

    show_match = META_SHOW_RE.search(text)
    title_match = META_TITLE_RE.search(text)

    show = show_match.group(1).strip() if show_match else _DEFAULT_BRAND["show"]
    brand = get_brand(show)
    meta = {
        "show": show,
        "episode_title": title_match.group(1).strip() if title_match else "",
        "script_path": str(path),
        "brand": brand,
    }

    animations = []
    for i, m in enumerate(ANIMATION_RE.finditer(text), start=1):
        raw = m.group(1).strip()

        # Extract duration hint if present (e.g. "5-second")
        dur_match = re.search(r"(\d+)-second", raw, re.IGNORECASE)
        duration_sec = int(dur_match.group(1)) if dur_match else 3

        # Classify type
        if "title card" in raw.lower():
            anim_type = "title_card"
        elif "outro card" in raw.lower():
            anim_type = "outro_card"
        elif "lower third" in raw.lower():
            anim_type = "lower_third"
        elif "transition" in raw.lower():
            anim_type = "transition"
        else:
            anim_type = "generic"

        # Extract quoted label if present
        label_match = re.search(r'"([^"]+)"', raw)
        label = label_match.group(1) if label_match else raw

        animations.append({
            "index": i,
            "raw": raw,
            "type": anim_type,
            "label": label,
            "duration_sec": duration_sec,
            "duration_frames": duration_sec * brand["fps"],
        })

    return meta, animations


# ---------------------------------------------------------------------------
# Prompt builders per animation type
# ---------------------------------------------------------------------------

def _brand_block(brand: dict) -> str:
    b = brand
    p = b["palette"]
    return f"""## Brand spec
- Show: {b['show']}
- FPS: {b['fps']}
- Background: {p['bg']}
- Surface: {p['surface']}
- Accent: {p['accent']}
- Accent2: {p['accent2']}
- Text: {p['text']}
- Muted: {p['muted']}
- Heading font: {b['fonts']['heading']}
- Body font: {b['fonts']['body']}"""


def build_prompt_title_card(anim: dict, meta: dict) -> str:
    b = meta["brand"]
    frames = anim["duration_frames"]
    fps = b["fps"]
    p = b["palette"]
    return f"""# Animation Prompt — Title Card
## Context
Script: {meta['script_path']}
Episode: {meta['episode_title']}
Raw tag: [{anim['raw']}]

## Task
Create a Remotion React component (`TitleCard.tsx`) that renders a {anim['duration_sec']}-second animated title card ({frames} frames at {fps} fps).

{_brand_block(b)}

## Text to display
"{anim['label']}"

## Animation spec
1. **0–8f**: Background fades in from transparent (opacity 0→1) over `{p['bg']}`.
2. **0–12f**: A horizontal accent line (2px, color `{p['accent']}`, width=60% of frame) slides in from left using `interpolate(frame, [0,12], ['-100%','0%'])` on `translateX`.
3. **6–20f**: Show name ("{meta['show']}") fades and slides up (translateY 20→0, opacity 0→1) using spring physics (`fps`, `damping:80`, `stiffness:200`).
4. **14–30f**: Main title text fades and slides up with a 3-frame stagger per line if multi-line. Use spring.
5. **{frames-10}–{frames}f**: Entire composition fades to black (opacity 1→0).

## Code requirements
- Single `TitleCard` exported component
- Accept props: `{{ titleText: string; showName: string; durationInFrames: number }}`
- Use `useCurrentFrame`, `useVideoConfig`, `interpolate`, `spring` from `remotion`
- No external libraries beyond `remotion`
- Heading font: {b['fonts']['heading']}

## Output
Full `TitleCard.tsx` file content, ready to drop into `remotion/src/compositions/`.
"""


def build_prompt_outro_card(anim: dict, meta: dict) -> str:
    b = meta["brand"]
    frames = anim["duration_frames"]
    fps = b["fps"]
    p = b["palette"]
    return f"""# Animation Prompt — Outro Card
## Context
Script: {meta['script_path']}
Episode: {meta['episode_title']}
Raw tag: [{anim['raw']}]

## Task
Create a Remotion React component (`OutroCard.tsx`) that renders a {anim['duration_sec']}-second animated outro/end-card ({frames} frames at {fps} fps).

{_brand_block(b)}

## Text to display
"{anim['label']}"

## Animation spec
1. **0–8f**: Background fades in (`{p['bg']}`).
2. **0–15f**: Subscribe nudge icon (bell emoji or SVG ring icon, color `{p['accent2']}`) bounces in from below using spring (`damping:60`).
3. **10–25f**: "Next up:" label fades in (muted color `{p['muted']}`, small caps, 14px).
4. **18–35f**: Next episode text (main body) slides and fades in with spring.
5. **{frames-12}–{frames}f**: Fade to black.

## Code requirements
- Single `OutroCard` exported component
- Accept props: `{{ nextText: string; episodeTitle: string; durationInFrames: number }}`
- Use `useCurrentFrame`, `useVideoConfig`, `interpolate`, `spring` from `remotion`
- No external libraries beyond `remotion`

## Output
Full `OutroCard.tsx` file content, ready to drop into `remotion/src/compositions/`.
"""


def build_prompt_lower_third(anim: dict, meta: dict) -> str:
    b = meta["brand"]
    frames = anim["duration_frames"]
    p = b["palette"]
    return f"""# Animation Prompt — Lower Third
## Context
Script: {meta['script_path']}
Raw tag: [{anim['raw']}]

## Task
Create a Remotion React component (`LowerThird.tsx`) for a {anim['duration_sec']}-second lower-third overlay ({frames} frames at {b['fps']} fps).

{_brand_block(b)}

## Text to display
"{anim['label']}"

## Animation spec
1. **0–10f**: Accent bar (4px tall, full width, color `{p['accent']}`) wipes in left→right.
2. **5–18f**: Text slides up from bar with spring + fade.
3. **{frames-10}–{frames}f**: Reverse — text fades out, bar wipes right→left.

## Code requirements
- Accept props: `{{ text: string; durationInFrames: number }}`
- Use `useCurrentFrame`, `interpolate`, `spring` from `remotion`
- Body font: {b['fonts']['body']}

## Output
Full `LowerThird.tsx` file.
"""


def build_prompt_generic(anim: dict, meta: dict) -> str:
    b = meta["brand"]
    frames = anim["duration_frames"]
    return f"""# Animation Prompt — {anim['type'].replace('_', ' ').title()}
## Context
Script: {meta['script_path']}
Raw tag: [{anim['raw']}]

## Task
Create a Remotion React component for a {anim['duration_sec']}-second animation ({frames} frames at {b['fps']} fps).

{_brand_block(b)}

## Description
"{anim['label']}"

## Animation spec
Design an animation that matches the description above. Follow the brand spec. Use spring physics for entrances, fade-to-black for exits. Keep motion purposeful — no decoration for its own sake.

## Code requirements
- Single exported component
- Use `useCurrentFrame`, `useVideoConfig`, `interpolate`, `spring` from `remotion`
- Accept relevant text/config as typed props

## Output
Full `.tsx` file content ready for `remotion/src/compositions/`.
"""


BUILDERS = {
    "title_card": build_prompt_title_card,
    "outro_card": build_prompt_outro_card,
    "lower_third": build_prompt_lower_third,
    "generic": build_prompt_generic,
    "transition": build_prompt_generic,
}


# ---------------------------------------------------------------------------
# TSX templates for rendering
# ---------------------------------------------------------------------------

def _brand_const_tsx(brand: dict) -> str:
    p = brand["palette"]
    lines = [
        f'const B_BG = "{p["bg"]}";',
        f'const B_SURFACE = "{p["surface"]}";',
        f'const B_ACCENT = "{p["accent"]}";',
        f'const B_ACCENT2 = "{p["accent2"]}";',
        f'const B_TEXT = "{p["text"]}";',
        f'const B_MUTED = "{p["muted"]}";',
    ]
    return "\n".join(lines)


_TITLE_CARD_TSX = """\
import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, spring, AbsoluteFill, random } from "remotion";

__BRAND__

const GLYPHS = "01<>[]{}().,;:=+-*/_|".split("");

export const __COMP__: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames, width, height } = useVideoConfig();

  const bgOp = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [durationInFrames - 12, durationInFrames], [1, 0], { extrapolateLeft: "clamp" });

  // animated grid scale + drift
  const gridScale = interpolate(spring({ frame, fps, config: { damping: 200 } }), [0, 1], [1.4, 1]);
  const gridY = (frame * 0.6) % 80;

  // code-rain columns
  const cols = 24;
  const rain = Array.from({ length: cols }, (_, i) => {
    const seed = i * 7.13;
    const speed = 2 + random(`s${i}`) * 4;
    const offset = random(`o${i}`) * height;
    const y = ((frame * speed + offset) % (height + 200)) - 200;
    const glyph = GLYPHS[Math.floor((frame / 4 + seed) % GLYPHS.length)];
    const op = 0.12 + random(`a${i}`) * 0.25;
    const x = (i + 0.5) * (width / cols);
    return { x, y, glyph, op, key: i };
  });

  // glitch offsets
  const glitchOn = frame > 14 && frame < 22;
  const glitchX = glitchOn ? (random(`g${Math.floor(frame / 2)}`) - 0.5) * 12 : 0;

  // chromatic aberration shimmer late
  const aberration = interpolate(frame, [22, 40, durationInFrames - 20, durationInFrames], [6, 2, 2, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // episode badge
  const badgeProg = spring({ frame: Math.max(0, frame - 4), fps, config: { damping: 14, stiffness: 180 } });
  const badgeRot = interpolate(frame, [0, 60], [0, 360]);

  // show subtitle
  const showProg = spring({ frame: Math.max(0, frame - 10), fps, config: { damping: 80, stiffness: 200 } });

  // title char-by-char reveal
  const title = "__LABEL__";
  const chars = title.split("");
  const titleStart = 18;

  // bottom progress bar
  const barProg = interpolate(frame, [10, durationInFrames - 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // corner brackets draw
  const cornerProg = spring({ frame: Math.max(0, frame - 6), fps, config: { damping: 100, stiffness: 120 } });
  const cornerLen = interpolate(cornerProg, [0, 1], [0, 120]);

  // scanline
  const scanY = (frame * 14) % height;

  return (
    <AbsoluteFill style={{ backgroundColor: B_BG, opacity: bgOp * fadeOut, fontFamily: "JetBrains Mono, monospace", overflow: "hidden" }}>
      {/* radial vignette */}
      <AbsoluteFill style={{ background: `radial-gradient(ellipse at center, transparent 30%, ${B_BG} 85%)`, zIndex: 5, pointerEvents: "none" }} />

      {/* grid */}
      <AbsoluteFill style={{ opacity: 0.18, transform: `scale(${gridScale}) translateY(${gridY}px)`, backgroundImage: `linear-gradient(${B_ACCENT}33 1px, transparent 1px), linear-gradient(90deg, ${B_ACCENT}33 1px, transparent 1px)`, backgroundSize: "80px 80px" }} />

      {/* code rain */}
      <AbsoluteFill>
        {rain.map((r) => (
          <div key={r.key} style={{ position: "absolute", left: r.x, top: r.y, color: B_ACCENT2, opacity: r.op, fontSize: 22, fontFamily: "JetBrains Mono, monospace", textShadow: `0 0 8px ${B_ACCENT2}` }}>
            {r.glyph}
          </div>
        ))}
      </AbsoluteFill>

      {/* scanline */}
      <div style={{ position: "absolute", left: 0, right: 0, top: scanY, height: 2, background: `linear-gradient(90deg, transparent, ${B_ACCENT}88, transparent)`, opacity: 0.6, zIndex: 3 }} />

      {/* corner brackets */}
      {[[60, 60, 1, 1], [width - 60, 60, -1, 1], [60, height - 60, 1, -1], [width - 60, height - 60, -1, -1]].map(([cx, cy, sx, sy], i) => (
        <svg key={i} width={140} height={140} style={{ position: "absolute", left: cx - 70, top: cy - 70, zIndex: 4 }}>
          <line x1={70} y1={70} x2={70 + sx * cornerLen} y2={70} stroke={B_ACCENT} strokeWidth={3} />
          <line x1={70} y1={70} x2={70} y2={70 + sy * cornerLen} stroke={B_ACCENT} strokeWidth={3} />
        </svg>
      ))}

      {/* episode badge top-left */}
      <div style={{ position: "absolute", top: 100, left: 100, display: "flex", alignItems: "center", gap: 20, opacity: badgeProg, transform: `translateY(${interpolate(badgeProg, [0, 1], [-30, 0])}px)`, zIndex: 6 }}>
        <div style={{ width: 64, height: 64, borderRadius: "50%", border: `2px dashed ${B_ACCENT}`, transform: `rotate(${badgeRot}deg)`, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div style={{ width: 36, height: 36, borderRadius: "50%", background: B_ACCENT, boxShadow: `0 0 24px ${B_ACCENT}` }} />
        </div>
        <div style={{ color: B_MUTED, fontSize: 16, letterSpacing: 6, textTransform: "uppercase" as const }}>
          ● REC<br/><span style={{ color: B_TEXT }}>EPISODE</span>
        </div>
      </div>

      {/* main center stack */}
      <AbsoluteFill style={{ display: "flex", justifyContent: "center", alignItems: "center", zIndex: 7 }}>
        <div style={{ textAlign: "center", padding: "0 8%", transform: `translateX(${glitchX}px)` }}>
          <div style={{ color: B_MUTED, fontSize: 22, letterSpacing: 8, textTransform: "uppercase" as const, marginBottom: 30, transform: `translateY(${interpolate(showProg, [0, 1], [30, 0])}px)`, opacity: interpolate(showProg, [0, 1], [0, 1]) }}>
            <span style={{ color: B_ACCENT }}>$</span> __SHOW__ <span style={{ opacity: (Math.floor(frame / 15) % 2) }}>▍</span>
          </div>
          {/* aberration title */}
          <div style={{ position: "relative", display: "inline-block" }}>
            <div style={{ position: "absolute", inset: 0, color: B_ACCENT, mixBlendMode: "screen" as const, transform: `translate(${-aberration}px, 0)`, opacity: 0.7 }}>
              {chars.map((c, i) => {
                const cp = spring({ frame: Math.max(0, frame - (titleStart + i * 1.2)), fps, config: { damping: 12, stiffness: 220 } });
                return <span key={i} style={{ display: "inline-block", opacity: cp }}>{c === " " ? "\\u00A0" : c}</span>;
              })}
            </div>
            <div style={{ position: "absolute", inset: 0, color: B_ACCENT2, mixBlendMode: "screen" as const, transform: `translate(${aberration}px, 0)`, opacity: 0.7 }}>
              {chars.map((c, i) => {
                const cp = spring({ frame: Math.max(0, frame - (titleStart + i * 1.2)), fps, config: { damping: 12, stiffness: 220 } });
                return <span key={i} style={{ display: "inline-block", opacity: cp }}>{c === " " ? "\\u00A0" : c}</span>;
              })}
            </div>
            <div style={{ color: B_TEXT, fontSize: 72, fontWeight: 800, lineHeight: 1.15, letterSpacing: -1, position: "relative" }}>
              {chars.map((c, i) => {
                const cp = spring({ frame: Math.max(0, frame - (titleStart + i * 1.2)), fps, config: { damping: 12, stiffness: 220 } });
                const cy = interpolate(cp, [0, 1], [40, 0]);
                return (
                  <span key={i} style={{ display: "inline-block", opacity: cp, transform: `translateY(${cy}px)` }}>
                    {c === " " ? "\\u00A0" : c}
                  </span>
                );
              })}
            </div>
          </div>
        </div>
      </AbsoluteFill>

      {/* bottom progress bar */}
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 6, background: `${B_ACCENT}22`, zIndex: 8 }}>
        <div style={{ width: `${barProg * 100}%`, height: "100%", background: `linear-gradient(90deg, ${B_ACCENT}, ${B_ACCENT2})`, boxShadow: `0 0 20px ${B_ACCENT}` }} />
      </div>
    </AbsoluteFill>
  );
};
"""

_OUTRO_CARD_TSX = """\
import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, spring, AbsoluteFill, random } from "remotion";

__BRAND__

export const __COMP__: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames, width, height } = useVideoConfig();
  const bgOp = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [durationInFrames - 14, durationInFrames], [1, 0], { extrapolateLeft: "clamp" });

  // floating particles
  const dots = Array.from({ length: 60 }, (_, i) => {
    const baseX = random(`px${i}`) * width;
    const baseY = random(`py${i}`) * height;
    const drift = Math.sin(frame * 0.02 + i) * 20;
    const r = 2 + random(`pr${i}`) * 4;
    const op = 0.15 + random(`po${i}`) * 0.4;
    return { x: baseX + drift, y: baseY + Math.cos(frame * 0.015 + i) * 15, r, op, key: i };
  });

  // radial pulse rings (3 staggered)
  const rings = [0, 20, 40].map((delay, i) => {
    const p = ((frame - delay) % 60) / 60;
    return { scale: 0.6 + p * 2.5, opacity: (1 - p) * 0.5, key: i };
  });

  // bell shake (after entrance)
  const bellEnter = spring({ frame, fps, config: { damping: 12, stiffness: 200 } });
  const shakeStart = 24;
  const shake = frame > shakeStart ? Math.sin((frame - shakeStart) * 0.8) * interpolate(frame, [shakeStart, shakeStart + 8, shakeStart + 30], [0, 14, 0], { extrapolateRight: "clamp" }) : 0;
  const bellY = interpolate(bellEnter, [0, 1], [60, 0]);

  // arrow draw (SVG)
  const arrowProg = spring({ frame: Math.max(0, frame - 18), fps, config: { damping: 60, stiffness: 120 } });

  // next-episode card slide-in
  const cardProg = spring({ frame: Math.max(0, frame - 28), fps, config: { damping: 18, stiffness: 140 } });
  const cardY = interpolate(cardProg, [0, 1], [80, 0]);

  // subscribe CTA pulse
  const ctaPulse = 1 + Math.sin(frame * 0.18) * 0.04;

  // countdown
  const cdStart = Math.max(0, durationInFrames - 90);
  const cd = Math.max(0, 3 - Math.floor((frame - cdStart) / 30));
  const showCd = frame >= cdStart;

  return (
    <AbsoluteFill style={{ backgroundColor: B_BG, opacity: bgOp * fadeOut, fontFamily: "Inter, sans-serif", overflow: "hidden" }}>
      {/* gradient backdrop */}
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 60%, ${B_ACCENT}22 0%, transparent 60%)` }} />

      {/* particles */}
      <AbsoluteFill>
        {dots.map((d) => (
          <div key={d.key} style={{ position: "absolute", left: d.x, top: d.y, width: d.r * 2, height: d.r * 2, borderRadius: "50%", background: B_ACCENT2, opacity: d.op, boxShadow: `0 0 ${d.r * 4}px ${B_ACCENT2}` }} />
        ))}
      </AbsoluteFill>

      {/* rings behind bell */}
      <AbsoluteFill style={{ display: "flex", justifyContent: "center", alignItems: "center" }}>
        <div style={{ position: "relative", width: 280, height: 280, marginTop: -200 }}>
          {rings.map((r) => (
            <div key={r.key} style={{ position: "absolute", inset: 0, borderRadius: "50%", border: `2px solid ${B_ACCENT}`, transform: `scale(${r.scale})`, opacity: r.opacity }} />
          ))}
        </div>
      </AbsoluteFill>

      {/* center content */}
      <AbsoluteFill style={{ display: "flex", flexDirection: "column" as const, justifyContent: "center", alignItems: "center", paddingTop: 80 }}>
        {/* bell with shake */}
        <div style={{ fontSize: 96, transform: `translate(${shake}px, ${bellY}px) rotate(${shake}deg)`, marginBottom: 28, filter: `drop-shadow(0 0 30px ${B_ACCENT})` }}>🔔</div>

        {/* subscribe CTA pill */}
        <div style={{ display: "flex", alignItems: "center", gap: 14, padding: "14px 32px", borderRadius: 999, background: B_ACCENT, color: B_BG, fontWeight: 700, fontSize: 22, letterSpacing: 2, textTransform: "uppercase" as const, opacity: interpolate(frame, [10, 24], [0, 1], { extrapolateLeft: "clamp" }), transform: `scale(${ctaPulse})`, boxShadow: `0 10px 40px ${B_ACCENT}66` }}>
          ▶ Subscribe
        </div>

        {/* divider with arrow */}
        <svg width={500} height={80} style={{ marginTop: 40 }}>
          <line x1={20} y1={40} x2={20 + arrowProg * 440} y2={40} stroke={B_MUTED} strokeWidth={2} strokeDasharray="6 6" />
          <polygon points={`${20 + arrowProg * 460},40 ${20 + arrowProg * 440},32 ${20 + arrowProg * 440},48`} fill={B_ACCENT} opacity={arrowProg} />
        </svg>

        {/* next-up card */}
        <div style={{ marginTop: 12, padding: "26px 44px", border: `1px solid ${B_ACCENT}55`, borderRadius: 18, background: `${B_SURFACE}cc`, backdropFilter: "blur(8px)", maxWidth: 900, textAlign: "center", opacity: cardProg, transform: `translateY(${cardY}px)`, boxShadow: `0 20px 60px rgba(0,0,0,0.4)` }}>
          <div style={{ color: B_MUTED, fontSize: 16, letterSpacing: 6, textTransform: "uppercase" as const, marginBottom: 14 }}>
            ▸ Next Up
          </div>
          <div style={{ color: B_TEXT, fontSize: 38, fontWeight: 700, lineHeight: 1.25 }}>
            __LABEL__
          </div>
        </div>
      </AbsoluteFill>

      {/* countdown */}
      {showCd && (
        <div style={{ position: "absolute", bottom: 60, right: 80, fontSize: 28, color: B_MUTED, fontFamily: "JetBrains Mono, monospace" }}>
          starts in <span style={{ color: B_ACCENT, fontSize: 40, fontWeight: 700 }}>{cd}</span>
        </div>
      )}
    </AbsoluteFill>
  );
};
"""

_LOWER_THIRD_TSX = """\
import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, spring, AbsoluteFill } from "remotion";

__BRAND__

export const __COMP__: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const cardProg = spring({ frame, fps, config: { damping: 16, stiffness: 160 } });
  const cardX = interpolate(cardProg, [0, 1], [-600, 0]);
  const exitProg = interpolate(frame, [durationInFrames - 14, durationInFrames], [0, 1], { extrapolateLeft: "clamp" });
  const exitX = interpolate(exitProg, [0, 1], [0, -800]);

  const accentScale = spring({ frame: Math.max(0, frame - 4), fps, config: { damping: 12, stiffness: 200 } });
  const accentRot = interpolate(frame, [0, durationInFrames], [0, 90]);

  const label = "__LABEL__";
  const chars = label.split("");
  const start = 8;

  const sweep = interpolate(frame, [10, 26], [-100, 200], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ display: "flex", alignItems: "flex-end", paddingBottom: 90, paddingLeft: 90, fontFamily: "Inter, sans-serif" }}>
      <div style={{ transform: `translateX(${cardX + exitX}px)`, display: "flex", alignItems: "center", gap: 24 }}>
        {/* rotating accent block */}
        <div style={{ position: "relative", width: 72, height: 72 }}>
          <div style={{ position: "absolute", inset: 0, background: B_ACCENT, transform: `rotate(${accentRot}deg) scale(${accentScale})`, borderRadius: 8, boxShadow: `0 0 30px ${B_ACCENT}88` }} />
          <div style={{ position: "absolute", inset: 18, background: B_BG, transform: `rotate(${-accentRot}deg)`, borderRadius: 4 }} />
        </div>

        {/* card */}
        <div style={{ position: "relative", padding: "20px 36px", background: `${B_SURFACE}ee`, borderLeft: `4px solid ${B_ACCENT}`, borderRadius: 12, backdropFilter: "blur(10px)", boxShadow: `0 12px 40px rgba(0,0,0,0.5)`, overflow: "hidden" }}>
          {/* shimmer sweep */}
          <div style={{ position: "absolute", top: 0, bottom: 0, left: `${sweep}%`, width: 80, background: `linear-gradient(90deg, transparent, ${B_ACCENT}33, transparent)`, transform: "skewX(-20deg)" }} />
          <div style={{ color: B_MUTED, fontSize: 14, letterSpacing: 4, textTransform: "uppercase" as const, marginBottom: 6 }}>
            ▍Concept
          </div>
          <div style={{ color: B_TEXT, fontSize: 38, fontWeight: 700, lineHeight: 1.2, position: "relative" }}>
            {chars.map((c, i) => {
              const cp = spring({ frame: Math.max(0, frame - (start + i * 0.8)), fps, config: { damping: 14, stiffness: 240 } });
              return (
                <span key={i} style={{ display: "inline-block", opacity: cp, transform: `translateY(${interpolate(cp, [0, 1], [16, 0])}px)` }}>
                  {c === " " ? "\\u00A0" : c}
                </span>
              );
            })}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
"""

_GENERIC_TSX = """\
import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, spring, AbsoluteFill, random } from "remotion";

__BRAND__

export const __COMP__: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames, width, height } = useVideoConfig();
  const fadeOut = interpolate(frame, [durationInFrames - 12, durationInFrames], [1, 0], { extrapolateLeft: "clamp" });

  // orbiting accent shapes
  const orbits = [0, 1, 2].map((i) => {
    const t = frame * 0.02 + i * 2.1;
    const radius = 280 + i * 60;
    return { x: Math.cos(t) * radius, y: Math.sin(t) * radius * 0.6, key: i, hue: i };
  });

  // background noise dots
  const noise = Array.from({ length: 80 }, (_, i) => ({
    x: random(`nx${i}`) * width,
    y: random(`ny${i}`) * height,
    r: 1 + random(`nr${i}`) * 2,
    op: 0.1 + random(`no${i}`) * 0.2,
    key: i,
  }));

  // word-by-word kinetic reveal
  const label = "__LABEL__";
  const words = label.split(" ");
  const start = 6;
  const perWord = 4;

  return (
    <AbsoluteFill style={{ backgroundColor: B_BG, opacity: fadeOut, fontFamily: "Inter, sans-serif", overflow: "hidden" }}>
      {/* diagonal gradient bg */}
      <AbsoluteFill style={{ background: `linear-gradient(135deg, ${B_SURFACE} 0%, ${B_BG} 50%, ${B_SURFACE} 100%)`, opacity: 0.5 }} />

      {/* noise */}
      <AbsoluteFill>
        {noise.map((n) => (
          <div key={n.key} style={{ position: "absolute", left: n.x, top: n.y, width: n.r * 2, height: n.r * 2, borderRadius: "50%", background: B_MUTED, opacity: n.op }} />
        ))}
      </AbsoluteFill>

      {/* orbiting shapes */}
      <AbsoluteFill style={{ display: "flex", justifyContent: "center", alignItems: "center" }}>
        <div style={{ position: "relative", width: 1, height: 1 }}>
          {orbits.map((o) => (
            <div key={o.key} style={{ position: "absolute", left: o.x, top: o.y, width: 80 - o.hue * 18, height: 80 - o.hue * 18, borderRadius: o.hue === 1 ? "50%" : 12, background: o.hue === 0 ? B_ACCENT : o.hue === 1 ? B_ACCENT2 : B_MUTED, opacity: 0.18, transform: `rotate(${frame * (o.hue + 1)}deg)`, boxShadow: `0 0 40px ${o.hue === 0 ? B_ACCENT : B_ACCENT2}66` }} />
          ))}
        </div>
      </AbsoluteFill>

      {/* word stack */}
      <AbsoluteFill style={{ display: "flex", justifyContent: "center", alignItems: "center", padding: "0 8%" }}>
        <div style={{ textAlign: "center", display: "flex", flexWrap: "wrap" as const, justifyContent: "center", gap: "0 18px", maxWidth: 1100 }}>
          {words.map((w, i) => {
            const wp = spring({ frame: Math.max(0, frame - (start + i * perWord)), fps, config: { damping: 14, stiffness: 180 } });
            const wy = interpolate(wp, [0, 1], [40, 0]);
            const ws = interpolate(wp, [0, 1], [0.85, 1]);
            const accent = i % 5 === 2;
            return (
              <span key={i} style={{ display: "inline-block", color: accent ? B_ACCENT : B_TEXT, fontSize: 64, fontWeight: 800, lineHeight: 1.15, letterSpacing: -1, opacity: wp, transform: `translateY(${wy}px) scale(${ws})`, textShadow: accent ? `0 0 30px ${B_ACCENT}55` : undefined }}>
                {w}
              </span>
            );
          })}
        </div>
      </AbsoluteFill>

      {/* underline accent */}
      <div style={{ position: "absolute", left: "20%", right: "20%", bottom: 120, height: 3, background: `linear-gradient(90deg, transparent, ${B_ACCENT}, transparent)`, transform: `scaleX(${spring({ frame: Math.max(0, frame - 10), fps, config: { damping: 60 } })})` }} />
    </AbsoluteFill>
  );
};
"""

_TSX_BY_TYPE = {
    "title_card": _TITLE_CARD_TSX,
    "outro_card": _OUTRO_CARD_TSX,
    "lower_third": _LOWER_THIRD_TSX,
    "generic": _GENERIC_TSX,
    "transition": _GENERIC_TSX,
}

_ANIM_ROOT_TSX = """\
import React from "react";
import { registerRoot, Composition } from "remotion";
__IMPORTS__

const AnimRoot: React.FC = () => (
  <>
__COMPOSITIONS__
  </>
);

registerRoot(AnimRoot);
"""


def _build_tsx(anim: dict, meta: dict, comp_name: str) -> str:
    tmpl = _TSX_BY_TYPE.get(anim["type"], _GENERIC_TSX)
    brand = meta["brand"]
    brand_const = _brand_const_tsx(brand)
    label = anim["label"].replace("<", "&lt;").replace(">", "&gt;")
    show = meta.get("show", _DEFAULT_BRAND["show"]).replace("<", "&lt;").replace(">", "&gt;")
    return (
        tmpl
        .replace("__BRAND__", brand_const)
        .replace("__COMP__", comp_name)
        .replace("__LABEL__", label)
        .replace("__SHOW__", show)
    )


# ---------------------------------------------------------------------------
# MP4 rendering
# ---------------------------------------------------------------------------

def render_animations(script_path: Path, animations: list[dict], meta: dict) -> list[Path]:
    import subprocess

    project_root = script_path.parent.parent.parent
    remotion_dir = project_root / "remotion"
    anim_comp_dir = remotion_dir / "src" / "compositions" / "animations"
    anim_comp_dir.mkdir(parents=True, exist_ok=True)
    out_dir = project_root / "output" / "animations"
    out_dir.mkdir(parents=True, exist_ok=True)

    slug = script_path.stem
    written: list[Path] = []

    try:
        comp_entries: list[tuple[str, int, Path]] = []
        for anim in animations:
            comp_name = f"Anim{anim['index']}"
            tsx = _build_tsx(anim, meta, comp_name)
            tsx_path = anim_comp_dir / f"{comp_name}.tsx"
            tsx_path.write_text(tsx, encoding="utf-8")
            written.append(tsx_path)
            out_mp4 = out_dir / f"{slug}_{anim['index']}_{anim['type']}.mp4"
            comp_entries.append((comp_name, anim["duration_frames"], out_mp4))

        imports = "\n".join(
            f'import {{ {c} }} from "./compositions/animations/{c}";'
            for c, _, _ in comp_entries
        )
        fps = meta["brand"]["fps"]
        compositions = "\n".join(
            f'    <Composition id="{c}" component={{{c}}} fps={{{fps}}} width={{1920}} height={{1080}} durationInFrames={{{d}}} />'
            for c, d, _ in comp_entries
        )
        root_content = (
            _ANIM_ROOT_TSX
            .replace("__IMPORTS__", imports)
            .replace("__COMPOSITIONS__", compositions)
        )
        root_path = remotion_dir / "src" / "anim_render_root.tsx"
        root_path.write_text(root_content, encoding="utf-8")
        written.append(root_path)

        rendered: list[Path] = []
        for comp_name, _, out_mp4 in comp_entries:
            print(f"  Rendering {comp_name} → {out_mp4.name} …")
            result = subprocess.run(
                ["npx", "remotion", "render",
                 "src/anim_render_root.tsx", comp_name, str(out_mp4)],
                cwd=remotion_dir,
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode != 0:
                print(f"  ERROR: {result.stderr[-600:]}")
            else:
                print(f"  ✓ {out_mp4}")
                rendered.append(out_mp4)

        return rendered

    finally:
        for f in written:
            if f.exists():
                f.unlink()
        try:
            anim_comp_dir.rmdir()
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _infer_week(script_path: Path) -> str | None:
    """Extract 2026-Wnn from script path, or return None."""
    import re
    m = re.search(r"(\d{4}-W\d{2})", str(script_path))
    return m.group(1) if m else None


def main() -> None:
    import argparse
    import subprocess

    parser = argparse.ArgumentParser(
        description="Parse [ANIMATION:] tags and write Remotion prompts (or render MP4s)."
    )
    parser.add_argument("script", help="Path to YouTube script .md file")
    parser.add_argument(
        "--niche", choices=["ds", "life", "poetry"],
        help="Niche shortcode — overrides SHOW: tag detection (ds, life, poetry)"
    )
    parser.add_argument(
        "--scene-plans", action="store_true",
        help="Also generate scene plan JSON via generate_scene_plans.py (infers --week from path)"
    )
    parser.add_argument(
        "--render", action="store_true",
        help="Render each animation to MP4 via Remotion (requires remotion/ project)"
    )
    args = parser.parse_args()

    script_path = Path(args.script).resolve()
    if not script_path.exists():
        print(f"Error: file not found — {script_path}")
        sys.exit(1)

    # Run scene plan generation first if requested
    if args.scene_plans:
        niche = args.niche
        if not niche:
            print("Error: --scene-plans requires --niche (ds, life, poetry)", file=sys.stderr)
            sys.exit(1)
        week = _infer_week(script_path)
        if not week:
            print("Error: could not infer ISO week from script path — pass to generate_scene_plans.py directly", file=sys.stderr)
            sys.exit(1)
        gen_sp = Path(__file__).parent / "generate_scene_plans.py"
        cmd = [sys.executable, str(gen_sp), "--script", str(script_path),
               "--niche", niche, "--week", week, "--mode", "short"]
        print(f"Running: {' '.join(cmd)}", file=sys.stderr)
        result = subprocess.run(cmd)
        if result.returncode != 0:
            sys.exit(result.returncode)

    meta, animations = parse_script(script_path)

    # Override brand with explicit --niche if provided
    if args.niche:
        meta["brand"] = get_brand_by_niche(args.niche)
        meta["show"] = NICHE_TO_SHOW[args.niche]

    if not animations:
        print(f"No [ANIMATION:] tags found in {script_path.name}")
        sys.exit(0)

    slug = script_path.stem

    # Always write text prompts
    out_dir = script_path.parent.parent.parent / "content" / "prompts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{slug}_animation_prompts.txt"

    separator = "\n" + "=" * 72 + "\n\n"
    blocks = []

    for anim in animations:
        builder = BUILDERS.get(anim["type"], build_prompt_generic)
        blocks.append(builder(anim, meta))
        print(f"  [{anim['index']}] {anim['type']} — \"{anim['label'][:60]}\"")

    out_path.write_text(separator.join(blocks), encoding="utf-8")
    print(f"\nWrote {len(animations)} prompt(s) → {out_path}")

    if args.render:
        print(f"\nRendering {len(animations)} animation(s) to MP4 …")
        outputs = render_animations(script_path, animations, meta)
        print(f"\nRendered {len(outputs)}/{len(animations)} MP4(s).")


if __name__ == "__main__":
    main()
