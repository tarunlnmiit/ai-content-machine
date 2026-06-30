#!/usr/bin/env python3
"""Generate a Claude-designed worksheet HTML (Breath Network design system) + PDF
from a blog post — the same approach used by hand for the W27 DS worksheet.

Pipeline:
  1. Ensure the outline JSON exists (runs generate_worksheet_outline.py if missing).
  2. One Claude call → structured design content (eyebrow / title / tagline / per-
     section prompt HTML + notes label).
  3. Assemble into the fixed CSS shell template, render to PDF (headless Chrome).

Outputs:
  content/worksheets/{week}/{slug}_worksheet.html
  output/worksheets/{week}/{slug}_worksheet.pdf

Usage:
    python3 scripts/generate_worksheet_html.py -i content/blogs/2026-W27/<slug>.md [--force]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.claude_cli import call_claude  # noqa: E402
from lib.schedule_calc import get_iso_week  # noqa: E402
from lib.html_pdf import html_to_pdf  # noqa: E402
from generate_worksheet_outline import NICHE_MAP, detect_niche, _extract_json  # noqa: E402

TEMPLATES = Path(__file__).parent / "templates"
NUM_NOTE_LINES = 6


def _load_template(name: str) -> str:
    return (TEMPLATES / name).read_text(encoding="utf-8")


def _build_design_prompt(blog_text: str, worksheet: dict, niche_key: str) -> str:
    """Ask Claude to fill the design slots — content only, never CSS/markup chrome."""
    n = len(worksheet.get("sections", []))
    sections_json = json.dumps(worksheet.get("sections", []), indent=2, ensure_ascii=False)
    example = (
        '<div class="prompts">\n'
        '  <p class="prompt">List <strong>every AI tool you pay for monthly</strong> — one row each.</p>\n'
        '  <p class="prompt">For each, capture the <strong>cost</strong>, the <em>task</em>, and whether it touches <code>sensitive data</code>.</p>\n'
        '</div>\n'
        '<div class="code-block">ollama pull llama3\nr = ollama.chat(model=\'llama3\', messages=[...])</div>'
    )
    return f"""\
You are designing a one-page companion worksheet for a blog by Tarun Gupta.
Niche: {niche_key}. The worksheet has exactly {n} sections.

Here is the blog (for grounding the prompts in its real content):
<<<BLOG
{blog_text[:8000]}
BLOG

Here is the approved worksheet outline (titles + prompts/questions per section):
<<<OUTLINE
{sections_json}
OUTLINE

Produce the EDITORIAL CONTENT only — never CSS, never page chrome. Return ONLY a
JSON object with this exact schema:
{{
  "eyebrow": "short uppercase kicker, ~3–6 words (e.g. 'Local Inference · Replace $200/Month')",
  "title_html": "the worksheet title; you MAY wrap ONE evocative word in <em>…</em> for accent",
  "tagline": "one warm sentence (<=30 words) on what the reader gets by working through it",
  "field3_label": "a short label for the 3rd header fill-in field (e.g. 'Annual spend $' or 'Session')",
  "sections": [
    {{
      "title": "section title (keep close to the outline title)",
      "content_html": "the section body as HTML using ONLY this vocabulary",
      "notes_label": "tiny uppercase label for the notes column (<=5 words)"
    }}
  ]
}}

content_html RULES — use ONLY these tags/classes, nothing else:
- Wrap text prompts in: <div class="prompts"> … </div>
- Each prompt line: <p class="prompt">…</p>  (turn the outline prompt into 2–4 punchy action lines)
- Emphasis inside a prompt: <strong>…</strong>, <em>…</em> (serif accent), <code>…</code> (inline code)
- Optional ONE code/template block per section: <div class="code-block">line1\\nline2</div>
  (only where the blog has real code/commands — DS yes, Life rarely)
- Keep it tight: this is a single A4-landscape page split across {n} sections.
Worked example of a good content_html:
{example}

