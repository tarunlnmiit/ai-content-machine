#!/usr/bin/env python3
"""Find best 60-sec moment in video based on content relevance to blog."""

import json
import argparse
from pathlib import Path
from collections import defaultdict

REPO = Path(__file__).parent.parent

def extract_key_phrases(text: str, top_n: int = 15) -> list[str]:
    """Extract important phrases from text. Requires: pip install nltk"""
    try:
        import nltk
        from nltk.tokenize import sent_tokenize
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)

        sentences = sent_tokenize(text.lower())
        # Simple: take sentences with 8-15 words (substantive)
        phrases = [s.strip() for s in sentences if 8 <= len(s.split()) <= 20]
        return phrases[:top_n]
    except ImportError:
        print("Warning: nltk not installed. Using simple word extraction.")
        words = text.lower().split()
        return list(set(w for w in words if len(w) > 5))[:top_n]

def transcribe_video(video_path: str) -> dict:
    """Transcribe video using Whisper. Returns {timestamp: text, ...}"""
    try:
        import subprocess
        import json as json_module
        import tempfile
        import os

        # Use temp dir for output instead of stdout (more reliable)
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                ["whisper", str(video_path), "--output_format", "json", "--output_dir", tmpdir],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print("Whisper error:", result.stderr)
                return {}

            # Find the JSON output file
            json_file = None
            for f in os.listdir(tmpdir):
                if f.endswith(".json"):
                    json_file = os.path.join(tmpdir, f)
                    break

            if not json_file:
                print("Error: Whisper did not produce JSON output")
                print("stderr:", result.stderr)
                return {}

            # Parse JSON output
            with open(json_file) as f:
                whisper_output = json_module.load(f)

            segments = whisper_output.get("segments", [])

            transcript = {}
            for seg in segments:
                start = int(seg["start"])
                end = int(seg["end"])
                text = seg["text"]
                # Store by second
                for sec in range(start, end + 1):
                    transcript[sec] = transcript.get(sec, "") + " " + text
            return transcript

    except FileNotFoundError:
        print("Error: whisper not found. Install: pip install openai-whisper")
        return {}

def score_window(window_text: str, key_phrases: list[str]) -> float:
    """Score 60-sec window by keyword density."""
    window_lower = window_text.lower()
    matches = sum(1 for phrase in key_phrases if phrase in window_lower)
    return matches / max(len(key_phrases), 1)

def find_best_moment(blog_path: str, video_path: str, window_size: int = 60, transcript: dict | None = None) -> dict:
    """Find best windows in video matching blog content. Reuse transcript to avoid double transcription."""

    # Read blog
    blog_text = Path(blog_path).read_text()
    key_phrases = extract_key_phrases(blog_text, top_n=15)

    print(f"Key themes from blog: {', '.join(key_phrases[:5])}")

    # Transcribe video if not provided
    if transcript is None:
        print("Transcribing video...")
        transcript = transcribe_video(video_path)

    if not transcript:
        print("Error: Could not transcribe video.")
        return {}

    # Score all windows
    max_time = max(transcript.keys())
    windows = defaultdict(float)

    for start in range(0, max(0, max_time - window_size), 10):  # 10-sec steps
        window_text = " ".join(transcript.get(t, "") for t in range(start, start + window_size))
        score = score_window(window_text, key_phrases)
        windows[start] = score

    # Get top 3
    top_windows = sorted(windows.items(), key=lambda x: x[1], reverse=True)[:3]

    return {
        "key_phrases": key_phrases,
        "top_moments": [
            {
                "start_time": f"{int(start // 60):02d}:{int(start % 60):02d}",
                "start_seconds": int(start),
                "relevance_score": round(score, 2),
            }
            for start, score in top_windows
        ],
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find best moment in video for reel based on blog content.")
    parser.add_argument("--blog", required=True, help="Path to blog markdown file")
    parser.add_argument("--video", required=True, help="Path to video file")
    parser.add_argument("--window-size", type=int, default=60, help="Window size in seconds (default 60)")
    parser.add_argument("--top-n", type=int, default=3, help="Return top N moments (default 3)")
    args = parser.parse_args()

    if not Path(args.blog).exists():
        print(f"Error: Blog not found: {args.blog}")
        exit(1)

    if not Path(args.video).exists():
        print(f"Error: Video not found: {args.video}")
        exit(1)

    result = find_best_moment(args.blog, args.video, window_size=args.window_size)

    if result:
        print(f"\nBest moments for {args.window_size}s clips:")
        for i, moment in enumerate(result["top_moments"][:args.top_n], 1):
            print(f"\n#{i} — {moment['start_time']} (score: {moment['relevance_score']})")
            print(f"   Command: python3 scripts/create_vertical_reels.py --start {moment['start_time']} --duration {args.window_size}")
    else:
        print("No results. Check whisper installation and video file.")
