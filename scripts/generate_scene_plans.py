#!/usr/bin/env python3
"""
generate_scene_plans.py — Use Claude CLI (Opus 4.8) to identify WHERE Remotion motion
graphics make the most sense in a YT script, then write a scene plan JSON.

No [ANIMATION:] tags required. Claude reads the full script semantically.

Usage:
  # Motion short (scenes ARE the video, sequential):
  python3 scripts/generate_scene_plans.py \\
    --script content/scripts/2026-W24/2026-06-08_data_science_tech_python-for-ml_yt.md \\
    --niche ds --week 2026-W24 --mode short

  # Long-form overlay (scenes inject at specific narration moments):
  python3 scripts/generate_scene_plans.py \\
    --script content/scripts/2026-W24/2026-06-08_data_science_tech_python-for-ml_yt.md \\
    --niche ds --week 2026-W24 --mode overlay

  # Dry-run (print plan, don't write file):
  python3 scripts/generate_scene_plans.py ... --dry-run

  # Bypass cache + regenerate:
  python3 scripts/generate_scene_plans.py ... --no-cache
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.claude_cli import call_claude

# Output: remotion/public/scene-plans/{week}/{slug}.json
SCENE_PLANS_ROOT = REPO / "remotion" / "public" / "scene-plans"
TEMPLATES_MAP_PATH = REPO / "remotion" / "public" / "templates-map.json"

NICHE_TEMPS = {"ds": 0.4, "life": 0.85, "poetry": 1.15}

NICHE_LABELS = {
    "ds": "Data Science / Python / Tech",
    "life": "Life & Self-Development / Habits / Mindset",
    "poetry": "Poetry / Quotes / Reflection",
}

# Tags injected by script generation that are editor hints, not script content.
EDITOR_TAGS = re.compile(
    r"\[(?:BROLL|SCREEN|ANIMATION|CODE_INSERT|PAUSE|PERSONAL_INSERT)[^\]]*\]",
    re.IGNORECASE,
)

def load_component_catalog(niche: str) -> str:
    """Build Claude prompt catalog from templates-map.json, filtered for niche."""
    data = json.loads(TEMPLATES_MAP_PATH.read_text())
    lines = ["Available Remotion components — use ONLY these exact names:\n"]
    for comp in data["scene_components"]:
        affinities = comp.get("niche_affinity", [])
        if affinities and niche not in affinities:
            continue
        source = comp.get("template_source", "custom")
        source_tag = f" [from {source} template]" if source != "custom" else ""
        lines.append(
            f"{comp['componentName']}{source_tag}\n"
            f"  When: {comp['use_when']}\n"
            f"  Props: {{ {comp['props']} }}\n"
            f"  Duration: {comp['duration_hint']}\n"
        )
    return "\n".join(lines)

SHORT_INSTRUCTIONS = """
You are analyzing a YouTube script for the niche: {niche_label}.

Your job: produce {shorts} DIFFERENT short-form videos from this ONE script. Each short is a
self-contained 30–60s motion video (no camera footage) built from 6–12 scenes played SEQUENTIALLY.

Think of it as slicing the script into {shorts} distinct angles — each short takes a DIFFERENT
hook, segment, or idea from the script and develops it into its own mini-story with its own
hook and payoff. Do NOT just re-cut the same moments {shorts} ways.

Rules for the SET of shorts:
- Each short must cover a DIFFERENT angle/segment of the script. Unique hook per short.
- No scene reuse across shorts — every scene belongs to exactly one short.
- Produce exactly {shorts} shorts.

Rules for EACH short:
- 6–12 scenes, played sequentially, self-contained (own hook + payoff).
- Per-short total durationSec MUST land in 30–60s.
- Each scene must use exactly one component from the catalog.
- Fill in the props with REAL content extracted from the script (actual data, actual code, actual words).
- The "script" field must be a SHORT verbatim excerpt (5–15 words) from the script that this scene accompanies.
- durationSec: DataVizReveal/CodeAnnotation/ToolComparison/CounterReveal = 6–8s; others = 4–6s.
- niche: use "{niche}" exactly.
- sceneId values: "scene-01", "scene-02", etc. (zero-padded index), restarting per short.

