#!/usr/bin/env python3
"""Generate a blog post using claude -p (Claude Pro subscription, no API key needed)."""

import argparse
import json
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

from _console import console, spinner

REPO = Path(__file__).parent.parent
NICHES = {"ds": "data_science_tech", "life": "life_self_dev", "poetry": "poetry_quotes"}


from lib.slug import slugify
from lib.schedule_calc import write_schedule_json, get_iso_week
from lib.virality import virality_block, project_keys, trigger_lexicon
from lib.worksheet_cta import worksheet_cta_markdown, has_cta, worksheet_url
from lib import interview as interview_flow
from lib.seo import extract_seo, seo_manual_steps
from lib.manual_steps import write_manual_steps
from lib.image_decision import decide_image, parse_markers
from lib.niche_config import model_for

# Niches that ship a companion worksheet (poetry does not).
WORKSHEET_NICHES = {"ds", "life"}

# Seven distinct emotion levers — shared by topic suggestion and title generation
# so candidate angles carry emotional pull / a curiosity gap before a title exists.
EMOTION_LEVERS = (
    "1. [FOMO]             — reader feels left behind if they don't read this now\n"
    "2. [FEAR]             — loss, risk, or negative consequence if they ignore this\n"
    "3. [CURIOSITY GAP]    — incomplete info that forces a click to resolve\n"
    "4. [COUNTERINTUITIVE] — violates common wisdom; surprises the reader\n"
    "5. [ASPIRATION]       — reader imagines a better version of themselves after reading\n"
    "6. [INSIDER SECRET]   — implies privileged knowledge others don't have\n"
    "7. [SOCIAL PROOF / SPECIFICITY] — specific numbers, timeframes, or results that signal credibility"
)


def load(path: Path) -> str:
    if not path.exists():
        sys.exit(f"Missing: {path}")
    return path.read_text(encoding="utf-8")


# ──────────────────────────────────────────────────────────────────────────────
# Research config (topic suggestion + title generation)
# ──────────────────────────────────────────────────────────────────────────────

RESEARCH_CONFIG: dict[str, dict] = {
    "ds": {
        "label": "Data Science / Tech",
        "google_seeds": [
            "data science career 2026", "machine learning for data scientists",
            "python data engineering", "AI tools for analysts", "Claude for data science",
        ],
        "medium_feeds": [
            "https://medium.com/feed/tag/data-science",
            "https://medium.com/feed/tag/machine-learning",
        ],
    },
    "life": {
        "label": "Life & Self-Development",
        "google_seeds": [
            "productivity habits 2025", "self improvement morning routine",
            "focus and deep work tips", "personal growth mindset", "discipline vs motivation",
        ],
        "medium_feeds": [
            "https://medium.com/feed/tag/self-improvement",
            "https://medium.com/feed/tag/productivity",
        ],
    },
    "poetry": {
        "label": "Poetry / Quotes",
        "google_seeds": [
            "poetry about life lessons", "short poem about change and growth",
            "quotes on grief and growth", "poem about solitude meaning",
        ],
        "medium_feeds": [
            "https://medium.com/feed/tag/poetry",
        ],
    },
}


# Type-specific Google seed overrides for DS (applied when --type is set).
_DS_TYPE_SEEDS: dict[str, list[str]] = {
    "tutorial": [
        "python data science tutorial 2026",
        "Claude MCP hands-on tutorial",
        "build AI agent python step by step",
        "machine learning code example 2026",
        "automate data pipeline python tutorial",
    ],
    "news": [
        "AI impact on data science jobs 2026",
        "data science career trends 2026",
        "machine learning industry news 2026",
        "Claude AI latest news analysis",
        "data scientist future AI era",
    ],
}


def _get(url: str, timeout: int = 6) -> str:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; RSS reader)"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""


def fetch_google_signals(niche: str, seeds_override: list[str] | None = None) -> list[str]:
    seeds = seeds_override or RESEARCH_CONFIG[niche]["google_seeds"]
    seen: set[str] = set()
    results: list[str] = []
    for seed in seeds[:3]:
        q = urllib.parse.quote_plus(seed)
        raw = _get(f"https://suggestqueries.google.com/complete/search?client=firefox&q={q}")
        try:
            data = json.loads(raw)
            for s in (data[1] if len(data) > 1 else []):
                if s not in seen:
                    seen.add(s)
                    results.append(s)
        except Exception:
            pass
    return results[:15]


def fetch_medium_titles(niche: str) -> list[str]:
    feeds = RESEARCH_CONFIG[niche]["medium_feeds"]
    titles: list[str] = []
    for url in feeds:
        raw = _get(url, timeout=8)
        for m in re.findall(r"<title><!\[CDATA\[(.+?)\]\]></title>", raw):
            if m not in titles:
                titles.append(m)
        for m in re.findall(r"<title>(.+?)</title>", raw):
            clean = re.sub(r"<[^>]+>", "", m).strip()
            if clean and clean not in titles and "Medium" not in clean:
                titles.append(clean)
    return titles[1:16]  # skip feed-level title


def get_recent_titles(niche: str, days: int = 90) -> list[str]:
    cutoff = date.today() - timedelta(days=days)
    niche_str = NICHES[niche]          # e.g. "data_science_tech"
    blog_dir = REPO / "content" / "blogs"
    titles: list[str] = []

    # ── Primary source: annual tracker (authoritative per CLAUDE.md "TRACKER FIRST") ──
    try:
        from lib.tracker import read_recent_titles as _tracker_titles
        tracker_titles = _tracker_titles(niche, days=days)
        if tracker_titles:
            titles.extend(tracker_titles)
    except Exception:
        pass  # tracker unavailable — filesystem fallback below

    # ── Fallback / supplement: scan blogs/ directory for any missing entries ──
    seen_lower = {t.lower() for t in titles}
    if not blog_dir.exists():
        return titles
    for md in blog_dir.rglob("*.md"):
        stem = md.stem
        if f"_{niche_str}_" not in stem:
            continue
        date_part = stem.split(f"_{niche_str}_")[0]
        try:
            file_date = date.fromisoformat(date_part)
        except ValueError:
            continue
        if file_date < cutoff:
            continue
        for line in md.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("#"):
                t = line.lstrip("#").strip()
                if t and t.lower() not in seen_lower:
                    titles.append(t)
                    seen_lower.add(t.lower())
                break
    return titles


