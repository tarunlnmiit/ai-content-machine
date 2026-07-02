#!/usr/bin/env python3
"""Pre-processor: generate a 5-beat reel script BEFORE recording.

Run this BEFORE recording. It produces:
  - reel_script.md  → read this, record your talking head or voiceover
  - manifest.json   → pipeline reads this after you record (format, niche, slug, paths)

Two modes:
  --from blog  <blog.md>   Condense an existing blog post into a 45-90s reel script.
  --from tool  <week>      Generate a tool/build-in-public reel for a given ISO week.
               [--project <key>]  Specify project key from projects.json (free_tool_ds, etc.)
               [--angle <n>]      Pick specific angle_rotation index (0-based; default: auto)

Both modes:
  - Apply the 5-beat virality framework (viral_reel_formula.md)
  - Select the best hook from twitter_hook_patterns.json for the niche
  - Inject honesty guardrail (for tool reels: from projects.json)
  - Output is ~45s of spoken content at 140-160 wpm

Usage:
    # Blog to reel
    python3 scripts/prepare_reel_script.py \\
        --from blog content/blogs/2026-W26/2026-06-24_ds_python-tips.md \\
        --niche ds \\
        --slug 2026-06-24_ds_python-tips_reel

    # Tool reel
    python3 scripts/prepare_reel_script.py \\
        --from tool 2026-W26 \\
        --niche ds \\
        --project free_tool_ds \\
        --slug 2026-06-24_ds_n8n-tool-reel

Output directory: content/reels/<week>/<slug>/
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.niche_config import model_for

KB = REPO / "data" / "kb"
CONTENT_REELS = REPO / "content" / "reels"

VIRAL_FORMULA_PATH = KB / "viral_reel_formula.md"
HOOK_PATTERNS_PATH = KB / "twitter_hook_patterns.json"
PROJECTS_PATH = KB / "projects.json"
WEEKLY_IDEAS_PATH = REPO / "data" / "ideas" / "weekly_ideas.md"

CLAUDE_MODEL_SCRIPT = model_for("reel_script")  # script generation: quality matters
CLAUDE_MODEL_HOOK = model_for("reel_hook")      # hook selection: cheap classification

# Word count targets for a 45s reel at 140-160 wpm
TARGET_WORDS_MIN = 100
TARGET_WORDS_MAX = 130


# ---------------------------------------------------------------------------
# Loading helpers
# ---------------------------------------------------------------------------

def load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict | list:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_hook_patterns(niche: str) -> list[dict]:
    """Return hook patterns applicable to this niche."""
    data = load_json(HOOK_PATTERNS_PATH)
    patterns = data if isinstance(data, list) else data.get("categories", [])
    niche_key = {"ds": "ds", "life": "life", "poetry": "poetry"}.get(niche, niche)
    return [p for p in patterns if niche_key in p.get("use_for", [])]


def load_project(project_key: str) -> dict | None:
    """Load a build-in-public project from projects.json by key."""
    data = load_json(PROJECTS_PATH)
    projects = data if isinstance(data, list) else data.get("projects", [])
    return next((p for p in projects if p.get("key") == project_key), None)


def load_blog(blog_path: Path) -> str:
    """Load blog markdown. Strip front-matter if present."""
    text = load_text(blog_path)
    # Strip YAML front-matter (--- ... ---)
    text = re.sub(r"^---[\s\S]*?---\n", "", text).strip()
    # Limit to first 3000 chars to avoid blowing up the prompt
    if len(text) > 3000:
        text = text[:3000] + "\n\n[... truncated for prompt length ...]"
    return text


def get_weekly_idea(week: str, niche: str, project_key: str | None) -> str:
    """Read weekly_ideas.md and extract the tool reel idea for this niche/week."""
    if not WEEKLY_IDEAS_PATH.exists():
        return f"Tool reel for {niche} niche, week {week}."
    text = load_text(WEEKLY_IDEAS_PATH)
    # Look for a line mentioning the project key or niche+reel
    niche_label = {"ds": "Data Science", "life": "Life", "poetry": "Poetry"}.get(niche, niche)
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if project_key and project_key in line:
            context = "\n".join(lines[max(0, i - 1): i + 5])
            return context.strip()
        if niche_label in line and ("tool" in line.lower() or "reel" in line.lower()):
            context = "\n".join(lines[max(0, i - 1): i + 5])
            return context.strip()
    return f"Weekly tool reel for {niche} niche ({week})."


# ---------------------------------------------------------------------------
# Claude CLI caller
# ---------------------------------------------------------------------------

def call_claude(prompt: str, model: str) -> str:
    """Call `claude -p <prompt> --model <model>` and return stdout."""
    claude_bin = shutil.which("claude")
    if not claude_bin:
        raise RuntimeError("claude CLI not found in PATH. Is it installed and logged in?")
    r = subprocess.run(
        [claude_bin, "-p", prompt, "--model", model],
        capture_output=True, text=True, timeout=300,
    )
    if r.returncode != 0:
        raise RuntimeError(
            f"claude -p failed (exit {r.returncode}):\nstderr: {r.stderr[-400:]}"
        )
    return r.stdout.strip()


# ---------------------------------------------------------------------------
# Hook selection
# ---------------------------------------------------------------------------

def select_best_hook(
    patterns: list[dict],
    topic_summary: str,
    niche: str,
) -> dict:
    """Ask Claude Haiku to pick the best hook pattern for this topic and niche.

    Returns the chosen pattern dict.
    """
    if not patterns:
        return {"name": "Bold Declaration", "pattern": "[BOLD CLAIM]. [Why it matters.]"}

    pattern_list = "\n".join(
        f"{i + 1}. **{p['name']}**: {p['description']}\n   Pattern: {p['pattern']}"
        for i, p in enumerate(patterns[:8])  # cap at 8 to keep prompt short
    )

    prompt = f"""Pick the BEST hook pattern for this {niche} reel topic.