CREATIVE DIRECTION — you are the motion graphics director, not a caption writer:
- WordReveal is a LAST RESORT. Use it for at most 1 in 5 scenes (≤20% of total).
  Before placing a WordReveal, ask: can CounterReveal, DataVizReveal, AtmosphericQuote,
  NumberedTips, LineReveal, ImageTextReveal, or HandwrittenReveal carry this moment with more visual impact?
- CounterReveal: whenever the speaker mentions a specific number, stat, percentage, or metric.
- ImageTextReveal: narrative peaks, emotional beats, cinematic atmosphere — bold headline on image.
- HandwrittenReveal: poetry verses, intimate emotional lines, lyrical moments — life and poetry niche only.
- AtmosphericQuote: thesis lines, memorable one-liners, poem openings — never WordReveal for these.
- Every scene should SHOW and VISUALIZE — data, structure, emotion, contrast — not just caption words.

REQUIRED COMPONENT RULES (hard constraints — violating these is an error):
- If ANY number, stat, percentage, count, or metric appears in the script → at least ONE scene MUST use CounterReveal.
- If niche is life or poetry → at least ONE scene MUST use ImageTextReveal (pick the most cinematic/emotional moment).
- If niche is poetry → at least ONE scene MUST use HandwrittenReveal (pick a verse or lyrical line).
- EXACTLY ONE scene MUST use CUSTOM_SCENE_SLOT — pick the single most visually complex moment (data flow, abstract concept, emotional peak) where a generative motion graphic adds value no existing component can match. Set props.description to a clear 2–3 sentence brief for the visual.

Return a JSON array of {shorts} short objects. Each short object MUST have exactly these fields:
{{
  "shortId": "s01",
  "angle": "one-line unique angle/hook this short covers",
  "scenes": [
    {{
      "sceneId": "scene-01",
      "componentName": "ExactComponentName",
      "script": "verbatim excerpt 5–15 words",
      "niche": "{niche}",
      "durationSec": 6,
      "props": {{ ... component-specific props ... }}
    }}
  ]
}}

shortId values: "s01", "s02", etc. (zero-padded index).
Return ONLY the JSON array. No prose, no markdown fences, no explanation.
"""

OVERLAY_INSTRUCTIONS = """
You are analyzing a YouTube script for the niche: {niche_label}.

Your job: identify moments in this script where inserting a Remotion motion graphic as
an OVERLAY would amplify what the speaker is saying. These will appear briefly ON TOP of
the talking-head video while the speaker is talking.

Use your judgment on COUNT — base it on the script's content density:
- A data-heavy or concept-rich script may warrant many overlays (15–25).
- A storytelling or reflective script may only need a moderate number (12–18).
- Only pick moments where a visual genuinely adds value (showing data the speaker cites,
  illustrating a concept, displaying a code snippet the speaker references).
  Never insert one just to fill space.

LAYOUT SELECTION — every scene must have a "layout" field:
- "fullscreen": DataVizReveal, CodeAnnotation, ToolComparison, ConceptExplainer — these need full width to be legible.
  durationSec: 4–6 seconds.
- "panel-left" or "panel-right": WordReveal, NumberedTips, AtmosphericQuote,
  LineReveal, HabitLoop, TransformationArc — speaker stays visible, scene fills 1/3 of screen.
  Alternate left/right across consecutive panel scenes to avoid visual monotony.
  durationSec: 6–10 seconds (longer is fine since the speaker is still on screen).
- "panel-top": AtmosphericQuote, WordReveal, LineReveal — works as a cinematic banner above the speaker.
  Best for poetry/life niche when the moment calls for a moody atmosphere.
  Use sparingly: 1–2 per video at most. durationSec: 5–8 seconds.

