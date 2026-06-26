#!/usr/bin/env python3
"""Weekly idea machine — surfaces virality-scored ideas + mandatory project reels + raw takes.

Reads:
  data/ideas/{source}_{date}.json  — suggest / youtube / reddit / external for each day this week
  data/kb/projects.json            — build-in-public projects + angle rotation
  data/kb/raw_take_questions.json  — 28 Hinglish raw-take questions (Life niche, 4/week)
  data/kb/master_brief.md          — voice / competition intelligence
  data/kb/twitter_hook_patterns.json

Outputs:
  data/ideas/weekly_ideas.md       — overwritten with --force

Usage:
  python3 scripts/idea_scorer.py               # current ISO week
  python3 scripts/idea_scorer.py --week W27    # specific week
  python3 scripts/idea_scorer.py --force       # regenerate even if file exists
  python3 scripts/idea_scorer.py --dry-run     # print to stdout, don't write
  python3 scripts/idea_scorer.py --top 8       # more ideas per niche
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import anthropic
from dotenv import load_dotenv
from rich.console import Console

REPO    = Path(__file__).resolve().parent.parent
DATA    = REPO / "data"
IDEAS   = DATA / "ideas"
KB      = DATA / "kb"
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lib.schedule_calc import get_iso_week  # noqa: E402

load_dotenv(REPO / ".env")
console = Console()

# ── Niche constants ───────────────────────────────────────────────────────────

_NICHE_LABELS = {
    "ds":     "DS — Data Science / Tech",
    "life":   "Life — Life & Self-Development",
    "poetry": "Poetry / Quotes",
}
_NICHE_JSON_KEYS = {
    "ds":     "data_science_tech",
    "life":   "life_self_dev",
    "poetry": "poetry_quotes",
}
_JSON_TO_NICHE = {v: k for k, v in _NICHE_JSON_KEYS.items()}

# ── Off-topic filters (preserved from original) ───────────────────────────────

NICHE_BLOCKLIST = {
    "poetry": re.compile(
        r"\b(AI|GPT|ChatGPT|LLM|Claude|Anthropic|OpenAI|machine learning|"
        r"agent|crypto|bitcoin|startup|saas|stripe|kubernetes|docker|api)\b|"
        r"\b(ASMR|fanfic|fanfiction|songwriter|songwriting|lyrics|"
        r"taylor swift|beyonc[eé]|kanye|drake|"
        r"netflix|hbo|movie review|tv show|anime|kdrama|"
        r"trump|biden|election|congress|senate|"
        r"how to write|writing tips|writing prompt|world.?building|"
        r"discourse|treatise|hermeneutic|exegesis|"
        r"marketing|seo|conversion|funnel|monetiz|substack growth)\b",
        re.IGNORECASE,
    ),
    "life": re.compile(
        r"\b(AI|GPT|ChatGPT|LLM|crypto|bitcoin|kubernetes|docker)\b",
        re.IGNORECASE,
    ),
}

HASHTAG_SPAM   = re.compile(r"(#\w+\s*){3,}")
ACADEMIC_ESSAY = re.compile(
    r"\b(reception of|reading of|analysis of|study of|in the works of|"
    r"hermeneutic|exegesis|literary criticism)\b",
    re.IGNORECASE,
)


def _passes_blocklist(item: dict) -> bool:
    niche   = item.get("niche", "")
    payload = f"{item.get('title','')} {item.get('summary','')}"
    pattern = NICHE_BLOCKLIST.get(niche)
    if pattern and pattern.search(payload):
        return False
    if niche == "poetry":
        if HASHTAG_SPAM.search(item.get("title", "")):
            return False
        if ACADEMIC_ESSAY.search(item.get("title", "")):
            return False
    return True


# ── Loaders ──────────────────────────────────────────────────────────────────

def _load_json(path: Path, required: bool = False) -> Any:
    if not path.exists():
        if required:
            sys.exit(f"Required file not found: {path}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        console.print(f"[warn]JSON error in {path}: {e}[/warn]")
        return None


def _week_dates(week: str) -> list[str]:
    """Return ISO date strings Mon–Sun for the given '2026-W26' week string."""
    year_str, wk_str = week.split("-W")
    year, wk = int(year_str), int(wk_str)
    jan4     = datetime.date(year, 1, 4)
    week1_mon = jan4 - datetime.timedelta(days=jan4.weekday())
    week_mon  = week1_mon + datetime.timedelta(weeks=wk - 1)
    return [(week_mon + datetime.timedelta(days=d)).isoformat() for d in range(7)]


def _load_week_ideas(week: str) -> dict[str, list[dict]]:
    """Aggregate all per-day idea files for the week into per-niche item lists."""
    dates   = _week_dates(week)
    sources = ["suggest", "youtube", "reddit", "external"]
    agg: dict[str, list[dict]] = {k: [] for k in _NICHE_JSON_KEYS.keys()}

    for date in dates:
        for src in sources:
            data = _load_json(IDEAS / f"{src}_{date}.json")
            if not data:
                continue

            if src == "suggest" and isinstance(data, dict):
                # {niche_key: {seed: {platform: [strings]}}}
                for niche_json_key, seeds in data.items():
                    niche = _JSON_TO_NICHE.get(niche_json_key)
                    if not niche or not isinstance(seeds, dict):
                        continue
                    for seed, platforms in seeds.items():
                        if not isinstance(platforms, dict):
                            continue
                        for plat, suggestions in platforms.items():
                            if not isinstance(suggestions, list):
                                continue
                            for s in suggestions:
                                if isinstance(s, str) and len(s) >= 6:
                                    agg[niche].append({
                                        "title": s, "niche": niche,
                                        "source": f"suggest_{plat}", "score": 0.7,
                                    })
            elif isinstance(data, dict):
                # Standard {niche_json_key: [items]}
                for niche_json_key, items in data.items():
                    niche = _JSON_TO_NICHE.get(niche_json_key)
                    if not niche or not isinstance(items, list):
                        continue
                    for item in items:
                        if not isinstance(item, dict):
                            continue
                        item.setdefault("source", src)
                        item["niche"] = niche
                        if "score" not in item:
                            pts = item.get("points", 0) + item.get("reactions", 0)
                            item["score"] = min(pts / 50.0, 1.0) if pts else 0.6
                        agg[niche].append(item)

    return agg


# ── Deduplication + novelty ───────────────────────────────────────────────────

def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _deduplicate(items: list[dict], threshold: float = 0.80) -> list[dict]:
    seen, out = [], []
    for item in items:
        t = item.get("title", "")
        if not any(_similarity(t, s) >= threshold for s in seen):
            out.append(item)
            seen.append(t)
    return out


def _apply_novelty_penalty(items: list[dict], archive_titles: list[str]) -> list[dict]:
    for item in items:
        t       = item.get("title", "")
        max_sim = max((_similarity(t, a) for a in archive_titles), default=0)
        base    = item.get("score", 0.5)
        item["adj_score"] = base * 0.4 if max_sim > 0.6 else base
    return items


# ── Deterministic project reel + raw takes ────────────────────────────────────

def weekly_project_reel(niche: str, week_num: int, projects_data: dict) -> dict | None:
    """Return the project-reel brief dict for this niche × week.

    Rotates angle_rotation deterministically: angle_rotation[(week_num-1) % len(angles)].
    Returns None if no matching project exists (e.g. poetry).
    """
    projects = projects_data.get("projects", [])
    candidates = [
        p for p in projects
        if niche in p.get("niches", [p.get("hashtag_niche", "")])
        and p.get("cadence", {}).get("frequency") == "weekly"
    ]
    if not candidates:
        return None
    proj   = candidates[0]
    angles = proj.get("cadence", {}).get("angle_rotation", [])
    if not angles:
        return None
    angle = angles[(week_num - 1) % len(angles)]
    return {
        "key":       proj["key"],
        "name":      proj["name"],
        "angle":     angle,
        "dm_kw":     proj.get("dm_keyword", ""),
        "pitch":     proj.get("pitch", ""),
        "guardrail": proj.get("honesty_guardrail", ""),
        "deliverable": proj.get("deliverable", ""),
    }


def weekly_raw_take_batch(week_num: int, questions_data: dict, n: int = 4) -> list[dict]:
    """Return n Life raw-take questions for this week.

    Rotation: batch_idx = (week_num - 1) % floor(len / n). ~7 weeks before repeat.
    """
    questions = questions_data.get("questions", [])
    if not questions:
        return []
    num_batches = max(1, len(questions) // n)
    start       = ((week_num - 1) % num_batches) * n
    return questions[start : start + n]


# ── Claude Haiku idea scoring ─────────────────────────────────────────────────

_SCORE_SYSTEM = """\
You are a content strategist for Tarun Gupta (@mistakenlyhuman / @breathofdatascience).
Niche: {niche_label}.
Voice: Analytical but warm, personal examples, no jargon without context.
Banned words: "In conclusion", "Dive into", "Leverage", "Game-changer", "Synergy".

