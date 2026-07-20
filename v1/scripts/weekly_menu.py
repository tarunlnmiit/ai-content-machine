#!/usr/bin/env python3
"""The Menu — the single decision surface the human sees each week.

One markdown file, checkbox per item. Everything is pre-decided by the machine;
the human only ticks ✅ (make/ship it) or leaves ❌. Shows exactly ONE headline
metric from last week (anti-demotivation: no metric-staring).

Reads:  content/sessions/{week}/prompt_pack.json   (recording questions)
        data/ideas/weekly_ideas.md                 (blog slots per niche)
        data/analytics/weekly_insights.md          (one headline metric)
Writes: data/ideas/weekly_menu.md

Usage:  python3 scripts/weekly_menu.py [--week 2026-W29]
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.schedule_calc import get_iso_week  # noqa: E402

SESSIONS_DIR = REPO / "content" / "sessions"
IDEAS_MD = REPO / "data" / "ideas" / "weekly_ideas.md"
INSIGHTS_MD = REPO / "data" / "analytics" / "weekly_insights.md"
MENU_MD = REPO / "data" / "ideas" / "weekly_menu.md"

NICHE_LABEL = {"life": "Life", "poetry": "Poetry", "ds": "DS"}
EPISODE_ROTATION = ["poetry", "ds", "life"]  # indexed by week_num % 3; anchored so 2026-W29 → life


def headline_metric() -> str:
    """First concrete number from last week's insights — exactly one."""
    if not INSIGHTS_MD.exists():
        return "_(no analytics yet — run collect_analytics.py)_"
    text = INSIGHTS_MD.read_text(encoding="utf-8")
    for line in text.splitlines():
        m = re.search(r"([\d,]{2,}\s*(views|likes|subscribers|reads|followers|saves))", line, re.I)
        if m:
            return f"**{m.group(1).strip()}** — {line.strip().lstrip('-•* ')[:90]}"
    return "_(no headline number found in insights)_"


def blog_slots() -> list[str]:
    """Top scored idea title per niche from weekly_ideas.md, else placeholder."""
    slots = []
    text = IDEAS_MD.read_text(encoding="utf-8") if IDEAS_MD.exists() else ""
    headers = {"ds": "DS — Data Science / Tech", "life": "Life — Life & Self-Development",
               "poetry": "Poetry / Quotes"}
    for niche, header in headers.items():
        m = re.search(rf"^## {re.escape(header)}.*?(?=^## |\Z)", text, re.M | re.S)
        section = m.group(0) if m else ""
        idea = ""
        im = re.search(r"^\s*(?:\d+\.|[-•])\s*\*\*(.{10,120}?)\*\*", section, re.M)
        if im:
            idea = im.group(1).strip()
        slots.append(f"- [ ] **{NICHE_LABEL[niche]} blog** — {idea or 'pick from weekly_ideas.md'}")
    return slots


def main() -> int:
    ap = argparse.ArgumentParser(description="Render the weekly menu.")
    ap.add_argument("--week", help="ISO week (default: current)")
    args = ap.parse_args()
    week = args.week or get_iso_week(datetime.date.today().isoformat())
    week_num = int(week.split("-W")[1])
    episode_niche = EPISODE_ROTATION[week_num % len(EPISODE_ROTATION)]

    pack_path = SESSIONS_DIR / week / "prompt_pack.json"
    questions = []
    if pack_path.exists():
        pack = json.loads(pack_path.read_text(encoding="utf-8"))
        questions = pack.get("questions", [])

    q_lines = [
        f"- [ ] `{q['id']}` [{NICHE_LABEL.get(q['niche'], q['niche'])}] {q['text']}"
        for q in questions
    ] or ["- [ ] _(no prompt pack — run generate_prompt_pack.py)_"]

    menu = f"""# The Menu — {week}

_Tick ✅ what ships. Untouched = skipped, no guilt. Nothing here needs more than a checkbox._

## Last week, one number
{headline_metric()}

## 🎙 Recording session (weekend, 60–90 min, green screen)
Teleprompter: `content/sessions/{week}/teleprompter.html` — pause 3s, read the
question aloud verbatim, answer raw. Re-read the question to retake.

{chr(10).join(q_lines)}

## 📺 This week's episode
- [ ] Long-form episode: **{NICHE_LABEL[episode_niche]}** → its channel (rotation)

## ✍️ Blogs (Claude writes; you approve)
{chr(10).join(blog_slots())}

## 📤 Publish slots (auto once approved)
- Reels: 3–4 best clips → IG + YT Shorts (scheduler)
- Episode → YouTube ({NICHE_LABEL[episode_niche]} channel)
- Blogs → Medium + worksheet (DS/Life)

_Review outputs Sunday in `output/review/{week}/` — 20 minutes, then done._
"""
    MENU_MD.write_text(menu, encoding="utf-8")
    print(f"✓ {MENU_MD}")
    print(f"  episode niche this week: {episode_niche} · {len(questions)} questions on the menu")
    return 0


if __name__ == "__main__":
    sys.exit(main())