def suggest_topics(
    niche: str,
    google: list[str],
    medium: list[str],
    recent: list[str],
    blog_type: str | None = None,
) -> list[str]:
    cfg = RESEARCH_CONFIG[niche]
    recent_block = (
        "Already covered in the last 90 days — avoid these angles:\n"
        + "\n".join(f"  - {t}" for t in recent[:20])
        if recent else "No recent posts found."
    )
    google_block = "\n".join(f"  - {s}" for s in google[:12]) or "  (unavailable)"
    medium_block = "\n".join(f"  - {t}" for t in medium[:10]) or "  (unavailable)"
    trigger_block = ", ".join(trigger_lexicon(niche))

    type_directive = ""
    if niche == "ds" and blog_type:
        type_directive = {
            "tutorial": (
                "\nBLOG TYPE: TUTORIAL — every topic must be code-first: a step-by-step how-to, "
                "hands-on guide, or worked example. Examples: 'Build X with Claude', "
                "'How to automate Y in Python', 'Step-by-step: setting up Z'. Readers learn by doing.\n"
            ),
            "news": (
                "\nBLOG TYPE: NEWS/OPINION — every topic must be conceptual or editorial, no code. "
                "Angles: current AI/DS industry developments, job market analysis, tool comparisons, "
                "contrarian takes, career debates. Examples: 'Why X is wrong', "
                "'The real problem with Y', 'What Z means for DS careers'.\n"
            ),
        }.get(blog_type, "")

    prompt = f"""\
You are a content strategist for Tarun Gupta — a 10-year data scientist and creator.
Niche: {cfg['label']}
Voice: analytical but warm, personal examples, no jargon without context.
Banned words: "In conclusion", "Dive into", "Leverage", "Game-changer", "Synergy"
{type_directive}
{recent_block}

Google search signals (what people are actively searching right now):
{google_block}

Trending on Medium right now:
{medium_block}

Emotional vocabulary for this niche — lean into these words where honest, never forced:
{trigger_block}

Each of the 5 topics must pull a DIFFERENT emotion lever (do NOT print the lever — let it shape the angle):
{EMOTION_LEVERS}

Generate exactly 5 blog topic options. Each must:
- Be a fresh angle NOT covered in the last 90 days list above
- Have real demand (grounded in the search signals)
- Be specific — immediately clear what the post argues or teaches
- Carry a CURIOSITY GAP — an unresolved tension or question the post pays off
- Use a different emotion lever from the list above (all 5 distinct)
- Work as a standalone blog post (not a series)

Reply with exactly:
1. [topic]
2. [topic]
3. [topic]
4. [topic]
5. [topic]

No labels. No explanation. Just the 5 lines.
"""
    raw = run_claude(prompt, timeout=90, description="Researching topic options...")
    topics: list[str] = []
    for line in raw.splitlines():
        s = line.strip()
        if s and s[0].isdigit() and "." in s[:3]:
            t = s.split(".", 1)[1].strip()
            if t:
                topics.append(t)
    return topics[:5] or [l.strip() for l in raw.splitlines() if l.strip()][:5]


# ──────────────────────────────────────────────────────────────────────────────
# "skip" → Claude answers as the creator, in Tarun's voice
# ──────────────────────────────────────────────────────────────────────────────

SKIP_TOKEN = "skip"

_PERSONA = (
    "You are Tarun Gupta — a 10-year data scientist, writer, and creator. "
    "Answer in the FIRST PERSON as Tarun, in his authentic voice: analytical but warm, "
    "personal and specific with real examples, no jargon without context. "
    'Never use these words: "In conclusion", "Dive into", "Leverage", "Game-changer", "Synergy".'
)


def _clean_title(s: str) -> str:
    """Strip a leading [LEVER] prefix from a title option."""
    return re.sub(r"^\[[^\]]+\]\s*", "", s).strip()


def _match_option(raw: str, options: list[str]) -> str:
    """Map Claude's free-text choice back to one of the actual options.

    Claude is asked to echo an option verbatim, but may add a leading number or
    stray words. Strip a leading 'N.'/'N)' then match by exact text, then by best
    fuzzy ratio (difflib), falling back to the first option.
    """
    import difflib

    r = _clean_title(re.sub(r"^\s*\d+[.)]\s*", "", raw)).lower()
    if not r:
        return options[0]
    cleaned = [_clean_title(o).lower() for o in options]
    for opt, oc in zip(options, cleaned):
        if oc and oc == r:
            return opt
    best = difflib.get_close_matches(r, cleaned, n=1, cutoff=0.6)
    if best:
        return options[cleaned.index(best[0])]
    return options[0]


def answer_on_behalf(
    kind: str,
    *,
    master_brief: str = "",
    topic: str = "",
    niche_label: str = "",
    question: str = "",
    options: list[str] | None = None,
) -> str:
    """Generate an answer as Tarun when the creator types 'skip'.

    kind: 'topic' | 'title' → choose the strongest option (returns a verbatim option);
          'creator_input'    → write the personal angle;
          'interview'        → answer one interview question.
    """
    kb = f"\n\nWhat you know about Tarun (use it for authenticity):\n{master_brief.strip()}" if master_brief else ""
    if kind in ("topic", "title"):
        opts = options or [""]
        label = "topic" if kind == "topic" else "title"
        listing = "\n".join(f"{i}. {o}" for i, o in enumerate(opts, 1))
        prompt = (
            f"{_PERSONA}{kb}\n\nNiche: {niche_label}\n"
            f"Here are the {label} options:\n{listing}\n\n"
            f"Choose the single strongest {label} for you to publish — the one with the most "
            f"emotional pull and curiosity gap that is also true to your experience. "
            f"Reply with ONLY the chosen {label} text, exactly as written above, and nothing else."
        )
        raw = run_claude(prompt, timeout=90, description=f"Claude choosing a {label} on your behalf…")
        return _match_option(raw, opts)
    if kind == "creator_input":
        prompt = (
            f"{_PERSONA}{kb}\n\nNiche: {niche_label}\nTopic: {topic}\n\n"
            "Speaking as yourself, give the personal angle for this blog: the specific stories, "
            "opinions, lived examples, and point of view you would bring. Write 5–9 first-person "
            "sentences of raw substance (not polished prose — the article gets written from this). "
            "No preamble, just your take."
        )
        return run_claude(prompt, timeout=120, description="Claude writing your angle on your behalf…").strip()
    if kind == "interview":
        prompt = (
            f"{_PERSONA}{kb}\n\nNiche: {niche_label}\nTopic: {topic}\n\n"
            "Answer this interview question as yourself — honestly and specifically, in 2–5 sentences, "
            f"with a concrete personal example where it fits:\n\nQ: {question}\n\nReply with just your answer."
        )
        return run_claude(prompt, timeout=120, description="Claude answering on your behalf…").strip()
    return ""