TOPIC: {topic_summary}

HOOK PATTERNS:
{pattern_list}

Reply with ONLY a JSON object: {{"choice": <number 1-{min(len(patterns), 8)}>, "reason": "<10 words>"}}"""

    try:
        raw = call_claude(prompt, CLAUDE_MODEL_HOOK)
        m = re.search(r'\{"choice"\s*:\s*(\d+)', raw)
        if m:
            idx = int(m.group(1)) - 1
            if 0 <= idx < len(patterns):
                return patterns[idx]
    except Exception as e:
        print(f"[script] Hook selection failed ({e}), using default")

    return patterns[0]


# ---------------------------------------------------------------------------
# Script generation prompts
# ---------------------------------------------------------------------------

def build_blog_reel_prompt(
    niche: str,
    blog_text: str,
    hook_pattern: dict,
    formula_text: str,
) -> str:
    niche_voice = {
        "ds": "technical, authoritative, personal — Fireship energy but your own voice",
        "life": "warm, honest, intimate — Casey Neistat vlog meets personal journal",
        "poetry": "deliberate, contemplative — spoken word, every word earns its place",
    }.get(niche, "")

    return f"""You are writing a 45-second talking-head or voiceover reel script from a blog post.

## VOICE
Niche: {niche.upper()} | Tone: {niche_voice}
This is Tarun Gupta speaking — 10-year data scientist, content creator, building in public.
Banned words: "In conclusion", "Dive into", "Leverage", "Game-changer", "Synergy"

## VIRALITY FORMULA (5 beats, follow exactly)
{formula_text[:1500]}

## HOOK PATTERN TO USE
Pattern name: {hook_pattern.get("name", "Bold Declaration")}
Pattern template: {hook_pattern.get("pattern", "")}
Why it works: {hook_pattern.get("description", "")}

## BLOG SOURCE (condense this — do not copy-paste)
{blog_text}

## RULES
- Target: {TARGET_WORDS_MIN}–{TARGET_WORDS_MAX} words spoken (~45s at 140–160 wpm)
- First sentence = hook. Hard opening. No "Hey everyone" or intro.
- Beat 3 (Reveal/Proof): give ONE specific insight from the blog — a concrete example, stat, or technique
- Beat 5 (CTA): ONE clear action. For {niche}: link in bio or "comment X and I'll send you Y"
- Write what will be SPOKEN OUT LOUD, not read. Short sentences. Natural pauses.
- Mark each beat with a label on its own line: [HOOK] [PROBLEM] [REVEAL] [PAYOFF] [CTA]

