#!/usr/bin/env python3
"""
Collect weekly analytics: YouTube (Data API v3), Twitter (twitter_tweets.json),
Instagram (instagram_posts.json). Summarise with Ollama. Save weekly_insights.md.

Runs via cron every Sunday at 8 PM.
Twitter and Instagram data assumed refreshed by Composio/Apify before this runs.
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
from _console import console, progress_bar

REPO = Path(__file__).parent.parent
load_dotenv(REPO / ".env")

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma4:e2b"

YOUTUBE_CHANNELS = {
    "Breath of Data Science": os.getenv("YT_CHANNEL_ID_DS",       "UCxxxxDS"),
    "Breath of Life":         os.getenv("YT_CHANNEL_ID_LIFE",     "UCxxxxLife"),
    "Breath of Poetry":       os.getenv("YT_CHANNEL_ID_POETRY",   "UCxxxxPoetry"),
    "Breath of Relaxing":     os.getenv("YT_CHANNEL_ID_RELAXING", "UCxxxxRelax"),
}


# ── YouTube ───────────────────────────────────────────────────────────────────

def fetch_youtube_channel_stats(channel_id: str, api_key: str) -> dict | None:
    try:
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params={"part": "statistics,snippet", "id": channel_id, "key": api_key},
            timeout=10,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])
        if not items:
            return None
        stats = items[0]["statistics"]
        return {
            "subscribers":   int(stats.get("subscriberCount", 0)),
            "total_views":   int(stats.get("viewCount", 0)),
            "video_count":   int(stats.get("videoCount", 0)),
        }
    except Exception as e:
        console.print(f"  [warn]YouTube API error ({channel_id}): {e}[/warn]")
        return None


def fetch_youtube_recent_videos(channel_id: str, api_key: str, max_results: int = 5) -> list[dict]:
    try:
        # Get uploads playlist ID
        ch_resp = requests.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params={"part": "contentDetails", "id": channel_id, "key": api_key},
            timeout=10,
        )
        ch_resp.raise_for_status()
        items = ch_resp.json().get("items", [])
        if not items:
            return []
        uploads_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # Get recent video IDs from uploads playlist
        pl_resp = requests.get(
            "https://www.googleapis.com/youtube/v3/playlistItems",
            params={"part": "snippet", "playlistId": uploads_id,
                    "maxResults": max_results, "key": api_key},
            timeout=10,
        )
        pl_resp.raise_for_status()
        video_ids = [
            item["snippet"]["resourceId"]["videoId"]
            for item in pl_resp.json().get("items", [])
        ]
        if not video_ids:
            return []

        # Get stats for those videos
        v_resp = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={"part": "snippet,statistics", "id": ",".join(video_ids), "key": api_key},
            timeout=10,
        )
        v_resp.raise_for_status()
        videos = []
        for item in v_resp.json().get("items", []):
            s = item["statistics"]
            videos.append({
                "title":    item["snippet"]["title"],
                "views":    int(s.get("viewCount", 0)),
                "likes":    int(s.get("likeCount", 0)),
                "comments": int(s.get("commentCount", 0)),
                "published": item["snippet"]["publishedAt"][:10],
            })
        return videos
    except Exception as e:
        console.print(f"  [warn]YouTube recent videos error ({channel_id}): {e}[/warn]")
        return []


def collect_youtube(api_key: str) -> dict:
    results = {}
    for name, channel_id in YOUTUBE_CHANNELS.items():
        if channel_id.startswith("UCxxxx"):
            console.print(f"  [warn]YT channel ID not set for {name} — skipping[/warn]")
            continue
        stats  = fetch_youtube_channel_stats(channel_id, api_key)
        videos = fetch_youtube_recent_videos(channel_id, api_key)
        results[name] = {"stats": stats, "recent_videos": videos}
    return results


# ── Twitter ───────────────────────────────────────────────────────────────────

def collect_twitter() -> dict:
    path = REPO / "data" / "analytics" / "twitter_tweets.json"
    if not path.exists():
        return {"error": "twitter_tweets.json not found"}

    try:
        tweets = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse failed: {e}"}

    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    recent = []
    for t in tweets:
        try:
            created = datetime.strptime(t["createdAt"], "%a %b %d %H:%M:%S +0000 %Y").replace(tzinfo=timezone.utc)
            if created >= cutoff:
                recent.append(t)
        except Exception:
            continue

    if not recent:
        # Fall back to last 10 tweets regardless of date
        recent = tweets[:10] if tweets else []

    total_views    = sum(t.get("viewCount", 0)    for t in recent)
    total_likes    = sum(t.get("likeCount", 0)    for t in recent)
    total_retweets = sum(t.get("retweetCount", 0) for t in recent)
    total_replies  = sum(t.get("replyCount", 0)   for t in recent)

    top = sorted(recent, key=lambda t: t.get("viewCount", 0), reverse=True)[:3]

    return {
        "tweets_this_week": len(recent),
        "total_views":      total_views,
        "total_likes":      total_likes,
        "total_retweets":   total_retweets,
        "total_replies":    total_replies,
        "avg_views":        round(total_views / len(recent), 1) if recent else 0,
        "top_tweets": [
            {"text": t["text"][:120], "views": t.get("viewCount", 0),
             "likes": t.get("likeCount", 0), "url": t.get("url", "")}
            for t in top
        ],
    }


# ── Instagram ─────────────────────────────────────────────────────────────────

def collect_instagram() -> dict:
    path = REPO / "data" / "analytics" / "instagram_posts.json"
    if not path.exists():
        return {"error": "instagram_posts.json not found"}

    try:
        posts = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse failed: {e}"}

    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    recent = []
    for p in posts:
        try:
            ts = datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00"))
            if ts >= cutoff:
                recent.append(p)
        except Exception:
            continue

    if not recent:
        recent = posts[:5] if posts else []

    def engagement(p: dict) -> float:
        insights = p.get("insights", {})
        saves    = insights.get("saved", 0) if isinstance(insights, dict) else 0
        reach    = insights.get("reach", 1) if isinstance(insights, dict) else 1
        likes    = p.get("like_count", 0)
        comments = p.get("comments_count", 0)
        return (likes + comments + saves * 5) / max(reach, 1)

    top = sorted(recent, key=engagement, reverse=True)[:3]

    return {
        "posts_this_week": len(recent),
        "total_likes":     sum(p.get("like_count", 0)    for p in recent),
        "total_comments":  sum(p.get("comments_count", 0) for p in recent),
        "top_posts": [
            {
                "caption":  (p.get("caption") or "")[:100],
                "likes":    p.get("like_count", 0),
                "comments": p.get("comments_count", 0),
                "type":     p.get("media_type", ""),
                "url":      p.get("permalink", ""),
            }
            for p in top
        ],
    }


# ── Summary backends ──────────────────────────────────────────────────────────

def _make_summary_prompt(data: dict) -> str:
    return f"""You are a content analytics assistant. Given this week's platform data for a creator (data scientist, content creator), write a plain-English summary in 3–5 bullet points. Be specific. Name actual numbers. Flag what's working and what needs attention. No preamble.

