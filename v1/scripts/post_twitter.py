#!/usr/bin/env python3
"""
Post a Twitter/X thread via OAuth 1.0a (tweepy).
Credentials: X_CONSUMER_KEY, X_CONSUMER_KEY_SECRET,
             X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET from .env

Usage (standalone):
    python3 scripts/post_twitter.py --thread-file content/derivatives/{slug}/twitter_thread.txt
    python3 scripts/post_twitter.py --tweets "Tweet 1" "Tweet 2" "Tweet 3"

Called by scheduler.py with a list of tweet strings.
"""

import argparse
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import tweepy
from dotenv import load_dotenv

REPO = Path(__file__).parent.parent
DB_PATH = REPO / "data" / "scheduling.db"
load_dotenv(REPO / ".env")


def get_client() -> tweepy.Client:
    consumer_key = os.getenv("X_CONSUMER_KEY")
    consumer_secret = os.getenv("X_CONSUMER_KEY_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

    missing = [k for k, v in {
        "X_CONSUMER_KEY": consumer_key,
        "X_CONSUMER_KEY_SECRET": consumer_secret,
        "X_ACCESS_TOKEN": access_token,
        "X_ACCESS_TOKEN_SECRET": access_token_secret,
    }.items() if not v]

    if missing:
        sys.exit(f"Missing env vars: {', '.join(missing)}")

    return tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )


def parse_thread_file(path: Path) -> list[str]:
    """Split twitter_thread.txt on blank lines — each block is one tweet."""
    text = path.read_text(encoding="utf-8").strip()
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    return blocks


def post_thread(tweets: list[str], db_post_id: int | None = None, slug: str | None = None) -> list[str]:
    """
    Post tweets in sequence, each replying to the previous.
    Returns list of posted tweet IDs.
    Updates scheduling.db if db_post_id provided.
    """
    if not tweets:
        sys.exit("No tweets to post.")

    client = get_client()
    posted_ids = []
    reply_to = None

    for i, text in enumerate(tweets):
        if len(text) > 280:
            print(f"  Warning: tweet {i+1} is {len(text)} chars — truncating to 280")
            text = text[:277] + "..."

        try:
            if reply_to:
                response = client.create_tweet(text=text, in_reply_to_tweet_id=reply_to, user_auth=True)
            else:
                response = client.create_tweet(text=text, user_auth=True)

            tweet_id = str(response.data["id"])
            posted_ids.append(tweet_id)
            reply_to = tweet_id
            print(f"  Posted tweet {i+1}/{len(tweets)}: {tweet_id}")

            if i < len(tweets) - 1:
                time.sleep(1.5)  # avoid rate limit between thread tweets

        except tweepy.TweepyException as e:
            print(f"  Error posting tweet {i+1}: {e}", file=sys.stderr)
            _log_failure(db_post_id, str(e))
            raise

    _log_success(db_post_id, posted_ids, slug)
    return posted_ids


def _log_success(db_post_id: int | None, tweet_ids: list[str], slug: str | None):
    if db_post_id is None or not DB_PATH.exists():
        return
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE posts SET status='posted', posted_at=?, metadata_json=? WHERE id=?",
        (
            datetime.now(timezone.utc).isoformat(),
            json.dumps({"tweet_ids": tweet_ids, "slug": slug}),
            db_post_id,
        ),
    )
    conn.commit()
    conn.close()


def _log_failure(db_post_id: int | None, error: str):
    if db_post_id is None or not DB_PATH.exists():
        return
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE posts SET status='failed', posted_at=?, metadata_json=? WHERE id=?",
        (
            datetime.now(timezone.utc).isoformat(),
            json.dumps({"error": error}),
            db_post_id,
        ),
    )
    conn.commit()
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Post a Twitter/X thread.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--thread-file", help="Path to twitter_thread.txt")
    group.add_argument("--tweets", nargs="+", help="Tweet strings (one per argument)")
    parser.add_argument("--dry-run", action="store_true", help="Print tweets without posting")
    args = parser.parse_args()

    if args.thread_file:
        path = Path(args.thread_file)
        if not path.is_absolute():
            path = REPO / path
        tweets = parse_thread_file(path)
    else:
        tweets = args.tweets

    print(f"Thread: {len(tweets)} tweets")
    for i, t in enumerate(tweets):
        print(f"  [{i+1}] {t[:80]}{'...' if len(t) > 80 else ''}")

    if args.dry_run:
        print("\nDry run — nothing posted.")
        return

    ids = post_thread(tweets)
    print(f"\nPosted {len(ids)} tweets. First ID: {ids[0]}")
    print(f"Thread URL: https://twitter.com/i/web/status/{ids[0]}")


if __name__ == "__main__":
    main()