Write ONLY the script. No metadata, no preamble."""


def build_tool_reel_prompt(
    niche: str,
    project: dict,
    angle: str,
    hook_pattern: dict,
    formula_text: str,
    week: str,
) -> str:
    niche_voice = {
        "ds": "technical, honest, build-in-public energy",
        "life": "warm, practical, real-talk",
        "poetry": "deliberate, personal",
    }.get(niche, "")

    dm_keyword = project.get("dm_keyword", "")
    pitch = project.get("pitch", "")
    guardrail = project.get("honesty_guardrail", "")
    cta_line = (
        f"Comment '{dm_keyword}' and I'll DM you the link." if dm_keyword
        else "Link in bio."
    )

    return f"""You are writing a 45-second reel script about a build-in-public tool.

## VOICE
Niche: {niche.upper()} | Tone: {niche_voice}
Creator: Tarun Gupta — 10-year data scientist, building tools for {niche} creators.
Banned words: "In conclusion", "Dive into", "Leverage", "Game-changer", "Synergy"

## VIRALITY FORMULA (5 beats, follow exactly)
{formula_text[:1500]}

## HOOK PATTERN TO USE
Pattern name: {hook_pattern.get("name", "Bold Declaration")}
Pattern template: {hook_pattern.get("pattern", "")}

## TOOL CONTEXT
Tool name: {project.get("name", "")}
What it does: {pitch}
This week's angle: {angle}
Week: {week}

## HONESTY GUARDRAIL (mandatory — do not break)
{guardrail}

## CTA
{cta_line}

## RULES
- Target: {TARGET_WORDS_MIN}–{TARGET_WORDS_MAX} words spoken (~45s at 140–160 wpm)
- First sentence = hook from the pattern above. Hard opening.
- Beat 3 (Reveal/Proof): show the tool doing the thing — be specific, show real output or a real step
- Never overclaim what the tool does. Apply the honesty guardrail above.
- Write what will be SPOKEN OUT LOUD. Short sentences. Natural pauses.
- Mark each beat: [HOOK] [PROBLEM] [REVEAL] [PAYOFF] [CTA]

