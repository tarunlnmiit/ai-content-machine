#!/usr/bin/env python3
"""Weekly raw-session prompt pack — questions the creator answers on camera.

Merges, in priority order:
  data/ideas/thought_inbox.md      — raw thoughts/audience questions (highest priority)
  (provocation)                    — systems-thinking self-debug questions, Claude-generated
  data/kb/raw_take_questions.json  — Life question bank (rotated by ISO week,
                                     via idea_scorer.weekly_raw_take_batch)
  data/ideas/weekly_ideas.md       — scored ideas → secondary-niche questions
  data/analytics/weekly_insights.md — winner themes (bias, optional)

Outputs:
  content/sessions/{week}/prompt_pack.json  — slicer ground truth (spoken markers)
  content/sessions/{week}/teleprompter.html — one question per slide, arrow keys

Recording protocol (why this file is the slicer's ground truth):
  The creator READS EACH QUESTION ALOUD VERBATIM after ~3s of silence, then
  answers. slice_raw_session.py fuzzy-matches the spoken question against
  "text" below to cut the session into per-question clips.

Usage:
  python3 scripts/generate_prompt_pack.py                       # current week
  python3 scripts/generate_prompt_pack.py --week 2026-W29
  python3 scripts/generate_prompt_pack.py --theme career,self-doubt
  python3 scripts/generate_prompt_pack.py --n-life 4 --n-poetry 2 --n-ds 2
"""

from __future__ import annotations

import argparse
import datetime
import difflib
import html
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.claude_cli import call_claude          # noqa: E402
from lib.niche_config import model_for          # noqa: E402
from lib.schedule_calc import get_iso_week      # noqa: E402

QUESTIONS_JSON = REPO / "data" / "kb" / "raw_take_questions.json"
IDEAS_MD       = REPO / "data" / "ideas" / "weekly_ideas.md"
INSIGHTS_MD    = REPO / "data" / "analytics" / "weekly_insights.md"
SESSIONS_DIR   = REPO / "content" / "sessions"
INBOX_MD       = REPO / "data" / "ideas" / "thought_inbox.md"

THESIS = (
    "I debug life like I debug systems — 10-year data scientist, "
    "systems thinking applied to life and career."
)


def _extract_json_array(raw: str) -> list:
    """Parse a JSON array from a Claude response, tolerating fences and prose."""
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("["), raw.rfind("]")
        if start == -1 or end <= start:
            raise ValueError("no JSON array in response")
        parsed = json.loads(raw[start : end + 1])
    if not isinstance(parsed, list):
        raise ValueError("response JSON is not a list")
    return parsed


# ── Life questions (bank rotation) ────────────────────────────────────────────

