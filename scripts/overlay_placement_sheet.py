#!/usr/bin/env python3
"""
overlay_placement_sheet.py — Generate a manual-edit placement sheet for overlay scenes.

For a given week (and niche), reads the overlay scene plan(s), and writes a Markdown
sheet listing each scene's timestamp, duration, clip filename, and on-screen text — so
you can drop the pre-rendered overlay clips onto your talking-head timeline in DaVinci
at the right moments. No rendering, no compositing — full manual control.

Run this during the manual video edit, after overlay scenes are rendered
(render_overlay_scenes.py) and aligned (patch_edit_plan_overlays.py).

Usage:
  python3 scripts/overlay_placement_sheet.py --week 2026-W24
  python3 scripts/overlay_placement_sheet.py --week 2026-W24 --niche poetry
"""

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

# Reuse overlay-plan resolution, output dir, and the clip-naming convention.
from render_overlay_scenes import find_overlay_plan, output_dir

# Props keys carrying human-readable display text, in priority order.
_PROPS_TEXT_KEYS = (
    "quote", "headline", "title", "text", "term", "definition",
    "line", "lines", "label", "before", "after", "number", "value",
)


def mmss(sec: float) -> str:
    s = int(round(sec))
    return f"{s // 60}:{s % 60:02d}"


def scene_shows(scene: dict) -> str:
    props = scene.get("props", {})
    parts: list[str] = []
    for key in _PROPS_TEXT_KEYS:
        val = props.get(key)
        if isinstance(val, str) and val.strip():
            parts.append(val.strip())
        elif isinstance(val, list):
            parts.extend(str(v).strip() for v in val if str(v).strip())
    return " / ".join(parts)[:90] if parts else "(visual / animation — no text)"


def clip_filename(niche: str, scene: dict) -> str:
    # Mirrors render_overlay_scenes.render_scene: f"{niche}_{sceneId}_{component}.mp4"
    return f"{niche}_{scene.get('sceneId','scene')}_{scene.get('componentName','Scene')}.mp4"


def build_sheet(week: str, niche: str, scenes: list) -> str:
    interp = [s for s in scenes if s.get("atSecSource") == "interp"]
    lines = [
        f"# {niche.upper()} — Manual Overlay Placement ({week})",
        "",
        f"**Clips:** `output/animations/{week}/overlay-scenes/{niche}_scene-*.mp4`",
        "",
        "## How (DaVinci, minimal friction)",
        "1. Talking-head video on track **V1**.",
        "2. Each overlay clip on **V2 above it**, starting at its **Time**. Clips are full-frame "
        "with an opaque background → they fully cover V1 for their **Dur** = a clean cutaway. No scaling needed.",
        "3. Want the speaker still visible? Scale the V2 clip to ~35% and park it left/right — the card reads as a side panel.",
        "",
        "## ⚠️ Timing rule",
        "Times are measured from your **first spoken word**. If your edited timeline has an intro or "
        "lead silence before the first word, **add that offset to every Time**.",
        "",
    ]
    if interp:
        ids = ", ".join(s.get("sceneId", "?") for s in interp)
        lines += [
            f"> ⚠️ **{len(interp)} scene(s) have estimated (interpolated) times** — {ids}. "
            "These weren't spoken verbatim (e.g. on-screen code or heavy paraphrase); eyeball and nudge them.",
            "",
        ]
    lines += [
        "## Placement table",
        "",
        f"| # | Time | Dur | File (in `overlay-scenes/`) | Exact? | Shows on screen |",
        "|---|------|-----|------------------------------|--------|-----------------|",
    ]
    for s in scenes:
        num = s.get("sceneId", "scene-??").replace("scene-", "")
        at = s.get("atSec")
        time = mmss(at) if isinstance(at, (int, float)) else "?"
        dur = f"{s.get('durationSec','?')}s"
        fname = f"`{clip_filename(niche, s)}`"
        exact = "✓" if s.get("atSecSource") == "anchor" else "~est"
        lines.append(f"| {num} | {time} | {dur} | {fname} | {exact} | {scene_shows(s)} |")
    lines.append("")
    lines.append("Filename pattern: `" + niche + "_scene-NN_<Component>.mp4`. `Exact? ✓` = anchored to a verbatim spoken phrase; `~est` = interpolated estimate.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate manual overlay placement sheet(s)")
    parser.add_argument("--week", required=True, help="ISO week, e.g. 2026-W24")
    parser.add_argument("--niche", choices=["ds", "life", "poetry"], help="Only this niche (default: all)")
    args = parser.parse_args()

    niches = [args.niche] if args.niche else ["ds", "life", "poetry"]
    out_dir = output_dir(args.week)
    wrote = 0
    for niche in niches:
        plan_path = find_overlay_plan(args.week, niche)
        if not plan_path:
            print(f"  [skip] no overlay plan for {niche} in {args.week}")
            continue
        scenes = json.loads(plan_path.read_text())
        sheet = build_sheet(args.week, niche, scenes)
        out_file = out_dir / f"{niche.upper()}_PLACEMENT.md"
        out_file.write_text(sheet)
        anchored = sum(1 for s in scenes if s.get("atSecSource") == "anchor")
        print(f"  [{niche}] {len(scenes)} scenes ({anchored} exact) → {out_file.relative_to(REPO)}")
        wrote += 1

    if not wrote:
        print("No sheets written.")
        sys.exit(1)


if __name__ == "__main__":
    main()
