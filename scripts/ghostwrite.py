#!/usr/bin/env python3
"""Convert source material (transcript, notes, raw draft) into a polished blog post.

Uses ghostwriter_agent.md prompt + Tarun's voice rules.
Output saved to content/blogs/.

Usage:
    python ghostwrite.py --source path/to/notes.txt --niche ds
    python ghostwrite.py --source transcript.txt --niche life --voice conversational
    python ghostwrite.py --source notes.md --niche ds --desire clarity --topic "why pandas is slow"
"""

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

from _console import console, spinner

REPO = Path(__file__).parent.parent

NICHES = {
    "ds": "data_science_tech",
    "life": "life_self_dev",
    "poetry": "poetry_quotes",
}

VOICE_STYLES = {
    "analytical": "Analytical Enthusiasm — enthusiastic about ideas, makes complex things accessible, balances depth with readability.",
    "conversational": "Authentic Conversational — direct, no-nonsense, challenges conventional wisdom, no hedging.",
    "deletion": "Discovery by Deletion — maximum impact per word, ruthless editing, clarity through brevity.",
    "decision": "Decision Framework — reframes risk and tradeoffs, provides mental models, helps readers see situations differently.",
}

NICHE_DEFAULT_VOICE = {
    "ds": "analytical",
    "life": "conversational",
    "poetry": "conversational",
}

DESIRES = {
    "success": "Survival & Success — progress, achievement, security. Key phrases: breakthrough, unlocked, finally.",
    "clarity": "Comfort & Clarity — simplicity, ease, certainty. Key phrases: simple, easy, finally understand.",
    "status": "Perceived Status — expertise, authority, credibility. Key phrases: research shows, discovered.",
    "tribe": "Safety of Tribe — belonging, community, fitting in.",
    "fear": "Freedom From Fear — protection, security. Key phrases: protect, avoid, safe.",
    "enjoyment": "Life Enjoyment — freedom, experience, pleasure.",
}


from lib.slug import slugify


def load(path: Path) -> str:
    if not path.exists():
        sys.exit(f"Missing: {path}")
    return path.read_text(encoding="utf-8")


def extract_resolved_inserts(source_path: Path) -> dict:
    """Extract resolved [PERSONAL_INSERT:...], [CODE_INSERT:...], [IMAGE_INSERT:...] from blog.

    Returns dict: {insert_type: [list of resolved content blocks]}
    """
    source_text = load(source_path)
    inserts = {"personal": [], "code": [], "image": []}

    patterns = {
        "personal": r"\[PERSONAL_INSERT:\s*(.*?)\]",
        "code": r"\[CODE_INSERT:\s*(.*?)\]",
        "image": r"\[IMAGE_INSERT:\s*(.*?)\]",
    }

    for insert_type, pattern in patterns.items():
        matches = re.finditer(pattern, source_text, re.DOTALL)
        for match in matches:
            content = match.group(1).strip()
            if content:
                inserts[insert_type].append(content)

    return inserts


def inject_resolved_inserts(output_text: str, source_inserts: dict) -> str:
    """Replace new [PLACEHOLDER] inserts in output with resolved content from source.

    Matches by type and order: first PERSONAL_INSERT in output → first from source, etc.
    """
    if not any(source_inserts.values()):
        return output_text

    result = output_text
    insert_types = ["personal", "code", "image"]

    for insert_type in insert_types:
        if not source_inserts[insert_type]:
            continue

        type_upper = insert_type.upper()
        pattern = rf"\[{type_upper}_INSERT:[^\]]*\]"
        source_list = source_inserts[insert_type]
        counter = [0]  # Use list to allow mutation in nested function

        def replacer(match):
            if counter[0] < len(source_list):
                content = source_list[counter[0]]
                counter[0] += 1
                return f"[{type_upper}_INSERT: {content}]"
            return match.group(0)

        result = re.sub(pattern, replacer, result)

    return result