MIX REQUIREMENT — the final set MUST include both fullscreen and panel scenes:
- At least 25% of scenes must be fullscreen (DataVizReveal, ToolComparison, CounterReveal, or CodeAnnotation if available).
- At least 25% of scenes must be panel (any panel layout).
- Never use only one layout type across the whole video.
- For each stat, number, or quantitative claim the speaker makes → prefer CounterReveal or DataVizReveal (fullscreen).
- For each explicit comparison the speaker makes → prefer ToolComparison (fullscreen).
- For concepts, quotes, and narrative moments → use panel scenes.

CREATIVE DIRECTION — you are the motion graphics director, not a caption writer:
- WordReveal is a LAST RESORT. Use it for at most 1 in 5 scenes (≤20% of total).
  Before placing a WordReveal, ask: can CounterReveal, DataVizReveal, AtmosphericQuote,
  NumberedTips, LineReveal, ImageTextReveal, or HandwrittenReveal carry this moment with more visual impact?
- CounterReveal: whenever the speaker cites a specific number, stat, percentage, or metric — animate it counting up.
- ImageTextReveal: narrative peaks, emotional beats, cinematic atmosphere — bold headline anchored on an image.
- HandwrittenReveal: poetry verses, intimate emotional lines, lyrical moments — life and poetry niche only.
- AtmosphericQuote: thesis lines, memorable one-liners, poem openings — prefer over WordReveal for these.
- Every scene should SHOW and VISUALIZE — data, structure, emotion, contrast — not just caption words.

REQUIRED COMPONENT RULES (hard constraints — violating these is an error):
- If ANY number, stat, percentage, count, or metric appears in the script → at least ONE scene MUST use CounterReveal.
- If niche is life or poetry → at least ONE scene MUST use ImageTextReveal (pick the most cinematic/emotional moment).
- If niche is poetry → at least ONE scene MUST use HandwrittenReveal (pick a verse or lyrical line).
- EXACTLY ONE scene MUST use CUSTOM_SCENE_SLOT — pick the single most visually complex moment (data flow, abstract concept, emotional peak) where a generative motion graphic adds value no existing component can match. Set props.description to a clear 2–3 sentence brief for the visual.

Rules:
- Each scene must use exactly one component from the catalog.
- Fill in the props with REAL content extracted from the script.
- The "script" field must be a SHORT verbatim excerpt (5–15 words) from the script marking when this overlay appears.
- niche: use "{niche}" exactly.
- USE ALL AVAILABLE COMPONENTS — do not default to the same 3–4 components. Actively look for
  moments that suit HabitLoop, LineReveal, AtmosphericQuote, DataVizReveal, TransformationArc,
  CounterReveal, ImageTextReveal, HandwrittenReveal, and ToolComparison, not just WordReveal and NumberedTips.
  Every component in the catalog should appear at least once if the script gives an opportunity.

Each object in the array MUST have exactly these fields:
{{
  "sceneId": "scene-01",
  "componentName": "ExactComponentName",
  "script": "verbatim excerpt 5–15 words",
  "niche": "{niche}",
  "durationSec": 5,
  "layout": "panel-left",
  "props": {{ ... component-specific props ... }}
}}

