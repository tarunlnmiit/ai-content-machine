#!/usr/bin/env python3
"""
generate_custom_scene.py — Prompt → Claude Sonnet → TSX scene component → tsc self-correct loop.

Generates a new Remotion scene component from a natural language description, verifies it
compiles, and auto-registers it in SceneRenderer.tsx.

Usage:
  python3 scripts/generate_custom_scene.py \\
    --name TimelineReveal \\
    --prompt "A horizontal timeline with 4 events that slide in left-to-right with spring physics. Each event has a year label above and a description below. Use niche accent color for the active dot." \\
    --niche life

  # Dry-run — print generated TSX without writing or registering:
  python3 scripts/generate_custom_scene.py --name Foo --prompt "..." --dry-run

  # Skip auto-registration in SceneRenderer.tsx:
  python3 scripts/generate_custom_scene.py --name Foo --prompt "..." --no-register
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.claude_cli import call_claude

SCENES_DIR = REPO / "remotion" / "src" / "compositions" / "scenes"
RENDERER_PATH = REPO / "remotion" / "src" / "compositions" / "SceneRenderer.tsx"
REMOTION_DIR = REPO / "remotion"

MODEL = "claude-haiku-4-5-20251001"
MAX_RETRIES = 3

# ── Prompt templates ────────────────────────────────────────────────────────

SYSTEM_CONTEXT = """\
You are writing a Remotion TSX scene component for a content creator's video pipeline.
The component will be rendered at 1920×1080 (or 1080×1920 portrait for shorts).

REQUIRED IMPORTS (use ONLY these — no other packages):
  import {{ AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig }} from "remotion";
  import {{ COLORS, FONTS, RADIUS, SPACING, type Niche,
           nicheAccent, nicheAccentDark, nicheGlow, nicheGlowStrong, nicheGrid,
           gridOverlay, glassPanel }} from "../../styles/chronixel";

DESIGN TOKEN REFERENCE (chronixel.ts):
  COLORS.bg           = "#1E1B2E"  (dark purple-black background)
  COLORS.text         = "#f0f0f2"
  COLORS.textMuted    = "rgba(240,240,242,0.50)"
  COLORS.textDim      = "rgba(240,240,242,0.30)"
  COLORS.surface      = "rgba(255,255,255,0.05)"
  COLORS.surfaceBorder= "rgba(255,255,255,0.10)"

  Per-niche colors — always use helpers, never hardcode hex:
    nicheAccent(niche)       → #6B8FA8 (ds) | #E8705A (life) | #B89850 (poetry)
    nicheGlow(niche)         → 20% alpha version of accent
    nicheGlowStrong(niche)   → 40% alpha version of accent
    nicheGrid(niche)         → 6% alpha grid line color
    gridOverlay(niche)       → CSS object: backgroundImage linear-gradient grid

  FONTS.heading / FONTS.headingWeight (800) / FONTS.body / FONTS.semibold (600) / FONTS.mono
  RADIUS.sm=8 / RADIUS.md=14 / RADIUS.lg=20 / RADIUS.pill=999
  SPACING.xs=8 / SPACING.sm=16 / SPACING.md=24 / SPACING.lg=40 / SPACING.xl=64

COMPONENT RULES:
1. Props interface MUST extend Record<string, unknown>:
   export interface {name}Props extends Record<string, unknown> {{
     niche: Niche;
     // ... other props
   }}
2. Export the component as a named function: export function {name}(...)
3. Background: AbsoluteFill with backgroundColor: COLORS.bg
4. Grid overlay: add <AbsoluteFill style={{gridOverlay(niche)}} /> as second layer
5. All animation: use spring() and interpolate() — no CSS transitions or keyframes
6. Stagger: delay = itemIndex * staggerFrames + initialOffset
7. Keep component self-contained — no external state, no useEffect, no useRef

ANTI-PATTERNS (never do these):
- No hardcoded hex colors
- No CSS animations or keyframes
- No imports beyond the ones listed above
- No React.FC, no hooks other than useCurrentFrame/useVideoConfig

Return ONLY the TypeScript code. No prose, no markdown fences, no explanation.
"""

GENERATION_PROMPT_TEMPLATE = """\
{system_context}

COMPONENT NAME: {name}
DEFAULT NICHE (for examples): {niche}

SCENE DESCRIPTION:
{description}

Write the complete TSX file for this Remotion scene component.
"""

CORRECTION_PROMPT_TEMPLATE = """\
{system_context}

COMPONENT NAME: {name}

The following TypeScript errors were found in the generated component.
Fix ONLY the type errors — preserve the visual design and animation logic exactly.

CURRENT CODE:
{code}

TYPESCRIPT ERRORS:
{errors}

Return ONLY the corrected TypeScript code. No prose, no markdown fences.
"""


# ── Helpers ─────────────────────────────────────────────────────────────────

def extract_tsx(raw: str) -> str:
    """Strip markdown fences and return the TSX code block."""
    # Remove ```tsx or ```typescript or ``` fences
    raw = re.sub(r"```(?:tsx?|typescript)?\n?", "", raw)
    raw = re.sub(r"```\s*$", "", raw, flags=re.MULTILINE)
    return raw.strip()


def run_tsc_for_file(file_path: Path) -> list[str]:
    """Run tsc --noEmit and return errors that belong to file_path only."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True,
        text=True,
        cwd=REMOTION_DIR,
        timeout=60,
    )
    if result.returncode == 0:
        return []

    filename = file_path.name
    errors = []
    for line in (result.stdout + result.stderr).splitlines():
        if filename in line and ": error TS" in line:
            errors.append(line.strip())
    return errors


