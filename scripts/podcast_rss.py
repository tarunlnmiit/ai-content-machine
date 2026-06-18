#!/usr/bin/env python3
"""
podcast_rss.py — RSS feed management for podcast episodes.

Uploads MP3s to GitHub Releases and maintains RSS XML for Spotify ingestion.
Spotify polls the RSS URL and picks up new episodes automatically.

SETUP (one-time):
  1. gh repo create tarunlnmiit/podcast-feed --public
  2. Repo Settings → Pages → Source: main branch / root
  3. Spotify for Podcasters → Import → paste RSS URL:
       life.xml:   https://tarunlnmiit.github.io/podcast-feed/life.xml
       poetry.xml: https://tarunlnmiit.github.io/podcast-feed/poetry.xml

USAGE:
  Called automatically by produce_podcast.py.

REQUIRES:
  gh CLI authenticated (gh auth status)
  ffmpeg (for ffprobe duration)
"""

import base64
import json
import subprocess
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.etree import ElementTree as ET

BASE_DIR = Path(__file__).resolve().parent.parent
RSS_DIR = BASE_DIR / "data" / "podcast" / "rss"
ARTWORK_DIR = BASE_DIR / "data" / "podcast" / "artwork"

PODCAST_REPO = "tarunlnmiit/podcast-feed"
PAGES_BASE = "https://tarunlnmiit.github.io/podcast-feed"

SHOW_CONFIG: dict[str, dict] = {
    "life": {
        "title": "Breath of Life",
        "description": "Personal development and life lessons from a 10-year data scientist.",
        "category": "Self-Improvement",
        "link": "https://youtube.com/@breathoflife_",
    },
    "poetry": {
        "title": "Breath of Poetry",
        "description": "Poetry, reflection, and the art of feeling seen.",
        "category": "Arts",
        "link": "https://youtube.com/@breathofpoetry",
    },
}

ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"
CONTENT_NS = "http://purl.org/rss/1.0/modules/content/"


# ── Duration ───────────────────────────────────────────────────────────────────