Return ONLY a valid JSON array (no markdown fences). Each object must have:
  "idea"   : string — specific, concrete topic angle (not generic)
  "format" : string — one of "Blog + Reel", "Reel only", "Blog only", "Carousel"
  "hook"   : string — 1 punchy hook line (<12 words), strong opening claim
  "score"  : integer 1–10 (10 = highest virality: search demand + emotional pull + hook potential)
  "why"    : string — ≤12 words explaining the score

Return {top_n} best ideas, sorted descending by score.
"""

_SCORE_PROMPT = """\
Recent titles (avoid these angles — covered last 90 days):
{recent}

Keyword signals this week (Google/YouTube autocomplete + Reddit + external):
{keywords}

Master brief excerpt (voice, what's working):
{brief}

Return {top_n} scored ideas for the {niche_label} niche.
"""


def _score_with_claude(
    niche: str,
    items: list[dict],
    recent_titles: list[str],
    master_brief: str,
    hook_patterns: str,
    client: anthropic.Anthropic,
    top_n: int = 5,
) -> list[dict]:
    label   = _NICHE_LABELS.get(niche, niche)
    # Sample the highest-adj_score items first, cap at 100 for token budget
    top_items = sorted(items, key=lambda x: x.get("adj_score", 0), reverse=True)[:100]
    kw_lines  = "\n".join(f"- {it['title']}" for it in top_items)

    system = _SCORE_SYSTEM.format(niche_label=label, top_n=top_n)
    prompt = _SCORE_PROMPT.format(
        recent="\n".join(f"- {t}" for t in recent_titles) if recent_titles else "(none)",
        keywords=kw_lines,
        brief=(master_brief or "")[:2000],
        niche_label=label,
        top_n=top_n,
    )
    try:
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1500,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.rsplit("```", 1)[0]
        return sorted(json.loads(raw), key=lambda x: -x.get("score", 0))
    except Exception as e:
        console.print(f"  [warn]{niche} scoring failed: {e}[/warn]")
        return []


# ── Markdown output ───────────────────────────────────────────────────────────

def _render_project_reel(reel: dict) -> str:
    cmd = f"python3 scripts/repurpose_blog.py --input <blog.md> --project {reel['key']}"
    hooks = [
        f"Here's {reel['angle'].lower()} — for free.",
        f"I built {reel['name'].split(':')[0].strip()} and {reel['angle'].lower()}.",
    ]
    hook_lines = "\n".join(f"  - {h}" for h in hooks)
    return (
        f"### 🔧 Tool Reel (mandatory — 1/week · {reel['key']})\n"
        f"> `{cmd}`\n"
        f"> DM keyword: **{reel['dm_kw']}** · _{reel['guardrail']}_\n"
        f"\n"
        f"**Project:** {reel['name']}\n"
        f"**This week's angle:** {reel['angle']}\n"
        f"**Hook options (record 5×, keep winner):**\n"
        f"{hook_lines}\n"
        f"**5-beat:** Hook 0–3s → Problem 3–8s → Reveal+proof 8–28s → Payoff 28–35s → "
        f"CTA 'Comment **{reel['dm_kw']}**' 35–45s\n"
    )


def _render_raw_takes(questions: list[dict]) -> str:
    lines = [
        "### 🎤 Raw Take Batch (4 this week — Hinglish, batch-record in one sitting)",
        "> `docs/raw-take-format.md` · Format: 'Someone asked me — <Q>' → raw opinion → landing line",
        "",
    ]
    for i, q in enumerate(questions, 1):
        lines.append(f"{i}. **Q:** _{q['q']}_ `[{q.get('theme','')}]`")
        lines.append(f"   Hook: \"Someone asked me — {q['q']}\"")
        lines.append("")
    return "\n".join(lines)


def _render_scored_table(ideas: list[dict]) -> str:
    if not ideas:
        return "_No ideas scored — check that idea input files exist for this week._\n"
    rows = [
        "| Score | Idea | Hook | Format |",
        "|-------|------|------|--------|",
    ]
    for idea in ideas:
        score = idea.get("score", "?")
        title = idea.get("idea", "").replace("|", "\\|")
        hook  = idea.get("hook", "").replace("|", "\\|")
        fmt   = idea.get("format", "").replace("|", "\\|")
        rows.append(f"| {score}/10 | {title} | {hook} | {fmt} |")
    return "\n".join(rows) + "\n"


def render_weekly_ideas(
    week: str,
    project_reels: dict[str, dict | None],
    raw_takes: list[dict],
    scored: dict[str, list[dict]],
) -> str:
    today = datetime.date.today().isoformat()
    lines = [
        f"# Weekly Content Ideas — {week}",
        f"_Generated: {today} · Regenerate: `python3 scripts/idea_scorer.py --force`_",
        "",
        "---",
        "",
    ]
    for niche in ("ds", "life", "poetry"):
        label = _NICHE_LABELS[niche]
        lines += [f"## {label}", ""]

        reel = project_reels.get(niche)
        if reel:
            lines += [_render_project_reel(reel), ""]

        if niche == "life" and raw_takes:
            lines += [_render_raw_takes(raw_takes), ""]

        lines += ["### 📝 Blog + Reel Ideas (virality-scored)", ""]
        lines += [_render_scored_table(scored.get(niche, [])), ""]
        lines += ["---", ""]

    return "\n".join(lines)


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Generate weekly_ideas.md with scored ideas + project reels + raw takes."
    )
    ap.add_argument("--week",    default=None,   help="ISO week e.g. W26 or 2026-W26 (default: current)")
    ap.add_argument("--top",     type=int, default=5, help="Scored ideas per niche (default 5)")
    ap.add_argument("--force",   action="store_true", help="Overwrite existing weekly_ideas.md")
    ap.add_argument("--dry-run", action="store_true", help="Print to stdout; don't write file")
    args = ap.parse_args()

    # Resolve week string
    today = datetime.date.today().isoformat()
    if args.week:
        w = args.week.strip()
        if not w.startswith("20"):
            w = f"{today[:4]}-{w}" if w.startswith("W") else f"20{w}"
        week = w
    else:
        week = get_iso_week(today)

    week_num = int(week.split("-W")[1])
    out_path = IDEAS / "weekly_ideas.md"

    if out_path.exists() and not args.force and not args.dry_run:
        console.print(f"[dim]weekly_ideas.md exists — use --force to regenerate[/dim]")
        console.print(f"  → {out_path.relative_to(REPO)}")
        return

    console.rule(f"[bold]Idea machine — {week}[/bold]")

    # ── KB files ──────────────────────────────────────────────────────────────
    projects_data = _load_json(KB / "projects.json", required=True)
    raw_qs_data   = _load_json(KB / "raw_take_questions.json", required=True)
    master_brief  = (KB / "master_brief.md").read_text(encoding="utf-8") if (KB / "master_brief.md").exists() else ""
    hook_patterns = (KB / "twitter_hook_patterns.json").read_text(encoding="utf-8") if (KB / "twitter_hook_patterns.json").exists() else ""

    # ── Deterministic ─────────────────────────────────────────────────────────
    console.print("\n[bold]1/3 Project reels (deterministic)[/bold]")
    project_reels: dict[str, dict | None] = {}
    for niche in ("ds", "life", "poetry"):
        reel = weekly_project_reel(niche, week_num, projects_data)
        project_reels[niche] = reel
        if reel:
            console.print(f"  {niche}: {reel['name']} → \"{reel['angle']}\"")
        else:
            console.print(f"  {niche}: (no project this week)")

    console.print("\n[bold]2/3 Raw take batch (deterministic)[/bold]")
    raw_takes = weekly_raw_take_batch(week_num, raw_qs_data)
    for i, q in enumerate(raw_takes, 1):
        text = q["q"][:65] + "…" if len(q["q"]) > 65 else q["q"]
        console.print(f"  {i}. {text}")

    # ── Idea inputs ───────────────────────────────────────────────────────────
    console.print("\n[bold]3/3 Scoring ideas with Claude Haiku[/bold]")
    week_items = _load_week_ideas(week)
    for niche, items in week_items.items():
        console.print(f"  {niche}: {len(items)} raw signals loaded")

    # Recent tracker titles (repeat-angle filter)
    recent_by_niche: dict[str, list[str]] = {n: [] for n in ("ds", "life", "poetry")}
    try:
        from lib.tracker import read_recent_titles
        for niche in ("ds", "life", "poetry"):
            recent_by_niche[niche] = read_recent_titles(niche, days=90)
    except Exception as e:
        console.print(f"  [dim]Tracker unavailable: {e}[/dim]")

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY_FREE"))
    scored: dict[str, list[dict]] = {}

    for niche in ("ds", "life", "poetry"):
        items = week_items.get(niche, [])
        # Filter off-topic
        items = [it for it in items if _passes_blocklist(it)]
        # Deduplicate
        items = _deduplicate(items)
        # Novelty penalty vs recent tracker
        items = _apply_novelty_penalty(items, recent_by_niche.get(niche, []))

        if not items:
            console.print(f"  {niche}: no signals after filtering — skipping Claude call")
            scored[niche] = []
            continue

        console.print(f"  {niche}: {len(items)} items → scoring…", end=" ", flush=True)
        ideas = _score_with_claude(
            niche, items, recent_by_niche.get(niche, []),
            master_brief, hook_patterns, client, top_n=args.top,
        )
        scored[niche] = ideas
        console.print(f"{len(ideas)} ideas returned")

    # ── Render ────────────────────────────────────────────────────────────────
    output = render_weekly_ideas(week, project_reels, raw_takes, scored)

    if args.dry_run:
        print(output)
    else:
        IDEAS.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        console.print(f"\n[success]✓ weekly_ideas.md → {out_path.relative_to(REPO)}[/success]")

    console.print("\n[dim]Next: `produce_blog.py --topic <idea>` · record reel from brief · run `run_blog_pipeline.py`[/dim]")


if __name__ == "__main__":
    main()
