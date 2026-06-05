#!/usr/bin/env python3
"""Draft an original course lesson script via Claude Sonnet (claude -p --model).

Routes to Sonnet 4.6 — see docs/course-production-guide.md. Output is a 10–15 min
talking-head script in Tarun's voice that he then edits and personalises before
recording.

Contract (plan line 247): lesson title + 3 key points + 1 personal story prompt
-> Sonnet drafts the full script. Nothing published is fed in; every lesson is
original (course originality mandate).

Usage:
  python3 scripts/draft_lesson_script.py \
    --niche ds \
    --title "How practitioners actually frame a problem" \
    --point "Business question != modelling question" \
    --point "Most time goes to defining the target, not the model" \
    --point "Frame for the decision, not the metric" \
    --story "The churn project where the real question was retention budget"
"""

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

from _console import console, spinner
from lib.slug import slugify

REPO = Path(__file__).parent.parent
MODEL = "claude-sonnet-4-6"

# Guard against the headless `claude` occasionally returning a permission/meta
# stub (e.g. "Awaiting write permission...") instead of the lesson body. Root
# cause: the inner agent tries to *write* the file rather than print it, so we
# deny the write tools (it can only print) and retry on any residual stub.
MIN_WORDS = 250
MAX_TRIES = 3
DENY_TOOLS = "Write,Edit,NotebookEdit,Bash"
META_MARKERS = (
    "write permission", "approve to save", "awaiting", "waiting for permission",
    "once approved", "please approve",
)

NICHES = {"ds": "data_science", "life": "life_self_dev", "poetry": "poetry"}
NICHE_LABELS = {
    "ds": "Data Science/Tech",
    "life": "Life & Self-Development",
    "poetry": "Poetry/Creative Expression",
}
COURSE_NAMES = {
    "ds": "Data Science from the Inside: A Practitioner's Mindset",
    "life": "Systems for Humans: Build a Life That Doesn't Exhaust You",
    "poetry": "Write Like You Mean It: Poetry for People Who Think They Can't",
}
LESSON_MINUTES = {"ds": "10–15", "life": "8–12", "poetry": "6–10"}


def load(path: Path) -> str:
    if not path.exists():
        sys.exit(f"Missing: {path}")
    return path.read_text(encoding="utf-8")


def strip_preamble(text: str) -> str:
    """Drop any leading chatter before the first Markdown heading.

    Sonnet occasionally prefixes a confirmation line (e.g. "Writing the script
    now...") despite the "Return ONLY ... No preamble" instruction. The script
    body always starts with a Markdown heading, so the first `#` line is the
    real start.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.lstrip().startswith("#"):
            return "\n".join(lines[i:]).strip()
    return text.strip()


def build_prompt(
    writing_agent: str,
    master_brief: str,
    niche: str,
    title: str,
    points: list[str],
    story: str,
) -> str:
    points_block = "\n".join(f"  {i}. {p}" for i, p in enumerate(points, 1))
    return f"""{writing_agent}

---

## Knowledge Base (master_brief.md) — voice & background context

{master_brief}

---

## Task: Draft an ORIGINAL course lesson script

You are drafting a video lesson for a paid course. This is the product being
sold, so quality matters more than speed. The output is a talking-head script
the creator (Tarun) reads to camera.

Course:  {COURSE_NAMES[niche]}
Niche:   {NICHE_LABELS[niche]}
Lesson:  {title}
Length:  {LESSON_MINUTES[niche]} minutes spoken (~150 words/min)

Key points this lesson MUST teach:
{points_block}

Personal story to weave in (creator will expand with real detail):
  {story}

HARD RULES:
1. ORIGINAL ONLY. Do not reuse, paraphrase, or restructure any blog, YouTube
   script, or published content. This is a separate product line. Write fresh.
2. Voice: analytical but warm, personal examples, no jargon without context.
   Obey the banned-words list in the knowledge base.
