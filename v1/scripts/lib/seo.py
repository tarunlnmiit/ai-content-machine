"""Medium SEO helpers — extract per-article SEO fields and render manual steps.

Medium's public API can't set a story's SEO title / SEO description, so the blog
generators emit them as trailing HTML comments in the saved markdown:

    <!-- Target keyphrase: kale and ginger soup recipe -->
    <!-- SEO title: Easy Healthy Kale and Ginger Soup Recipe -->
    <!-- SEO description: A quick, healthy kale and ginger soup recipe ... -->

The pipeline surfaces them so the writer can paste them into Medium's SEO
settings (••• → SEO settings) after the draft exists. See docs/guides/medium-seo.md.
"""

from __future__ import annotations

import re

_PATTERNS: dict[str, re.Pattern[str]] = {
    "keyphrase": re.compile(r"<!--\s*target keyphrase:\s*(.+?)\s*-->", re.IGNORECASE | re.DOTALL),
    "seo_title": re.compile(r"<!--\s*seo title:\s*(.+?)\s*-->", re.IGNORECASE | re.DOTALL),
    "seo_description": re.compile(r"<!--\s*seo description:\s*(.+?)\s*-->", re.IGNORECASE | re.DOTALL),
}


def extract_seo(md: str) -> dict[str, str]:
    """Return {keyphrase, seo_title, seo_description} parsed from markdown comments.

    Missing fields are omitted. Tolerant of absent or partial blocks (returns {}).
    """
    out: dict[str, str] = {}
    for key, pat in _PATTERNS.items():
        m = pat.search(md or "")
        if m:
            val = m.group(1).strip()
            if val:
                out[key] = val
    return out


def seo_manual_steps(seo: dict[str, str]) -> str:
    """Render the post-run manual checklist for Medium's SEO settings.

    Returns "" when no SEO fields are present, so callers can `if steps: print`.
    """
    if not seo:
        return ""
    title = seo.get("seo_title", "(not generated — add manually)")
    desc = seo.get("seo_description", "(not generated — add manually)")
    keyphrase = seo.get("keyphrase", "(not generated)")
    lines = [
        "─ MANUAL STEPS (Medium can't set these via API) ─",
        "1. Open the story in Medium → ••• (More) → SEO settings.",
        f"2. SEO title:        {title}",
        f"3. SEO description:  {desc}",
        f"   (target keyphrase: {keyphrase} — already woven into the title + first paragraph)",
        "4. Re-upload any images (local /content/... paths don't render on Medium).",
        "5. Decide paywall: Google searchers are often non-members and will hit the paywall.",
    ]
    return "\n".join(lines)