def build_prompt(
    ghostwriter_agent: str,
    master_brief: str,
    source_text: str,
    niche: str,
    voice: str,
    desire: str | None,
    topic: str | None,
    format: str = "blog",
) -> str:
    niche_label = {
        "ds": "Data Science/Tech",
        "life": "Life & Self-Development",
        "poetry": "Poetry/Quotes",
    }[niche]

    word_count_constraint = (
        "\n**Word count: 800–1,000 words total. Every section must be shorter than usual. "
        "Hook ≤100w, Context ≤150w, each Section ≤150w, Takeaway ≤100w, CTA ≤80w. "
        "Lyrical economy — cut anything that does not earn its line.**"
        if niche == "poetry" else ""
    )

    voice_instruction = VOICE_STYLES[voice]
    desire_instruction = (
        f"\n**Human Desire to tap into:** {DESIRES[desire]}" if desire else ""
    )
    topic_instruction = (
        f"\n**Working topic/title:** {topic}" if topic else ""
    )

    if format == "yt":
        task_instruction = "Apply every instruction in the YouTube Script Agent Prompt above.\nConvert the source material below into a voiceover script in Tarun's voice.\nPreserve every concrete detail, number, and genuine insight from the source — do not genericize.\nProduce the complete script with all [PAUSE], [BROLL:], [SCREEN:], and [PERSONAL_INSERT:] markers as specified."
    else:
        task_instruction = "Apply every instruction in the Ghostwriter Agent Prompt above.\nConvert the source material below into a polished blog post in Tarun's voice.\nPreserve every concrete detail, number, and genuine insight from the source — do not genericize.\nProduce the full blog post in clean Markdown, structured exactly as specified."

    image_insert_requirement = (
        "\n2. Include at least 1 `[IMAGE_INSERT: concrete pexels search term]` marker in the blog body."
        if format == "blog" else ""
    )

    return f"""{ghostwriter_agent}

---

## Knowledge Base (master_brief.md)

{master_brief}

---

## Task

Niche: {niche_label}
Voice Style: {voice_instruction}{desire_instruction}{topic_instruction}{word_count_constraint}

{task_instruction}

**MANDATORY REQUIREMENTS (no exceptions):**
1. If source contains a poem (lines starting with `> ` or inside `[POEM_BLOCKQUOTE_BELOW_PRESERVE_EXACTLY]` markers), embed the COMPLETE poem in one unbroken blockquote block right after the HOOK. Do NOT split across sections.{image_insert_requirement}

---

## Source Material

{source_text}
"""


