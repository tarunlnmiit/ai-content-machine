#!/usr/bin/env python3
"""
Reddit RSS scraper for 9 subreddits (3 per niche).
Fetches from reddit.com/r/SUBREDDIT/.rss, no API key required.
Scores by title keyword match + recency decay.
Saves top 5 per niche to data/ideas/reddit_YYYY-MM-DD.json
"""

import feedparser
import json
import math
import os
from datetime import datetime
from pathlib import Path

import requests
from _console import console, progress_bar

SUBREDDITS = {
    "data_science_tech": [
        "datascience", "MachineLearning", "learnprogramming",
        "programming", "Python", "learnmachinelearning",
        "mlops", "analytics", "DataAnalysis", "dataengineering",
    ],
    "life_self_dev": [
        "selfimprovement", "productivity", "stoicism",
        "getmotivated", "DecidingToBeBetter",
        "psychology", "AcademicPsychology",
        "mentalhealth", "MentalHealthSupport",
        "LifeProTips", "LifeAdvice",
    ],
    "poetry_quotes": [
        "Poetry", "quotes", "WritingPrompts",
        "Poem", "OCPoetry",
    ],
}

KEYWORDS = {
    "data_science_tech": [
        "data", "machine learning", "python", "ai", "analysis", "statistics", "model",
        "mlops", "pipeline", "deployment", "analytics", "sql", "etl", "warehouse",
    ],
    "life_self_dev": [
        "habit", "motivation", "goal", "discipline", "growth", "mindset", "success",
        "psychology", "mental health", "anxiety", "burnout", "therapy",
        "life lesson", "advice", "wisdom", "emotional",
    ],
    "poetry_quotes": ["poem", "poetry", "quote", "verse", "inspiration", "metaphor", "wisdom"],
}


def calculate_recency_score(pub_date):
    try:
        from time import mktime
        pub_datetime = datetime.fromtimestamp(mktime(pub_date))
        age_hours = (datetime.now() - pub_datetime).total_seconds() / 3600
        decay_rate = 0.693 / (7 * 24)
        return max(0, math.exp(-decay_rate * age_hours))
    except Exception:
        return 0.5


def score_title(title, keywords, recency_score):
    keyword_matches = sum(1 for kw in keywords if kw.lower() in title.lower())
    return keyword_matches * 0.3 + recency_score


def fetch_subreddit_rss(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/.rss"
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 content-machine/1.0"},
            timeout=10,
        )
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        return feed.entries or []
    except Exception as e:
        console.print(f"  [warn]Error fetching r/{subreddit}: {e}[/warn]")
        return []


def scrape_reddit(output_dir="data/ideas"):
    all_subreddits = [(niche, sub) for niche, subs in SUBREDDITS.items() for sub in subs]
    results = {niche: [] for niche in SUBREDDITS}

    console.rule("[info]Reddit RSS Scraper[/info]")

    with progress_bar() as progress:
        task = progress.add_task("Fetching subreddits", total=len(all_subreddits))

        for niche, subreddit in all_subreddits:
            progress.update(task, description=f"r/{subreddit} [{niche[:12]}]")
            entries = fetch_subreddit_rss(subreddit)
            keywords = KEYWORDS[niche]

            for entry in entries:
                try:
                    recency = calculate_recency_score(entry.published_parsed)
                    score = score_title(entry.title, keywords, recency)
                    results[niche].append({
                        "title": entry.title,
                        "url": entry.link,
                        "subreddit": subreddit,
                        "published": entry.published,
                        "score": score,
                        "keyword_matches": sum(1 for kw in keywords if kw.lower() in entry.title.lower()),
                        "recency_score": recency,
                    })
                except Exception:
                    pass

            progress.advance(task)

    # Keep top 5 per niche
    for niche in results:
        results[niche] = sorted(results[niche], key=lambda x: x["score"], reverse=True)[:5]

    # Save
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_path = Path(output_dir) / f"reddit_{date_str}.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    console.print(f"\n[success]✓ Saved {out_path}[/success]")
    for niche, posts in results.items():
        console.print(f"  [niche]{niche}[/niche]: {len(posts)} posts")
        for i, p in enumerate(posts, 1):
            console.print(f"    {i}. [dim]{p['title'][:70]}[/dim] (score: {p['score']:.2f})")

    return results


if __name__ == "__main__":
    scrape_reddit()
