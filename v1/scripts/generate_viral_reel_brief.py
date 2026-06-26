#!/usr/bin/env python3
"""Generate standalone viral reel briefs — for reels with no existing blog/recording.

Unlike generate_ig_reel_brief.py (which clips from an existing recording),
this script produces a **recording plan**: what to say, what to show, beat by beat.

Two entry points:
  --idea  "Why polars is faster than pandas"  → brief for one specific idea
  --from-weekly                                → briefs for this week's tool reels
                                                 (reads data/ideas/weekly_ideas.md)

Output: content/reels/{week}/{slug}_viral_reel_brief.md

Usage:
  python3 scripts/generate_viral_reel_brief.py \\
      --idea "5 Python one-liners I use daily" --niche ds --week 2026-W26

  python3 scripts/generate_viral_reel_brief.py \\
      --from-weekly --week 2026-W26            # tool reels (DS + Life)

  python3 scripts/generate_viral_reel_brief.py \\
      --idea "Why I stopped journaling and what replaced it" --niche life --week 2026-W26 \\
      --project free_tool_life
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import anthropic
from dotenv import load_dotenv
from rich.console import Console

from lib.schedule_calc import get_iso_week  # noqa: E402
from lib.virality import virality_block     # noqa: E402

load_dotenv(REPO / ".env")
console = Console()

# ── Niche routing ──────────────────────────────────────────────────────────────

NICHE_ACCOUNT = {
    "ds":      "@breathofdatascience",
    "life":    "@mistakenlyhuman",
    "poetry":  "@mistakenlyhuman",
}
NICHE_LABEL = {
    "ds":     "Data Science / Python / Tech",
    "life":   "Life & Self-Development",
    "poetry": "Poetry / Quotes",
}

# ── Prompt ─────────────────────────────────────────────────────────────────────

_SYSTEM = """\
You are a short-form video strategist for Tarun Gupta, a 10-year data scientist and content creator.
Voice: Analytical but warm. Personal examples over generic advice. No jargon without context.
Banned words: "In conclusion", "Dive into", "Leverage", "Game-changer", "Synergy".
The reel is 35–45 seconds. It follows the 5-beat formula exactly.
Return ONLY valid JSON — no markdown fences, no prose.
"""

_PROMPT = """\
## Virality directives (apply to every beat, hook, and caption)

{virality}

---

## Viral reel formula — 5-beat structure (non-negotiable)

Beat 1 — HOOK (0–3s): Bold claim or specific result. Face + big text overlay. Hard cut. No "hey guys."
Beat 2 — PROBLEM (3–8s): Name the pain the viewer feels RIGHT NOW. Visceral and specific.
Beat 3 — REVEAL + PROOF (8–28s): What it is + SHOW it actually working. Screen-record real output. Proof beats claims.
Beat 4 — PAYOFF (28–35s): Why it matters / the result. Back to face, confident close.
Beat 5 — CTA (35–45s): ONE action. "Comment '{dm_kw}' and I'll DM you the link."

Hook rules:
- 5 hook variants. Rank them by scroll-stop power (1 = strongest).
- Strong hook patterns: Bold Declaration / Data+Mechanism / Contrarian Mirror / Social Proof Inversion.
- Every hook needs: a concrete number OR a specific result OR a named before/after.
- Bad: "This Python mistake will ruin your code." Good: "Python silently concatenated my strings — no error, wrong answer — I trusted it for a week."

Caption formula: {caption_formula}

Honesty guardrail: {guardrail}
Project key: {project_key}
DM keyword: {dm_kw}

---

## Task

Idea: {idea}
Niche: {niche_label}
Account: {account}
Type: {reel_type}