Write ONLY the script. No metadata, no preamble."""


# ---------------------------------------------------------------------------
# Word count + quality check
# ---------------------------------------------------------------------------

def count_spoken_words(script: str) -> int:
    """Count words in script, excluding beat labels like [HOOK]."""
    clean = re.sub(r"\[[A-Z/]+\]", "", script)
    return len(clean.split())


def validate_script(script: str) -> list[str]:
    """Return list of warnings about the script. Empty = looks good."""
    warnings = []
    word_count = count_spoken_words(script)
    if word_count < TARGET_WORDS_MIN:
        warnings.append(f"Script too short: {word_count} words (min {TARGET_WORDS_MIN})")
    if word_count > TARGET_WORDS_MAX + 30:
        warnings.append(f"Script too long: {word_count} words (max {TARGET_WORDS_MAX})")

    required_beats = ["[HOOK]", "[PROBLEM]", "[REVEAL]", "[PAYOFF]", "[CTA]"]
    for beat in required_beats:
        if beat not in script:
            warnings.append(f"Missing beat: {beat}")

    banned = ["In conclusion", "Dive into", "Leverage", "Game-changer", "Synergy"]
    for word in banned:
        if word.lower() in script.lower():
            warnings.append(f"Contains banned word: '{word}'")

    return warnings


# ---------------------------------------------------------------------------
# Manifest writer
# ---------------------------------------------------------------------------

def write_manifest(
    out_dir: Path,
    slug: str,
    niche: str,
    content_type: str,   # "blog_reel" | "tool_reel"
    source_path: str,
    script_path: str,
    project_key: str | None,
    week: str,
) -> Path:
    """Write manifest.json that run_video_pipeline.py reads after recording."""
    manifest = {
        "slug": slug,
        "niche": niche,
        "format": "reel",
        "content_type": content_type,
        "week": week,
        "source": source_path,
        "reel_script": script_path,
        "project_key": project_key,
        "created_at": datetime.now().isoformat(),
        "_note": (
            "Record reel_script.md as talking-head or voiceover, then run: "
            f"python3 scripts/run_video_pipeline.py --raw <recording> --manifest {out_dir}/manifest.json"
        ),
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return manifest_path


# ---------------------------------------------------------------------------
# Main modes
# ---------------------------------------------------------------------------

def run_blog_mode(
    blog_path: Path,
    niche: str,
    slug: str,
    week: str,
    out_dir: Path,
) -> None:
    print(f"[reel-script] MODE: blog → reel | niche={niche} | slug={slug}")

    blog_text = load_blog(blog_path)
    hook_patterns = load_hook_patterns(niche)
    formula_text = load_text(VIRAL_FORMULA_PATH)

    # Topic summary for hook selection (first non-empty paragraph of blog)
    first_para = next(
        (p.strip() for p in blog_text.split("\n\n") if len(p.strip()) > 40), blog_text[:200]
    )
    topic_summary = re.sub(r"[#*_]", "", first_para[:200]).strip()

    print(f"[reel-script] Selecting hook pattern for: \"{topic_summary[:80]}...\"")
    hook = select_best_hook(hook_patterns, topic_summary, niche)
    print(f"[reel-script] Hook pattern: {hook.get('name')}")

    prompt = build_blog_reel_prompt(niche, blog_text, hook, formula_text)
    print(f"[reel-script] Calling Claude {CLAUDE_MODEL_SCRIPT} for script generation...")
    script = call_claude(prompt, CLAUDE_MODEL_SCRIPT)

    warnings = validate_script(script)
    word_count = count_spoken_words(script)
    print(f"[reel-script] Script: {word_count} words (~{word_count // 2.5:.0f}s spoken)")
    for w in warnings:
        print(f"  ⚠️  {w}")

    # Write outputs
    out_dir.mkdir(parents=True, exist_ok=True)
    script_path = out_dir / "reel_script.md"
    script_path.write_text(
        f"# Reel Script — {slug}\n"
        f"**Niche:** {niche.upper()}  |  **Format:** reel  |  **Words:** {word_count}  "
        f"|  **Hook:** {hook.get('name')}\n\n"
        f"---\n\n"
        f"{script}\n\n"
        f"---\n"
        f"*Record this as a talking head or voiceover. ~45s at natural pace.*\n"
        f"*Then run:* `python3 scripts/run_video_pipeline.py --raw <recording> --manifest manifest.json`\n"
    )

    manifest_path = write_manifest(
        out_dir=out_dir,
        slug=slug,
        niche=niche,
        content_type="blog_reel",
        source_path=str(blog_path),
        script_path=str(script_path),
        project_key=None,
        week=week,
    )

    print(f"\n[reel-script] ✓ Script: {script_path}")
    print(f"[reel-script] ✓ Manifest: {manifest_path}")
    if warnings:
        print(f"[reel-script] ⚠️  {len(warnings)} warnings above — review before recording")
    else:
        print("[reel-script] Script looks good. Record it, then run the pipeline.")


def run_tool_mode(
    week: str,
    niche: str,
    slug: str,
    project_key: str | None,
    angle_idx: int | None,
    out_dir: Path,
) -> None:
    print(f"[reel-script] MODE: tool → reel | niche={niche} | week={week} | project={project_key}")

    formula_text = load_text(VIRAL_FORMULA_PATH)
    hook_patterns = load_hook_patterns(niche)

    # Load project context
    project: dict = {}
    if project_key:
        project = load_project(project_key) or {}
        if not project:
            print(f"[reel-script] WARNING: project_key '{project_key}' not found in projects.json")
    else:
        # Auto-select project by niche
        data = load_json(PROJECTS_PATH)
        projects = data if isinstance(data, list) else data.get("projects", [])
        niche_projects = [p for p in projects if niche in p.get("niches", [])]
        if niche_projects:
            project = niche_projects[0]
            project_key = project.get("key")
            print(f"[reel-script] Auto-selected project: {project_key}")

    # Select angle from rotation
    angles = project.get("cadence", {}).get("angle_rotation", [])
    if angles:
        if angle_idx is not None and 0 <= angle_idx < len(angles):
            angle = angles[angle_idx]
        else:
            # Rotate by ISO week number
            try:
                week_num = int(week.split("-W")[-1])
            except (ValueError, IndexError):
                week_num = 0
            angle = angles[week_num % len(angles)]
        print(f"[reel-script] Angle: \"{angle}\"")
    else:
        angle = get_weekly_idea(week, niche, project_key)
        print(f"[reel-script] Angle (from weekly ideas): \"{angle[:80]}\"")

    # Topic summary for hook selection
    topic_summary = f"{project.get('pitch', niche + ' tool')} — angle: {angle}"

    print(f"[reel-script] Selecting hook pattern...")
    hook = select_best_hook(hook_patterns, topic_summary, niche)
    print(f"[reel-script] Hook pattern: {hook.get('name')}")

    prompt = build_tool_reel_prompt(
        niche=niche,
        project=project,
        angle=angle,
        hook_pattern=hook,
        formula_text=formula_text,
        week=week,
    )
    print(f"[reel-script] Calling Claude {CLAUDE_MODEL_SCRIPT} for script generation...")
    script = call_claude(prompt, CLAUDE_MODEL_SCRIPT)

    warnings = validate_script(script)
    word_count = count_spoken_words(script)
    print(f"[reel-script] Script: {word_count} words (~{word_count // 2.5:.0f}s spoken)")
    for w in warnings:
        print(f"  ⚠️  {w}")

    # Write outputs
    out_dir.mkdir(parents=True, exist_ok=True)
    script_path = out_dir / "reel_script.md"

    dm_keyword = project.get("dm_keyword", "")
    cta_reminder = (
        f"**DM keyword:** `{dm_keyword}` — set up comment→DM automation before publishing.\n"
        if dm_keyword else ""
    )

    script_path.write_text(
        f"# Tool Reel Script — {slug}\n"
        f"**Niche:** {niche.upper()}  |  **Project:** {project.get('name', project_key)}  "
        f"|  **Angle:** {angle}  |  **Words:** {word_count}  |  **Hook:** {hook.get('name')}\n\n"
        f"{cta_reminder}"
        f"---\n\n"
        f"{script}\n\n"
        f"---\n"
        f"*Record this as a talking head or voiceover. ~45s at natural pace.*\n"
        f"*Then run:* `python3 scripts/run_video_pipeline.py --raw <recording> --manifest manifest.json`\n"
    )

    manifest_path = write_manifest(
        out_dir=out_dir,
        slug=slug,
        niche=niche,
        content_type="tool_reel",
        source_path=f"data/ideas/weekly_ideas.md#{week}",
        script_path=str(script_path),
        project_key=project_key,
        week=week,
    )

    print(f"\n[reel-script] ✓ Script: {script_path}")
    print(f"[reel-script] ✓ Manifest: {manifest_path}")
    if warnings:
        print(f"[reel-script] ⚠️  {len(warnings)} warnings above — review before recording")
    else:
        print("[reel-script] Script looks good. Record it, then run the pipeline.")


# ---------------------------------------------------------------------------
# ISO week helper
# ---------------------------------------------------------------------------

def current_iso_week() -> str:
    d = datetime.now().isocalendar()
    return f"{d[0]}-W{d[1]:02d}"


def week_from_slug_or_date(slug: str) -> str:
    """Try to extract ISO week from slug date prefix (YYYY-MM-DD_...)."""
    m = re.match(r"(\d{4}-\d{2}-\d{2})", slug)
    if m:
        from datetime import date
        d = date.fromisoformat(m.group(1))
        iso = d.isocalendar()
        return f"{iso[0]}-W{iso[1]:02d}"
    return current_iso_week()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Generate a 5-beat reel script before recording.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("--from", dest="source", required=True,
                    choices=["blog", "tool"],
                    help="Source: 'blog' (condense a blog post) or 'tool' (tool/competitor reel)")
    ap.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    ap.add_argument("--slug", required=True,
                    help="Content slug (e.g. 2026-06-24_ds_python-tips_reel)")

    # Blog mode
    ap.add_argument("--blog", default=None,
                    help="Path to blog .md file (required when --from blog)")

    # Tool mode
    ap.add_argument("--week", default=None,
                    help="ISO week string (e.g. 2026-W26). Defaults to current week.")
    ap.add_argument("--project", default=None,
                    help="Project key from projects.json (e.g. free_tool_ds). Auto-detected if omitted.")
    ap.add_argument("--angle", default=None, type=int,
                    help="Angle index from project's angle_rotation list (0-based). Auto-rotated if omitted.")

    args = ap.parse_args()

    week = args.week or week_from_slug_or_date(args.slug)
    out_dir = CONTENT_REELS / week / args.slug

    if args.source == "blog":
        if not args.blog:
            ap.error("--blog <path> is required when --from blog")
        blog_path = Path(args.blog)
        if not blog_path.exists():
            print(f"ERROR: Blog file not found: {blog_path}", file=sys.stderr)
            sys.exit(1)
        run_blog_mode(
            blog_path=blog_path,
            niche=args.niche,
            slug=args.slug,
            week=week,
            out_dir=out_dir,
        )

    elif args.source == "tool":
        run_tool_mode(
            week=week,
            niche=args.niche,
            slug=args.slug,
            project_key=args.project,
            angle_idx=args.angle,
            out_dir=out_dir,
        )


if __name__ == "__main__":
    main()
