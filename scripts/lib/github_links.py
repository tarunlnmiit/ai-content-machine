"""GitHub code link helpers for YouTube descriptions and pinned comments.

Parallel to worksheet_cta.py. Used by push_tutorial_code.py and
upload_youtube.py to inject tutorial code links into DS video metadata.
"""

from __future__ import annotations

GITHUB_CODE_MARKER = "<!-- github-code -->"


def github_yt_description_snippet(url: str, title: str | None = None) -> str:
    """Block to include in the YouTube video description."""
    label = title or "Tutorial code"
    return f"{GITHUB_CODE_MARKER}\n💻 {label} (GitHub):\n{url}"


def github_yt_pinned_comment(url: str, title: str | None = None) -> str:
    """Text for the pinned comment posted after upload."""
    label = title or "Tutorial code"
    return f"💻 {label} (full code on GitHub):\n{url}"


def has_github_snippet(text: str) -> bool:
    return GITHUB_CODE_MARKER in text
