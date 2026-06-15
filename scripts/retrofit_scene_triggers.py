#!/usr/bin/env python3
"""
retrofit_scene_triggers.py — Re-anchor overlay scene timing triggers to the actual
spoken transcript (captions), without touching scene content.

Why: overlay scene `script` fields are verbatim excerpts from the WRITTEN script and
serve as the timing anchor in align_overlay_scenes. When a take is ad-libbed off-script,
those excerpts never appear in the transcript, so timing falls back to interpolation
(manifest `matched=False`). Captions are ground truth of what was actually said — Claude
maps each existing scene to the verbatim spoken phrase it should appear over, so the
deterministic strict matcher (run afterwards via patch_edit_plan_overlays.py) can anchor
precisely.

Non-destructive: only the `script` trigger is rewritten. componentName, props, layout,
and durationSec are preserved exactly. Scenes whose content was never spoken (e.g. code
snippets) keep their original trigger and stay honestly interpolated.

Usage:
  python3 scripts/retrofit_scene_triggers.py \\
    --overlay remotion/public/scene-plans/2026-W24/<slug>_overlay.json
  # --captions auto-resolves from remotion/public/captions/<week>/ when omitted

  python3 scripts/retrofit_scene_triggers.py --overlay <path> --captions <path> --dry-run
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.claude_cli import call_claude

REMOTION_PUBLIC = REPO / "remotion" / "public"
CAPTIONS_ROOT = REMOTION_PUBLIC / "captions"

# Props keys that carry human-readable display text worth showing Claude as context.
_PROPS_TEXT_KEYS = (
    "quote", "headline", "title", "text", "term", "definition", "label",
    "line", "lines", "caption", "description", "before", "after", "left", "right",
)


def extract_json(raw: str) -> list:
    """Parse a JSON array from Claude output, tolerating fences/preamble/trailing text."""
    raw = re.sub(r"```(?:json)?", "", raw)
    bracket = raw.find("[")
    if bracket < 0:
        raise json.JSONDecodeError("No JSON array found in output", raw, 0)
    result, _ = json.JSONDecoder().raw_decode(raw, bracket)
    return result


def build_transcript(captions: list) -> str:
    """Join caption entries into a single spoken-text string."""
    return " ".join(c.get("text", "").strip() for c in captions if c.get("text", "").strip())


def scene_display_text(scene: dict) -> str:
    """Pull the most descriptive human-readable text out of a scene's props."""
    props = scene.get("props", {})
    parts: list[str] = []
    for key in _PROPS_TEXT_KEYS:
        val = props.get(key)
        if isinstance(val, str) and val.strip():
            parts.append(val.strip())
        elif isinstance(val, list):
            parts.extend(str(v).strip() for v in val if str(v).strip())
    return " / ".join(parts)[:300]


def build_prompt(transcript: str, scenes: list) -> str:
    scene_lines = []
    for s in scenes:
        sid = s.get("sceneId", "?")
        comp = s.get("componentName", "?")
        cur = s.get("script", "")
        disp = scene_display_text(s)
        scene_lines.append(
            f'- {sid} [{comp}]: current_trigger="{cur}"' + (f' | shows="{disp}"' if disp else "")
        )
    scenes_block = "\n".join(scene_lines)
    return f"""You are aligning pre-designed video overlays to a spoken transcript.

Below is the TRANSCRIPT of what the speaker actually said (the delivery was partly
improvised, so it paraphrases the original script). Below that is an ordered list of
overlay SCENES. Each scene already has its content decided — your ONLY job is to find,
for each scene, the moment in the TRANSCRIPT where that overlay should appear.

For each scene return a "trigger": a VERBATIM excerpt of 5-15 consecutive words COPIED
EXACTLY from the TRANSCRIPT (same words, same spelling) marking when the overlay's moment
is spoken. The triggers must occur in non-decreasing order through the transcript
(scene-01's trigger at or before scene-02's, and so on).

If a scene's content was never actually spoken (e.g. a code snippet the speaker only
showed on screen), return "trigger": null for that scene — do not invent a location.

TRANSCRIPT (what the speaker actually said):
\"\"\"
{transcript}
\"\"\"

SCENES (in order):
{scenes_block}

Return ONLY a JSON array, one object per scene, in the same order:
[{{"sceneId": "scene-01", "trigger": "exact words copied from transcript"}}, ...]
Use null (not a string) when the content was never spoken. No prose, no markdown fences.
"""


