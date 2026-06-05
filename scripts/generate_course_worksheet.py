#!/usr/bin/env python3
"""Generate an ORIGINAL course worksheet via Claude Sonnet (claude -p --model).

Contract (plan line 249): lesson topic + learning objective -> Sonnet creates an
original worksheet (reflection / exercise / code) with NO overlap with any
published blog. Unlike scripts/generate_worksheet_outline.py — which derives a
worksheet FROM a published blog — this script ingests no published content. The
course is a separate product line and every worksheet must be original.

Output is Markdown (printable / Notion-ready). Worksheet type adapts per niche:
  ds      -> code + exercise worksheet
  life    -> reflection / journaling prompts
  poetry  -> writing prompts

Usage:
  python3 scripts/generate_course_worksheet.py \
    --niche ds \
    --topic "Framing a problem before touching a model" \
    --objective "Student can translate a vague business ask into a testable target variable"
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
# stub instead of the worksheet body. Root cause: the inner agent tries to
# *write* the file rather than print it, so we deny the write tools (it can only
# print) and retry on any residual stub.
MIN_WORDS = 150
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
# Banned-words list lives in prompts/writing_agent.md, which this script does not
# load (worksheets are structural, not prose). Inline the literal list so the
# "obey the banned-words list" instruction below is not toothless.
BANNED_WORDS = (
    '"In conclusion" · "Dive into" · "Leverage" · "Game-changer" · "Synergy" · '
    '"It\'s important to note" · "In today\'s fast-paced world" · any corporate jargon'
)

WORKSHEET_KIND = {
    "ds": (
        "a hands-on CODE + EXERCISE worksheet. Include a short scenario, 3–5 "
        "graded tasks (easy → applied), starter code in fenced ```python blocks "
        "where useful, and a self-check section with what a correct approach looks like."
    ),
    "life": (
        "a REFLECTION / JOURNALING worksheet. Include a self-audit table, 5–7 "
        "honest prompts that move from observation to action, and a small weekly "
        "review loop the student fills in."
    ),
    "poetry": (
        "a WRITING-PROMPT worksheet. Include 4–6 graded prompts (observation → "
        "first honest line → finished short poem), one constraint exercise, and "
        "a 'share without shame' reflection at the end."
    ),
}


def load(path: Path) -> str:
    if not path.exists():
        sys.exit(f"Missing: {path}")
    return path.read_text(encoding="utf-8")


def strip_preamble(text: str) -> str:
    """Drop any leading chatter before the first Markdown heading.

    Sonnet occasionally prefixes a confirmation line despite the "Return ONLY
    the worksheet ... No preamble" instruction. The worksheet always starts with
    a `#` heading, so the first `#` line is the real start.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.lstrip().startswith("#"):
            return "\n".join(lines[i:]).strip()
    return text.strip()


def build_prompt(
    master_brief: str, niche: str, topic: str, objective: str
) -> str:
    return f"""## Knowledge Base (master_brief.md) — voice & background context

{master_brief}

---

## Task: Create an ORIGINAL course worksheet

You are creating a worksheet that ships inside a paid course. It accompanies one
video lesson. This is the product being sold — make it genuinely useful, not
filler.

Niche:              {NICHE_LABELS[niche]}
Lesson topic:       {topic}
Learning objective: By the end, {objective}
Worksheet type:     Build {WORKSHEET_KIND[niche]}

HARD RULES:
1. ORIGINAL ONLY. Do not reuse, paraphrase, or restructure any published blog,
   YouTube script, or other content. Write fresh. No overlap with existing work.
2. Every task must serve the learning objective above — no padding.
3. Voice: analytical but warm, plain language, no jargon without context.
   BANNED words/phrases — never use: {BANNED_WORDS}
4. Audience: Indian students aged 16–25. Examples should fit that life context.
5. Output clean printable Markdown:
   - `# {topic} — Worksheet`
   - A one-line objective restatement
   - The graded tasks/prompts as numbered sections with space to write
   - A closing self-check or reflection
6. Leave fill-in space with blank lines or `____` underscores where the student writes.

Return ONLY the worksheet Markdown. No preamble."""


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
        description="Generate an original course worksheet via Claude Sonnet."
    )
    parser.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    parser.add_argument("--topic", required=True, help="Lesson topic")
    parser.add_argument(
        "--objective", required=True,
        help="Learning objective (what the student can do after)",
    )
    args = parser.parse_args()

    console.rule("[info]Course Worksheet Generator (Sonnet)[/info]")
    console.print(f"Topic: [bold]{args.topic}[/bold]  Niche: [niche]{args.niche}[/niche]")

    master_brief = load(REPO / "data" / "kb" / "master_brief.md")
    prompt = build_prompt(master_brief, args.niche, args.topic, args.objective)

    worksheet = run_claude(prompt, timeout=600, description="Generating worksheet (Sonnet)...")

    # poetry worksheets live under prompts/ per the plan's folder map; others under worksheets/
    sub = "prompts" if args.niche == "poetry" else "worksheets"
    today = date.today().isoformat()
    slug = slugify(args.topic)
    out_dir = REPO / "content" / "courses" / NICHES[args.niche] / sub
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{today}_{slug}_worksheet.md"
    out_path.write_text(worksheet, encoding="utf-8")

    console.print(f"\n[success]✓ Saved:[/success] {out_path.relative_to(REPO)}")
    console.print(f"  Words: {len(worksheet.split()):,}")
    console.print("  Review for originality + fit before adding to the course.")


if __name__ == "__main__":
    main()