sceneId values: "scene-01", "scene-02", etc. (zero-padded index).
Return ONLY the JSON array. No prose, no markdown fences, no explanation.
"""


def clean_script(text: str) -> str:
    return EDITOR_TAGS.sub("", text).strip()


def parse_script_sections(text: str) -> str:
    """Return script content cleaned of editor tags, with section headers preserved."""
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        line = EDITOR_TAGS.sub("", line).rstrip()
        if line:
            cleaned.append(line)
    return "\n".join(cleaned)


def extract_json(raw: str) -> list:
    """Parse JSON array from Claude output.

    Handles: preamble prose, markdown fences, trailing text/explanation.
    Uses raw_decode so trailing content after ] is silently ignored.
    """
    # Strip markdown code fences first so they don't land inside the search window
    raw = re.sub(r"```(?:json)?", "", raw)
    bracket = raw.find("[")
    if bracket < 0:
        raise json.JSONDecodeError("No JSON array found in output", raw, 0)
    result, _ = json.JSONDecoder().raw_decode(raw, bracket)
    return result


VALID_LAYOUTS = {"fullscreen", "panel-left", "panel-right", "panel-top"}

# These components hardcode widths that break at 1/3 screen (~640px).
# Automatically coerced to "fullscreen" if the model assigns a panel layout.
FULLSCREEN_ONLY_COMPONENTS = {"DataVizReveal", "CodeAnnotation", "ToolComparison", "ConceptExplainer", "CounterReveal", "HandwrittenReveal", "ImageTextReveal"}


def validate_scene(scene: dict, index: int) -> None:
    required = {"sceneId", "componentName", "script", "niche", "durationSec", "props"}
    missing = required - set(scene.keys())
    if missing:
        raise ValueError(f"Scene {index} missing fields: {missing}")
    if not isinstance(scene["props"], dict):
        raise ValueError(f"Scene {index} props must be a dict, got {type(scene['props'])}")
    if not isinstance(scene["durationSec"], (int, float)):
        raise ValueError(f"Scene {index} durationSec must be a number")
    if "layout" in scene and scene["layout"] not in VALID_LAYOUTS:
        raise ValueError(f"Scene {index} layout '{scene['layout']}' invalid — must be one of {VALID_LAYOUTS}")
    component = scene.get("componentName", "")
    layout = scene.get("layout")
    if component in FULLSCREEN_ONLY_COMPONENTS and layout and layout != "fullscreen":
        print(
            f"  [warn] Scene {index} ({component}) assigned '{layout}' — component requires full width;"
            " coercing to 'fullscreen'",
            file=sys.stderr,
        )
        scene["layout"] = "fullscreen"


def build_prompt(script_text: str, niche: str, mode: str, shorts: int = 7) -> str:
    niche_label = NICHE_LABELS.get(niche, niche)
    if mode == "short":
        instructions = SHORT_INSTRUCTIONS.format(
            niche_label=niche_label, niche=niche, shorts=shorts
        )
    else:
        instructions = OVERLAY_INSTRUCTIONS.format(niche_label=niche_label, niche=niche)
    catalog = load_component_catalog(niche)
    return f"""{instructions}

COMPONENT CATALOG:
{catalog}