def resolve_captions(overlay_path: Path, explicit: "str | None") -> "Path | None":
    if explicit:
        p = Path(explicit)
        return p if p.is_absolute() else (REPO / p)
    # Auto-resolve: overlay file lives under scene-plans/<week>/...; mirror to captions/<week>/.
    week = overlay_path.parent.name
    week_dir = CAPTIONS_ROOT / week
    if not week_dir.exists():
        return None
    candidates = sorted(week_dir.glob("*.captions.json")) + sorted(week_dir.glob("*.json"))
    if not candidates:
        return None
    # Heuristic: pick the caption file sharing the most slug tokens with the overlay name.
    overlay_tokens = set(re.split(r"[-_]", overlay_path.stem.lower()))
    best = max(
        candidates,
        key=lambda c: len(overlay_tokens & set(re.split(r"[-_.]", c.stem.lower()))),
    )
    return best


def main() -> None:
    parser = argparse.ArgumentParser(description="Re-anchor overlay triggers to the spoken transcript")
    parser.add_argument("--overlay", required=True, help="Path to overlay scene-plan JSON")
    parser.add_argument("--captions", default=None, help="Path to captions JSON (auto-resolved if omitted)")
    parser.add_argument("--model", default="claude-opus-4-8", help="Claude model id")
    parser.add_argument("--no-cache", action="store_true", help="Bypass cache, call Claude fresh")
    parser.add_argument("--dry-run", action="store_true", help="Print proposed triggers, don't write")
    args = parser.parse_args()

    overlay_path = Path(args.overlay)
    if not overlay_path.is_absolute():
        overlay_path = REPO / overlay_path
    if not overlay_path.exists():
        sys.exit(f"Overlay scene plan not found: {overlay_path}")

    captions_path = resolve_captions(overlay_path, args.captions)
    if not captions_path or not captions_path.exists():
        sys.exit(
            "Captions not found. Pass --captions explicitly "
            f"(looked under {CAPTIONS_ROOT / overlay_path.parent.name})."
        )

    scenes = json.loads(overlay_path.read_text())
    captions = json.loads(captions_path.read_text())
    transcript = build_transcript(captions)
    if not transcript:
        sys.exit(f"Captions file has no text: {captions_path}")

    print(f"[captions] {len(captions)} entries from {captions_path.name}")
    print(f"[scenes]   {len(scenes)} overlay scenes from {overlay_path.name}")

    prompt = build_prompt(transcript, scenes)
    raw = call_claude(
        prompt,
        cache=not args.no_cache,
        model=args.model,
        temperature=0.2,
        timeout=180,
        stream=True,
        progress_label="Mapping overlay scenes to spoken transcript",
    )

    try:
        mapping = extract_json(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Claude returned invalid JSON: {e}", file=sys.stderr)
        print("Raw (first 500):", raw[:500], file=sys.stderr)
        sys.exit(1)

    by_id = {m.get("sceneId"): m.get("trigger") for m in mapping if isinstance(m, dict)}

    rewritten = 0
    skipped = 0
    transcript_lower = transcript.lower()
    for scene in scenes:
        sid = scene.get("sceneId")
        trigger = by_id.get(sid)
        if isinstance(trigger, str) and trigger.strip():
            # Trust only verbatim triggers — they must actually be in the transcript so
            # the downstream strict matcher can anchor them. Otherwise leave untouched.
            if trigger.strip().lower() in transcript_lower:
                old = scene.get("script", "")
                scene["script"] = trigger.strip()
                rewritten += 1
                print(f"  {sid}: {old[:38]!r} → {trigger.strip()[:48]!r}")
            else:
                skipped += 1
                print(f"  {sid}: [skip] trigger not verbatim in transcript — kept original")
        else:
            skipped += 1
            print(f"  {sid}: [skip] not spoken (null) — kept original")

    print(f"\n── Summary ── rewritten {rewritten} / kept {skipped} / total {len(scenes)}")

    if args.dry_run:
        print("[dry-run] Not writing overlay JSON.")
        return

    overlay_path.write_text(json.dumps(scenes, indent=2, ensure_ascii=False))
    print(f"[overlay] written → {overlay_path.name}")
    print("\nNext: re-run patch_edit_plan_overlays.py to recompute atSec, then render_overlay_scenes.py.")


if __name__ == "__main__":
    main()
