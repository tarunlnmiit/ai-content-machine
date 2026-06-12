"""Worksheet CTA helpers.

Shared by produce_blog.py (Phase 3: auto-insert into new blog markdown) and
worksheet_links.py (Phase 1/2: emit copy-paste links for blogs already on
Medium). The public URL shape is the single source of truth here.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_BASE_URL = "https://worksheets-thebreathnetwork.vercel.app"

# Marker so auto-insertion is idempotent (guard against double-insert).
CTA_MARKER = "<!-- worksheet-cta -->"
# Spoken-script marker (YT), same idempotency guard.
YT_CTA_MARKER = "<!-- worksheet-yt-cta -->"

_REPO = Path(__file__).resolve().parent.parent.parent
_MANIFEST = _REPO / "worksheets-manifest.json"


def base_url() -> str:
    """Base URL for the worksheet delivery app (no trailing slash)."""
    return os.environ.get("WORKSHEET_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def worksheet_url(slug: str) -> str:
    """Public, gated download URL for a worksheet slug."""
    return f"{base_url()}/get-worksheet?slug={slug}"


def _manifest() -> dict:
    try:
        return json.loads(_MANIFEST.read_text(encoding="utf-8")).get("worksheets", {})
    except (OSError, ValueError):
        return {}


def worksheet_exists(slug: str) -> bool:
    """True if a built worksheet PDF maps to this slug."""
    return slug in _manifest()


def worksheet_title(slug: str) -> str | None:
    """Title for a slug from the manifest, if present."""
    entry = _manifest().get(slug)
    return entry.get("title") if entry else None


def worksheet_blog_snippet(slug: str, title: str | None = None) -> str:
    """One-line markdown hyperlink to paste into a blog body."""
    label = title or worksheet_title(slug) or "the companion worksheet"
    return f"📋 **Free worksheet:** [Download {label} →]({worksheet_url(slug)})"


def worksheet_yt_spoken_cta() -> str:
    """Spoken line for a YouTube script — points viewers to the description.

    Wrapped in YT_CTA_MARKER so it is appended at most once.
    """
    return (
        f"{YT_CTA_MARKER}\n\n"
        "**[WORKSHEET CTA]** Oh — and I made a free worksheet to go with this. "
        "It's linked in the description, no cost. Grab it and actually put this into practice.\n"
    )


def worksheet_yt_description_snippet(slug: str, title: str | None = None) -> str:
    """Block to paste into the YouTube video description."""
    label = title or worksheet_title(slug) or "Companion worksheet"
    return f"📋 Free worksheet — {label}:\n{worksheet_url(slug)}"


def has_yt_cta(text: str) -> bool:
    return YT_CTA_MARKER in text


def worksheet_cta_markdown(slug: str, title: str | None = None) -> str:
    """Markdown CTA block to append to a blog body.

    Wrapped in CTA_MARKER so it can be detected and not duplicated.
    """
    link_text = "Download the companion worksheet →"
    body = (
        f"{CTA_MARKER}\n\n"
        "---\n\n"
        "### Want to put this into practice?\n\n"
        f"[{link_text}]({worksheet_url(slug)})\n\n"
        "_Free PDF. Enter your email and it opens right away._\n"
    )
    return body


def has_cta(markdown: str) -> bool:
    """True if a worksheet CTA is already present."""
    return CTA_MARKER in markdown
