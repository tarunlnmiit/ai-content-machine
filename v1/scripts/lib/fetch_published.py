#!/usr/bin/env python3
"""Fetch full text + metadata for an already-published YouTube video or Medium blog.

Used by scripts/teaser_from_published.py to turn an existing published URL into a
short teaser + backlink.

Strategy (per the plan):
  - YouTube  → transcript via youtube-transcript-api; title/channel via oEmbed.
  - Medium   → article body via requests + BeautifulSoup (no API key needed).
  - Local fallback → if the piece already lives in the repo, read local text
    instead of hitting the network.

No API keys required. Network failures raise FetchError with a clear message.
"""

from __future__ import annotations

import datetime as _dt
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, parse_qs

import requests

REPO = Path(__file__).resolve().parent.parent.parent
MEDIUM_INDEX = REPO / "output" / "published" / "medium_posts.json"
SCRIPTS_DIR = REPO / "content" / "scripts"

_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

# Channel display name (from YouTube oEmbed author_name) → niche key.
CHANNEL_NICHE = {
    "breath of data science": "ds",
    "breath of life": "life",
    "breath of poetry": "poetry",
}

_NICHE_KEYWORDS = {
    "ds": ["python", "data", "machine learning", "model", "code", "algorithm", "sql", "pandas"],
    "poetry": ["poem", "poetry", "verse", "stanza", "metaphor", "soul", "heart", "longing"],
    "life": ["habit", "productivity", "growth", "morning", "discipline", "mindset", "routine"],
}


class FetchError(RuntimeError):
    """Raised when a published piece cannot be fetched."""


@dataclass(frozen=True)
class PublishedPiece:
    url: str
    kind: str          # "video" | "blog"
    title: str
    text: str
    niche: str         # ds | life | poetry
    slug: str          # YYYY-MM-DD_niche_<title-slug>
    date: str          # YYYY-MM-DD
    channel: str = ""


# ── URL helpers ──────────────────────────────────────────────────────────

