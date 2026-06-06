#!/usr/bin/env python3
"""
Fetch stock video clips from Pexels/Pixabay based on blog content themes.
Auto-download clips matching blog keywords → organized by slug + niche.

Usage:
  python3 scripts/fetch_videos.py --input content/blogs/2026-04-30-data-science-tech-*.md --niche ds
  python3 scripts/fetch_videos.py --input content/blogs/2026-05-03-life-self-dev-*.md --niche life
  python3 scripts/fetch_videos.py --input content/blogs/2026-05-03-poetry-quotes-*.md --niche poetry
"""

import argparse
import os
import json
import re
import requests
import subprocess
from pathlib import Path
from typing import Optional

# Load .env file
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    with open(env_file, "r") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                value = value.strip('"\'')
                os.environ[key] = value

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")

NICHE_KEYWORDS = {
    "ds": ["code", "data", "python", "algorithm", "machine learning", "analysis", "database"],
    "life": ["nature", "journey", "growth", "morning", "outdoor", "lifestyle", "wellness"],
    "poetry": ["abstract", "artistic", "nature", "sunset", "water", "sky", "contemplative"],
}

def extract_broll_cues_from_script(script_path: str) -> list:
    """Parse [BROLL: description] markers from YouTube script file."""
    with open(script_path, "r") as f:
        content = f.read()

    cues = []
    pattern = r'\[BROLL:\s*([^\]]+)\]'
    for match in re.finditer(pattern, content):
        cue_text = match.group(1).strip()
        cues.append(cue_text)

    return cues

def extract_keywords_from_blog(blog_path: str, niche: str) -> list:
    """Generate stock video search terms from blog content using Claude."""
    with open(blog_path, "r") as f:
        content = f.read()

    niche_context = {
        "ds": "data science/tech - should search for code, technical visuals, data analysis, programming concepts",
        "life": "life & self-development - should search for lifestyle visuals, nature, personal growth, wellness themes",
        "poetry": "poetry & quotes - should search for artistic, contemplative, emotional visuals that inspire reflection"
    }

    prompt = f"""Read this blog post and generate 4-5 specific stock video search terms optimized for B-roll in a {niche_context.get(niche, 'general')} video.

Return ONLY a JSON array of search terms (strings), nothing else. Example: ["morning routine", "coffee cup", "workspace", "nature walk"]

Blog content:
{content[:2000]}"""

    try:
        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).parent))
        from lib.claude_cli import call_claude
        response_text = call_claude(prompt, cache=True, timeout=30).strip()

        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            search_terms = json.loads(json_match.group())
            return search_terms if isinstance(search_terms, list) else []

        return NICHE_KEYWORDS.get(niche, [])

    except Exception as e:
        print(f"Claude search term generation failed: {e}, using fallback niche keywords")
        return NICHE_KEYWORDS.get(niche, [])

def fetch_pexels_videos(query: str, per_page: int = 3) -> list:
    """Fetch videos from Pexels API."""
    if not PEXELS_API_KEY:
        return []

    headers = {"Authorization": PEXELS_API_KEY}
    url = "https://api.pexels.com/v1/videos/search"
    params = {"query": query, "per_page": per_page, "orientation": "landscape"}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        videos = []
        for vid in data.get("videos", []):
            video_files = vid.get("video_files", [])
            landscape_files = [
                f for f in video_files
                if f.get("width", 0) >= f.get("height", 1) and f.get("width", 0) > 0
            ]
            if not landscape_files:
                continue
            best = min(landscape_files, key=lambda x: abs(x.get("height", 1080) - 1080))
            videos.append({
                "url": best["link"],
                "title": vid.get("url", ""),
                "duration": vid.get("duration", 0),
                "source": "pexels"
            })
        return videos
    except Exception as e:
        print(f"Pexels error: {e}")
        return []

def fetch_pixabay_videos(query: str, per_page: int = 3) -> list:
    """Fetch videos from Pixabay API."""
    if not PIXABAY_API_KEY:
        return []

    url = "https://pixabay.com/api/videos/"
    # Pixabay requires per_page to be minimum 3
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "per_page": max(3, per_page),
        "order": "popular"
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        videos = []
        for vid in data.get("hits", []):
            video_urls = vid.get("videos", {})
            best_url = None

            for size in ["large", "medium", "small", "tiny"]:
                v = video_urls.get(size, {})
                if not v.get("url"):
                    continue
                w, h = v.get("width", 0), v.get("height", 1)
                if w < h:  # skip portrait
                    continue
                best_url = v["url"]
                break

            if best_url:
                videos.append({
                    "url": best_url,
                    "title": f"Pixabay: {vid.get('tags', query)}",
                    "duration": vid["duration"],
                    "source": "pixabay"
                })
        return videos
    except Exception as e:
        print(f"Pixabay error: {e}")
        return []

