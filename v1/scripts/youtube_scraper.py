#!/usr/bin/env python3
"""
YouTube Data API v3 scraper.
Searches trending in 3 niches (last 7 days).
Scores by engagement rate = (likes + comments) / views.
Saves top 10 to data/ideas/youtube_YYYY-MM-DD.json
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import googleapiclient.discovery
from dotenv import load_dotenv
from _console import console, progress_bar

load_dotenv()

SEARCH_QUERIES = {
    "data_science_tech": ["data science", "machine learning", "python tutorial"],
    "life_self_dev":     ["productivity tips", "habit building", "self improvement"],
    "poetry_quotes":     ["poetry reading", "motivational quotes", "creative writing"],
}


def get_youtube_client():
    api_key = os.getenv("GOOGLE_CONSOLE_API_KEY") or os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_CONSOLE_API_KEY not set in .env")
    return googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)


def search_videos(youtube, query, published_after):
    try:
        resp = youtube.search().list(
            q=query, part="snippet", type="video",
            publishedAfter=published_after, order="relevance",
            maxResults=10, regionCode="US",
        ).execute()
        return resp.get("items", [])
    except Exception as e:
        console.print(f"  [warn]Search error '{query}': {e}[/warn]")
        return []


def get_video_stats(youtube, video_id):
    try:
        resp = youtube.videos().list(id=video_id, part="statistics,snippet").execute()
        items = resp.get("items", [])
        if not items:
            return None
        stats = items[0]["statistics"]
        snippet = items[0]["snippet"]
        return {
            "video_id": video_id,
            "title": snippet["title"],
            "channel": snippet["channelTitle"],
            "published_at": snippet["publishedAt"],
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
        }
    except Exception:
        return None


def scrape_youtube(output_dir="data/ideas"):
    youtube = get_youtube_client()
    published_after = (datetime.now() - timedelta(days=7)).isoformat() + "Z"

    all_queries = [(niche, q) for niche, qs in SEARCH_QUERIES.items() for q in qs]
    results = {niche: [] for niche in SEARCH_QUERIES}

    console.rule("[info]YouTube Scraper[/info]")

    with progress_bar() as progress:
        search_task = progress.add_task("Searching queries", total=len(all_queries))
        video_ids_by_niche = {niche: [] for niche in SEARCH_QUERIES}

        for niche, query in all_queries:
            progress.update(search_task, description=f"Search: {query[:35]}")
            items = search_videos(youtube, query, published_after)
            for item in items:
                vid_id = item["id"].get("videoId")
                if vid_id:
                    video_ids_by_niche[niche].append(vid_id)
            progress.advance(search_task)

        # Deduplicate video IDs
        all_ids = list({vid for ids in video_ids_by_niche.values() for vid in ids})
        stats_task = progress.add_task("Fetching video stats", total=len(all_ids))

        stats_cache = {}
        for vid_id in all_ids:
            progress.update(stats_task, description=f"Stats: {vid_id}")
            stats = get_video_stats(youtube, vid_id)
            if stats:
                engagement = (stats["likes"] + stats["comments"]) / max(stats["views"], 1)
                stats_cache[vid_id] = {**stats, "engagement_rate": engagement,
                                       "url": f"https://youtu.be/{vid_id}"}
            progress.advance(stats_task)

    # Assign to niches and rank
    for niche, vid_ids in video_ids_by_niche.items():
        niche_videos = [stats_cache[v] for v in vid_ids if v in stats_cache]
        results[niche] = sorted(niche_videos, key=lambda x: x["engagement_rate"], reverse=True)[:10]

    # Save
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_path = Path(output_dir) / f"youtube_{date_str}.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    console.print(f"\n[success]✓ Saved {out_path}[/success]")
    for niche, vids in results.items():
        console.print(f"  [niche]{niche}[/niche]: {len(vids)} videos")
        for i, v in enumerate(vids[:3], 1):
            console.print(f"    {i}. [dim]{v['title'][:60]}[/dim] ({v['engagement_rate']*100:.2f}%)")

    return results


if __name__ == "__main__":
    scrape_youtube()