Data:
{json.dumps(data, indent=2, default=str)[:4000]}

Summary:"""


def _summarise_with_ollama(prompt: str) -> str:
    resp = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=60,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Ollama HTTP {resp.status_code}")
    return resp.json().get("response", "").strip()


def summarise(data: dict) -> str:
    prompt = _make_summary_prompt(data)
    try:
        result = _summarise_with_ollama(prompt)
        console.print("  [success]Summary via Ollama[/success]")
        return result
    except Exception as e:
        console.print(f"  [warn]Ollama failed: {e}[/warn]")
    return "Summary unavailable — Ollama failed."


# ── Save ──────────────────────────────────────────────────────────────────────

def save_report(youtube: dict, twitter: dict, instagram: dict, summary: str) -> Path:
    now  = datetime.now()
    week = now.strftime("%Y-W%W")

    lines = [
        f"# Weekly Analytics — {week}",
        f"*Generated: {now.strftime('%Y-%m-%d %H:%M')}*",
        "",
        "## Summary",
        summary,
        "",
        "---",
        "",
        "## YouTube",
    ]

    for channel, data in youtube.items():
        lines.append(f"\n### {channel}")
        stats = data.get("stats")
        if stats:
            lines.append(f"- Subscribers: {stats['subscribers']:,}")
            lines.append(f"- Total views: {stats['total_views']:,}")
            lines.append(f"- Videos: {stats['video_count']:,}")
        videos = data.get("recent_videos", [])
        if videos:
            lines.append("\nRecent videos:")
            for v in videos:
                lines.append(f"  - [{v['published']}] {v['title']} — {v['views']:,} views, {v['likes']:,} likes")

    lines += [
        "",
        "---",
        "",
        "## Twitter / X",
        f"- Tweets this week: {twitter.get('tweets_this_week', 'N/A')}",
        f"- Total views: {twitter.get('total_views', 'N/A'):,}" if isinstance(twitter.get('total_views'), int) else f"- Total views: N/A",
        f"- Likes: {twitter.get('total_likes', 'N/A')}",
        f"- Retweets: {twitter.get('total_retweets', 'N/A')}",
        f"- Avg views/tweet: {twitter.get('avg_views', 'N/A')}",
    ]
    if twitter.get("top_tweets"):
        lines.append("\nTop tweets:")
        for t in twitter["top_tweets"]:
            lines.append(f"  - {t['views']:,} views | {t['text'][:80]}…")

    lines += [
        "",
        "---",
        "",
        "## Instagram",
        f"- Posts this week: {instagram.get('posts_this_week', 'N/A')}",
        f"- Total likes: {instagram.get('total_likes', 'N/A')}",
        f"- Total comments: {instagram.get('total_comments', 'N/A')}",
    ]
    if instagram.get("top_posts"):
        lines.append("\nTop posts:")
        for p in instagram["top_posts"]:
            lines.append(f"  - {p['likes']} likes, {p['comments']} comments | {p['caption'][:80]}")

    out = REPO / "data" / "analytics" / "weekly_insights.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    console.rule("[info]Analytics Collector[/info]")

    with progress_bar() as progress:
        yt_task = progress.add_task("YouTube", total=len(YOUTUBE_CHANNELS))
        tw_task = progress.add_task("Twitter", total=1)
        ig_task = progress.add_task("Instagram", total=1)
        ai_task = progress.add_task("Ollama summary", total=1)

        api_key = os.getenv("GOOGLE_CONSOLE_API_KEY")
        if not api_key:
            console.print("[warn]GOOGLE_CONSOLE_API_KEY not set — skipping YouTube[/warn]")
            youtube = {}
        else:
            youtube = collect_youtube(api_key)
        progress.update(yt_task, completed=len(YOUTUBE_CHANNELS))

        twitter = collect_twitter()
        progress.update(tw_task, completed=1)

        instagram = collect_instagram()
        progress.update(ig_task, completed=1)

        combined = {"youtube": youtube, "twitter": twitter, "instagram": instagram}
        summary  = summarise(combined)
        progress.update(ai_task, completed=1)

    out = save_report(youtube, twitter, instagram, summary)

    console.print(f"\n[success]✓ Saved: {out.relative_to(REPO)}[/success]")
    console.print("\n[bold]Summary:[/bold]")
    console.print(summary)


if __name__ == "__main__":
    main()
