#!/usr/bin/env python3
"""
Trend Pulse aggregator for multi-source trending topics.
Fetches from 20 free sources, classifies by creator niches.
Saves top 100 classified to data/ideas/trend_pulse_YYYY-MM-DD.json
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
import os

from _console import console, progress_bar

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
    """Classify trend using keyword matching."""
    return classify_trend(keyword, NICHE_KEYWORDS)


def scrape_trends(output_dir="data/ideas"):
    console.rule("[info]Trend Pulse Scraper — Niche Classification[/info]")

    with progress_bar() as progress:
        task = progress.add_task("Fetching top 100 trends...", total=1)

        try:
            result = subprocess.run(
                ["trend-pulse", "trending", "--sources", "google_trends,reddit,hackernews", "--count", "100"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                console.print(f"  [warn]Error running trend-pulse: {result.stderr[:100]}[/warn]")
                trends_data = {"merged": []}
            else:
                trends_data = json.loads(result.stdout)

            progress.advance(task)
        except Exception as e:
            console.print(f"  [warn]Error fetching trends: {str(e)[:100]}[/warn]")
            trends_data = {"merged": []}

    all_trends = trends_data.get("merged", [])
    niche_results = {niche: [] for niche in NICHE_KEYWORDS}
    unclassified = []

    with progress_bar() as progress:
        task = progress.add_task("Classifying trends...", total=len(all_trends))

        for trend in all_trends:
            niche = classify_trend_with_llm(trend.get("keyword", ""))
            if niche:
                niche_results[niche].append(trend)
            else:
                unclassified.append(trend)
            progress.advance(task)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_path = Path(output_dir) / f"trend_pulse_{date_str}.json"

    output = {
        "timestamp": trends_data.get("timestamp", datetime.now().isoformat()),
        "sources": trends_data.get("sources_ok", []),
        "total_trends": len(all_trends),
        "by_niche": niche_results,
        "unclassified": unclassified[:10],
    }

    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    console.print(f"\n[success]✓ Saved {out_path}[/success]")
    console.print(f"  [info]Sources: {', '.join(trends_data.get('sources_ok', []))}[/info]")
    console.print(f"  [info]Total trends: {len(all_trends)}[/info]")

    for niche, trends in niche_results.items():
        console.print(f"\n  [niche]{niche}[/niche]: {len(trends)} trends")
        for i, t in enumerate(trends[:3], 1):
            console.print(f"    {i}. [dim]{t.get('keyword')}[/dim] (score: {t.get('score', 0):.0f})")

    return output


if __name__ == "__main__":
    scrape_trends()
