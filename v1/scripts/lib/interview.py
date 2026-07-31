"""Two-call interview flow for the Medium blog pipeline.

CALL 1 (question_generator.md)  topic + trend context -> suggested angle + 5–8 questions
   interactive Q&A               ask one at a time, edit/skip, empty-safe
CALL 2 (article_writer.md)       topic + Q&A           -> title options, subtitle, article, tags, CTA

The model client is injected (`run_claude`) so this module has no dependency on a
specific SDK — produce_blog.py passes its `claude -p` subprocess wrapper.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from _console import console

REPO = Path(__file__).resolve().parent.parent.parent  # .../v1
PROMPTS_DIR = REPO / "prompts"
CONFIG_PATH = REPO / "config" / "interview.json"

# Env overrides apply to whichever niche is being produced.
_ENV_OVERRIDES = {
    "NICHE": "INTERVIEW_NICHE",
    "AUDIENCE": "INTERVIEW_AUDIENCE",
    "AUTHOR_VOICE": "INTERVIEW_AUTHOR_VOICE",
    "EMAIL_CTA_TARGET": "INTERVIEW_EMAIL_CTA_TARGET",
}
_REQUIRED_KEYS = ("NICHE", "AUDIENCE", "AUTHOR_VOICE", "EMAIL_CTA_TARGET")
_SKIPPED = "[skipped]"


# ──────────────────────────────────────────────────────────────────────────────
# Config + templating
# ──────────────────────────────────────────────────────────────────────────────

def load_interview_config(niche: str) -> dict[str, str]:
    """Merge defaults + per-niche config + env overrides into a flat dict."""
    try:
        raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Missing interview config: {CONFIG_PATH}")
    except json.JSONDecodeError as e:
        raise SystemExit(f"Invalid JSON in {CONFIG_PATH}: {e}")

    cfg = {k: v for k, v in raw.get("defaults", {}).items() if not k.startswith("_")}
    cfg.update({k: v for k, v in raw.get(niche, {}).items() if not k.startswith("_")})
    for key, env_var in _ENV_OVERRIDES.items():
        if os.environ.get(env_var):
            cfg[key] = os.environ[env_var]

    missing = [k for k in _REQUIRED_KEYS if not cfg.get(k)]
    if missing:
        raise SystemExit(
            f"interview.json (niche '{niche}') is missing required keys: {', '.join(missing)}"
        )
    return cfg


def render_template(template_name: str, values: dict[str, str]) -> str:
    """Substitute {{PLACEHOLDER}} tokens. Unknown placeholders are left blank."""
    text = (PROMPTS_DIR / template_name).read_text(encoding="utf-8")
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            text = text[end + 5:]

    def repl(match: re.Match) -> str:
        return str(values.get(match.group(1).strip(), ""))

    return re.sub(r"\{\{\s*([A-Z_]+)\s*\}\}", repl, text)


# ──────────────────────────────────────────────────────────────────────────────
# CALL 1 — questions
# ──────────────────────────────────────────────────────────────────────────────

def generate_questions(
    run_claude,
    *,
    topic: str,
    trend_context: str,
    cfg: dict[str, str],
    extra_instruction: str = "",
) -> tuple[str, list[str]]:
    """Returns (suggested_angle, questions)."""
    prompt = render_template("question_generator.md", {
        "TOPIC": topic,
        "TREND_CONTEXT": trend_context or "(no trend data available)",
        "NICHE": cfg["NICHE"],
        "AUDIENCE": cfg["AUDIENCE"],
    })
    if extra_instruction:
        prompt += f"\n\n{extra_instruction}"
    raw = run_claude(prompt, timeout=120, description="Generating interview questions...")
    return _parse_questions(raw)


def _parse_questions(raw: str) -> tuple[str, list[str]]:
    angle = ""
    questions: list[str] = []
    for line in raw.splitlines():
        s = line.strip()
        if s.upper().startswith("SUGGESTED ANGLE:"):
            angle = s.split(":", 1)[1].strip()
            continue
        m = re.match(r"^(\d+)[.)]\s+(.*)", s)
        if m and m.group(2).strip():
            questions.append(m.group(2).strip())
    return angle, questions


# ──────────────────────────────────────────────────────────────────────────────
# Interactive Q&A — one at a time, edit/skip, never crash on empty input
# ──────────────────────────────────────────────────────────────────────────────

_DONE_SENTINEL = "&&"


def _read_answer(prompt_label: str) -> str:
    """Read a possibly multi-line answer. Type '&&' on its own line to finish.

    Blank lines are kept as paragraph breaks — only '&&' ends input.
    `skip` (alone, first line) marks the question skipped. Empty -> skipped.
    """
    console.print(f"  [dim](type your answer; type '&&' on a new line to finish · 'skip' to skip)[/dim]")
    lines: list[str] = []
    while True:
        try:
            line = input("  > ")
        except (EOFError, KeyboardInterrupt):
            break
        if line.strip().lower() == "skip" and not lines:
            return _SKIPPED
        if line.strip() == _DONE_SENTINEL:
            break
        lines.append(line)
    answer = "\n".join(lines).strip()
    return answer or _SKIPPED


def run_interview(questions: list[str], on_skip=None) -> list[tuple[str, str]]:
    """Ask each question; then allow editing any answer by number. Robust to empties.

    If `on_skip(question) -> str` is provided, a skipped/empty answer is replaced by
    its return value (Claude answering on the creator's behalf) instead of [skipped].
    """
    def resolve(q: str, ans: str) -> str:
        if ans == _SKIPPED and on_skip:
            console.print("  [dim]skipped — Claude answering on your behalf…[/dim]")
            return on_skip(q) or _SKIPPED
        return ans

    answers: list[str] = []
    console.print("\n[bold]── Interview ──[/bold]")
    for i, q in enumerate(questions, 1):
        console.print(f"\n  [bold]Q{i}/{len(questions)}.[/bold] {q}")
        answers.append(resolve(q, _read_answer(q)))

    # Edit pass — optional, loops until the author is done.
    while True:
        console.print("\n[bold]── Review answers ──[/bold]")
        for i, (q, a) in enumerate(zip(questions, answers), 1):
            shown = a if a != _SKIPPED else "[skipped]"
            preview = shown if len(shown) <= 80 else shown[:77] + "…"
            console.print(f"  [bold]{i}.[/bold] {preview}")
        try:
            choice = input(
                "\n  Edit which answer? (number to re-answer · Enter to continue): "
            ).strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not choice:
            break
        if choice.isdigit() and 1 <= int(choice) <= len(questions):
            idx = int(choice) - 1
            console.print(f"\n  [bold]Q{idx + 1}.[/bold] {questions[idx]}")
            answers[idx] = resolve(questions[idx], _read_answer(questions[idx]))
        else:
            console.print(f"  [warn]Enter a number 1–{len(questions)}, or press Enter.[/warn]")

    return list(zip(questions, answers))


def format_qa(pairs: list[tuple[str, str]]) -> str:
    """Render Q&A pairs for the article-writer prompt. Skipped answers are dropped."""
    blocks: list[str] = []
    for i, (q, a) in enumerate(pairs, 1):
        if a == _SKIPPED:
            continue
        blocks.append(f"Q{i}: {q}\nA{i}: {a}")
    return "\n\n".join(blocks) or "(the author skipped the interview — write from the topic alone)"


# ──────────────────────────────────────────────────────────────────────────────
# CALL 2 — article
# ──────────────────────────────────────────────────────────────────────────────

def write_article(
    run_claude,
    *,
    topic: str,
    qa_pairs: list[tuple[str, str]],
    cfg: dict[str, str],
    extra_instruction: str = "",
) -> dict:
    """Returns {title_options, subtitle, article, tags, email_cta, raw}."""
    prompt = render_template("article_writer.md", {
        "TOPIC": topic,
        "NICHE": cfg["NICHE"],
        "AUDIENCE": cfg["AUDIENCE"],
        "VOICE_NOTES": cfg["AUTHOR_VOICE"],
        "ANSWERS": format_qa(qa_pairs),
        "CTA_LINK_OR_DESC": cfg["EMAIL_CTA_TARGET"],
    })
    if extra_instruction:
        prompt += f"\n\n{extra_instruction}"
    raw = run_claude(prompt, timeout=900, description="Writing the article (Opus 4.8, may take several minutes)...")
    return _parse_article(raw)


def _parse_article(raw: str) -> dict:
    """Parse the fixed CALL-2 output format. Tolerant of missing sections."""
    sections = {
        "title_options": [], "subtitle": "", "article": "", "tags": [], "email_cta": "",
        "keyphrase": "", "seo_title": "", "seo_description": "",
    }
    lines = raw.splitlines()
    current = None
    article_lines: list[str] = []

    for line in lines:
        upper = line.strip().upper()
        if upper.startswith("TITLE OPTIONS:"):
            current = "title"
            rest = line.split(":", 1)[1].strip()
            if rest:
                sections["title_options"].extend(_split_titles(rest))
            continue
        if upper.startswith("SUBTITLE:"):
            current = "subtitle"
            sections["subtitle"] = line.split(":", 1)[1].strip()
            continue
        if upper.startswith("ARTICLE:"):
            current = "article"
            rest = line.split(":", 1)[1].strip()
            if rest:
                article_lines.append(rest)
            continue
        if upper.startswith("TAGS:"):
            current = "tags"
            sections["tags"] = _split_tags(line.split(":", 1)[1])
            continue
        if upper.startswith("EMAIL CTA:"):
            current = "cta"
            sections["email_cta"] = line.split(":", 1)[1].strip()
            continue
        if upper.startswith("TARGET KEYPHRASE:"):
            current = "keyphrase"
            sections["keyphrase"] = line.split(":", 1)[1].strip()
            continue
        if upper.startswith("SEO TITLE:"):
            current = "seo_title"
            sections["seo_title"] = line.split(":", 1)[1].strip()
            continue
        if upper.startswith("SEO DESCRIPTION:"):
            current = "seo_description"
            sections["seo_description"] = line.split(":", 1)[1].strip()
            continue

        if current == "title" and line.strip():
            sections["title_options"].extend(_split_titles(line))
        elif current == "article":
            article_lines.append(line)

    sections["article"] = "\n".join(article_lines).strip()
    if not sections["title_options"]:
        # Fallback: first markdown H1 in the article, else a placeholder.
        m = re.search(r"^#\s+(.+)$", sections["article"], re.MULTILINE)
        sections["title_options"] = [m.group(1).strip()] if m else ["Untitled draft"]
    return sections


def _split_titles(text: str) -> list[str]:
    out: list[str] = []
    for part in re.split(r"\s*\|\s*|\n", text):
        cleaned = re.sub(r"^\s*\d+[.)]\s*", "", part).strip().strip('"').strip()
        if cleaned:
            out.append(cleaned)
    return out


def _split_tags(text: str) -> list[str]:
    return [t.strip().lstrip("#").strip() for t in re.split(r"[,\n]", text) if t.strip()][:5]


def assemble_markdown(title: str, parsed: dict) -> str:
    """Build the saved blog Markdown from CALL-2 output."""
    subtitle = parsed.get("subtitle", "").strip()
    body = parsed.get("article", "").strip()
    # Drop a duplicate H1 if the model already opened the article with one.
    body = re.sub(r"^#\s+.+\n+", "", body, count=1) if body.startswith("# ") else body

    parts = [f"# {title}"]
    if subtitle:
        parts.append(f"*{subtitle}*")
    parts.append(body)
    md = "\n\n".join(parts).rstrip()

    tags = parsed.get("tags", [])
    if tags:
        md += f"\n\n<!-- Medium tags: {', '.join(tags)} -->"

    # SEO fields as trailing comments (Medium API can't set them; surfaced for a
    # manual paste into Medium's SEO settings). See scripts/lib/seo.py.
    keyphrase = parsed.get("keyphrase", "").strip()
    seo_title = parsed.get("seo_title", "").strip()
    seo_description = parsed.get("seo_description", "").strip()
    if keyphrase:
        md += f"\n<!-- Target keyphrase: {keyphrase} -->"
    if seo_title:
        md += f"\n<!-- SEO title: {seo_title} -->"
    if seo_description:
        md += f"\n<!-- SEO description: {seo_description} -->"
    return md + "\n"