def patch_scene_renderer(name: str) -> None:
    """Add import + switch case for the new component to SceneRenderer.tsx."""
    src = RENDERER_PATH.read_text()

    import_line = f'import {{ {name} }} from "./scenes/{name}";'
    case_line = f'    case "{name}":        return <{name}        {{...p}} />;'

    # Insert import after last scene import line
    last_import_match = list(re.finditer(r'^import \{[^}]+\} from "\./scenes/[^"]+";', src, re.MULTILINE))
    if not last_import_match:
        print(f"  [warn] Could not locate scene imports in SceneRenderer.tsx — add manually:\n  {import_line}", file=sys.stderr)
    else:
        insert_pos = last_import_match[-1].end()
        src = src[:insert_pos] + "\n" + import_line + src[insert_pos:]

    # Insert case before `default:` line
    default_match = re.search(r'^\s+default:\s+return', src, re.MULTILINE)
    if not default_match:
        print(f"  [warn] Could not locate default case in SceneRenderer.tsx — add manually:\n  {case_line}", file=sys.stderr)
    else:
        insert_pos = default_match.start()
        src = src[:insert_pos] + case_line + "\n" + src[insert_pos:]

    RENDERER_PATH.write_text(src)
    print(f"  ✓ SceneRenderer.tsx patched — import + case '{name}' added")


# ── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a custom Remotion scene component using Claude Sonnet")
    parser.add_argument("--name", required=True, help="PascalCase component name, e.g. TimelineReveal")
    parser.add_argument("--prompt", required=True, help="Natural language description of the scene")
    parser.add_argument("--niche", choices=["ds", "life", "poetry"], default="ds",
                        help="Default niche for design hints (default: ds)")
    parser.add_argument("--dry-run", action="store_true", help="Print TSX without writing files")
    parser.add_argument("--no-register", action="store_true", help="Skip patching SceneRenderer.tsx")
    args = parser.parse_args()

    name = args.name
    if not re.match(r"^[A-Z][a-zA-Z0-9]+$", name):
        print(f"ERROR: --name must be PascalCase with no spaces, e.g. TimelineReveal (got: {name})", file=sys.stderr)
        sys.exit(1)

    out_path = SCENES_DIR / f"{name}.tsx"
    if out_path.exists() and not args.dry_run:
        print(f"ERROR: {out_path.relative_to(REPO)} already exists. Choose a different --name or delete it first.", file=sys.stderr)
        sys.exit(1)

    system_ctx = SYSTEM_CONTEXT.format(name=name)
    gen_prompt = GENERATION_PROMPT_TEMPLATE.format(
        system_context=system_ctx,
        name=name,
        niche=args.niche,
        description=args.prompt,
    )

    print(f"Calling Claude Sonnet ({MODEL}) to generate {name}.tsx...", file=sys.stderr)

    raw = call_claude(gen_prompt, cache=False, model=MODEL, stream=True,
                      timeout=300,
                      progress_label=f"Generating {name}")
    code = extract_tsx(raw)

    if args.dry_run:
        print(f"\n{'─'*60}\n{code}\n{'─'*60}")
        print("\n[dry-run] Not writing files.")
        return

    # Self-correct loop
    for attempt in range(MAX_RETRIES + 1):
        out_path.write_text(code)

        errors = run_tsc_for_file(out_path)
        if not errors:
            print(f"  ✓ tsc passed (attempt {attempt + 1})")
            break

        print(f"  [attempt {attempt + 1}] tsc errors:", file=sys.stderr)
        for e in errors:
            print(f"    {e}", file=sys.stderr)

        if attempt >= MAX_RETRIES:
            print(f"\nERROR: tsc still failing after {MAX_RETRIES} correction attempts.", file=sys.stderr)
            print(f"Component written to {out_path.relative_to(REPO)} — fix manually.", file=sys.stderr)
            sys.exit(1)

        print(f"  Asking Claude Sonnet to self-correct (attempt {attempt + 2}/{MAX_RETRIES + 1})...", file=sys.stderr)
        fix_prompt = CORRECTION_PROMPT_TEMPLATE.format(
            system_context=system_ctx,
            name=name,
            code=code,
            errors="\n".join(errors),
        )
        raw = call_claude(fix_prompt, cache=False, model=MODEL, stream=True,
                          timeout=300,
                          progress_label=f"Correcting {name} (attempt {attempt + 2})")
        code = extract_tsx(raw)

    print(f"\n✓ Written: {out_path.relative_to(REPO)}")

    if not args.no_register:
        patch_scene_renderer(name)
        print(f"\nNext: add '{name}' to remotion/public/templates-map.json scene_components if you want")
        print(f"      the scene planner to use it. Props hint: <describe your props here>")
    else:
        print(f"\nSkipped SceneRenderer.tsx registration (--no-register).")
        print(f"Add manually:\n  import {{ {name} }} from \"./scenes/{name}\";")
        print(f"  case \"{name}\": return <{name} {{...p}} />;")


if __name__ == "__main__":
    main()