def download_video(url: str, output_path: str) -> bool:
    """Download video file."""
    try:
        resp = requests.get(url, timeout=30, stream=True)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Download error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Auto-fetch stock videos for blog or YouTube script")
    parser.add_argument("--input", help="Blog markdown file")
    parser.add_argument("--script", help="YouTube script file (uses [BROLL:] cues instead of blog)")
    parser.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    parser.add_argument("--source", default="stock", choices=["stock", "ai"],
                        help="stock = Pexels/Pixabay (default), ai = muapi.ai generative video")
    parser.add_argument("--model", default="seedance-lite-t2v",
                        choices=["seedance-lite-t2v", "seedance-pro-t2v", "kling-v2.1-master-t2v"],
                        help="muapi.ai model (only used with --source ai)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would download, don't download")
    args = parser.parse_args()

    if not args.input and not args.script:
        print("Error: provide either --input (blog) or --script (YouTube script)")
        return

    # Delegate to AI generator when --source ai
    if args.source == "ai":
        if not args.script:
            print("Error: --source ai requires --script (needs [BROLL:] cues)")
            return
        import subprocess
        cmd = [
            "python3", str(Path(__file__).parent / "generate_video_ai.py"),
            "--script", args.script,
            "--niche", args.niche,
            "--model", args.model,
        ]
        if args.dry_run:
            cmd.append("--dry-run")
        subprocess.run(cmd, check=True)
        return

    if args.script:
        if not os.path.exists(args.script):
            print(f"Error: {args.script} not found")
            return
        script_stem = Path(args.script).stem
        search_terms = extract_broll_cues_from_script(args.script)
        output_dir = Path(f"assets/videos/{script_stem}")
        use_script = True
    else:
        if not os.path.exists(args.input):
            print(f"Error: {args.input} not found")
            return
        script_stem = Path(args.input).stem
        search_terms = extract_keywords_from_blog(args.input, args.niche)
        output_dir = Path(f"assets/videos/{script_stem}")
        use_script = False

    output_dir.mkdir(parents=True, exist_ok=True)

    all_videos = []
    video_map = {}

    source_label = "YouTube script" if use_script else "blog"
    print(f"Fetching videos for: {script_stem} ({source_label})")
    print(f"Search terms/B-roll cues: {search_terms}")

    for cue_idx, term in enumerate(search_terms):
        print(f"\n  [{cue_idx}] Searching '{term}'...")

        pexels_vids = fetch_pexels_videos(term, per_page=4)
        pixabay_vids = fetch_pixabay_videos(term, per_page=2)

        if pexels_vids:
            print(f"    [Pexels] {len(pexels_vids)} found")
        if pixabay_vids:
            print(f"    [Pixabay] {len(pixabay_vids)} found")

        videos = pexels_vids + pixabay_vids
        all_videos.extend(videos)

        for i, vid in enumerate(videos[:6]):
            idx = len(video_map)
            filename = f"{script_stem}_clip_{idx:02d}.mp4"
            filepath = output_dir / filename

            print(f"    [{idx}] {vid['source'].upper()} — {vid.get('duration', 0)}s")

            entry = {
                "source": vid["source"],
                "search_term": term,
                "duration": vid.get("duration", 0),
                "url": vid["url"],
                "downloaded": False
            }
            if use_script:
                entry["section_cue"] = cue_idx
            video_map[filename] = entry

            if not args.dry_run:
                if download_video(vid["url"], str(filepath)):
                    video_map[filename]["downloaded"] = True
                    print(f"       ✓ Downloaded → {filename}")
                else:
                    print(f"       ✗ Failed → {filename}")

    map_file = output_dir / "VIDEO_MAP.json"
    with open(map_file, "w") as f:
        json.dump(video_map, f, indent=2)

    print(f"\nVideo map saved → {map_file}")
    print(f"Total clips: {len(video_map)} ({sum(1 for v in video_map.values() if v['downloaded'])} downloaded)")
    print(f"Output dir: {output_dir}")

if __name__ == "__main__":
    main()
