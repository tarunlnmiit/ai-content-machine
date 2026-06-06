#!/usr/bin/env python3
"""Compile the poetry course prompt sheets into one downloadable deck (Step 5 of the
companion-assets plan).

Reads every worksheet in content/courses/poetry/prompts/ (the six lesson prompt sheets
plus the "starter lines" deck sheet) and assembles a single prompt_deck.md with a title
page, a table of contents, and each sheet as its own numbered section. Pure structure —
no Claude call — so it is fully reproducible: re-run it after adding a new prompt sheet
and the deck rebuilds deterministically.

The deck itself (prompt_deck.md) is excluded from its own input because it does not match
the `*_worksheet.md` glob.

Usage (project conda env, no extra deps):
  conda run -n content_engine_env python scripts/compile_prompt_deck.py --niche poetry
"""

import argparse
import sys
from datetime import date
from pathlib import Path

from _console import console

REPO = Path(__file__).parent.parent
NICHES = {"poetry": "poetry"}
DECK_NAME = "prompt_deck.md"


def github_anchor(text: str) -> str:
    """GitHub-flavoured Markdown heading anchor: lowercase, spaces -> hyphens, drop punctuation."""
    keep = [c for c in text.lower() if c.isalnum() or c in " -"]
    return "".join(keep).strip().replace(" ", "-")


def parse_sheet(path: Path) -> tuple[str, str]:
    """Return (title, body) for one prompt worksheet.

    Title comes from the first ATX heading with the trailing ' — Worksheet' stripped.
    Body is everything after that heading, with inner headings demoted one level so a
    sheet's own `## Part 1` nests under the deck's `##` section rather than competing with it.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    start = next((i for i, ln in enumerate(lines) if ln.lstrip().startswith("#")), None)
    if start is None:
        sys.exit(f"No Markdown heading found in {path.name} — cannot title its section.")

    raw_title = lines[start].lstrip("#").strip()
    title = raw_title.removesuffix("— Worksheet").removesuffix("—").strip()

    demoted = ["#" + ln if ln.lstrip().startswith("#") else ln for ln in lines[start + 1 :]]
    body = "\n".join(demoted).strip()
    return title, body


def build_deck(sheets: list[tuple[str, str]], niche: str) -> str:
    today = date.today().isoformat()
    parts: list[str] = []

    # Title page
    parts.append("# The Blank-Page Deck — Poetry Prompt Collection\n")
    parts.append(
        "Every prompt sheet from the poetry course, gathered into one place to pull from "
        "whenever the page is blank. Print it, keep it open in a tab, or drop it in your "
        "notebook app. There is no order you have to follow — open to any page and write.\n"
    )
    parts.append(
        f"- Compiled: {today}\n"
        f"- Sheets: {len(sheets)}\n"
        "- **Original** — every prompt was written for this course, not borrowed.\n"
        "- Reproducible: rebuild with `python scripts/compile_prompt_deck.py`.\n"
    )
    parts.append("\n---\n")

    # Table of contents
    parts.append("## Contents\n")
    for n, (title, _) in enumerate(sheets, 1):
        anchor = github_anchor(f"{n}. {title}")
        parts.append(f"{n}. [{title}](#{anchor})")
    parts.append("\n---\n")

    # Sections
    for n, (title, body) in enumerate(sheets, 1):
        parts.append(f"## {n}. {title}\n")
        parts.append(body)
        parts.append("\n---\n")

    return "\n".join(parts).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile poetry prompt sheets into one deck.")
    parser.add_argument("--niche", default="poetry", choices=list(NICHES))
    args = parser.parse_args()

    console.rule("[info]Prompt Deck Compiler[/info]")
    prompts_dir = REPO / "content" / "courses" / NICHES[args.niche] / "prompts"
    if not prompts_dir.exists():
        sys.exit(f"Missing prompts dir: {prompts_dir}")

    sheet_paths = sorted(prompts_dir.glob("*_worksheet.md"))
    if not sheet_paths:
        sys.exit(f"No *_worksheet.md sheets found in {prompts_dir}")

    sheets = [parse_sheet(p) for p in sheet_paths]
    for p, (title, _) in zip(sheet_paths, sheets):
        console.print(f"  [niche]+[/niche] {title}  [dim]({p.name})[/dim]")

    deck = build_deck(sheets, args.niche)
    out_path = prompts_dir / DECK_NAME
    out_path.write_text(deck, encoding="utf-8")

    console.print(f"\n[success]✓ Saved:[/success] {out_path.relative_to(REPO)}")
    console.print(f"  Sections: {len(sheets)}  Words: {len(deck.split()):,}")


if __name__ == "__main__":
    main()