SCRIPT:
{script_text}
"""


def slug_from_script_path(script_path: Path) -> str:
    name = script_path.stem
    # Strip _yt suffix if present
    if name.endswith("_yt"):
        name = name[:-3]
    return name


def output_path(week: str, slug: str, mode: str) -> Path:
    suffix = "_overlay" if mode == "overlay" else ""
    return SCENE_PLANS_ROOT / week / f"{slug}{suffix}.json"


def short_output_path(week: str, slug: str, short_id: str) -> Path:
    return SCENE_PLANS_ROOT / week / f"{slug}_{short_id}.json"


def total_duration(scenes: list) -> float:
    return sum(s.get("durationSec", 0) for s in scenes)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Remotion scene plan from YT script using Claude")
    parser.add_argument("--script", required=True, help="Path to YT script markdown file")
    parser.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    parser.add_argument("--week", required=True, help="ISO week e.g. 2026-W24")
    parser.add_argument("--mode", choices=["short", "overlay"], default="short",
                        help="short = sequential scenes for motion short; overlay = inject into long-form")
    parser.add_argument("--shorts", type=int, default=7,
                        help="Number of unique shorts to generate (short mode only)")
    parser.add_argument("--slug", default=None,
                        help="Override output slug (must match prepare_remotion_edit.py --slug to auto-wire)")
    parser.add_argument("--dry-run", action="store_true", help="Print plan, don't write file")
    parser.add_argument("--no-cache", action="store_true", help="Bypass cache, call Claude fresh")
    args = parser.parse_args()

    script_path = Path(args.script)
    if not script_path.is_absolute():
        script_path = REPO / script_path
    if not script_path.exists():
        print(f"ERROR: script not found: {script_path}", file=sys.stderr)
        sys.exit(1)

    raw_script = script_path.read_text()
    script_text = parse_script_sections(raw_script)

    prompt = build_prompt(script_text, args.niche, args.mode, args.shorts)

    temp = NICHE_TEMPS[args.niche]
    # Short mode emits {shorts}× the output of a single plan — give Claude more time.
    timeout = 600 if args.mode == "short" else 180
    print(f"Calling Claude Opus 4.8 (temp={temp}, mode={args.mode}, "
          f"{f'shorts={args.shorts}, ' if args.mode == 'short' else ''}"
          f"cache={'off' if args.no_cache else 'on'})...", file=sys.stderr)

    raw = call_claude(
        prompt,
        cache=not args.no_cache,
        model="claude-opus-4-8",
        temperature=temp,
        timeout=timeout,
        stream=True,
        progress_label=f"Analyzing script for {args.niche.upper()} scene plan",
    )

    try:
        parsed = extract_json(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Claude returned invalid JSON: {e}", file=sys.stderr)
        print("Raw output (first 500 chars):", raw[:500], file=sys.stderr)
        sys.exit(1)

    if not isinstance(parsed, list):
        print(f"ERROR: Expected JSON array, got {type(parsed)}", file=sys.stderr)
        sys.exit(1)

    slug = args.slug if args.slug else slug_from_script_path(script_path)

    if args.mode == "short":
        write_shorts(parsed, slug, args)
    else:
        write_overlay(parsed, slug, args)


def write_overlay(scenes: list, slug: str, args) -> None:
    errors = []
    for i, scene in enumerate(scenes):
        try:
            validate_scene(scene, i)
        except ValueError as e:
            errors.append(str(e))
    if errors:
        print("ERROR: Scene validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    out_path = output_path(args.week, slug, args.mode)
    components_used = [s["componentName"] for s in scenes]
    print(f"\n{len(scenes)} scenes generated:")
    for i, s in enumerate(scenes):
        print(f"  {i+1:2d}. {s['componentName']:<22} — \"{s['script'][:60]}\"")
    print(f"\nComponents: {', '.join(dict.fromkeys(components_used))}")

    if args.dry_run:
        print("\n[dry-run] Not writing file.")
        print(json.dumps(scenes, indent=2))
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(scenes, indent=2))
    print(f"\n✓ Written: {out_path.relative_to(REPO)}")


def write_shorts(shorts: list, slug: str, args) -> None:
    if len(shorts) != args.shorts:
        print(f"ERROR: Requested {args.shorts} shorts, Claude returned {len(shorts)}",
              file=sys.stderr)
        sys.exit(1)

    errors = []
    for si, short in enumerate(shorts):
        if not isinstance(short, dict):
            errors.append(f"Short {si} is not an object")
            continue
        if not short.get("angle"):
            errors.append(f"Short {si} missing 'angle'")
        scenes = short.get("scenes")
        if not isinstance(scenes, list) or not scenes:
            errors.append(f"Short {si} missing/empty 'scenes'")
            continue
        for i, scene in enumerate(scenes):
            try:
                validate_scene(scene, i)
            except ValueError as e:
                errors.append(f"Short {si}: {e}")

    if errors:
        print("ERROR: Shorts validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    # Duration warnings (non-fatal) — per-short total should land 30–60s.
    print(f"\n{len(shorts)} shorts generated:")
    for si, short in enumerate(shorts):
        scenes = short["scenes"]
        dur = total_duration(scenes)
        short_id = short.get("shortId") or f"s{si + 1:02d}"
        flag = "" if 30 <= dur <= 60 else "  ⚠ out of 30–60s range"
        print(f"  {short_id}: {len(scenes):2d} scenes, {dur:.0f}s — \"{short['angle'][:50]}\"{flag}")
        if not (30 <= dur <= 60):
            print(f"  [warn] Short {short_id} duration {dur:.0f}s outside 30–60s",
                  file=sys.stderr)

    if args.dry_run:
        print("\n[dry-run] Not writing files.")
        print(json.dumps(shorts, indent=2))
        return

    for si, short in enumerate(shorts):
        short_id = short.get("shortId") or f"s{si + 1:02d}"
        out_path = short_output_path(args.week, slug, short_id)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # Write plain scenes array — keeps Remotion composition prop format unchanged.
        out_path.write_text(json.dumps(short["scenes"], indent=2))
        print(f"  ✓ {out_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