Generate a full recording brief as JSON with this schema:
{{
  "title": "string — working title for the reel (used in filename)",
  "dm_keyword": "WORD",
  "hooks": [
    {{"rank": 1, "text": "string", "pattern": "Bold Declaration | Data+Mechanism | Contrarian Mirror | Social Proof Inversion", "why": "≤15 words"}},
    {{"rank": 2, "text": "string", "pattern": "...", "why": "..."}},
    {{"rank": 3, "text": "string", "pattern": "...", "why": "..."}},
    {{"rank": 4, "text": "string", "pattern": "...", "why": "..."}},
    {{"rank": 5, "text": "string", "pattern": "...", "why": "..."}}
  ],
  "beats": [
    {{"beat": 1, "name": "Hook", "time": "0–3s", "script": "exactly what to say", "visual": "what to show/do on screen"}},
    {{"beat": 2, "name": "Problem", "time": "3–8s", "script": "...", "visual": "..."}},
    {{"beat": 3, "name": "Reveal+Proof", "time": "8–28s", "script": "...", "visual": "screen-record suggestion or B-roll"}},
    {{"beat": 4, "name": "Payoff", "time": "28–35s", "script": "...", "visual": "..."}},
    {{"beat": 5, "name": "CTA", "time": "35–45s", "script": "Comment [KEYWORD] and I'll DM you [what] 👇", "visual": "point-down, keyword on screen"}}
  ],
  "caption": "string — full Instagram caption following the caption formula above",
  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "b_roll_ideas": ["string — 3–5 specific B-roll ideas: screen recordings, demos, before/after"],
  "posting_note": "string — one-line production or timing tip for this specific idea"
}}
"""

# ── Helpers ────────────────────────────────────────────────────────────────────

def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _slugify(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", text.lower())
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s[:60]


def _load_project(project_key: str | None) -> dict:
    if not project_key:
        return {}
    pjson = _load_json(REPO / "data" / "kb" / "projects.json") or {}
    for p in pjson.get("projects", []):
        if p.get("key") == project_key:
            return p
    return {}


def _caption_formula_hint(niche: str) -> str:
    """One-line formula hint for the caption — full details are in virality_block."""
    if niche == "ds":
        return 'Line 1: Comment "[KEYWORD] and I\'ll send you [deliverable] 👆" → numbered list of full value → hashtags.'
    if niche == "life":
        return "Single precise mechanism insight (Mode C) OR 5-sentence essay+vulnerability for heavy topics. Flat close, no crescendo."
    return "Full poem verbatim, OR one devastating line + emoji. NEVER explain the poem. Permission close."


# ── Claude call ────────────────────────────────────────────────────────────────

def generate_brief(
    idea: str,
    niche: str,
    week: str,
    project_key: str | None = None,
    reel_type: str = "idea",
) -> dict | None:
    """Call Claude Sonnet and return the parsed brief dict, or None on failure."""
    proj    = _load_project(project_key)
    account = NICHE_ACCOUNT.get(niche, "@mistakenlyhuman")
    label   = NICHE_LABEL.get(niche, niche)
    dm_kw   = proj.get("dm_keyword", "LINK")
    guardrail = proj.get("honesty_guardrail", "State what it actually does — no overclaiming.")

    virality = virality_block("instagram_caption", niche, project_key)

    prompt = _PROMPT.format(
        virality=virality or "(no virality block — follow formula above)",
        dm_kw=dm_kw,
        caption_formula=_caption_formula_hint(niche),
        guardrail=guardrail,
        project_key=project_key or "(none)",
        idea=idea,
        niche_label=label,
        account=account,
        reel_type=reel_type,
    )

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY_FREE"))
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3000,
            system=_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.rsplit("```", 1)[0]
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            console.print(f"  [warn]No JSON in Claude output[/warn]")
            return None
        return json.loads(m.group(0))
    except Exception as e:
        console.print(f"  [warn]Claude error: {e}[/warn]")
        return None


# ── Markdown renderer ──────────────────────────────────────────────────────────

def brief_to_markdown(brief: dict, idea: str, niche: str, week: str,
                      project_key: str | None = None) -> str:
    account  = NICHE_ACCOUNT.get(niche, "@mistakenlyhuman")
    proj     = _load_project(project_key)
    guardrail = proj.get("honesty_guardrail", "State what it actually does — no overclaiming.")
    utm_link  = proj.get("dm_link_template", "(set in projects.json)")

    hooks_md = "\n\n".join(
        f"**{h['rank']}. {h['text']}**\n"
        f"> Pattern: _{h.get('pattern','')}_  ·  {h.get('why','')}"
        for h in brief.get("hooks", [])
    )

    beats_rows = "\n".join(
        f"| {b['beat']}. {b['name']} | `{b['time']}` | {b['script']} | {b['visual']} |"
        for b in brief.get("beats", [])
    )

    broll = "\n".join(f"- {b}" for b in brief.get("b_roll_ideas", []))
    hashtags = " ".join(brief.get("hashtags", []))

    checklist_honesty = f"- [ ] Honesty guardrail: _{guardrail}_"
    checklist_utm     = f"- [ ] UTM link in DM/description: `{utm_link}`"

    return f"""# Viral Reel Brief — {idea}

