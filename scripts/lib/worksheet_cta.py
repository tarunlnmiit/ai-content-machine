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


def extract_worksheet_slug_from_dir(dir_name: str) -> str | None:
    """Extract worksheet slug from derivative directory name.

    Pattern: YYYY-MM-DD_{niche}_{slug}
    Returns the {slug} part, or None if format doesn't match.
    """
    import re
    match = re.match(r'^\d{4}-\d{2}-\d{2}_(?:data_science_tech|life_self_dev|poetry_quotes)_(.+)$', dir_name)
    return match.group(1) if match else None


def inject_worksheet_ctas_to_dir(out_dir: Path, worksheet_slug: str, niche: str) -> list[str]:
    """Inject worksheet CTAs into all derivative files in a directory.

    Args:
        out_dir: Path to derivative directory (e.g., content/derivatives/2026-W24/...)
        worksheet_slug: The worksheet slug (e.g., "python-for-data-science-tutorial-4-pandas-for-data-analysis")
        niche: Niche key ('ds' or 'life')

    Returns:
        List of modified file paths (relative to repo).

    Idempotent: skips files that already contain the worksheet URL.
    """
    from pathlib import Path
    from .hashtags import hashtag_line

    url = worksheet_url(worksheet_slug)
    title = worksheet_title(worksheet_slug)
    modified = []

    # Skip if worksheet URL already present (idempotent)
    if not url:
        return []

    # Instagram: append before hashtags
    ig_file = out_dir / "instagram_caption.txt"
    if ig_file.exists():
        text = ig_file.read_text(encoding="utf-8")
        if url not in text:
            # Find last line (hashtags); insert before it
            lines = text.rstrip("\n").split("\n")
            ws_line = f"📋 Free worksheet → {url}"

            # Check if last line is hashtags
            if lines and lines[-1].startswith("#"):
                lines.insert(-1, ws_line)
            else:
                lines.append(ws_line)

            # Add hashtags if missing
            if not any(line.startswith("#") for line in lines):
                tags = hashtag_line(niche, "instagram")
                if tags:
                    lines.append(tags)

            ig_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
            modified.append(str(ig_file.relative_to(Path(__file__).resolve().parent.parent.parent)))

    # LinkedIn: append at end with hashtags fallback
    li_file = out_dir / "linkedin_post.txt"
    if li_file.exists():
        text = li_file.read_text(encoding="utf-8")
        if url not in text:
            ws_line = f"📋 **Free worksheet:** [Download {title or 'the companion worksheet'} →]({url})"
            lines = text.rstrip("\n").split("\n")
            lines.append("")
            lines.append(ws_line)

            # Add hashtags if missing
            if not any(line.startswith("#") for line in lines):
                tags = hashtag_line(niche, "linkedin")
                if tags:
                    lines.append("")
                    lines.append(tags)

            li_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
            modified.append(str(li_file.relative_to(Path(__file__).resolve().parent.parent.parent)))

    # Threads: append at end with hashtags fallback
    threads_file = out_dir / "threads_post.txt"
    if threads_file.exists():
        text = threads_file.read_text(encoding="utf-8")
        if url not in text:
            ws_line = f"📋 Free worksheet → {url}"
            lines = text.rstrip("\n").split("\n")
            lines.append("")
            lines.append(ws_line)

            # Add hashtags if missing
            if not any(line.startswith("#") for line in lines):
                tags = hashtag_line(niche, "threads")
                if tags:
                    lines.append("")
                    lines.append(tags)

            threads_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
            modified.append(str(threads_file.relative_to(Path(__file__).resolve().parent.parent.parent)))

    # Twitter: append to closing tweet + hashtags fallback
    twitter_file = out_dir / "twitter_thread.txt"
    if twitter_file.exists():
        text = twitter_file.read_text(encoding="utf-8")
        if url not in text:
            lines = text.rstrip("\n").split("\n\n")  # tweets separated by blank lines
            if lines:
                last_tweet = lines[-1]
                # Add hashtags to closing tweet if missing
                if not last_tweet.lstrip().startswith("#"):
                    tags = hashtag_line(niche, "twitter")
                    if tags:
                        last_tweet = last_tweet.rstrip() + "\n\n" + tags
                # Append worksheet URL to closing tweet
                lines[-1] = last_tweet.rstrip() + "\n\n" + f"📋 {url}"

            twitter_file.write_text("\n\n".join(lines) + "\n", encoding="utf-8")
            modified.append(str(twitter_file.relative_to(Path(__file__).resolve().parent.parent.parent)))

    # Newsletter: append worksheet URL line
    newsletter_file = out_dir / "newsletter.txt"
    if newsletter_file.exists():
        text = newsletter_file.read_text(encoding="utf-8")
        if url not in text:
            newsletter_file.write_text(text.rstrip("\n") + f"\n\n📋 Free worksheet: {url}\n", encoding="utf-8")
            modified.append(str(newsletter_file.relative_to(Path(__file__).resolve().parent.parent.parent)))

    # YouTube metadata: replace [LINKS_PLACEHOLDER]
    yt_file = out_dir / "youtube_metadata.json"
    if yt_file.exists():
        import json
        try:
            data = json.loads(yt_file.read_text(encoding="utf-8"))
            if "[LINKS_PLACEHOLDER]" in data.get("description", ""):
                ws_block = f"📋 Free worksheet — {title or 'Companion worksheet'}:\n{url}"
                data["description"] = data["description"].replace("[LINKS_PLACEHOLDER]", ws_block)
                yt_file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                modified.append(str(yt_file.relative_to(Path(__file__).resolve().parent.parent.parent)))
        except (json.JSONDecodeError, KeyError):
            pass

    return modified
