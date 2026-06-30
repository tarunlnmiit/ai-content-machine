"""Write a per-slug 'manual steps' sidecar so the human to-dos live next to the
content (keyed by slug) instead of cluttering the blog body or only the console.

File: content/derivatives/{week}/{full_slug}/manual_steps.md
"""

from __future__ import annotations

from datetime import date
from pathlib import Path


def _render(full_slug: str, sections: list[tuple[str, str]]) -> str:
    lines = [
        f"# Manual steps — `{full_slug}`",
        "",
        f"_Generated {date.today().isoformat()}. Everything below is a human action; "
        "the blog body stays clean._",
        "",
    ]
    for heading, body in sections:
        body = (body or "").strip()
        if not body:
            continue
        lines.append(f"## {heading}")
        lines.append("")
        lines.append(body)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_manual_steps(deriv_dir: Path, full_slug: str, sections: list[tuple[str, str]]) -> Path:
    """Render the sidecar markdown. `sections` is an ordered list of (heading, body).

    `deriv_dir` is the per-slug derivatives directory (where schedule.json lives).
    Returns the written path.
    """
    deriv_dir.mkdir(parents=True, exist_ok=True)
    out = deriv_dir / "manual_steps.md"
    out.write_text(_render(full_slug, sections), encoding="utf-8")
    return out
