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

from lib.schedule_calc import write_schedule_json, get_iso_week
from lib.content_paths import derivatives_dir

REPO = Path(__file__).parent.parent
load_dotenv(REPO / ".env")

DERIVATIVE_FILES = {
    "linkedin_post": ("linkedin_post.txt", "text"),
    "linkedin_document_caption": ("linkedin_document_caption.txt", "text"),
    "instagram_caption": ("instagram_caption.txt", "text"),
    "newsletter_summary": ("newsletter.txt", "text"),
    "slide_outline": ("slide_outline.json", "json"),
    "youtube_metadata": ("youtube_metadata.json", "json"),
    "youtube_shorts_metadata": ("youtube_shorts_metadata.json", "json"),
    "polls": ("polls.json", "json"),
    "claude_design_brief": ("claude_design_brief.json", "json"),
}

# ── YT filming script prompt ──────────────────────────────────────────────────
_YT_SCRIPT_PROMPT = """\
You are writing a verbal YouTube filming script from a blog post.

Creator: Tarun Gupta
Niche: {niche_label}
Voice: Analytical but warm. Personal examples. No jargon without context.
BANNED: "In conclusion", "Dive into", "Leverage", "Game-changer", "Synergy"

Write a complete filming script the creator reads from a teleprompter or uses as on-set reference.
Target runtime: 8–12 minutes.

OUTPUT FORMAT — markdown only, nothing before or after:

---
slug: {slug}
niche: {niche}
estimated_duration: Xmin
---

## Hook (0:00–0:30)
[First 30 seconds verbatim — answer: why watch the next 10 minutes RIGHT NOW?]

## [Section 1 Title] (~X:XX–X:XX)
[Spoken content. Address one person directly. Specific numbers, examples, analogies.]
[BROLL: what to show — code screen, slides, or "talking head"]

[3–5 sections total — repeat the section block]

## CTA + Close (~X:XX–end)
[Natural subscribe/comment prompt. DS/Life: mention the free worksheet. Keep under 45 seconds.]

---

BLOG POST:
{blog_text}
"""


from lib.slug import slugify
from lib.hashtags import hashtag_line
from lib.virality import virality_block, caption_formula_digest, project_keys


def niche_from_slug(slug: str) -> str:
    """Map a derivative slug to a niche key (ds / life / poetry)."""
    if "data_science_tech" in slug:
        return "ds"
    if "poetry_quotes" in slug:
        return "poetry"
    return "life"


def load(path: Path, required: bool = True) -> str | None:
    if not path.exists():
        if required:
            sys.exit(f"Missing required file: {path}")
        return None
    return path.read_text(encoding="utf-8")