def select_topic(topics: list[str], niche_label: str, master_brief: str = "") -> str:
    console.print(f"\n[bold]── Pick a topic  ·  {niche_label} ──[/bold]")
    for i, t in enumerate(topics, 1):
        console.print(f"  [bold]{i}.[/bold] {t}")
    console.print("  [dim](type a number, or 'skip' to let Claude pick on your behalf)[/dim]\n")
    while True:
        try:
            raw = input(f"  Your pick (1–{len(topics)}): ").strip()
        except EOFError:
            raw = SKIP_TOKEN
        if raw.lower() == SKIP_TOKEN:
            chosen = answer_on_behalf("topic", master_brief=master_brief, niche_label=niche_label, options=topics)
            console.print(f"  [info]Skipped — Claude picked:[/info] {chosen}")
            return chosen
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(topics):
                return topics[idx]
        except ValueError:
            pass
        console.print(f"  [warn]Enter a number between 1 and {len(topics)}, or 'skip'.[/warn]")


def get_creator_input(topic: str, niche_label: str, master_brief: str = "") -> str:
    console.print(f"\n[bold]── Your thoughts  ·  {niche_label} ──[/bold]")
    console.print(f"  Topic confirmed: [bold]{topic}[/bold]")
    console.print(
        "  Add your personal angle, examples, opinions, or stories.\n"
        "  Claude will polish the language but preserve every idea.\n"
        "  [Press Enter twice to finish · type 'skip' to let Claude write your angle on your behalf]\n"
    )
    lines: list[str] = []
    blank_count = 0
    while True:
        try:
            line = input("  > ")
        except EOFError:
            break
        if line.strip().lower() == SKIP_TOKEN and not lines:
            console.print("  [info]Skipped — Claude is writing your angle on your behalf…[/info]")
            return answer_on_behalf(
                "creator_input", master_brief=master_brief, topic=topic, niche_label=niche_label
            )
        if line == "":
            blank_count += 1
            if blank_count >= 2 or not lines:
                break
            lines.append("")
        else:
            blank_count = 0
            lines.append(line)
    return "\n".join(lines).strip()


def suggest_titles(
    niche: str,
    topic: str,
    creator_input: str,
    google: list[str],
    blog_type: str | None = None,
) -> list[str]:
    cfg = RESEARCH_CONFIG[niche]
    top_keywords = ", ".join(google[:6]) or "(unavailable)"
    creator_ctx = f"Creator's personal angle: {creator_input}" if creator_input else ""
    type_ctx = ""
    if niche == "ds" and blog_type:
        type_ctx = {
            "tutorial": (
                "Post type: CODE-FIRST TUTORIAL. "
                "Titles that imply hands-on value work well — 'Build', 'How to', "
                "'Step-by-step', 'The script that...', '[N] lines of Python that...' "
                "are strong frames. Outcome-led titles outperform topic labels."
            ),
            "news": (
                "Post type: NEWS/OPINION — no code. "
                "Titles should imply an editorial take: contrarian claim, industry analysis, "
                "career warning, or insider perspective. "
                "Declarative ('X is wrong') beats question ('Is X wrong?')."
            ),
        }.get(blog_type, "")

    prompt = f"""\
Generate 7 maximum-clickbait-but-credible blog title options for this creator.

Niche:    {cfg['label']}
Topic:    {topic}
{creator_ctx}
{type_ctx}
Keywords with real search demand: {top_keywords}

Each title must use a DIFFERENT emotion lever — prefix each line with its lever in brackets:
{EMOTION_LEVERS}

Rules every title must follow:
- Signals exactly who it's for (right reader self-selects in)
- Creates enough tension that NOT clicking feels like a loss
- As clickbait as possible while remaining credible and true to the content
- Under 85 characters where possible
- No: "game-changer", "leverage", "dive into", "secret sauce", "In conclusion"

Reply with exactly 7 lines in this format:
1. [LEVER] title text
2. [LEVER] title text
...
7. [LEVER] title text
"""
    raw = run_claude(prompt, timeout=90, description="Generating title options...")
    titles: list[str] = []
    for line in raw.splitlines():
        s = line.strip()
        if s and s[0].isdigit() and "." in s[:3]:
            t = s.split(".", 1)[1].strip()
            if t:
                titles.append(t)
    return titles[:7] or [l.strip() for l in raw.splitlines() if l.strip()][:7]


def select_title(titles: list[str], topic: str, master_brief: str = "") -> str:
    short = topic[:50] + ("…" if len(topic) > 50 else "")
    console.print(f"\n[bold]── Pick a title  ·  {short} ──[/bold]")
    for i, title in enumerate(titles, 1):
        console.print(f"  [bold]{i}.[/bold] {title}\n")
    console.print("  [dim](type a number, or 'skip' to let Claude pick on your behalf)[/dim]")
    while True:
        try:
            raw = input(f"  Your pick (1–{len(titles)}): ").strip()
        except EOFError:
            raw = SKIP_TOKEN
        if raw.lower() == SKIP_TOKEN:
            chosen = _clean_title(
                answer_on_behalf("title", master_brief=master_brief, topic=topic,
                                 niche_label="", options=titles)
            )
            console.print(f"  [info]Skipped — Claude picked:[/info] {chosen}")
            return chosen
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(titles):
                return _clean_title(titles[idx])
        except ValueError:
            pass
        console.print(f"  [warn]Enter a number between 1 and {len(titles)}, or 'skip'.[/warn]")


