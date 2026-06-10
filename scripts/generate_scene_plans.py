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

COMPONENT_CATALOG = """
Available Remotion components — use ONLY these exact names:

DataVizReveal
  When: citing a number, statistic, comparison, or data trend.
  Props: { "title": str, "data": [{"label": str, "value": number}], "chartType": "bar"|"line"|"number" }

CodeAnnotation
  When: showing or explaining a code snippet, function, or syntax.
  Props: { "code": str, "language": str, "highlight": [lineNumber], "annotation": str }
  (highlight and annotation are optional)

ConceptExplainer
  When: introducing a term, concept, or framework the viewer may not know.
  Props: { "term": str, "definition": str, "analogy": str }
  (analogy is optional)

ToolComparison
  When: comparing two approaches, tools, libraries, or strategies side by side.
  Props: { "left": {"label": str, "points": [str]}, "right": {"label": str, "points": [str]} }

NumberedTips
  When: listing 3–5 steps, rules, principles, or tips.
  Props: { "title": str, "tips": [{"number": int, "text": str}] }

TransformationArc
  When: describing a before/after shift, problem/solution, or growth story.
  Props: { "before": str, "after": str, "label": str }
  (label is optional, e.g. "The shift")

HabitLoop
  When: describing a cycle, feedback loop, or recurring system or process.
  Props: { "title": str, "phases": [{"label": str}] }

WordReveal
  When: a short powerful phrase, key term, or memorable line should land hard.
  Props: { "words": [str], "emphasis": [int] }
  (emphasis = 0-based indices of the words to bold)

AtmosphericQuote
  When: a full-screen quote, thesis statement, poem title, or poetic moment.
  Props: { "quote": str, "attribution": str }
  (attribution is optional)

LineReveal
  When: a poem, verse, lyric, or multi-line revelation should appear line by line.
  Props: { "lines": [str] }
"""

SHORT_INSTRUCTIONS = """
You are analyzing a YouTube script for the niche: {niche_label}.

Your job: identify 6–12 moments in this script where a Remotion motion graphic would make
the content more engaging, clearer, or more memorable. These scenes will be played SEQUENTIALLY
and together they will form a short-form video (no camera footage).

Rules:
- Cover the script's full arc (intro, middle, end).
- Choose scenes that visualize or amplify the most impactful moments.
- Each scene must use exactly one component from the catalog.
- Fill in the props with REAL content extracted from the script (actual data, actual code, actual words).
- The "script" field must be a SHORT verbatim excerpt (5–15 words) from the script that this scene accompanies.
- durationSec: DataVizReveal/CodeAnnotation/ToolComparison = 6–8s; others = 4–6s.
- niche: use "{niche}" exactly.

Return ONLY a valid JSON array. No prose, no markdown fences, no explanation.
"""

OVERLAY_INSTRUCTIONS = """
You are analyzing a YouTube script for the niche: {niche_label}.

Your job: identify 3–6 moments in this script where inserting a Remotion motion graphic as
an OVERLAY would amplify what the speaker is saying. These will appear briefly ON TOP of
the talking-head video while the speaker is talking — so be conservative, only pick moments
where a visual genuinely adds value (showing data the speaker cites, illustrating a concept,
displaying a code snippet the speaker references).

Rules:
- Be selective — not every section needs a graphic. Only the moments where a visual is truly additive.
- Each scene must use exactly one component from the catalog.
- Fill in the props with REAL content extracted from the script.
- The "script" field must be a SHORT verbatim excerpt (5–15 words) from the script marking when this overlay appears.
- durationSec: 4–6 seconds maximum (these are overlays, not full replacements).
- niche: use "{niche}" exactly.

Return ONLY a valid JSON array. No prose, no markdown fences, no explanation.
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
    """Parse JSON from Claude output, stripping markdown fences if present."""
    raw = raw.strip()
    # Strip ```json ... ``` or ``` ... ```
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()
    return json.loads(raw)


def validate_scene(scene: dict, index: int) -> None:
    required = {"sceneId", "componentName", "script", "niche", "durationSec", "props"}
    missing = required - set(scene.keys())
    if missing:
        raise ValueError(f"Scene {index} missing fields: {missing}")
    if not isinstance(scene["props"], dict):
        raise ValueError(f"Scene {index} props must be a dict, got {type(scene['props'])}")
    if not isinstance(scene["durationSec"], (int, float)):
        raise ValueError(f"Scene {index} durationSec must be a number")


def build_prompt(script_text: str, niche: str, mode: str) -> str:
    niche_label = NICHE_LABELS.get(niche, niche)
    instructions = (SHORT_INSTRUCTIONS if mode == "short" else OVERLAY_INSTRUCTIONS).format(
        niche_label=niche_label, niche=niche
    )
    return f"""{instructions}

COMPONENT CATALOG:
{COMPONENT_CATALOG}

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


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Remotion scene plan from YT script using Claude")
    parser.add_argument("--script", required=True, help="Path to YT script markdown file")
    parser.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    parser.add_argument("--week", required=True, help="ISO week e.g. 2026-W24")
    parser.add_argument("--mode", choices=["short", "overlay"], default="short",
                        help="short = sequential scenes for motion short; overlay = inject into long-form")
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

    prompt = build_prompt(script_text, args.niche, args.mode)

    temp = NICHE_TEMPS[args.niche]
    print(f"Calling Claude Opus 4.8 (temp={temp}, mode={args.mode}, cache={'off' if args.no_cache else 'on'})...",
          file=sys.stderr)

    raw = call_claude(
        prompt,
        cache=not args.no_cache,
        model="claude-opus-4-8",
        temperature=temp,
        timeout=180,
        stream=True,
        progress_label=f"Analyzing script for {args.niche.upper()} scene plan",
    )

    try:
        scenes = extract_json(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Claude returned invalid JSON: {e}", file=sys.stderr)
        print("Raw output (first 500 chars):", raw[:500], file=sys.stderr)
        sys.exit(1)

    if not isinstance(scenes, list):
        print(f"ERROR: Expected JSON array, got {type(scenes)}", file=sys.stderr)
        sys.exit(1)

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

    slug = slug_from_script_path(script_path)
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


if __name__ == "__main__":
    main()
