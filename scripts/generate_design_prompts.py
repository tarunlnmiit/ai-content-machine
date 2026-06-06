#!/usr/bin/env python3
"""
Generate Claude Design prompts (slide deck, Instagram story, reel cover, social post set)
from a blog post using Claude API.

For Data Science/Tech tutorial content: extracts, completes, and validates code blocks
before including them in the design brief.

Usage:
    python scripts/generate_design_prompts.py --input content/blogs/my_blog.md
    python scripts/generate_design_prompts.py --input content/blogs/my_blog.md --niche life
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).parent.parent

NICHE_PATTERNS = {
    "data_science_tech": "ds",
    "life_self_dev": "life",
    "poetry_quotes": "poetry",
}

def call_claude_pro(prompt: str) -> str:
    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(f"claude -p failed: {result.stderr.strip()}")
    return result.stdout.strip()


def extract_json_response(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


from lib.slug import slugify


def detect_niche(blog_path: Path) -> str:
    name = blog_path.stem.lower()
    for pattern, niche in NICHE_PATTERNS.items():
        if pattern in name:
            return niche
    return "life"


def extract_code_blocks(markdown: str) -> list[str]:
    return re.findall(r"```(?:python|py)\n(.*?)```", markdown, re.DOTALL)


def classify_ds_content(blog_text: str) -> str:
    prompt = (
        "Classify this Data Science blog as one word:\n"
        "- tutorial: step-by-step, teaches how to do X with code\n"
        "- explanation: conceptual, explains what/why\n"
        "- conversational: opinion/story-driven, no hands-on code\n\n"
        "Reply with ONLY one word.\n\n"
        f"Blog (first 3000 chars):\n{blog_text[:3000]}"
    )
    response = call_claude_pro(prompt)
    return response.strip().lower()


def make_code_complete(code: str, context: str, error: str | None = None) -> str:
    if error:
        prompt = (
            f"This Python code failed. Fix it.\n\nError:\n{error}\n\nCode:\n```python\n{code}\n```\n\n"
            "Return ONLY the fixed Python code. No explanation. No markdown fences."
        )
    else:
        prompt = (
            f"Make this Python code self-contained and runnable.\n"
            f"Add imports, sample data, any missing setup. Keep core logic unchanged.\n"
            f"Use only standard library + common packages (pandas, numpy, scikit-learn, matplotlib).\n"
            f"Context: {context}\n\nCode:\n```python\n{code}\n```\n\n"
            "Return ONLY the complete runnable code. No explanation. No markdown fences."
        )
    response = call_claude_pro(prompt)
    return response.strip()


def run_code(code: str) -> tuple[bool, str]:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        tmp = f.name
    try:
        result = subprocess.run(
            ["python", tmp],
            capture_output=True,
            text=True,
            timeout=30,
        )
        success = result.returncode == 0
        return success, result.stdout if success else result.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout after 30s"
    finally:
        Path(tmp).unlink(missing_ok=True)


def validate_code_block(raw: str, context: str) -> dict:
    code = raw
    for attempt in range(3):
        error = None if attempt == 0 else last_error
        complete = make_code_complete(code, context, error=error)
        success, output = run_code(complete)
        if success:
            return {"original": raw, "complete": complete, "tested": True, "output_preview": output[:500]}
        last_error = output
        code = complete  # feed fixed version into next attempt
    return {"original": raw, "complete": code, "tested": False, "error": last_error}


def build_user_message(
    blog_text: str,
    niche: str,
    slide_outline: dict | None,
    design_brief: dict | None,
    validated_code: list[dict] | None,
) -> str:
    parts = [f"## Niche\n\n{niche}", f"## Blog Post\n\n{blog_text}"]

    if slide_outline:
        parts.append(f"## Slide Outline\n\n```json\n{json.dumps(slide_outline, indent=2)}\n```")

    if design_brief:
        parts.append(f"## Design Brief\n\n```json\n{json.dumps(design_brief, indent=2)}\n```")

    if validated_code:
        code_section = "## Validated Code Blocks (DS Tutorial — include in CODE_BLOCK slides)\n\n"
        for i, block in enumerate(validated_code):
            status = "TESTED ✓" if block["tested"] else "UNTESTED"
            code_section += f"### Code Block {i + 1} ({status})\n\n```python\n{block['complete']}\n```\n\n"
        parts.append(code_section)

    parts.append("Generate all 4 design prompts now.")
    return "\n\n---\n\n".join(parts)


def parse_prompts(raw: str) -> dict[str, str]:
    keys = {
        "slide_deck": (r"---BEGIN SLIDE DECK PROMPT---", r"---END SLIDE DECK PROMPT---"),
        "instagram_story": (r"---BEGIN INSTAGRAM STORY PROMPT---", r"---END INSTAGRAM STORY PROMPT---"),
        "reel_cover": (r"---BEGIN REEL COVER PROMPT---", r"---END REEL COVER PROMPT---"),
        "social_post": (r"---BEGIN SOCIAL POST PROMPT---", r"---END SOCIAL POST PROMPT---"),
    }
    result = {}
    for key, (start, end) in keys.items():
        pattern = re.escape(start) + r"\n(.*?)" + re.escape(end)
        match = re.search(pattern, raw, re.DOTALL)
        result[key] = match.group(1).strip() if match else raw
    return result


def main():
    parser = argparse.ArgumentParser(description="Generate Claude Design prompts from a blog post.")
    parser.add_argument("--input", required=True, help="Path to blog Markdown file")
    parser.add_argument("--niche", choices=["ds", "life", "poetry"], help="Override niche detection")
    args = parser.parse_args()

    blog_path = Path(args.input)
    if not blog_path.is_absolute():
        blog_path = REPO / blog_path
    if not blog_path.exists():
        sys.exit(f"File not found: {blog_path}")

    blog_text = blog_path.read_text(encoding="utf-8")
    slug = blog_path.stem
    niche = args.niche or detect_niche(blog_path)

    system_prompt = (REPO / "prompts" / "claude_design_agent.md").read_text(encoding="utf-8")

    derivatives_dir = REPO / "content" / "derivatives" / slug
    slide_outline = None
    if (derivatives_dir / "slide_outline.json").exists():
        slide_outline = json.loads((derivatives_dir / "slide_outline.json").read_text())

    design_brief = None
    if (derivatives_dir / "claude_design_brief.json").exists():
        design_brief = json.loads((derivatives_dir / "claude_design_brief.json").read_text())

    # DS-only: classify + validate code
    validated_code = None
    if niche == "ds":
        print("Classifying DS content type...")
        content_type = classify_ds_content(blog_text)
        print(f"  → {content_type}")

        if content_type == "tutorial":
            raw_blocks = extract_code_blocks(blog_text)
            if raw_blocks:
                context = blog_path.stem.replace("-", " ").replace("_", " ")
                print(f"Found {len(raw_blocks)} code block(s). Generating + validating...")
                validated_code = []
                for i, raw in enumerate(raw_blocks):
                    print(f"  Block {i + 1}/{len(raw_blocks)}...", end=" ", flush=True)
                    result = validate_code_block(raw, context)
                    print("✓ tested" if result["tested"] else "✗ untested")
                    validated_code.append(result)

    print("Generating Claude Design prompts...")
    user_message = build_user_message(blog_text, niche, slide_outline, design_brief, validated_code)

    full_prompt = f"{system_prompt}\n\n---\n\n{user_message}"
    raw_output = call_claude_pro(full_prompt)

    prompts = parse_prompts(raw_output)

    out_dir = REPO / "output" / "scheduled"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"claude_design_prompts_{slug}.md"

    lines = [f"# Claude Design Prompts — {blog_path.stem}", f"\nNiche: {niche}"]
    if validated_code:
        tested = sum(1 for c in validated_code if c["tested"])
        lines.append(f"Code blocks: {tested}/{len(validated_code)} validated")
    lines.append("\n---\n")
    lines.append("## 1. SLIDE DECK PROMPT\n\n" + prompts["slide_deck"])
    lines.append("\n---\n")
    lines.append("## 2. INSTAGRAM STORY SEQUENCE PROMPT\n\n" + prompts["instagram_story"])
    lines.append("\n---\n")
    lines.append("## 3. REEL COVER / THUMBNAIL PROMPT\n\n" + prompts["reel_cover"])
    lines.append("\n---\n")
    lines.append("## 4. SOCIAL POST SET PROMPT (Instagram · LinkedIn · Twitter/X · Threads)\n\n" + prompts["social_post"])

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✓ Prompts → {out_path.relative_to(REPO)}")

    if validated_code:
        code_path = out_dir / f"validated_code_{slug}.json"
        code_path.write_text(json.dumps(validated_code, indent=2), encoding="utf-8")
        print(f"✓ Validated code → {code_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