def build_prompt(repurposing_agent: str, hook_patterns: str | None,
                 ig_insights: str | None, blog_text: str,
                 niche: str = "life", project_key: str | None = None,
                 master_brief: str | None = None) -> str:
    sections = [repurposing_agent]

    virality = virality_block("thread", niche, project_key)
    if virality:
        sections.append("## Virality Directives (apply to every platform)\n\n" + virality)

    caption_formula = caption_formula_digest(niche)
    if caption_formula:
        sections.append(
            "## CAPTION FORMULA (authoritative for instagram_caption — this niche)\n\n"
            + caption_formula
        )

    if master_brief:
        sections.append(
            "## Master Brief (creator voice, competition intelligence, what's working)\n\n"
            + master_brief
        )

    if hook_patterns:
        sections.append(
            "## twitter_hook_patterns.json (loaded)\n\n```json\n"
            + hook_patterns
            + "\n```"
        )
    if ig_insights:
        sections.append(
            "## ig_format_guidance.json (June 2026 — competition-based)\n\n```json\n"
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

def format_linkedin(data: dict, niche: str = "life") -> str:
    """LinkedIn post BODY only — clean, no outbound link. The blog link belongs in
    the pinned first comment (LinkedIn suppresses reach on body links); that comment
    is written to a separate file by save_derivatives (format_linkedin_comment) and
    posted by the scheduler daemon after the post is created."""
    lines = [data.get("opening_line", ""), "", data.get("body", "")]
    tags = hashtag_line(niche, "linkedin", data.get("hashtags"))
    if tags:
        lines += ["", tags]
    return "\n".join(lines)


def format_linkedin_comment(data: dict, niche: str = "life") -> str:
    """The pinned first comment for a LinkedIn post (carries the blog link).

    May still contain the [BLOG_LINK] placeholder if the blog isn't published yet —
    the publish flow substitutes the real URL, and the daemon refuses to post a
    comment that still holds an unresolved placeholder.
    """
    return (data.get("first_comment") or "").strip()


def format_linkedin_document_caption(data: dict, niche: str = "life") -> str:
    """Caption body for the LinkedIn document (slide deck) post.

    No outbound link in body — worksheet link goes in the pinned first comment,
    YT link in the second comment (same as strategy doc: 1st=Worksheet, 2nd=YT).
    """
    lines = [data.get("opening_line", ""), "", data.get("body", "")]
    tags = hashtag_line(niche, "linkedin", data.get("hashtags"))
    if tags:
        lines += ["", tags]
    return "\n".join(lines)


def format_instagram(data: dict, niche: str = "life") -> str:
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
    tags = hashtag_line(niche, "instagram", data.get("hashtags"))
    if tags:
        lines += ["", tags]
    return "\n".join(lines)


def format_instagram_caption_clean(data: dict, niche: str = "life") -> str:
    """The POST-READY Instagram caption (no Format:/Why:/Slides brief header).

    `format_instagram` produces a human review brief; this is what actually gets
    published — hook line, caption body, CTA, hashtags. Written to a separate file
    so the auto-publish daemon stages real caption text, not the brief.
    """
    parts = [data.get("hook_line", ""), "", data.get("caption_body", "")]
    cta = data.get("cta_line", "")
    if cta:
        parts += ["", cta]
    tags = hashtag_line(niche, "instagram", data.get("hashtags"))
    if tags:
        parts += ["", tags]
    return "\n".join(p for p in parts if p is not None).strip()


def format_newsletter(data: dict, niche: str = "life") -> str:
    return (
        f"Subject: {data.get('subject_line', '')}\n"
        f"Preview: {data.get('preview_text', '')}\n\n"
        + data.get("body", "")
    )


def save_derivatives(out_dir: Path, data: dict, platforms: list[str] | None = None,
                     niche: str = "life") -> list[str]:
    saved = []
    formatters = {
        "linkedin_post": format_linkedin,
        "linkedin_document_caption": format_linkedin_document_caption,
        "instagram_caption": format_instagram,
        "newsletter_summary": format_newsletter,
    }

    # Map platform names to derivative keys
    platform_map = {
        "linkedin": "linkedin_post",
        "instagram": "instagram_caption",
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
                text = formatter(value, niche) if formatter else str(value)
                path.write_text(text, encoding="utf-8")
            saved.append(str(path.relative_to(REPO)))

            # LinkedIn comments: strategy order = 1st=Worksheet, 2nd=Blog link.
            # The blog link (first_comment from LLM) is saved as the SECOND comment file.
            # Phase 2 writes the worksheet URL to linkedin_first_comment.txt (pinned 1st).
            if key == "linkedin_post":
                comment = format_linkedin_comment(value, niche)
                if comment:
                    cpath = out_dir / "linkedin_second_comment.txt"
                    cpath.write_text(comment, encoding="utf-8")
                    saved.append(str(cpath.relative_to(REPO)))

            # Instagram: write the post-ready caption alongside the human brief, so
            # the auto-publish daemon stages clean caption text (not Format:/Why:…).
            if key == "instagram_caption":
                clean = format_instagram_caption_clean(value, niche)
                if clean:
                    cpath = out_dir / "instagram_caption_clean.txt"
                    cpath.write_text(clean, encoding="utf-8")
                    saved.append(str(cpath.relative_to(REPO)))

            progress.advance(task)

    return saved


# ── Phase 2 helpers ───────────────────────────────────────────────────────

def run_step(cmd: list, label: str = "") -> bool:
    """Run a subprocess step. Non-fatal — returns True on success, False on failure."""
    label = label or (Path(str(cmd[1])).stem if len(cmd) > 1 else "step")
    console.print(f"  $ {' '.join(str(c) for c in cmd)}")
    r = subprocess.run([str(c) for c in cmd], cwd=REPO)
    if r.returncode != 0:
        console.print(f"  [warn]  ⚠ {label} failed (exit {r.returncode}) — continuing[/warn]")
        return False
    return True


def inject_worksheet_cta_into_blog(blog_path: Path, slug: str) -> None:
    """Append worksheet CTA block to the blog file if not already present (DS/Life only)."""
    from lib.worksheet_cta import (
        has_cta,
        worksheet_cta_markdown,
        extract_worksheet_slug_from_dir,
        worksheet_exists,
    )
    ws_slug = extract_worksheet_slug_from_dir(slug)
    if not ws_slug or not worksheet_exists(ws_slug):
        console.print("  [dim]skip blog CTA — worksheet not yet published[/dim]")
        return
    text = blog_path.read_text(encoding="utf-8")
    if has_cta(text):
        console.print("  [dim]skip blog CTA — already injected[/dim]")
        return
    cta = worksheet_cta_markdown(ws_slug)
    blog_path.write_text(text.rstrip() + "\n\n" + cta + "\n", encoding="utf-8")
    console.print(f"  [success]✓ Worksheet CTA injected into blog[/success]")


def write_linkedin_document_comments(out_dir: Path, slug: str, week: str) -> None:
    """Write comment files for the LinkedIn document (slide deck) post.

    Strategy: 1st comment = Worksheet link, 2nd comment = YT link.
    linkedin_document_first_comment.txt  — worksheet URL (if published)
    linkedin_document_second_comment.txt — YT video link (from youtube_metadata.json)
    Self-idempotent: skips each file if it already exists.
    """
    # ── 1st comment: worksheet URL ────────────────────────────────────────────
    doc1_path = out_dir / "linkedin_document_first_comment.txt"
    if not doc1_path.exists():
        from lib.worksheet_cta import (
            extract_worksheet_slug_from_dir,
            worksheet_exists,
            worksheet_url,
            worksheet_title,
        )
        ws_slug = extract_worksheet_slug_from_dir(slug)
        if ws_slug and worksheet_exists(ws_slug):
            title = worksheet_title(ws_slug) or "free worksheet"
            url   = worksheet_url(ws_slug)
            doc1_path.write_text(f"🎯 {title}: {url}\n", encoding="utf-8")
            console.print(f"  [success]✓ LinkedIn doc 1st comment (worksheet) → {doc1_path.relative_to(REPO)}[/success]")
        else:
            console.print("  [dim]skip doc 1st comment — worksheet not yet published[/dim]")
    else:
        console.print("  [dim]skip doc 1st comment — exists[/dim]")

    # ── 2nd comment: YT link ──────────────────────────────────────────────────
    doc2_path = out_dir / "linkedin_document_second_comment.txt"
    if not doc2_path.exists():
        yt_meta_path = out_dir / "youtube_metadata.json"
        yt_url = ""
        if yt_meta_path.exists():
            try:
                yt_meta = json.loads(yt_meta_path.read_text(encoding="utf-8"))
                yt_url = yt_meta.get("video_url") or yt_meta.get("url") or ""
            except (json.JSONDecodeError, OSError):
                pass
        if not yt_url:
            yt_url = "[YT_LINK]"   # placeholder — inject_worksheet_ctas.py will resolve
        doc2_path.write_text(f"▶ Full video: {yt_url}\n", encoding="utf-8")
        console.print(f"  [success]✓ LinkedIn doc 2nd comment (YT link) → {doc2_path.relative_to(REPO)}[/success]")
    else:
        console.print("  [dim]skip doc 2nd comment — exists[/dim]")


def write_linkedin_first_comment(out_dir: Path, slug: str) -> None:
    """Write linkedin_first_comment.txt with the worksheet URL (DS/Life only).

    Strategy: 1st pinned comment = Worksheet link, 2nd = Blog link.
    The blog link (2nd) is written in Phase 1 as linkedin_second_comment.txt.
    This function writes the worksheet URL as the FIRST comment (pinned, highest visibility).
    Only written once the worksheet is published in the manifest.
    """
    cpath = out_dir / "linkedin_first_comment.txt"
    if cpath.exists():
        console.print(f"  [dim]skip LinkedIn 1st comment — exists[/dim]")
        return
    from lib.worksheet_cta import (
        extract_worksheet_slug_from_dir,
        worksheet_exists,
        worksheet_url,
        worksheet_title,
    )
    ws_slug = extract_worksheet_slug_from_dir(slug)
    if not ws_slug or not worksheet_exists(ws_slug):
        console.print("  [dim]skip LinkedIn 1st comment — worksheet not yet published[/dim]")
        return
    title = worksheet_title(ws_slug) or "free worksheet"
    url = worksheet_url(ws_slug)
    cpath.write_text(f"🎯 {title}: {url}\n", encoding="utf-8")
    console.print(f"  [success]✓ LinkedIn 1st comment (worksheet) → {cpath.relative_to(REPO)}[/success]")


def generate_yt_script(blog_text: str, slug: str, week: str, niche: str) -> None:
    """Generate a verbal YouTube filming script; save to content/scripts/{week}/{slug}_yt.md."""
    niche_labels = {
        "ds":     "Data Science / Python / Tech (@breathofdatascience)",
        "life":   "Life & Self-Development (@mistakenlyhuman)",
        "poetry": "Poetry / Quotes (@breathofpoetry)",
    }

    # Prepend virality intelligence + master brief so the script follows proven hooks/guardrails.
    sections: list[str] = []
    v_block = virality_block("yt_script", niche)
    if v_block:
        sections.append("## Virality Directives\n\n" + v_block)
    master_brief_path = REPO / "data" / "kb" / "master_brief.md"
    if master_brief_path.exists():
        sections.append(
            "## Master Brief (creator voice, competition intelligence, what's working)\n\n"
            + master_brief_path.read_text(encoding="utf-8")
        )
    sections.append(_YT_SCRIPT_PROMPT.format(
        slug=slug,
        niche=niche,
        niche_label=niche_labels.get(niche, niche),
        blog_text=blog_text[:6000],
    ))
    prompt = "\n\n---\n\n".join(sections)

    console.print("  Generating YT filming script…")
    try:
        raw, _ = call_claude_pro(prompt)
    except RuntimeError as e:
        console.print(f"  [warn]YT script failed: {e}[/warn]")
        return
    out_path = REPO / "content" / "scripts" / week / f"{slug}_yt.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(raw, encoding="utf-8")
    console.print(f"  [success]✓ YT script → {out_path.relative_to(REPO)}[/success]")


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Repurpose a blog post into platform derivatives (Phase 1) + expanded outputs (Phase 2)."
    )
    parser.add_argument("--input", help="Path to blog Markdown file")
    parser.add_argument("--source", help="Path to source article (Medium, notes, etc.)")
    parser.add_argument(
        "--platforms",
        nargs="+",
        choices=["linkedin", "instagram", "newsletter", "slides", "youtube"],
        help="Limit Phase 1 text derivatives (default: all). Phase 2 always runs.",
    )
    parser.add_argument(
        "--design",
        action="store_true",
        help="After Phase 1, generate Claude Design prompts via generate_design_prompts.py",
    )
    parser.add_argument(
        "--project",
        default=None,
        help="Build-in-public project key (see data/kb/projects.json).",
    )
    parser.add_argument(
        "--step",
        choices=["worksheet", "blog-cta", "linkedin-comment", "slides", "carousel", "reel-brief", "yt-script"],
        default=None,
        help=(
            "Run only this one Phase 2 step — skips Phase 1 entirely and forces regeneration. "
            "Choices: worksheet · blog-cta · linkedin-comment · slides · carousel · reel-brief · yt-script"
        ),
    )
    args = parser.parse_args()

    if args.project and args.project not in project_keys():
        parser.error(f"--project must be one of: {', '.join(project_keys()) or '(none defined)'}")

    if not args.input and not args.source:
        sys.exit("Require --input (blog file) or --source (article file)")
    if args.input and args.source:
        sys.exit("Choose --input OR --source, not both")

    blog_path = Path(args.input or args.source)
    if not blog_path.is_absolute():
        blog_path = REPO / blog_path
    if not blog_path.exists():
        sys.exit(f"File not found: {blog_path}")

    blog_text = blog_path.read_text(encoding="utf-8")
    slug       = blog_path.stem
    date_str   = slug[:10]
    niche      = niche_from_slug(slug)
    out_dir    = derivatives_dir(date_str, slug)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── Phase 1: Claude call → all text derivatives ────────────────────────
    if args.step:
        console.print(f"[info]--step {args.step!r}: skipping Phase 1 → running Phase 2 step only[/info]")
    else:
        console.rule("[info]Phase 1 — Text derivatives[/info]")
        source_type = "Source article" if args.source else "Blog"
        console.print(f"{source_type}: [bold]{blog_path.name}[/bold]")
        if args.platforms:
            console.print(f"Platforms: {', '.join(args.platforms)}")

        repurposing_agent = load(REPO / "prompts" / "repurposing_agent.md")
        hook_patterns = load(REPO / "data" / "kb" / "twitter_hook_patterns.json", required=False)
        ig_insights   = load(REPO / "data" / "kb" / "ig_insights.json", required=False)
        master_brief  = load(REPO / "data" / "kb" / "master_brief.md", required=False)

        if not hook_patterns:
            console.print("[warn]twitter_hook_patterns.json not found — fallback active[/warn]")
        if not ig_insights:
            console.print("[warn]ig_insights.json not found — fallback active[/warn]")
        if not master_brief:
            console.print("[warn]master_brief.md not found — competition intelligence unavailable[/warn]")

        combined_prompt = build_prompt(
            repurposing_agent, hook_patterns, ig_insights, blog_text,
            niche=niche, project_key=args.project,
            master_brief=master_brief,
        )

        parsed, usage = generate(combined_prompt)

        saved = save_derivatives(out_dir, parsed, args.platforms, niche)
        console.print(f"\n[success]✓ {len(saved)} derivatives → {out_dir.relative_to(REPO)}[/success]")
        for f in saved:
            console.print(f"  [dim]{f}[/dim]")

        # Inject worksheet CTA into derivatives immediately (DS/Life, if published)
        if niche in ("ds", "life"):
            from lib.worksheet_cta import (
                inject_worksheet_ctas_to_dir,
                extract_worksheet_slug_from_dir,
                worksheet_exists,
            )
            ws_slug = extract_worksheet_slug_from_dir(slug)
            if ws_slug and worksheet_exists(ws_slug):
                modified = inject_worksheet_ctas_to_dir(out_dir, ws_slug, niche)
                if modified:
                    console.print(
                        f"\n[success]✓ Worksheet CTA injected into {len(modified)} derivatives[/success]"
                    )

        schedule_file = out_dir / "schedule.json"
        if not schedule_file.exists():
            schedule_path = write_schedule_json(slug, niche, REPO / "content" / "derivatives")
            console.print(f"[success]✓ Schedule:[/success] {schedule_path.relative_to(REPO)}")
        else:
            console.print(f"[dim]Schedule already exists:[/dim] {schedule_file.relative_to(REPO)}")

        console.print(f"\n[dim]Token usage ({usage['backend']}):[/dim]")
        if usage["backend"] == "claude-pro-subprocess":
            console.print("  [dim]Not available for claude -p subprocess[/dim]")
        else:
            console.print(f"  Input:  {usage['input_tokens']:,}")
            console.print(f"  Output: {usage['output_tokens']:,}")
            console.print(f"  Total:  {usage['input_tokens'] + usage['output_tokens']:,}")

        if args.design:
            console.rule("[info]Claude Design Prompt Generator[/info]")
            result = subprocess.run(
                [sys.executable, str(REPO / "scripts" / "generate_design_prompts.py"),
                 "--input", str(blog_path)],
                cwd=REPO,
            )
            if result.returncode != 0:
                console.print("[warn]Design prompt generation failed — run manually:[/warn]")
                console.print(
                    f"  python scripts/generate_design_prompts.py --input {blog_path.relative_to(REPO)}"
                )

    # ── Phase 2: expanded derivatives ─────────────────────────────────────
    console.rule("[info]Phase 2 — Expanded derivatives[/info]")
    week      = get_iso_week(date_str)
    SCRIPTS   = REPO / "scripts"
    proj_flag = ["--project", args.project] if args.project else []
    step_only = args.step  # None = all; else = only this step (force-run)

    def should_run(step_name: str, out_path: Path | None = None) -> bool:
        """True if this Phase 2 step should execute.

        In --step mode: True only for the targeted step; ignores out_path (force-run).
        In normal mode: True unless out_path already exists (idempotency).
        """
        if step_only:
            if step_only != step_name:
                console.print(f"  [dim]skip — run with --step {step_name} to target[/dim]")
                return False
            return True
        if out_path and out_path.exists():
            console.print(f"  [dim]skip — {out_path.relative_to(REPO)} exists[/dim]")
            return False
        return True

    # 2a. Worksheet outline + Canva design prompt (DS/Life only)
    #     Generates:
    #       content/worksheets/{week}/{slug}_worksheet.json   ← structure/outline
    #       content/prompts/{week}/{slug}_worksheet_prompt.txt ← Canva design prompt
    #     The actual PDF is Canva-manual (use the prompt above). After publishing the PDF,
    #     run inject_worksheet_ctas.py to push URLs into captions and this blog file.
    if niche in ("ds", "life"):
        console.print("\n[bold]2a. Worksheet outline (JSON)[/bold]")
        ws_json = REPO / "content" / "worksheets" / week / f"{slug}_worksheet.json"
        if should_run("worksheet", ws_json):
            run_step(
                ["python3", SCRIPTS / "generate_worksheet_outline.py", "-i", str(blog_path)],
                "generate_worksheet_outline",
            )

    # 2b. Inject worksheet CTA into the blog .md file itself (DS/Life only)
    #     Runs only when the worksheet is published (present in the manifest).
    #     The function is self-idempotent (checks has_cta internally).
    if niche in ("ds", "life"):
        console.print("\n[bold]2b. Blog worksheet CTA[/bold]")
        if not step_only or step_only == "blog-cta":
            inject_worksheet_cta_into_blog(blog_path, slug)
        else:
            console.print(f"  [dim]skip — run with --step blog-cta to target[/dim]")

    # 2c. LinkedIn first comment — worksheet URL (DS/Life only)
    #     Strategy: 1st comment = Worksheet, 2nd comment = Blog link (written in Phase 1).
    #     Only written once the worksheet is published (manifest check inside function).
    if niche in ("ds", "life"):
        console.print("\n[bold]2c. LinkedIn first comment (worksheet URL)[/bold]")
        li1_path = out_dir / "linkedin_first_comment.txt"
        if not step_only or step_only == "linkedin-comment":
            if step_only == "linkedin-comment":
                li1_path.unlink(missing_ok=True)   # force regeneration when explicitly targeted
            write_linkedin_first_comment(out_dir, slug)
        else:
            console.print(f"  [dim]skip — run with --step linkedin-comment to target[/dim]")

    # 2c2. LinkedIn document post comments — 1st=Worksheet, 2nd=YT link (DS/Life only)
    if niche in ("ds", "life"):
        console.print("\n[bold]2c2. LinkedIn document post comments (worksheet + YT link)[/bold]")
        if not step_only or step_only == "linkedin-comment":
            write_linkedin_document_comments(out_dir, slug, week)
        else:
            console.print(f"  [dim]skip — run with --step linkedin-comment to target[/dim]")

    # 2d. Slide deck (reads slide_outline.json from Phase 1)
    console.print("\n[bold]2d. Slide deck[/bold]")
    slides_html = REPO / "assets" / "slides" / week / f"{slug}_slides.html"
    if should_run("slides", slides_html):
        run_step(
            ["python3", SCRIPTS / "generate_slide_deck.py", "--slug", slug]
            + (["--force"] if step_only else []) + proj_flag,
            "generate_slide_deck",
        )

    # 2e. IG carousel (HTML + Playwright PNG export)
    console.print("\n[bold]2e. IG carousel[/bold]")
    carousel_html = REPO / "assets" / "carousels" / f"{slug}_carousel.html"
    if should_run("carousel", carousel_html):
        run_step(
            ["python3", SCRIPTS / "generate_carousel.py",
             "--blog", str(blog_path), "--export"]
            + (["--force"] if step_only else []) + proj_flag,
            "generate_carousel",
        )

    # 2f. IG reel brief
    console.print("\n[bold]2f. IG reel brief[/bold]")
    reel_brief = out_dir / "ig_reel_brief.md"
    if should_run("reel-brief", reel_brief):
        run_step(
            ["python3", SCRIPTS / "generate_ig_reel_brief.py",
             "--slug", slug, "--week", week] + proj_flag,
            "generate_ig_reel_brief",
        )

    # 2g. YT filming script (inline Claude call → content/scripts/{week}/{slug}_yt.md)
    console.print("\n[bold]2g. YT filming script[/bold]")
    yt_script_path = REPO / "content" / "scripts" / week / f"{slug}_yt.md"
    if should_run("yt-script", yt_script_path):
        generate_yt_script(blog_text, slug, week, niche)

    console.print()


if __name__ == "__main__":
    main()