def get_audio_duration(mp3: Path) -> str:
    """Return HH:MM:SS duration via ffprobe."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json", str(mp3),
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return "00:00:00"
    data = json.loads(result.stdout)
    seconds = int(float(data.get("format", {}).get("duration", 0)))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


# ── GitHub Release upload ──────────────────────────────────────────────────────

def _check_gh_auth() -> None:
    result = subprocess.run(["gh", "auth", "status"], capture_output=True)
    if result.returncode != 0:
        sys.exit("gh CLI not authenticated. Run: gh auth login")


def upload_mp3(mp3: Path, niche: str, week: str) -> str:
    """Upload MP3 to GitHub Releases. Returns public download URL."""
    tag = f"podcast-{niche}-{week}"
    title = f"{SHOW_CONFIG[niche]['title']} — {week}"

    # Delete existing release with same tag (idempotent re-run)
    subprocess.run(
        ["gh", "release", "delete", tag, "--repo", PODCAST_REPO, "--yes"],
        capture_output=True,
    )

    print(f"  Uploading {mp3.name} to GitHub Releases ({tag})...")
    result = subprocess.run(
        [
            "gh", "release", "create", tag,
            "--repo", PODCAST_REPO,
            "--title", title,
            "--notes", f"Podcast episode: {title}",
            str(mp3),
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh release create failed:\n{result.stderr}")

    url = f"https://github.com/{PODCAST_REPO}/releases/download/{tag}/{mp3.name}"
    print(f"  [ok] MP3 URL: {url}")
    return url


# ── RSS XML ────────────────────────────────────────────────────────────────────

ET.register_namespace("itunes", ITUNES_NS)
ET.register_namespace("content", CONTENT_NS)


def _itunes(tag: str) -> str:
    return f"{{{ITUNES_NS}}}{tag}"


def _make_channel(niche: str) -> ET.Element:
    """Create a fresh RSS channel element."""
    config = SHOW_CONFIG[niche]
    artwork_url = f"{PAGES_BASE}/artwork/{niche}.jpg"

    rss = ET.Element("rss", {
        "version": "2.0",
        "xmlns:itunes": ITUNES_NS,
        "xmlns:content": CONTENT_NS,
    })
    channel = ET.SubElement(rss, "channel")

    def sub(parent: ET.Element, tag: str, text: str) -> ET.Element:
        el = ET.SubElement(parent, tag)
        el.text = text
        return el

    sub(channel, "title", config["title"])
    sub(channel, "link", config["link"])
    sub(channel, "description", config["description"])
    sub(channel, "language", "en-us")
    sub(channel, _itunes("author"), "Tarun Gupta")
    sub(channel, _itunes("summary"), config["description"])
    ET.SubElement(channel, _itunes("image"), {"href": artwork_url})
    ET.SubElement(channel, _itunes("category"), {"text": config["category"]})
    sub(channel, _itunes("explicit"), "false")

    return rss


def _build_item(
    title: str,
    description: str,
    mp3_url: str,
    mp3_bytes: int,
    duration: str,
    pub_date: str,
) -> ET.Element:
    item = ET.Element("item")

    def sub(tag: str, text: str) -> ET.Element:
        el = ET.SubElement(item, tag)
        el.text = text
        return el

    sub("title", title)
    sub("description", description)
    sub("pubDate", pub_date)
    sub("guid", mp3_url).set("isPermaLink", "true")
    sub(_itunes("duration"), duration)
    sub(_itunes("summary"), description[:255])
    ET.SubElement(item, "enclosure", {
        "url": mp3_url,
        "type": "audio/mpeg",
        "length": str(mp3_bytes),
    })
    return item


def update_rss_xml(
    niche: str,
    title: str,
    description: str,
    mp3_url: str,
    mp3_path: Path,
    duration: str,
) -> Path:
    """Prepend new episode item to RSS feed. Creates feed from scratch if needed."""
    RSS_DIR.mkdir(parents=True, exist_ok=True)
    rss_path = RSS_DIR / f"{niche}.xml"

    pub_date = format_datetime(datetime.now(timezone.utc))
    mp3_bytes = mp3_path.stat().st_size

    item = _build_item(title, description, mp3_url, mp3_bytes, duration, pub_date)

    if rss_path.exists():
        ET.register_namespace("itunes", ITUNES_NS)
        ET.register_namespace("content", CONTENT_NS)
        tree = ET.parse(rss_path)
        rss_el = tree.getroot()
        channel = rss_el.find("channel")
        if channel is None:
            raise ValueError(f"Malformed RSS at {rss_path} — no <channel>")
        # Insert new item before existing items (most recent first)
        first_item_idx = next(
            (i for i, child in enumerate(list(channel)) if child.tag == "item"),
            len(list(channel)),
        )
        channel.insert(first_item_idx, item)
    else:
        rss_el = _make_channel(niche)
        channel = rss_el.find("channel")
        channel.append(item)

    ET.indent(rss_el, space="  ")
    tree_out = ET.ElementTree(rss_el)
    with rss_path.open("wb") as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        tree_out.write(f, encoding="utf-8", xml_declaration=False)

    print(f"  [ok] RSS updated: {rss_path.relative_to(BASE_DIR)}")
    return rss_path


# ── Push RSS to GitHub Pages ───────────────────────────────────────────────────

def push_rss(niche: str) -> None:
    """Upload RSS XML to tarunlnmiit/podcast-feed via GitHub API (no clone needed)."""
    rss_path = RSS_DIR / f"{niche}.xml"
    if not rss_path.exists():
        raise FileNotFoundError(f"RSS file not found: {rss_path}")

    content_b64 = base64.b64encode(rss_path.read_bytes()).decode()
    remote_path = f"{niche}.xml"

    # Fetch current file SHA (required for update; omit for create)
    sha_result = subprocess.run(
        ["gh", "api", f"repos/{PODCAST_REPO}/contents/{remote_path}",
         "--jq", ".sha"],
        capture_output=True, text=True,
    )
    sha = sha_result.stdout.strip() if sha_result.returncode == 0 else None

    fields = [
        "-f", f"message=Update {niche} RSS feed",
        "-f", f"content={content_b64}",
    ]
    if sha:
        fields += ["-f", f"sha={sha}"]

    result = subprocess.run(
        ["gh", "api", f"repos/{PODCAST_REPO}/contents/{remote_path}",
         "--method", "PUT", *fields],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to push RSS to GitHub:\n{result.stderr}")

    print(f"  [ok] RSS live: {PAGES_BASE}/{niche}.xml")


# ── Orchestrator ───────────────────────────────────────────────────────────────

def publish_episode(
    mp3: Path,
    title: str,
    description: str,
    niche: str,
    week: str,
) -> None:
    """Full pipeline: upload MP3 → update RSS → push to GitHub Pages."""
    _check_gh_auth()

    duration = get_audio_duration(mp3)
    mp3_url = upload_mp3(mp3, niche, week)
    update_rss_xml(niche, title, description, mp3_url, mp3, duration)
    push_rss(niche)

    print(f"\n  Episode published via RSS.")
    print(f"  Spotify will pick it up within ~1hr from:")
    print(f"  {PAGES_BASE}/{niche}.xml")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Push podcast RSS feed manually.")
    parser.add_argument("--niche", choices=["life", "poetry"], required=True)
    parser.add_argument("--push-only", action="store_true", help="Only push existing RSS, no upload")
    args = parser.parse_args()
    if args.push_only:
        push_rss(args.niche)
    else:
        print("Use produce_podcast.py for full episode publishing.")
