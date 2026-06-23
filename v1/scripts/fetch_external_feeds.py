#!/usr/bin/env python3
"""External RSS/JSON feed scraper — no API keys, free sources.

Sources:
  DS/Tech:
    - Hacker News (top stories RSS + Algolia hot)
    - arXiv cs.LG, cs.AI, stat.ML new submissions
    - DEV.to top articles (last 7 days)
    - GitHub Trending (HTML scrape — devs use today)
    - Papers With Code trending (HTML scrape)
  Life/Self-dev:
    - Medium tag RSS (self-improvement, psychology, mental-health, productivity)
    - Spotify Podcast Charts (Top Episodes — health/self-help via public chart)
  Poetry/Quotes:
    - Medium tag RSS (poetry, quotes)
    - Poetry Foundation poem-of-the-day RSS
    - Goodreads Quotes (HTML scrape)

Output: data/ideas/external_YYYY-MM-DD.json
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup

REPO = Path(__file__).parent.parent
UA = {"User-Agent": "Mozilla/5.0 content-machine/1.0"}

FEEDS = {
    "data_science_tech": [
        ("hn_top", "https://news.ycombinator.com/rss"),
        ("arxiv_cs_lg", "https://export.arxiv.org/rss/cs.LG"),
        ("arxiv_cs_ai", "https://export.arxiv.org/rss/cs.AI"),
        ("arxiv_stat_ml", "https://export.arxiv.org/rss/stat.ML"),
        ("medium_data_science", "https://medium.com/feed/tag/data-science"),
        ("medium_mlops", "https://medium.com/feed/tag/mlops"),
        ("medium_analytics", "https://medium.com/feed/tag/data-analytics"),
    ],
    "life_self_dev": [
        ("medium_self_improvement", "https://medium.com/feed/tag/self-improvement"),
        ("medium_psychology", "https://medium.com/feed/tag/psychology"),
        ("medium_mental_health", "https://medium.com/feed/tag/mental-health"),
        ("medium_productivity", "https://medium.com/feed/tag/productivity"),
        ("medium_life_lessons", "https://medium.com/feed/tag/life-lessons"),
    ],
    "poetry_quotes": [
        ("medium_poetry", "https://medium.com/feed/tag/poetry"),
        ("medium_quotes", "https://medium.com/feed/tag/quotes"),
        ("poets_org_poem_a_day", "https://poets.org/poem-a-day/feed"),
    ],
}


def fetch_rss(name: str, url: str, limit: int = 15) -> list:
    try:
        resp = requests.get(url, headers=UA, timeout=12)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        items = []
        for e in feed.entries[:limit]:
            items.append({
                "source": name,
                "title": getattr(e, "title", "").strip(),
                "url": getattr(e, "link", ""),
                "summary": re.sub(r"<[^>]+>", " ", getattr(e, "summary", ""))[:400].strip(),
                "published": getattr(e, "published", ""),
            })
        return items
    except Exception as err:
        print(f"  warn: {name} → {err}")
        return []


def fetch_hn_algolia(query: str = "", days: int = 7, min_points: int = 100, limit: int = 30) -> list:
    """Hacker News Algolia API — hot stories last N days."""
    since = int((datetime.now().timestamp())) - days * 86400
    url = "https://hn.algolia.com/api/v1/search"
    params = {
        "tags": "story",
        "numericFilters": f"points>{min_points},created_at_i>{since}",
        "hitsPerPage": limit,
    }
    if query:
        params["query"] = query
    try:
        resp = requests.get(url, params=params, timeout=12)
        resp.raise_for_status()
        hits = resp.json().get("hits", [])
        return [
            {
                "source": "hn_algolia",
                "title": h.get("title", ""),
                "url": h.get("url", f"https://news.ycombinator.com/item?id={h.get('objectID')}"),
                "summary": "",
                "points": h.get("points", 0),
                "comments": h.get("num_comments", 0),
                "published": h.get("created_at", ""),
            }
            for h in hits if h.get("title")
        ]
    except Exception as err:
        print(f"  warn: hn_algolia → {err}")
        return []


def fetch_devto(top_days: int = 7, limit: int = 25) -> list:
    """DEV.to top articles past N days."""
    url = "https://dev.to/api/articles"
    try:
        resp = requests.get(url, params={"top": top_days, "per_page": limit}, timeout=12)
        resp.raise_for_status()
        return [
            {
                "source": "devto_top",
                "title": a.get("title", ""),
                "url": a.get("url", ""),
                "summary": a.get("description", "")[:400],
                "reactions": a.get("public_reactions_count", 0),
                "published": a.get("published_at", ""),
                "tags": a.get("tag_list", []),
            }
            for a in resp.json()
        ]
    except Exception as err:
        print(f"  warn: devto → {err}")
        return []


def fetch_github_trending(language: str = "python", since: str = "weekly") -> list:
    """Scrape github.com/trending — no API."""
    url = f"https://github.com/trending/{language}?since={since}"
    try:
        resp = requests.get(url, headers=UA, timeout=12)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        items = []
        for repo in soup.select("article.Box-row")[:20]:
            link = repo.select_one("h2 a")
            desc = repo.select_one("p")
            if not link:
                continue
            href = link.get("href", "").strip()
            items.append({
                "source": f"github_trending_{language}",
                "title": href.lstrip("/").replace("\n", "").strip(),
                "url": f"https://github.com{href}",
                "summary": (desc.text.strip() if desc else "")[:300],
            })
        return items
    except Exception as err:
        print(f"  warn: github_trending → {err}")
        return []


def fetch_goodreads_quotes(tag: str = "inspirational") -> list:
    url = f"https://www.goodreads.com/quotes/tag/{tag}"
    try:
        resp = requests.get(url, headers=UA, timeout=12)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        items = []
        for q in soup.select("div.quote")[:20]:
            text = q.select_one("div.quoteText")
            if not text:
                continue
            txt = text.get_text(" ", strip=True)
            items.append({
                "source": f"goodreads_{tag}",
                "title": txt[:200],
                "url": url,
                "summary": txt[:500],
            })
        return items
    except Exception as err:
        print(f"  warn: goodreads → {err}")
        return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default=str(REPO / "data" / "ideas"))
    ap.add_argument("--niche", choices=["data_science_tech", "life_self_dev", "poetry_quotes", "all"], default="all")
    args = ap.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = {n: [] for n in FEEDS}
    niches = list(FEEDS.keys()) if args.niche == "all" else [args.niche]

    for niche in niches:
        print(f"\n[{niche}]")
        for name, url in FEEDS[niche]:
            print(f"  fetch {name}")
            results[niche] += fetch_rss(name, url)

    # DS extras
    if args.niche in ("data_science_tech", "all"):
        print("\n[data_science_tech extras]")
        print("  fetch hn_algolia")
        results["data_science_tech"] += fetch_hn_algolia(min_points=100, limit=30)
        print("  fetch devto")
        results["data_science_tech"] += fetch_devto()
        print("  fetch github_trending python")
        results["data_science_tech"] += fetch_github_trending("python")

    # Poetry extras
    if args.niche in ("poetry_quotes", "all"):
        print("\n[poetry_quotes extras]")
        for tag in ("inspirational", "life", "love", "poetry"):
            print(f"  fetch goodreads/{tag}")
            results["poetry_quotes"] += fetch_goodreads_quotes(tag)

    date = datetime.now().strftime("%Y-%m-%d")
    out_file = out_dir / f"external_{date}.json"
    out_file.write_text(json.dumps(results, indent=2))

    total = sum(len(v) for v in results.values())
    print(f"\n✓ {total} items → {out_file}")
    for n, items in results.items():
        print(f"  {n}: {len(items)}")


if __name__ == "__main__":
    main()