def run_claude(prompt: str, timeout: int, description: str) -> str:
    with spinner() as progress:
        task = progress.add_task(description)
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True, text=True, timeout=timeout,
        )
        progress.update(task, description=f"[success]{description} — done[/success]")

    if result.returncode != 0:
        console.print(f"[error]claude error:[/error] {result.stderr.strip()}")
        sys.exit(1)
    if not result.stdout.strip():
        console.print("[error]claude returned empty output[/error]")
        sys.exit(1)
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Ghostwrite a blog post from source material."
    )
    parser.add_argument("--source", required=True, help="Path to source file (transcript, notes, draft)")
    parser.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    parser.add_argument(
        "--voice",
        choices=["analytical", "conversational", "deletion", "decision"],
        help="Voice style (default: analytical for ds, conversational for life/poetry)",
    )
    parser.add_argument(
        "--desire",
        choices=list(DESIRES.keys()),
        help="Human desire to tap into (optional)",
    )
    parser.add_argument(
        "--topic",
        help="Working topic or title (optional — extracted from source if omitted)",
    )
    parser.add_argument(
        "--format",
        choices=["blog", "yt", "podcast"],
        default="blog",
        help="Output format: blog (default), yt (YouTube script), podcast (podcast script)",
    )
    parser.add_argument(
        "--video-style",
        choices=["screen", "stock", "combo"],
        default=None,
        help="yt format only: 'screen' for screen recording, 'stock' for B-roll over voiceover, 'combo' for B-roll + screen hybrid. Inferred from niche if omitted.",
    )
    parser.add_argument(
        "--poet",
        default=None,
        help="Poetry niche only: name of poet for attribution (e.g., 'Ada Limón'). Omit if poem is Tarun's own.",
    )
    args = parser.parse_args()

    voice = args.voice or NICHE_DEFAULT_VOICE[args.niche]

    source_path = Path(args.source)
    if not source_path.is_absolute():
        source_path = REPO / source_path
    if not source_path.exists():
        sys.exit(f"Source file not found: {source_path}")

    source_text = source_path.read_text(encoding="utf-8")
    if not source_text.strip():
        sys.exit("Source file is empty.")

    if args.poet:
        poem_lines = "\n".join(f"> {line}" if line.strip() else ">" for line in source_text.split("\n") if line.strip())
        source_text = f"[POET_ATTRIBUTION: {args.poet}]\n\n[POEM_BLOCKQUOTE_BELOW_PRESERVE_EXACTLY]\n{poem_lines}\n> \n> — {args.poet}\n[END_POEM_BLOCKQUOTE]\n\nRest of context/reflection to follow:"

    console.rule("[info]Ghostwriter[/info]")
    console.print(f"Source: [bold]{source_path.name}[/bold]  ({len(source_text.split()):,} words)")
    console.print(f"Niche:  [niche]{args.niche}[/niche]  Voice: [bold]{voice}[/bold]  Format: [bold]{args.format}[/bold]", end="")
    if args.format == "yt":
        video_style = args.video_style or ("screen" if args.niche == "ds" else "stock")
        console.print(f"  Style: [bold]{video_style}[/bold]", end="")
    if args.desire:
        console.print(f"  Desire: [bold]{args.desire}[/bold]")
    else:
        console.print()

    if args.format == "yt":
        video_style = args.video_style or ("screen" if args.niche == "ds" else "stock")
        if video_style == "screen":
            agent_prompt = load(REPO / "prompts" / "yt_screen_script_agent.md")
        elif video_style == "combo":
            agent_prompt = load(REPO / "prompts" / "yt_combo_script_agent.md")
        else:
            agent_prompt = load(REPO / "prompts" / "yt_stock_script_agent.md")
    else:
        agent_prompt = load(REPO / "prompts" / "ghostwriter_agent.md")

    master_brief = load(REPO / "data" / "kb" / "master_brief.md")

    combined_prompt = build_prompt(
        agent_prompt, master_brief, source_text,
        args.niche, voice, args.desire, args.topic,
        format=args.format,
    )

    blog_text = run_claude(combined_prompt, timeout=600, description="Ghostwriting blog (2–5 min)...")

    # Validate IMAGE_INSERT present for blog format only; retry once if missing
    if args.format == "blog" and "[IMAGE_INSERT" not in blog_text:
        console.print("[warn]Warning: No IMAGE_INSERT found. Retrying with reinforced prompt...[/warn]")
        retry_prompt = combined_prompt + "\n\n**CRITICAL: You MUST include at least 1 [IMAGE_INSERT: ...] marker in the blog body.**"
        blog_text = run_claude(retry_prompt, timeout=600, description="Retrying with IMAGE_INSERT enforcement...")
        if "[IMAGE_INSERT" not in blog_text:
            console.print("[warn]⚠ Still no IMAGE_INSERT after retry. Proceeding anyway.[/warn]")

    # If source is a blog and format is yt, inject resolved inserts from blog into script output
    inserts_from_blog = False
    if args.format == "yt" and "blogs" in str(source_path):
        source_inserts = extract_resolved_inserts(source_path)
        blog_text = inject_resolved_inserts(blog_text, source_inserts)
        inserts_from_blog = True

    today = date.today().isoformat()
    base = args.topic or source_path.stem
    slug = slugify(base)

    if args.format == "blog":
        filename = f"{today}_{NICHES[args.niche]}_{slug}.md"
        out_dir = REPO / "content" / "blogs"
    elif args.format == "yt":
        filename = f"{today}_{slug}_yt.md"
        out_dir = REPO / "content" / "scripts"
    elif args.format == "podcast":
        filename = f"{today}_{slug}_podcast.md"
        out_dir = REPO / "content" / "scripts"

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    out_path.write_text(blog_text, encoding="utf-8")

    word_count = len(blog_text.split())
    personal_inserts = blog_text.count("[PERSONAL_INSERT")
    code_inserts = blog_text.count("[CODE_INSERT")
    image_inserts = blog_text.count("[IMAGE_INSERT")

    console.print(f"\n[success]✓ Saved:[/success] {out_path.relative_to(REPO)}")
    console.print(f"  Words:             {word_count:,}")
    console.print(f"  [PERSONAL_INSERT]: {personal_inserts}")
    console.print(f"  [CODE_INSERT]:     {code_inserts}")
    console.print(f"  [IMAGE_INSERT]:    {image_inserts}")

    summary_prompt = (
        "Summarise the following blog post in exactly 3 sentences. "
        "Be specific — name the core argument, one key insight, and the takeaway. "
        "No preamble.\n\n" + blog_text[:4000]
    )
    summary = run_claude(summary_prompt, timeout=60, description="Generating summary...")

    console.print("\n[bold]Summary:[/bold]")
    console.print(summary)

    if (personal_inserts or code_inserts or image_inserts) and not inserts_from_blog:
        console.print(
            f"\n[warn]Action needed:[/warn] "
            f"Fill {personal_inserts} [PERSONAL_INSERT], "
            f"{code_inserts} [CODE_INSERT], "
            f"{image_inserts} [IMAGE_INSERT] before repurposing."
        )
        console.print(f"  grep -rn 'INSERT' {out_path.relative_to(REPO)}")

    if args.format == "blog":
        console.print(f"\n[dim]Next step:[/dim] python scripts/repurpose_blog.py --source {out_path.relative_to(REPO)}")
    elif args.format == "yt":
        video_style = args.video_style or ("screen" if args.niche == "ds" else "stock")
        if video_style == "stock":
            console.print(f"\n[dim]Next step:[/dim] python scripts/fetch_videos.py --script {out_path.relative_to(REPO)} --niche {args.niche}")
        elif video_style == "combo":
            console.print(f"\n[dim]Next step:[/dim] Fetch B-roll: python scripts/fetch_videos.py --script {out_path.relative_to(REPO)} --niche {args.niche}")
            console.print(f"[dim]Then:[/dim] Record screen + voiceover using {out_path.relative_to(REPO)}")
        else:
            console.print(f"\n[dim]Next step:[/dim] Record screen + voiceover using {out_path.relative_to(REPO)}")
    elif args.format == "podcast":
        console.print(f"\n[dim]Next step:[/dim] Record podcast using {out_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
