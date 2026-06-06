#!/usr/bin/env python3
"""
build_knowledge_base.py — Weekly knowledge base refresh pipeline.

Reads: Notion, YouTube, Twitter, Instagram, trends, Reddit ideas.
Synthesis uses Gemini 2.5 Flash API (gemini-3-flash-preview) with 1M context.
Writes: data/kb/master_brief.md
"""

import json
import os
import glob
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent
KB_DIR = BASE_DIR / "data" / "kb"
ANALYTICS_DIR = BASE_DIR / "data" / "analytics"
IDEAS_DIR = BASE_DIR / "data" / "ideas"

KB_DIR.mkdir(parents=True, exist_ok=True)
load_dotenv(BASE_DIR / ".env")

NOTION_TOKEN = os.getenv("NOTION_INTEGRATION_SECRET")
NOTION_CONTENT_DB = "5c1a6fa3-19f7-481b-9946-5224a579b569"

NOW = datetime.now(timezone.utc)
DAYS_30_AGO = NOW - timedelta(days=30)
DAYS_90_AGO = NOW - timedelta(days=90)


def log(msg: str) -> None:
    print(f"[{NOW.strftime('%H:%M:%S')}] {msg}", flush=True)


def load_analytics(source_name: str) -> dict:
    """Load latest analytics file for source."""
    pattern = f"{ANALYTICS_DIR}/{source_name}_*.json"
    files = sorted(glob.glob(pattern))
    if not files:
        return {}
    try:
        with open(files[-1]) as f:
            return json.load(f)
    except Exception as e:
        log(f"  Error loading {source_name}: {e}")
        return {}


def load_ideas() -> dict:
    """Load weekly ideas and recent scrapes."""
    data = {}

    # Weekly ideas ranking
    ideas_file = Path(IDEAS_DIR) / "weekly_ideas.md"
    if ideas_file.exists():
        data["weekly_ideas"] = ideas_file.read_text()

    # Reddit scrape
    reddit_files = sorted(glob.glob(f"{IDEAS_DIR}/reddit_*.json"))
    if reddit_files:
        try:
            with open(reddit_files[-1]) as f:
                data["reddit_trends"] = json.load(f)
        except:
            pass

    # YouTube ideas
    yt_ideas_files = sorted(glob.glob(f"{IDEAS_DIR}/youtube_*.json"))
    if yt_ideas_files:
        try:
            with open(yt_ideas_files[-1]) as f:
                data["youtube_trending"] = json.load(f)
        except:
            pass

    # Trend Pulse (multi-source trends)
    pulse_files = sorted(glob.glob(f"{IDEAS_DIR}/trend_pulse_*.json"))
    if pulse_files:
        try:
            with open(pulse_files[-1]) as f:
                data["trend_pulse"] = json.load(f)
        except:
            pass

    # Google Trends (legacy)
    trends_files = sorted(glob.glob(f"{IDEAS_DIR}/google_trends_*.json"))
    if trends_files:
        try:
            with open(trends_files[-1]) as f:
                data["google_trends"] = json.load(f)
        except:
            pass

    # Instagram Trends
    ig_trends_files = sorted(glob.glob(f"{IDEAS_DIR}/instagram_trends_*.json"))
    if ig_trends_files:
        try:
            with open(ig_trends_files[-1]) as f:
                data["instagram_trends"] = json.load(f)
        except:
            pass

    return data


def fetch_notion_archive() -> dict:
    """Fetch published content from Notion (last 90 days)."""
    if not NOTION_TOKEN:
        return {}

    log("Notion: fetching published content (90 days)…")
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }

    cutoff = DAYS_90_AGO.date().isoformat()
    payload = {
        "filter": {
            "and": [
                {"property": "Status", "status": {"equals": "Published"}},
                {"property": "Publish Date", "date": {"on_or_after": cutoff}},
            ]
        },
        "page_size": 100,
    }

    posts = []
    cursor = None

    try:
        while True:
            if cursor:
                payload["start_cursor"] = cursor

            resp = requests.post(
                f"https://api.notion.com/v1/databases/{NOTION_CONTENT_DB}/query",
                headers=headers,
                json=payload,
                timeout=30,
            )

            if resp.status_code != 200:
                log(f"  Notion API error {resp.status_code}")
                break

            data = resp.json()

            for page in data.get("results", []):
                props = page.get("properties", {})

                def get_prop(name: str) -> str:
                    prop = props.get(name, {})
                    ptype = prop.get("type")
                    if ptype == "title":
                        return "".join(t["plain_text"] for t in prop.get("title", []))
                    if ptype == "rich_text":
                        return "".join(t["plain_text"] for t in prop.get("rich_text", []))
                    if ptype == "select":
                        sel = prop.get("select")
                        return sel["name"] if sel else ""
                    if ptype == "date":
                        d = prop.get("date")
                        return d["start"] if d else ""
                    return ""

                posts.append({
                    "title": get_prop("Name"),
                    "topic": get_prop("Topic"),
                    "status": get_prop("Status"),
                    "publish_date": get_prop("Publish Date"),
                })

            if not data.get("has_more"):
                break
            cursor = data.get("next_cursor")

        log(f"  Fetched {len(posts)} published posts")
        return {"posts": posts, "count": len(posts)}
    except Exception as e:
        log(f"  Notion fetch failed: {e}")
        return {}