def select_option(options: list[str], header: str, on_skip=None) -> str:
    """Pick one option from a numbered list. Empty input defaults to option 1.
    Strips leading [LEVER] prefix from title options before returning.
    If `on_skip` is given, typing 'skip' lets Claude choose on the creator's behalf."""
    console.print(f"\n[bold]── {header} ──[/bold]")
    for i, opt in enumerate(options, 1):
        console.print(f"  [bold]{i}.[/bold] {opt}\n")
    if on_skip:
        console.print("  [dim](type a number, Enter = 1, or 'skip' to let Claude pick)[/dim]")
    while True:
        try:
            raw = input(f"  Your pick (1–{len(options)}, Enter = 1): ").strip()
        except (EOFError, KeyboardInterrupt):
            return _clean_title(options[0])
        if on_skip and raw.lower() == SKIP_TOKEN:
            chosen = _clean_title(on_skip(options))
            console.print(f"  [info]Skipped — Claude picked:[/info] {chosen}")
            return chosen
        if not raw:
            return _clean_title(options[0])
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return _clean_title(options[int(raw) - 1])
        console.print(f"  [warn]Enter a number between 1 and {len(options)}.[/warn]")


def run_interview_flow(
    niche: str,
    topic: str,
    google: list[str],
    medium: list[str],
    niche_label: str = "",
    master_brief: str = "",
) -> tuple[str, str]:
    """Two-call interview path. Returns (blog_markdown, chosen_title)."""
    cfg = interview_flow.load_interview_config(niche)
    # 'skip' on any interview question → Claude answers it as Tarun.
    answer_question = lambda q: answer_on_behalf(
        "interview", master_brief=master_brief, topic=topic, niche_label=niche_label, question=q
    )
    pick_title = lambda opts: answer_on_behalf(
        "title", master_brief=master_brief, topic=topic, niche_label=niche_label, options=opts
    )
    trend_bits = [s for s in (google[:6] + medium[:4]) if s]
    trend_context = "; ".join(trend_bits)

    # CALL 1 — questions
    angle, questions = interview_flow.generate_questions(
        run_claude, topic=topic, trend_context=trend_context, cfg=cfg,
    )
    if not questions:
        sys.exit("Interview engine returned no questions — aborting (try re-running).")
    if angle:
        console.print(f"\n[info]Suggested angle:[/info] {angle}")

    # Interactive Q&A — 'skip' a question → Claude answers it on your behalf
    qa_pairs = interview_flow.run_interview(questions, on_skip=answer_question)

    # CALL 2 — article
    parsed = interview_flow.write_article(run_claude, topic=topic, qa_pairs=qa_pairs, cfg=cfg)
    blog_md = interview_flow.assemble_markdown(parsed["title_options"][0] if parsed["title_options"] else "Draft", parsed)
    if "[IMAGE_INSERT" not in blog_md:
        console.print("[warn]No IMAGE_INSERT in article — retrying with enforcement...[/warn]")
        parsed = interview_flow.write_article(
            run_claude, topic=topic, qa_pairs=qa_pairs, cfg=cfg,
            extra_instruction="CRITICAL: You MUST include at least 1 [IMAGE_INSERT: search term | caption] marker in the article body.",
        )
    chosen_title = select_option(parsed["title_options"], "Pick a title", on_skip=pick_title)
    blog_md = interview_flow.assemble_markdown(chosen_title, parsed)

    if parsed.get("tags"):
        console.print(f"[info]Medium tags:[/info] {', '.join(parsed['tags'])}")
    return blog_md, chosen_title


