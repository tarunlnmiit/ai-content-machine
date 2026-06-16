"""
UTM link builder for attributing GitHub stars / follows back to content pieces.

Every repo link dropped in a DM, bio, or description should be UTM-tagged so the
star delta in `data/analytics/github_stars.json` can be correlated with the piece
that drove it.

Convention:
    utm_source   = platform   (instagram | youtube | tiktok | twitter | threads | linkedin)
    utm_medium   = format      (reel | short | bio | dm | post | thread)
    utm_campaign = project     (e.g. autopilot-jobhunt)
    utm_content  = piece slug  (e.g. 2026-06-16_autopilot_nightly-scan)
"""

from __future__ import annotations

from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl

PLATFORMS = {"instagram", "youtube", "tiktok", "twitter", "threads", "linkedin"}


def build_utm_url(
    base_url: str,
    *,
    source: str,
    medium: str,
    campaign: str,
    content: str = "",
) -> str:
    """Return base_url with UTM params merged in (existing query preserved)."""
    if source not in PLATFORMS:
        raise ValueError(f"Unknown source '{source}'. Expected one of {sorted(PLATFORMS)}")

    parts = urlparse(base_url)
    query = dict(parse_qsl(parts.query))
    query.update({
        "utm_source": source,
        "utm_medium": medium,
        "utm_campaign": campaign,
    })
    if content:
        query["utm_content"] = content
    return urlunparse(parts._replace(query=urlencode(query)))


def campaign_links(
    base_url: str,
    campaign: str,
    content: str,
    *,
    medium_by_platform: dict[str, str] | None = None,
) -> dict[str, str]:
    """Build one UTM link per platform for a single content piece."""
    defaults = {
        "instagram": "reel", "youtube": "short", "tiktok": "reel",
        "twitter": "thread", "threads": "post", "linkedin": "post",
    }
    medium_by_platform = {**defaults, **(medium_by_platform or {})}
    return {
        platform: build_utm_url(
            base_url, source=platform,
            medium=medium_by_platform[platform],
            campaign=campaign, content=content,
        )
        for platform in PLATFORMS
    }
