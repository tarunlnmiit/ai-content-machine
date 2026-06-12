#!/usr/bin/env python3
"""
patch_edit_plan_overlays.py — Align an overlay scene plan to captions and inject
scenePlanFile into an existing edit plan that was generated before the overlay existed.

Run this when:
  - An edit plan was generated before generate_scene_plans.py --mode overlay ran
  - OR the overlay file has a different slug prefix than the edit plan

Usage:
  python3 scripts/patch_edit_plan_overlays.py \\
    --edit-plan remotion/public/edit-plans/2026-W24/<slug>.json \\
    --overlay   remotion/public/scene-plans/2026-W24/<slug>_overlay.json

The overlay JSON is updated in-place with atSec timestamps.
The edit plan JSON gains a scenePlanFile field (relative to remotion/public/).
"""

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REMOTION_PUBLIC = REPO / "remotion" / "public"
sys.path.insert(0, str(REPO / "scripts"))

from prepare_remotion_edit import align_overlay_scenes  # reuse existing logic


def relative_to_public(path: Path) -> str:
    return str(path.relative_to(REMOTION_PUBLIC))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--edit-plan", required=True, help="Path to edit plan JSON")
    parser.add_argument("--overlay", required=True, help="Path to overlay scene plan JSON")
    args = parser.parse_args()

    edit_plan_path = Path(args.edit_plan)
    if not edit_plan_path.is_absolute():
        edit_plan_path = REPO / edit_plan_path

    overlay_path = Path(args.overlay)
    if not overlay_path.is_absolute():
        overlay_path = REPO / overlay_path

    if not edit_plan_path.exists():
        sys.exit(f"Edit plan not found: {edit_plan_path}")
    if not overlay_path.exists():
        sys.exit(f"Overlay scene plan not found: {overlay_path}")

    plan = json.loads(edit_plan_path.read_text())
    scenes = json.loads(overlay_path.read_text())

    # Load captions via path stored in the edit plan
    captions_rel = plan.get("captionsFile", "")
    captions_path = REMOTION_PUBLIC / captions_rel
    captions: list = []
    if captions_path.exists():
        captions = json.loads(captions_path.read_text())
        print(f"[captions] {len(captions)} tokens from {captions_path.name}")
    else:
        print(f"[captions] not found at {captions_path}, using even spacing")

    aligned = align_overlay_scenes(scenes, captions)
    matched = sum(1 for s in aligned if "atSec" in s)
    print(f"[scenes] {matched}/{len(aligned)} overlay scenes aligned to captions")

    overlay_path.write_text(json.dumps(aligned, indent=2))
    print(f"[overlay] written → {overlay_path.name}")

    scene_plan_file = relative_to_public(overlay_path)
    plan["scenePlanFile"] = scene_plan_file
    edit_plan_path.write_text(json.dumps(plan, indent=2))
    print(f"[edit-plan] scenePlanFile = {scene_plan_file!r} → {edit_plan_path.name}")
    print("\nDone. Re-render TalkingHeadEdit to see overlays.")


if __name__ == "__main__":
    main()
