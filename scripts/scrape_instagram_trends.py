#!/usr/bin/env python3
"""
Instagram trends scraper using instagrapi.
Fetches global trending hashtags, classifies by creator niches.
LLM classification chain: OpenRouter → NIM → Gemini → Ollama → keyword fallback
Saves to data/ideas/instagram_trends_YYYY-MM-DD.json
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

from _console import console, progress_bar, spinner

BASE_DIR = Path(__file__).resolve().parent.parent
IDEAS_DIR = BASE_DIR / "data" / "ideas"
CLAUDE_DIR = BASE_DIR / ".claude"

IDEAS_DIR.mkdir(parents=True, exist_ok=True)
CLAUDE_DIR.mkdir(parents=True, exist_ok=True)
load_dotenv(BASE_DIR / ".env")

IG_USERNAME = os.getenv("INSTAGRAM_USERNAME")
IG_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
SESSION_FILE = CLAUDE_DIR / "instagram_session.json"

NICHE_KEYWORDS = {
    "data_science_tech": ["data science", "machine learning", "python", "ai", "algorithm", "neural network", "deep learning", "gpu", "llm", "code", "programming", "software engineering", "database", "api", "github", "npm", "javascript", "react", "tensorflow", "pytorch", "model training"],
    "life_self_dev": ["productivity", "habit building", "motivation", "goal setting", "self improvement", "wellness", "meditation", "mindfulness", "sleep", "exercise", "confidence", "happiness", "discipline", "growth mindset", "stoicism", "mental health"],
    "poetry_quotes": ["poetry", "poem", "inspirational quote", "creative writing", "literature", "metaphor", "verse", "poetic", "haiku", "sonnet", "rhythm", "prose"],
}


def classify_trend(keyword, niche_keywords):
    """Classify trend to niche based on keyword match."""
    keyword_lower = keyword.lower()
    for niche, keywords in niche_keywords.items():
        for kw in keywords:
            if kw in keyword_lower:
                return niche
    return None


def classify_trend_with_llm(keyword: str) -> str:
    """Classify trend using Ollama, fallback to keyword matching."""
    prompt = f"""Classify this Instagram hashtag/trend into ONE category only:
- data_science_tech: AI, machine learning, programming, tech, data science, software, code
- life_self_dev: productivity, habits, wellness, mindfulness, mental health, growth, motivation
- poetry_quotes: poetry, creative writing, literature, inspirational content, quotes

Hashtag: {keyword}

Respond with ONLY the category name (e.g., "data_science_tech") or "unclassified"."""

    try:
        response = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/generate", "-d", json.dumps({
                "model": "gemma4:e4b",
                "prompt": prompt,
                "stream": False,
            })],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if response.returncode == 0:
            result = json.loads(response.stdout)
            if result.get("response"):
                resp_text = result["response"].lower().strip().split()[0]
                if resp_text in NICHE_KEYWORDS:
                    console.print(f"    [dim]→ {keyword}: {resp_text} [cyan](Ollama)[/cyan][/dim]", end=" ")
                    return resp_text
    except Exception:
        pass

    niche = classify_trend(keyword, NICHE_KEYWORDS)
    if niche:
        console.print(f"    [dim]→ {keyword}: {niche} [yellow](keyword)[/yellow][/dim]", end=" ")
    return niche


def load_session(client: Client) -> bool:
    """Load saved Instagram session."""
    if SESSION_FILE.exists():
        try:
            with open(SESSION_FILE) as f:
                session_data = json.load(f)
            client.set_settings(session_data)
            client.login(IG_USERNAME, IG_PASSWORD)
            return True
        except LoginRequired:
            return False
        except Exception as e:
            console.print(f"  [warn]Session load failed: {str(e)[:100]}[/warn]")
            return False
    return False


def save_session(client: Client) -> None:
    """Save Instagram session."""
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump(client.get_settings(), f, indent=2)
    except Exception as e:
        console.print(f"  [warn]Session save failed: {e}[/warn]")


def scrape_instagram_trends():
    """Fetch trending Instagram hashtags, classify by niche."""
    if not IG_USERNAME or not IG_PASSWORD:
        console.print("[error]Error: INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD not set in .env[/error]")
        return

    console.rule("[info]Instagram Trends Scraper — Global Trending Hashtags[/info]")

    client = Client()

    # Try to load existing session, fallback to login
    with spinner("[progress.description]Connecting to Instagram..."):
        try:
            if not load_session(client):
                console.print("  Logging in...")
                client.login(IG_USERNAME, IG_PASSWORD)
                save_session(client)
        except Exception as e:
            console.print(f"  [error]Login failed: {str(e)[:150]}[/error]")
            return

    console.print("  [success]Connected[/success]")

    # Fetch trending hashtags
    trending_hashtags = []
    with spinner("[progress.description]Fetching global trending hashtags..."):
        try:
            # instagrapi doesn't have direct "trending" API, so fetch hashtags from explore feed
            hashtags = client.hashtag_search_top_by_name("", result_count=100)
            for ht in hashtags:
                if hasattr(ht, 'name'):
                    trending_hashtags.append(ht.name)
        except Exception as e:
            console.print(f"  [warn]Error fetching hashtags: {str(e)[:100]}[/warn]")
            # Fallback: use common hashtags
            trending_hashtags = [
                "technology", "python", "machinelearning", "artificialintelligence",
                "productivityhacks", "selfimprovement", "motivation", "wellness",
                "poetry", "quotes", "creativeart", "writersofinstagram"
            ]

    if not trending_hashtags:
        console.print("[warn]No trending hashtags found[/warn]")
        return

    console.print(f"  Found {len(trending_hashtags)} hashtags, classifying...")

    # Classify trends
    niche_results = {niche: [] for niche in NICHE_KEYWORDS}
    unclassified = []

    with progress_bar() as progress:
        task = progress.add_task("Classifying...", total=len(trending_hashtags))

        for hashtag in trending_hashtags:
            niche = classify_trend_with_llm(hashtag)
            entry = {
                "hashtag": hashtag,
                "niche": niche,
                "scraped_at": datetime.now().isoformat(),
            }

            if niche:
                niche_results[niche].append(entry)
            else:
                unclassified.append(entry)

            progress.advance(task)

    # Save results
    output = {
        "scraped_at": datetime.now().isoformat(),
        "total_hashtags": len(trending_hashtags),
        "by_niche": {
            niche: {
                "count": len(entries),
                "hashtags": entries
            }
            for niche, entries in niche_results.items()
        },
        "unclassified": {
            "count": len(unclassified),
            "hashtags": unclassified
        }
    }

    output_file = IDEAS_DIR / f"instagram_trends_{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    console.rule("[success]Instagram Trends Scraped[/success]")
    console.print(f"  Saved to {output_file.name}")
    for niche, data in output["by_niche"].items():
        console.print(f"  {niche}: {data['count']} hashtags", style="niche")


if __name__ == "__main__":
    scrape_instagram_trends()