3. Structure the script as spoken delivery, not an essay:
   - COLD OPEN — a sharp line that earns the next 30 seconds. No "in this lesson".
   - WHY THIS MATTERS — stakes for an Indian student aged 16–25.
   - TEACH — work through the {len(points)} key points in order, each with a
     concrete example or worked-through reasoning.
   - STORY — the personal story, marked `[PERSONAL_STORY: ...]` where the
     creator drops in specific real detail.
   - DO THIS NOW — one concrete action tied to the worksheet for this lesson.
   - CLOSE — one memorable line. No recap, no "in conclusion".
4. Mark every spot needing the creator's real specifics with `[PERSONAL_INSERT: ...]`.
5. Write the spoken words only. Use plain Markdown headings for the sections
   above. No camera directions unless essential (then `[B-ROLL: ...]`).

Return ONLY the lesson script. No preamble."""


def run_claude(prompt: str, timeout: int, description: str) -> str:
    last_words = 0
    for attempt in range(1, MAX_TRIES + 1):
        label = description if attempt == 1 else f"{description} (retry {attempt - 1})"
        with spinner() as progress:
            task = progress.add_task(label)
            # Prompt goes via stdin: --disallowed-tools is variadic and would
            # otherwise swallow a trailing prompt arg as a tool name.
            result = subprocess.run(
                ["claude", "-p", "--model", MODEL, "--disallowed-tools", DENY_TOOLS],
                input=prompt, capture_output=True, text=True, timeout=timeout,
            )
            progress.update(task, description=f"[success]{label} — done[/success]")

        if result.returncode != 0:
            console.print(
                f"[warn]claude exited {result.returncode} on attempt "
                f"{attempt}/{MAX_TRIES}: {result.stderr.strip()[:120]}[/warn]"
            )
            continue

        text = strip_preamble(result.stdout)
        words = len(text.split())
        low = text.lower()
        if text and words >= MIN_WORDS and not any(m in low for m in META_MARKERS):
            return text

        last_words = words
        console.print(
            f"[warn]Suspect output ({words} words; permission-meta stub or "
            f"truncated) on attempt {attempt}/{MAX_TRIES}.[/warn]"
        )

    console.print(
        f"[error]Still suspect after {MAX_TRIES} tries (last: {last_words} words). "
        f"NOT saved — re-run later.[/error]"
    )
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Draft an original course lesson script via Claude Sonnet."
    )
    parser.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    parser.add_argument("--title", required=True, help="Lesson title")
    parser.add_argument(
        "--point", dest="points", action="append", required=True,
        metavar="KEY_POINT", help="A key point the lesson must teach (repeatable, give ~3)",
    )
    parser.add_argument(
        "--story", required=True,
        help="One-line prompt for the personal story to weave in",
    )
    args = parser.parse_args()

    console.rule("[info]Course Lesson Drafter (Sonnet)[/info]")
    console.print(f"Course: [bold]{COURSE_NAMES[args.niche]}[/bold]")
    console.print(f"Lesson: [bold]{args.title}[/bold]  Niche: [niche]{args.niche}[/niche]")

    writing_agent = load(REPO / "prompts" / "writing_agent.md")
    master_brief = load(REPO / "data" / "kb" / "master_brief.md")
    prompt = build_prompt(
        writing_agent, master_brief, args.niche, args.title, args.points, args.story
    )

    script_text = run_claude(prompt, timeout=600, description="Drafting lesson (Sonnet, 1–3 min)...")

    today = date.today().isoformat()
    slug = slugify(args.title)
    out_dir = REPO / "content" / "courses" / NICHES[args.niche] / "lesson_scripts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{today}_{slug}.md"
    out_path.write_text(script_text, encoding="utf-8")

    word_count = len(script_text.split())
    personal_inserts = script_text.count("[PERSONAL_INSERT") + script_text.count("[PERSONAL_STORY")

    console.print(f"\n[success]✓ Saved:[/success] {out_path.relative_to(REPO)}")
    console.print(f"  Words:           {word_count:,} (~{word_count // 150} min spoken)")
    console.print(f"  Personal markers: {personal_inserts}")
    if personal_inserts:
        console.print(
            f"\n[warn]Action needed:[/warn] Fill {personal_inserts} personal markers "
            f"with real detail before recording."
        )
        console.print(f"  grep -n 'PERSONAL' {out_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