def _read_poem() -> str:
    """Collect poem lines from stdin. Type && on own line to finish."""
    console.print("  [dim](paste your poem; type '&&' on a new line when done)[/dim]")
    lines: list[str] = []
    while True:
        try:
            line = input("  > ")
        except (EOFError, KeyboardInterrupt):
            break
        if line.strip() == "&&":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def run_poem_mode(topic: str, niche_label: str = "", master_brief: str = "") -> tuple[str, str]:
    """Poetry path: paste or generate a poem, wrap with 2-3 line intro + outro.
    Returns (blog_markdown, title)."""

    # ── Poem source ──────────────────────────────────────────────────────────
    console.print("\n[bold]── Poetry Mode ──[/bold]")
    console.print("  Do you have a poem to paste? [[bold]y[/bold]/n · 'skip' = Claude writes it] ", end="")
    try:
        have_poem = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        have_poem = "n"

    if have_poem == SKIP_TOKEN:
        console.print("  [info]Skipped — Claude is writing the poem on your behalf…[/info]")
        gen_prompt = (
            f"{_PERSONA}\n\nWrite a short, original poem about: {topic}.\n"
            "Voice: intimate, specific, no clichés. Length: 8–20 lines.\n"
            "Output ONLY the poem — no title, no explanation."
        )
        poem_text = run_claude(gen_prompt, timeout=120, description="Writing poem on your behalf…")
    elif have_poem in ("y", "yes", ""):
        console.print("\n  Paste your poem:")
        poem_text = _read_poem()
        if not poem_text:
            sys.exit("No poem provided — aborting.")
    else:
        # Generate poem
        console.print("\n  Topic / mood / form (e.g. 'grief in rain, free verse'): ", end="")
        try:
            prompt_input = input().strip()
        except (EOFError, KeyboardInterrupt):
            prompt_input = topic
        gen_prompt = (
            f"Write a short, original poem about: {prompt_input or topic}.\n"
            "Voice: intimate, specific, no clichés. Length: 8–20 lines.\n"
            "Output ONLY the poem — no title, no explanation."
        )
        poem_text = run_claude(gen_prompt, timeout=120, description="Writing poem...")

    # ── Title ─────────────────────────────────────────────────────────────────
    title_prompt = (
        f"Output exactly 5 short, evocative Medium titles for this poem. "
        f"Rules: one per line, no numbering, no quotes, no preamble, no explanation — "
        f"just 5 bare title lines. Emotional resonance, not clickbait.\n\nPOEM:\n{poem_text}"
    )
    raw_titles = run_claude(title_prompt, timeout=60, description="Generating titles...")
    title_options = [
        t.strip() for t in raw_titles.strip().splitlines()
        if t.strip() and not t.strip().lower().startswith(("here", "title", "1.", "2.", "3.", "4.", "5.", "-"))
    ][:5]
    if not title_options:
        title_options = [topic]
    chosen_title = select_option(
        title_options, "Pick a title",
        on_skip=lambda opts: answer_on_behalf(
            "title", master_brief=master_brief, topic=topic,
            niche_label=niche_label or "Poetry / Quotes", options=opts,
        ),
    )

    # ── Intro + Outro ─────────────────────────────────────────────────────────
    wrap_prompt = (
        f"You are a ghostwriter. Given this poem and its title, write:\n"
        f"1. INTRO: exactly 2–3 sentences before the poem. Context, mood, or when it was written. "
        f"No summary, no explanation of the poem — just a human moment that lands the reader in it.\n"
        f"2. OUTRO: exactly 2–3 sentences after the poem. A brief reflection or image that closes "
        f"the piece. The very last sentence should be a subtle, almost invisible nudge to follow "
        f"— something like 'More here, if you want it.' or 'I write more of these.' "
        f"Never say 'subscribe', 'click', 'follow me', or 'sign up'. Feel, don't sell.\n\n"
        f"Output format (exact):\nINTRO:\n<intro text>\nOUTRO:\n<outro text>\n\n"
        f"TITLE: {chosen_title}\nPOEM:\n{poem_text}"
    )
    raw_wrap = run_claude(wrap_prompt, timeout=120, description="Writing intro + outro...")

    intro, outro = "", ""
    section = None
    for line in raw_wrap.splitlines():
        if line.strip().upper() == "INTRO:":
            section = "intro"
        elif line.strip().upper() == "OUTRO:":
            section = "outro"
        elif section == "intro":
            intro = (intro + "\n" + line).strip()
        elif section == "outro":
            outro = (outro + "\n" + line).strip()

    if not intro:
        intro = ""
    if not outro:
        outro = ""

    # ── Image marker ──────────────────────────────────────────────────────────
    img_prompt = (
        f"Given this poem title and poem, write ONE specific Pexels image search term "
        f"(3-5 words, visual/concrete, no abstract nouns) that would make a beautiful "
        f"accompanying photo. Output only the search term, nothing else.\n\n"
        f"Title: {chosen_title}\nPoem:\n{poem_text}"
    )
    img_term = run_claude(img_prompt, timeout=30, description="Picking image...").strip().strip('"')
    image_marker = f"[IMAGE_INSERT: {img_term} | {chosen_title}]"

    # ── Assemble markdown ─────────────────────────────────────────────────────
    poem_block = "\n".join(f"> {ln}" for ln in poem_text.splitlines())
    blog_md = f"# {chosen_title}\n\n{intro}\n\n{image_marker}\n\n{poem_block}\n\n{outro}\n"

    return blog_md, chosen_title


def build_listicle_directive(n: int, topic: str, niche: str) -> str:
    """Listicle structure override. Forces top-N format with numbered item sections."""
    if n < 2:
        raise ValueError(f"--listicle count must be >= 2, got {n}")

    poetry_note = ""
    if niche == "poetry":
        poetry_note = (
            "\n- For poetry niche: each item is a distinct poem/quote/theme. "
            "Item bodies stay lyrical, ≤100w each."
        )

    return f"""

---

## LISTICLE OVERRIDE (this OVERRIDES the default structure in the Writing Agent Prompt)

Produce this blog as a **Top {n}** listicle. The title MUST start with "Top {n}" (or "{n} ", e.g. "{n} Ways to..."). Structure exactly:

1. **HOOK** — open with a sharp claim or stat that sets up why these {n} things matter. No throat-clearing.
2. **CONTEXT** — short framing: who this list is for, what criteria the items share, why this order.
3. **THE LIST** — exactly {n} numbered H2 sections:
   - `## 1. <Concrete item name>` ... `## {n}. <Concrete item name>`
   - Each item: one-line claim → 2-4 paragraph body → concrete example, code, or [PERSONAL_INSERT] where appropriate.
   - Order matters: rank by impact, difficulty, or chronology — state which in CONTEXT.
   - Each item body roughly equal length (±25%).
4. **TAKEAWAY** — the pattern that connects all {n} items. Not a recap.
5. **CTA** — one specific next action.

Rules:
- Item count is non-negotiable: exactly {n} items, not {n - 1}, not {n + 1}.
- No "honorable mentions" or "bonus" items appended.
- Item titles are concrete nouns/actions, not vague abstractions.{poetry_note}

Topic to listify: {topic}
"""