def classify_url(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "youtube.com" in host or "youtu.be" in host:
        return "video"
    return "blog"


def extract_video_id(url: str) -> Optional[str]:
    parts = urlparse(url)
    host = parts.netloc.lower()
    if "youtu.be" in host:
        return parts.path.lstrip("/").split("/")[0] or None
    if "youtube.com" in host:
        qs = parse_qs(parts.query)
        if "v" in qs:
            return qs["v"][0]
        m = re.search(r"/(shorts|embed|live)/([\w-]+)", parts.path)
        if m:
            return m.group(2)
    return None


# ── Niche / slug ─────────────────────────────────────────────────────────

def infer_niche(title: str, text: str, channel: str = "") -> str:
    ch = channel.strip().lower()
    if ch in CHANNEL_NICHE:
        return CHANNEL_NICHE[ch]
    blob = f"{title}\n{text[:2000]}".lower()
    scores = {n: sum(blob.count(k) for k in kws) for n, kws in _NICHE_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "life"


def make_slug(date: str, niche: str, title: str) -> str:
    from lib.slug import slugify
    from lib.niche_config import NICHE_MAP
    niche_full = NICHE_MAP.get(niche, "life_self_dev")
    return f"{date}_{niche_full}_{slugify(title, 50)}"


# ── Local fallback ───────────────────────────────────────────────────────

def _resolve_blog_file(source_file: str) -> Optional[Path]:
    """Resolve a recorded source_file path, tolerating the ISO-week folder move.

    medium_posts.json may store the pre-reorg flat path (content/blogs/<file>.md);
    files now live under content/blogs/<YYYY-Wnn>/<file>.md. Fall back to a glob
    on the basename.
    """
    direct = REPO / source_file
    if direct.exists():
        return direct
    matches = list((REPO / "content" / "blogs").glob(f"**/{Path(source_file).name}"))
    return matches[0] if matches else None


def _local_text(url: str) -> Optional[tuple[str, str, str]]:
    """Return (title, text, stem) from a repo-local file if this URL maps to one.

    `stem` is the blog filename without extension — already in
    `YYYY-MM-DD_niche_slug` form, so it doubles as the canonical slug.
    """
    if MEDIUM_INDEX.exists():
        try:
            for rec in json.loads(MEDIUM_INDEX.read_text()):
                if rec.get("medium_url") == url and rec.get("source_file"):
                    src = _resolve_blog_file(rec["source_file"])
                    if src:
                        return rec.get("title", src.stem), src.read_text(encoding="utf-8"), src.stem
        except (OSError, json.JSONDecodeError):
            pass
    return None


# ── YouTube ──────────────────────────────────────────────────────────────

def _youtube_oembed(url: str) -> tuple[str, str]:
    try:
        r = requests.get(
            "https://www.youtube.com/oembed",
            params={"url": url, "format": "json"},
            headers={"User-Agent": _UA},
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
        return data.get("title", ""), data.get("author_name", "")
    except (requests.RequestException, ValueError):
        return "", ""


def _youtube_transcript(video_id: str) -> str:
    from youtube_transcript_api import YouTubeTranscriptApi
    try:  # youtube-transcript-api >= 1.0 (instance API)
        snippets = YouTubeTranscriptApi().fetch(video_id)
        return " ".join(s.text for s in snippets).strip()
    except AttributeError:  # older static API
        rows = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(r["text"] for r in rows).strip()


def fetch_youtube(url: str, niche_hint: Optional[str] = None) -> PublishedPiece:
    vid = extract_video_id(url)
    if not vid:
        raise FetchError(f"Could not extract video id from {url}")
    title, channel = _youtube_oembed(url)
    try:
        text = _youtube_transcript(vid)
    except Exception as e:  # transcript disabled / none / network
        raise FetchError(f"No transcript for {url}: {type(e).__name__}: {e}")
    if not text:
        raise FetchError(f"Empty transcript for {url}")
    title = title or f"YouTube {vid}"
    niche = niche_hint or infer_niche(title, text, channel)
    date = _dt.date.today().isoformat()
    return PublishedPiece(
        url=url, kind="video", title=title, text=text, niche=niche,
        slug=make_slug(date, niche, title), date=date, channel=channel,
    )


# ── Medium ───────────────────────────────────────────────────────────────

def _meta(soup, *names: str) -> str:
    for name in names:
        tag = soup.find("meta", property=name) or soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            return tag["content"]
    return ""


def fetch_medium(url: str, niche_hint: Optional[str] = None) -> PublishedPiece:
    local = _local_text(url)
    title = text = published = ""
    try:
        from bs4 import BeautifulSoup
        r = requests.get(url, headers={"User-Agent": _UA}, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        title = _meta(soup, "og:title", "twitter:title") or (soup.title.string if soup.title else "")
        published = _meta(soup, "article:published_time")
        article = soup.find("article")
        if article:
            paras = [p.get_text(" ", strip=True) for p in article.find_all(["p", "h1", "h2", "h3", "li"])]
            text = "\n\n".join(p for p in paras if p)
        else:
            text = soup.get_text("\n", strip=True)
    except Exception as e:
        if not local:
            raise FetchError(f"Could not fetch Medium article {url}: {type(e).__name__}: {e}")

    # Prefer local text when the network gave a bot-wall stub.
    if (not text or len(text) < 200) and local:
        title, text, stem = local
        date = stem[:10] if re.match(r"\d{4}-\d{2}-\d{2}", stem) else _dt.date.today().isoformat()
        niche = niche_hint or infer_niche(title, text)
        return PublishedPiece(url=url, kind="blog", title=title, text=text,
                              niche=niche, slug=stem, date=date)

    if (not text or len(text) < 200):
        raise FetchError(
            f"Could not extract article text from {url} (bot wall, no local copy). "
            "Paste the text into a local file and pass it via repurpose_blog.py instead."
        )

    title = (title or "Untitled").strip()
    date = (published[:10] if re.match(r"\d{4}-\d{2}-\d{2}", published or "") else _dt.date.today().isoformat())
    niche = niche_hint or infer_niche(title, text)
    return PublishedPiece(
        url=url, kind="blog", title=title, text=text, niche=niche,
        slug=make_slug(date, niche, title), date=date,
    )


# ── Entry ────────────────────────────────────────────────────────────────

def fetch(url: str, niche_hint: Optional[str] = None) -> PublishedPiece:
    """Fetch a published piece from its URL (YouTube or Medium/blog)."""
    if classify_url(url) == "video":
        return fetch_youtube(url, niche_hint)
    return fetch_medium(url, niche_hint)