**Week:** {week}
**Niche:** {NICHE_LABEL.get(niche, niche)}
**Account:** {account}
**Project:** {project_key or "(standalone idea)"}
**Target length:** 35–45s · trim to 30s by cutting weakest sub-feature in beat 3

---

## Hooks — record ALL 5, pick winner after review

{hooks_md}

---

## 5-beat shot plan

| Beat | Time | Script (what to say) | Visual (what to show) |
|------|------|----------------------|-----------------------|
{beats_rows}

---

## Instagram caption

```
{brief.get("caption", "")}

{hashtags}
```

---

## DM keyword

`{brief.get("dm_keyword", "LINK")}` — arm in SuperProfile / CreatorFlow before posting.

---

## B-roll / proof ideas

{broll}

---

## Recording checklist

- [ ] Hook recorded 5× — watch back cold and pick the one that stops YOU
- [ ] Captions burned in (word-by-word, high contrast, big font)
- [ ] Hard cut at 0s — no slow intro
- [ ] No single clip longer than 4 seconds
- [ ] Trending audio low under voice
- [ ] Proof B-roll captured: 3–5s clips, zoomed for mobile
{checklist_honesty}
{checklist_utm}
- [ ] Derivatives run after posting: `python3 scripts/repurpose_blog.py --input <blog> --project {project_key or 'none'}`

---

## Posting note

{brief.get("posting_note", "")}