def synthesize_brief(analytics: dict, ideas: dict, notion: dict) -> str:
    """Use Claude CLI → Ollama for synthesis."""
    # Build context from all sources
    context_parts = [
        "# CREATOR ANALYTICS DATA",
        f"Generated: {NOW.isoformat()}",
        "",
        "## YouTube Analytics",
        json.dumps(analytics.get("youtube", {}), indent=2),
        "",
        "## Twitter Analytics",
        json.dumps(analytics.get("twitter", {}), indent=2),
        "",
        "## Instagram Analytics",
        json.dumps(analytics.get("instagram", {}), indent=2),
        "",
        "## Weekly Ideas & Rankings",
        ideas.get("weekly_ideas", "No weekly ideas generated yet."),
        "",
        "## Reddit Trends",
        json.dumps(ideas.get("reddit_trends", {}), indent=2),
        "",
        "## YouTube Trending Topics",
        json.dumps(ideas.get("youtube_trending", {}), indent=2),
        "",
        "## Multi-Source Trends (Google Trends, Reddit, Hacker News)",
        json.dumps(ideas.get("trend_pulse", {}), indent=2),
        "",
        "## Instagram Trending Hashtags (Classified by Niche)",
        json.dumps(ideas.get("instagram_trends", {}), indent=2),
        "",
        "## Published Content (90 days)",
        json.dumps(notion.get("posts", []), indent=2),
    ]

    full_context = "\n".join(context_parts)

    prompt = f"""You are a strategic content advisor analyzing creator data.

Based on comprehensive analytics data provided below, generate a structured knowledge base brief.

{full_context}

REQUIRED OUTPUT FORMAT (Markdown):

# Content Machine Knowledge Base
Generated: [date]

## Executive Summary
- Top performing content type and niche
- Key audience engagement patterns
- 1-2 major trends or opportunities

## Performance Metrics by Platform
### YouTube
- Views, watch time, engagement rates
- Top 3 performing videos by topic
- Best upload time/frequency pattern

### Twitter
- Top tweets by engagement
- Follower growth trajectory
- Hashtag performance

### Instagram
- Top posts by engagement rate
- Best content format
- Audience demographics

## Emerging Trends & Opportunities
- Top 5 trending topics in each niche
- Unexplored content gaps
- Seasonal opportunities

## Audience Insights
- Primary audience interests
- Engagement type (likes/comments/shares ratio)
- Time zone and activity patterns

## Strategic Recommendations
### This Week's Top 3 Content Ideas
1. [Idea] - Rationale based on data
2. [Idea] - Rationale based on data
3. [Idea] - Rationale based on data

### Niche Health Status
- Data Science/Tech: [status + growth %]
- Life & Self-Development: [status + growth %]
- Poetry/Quotes: [status + growth %]

## Technical Notes
- Content gaps: [what hasn't been covered]
- High-impact angles: [what resonates most]
- Platform optimization: [what works best where]

---

Use specific numbers from the analytics. Focus on actionable insights.
"""

    # Backend 1: Claude CLI
    import subprocess as _sp
    log("Calling claude -p ...")
    try:
        result = _sp.run(
            ["claude", "-p", prompt],
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        log(f"  claude -p failed (exit {result.returncode}), falling back to Ollama")
    except Exception as e:
        log(f"  claude -p error: {e}, falling back to Ollama")

    # Backend 2: Ollama
    log("Using Ollama for synthesis...")
    return synthesize_with_ollama(prompt)


def synthesize_with_ollama(prompt: str) -> str:
    """Synthesize brief using Ollama (gemma4:e4b)."""
    model = "gemma4:e4b"

    log(f"  Using {model} for synthesis...")
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=300,  # Increased timeout for complex synthesis
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "")
        else:
            raise RuntimeError(f"{model} failed: HTTP {response.status_code}")
    except Exception as e:
        raise RuntimeError(f"Ollama error: {e}. Ensure Ollama is running on localhost:11434 with {model}")


def save_brief(content: str) -> None:
    """Save knowledge base to file."""
    output_file = KB_DIR / "master_brief.md"
    output_file.write_text(content)
    log(f"✓ Saved knowledge base → {output_file}")


def main():
    """Main pipeline."""
    log("Building knowledge base…")

    log("Loading analytics data…")
    analytics = {
        "youtube": load_analytics("youtube"),
        "twitter": load_analytics("twitter"),
        "instagram": load_analytics("instagram"),
    }

    log("Loading ideas & trends…")
    ideas = load_ideas()

    log("Fetching Notion archive…")
    notion = fetch_notion_archive()

    log("Synthesizing knowledge base…")
    brief = synthesize_brief(analytics, ideas, notion)

    log("Saving brief…")
    save_brief(brief)

    log("✓ Knowledge base built successfully")


if __name__ == "__main__":
    main()
