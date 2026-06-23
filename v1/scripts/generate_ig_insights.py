#!/usr/bin/env python3
"""
Analyse instagram_posts.json → data/kb/ig_insights.json
Uses engagement metrics directly — no image analysis needed.
"""

import json
from pathlib import Path
from collections import defaultdict

REPO = Path(__file__).parent.parent
POSTS_FILE = REPO / "data/analytics/instagram_posts.json"
OUT_FILE = REPO / "data/kb/ig_insights.json"

FORMAT_MAP = {
    "VIDEO": "reel",
    "CAROUSEL_ALBUM": "carousel",
    "IMAGE": "single-image",
}

ENGAGEMENT_WEIGHTS = {
    "saved": 3,      # saves = strongest signal (content worth keeping)
    "shares": 2,
    "comments": 2,
    "likes": 1,
}


def engagement_score(insights: dict) -> float:
    score = sum(insights.get(k, 0) * w for k, w in ENGAGEMENT_WEIGHTS.items())
    reach = insights.get("reach", 1) or 1
    return score / reach  # normalise by reach


def analyse(posts: list) -> dict:
    by_format = defaultdict(list)
    for p in posts:
        fmt = FORMAT_MAP.get(p.get("media_type", ""), "unknown")
        ins = p.get("insights", {})
        by_format[fmt].append({
            "post_id": p.get("id"),
            "permalink": p.get("permalink"),
            "timestamp": p.get("timestamp"),
            "reach": ins.get("reach", 0),
            "saves": ins.get("saved", 0),
            "likes": ins.get("likes", 0),
            "comments": ins.get("comments", 0),
            "shares": ins.get("shares", 0),
            "views": ins.get("views", 0),
            "avg_watch_time_ms": ins.get("ig_reels_avg_watch_time", 0),
            "engagement_score": engagement_score(ins),
        })

    format_summary = {}
    for fmt, items in by_format.items():
        count = len(items)
        avg_reach = sum(i["reach"] for i in items) / count
        avg_saves = sum(i["saves"] for i in items) / count
        avg_likes = sum(i["likes"] for i in items) / count
        avg_shares = sum(i["shares"] for i in items) / count
        avg_comments = sum(i["comments"] for i in items) / count
        avg_eng = sum(i["engagement_score"] for i in items) / count

        top3 = sorted(items, key=lambda x: x["engagement_score"], reverse=True)[:3]

        format_summary[fmt] = {
            "post_count": count,
            "avg_reach": round(avg_reach, 1),
            "avg_saves": round(avg_saves, 2),
            "avg_likes": round(avg_likes, 1),
            "avg_shares": round(avg_shares, 2),
            "avg_comments": round(avg_comments, 2),
            "avg_engagement_score": round(avg_eng, 4),
            "top_posts": [
                {"permalink": p["permalink"], "saves": p["saves"],
                 "likes": p["likes"], "reach": p["reach"],
                 "engagement_score": round(p["engagement_score"], 4)}
                for p in top3
            ],
        }

    # Overall winner by engagement_score
    ranked = sorted(format_summary.items(), key=lambda x: x[1]["avg_engagement_score"], reverse=True)
    best_format = ranked[0][0]

    # Reel-specific: avg watch time
    reel_watch = None
    if "reel" in by_format:
        watch_times = [i["avg_watch_time_ms"] for i in by_format["reel"] if i["avg_watch_time_ms"] > 0]
        reel_watch = round(sum(watch_times) / len(watch_times) / 1000, 1) if watch_times else None

    # Recommendation logic for repurposing_agent
    def recommend(niche: str) -> dict:
        if niche == "poetry_quotes":
            # poetry → high saves expected on single image (quote cards) + reels
            img_eng = format_summary.get("single-image", {}).get("avg_engagement_score", 0)
            reel_eng = format_summary.get("reel", {}).get("avg_engagement_score", 0)
            primary = "single-image" if img_eng >= reel_eng else "reel"
            return {"primary": primary, "secondary": "reel" if primary == "single-image" else "single-image"}
        elif niche == "data_science_tech":
            # DS → carousels for educational content
            return {"primary": "carousel", "secondary": "reel"}
        else:
            # life_self_dev → follow overall engagement winner
            return {"primary": best_format, "secondary": ranked[1][0] if len(ranked) > 1 else best_format}

    return {
        "generated_from": str(POSTS_FILE.relative_to(REPO)),
        "total_posts_analysed": len(posts),
        "format_breakdown": {fmt: cnt for fmt, items in by_format.items() for cnt in [len(items)]},
        "best_format_overall": best_format,
        "best_format_rationale": f"Highest save-weighted engagement score ({ranked[0][1]['avg_engagement_score']:.4f}) vs "
                                  + ", ".join(f"{f}: {s['avg_engagement_score']:.4f}" for f, s in ranked[1:]),
        "reel_avg_watch_time_seconds": reel_watch,
        "format_stats": format_summary,
        "niche_recommendations": {
            "data_science_tech": recommend("data_science_tech"),
            "life_self_dev": recommend("life_self_dev"),
            "poetry_quotes": recommend("poetry_quotes"),
        },
        "repurposing_agent_instruction": (
            f"Default to '{best_format}' format unless niche-specific override applies. "
            "See niche_recommendations for per-niche guidance. "
            "Carousels perform best for educational/step-by-step content. "
            "Single-image suits quote/poetry posts. "
            "Reels suit narrative or transformation arc content."
        ),
    }


def main():
    posts = json.loads(POSTS_FILE.read_text(encoding="utf-8"))
    insights = analyse(posts)
    OUT_FILE.write_text(json.dumps(insights, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved: {OUT_FILE.relative_to(REPO)}")
    print(f"Best format overall: {insights['best_format_overall']}")
    print(f"Rationale: {insights['best_format_rationale']}")
    print("\nNiche recommendations:")
    for niche, rec in insights["niche_recommendations"].items():
        print(f"  {niche}: {rec['primary']} (fallback: {rec['secondary']})")


if __name__ == "__main__":
    main()
