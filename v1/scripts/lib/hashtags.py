"""Per-niche, per-platform hashtag builder for blog derivatives.

Merges a platform's Claude-generated topical hashtags with a curated niche
pool (from config/hashtags.json), dedupes case-insensitively, and caps per
platform. Brand pools keep tags consistent + on-brand; Claude's topical tags
keep them relevant to the specific post.

Topical (Claude) tags lead so the post-specific tag always appears; the
curated niche pool fills the remaining slots up to the per-platform cap.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
_CONFIG = _REPO / "config" / "hashtags.json"

# Fallbacks if config is missing/unreadable.
_DEFAULT_POOLS = {
    "ds": ["datascience", "python", "machinelearning", "dataanalytics", "coding", "programming", "ai", "tech"],
    "life": ["selfimprovement", "personaldevelopment", "habits", "productivity", "mindset", "growth", "motivation"],
    "poetry": ["poetry", "poems", "writing", "quotes", "poetrycommunity", "words", "literature"],
}
_DEFAULT_CAPS = {"twitter": 2, "threads": 3, "linkedin": 4, "instagram": 12}


def _load_config() -> tuple[dict, dict]:
    try:
        cfg = json.loads(_CONFIG.read_text(encoding="utf-8"))
        return cfg.get("niche_pools", _DEFAULT_POOLS), cfg.get("platform_caps", _DEFAULT_CAPS)
    except (OSError, ValueError):
        return _DEFAULT_POOLS, _DEFAULT_CAPS


def _normalize(tag: str) -> str:
    """A hashtag token: lowercase, alphanumerics only, no leading '#'."""
    return re.sub(r"[^0-9a-z]", "", str(tag).lower().lstrip("#"))


def build_hashtags(
    niche: str,
    platform: str,
    claude_tags: list[str] | None = None,
    max_count: int | None = None,
) -> list[str]:
    """Ordered, deduped, capped hashtag tokens (no '#') for a platform."""
    pools, caps = _load_config()
    pool = pools.get(niche, [])
    cap = max_count if max_count is not None else caps.get(platform, 4)
    topical = list(claude_tags or [])

    ordered = topical + pool  # topical leads; pool fills remaining slots

    seen: set[str] = set()
    out: list[str] = []
    for tag in ordered:
        token = _normalize(tag)
        if token and token not in seen:
            seen.add(token)
            out.append(token)
        if len(out) >= cap:
            break
    return out


def hashtag_line(
    niche: str,
    platform: str,
    claude_tags: list[str] | None = None,
    max_count: int | None = None,
) -> str:
    """Space-joined `#tag` string, or '' if none."""
    tags = build_hashtags(niche, platform, claude_tags, max_count)
    return " ".join(f"#{t}" for t in tags)
