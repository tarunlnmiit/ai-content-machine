#!/usr/bin/env python3
"""
Repurpose a blog post into platform derivatives.
Backend: Claude Pro (claude -p subprocess).
Saves each derivative as a separate file under content/derivatives/{slug}/
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from _console import console, spinner, progress_bar

REPO = Path(__file__).parent.parent
load_dotenv(REPO / ".env")

DERIVATIVE_FILES = {
    "twitter_thread": ("twitter_thread.txt", "text"),
    "linkedin_post": ("linkedin_post.txt", "text"),
    "instagram_caption": ("instagram_caption.txt", "text"),
    "threads_post": ("threads_post.txt", "text"),
    "newsletter_summary": ("newsletter.txt", "text"),
    "slide_outline": ("slide_outline.json", "json"),
    "youtube_metadata": ("youtube_metadata.json", "json"),
    "youtube_shorts_metadata": ("youtube_shorts_metadata.json", "json"),
    "polls": ("polls.json", "json"),
    "claude_design_brief": ("claude_design_brief.json", "json"),
}


from lib.slug import slugify


def load(path: Path, required: bool = True) -> str | None:
    if not path.exists():
        if required:
            sys.exit(f"Missing required file: {path}")
        return None
    return path.read_text(encoding="utf-8")


def build_prompt(repurposing_agent: str, hook_patterns: str | None,
                 ig_insights: str | None, blog_text: str) -> str:
    sections = [repurposing_agent]

    if hook_patterns:
        sections.append(
            "## twitter_hook_patterns.json (loaded)\n\n```json\n"
            + hook_patterns
            + "\n```"
        )
    if ig_insights:
        sections.append(
            "## ig_insights.json (loaded)\n\n```json\n"
            + ig_insights
            + "\n```"
        )

    sections.append(
        "## Blog Post to Repurpose\n\n" + blog_text
    )
    sections.append(
        "Return ONLY valid JSON matching the schema above. No markdown code fences. "
        "No explanation. JSON only."
    )

    return "\n\n---\n\n".join(sections)


def extract_json(text: str) -> dict:
    """Strip markdown fences if present, then parse JSON."""
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ``` wrappers
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


# ── Backend: claude -p (Claude Pro subscription) ─────────────────────────

def call_claude_pro(prompt: str) -> tuple[str, dict]:
    """Returns (text, usage_dict). Raises on subprocess failure."""
    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(f"claude -p failed: {result.stderr.strip()}")
    usage = {"input_tokens": 0, "output_tokens": 0, "backend": "claude-pro-subprocess"}
    return result.stdout.strip(), usage


# ── Retry logic with JSON enforcement ────────────────────────────────────

def call_with_retry(prompt: str, call_fn, label: str) -> tuple[dict, dict]:
    """
    Try call_fn(prompt) → parse JSON.
    On parse failure, retry once with stricter instruction.
    Returns (parsed_dict, usage).
    """
    for attempt in range(2):
        if attempt == 1:
            prompt = (
                "You must return ONLY a raw JSON object. "
                "No markdown. No explanation. No code fences. "
                "Start your response with { and end with }.\n\n"
                + prompt
            )
            console.print(f"  [warn][{label}] JSON parse failed — retrying with explicit JSON instruction[/warn]")

        text, usage = call_fn(prompt)

        try:
            parsed = extract_json(text)
            return parsed, usage
        except json.JSONDecodeError as e:
            if attempt == 0:
                continue
            raise RuntimeError(
                f"[{label}] JSON parse failed after retry: {e}\n"
                f"Raw output (first 500 chars):\n{text[:500]}"
            )


# ── Generate ──────────────────────────────────────────────────────────────

def generate(prompt: str) -> tuple[dict, dict]:
    """Call Claude Pro subprocess. Returns (parsed_dict, usage)."""
    backends = [
        ("Claude Pro (subprocess)", call_claude_pro),
    ]

    last_error = None
    for label, fn in backends:
        with spinner() as progress:
            task = progress.add_task(f"Trying {label}...")
            try:
                parsed, usage = call_with_retry(prompt, fn, label)
                progress.update(task, description=f"[success]{label} — OK[/success]")
                return parsed, usage
            except Exception as e:
                err_str = str(e)
                progress.update(task, description=f"[error]{label} — FAILED[/error]")
                console.print(f"  [error]{err_str[:120]}[/error]")
                last_error = e
                time.sleep(1)

    sys.exit(f"All backends failed. Last error: {last_error}")


# ── Save derivatives ──────────────────────────────────────────────────────

def format_twitter_thread(data: dict) -> str:
    parts = [data.get("hook_tweet", "")]
    parts.extend(data.get("tweets", []))
    parts.append(data.get("closing_tweet", ""))
    return "\n\n".join(t for t in parts if t)


def format_linkedin(data: dict) -> str:
    lines = [data.get("opening_line", ""), "", data.get("body", "")]
    hashtags = data.get("hashtags", [])
    if hashtags:
        lines += ["", " ".join(f"#{h.lstrip('#')}" for h in hashtags)]
    return "\n".join(lines)


def format_instagram(data: dict) -> str:
    lines = [
        f"Format: {data.get('format_chosen', '')}",
        f"Why: {data.get('format_rationale', '')}",
        "",
        data.get("hook_line", ""),
        "",
        data.get("caption_body", ""),
    ]
    if data.get("slide_titles"):
        lines += ["", "Slides:"]
        for i, t in enumerate(data["slide_titles"], 1):
            lines.append(f"  {i}. {t}")
    hashtags = data.get("hashtags", [])
    if hashtags:
        lines += ["", " ".join(f"#{h.lstrip('#')}" for h in hashtags)]
    return "\n".join(lines)


def format_newsletter(data: dict) -> str:
    return (
        f"Subject: {data.get('subject_line', '')}\n"
        f"Preview: {data.get('preview_text', '')}\n\n"
        + data.get("body", "")
    )


def format_threads(data: dict) -> str:
    return data.get("body", "")


def save_derivatives(out_dir: Path, data: dict, platforms: list[str] | None = None) -> list[str]:
    saved = []
    formatters = {
        "twitter_thread": format_twitter_thread,
        "linkedin_post": format_linkedin,
        "instagram_caption": format_instagram,
        "threads_post": format_threads,
        "newsletter_summary": format_newsletter,
    }

    # Map platform names to derivative keys
    platform_map = {
        "twitter": "twitter_thread",
        "linkedin": "linkedin_post",
        "instagram": "instagram_caption",
        "threads": "threads_post",
        "newsletter": "newsletter_summary",
        "slides": "slide_outline",
        "youtube": "youtube_metadata",
    }

    # Filter derivatives by platform if specified
    if platforms:
        filtered_keys = {platform_map[p] for p in platforms if p in platform_map}
        derivative_items = {k: v for k, v in DERIVATIVE_FILES.items() if k in filtered_keys}
    else:
        derivative_items = DERIVATIVE_FILES

    with progress_bar() as progress:
        task = progress.add_task("Saving derivatives", total=len(derivative_items))
        for key, (filename, mode) in derivative_items.items():
            progress.update(task, description=f"Saving {filename}")
            value = data.get(key)
            if value is None:
                console.print(f"  [warn]Key '{key}' missing — skipping[/warn]")
                progress.advance(task)
                continue
            path = out_dir / filename
            if mode == "json":
                path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
            else:
                formatter = formatters.get(key)
                text = formatter(value) if formatter else str(value)
                path.write_text(text, encoding="utf-8")
            saved.append(str(path.relative_to(REPO)))
            progress.advance(task)

    return saved


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Repurpose a blog post or article into platform derivatives.")
    parser.add_argument("--input", help="Path to blog Markdown file")
    parser.add_argument("--source", help="Path to source article (Medium, notes, etc.)")
    parser.add_argument(
        "--platforms",
        nargs="+",
        choices=["twitter", "linkedin", "instagram", "threads", "newsletter", "slides", "youtube"],
        help="Platform derivatives to generate (default: all)",
    )
    parser.add_argument(
        "--design",
        action="store_true",
        help="After repurposing, generate Claude Design prompts via generate_design_prompts.py",
    )
    args = parser.parse_args()

    if not args.input and not args.source:
        sys.exit("Require --input (blog file) or --source (article file)")
    if args.input and args.source:
        sys.exit("Choose --input OR --source, not both")

    if args.input:
        blog_path = Path(args.input)
    else:
        blog_path = Path(args.source)

    if not blog_path.is_absolute():
        blog_path = REPO / blog_path
    if not blog_path.exists():
        sys.exit(f"File not found: {blog_path}")

    blog_text = blog_path.read_text(encoding="utf-8")
    slug = blog_path.stem

    console.rule("[info]Repurposing Agent[/info]")
    source_type = "Source article" if args.source else "Blog"
    console.print(f"{source_type}: [bold]{blog_path.name}[/bold]")
    if args.platforms:
        console.print(f"Platforms: {', '.join(args.platforms)}")

    repurposing_agent = load(REPO / "prompts" / "repurposing_agent.md")
    hook_patterns = load(REPO / "data" / "kb" / "twitter_hook_patterns.json", required=False)
    ig_insights   = load(REPO / "data" / "kb" / "ig_insights.json", required=False)

    if not hook_patterns:
        console.print("[warn]twitter_hook_patterns.json not found — embedded fallback active[/warn]")
    if not ig_insights:
        console.print("[warn]ig_insights.json not found — embedded fallback active[/warn]")

    combined_prompt = build_prompt(repurposing_agent, hook_patterns, ig_insights, blog_text)

    parsed, usage = generate(combined_prompt)

    out_dir = REPO / "content" / "derivatives" / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    saved = save_derivatives(out_dir, parsed, args.platforms)

    console.print(f"\n[success]✓ {len(saved)} derivatives → content/derivatives/{slug}/[/success]")
    for f in saved:
        console.print(f"  [dim]{f}[/dim]")

    console.print(f"\n[dim]Token usage ({usage['backend']}):[/dim]")
    if usage['backend'] == "claude-pro-subprocess":
        console.print(f"  [dim]Not available for claude -p subprocess[/dim]")
    else:
        console.print(f"  Input:  {usage['input_tokens']:,}")
        console.print(f"  Output: {usage['output_tokens']:,}")
        console.print(f"  Total:  {usage['input_tokens'] + usage['output_tokens']:,}")

    if args.design:
        console.rule("[info]Claude Design Prompt Generator[/info]")
        design_script = REPO / "scripts" / "generate_design_prompts.py"
        result = subprocess.run(
            [sys.executable, str(design_script), "--input", str(blog_path)],
            cwd=REPO,
        )
        if result.returncode != 0:
            console.print("[warn]Design prompt generation failed — run manually:[/warn]")
            console.print(f"  python scripts/generate_design_prompts.py --input {blog_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