def build_prompt(
    writing_agent: str,
    master_brief: str,
    topic: str,
    niche: str,
    listicle: int | None = None,
    project_key: str | None = None,
    creator_input: str = "",
    chosen_title: str = "",
    blog_type: str | None = None,
) -> str:
    virality = virality_block("blog", niche, project_key)
    niche_label = {
        "ds": "Data Science/Tech",
        "life": "Life & Self-Development",
        "poetry": "Poetry/Quotes",
    }[niche]

    # DS-specific type directive — injected only when --type is set
    ds_type_block = ""
    if niche == "ds" and blog_type == "tutorial":
        ds_type_block = """

## DS BLOG TYPE: TUTORIAL
This is a code-first tutorial. Non-negotiable rules:
- Include at least 2 working, runnable Python code blocks (not pseudocode)
- Structure: problem → setup (with real imports and environment notes) → code walkthrough → result → lesson
- Code blocks appear immediately after the text that introduces them — never at the end of the piece
- Mark where full scripts or longer code belongs: [CODE_INSERT: one-line description of what the code does]
- Every snippet must be copy-paste runnable — test it mentally; every import must be present
- Do not editorialize, moralize, or pivot to career philosophy — teach the thing, then stop
"""
    elif niche == "ds" and blog_type == "news":
        ds_type_block = """

## DS BLOG TYPE: NEWS / OPINION
This is an editorial or trend piece. Non-negotiable rules:
- Zero code blocks — this is entirely conceptual, analytical, and opinionated
- Structure: strong opinion hook → what is happening → why it matters → Tarun's take → the implication
- Cite specific things: tool names, company names, dates, numbers — vague claims lose credibility
- Every paragraph must advance the argument; cut decoration
- End on an implication, not a summary, not a motivational close
"""

    word_count_constraint = (
        "\n**POETRY FORMAT — the poem leads, the essay is short.** Structure: the complete "
        "poem in one blockquote, then a SHORT reflective essay of 150–350 words (not 800+). "
        "Do not pad to long-form length. The poem is the product; the essay is one honest, "
        "specific reflection around it — no listicle, no sections, no motivational crescendo. "
        "Cut anything that does not earn its line.**"
        if niche == "poetry" else ""
    )
    listicle_block = build_listicle_directive(listicle, topic, niche) if listicle else ""

    title_rule = (
        f"3. **Title** — USE THIS EXACT TITLE (do not alter a single word): {chosen_title}\n"
        f"   # ← Do not change it."
        if chosen_title else
        "3. **Title** — use one of these four formulas (pick the strongest for the topic):\n"
        "   - Specific incident: \"The [Thing] That [Concrete Result]\"\n"
        "   - Counter-intuitive result: \"My [X] Was [Impressive Metric]. It Was Also [Failure].\"\n"
        "   - Named lesson: \"I [Situation]. Here's What [the Silence/Mistake] Was Hiding.\"\n"
        "   - Specific number + outcome: \"[N] [Things] That [Consequence]\"\n"
        "   NEVER use: \"Everything You Need to Know About X\" / \"The Ultimate Guide to Y\" / \"Why Z Matters\""
    )
    creator_block = (
        f"\n## Creator's Personal Angle (weave throughout — do not quote verbatim)\n"
        f"Polish the language freely, but preserve every idea and viewpoint:\n\n"
        f"{creator_input}\n"
        if creator_input else ""
    )

    return f"""{writing_agent}

---

## Virality Directives (apply throughout)

{virality}
{ds_type_block}
---

## Knowledge Base (master_brief.md)

{master_brief}

---
{creator_block}
## Task

Niche: {niche_label}
Topic: {topic}
{word_count_constraint}

Follow every instruction in the Writing Agent Prompt above.
Complete all pre-writing steps (Notion query note: operate as if you have reviewed recent published posts and confirmed this angle is unexplored — focus on writing).
Produce the full blog post in clean Markdown, structured exactly as specified.

**MANDATORY REQUIREMENTS (no exceptions):**
1. Include at least 1 `[IMAGE_INSERT: concrete pexels search term]` marker in the blog body.
2. For poetry niche: embed the complete poem (if one is core to the topic) in one unbroken blockquote block right after the HOOK.
{title_rule}
4. **First paragraph** — open on the specific incident or counter-intuitive fact, NOT with context-setting. Hook line first. One sentence of context second. The reader must know exactly why they're reading this by the end of the first paragraph.
5. **Subheadings** — every subheading must be a hook that pulls a skimmer in, not a section label. "The Problem" → "The Problem That 6 Months of Work Couldn't Solve". No exceptions.
6. **Shareable sentence** — identify the single most shareable sentence in the piece (the one a stranger would screenshot and send to a friend — NOT the thesis, but the most specific or emotionally precise observation). Mark it inline with `[QUOTABLE]`.
7. **Final paragraph** — end with weight. No bullet-point recap of what you covered. No "Let me know your thoughts in the comments." End on the [QUOTABLE] sentence, a question that stays with the reader, or a one-sentence implication of everything that came before.
{listicle_block}"""