Return exactly {n} sections, in order. No markdown fences, no commentary — just the JSON object.
"""


def _render_sections(sections: list[dict], section_tmpl: str) -> str:
    blocks = []
    for i, sec in enumerate(sections, 1):
        block = (
            section_tmpl
            .replace("__NUM__", str(i))
            .replace("__TITLE__", sec.get("title", f"Section {i}"))
            .replace("__CONTENT_HTML__", sec.get("content_html", "").strip())
            .replace("__NOTES_LABEL__", sec.get("notes_label", "Your notes"))
        )
        blocks.append(block)
    return "\n".join(blocks)


def _assemble_html(design: dict, sections: list[dict]) -> str:
    shell = _load_template("worksheet_shell.html")
    section_tmpl = _load_template("worksheet_section.html")
    title_html = design.get("title_html", "Companion Worksheet")
    doc_title = title_html.replace("<em>", "").replace("</em>", "")
    return (
        shell
        .replace("__DOC_TITLE__", doc_title)
        .replace("__EYEBROW__", design.get("eyebrow", ""))
        .replace("__TITLE_HTML__", title_html)
        .replace("__TAGLINE__", design.get("tagline", ""))
        .replace("__FIELD3_LABEL__", design.get("field3_label", "Session"))
        .replace("__SECTIONS__", _render_sections(sections, section_tmpl))
    )


def _ensure_outline(blog_path: Path, json_path: Path) -> None:
    if json_path.exists():
        return
    print("  [outline] worksheet JSON missing — generating it first…")
    subprocess.run(
        [sys.executable, str(Path(__file__).parent / "generate_worksheet_outline.py"),
         "-i", str(blog_path)],
        check=True,
    )


def generate(blog_path: Path, force: bool = False) -> Path | None:
    """Generate worksheet HTML + PDF for a blog. Returns the PDF path (or None if skipped)."""
    slug = blog_path.stem
    niche_key = detect_niche(slug)
    if not niche_key:
        print(f"  [skip] cannot detect DS/Life niche from slug: {slug}")
        return None
    week = get_iso_week(slug[:10])

    json_path = REPO / "content" / "worksheets" / week / f"{slug}_worksheet.json"
    html_path = REPO / "content" / "worksheets" / week / f"{slug}_worksheet.html"
    pdf_path = REPO / "output" / "worksheets" / week / f"{slug}_worksheet.pdf"

    if html_path.exists() and pdf_path.exists() and not force:
        print(f"  [skip] worksheet exists (use --force): {pdf_path.relative_to(REPO)}")
        return pdf_path

    _ensure_outline(blog_path, json_path)
    worksheet = json.loads(json_path.read_text(encoding="utf-8"))
    sections = worksheet.get("sections", [])
    if not sections:
        print("  [skip] worksheet JSON has no sections")
        return None

    blog_text = blog_path.read_text(encoding="utf-8")
    niche_cfg = NICHE_MAP[niche_key]
    prompt = _build_design_prompt(blog_text, worksheet, niche_key)

    print(f"  [design] Claude designing worksheet HTML ({len(sections)} sections)…")
    design: dict | None = None
    for attempt in range(2):
        if attempt == 1:
            prompt = "Return ONLY a raw JSON object, starting with { and ending with }.\n\n" + prompt
        try:
            raw = call_claude(prompt, cache=True, timeout=180,
                              temperature=niche_cfg["temperature"],
                              progress_label="worksheet design")
            design = _extract_json(raw)
            break
        except json.JSONDecodeError:
            if attempt == 0:
                continue
            sys.exit("  worksheet design JSON parse failed after retry.")
        except RuntimeError as e:
            sys.exit(f"  Claude call failed: {e}")

    # Prefer Claude's section content, but keep count + order from the outline.
    design_sections = (design or {}).get("sections", [])
    merged = []
    for i, sec in enumerate(sections):
        ds = design_sections[i] if i < len(design_sections) else {}
        merged.append({
            "title": ds.get("title") or sec.get("title", f"Section {i+1}"),
            "content_html": ds.get("content_html", ""),
            "notes_label": ds.get("notes_label", "Your notes"),
        })

    html = _assemble_html(design or {}, merged)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")
    print(f"  [html]  {html_path.relative_to(REPO)}")

    html_to_pdf(html_path, pdf_path)
    print(f"  [pdf]   {pdf_path.relative_to(REPO)}")
    return pdf_path


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate Claude-designed worksheet HTML + PDF from a blog.")
    ap.add_argument("-i", "--input", required=True, help="Path to blog markdown file")
    ap.add_argument("--force", action="store_true", help="Regenerate even if HTML+PDF exist")
    args = ap.parse_args()

    blog_path = Path(args.input)
    if not blog_path.is_absolute():
        blog_path = REPO / blog_path
    if not blog_path.exists():
        sys.exit(f"File not found: {blog_path}")

    print(f"=== generate_worksheet_html: {blog_path.stem} ===")
    generate(blog_path, force=args.force)


if __name__ == "__main__":
    main()