def life_questions(week_num: int, n: int, themes: list[str] | None) -> list[dict]:
    data = json.loads(QUESTIONS_JSON.read_text(encoding="utf-8"))
    pool = data.get("questions", [])
    if themes:
        pool = [q for q in pool if q.get("theme") in themes] or pool
    if not pool:
        return []
    num_batches = max(1, len(pool) // n)
    start = ((week_num - 1) % num_batches) * n
    batch = pool[start : start + n]
    return [
        {
            "niche": "life",
            "text": q.get("q_en") or q["q"],
            "theme": q.get("theme", ""),
            "source": "rotation",
        }
        for q in batch
    ]


# ── Secondary-niche questions from scored ideas ───────────────────────────────

def _ideas_section(niche_header: str) -> str:
    if not IDEAS_MD.exists():
        return ""
    text = IDEAS_MD.read_text(encoding="utf-8")
    m = re.search(rf"^## {re.escape(niche_header)}.*?(?=^## |\Z)", text, re.M | re.S)
    return m.group(0) if m else ""

def _winner_context() -> str:
    if not INSIGHTS_MD.exists():
        return ""
    return INSIGHTS_MD.read_text(encoding="utf-8")[:1500]

def niche_questions(niche: str, niche_header: str, n: int) -> list[dict]:
    """Turn this week's scored ideas into n spoken-question prompts via Haiku."""
    if n <= 0:
        return []
    section = _ideas_section(niche_header)
    prompt = f"""From the content ideas below, write exactly {n} spoken interview questions \
for a creator to answer raw on camera (no script). Each question must be one sentence, \
conversational English, under 18 words, phrased as something a viewer would ask \
("How do you...", "Why did you...", "What happens when..."). No numbering commentary.

Ideas for this week ({niche} niche):
{section or '(no scored ideas this week — invent evergreen questions for this niche)'}

Recent winner context (bias toward what worked, if any):
{_winner_context() or '(none)'}

Return ONLY a JSON array of {n} strings."""
    try:
        raw = call_claude(prompt, cache=True, timeout=90, model=model_for("metadata"))
        texts = _extract_json_array(raw)
    except Exception as e:
        print(f"  ⚠ {niche} question generation failed ({e}) — skipping", file=sys.stderr)
        return []
    return [
        {"niche": niche, "text": str(t).strip(), "theme": "scored_idea", "source": "generated"}
        for t in texts[:n]
    ]


# ── Thought inbox (highest priority) ──────────────────────────────────────────

def _section_lines(text: str, header: str) -> list[str]:
    """Bullet lines under `## {header}`, ignoring blanks/comments."""
    m = re.search(rf"^## {header}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return []
    lines = []
    for raw in m.group(1).splitlines():
        line = raw.strip()
        if not line or line.startswith("<!--"):
            continue
        if line.startswith("-"):
            line = line[1:].strip()
        if line:
            lines.append(line)
    return lines


def inbox_questions(inbox_path: Path) -> tuple[list[dict], list[str], list[str]]:
    """Convert thought-inbox bullets into spoken-question hooks via one Claude call.

    Returns (questions, used_thoughts, used_audience) so the caller can move
    consumed lines into `## consumed` after a successful pack write.
    """
    if not inbox_path.exists():
        return [], [], []
    text = inbox_path.read_text(encoding="utf-8")
    thoughts = _section_lines(text, "thoughts")
    audience = _section_lines(text, "audience")
    entries = thoughts + audience
    if not entries:
        return [], [], []
    numbered = "\n".join(f"{i + 1}. {e}" for i, e in enumerate(entries))
    prompt = f"""Convert each raw thought below into ONE natural spoken-question hook \
(English, under 90 characters) phrased as something a viewer or fan would ask Tarun \
Gupta on camera. Keep the essence of each entry. Return exactly {len(entries)} items, \
SAME ORDER as the input list.

Raw thoughts:
{numbered}

Return ONLY a JSON array of {len(entries)} objects: {{"question": "...", "niche": "life"|"ds"}}"""
    try:
        raw = call_claude(prompt, cache=True, timeout=90, model=model_for("reel_hook"))
        parsed = _extract_json_array(raw)
        assert len(parsed) == len(entries)
    except Exception as e:
        print(f"  ⚠ inbox question generation failed ({e}) — skipping", file=sys.stderr)
        return [], [], []
    questions = []
    for i, p in enumerate(parsed):
        kind = "inbox" if i < len(thoughts) else "audience"
        questions.append({
            "niche": p.get("niche", "life"),
            "text": str(p["question"]).strip(),
            "theme": kind,
            "source": kind,
        })
    return questions, thoughts, audience


def provocation_questions() -> list[dict]:
    """2-3 systems-thinking self-debug questions, seeded by recent winner context."""
    context = ""
    if INSIGHTS_MD.exists():
        context = "\n".join(INSIGHTS_MD.read_text(encoding="utf-8").splitlines()[:40])
    prompt = f"""Tarun Gupta's content thesis: "{THESIS}"

Write 2-3 thought-provoking spoken-question hooks (English, under 90 characters each, \
phrased "How do you...", "Why does...", "What happens when...") that a viewer would ask \
him on camera, grounded in this thesis and, where relevant, the recent context below.

Recent winner context:
{context or '(none)'}

Return ONLY a JSON array of 2-3 objects: {{"question": "...", "niche": "life"|"ds"}}"""
    try:
        raw = call_claude(prompt, cache=True, timeout=90, model=model_for("reel_hook"))
        parsed = _extract_json_array(raw)
    except Exception as e:
        print(f"  ⚠ provocation question generation failed ({e}) — skipping", file=sys.stderr)
        return []
    return [
        {"niche": p.get("niche", "life"), "text": str(p["question"]).strip(),
         "theme": "provocation", "source": "provocation"}
        for p in parsed if p.get("question")
    ]


def _dedupe(questions: list[dict]) -> list[dict]:
    """Drop near-identical questions (normalized SequenceMatcher ratio > 0.85)."""
    kept_norms: list[str] = []
    out: list[dict] = []
    for q in questions:
        norm = re.sub(r"\s+", " ", q["text"].strip().lower())
        if any(difflib.SequenceMatcher(None, norm, k).ratio() > 0.85 for k in kept_norms):
            continue
        kept_norms.append(norm)
        out.append(q)
    return out


def consume_inbox(inbox_path: Path, week: str, thoughts: list[str], audience: list[str]) -> None:
    """Move used inbox/audience lines into `## consumed / ### {week}`, keep unused."""
    if not thoughts and not audience:
        return
    text = inbox_path.read_text(encoding="utf-8")

    def _replace_section(text: str, header: str, used: list[str]) -> str:
        m = re.search(rf"^## {header}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
        if not m or not used:
            return text
        remaining = [ln for ln in _section_lines(text, header) if ln not in used]
        body = "\n" + "\n".join(f"- {ln}" for ln in remaining) + "\n\n" if remaining else "\n\n"
        return text[: m.start(1)] + body + text[m.end(1):]

    text = _replace_section(text, "thoughts", thoughts)
    text = _replace_section(text, "audience", audience)

    consumed_block = "\n".join(f"- {ln}" for ln in thoughts + audience)
    heading = f"### {week}"
    if re.search(rf"^{re.escape(heading)}\s*$", text, re.M):
        text = re.sub(
            rf"(^{re.escape(heading)}\s*$)",
            rf"\1\n{consumed_block}",
            text, count=1, flags=re.M,
        )
    else:
        text = text.rstrip("\n") + f"\n\n{heading}\n{consumed_block}\n"
    inbox_path.write_text(text, encoding="utf-8")


# ── Teleprompter HTML (one question per slide) ────────────────────────────────

_NICHE_COLORS = {"life": "#e8b44f", "poetry": "#b48ce8", "ds": "#4fc3e8"}

def build_teleprompter(pack: dict) -> str:
    slides = []
    qs = pack["questions"]
    for i, q in enumerate(qs):
        color = _NICHE_COLORS.get(q["niche"], "#ccc")
        slides.append(f"""
    <section class="slide" data-idx="{i}">
      <div class="meta"><span class="niche" style="color:{color}">{q['niche'].upper()}</span>
        <span class="count">{i + 1} / {len(qs)}</span></div>
      <p class="protocol">pause 3s &rarr; read the question aloud, word for word &rarr; answer raw</p>
      <h1 class="question">{html.escape(q['text'])}</h1>
      <p class="theme">{html.escape(q.get('theme', ''))}</p>
    </section>""")
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Prompt Pack — {pack['week']}</title>
<style>
  html,body {{ margin:0; height:100%; background:#0d0d10; color:#f4f1ea;
               font-family:Georgia,'Times New Roman',serif; }}
  .slide {{ display:none; height:100vh; box-sizing:border-box; padding:6vh 8vw;
            flex-direction:column; justify-content:center; }}
  .slide.active {{ display:flex; }}
  .meta {{ font-family:-apple-system,sans-serif; font-size:14px; letter-spacing:.2em;
           display:flex; justify-content:space-between; opacity:.9; }}
  .protocol {{ font-family:-apple-system,sans-serif; font-size:15px; color:#8a8578;
               margin:2vh 0 4vh; letter-spacing:.05em; }}
  .question {{ font-size:clamp(2.2rem, 5.5vw, 4.5rem); line-height:1.25; margin:0; }}
  .theme {{ font-family:-apple-system,sans-serif; color:#5c584e; margin-top:5vh;
            text-transform:uppercase; letter-spacing:.25em; font-size:12px; }}
  .hint {{ position:fixed; bottom:16px; right:24px; font-family:-apple-system,sans-serif;
           font-size:12px; color:#444; }}
</style></head><body>
{''.join(slides)}
  <div class="hint">&larr; / &rarr; or space to move &middot; one question per take</div>
<script>
  const slides = document.querySelectorAll('.slide');
  let idx = 0;
  function show(i) {{
    idx = Math.max(0, Math.min(slides.length - 1, i));
    slides.forEach((s, j) => s.classList.toggle('active', j === idx));
  }}
  document.addEventListener('keydown', e => {{
    if (e.key === 'ArrowRight' || e.key === ' ') show(idx + 1);
    if (e.key === 'ArrowLeft') show(idx - 1);
  }});
  show(0);
</script></body></html>"""


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description="Generate the weekly raw-session prompt pack.")
    ap.add_argument("--week", help="ISO week like 2026-W29 (default: current)")
    ap.add_argument("--theme", help="comma-separated Life theme filter (e.g. career,self-doubt)")
    ap.add_argument("--n-life", type=int, default=4)
    ap.add_argument("--n-poetry", type=int, default=2)
    ap.add_argument("--n-ds", type=int, default=2)
    ap.add_argument("--pack-size", type=int, default=8, help="max questions in the final pack")
    ap.add_argument("--inbox", default=str(INBOX_MD), help="path to thought_inbox.md")
    ap.add_argument("--force", action="store_true", help="overwrite existing pack")
    args = ap.parse_args()

    week = args.week or get_iso_week(datetime.date.today().isoformat())
    week_num = int(week.split("-W")[1])
    themes = [t.strip() for t in args.theme.split(",")] if args.theme else None

    out_dir = SESSIONS_DIR / week
    pack_path = out_dir / "prompt_pack.json"
    if pack_path.exists() and not args.force:
        print(f"{pack_path} exists — use --force to regenerate.")
        return 1

    inbox_path = (REPO / args.inbox) if not Path(args.inbox).is_absolute() else Path(args.inbox)
    priority_qs, used_thoughts, used_audience = inbox_questions(inbox_path)
    priority_qs = priority_qs + provocation_questions()

    fill_qs = (
        life_questions(week_num, args.n_life, themes)
        + niche_questions("poetry", "Poetry / Quotes", args.n_poetry)
        + niche_questions("ds", "DS — Data Science / Tech", args.n_ds)
    )

    questions = _dedupe(priority_qs + fill_qs)[: args.pack_size]
    if not questions:
        print("No questions produced — check question bank and weekly_ideas.md.")
        return 1
    for i, q in enumerate(questions):
        q["id"] = f"q{i + 1:02d}"

    pack = {
        "week": week,
        "generated": datetime.date.today().isoformat(),
        "theme_filter": themes or [],
        "language": "English",
        "protocol": "3s silence → read question aloud verbatim → answer raw; retake = pause 2s and restart",
        "questions": questions,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    pack_path.write_text(json.dumps(pack, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "teleprompter.html").write_text(build_teleprompter(pack), encoding="utf-8")

    consume_inbox(inbox_path, week, used_thoughts, used_audience)

    print(f"✓ {pack_path}")
    print(f"✓ {out_dir / 'teleprompter.html'}")
    for q in questions:
        print(f"  [{q['niche']:>6}] {q['text']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