def run_claude(prompt: str, timeout: int, description: str) -> str:
    # hero_blog routes via niche_config.MODEL_BY_TASK (Fable 5) — single turns can
    # run minutes on hard tasks, so article-writing callers pass generous timeouts.
    model = model_for("hero_blog")
    with spinner() as progress:
        task = progress.add_task(description)
        result = subprocess.run(
            ["claude", "-p", prompt, "--model", model],
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


HUMANIZE_PROMPT = """\
You are an editor performing a humanization pass on a blog post.

Apply these fixes — no exceptions:

1. Remove all AI tells:
   - Correlative constructions: "X aren't just Y, they're Z" → rewrite as direct claim
   - Filler hedges: might, could, perhaps, seems, possibly → commit or cut
   - Overused words: just, actually, basically, simply, really → cut or replace
   - Transition overuse: Furthermore, Moreover, Additionally, It's worth noting → cut or natural alternative
   - Throat-clearing openers: "In this post..." / "Today we'll..." → delete, start with substance

2. Strengthen weak sentences:
   - Passive → active voice
   - Vague claims → specific ones (if specific data isn't in text, mark with [SPECIFIC_NEEDED])
   - Long compound sentences → two short ones where rhythm improves

3. Preserve everything else exactly:
   - All [PERSONAL_INSERT], [CODE_INSERT], [IMAGE_INSERT] markers — do not touch
   - All Markdown structure, headings, code blocks
   - The author's voice, opinions, and specific examples
   - Word count within ±10%

Return ONLY the revised blog post. No preamble. No explanation.

---

Blog post to humanize:

"""


def main():
    parser = argparse.ArgumentParser(description="Produce a blog post via Claude Pro.")
    parser.add_argument(
        "--topic", default=None,
        help="Blog topic (omit to pick from 5 research-driven options)",
    )
    parser.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    parser.add_argument(
        "--humanize",
        action="store_true",
        help="Run a post-generation humanization pass to remove AI tells",
    )
    parser.add_argument(
        "--interview",
        action="store_true",
        help=(
            "Replace the free-text creator-input step with a two-call interview: "
            "model generates questions (prompts/question_generator.md), you answer "
            "interactively, model writes the article (prompts/article_writer.md). "
            "Config: config/interview.json. Omit to use the classic raw-input flow."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the full flow and save the draft, but never publish/stage to Medium.",
    )
    parser.add_argument(
        "--listicle",
        type=int,
        default=None,
        metavar="N",
        help="Produce a Top-N listicle blog (e.g. --listicle 5 for 'Top 5...'). N must be >= 2.",
    )
    parser.add_argument(
        "--project",
        default=None,
        help="Build-in-public project key (see data/kb/projects.json) — injects project virality context.",
    )
    parser.add_argument(
        "--type",
        choices=["tutorial", "news"],
        default=None,
        dest="blog_type",
        help=(
            "DS niche only. 'tutorial' = code-first procedural post with runnable Python; "
            "'news' = editorial/opinion/trend piece with no code. Rejected for Life and Poetry."
        ),
    )
    parser.add_argument(
        "--no-worksheet",
        action="store_true",
        help="Skip auto-generating the companion worksheet (DS/Life niches).",
    )
    parser.add_argument(
        "--image",
        choices=["auto", "stock", "ai"],
        default="auto",
        help=(
            "Image strategy. 'auto' = Claude decides AI vs stock per blog (default); "
            "'stock' = always fetch from Pexels; 'ai' = always emit an AI image prompt."
        ),
    )
    args = parser.parse_args()

    if args.listicle is not None and args.listicle < 2:
        parser.error("--listicle N must be >= 2")
    if args.project and args.project not in project_keys():
        parser.error(f"--project must be one of: {', '.join(project_keys()) or '(none defined)'}")
    if args.blog_type and args.niche != "ds":
        parser.error("--type is only valid for --niche ds")

    console.rule(f"[info]Blog Producer[/info]")
    console.print(f"Niche: [niche]{args.niche}[/niche]")
    if args.blog_type:
        console.print(f"Type:  [bold]{args.blog_type.upper()}[/bold]")

    writing_agent = load(REPO / "prompts" / "writing_agent.md")
    master_brief  = load(REPO / "data" / "kb" / "master_brief.md")

    # ── Step 1: Topic ────────────────────────────────────────────────────────
    google: list[str] = []
    medium: list[str] = []
    niche_label = RESEARCH_CONFIG[args.niche]["label"]
    # Use type-specific seeds for DS when --type is set
    ds_seeds = _DS_TYPE_SEEDS.get(args.blog_type) if args.blog_type else None

    if args.topic:
        topic = args.topic
        console.print(f"Topic: [bold]{topic}[/bold]")
        # Still fetch Google signals for title generation
        google = fetch_google_signals(args.niche, seeds_override=ds_seeds)
    else:
        console.print("\n[info]Fetching research signals...[/info]")
        recent = get_recent_titles(args.niche)
        console.print(f"  Recent blogs (last 90 days): {len(recent)} found")
        google = fetch_google_signals(args.niche, seeds_override=ds_seeds)
        console.print(f"  Google signals: {len(google)} found")
        medium = fetch_medium_titles(args.niche)
        console.print(f"  Medium titles: {len(medium)} found")
        topics = suggest_topics(args.niche, google, medium, recent, blog_type=args.blog_type)
        topic  = select_topic(topics, niche_label, master_brief=master_brief)
        console.print(f"\nTopic: [bold]{topic}[/bold]")

    # ── Steps 2–5: Draft ──────────────────────────────────────────────────────
    if args.niche == "poetry" and not args.interview:
        # Poetry mode: paste or generate poem + 2-3 line intro/outro only.
        blog_text, chosen_title = run_poem_mode(topic, niche_label=niche_label, master_brief=master_brief)
        console.print(f"\nTitle locked: [bold]{chosen_title}[/bold]\n")
    elif args.interview:
        # Two-call interview flow replaces creator-input + title + draft generation.
        if args.listicle or args.blog_type:
            console.print("[warn]--listicle/--type are ignored in --interview mode.[/warn]")
        blog_text, chosen_title = run_interview_flow(
            args.niche, topic, google, medium,
            niche_label=niche_label, master_brief=master_brief,
        )
        console.print(f"\nTitle locked: [bold]{chosen_title}[/bold]\n")
    else:
        # ── Step 2: Creator input ──────────────────────────────────────────────
        creator_input = get_creator_input(topic, niche_label, master_brief=master_brief)

        # ── Step 3: Title selection ────────────────────────────────────────────
        titles       = suggest_titles(args.niche, topic, creator_input, google, blog_type=args.blog_type)
        chosen_title = select_title(titles, topic, master_brief=master_brief)
        console.print(f"\nTitle locked: [bold]{chosen_title}[/bold]\n")

        # ── Step 4: Build prompt ───────────────────────────────────────────────
        combined_prompt = build_prompt(
            writing_agent, master_brief, topic, args.niche,
            listicle=args.listicle, project_key=args.project,
            creator_input=creator_input, chosen_title=chosen_title,
            blog_type=args.blog_type,
        )
        if args.listicle:
            console.print(f"[info]Listicle mode:[/info] Top {args.listicle}")
        if args.blog_type:
            console.print(f"[info]Blog type:[/info] {args.blog_type.upper()}")

        # Step 5 — generate blog
        blog_text = run_claude(combined_prompt, timeout=900,
                               description="Generating blog (2–5 min)...")

        # Validate IMAGE_INSERT present; retry once if missing
        if "[IMAGE_INSERT" not in blog_text:
            console.print("[warn]Warning: No IMAGE_INSERT found. Retrying with reinforced prompt...[/warn]")
            retry_prompt = combined_prompt + "\n\n**CRITICAL: You MUST include at least 1 [IMAGE_INSERT: ...] marker in the blog body.**"
            blog_text = run_claude(retry_prompt, timeout=900, description="Retrying with IMAGE_INSERT enforcement...")
            if "[IMAGE_INSERT" not in blog_text:
                console.print("[warn]⚠ Still no IMAGE_INSERT after retry. Proceeding anyway.[/warn]")

    # Step 1b — humanize (optional)
    if args.humanize:
        blog_text = run_claude(
            HUMANIZE_PROMPT + blog_text,
            timeout=300,
            description="Humanizing (removing AI tells)...",
        )

    # Step 2 — save
    today = date.today().isoformat()
    slug  = slugify(topic)  # use the local `topic` var, not args.topic (which can be None)
    filename = f"{today}_{NICHES[args.niche]}_{slug}.md"
    week = get_iso_week(today)
    out_dir  = REPO / "content" / "blogs" / week
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename

    # Append worksheet CTA for niches that ship a worksheet (idempotent).
    # Interview mode already ends with a tailored email CTA — don't double it.
    if not args.interview and args.niche in WORKSHEET_NICHES and not has_cta(blog_text):
        blog_text = blog_text.rstrip() + "\n\n" + worksheet_cta_markdown(slug)

    out_path.write_text(blog_text, encoding="utf-8")

    # Write schedule.json to derivatives dir; slug_dir is the per-slug home.
    full_slug = f"{today}_{NICHES[args.niche]}_{slug}"
    deriv_dir = REPO / "content" / "derivatives"
    schedule_path = write_schedule_json(full_slug, args.niche, deriv_dir)
    slug_dir = schedule_path.parent

    rel = out_path.relative_to(REPO)
    word_count = len(blog_text.split())
    personal_inserts = blog_text.count("[PERSONAL_INSERT")
    code_inserts     = blog_text.count("[CODE_INSERT")
    image_inserts    = blog_text.count("[IMAGE_INSERT")

    console.print(f"\n[success]✓ Saved:[/success] {rel}")
    console.print(f"[success]✓ Schedule:[/success] {schedule_path.relative_to(REPO)}")
    console.print(f"  Words: {word_count:,}  ·  PERSONAL:{personal_inserts} CODE:{code_inserts} IMAGE:{image_inserts}")

    # Collected human to-dos → written to a per-slug sidecar (not the blog body).
    manual: list[tuple[str, str]] = [
        ("Blog", f"- File: `{rel}`\n- Words: {word_count:,}\n- Slug: `{slug}` · Week: {week}"),
    ]
    if personal_inserts or code_inserts or image_inserts:
        manual.append((
            "Fill INSERT markers",
            f"- {personal_inserts} `[PERSONAL_INSERT]`\n- {code_inserts} `[CODE_INSERT]`"
            f"\n- {image_inserts} `[IMAGE_INSERT]`\n\n`grep -rn 'INSERT' content/blogs/{week}/{filename}`",
        ))

    # ── Step 3 — image strategy: AI vs stock ──────────────────────────────────
    if image_inserts:
        markers = parse_markers(blog_text)
        decision = decide_image(
            blog_text, args.niche, markers,
            force=(None if args.image == "auto" else args.image),
        )
        if decision["recommendation"] == "ai":
            console.print(f"\n[info]Image:[/info] AI recommended — {decision['reason']}")
            body = [f"**Recommendation: AI image** — {decision['reason']}",
                    "", "_Paste each prompt into your image generator (ChatGPT image / DALL·E):_", ""]
            for i, p in enumerate(decision["prompts"], 1):
                body.append(f"### Image {i} — {p.get('slot','')}\n\n```\n{p.get('prompt','').strip()}\n```\n")
            manual.append(("Image — AI generated", "\n".join(body)))
            console.print("  AI image prompt(s) saved to the manual-steps file (no stock fetched).")
        else:
            manual.append(("Image — stock", f"{decision.get('reason','')}\nFetched from Pexels into the blog's _images dir."))
            if not args.dry_run:
                console.print(f"\n[info]Fetching {image_inserts} image(s) from Pexels...[/info]")
                result = subprocess.run(
                    [sys.executable, str(Path(__file__).parent / "fetch_images.py"), "--input", str(out_path)],
                    capture_output=False,
                )
                if result.returncode != 0:
                    console.print("[warn]Image fetch failed — fill [IMAGE_INSERT] markers manually.[/warn]")

    # ── Step 4 — companion worksheet (DS/Life): Claude-designed HTML → PDF ─────
    if args.niche in WORKSHEET_NICHES and not args.no_worksheet:
        try:
            console.print("\n[info]Building companion worksheet (Claude-designed → PDF)...[/info]")
            subprocess.run(
                [sys.executable, str(Path(__file__).parent / "generate_worksheet_html.py"), "-i", str(out_path)],
                check=True,
            )
            subprocess.run(
                ["node", str(Path(__file__).parent / "build-worksheets-manifest.mjs")],
                check=True, capture_output=True,
            )
            url = worksheet_url(slug)
            console.print(f"  [success]✓ Worksheet ready[/success] · {url}")
            manual.append(("Worksheet", f"Gated link (CTA already auto-added to the blog body):\n\n{url}"))
        except Exception as e:  # noqa: BLE001 — never fail the blog on the worksheet
            console.print(f"[warn]Worksheet step failed: {e}[/warn]")
            manual.append(("Worksheet", f"⚠️ generation failed: {e}\nRetry: `python3 scripts/generate_worksheet_html.py -i {rel}`"))

    # ── SEO + publish → sidecar (Medium API can't set SEO title/description) ───
    seo_steps = seo_manual_steps(extract_seo(blog_text))
    if seo_steps:
        manual.append(("SEO — set manually on Medium", seo_steps))
    manual.append(("Publish", f"```\npython3 scripts/publish_medium.py --input {rel} --status draft\n```"))

    steps_path = write_manual_steps(slug_dir, full_slug, manual)
    console.print(f"\n[success]✓ Manual steps:[/success] {steps_path.relative_to(REPO)}")

    if args.dry_run:
        console.print("[info]DRY RUN:[/info] draft saved locally. Nothing staged or published to Medium.")


if __name__ == "__main__":
    main()
