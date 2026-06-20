#!/usr/bin/env python3
"""Close the loop: surface last week's TOP performers so next week reproduces them.

The machine already collects analytics (collect_analytics.py → weekly_insights.md);
the missing piece was feeding that back into what gets produced. Run this at the
START of weekly planning (before picking the 2 core ideas per niche). It reads the
latest data/analytics/weekly_insights.md and prints the winning posts/videos plus a
"do more of this" directive routed by niche.

Usage:
    python3 scripts/weekly_winners.py
    python3 scripts/weekly_winners.py --insights data/analytics/weekly_insights.md
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_INSIGHTS = REPO / "data" / "analytics" / "weekly_insights.md"


def _section(text: str, header: str) -> str:
    """Return the body of a '## {header}' section up to the next '## ' or '---'."""
    pattern = rf"##\s+{re.escape(header)}\s*\n(.*?)(?:\n##\s|\n---|\Z)"
    m = re.search(pattern, text, re.DOTALL)
    return m.group(1).strip() if m else ""


def _bullets_after(text: str, label: str, limit: int = 3) -> list[str]:
    """Collect up to `limit` bullet lines following a 'Label:' marker."""
    out: list[str] = []
    capturing = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith(label.lower()):
            capturing = True
            continue
        if capturing:
            if stripped.startswith("-"):
                out.append(stripped.lstrip("- ").strip())
                if len(out) >= limit:
                    break
            elif stripped and not stripped.startswith("-"):
                break
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Surface last week's winners for reproduction.")
    ap.add_argument("--insights", default=str(DEFAULT_INSIGHTS))
    args = ap.parse_args()

    path = Path(args.insights)
    if not path.exists():
        print(f"No insights file at {path} — run collect_analytics.py first.")
        return 1

    text = path.read_text(encoding="utf-8")
    ig = _bullets_after(_section(text, "Instagram"), "Top posts:")
    yt = []
    for channel in ("Breath of Data Science", "Breath of Life", "Breath of Poetry"):
        yt += [f"[{channel}] {b}" for b in _bullets_after(_section(text, channel), "Recent videos:", limit=2)]

    print("=" * 64)
    print("REPRODUCE LAST WEEK'S WINNERS — read before picking this week's ideas")
    print("=" * 64)
    print("\nInstagram (your highest-engagement surface):")
    for b in ig or ["(no Instagram top posts parsed)"]:
        print(f"  • {b}")
    print("\nYouTube (recent):")
    for b in yt or ["(no YouTube videos parsed)"]:
        print(f"  • {b}")
    print(
        "\nDirective:\n"
        "  • Pick this week's 2 core DS/Life reel ideas to RHYME with the top IG post\n"
        "    above (same emotional angle / format), not 14 slices of the long-form.\n"
        "  • If a niche has no winner this week, give it the maintenance minimum and\n"
        "    push the niche that IS winning (stagger, don't spread evenly).\n"
        "  • Poetry: the poem-only short that resonated — write the next in that vein.\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