---
_Generated by generate_viral_reel_brief.py — edit hooks/beats to match your voice before recording._
"""


# ── Weekly entries from weekly_ideas.md ───────────────────────────────────────

# Section header fragments — must match idea_scorer.py _NICHE_LABELS exactly
_NICHE_HEADER_FRAG: dict[str, str] = {
    "ds":      "DS —",
    "life":    "Life —",
    "poetry":  "Poetry",   # "Poetry / Quotes" — no em dash
}


def _niche_section(weekly_md: str, niche_short: str) -> str | None:
    """Return the niche section of weekly_ideas.md, or None if not found."""
    frag = _NICHE_HEADER_FRAG.get(niche_short, niche_short.capitalize())
    pat = re.compile(
        rf"## {re.escape(frag)}.*?(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pat.search(weekly_md)
    return m.group(0) if m else None


def _parse_tool_reels_from_weekly(weekly_md: str) -> list[dict]:
    """Extract tool reel entries from weekly_ideas.md.

    Only DS and Life have tool reels (project reels). Poetry does not.
    Returns list of {project_key, angle, niche} dicts.
    """
    entries = []
    for niche_short in ("ds", "life"):
        section = _niche_section(weekly_md, niche_short)
        if not section:
            continue
        proj_m = re.search(r"--project\s+(\w+)", section)
        if not proj_m:
            continue
        project_key = proj_m.group(1)
        angle_m = re.search(r"\*\*This week.*?angle:\*\*\s*(.+?)$", section, re.MULTILINE)
        angle = angle_m.group(1).strip() if angle_m else ""
        entries.append({"project_key": project_key, "angle": angle, "niche": niche_short})
    return entries


def _parse_scored_ideas_from_weekly(
    weekly_md: str, niche_short: str, top_n: int = 1
) -> list[dict]:
    """Extract top scored reel ideas for a niche from weekly_ideas.md.

    Parses the '### 📝 Blog + Reel Ideas' table and returns up to top_n rows
    where Format contains 'Reel' (covers 'Reel only' and 'Blog + Reel').
    Returns list of {idea, hook, score} dicts, highest score first.
    Works for all three niches — DS, Life, and Poetry.
    """
    if top_n <= 0:
        return []
    section = _niche_section(weekly_md, niche_short)
    if not section:
        return []

    row_re = re.compile(
        r"^\|\s*(\d+)/10\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|",
        re.MULTILINE,
    )
    results = []
    for m in row_re.finditer(section):
        score_str, idea, hook, fmt = m.groups()
        if "Reel" not in fmt:
            continue
        results.append({
            "idea":   idea.strip(),
            "hook":   hook.strip(),
            "score":  int(score_str),
            "format": fmt.strip(),
        })
        if len(results) >= top_n:
            break
    return results


# ── Main ───────────────────────────────────────────────────────────────────────

def _write_brief(idea: str, niche: str, week: str,
                 project_key: str | None, reel_type: str, force: bool) -> bool:
    slug = f"{_slugify(idea)}_reel_brief"
    out_dir  = REPO / "content" / "reels" / week
    out_path = out_dir / f"{slug}.md"

    if out_path.exists() and not force:
        console.print(f"  [dim]skip (exists) — {out_path.relative_to(REPO)}[/dim]")
        return True

    console.print(f"  idea: {idea[:70]}")
    console.print(f"  niche: {niche} | project: {project_key or 'none'} | type: {reel_type}")
    console.print("  calling Claude Sonnet…", end=" ", flush=True)

    brief = generate_brief(idea, niche, week, project_key, reel_type)
    if not brief:
        return False

    console.print("done")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(brief_to_markdown(brief, idea, niche, week, project_key), encoding="utf-8")
    console.print(f"  [success]✓ {out_path.relative_to(REPO)}[/success]")
    return True


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Generate a recording brief for a standalone viral reel."
    )
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--idea", help="Reel idea text (one brief)")
    src.add_argument("--from-weekly", action="store_true",
                     help="Generate briefs for this week's tool reels (DS/Life) AND top "
                          "scored reel idea per niche (DS, Life, Poetry) from weekly_ideas.md")
    ap.add_argument("--niche", choices=["ds", "life", "poetry"],
                    help="Required with --idea")
    ap.add_argument("--week", default=None,
                    help="ISO week e.g. W26 or 2026-W26 (default: current)")
    ap.add_argument("--project", default=None,
                    help="Build-in-public project key (data/kb/projects.json)")
    ap.add_argument("--type", dest="reel_type", default="idea",
                    choices=["idea", "tool", "raw_take"],
                    help="Reel type — affects brief emphasis (default: idea)")
    ap.add_argument("--top-ideas", type=int, default=1, metavar="N",
                    help="Number of top scored ideas to brief per niche (default: 1)")
    ap.add_argument("--force", action="store_true",
                    help="Overwrite existing brief")
    args = ap.parse_args()

    # Resolve week
    today = datetime.date.today().isoformat()
    if args.week:
        w = args.week.strip()
        if not w.startswith("20"):
            w = f"{today[:4]}-{w}" if w.startswith("W") else f"20{w}"
        week = w
    else:
        week = get_iso_week(today)

    console.rule(f"[bold]Viral reel brief — {week}[/bold]")

    if args.idea:
        if not args.niche:
            ap.error("--niche is required with --idea")
        ok = _write_brief(args.idea, args.niche, week, args.project, args.reel_type, args.force)
        sys.exit(0 if ok else 1)

    # --from-weekly
    weekly_md_path = REPO / "data" / "ideas" / "weekly_ideas.md"
    if not weekly_md_path.exists():
        console.print(f"[error]weekly_ideas.md not found — run idea_scorer.py first[/error]")
        sys.exit(1)

    weekly_md = weekly_md_path.read_text(encoding="utf-8")

    # Phase 1: tool reels — DS and Life mandatory weekly project reels
    tool_reels = _parse_tool_reels_from_weekly(weekly_md)
    if tool_reels:
        console.print(f"Found {len(tool_reels)} tool reel(s) in weekly_ideas.md")
    else:
        console.print("[warn]No tool reels found in weekly_ideas.md (DS/Life projects may be missing)[/warn]")

    ok_count = 0
    total = 0
    for entry in tool_reels:
        console.print(f"\n→ {entry['niche']} tool reel [{entry['project_key']}]")
        idea = entry["angle"] or f"Build-in-public: {entry['project_key']}"
        ok = _write_brief(
            idea=idea,
            niche=entry["niche"],
            week=week,
            project_key=entry["project_key"],
            reel_type="tool",
            force=args.force,
        )
        total += 1
        if ok:
            ok_count += 1

    # Phase 2: top scored reel ideas — all three niches (DS, Life, Poetry)
    top_n = args.top_ideas
    console.print(f"\nScoring top {top_n} reel idea(s) per niche from weekly_ideas.md")
    for niche_short in ("ds", "life", "poetry"):
        scored = _parse_scored_ideas_from_weekly(weekly_md, niche_short, top_n=top_n)
        if not scored:
            console.print(f"  [dim]{niche_short}: no reel-format ideas found in weekly_ideas.md[/dim]")
            continue
        for item in scored:
            console.print(f"\n→ {niche_short} idea [{item['score']}/10] {item['idea'][:60]}")
            ok = _write_brief(
                idea=item["idea"],
                niche=niche_short,
                week=week,
                project_key=None,
                reel_type="idea",
                force=args.force,
            )
            total += 1
            if ok:
                ok_count += 1

    console.print(f"\n[success]✓ {ok_count}/{total} viral reel briefs generated → content/reels/{week}/[/success]")


if __name__ == "__main__":
    main()
