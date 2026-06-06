#!/Users/tarungupta/miniconda3/envs/content_engine_env/bin/python3.14
"""
publish_medium.py — Publish a Markdown blog post to Medium.

USAGE:
    python3 scripts/publish_medium.py --input content/blogs/my-post.md
    python3 scripts/publish_medium.py --input content/blogs/my-post.md --canonical-url https://mysite.com/my-post
    python3 scripts/publish_medium.py --input content/blogs/my-post.md --tags "python,data,ai"
    python3 scripts/publish_medium.py --input content/blogs/my-post.md --token app   # use developer token
    python3 scripts/publish_medium.py --input content/blogs/my-post.md --status public

OPTIONS:
    --input PATH          Path to Markdown blog file (required)
    --canonical-url URL   Original post URL (overrides front-matter)
    --tags TAG1,TAG2      Comma-separated tags (overrides front-matter; max 5)
    --token personal|app  Which token to use (default: personal)
    --status STATUS       draft | public | unlisted (default: draft)
    --title TEXT          Override post title

FRONT-MATTER (optional YAML block at top of .md file):
    ---
    title: My Post Title
    tags: [python, data, ai]
    canonical_url: https://mysite.com/my-post
    status: draft
    ---

OUTPUTS:
    Prints the Medium post URL.
    Appends record to output/published/medium_posts.json.

TOKENS (.env):
    MEDIUM_INTEGRATION_TOKEN  — personal token (medium.com/me/settings)
    MEDIUM_DEVELOPER_TOKEN    — developer app token
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

MEDIUM_API = "https://api.medium.com/v1"
PUBLISHED_LOG = Path("output/published/medium_posts.json")


# ── Front-matter parser ───────────────────────────────────────────────────────

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split YAML front-matter from body. Returns (meta, body)."""
    if not text.startswith("---"):
        return {}, text

    end = text.find("\n---", 3)
    if end == -1:
        return {}, text

    raw_yaml = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    meta = {}

    for line in raw_yaml.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        # Parse lists: [a, b, c] or - item style
        if val.startswith("[") and val.endswith("]"):
            val = [v.strip().strip('"\'') for v in val[1:-1].split(",") if v.strip()]
        meta[key] = val

    return meta, body


def extract_title(body: str) -> str | None:
    """Pull first H1 from markdown body."""
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return None


# ── Medium API ────────────────────────────────────────────────────────────────

def get_user(token: str) -> dict:
    resp = requests.get(
        f"{MEDIUM_API}/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    if resp.status_code == 401:
        print("ERROR: Invalid or expired token.")
        sys.exit(1)
    resp.raise_for_status()
    return resp.json()["data"]


def create_post(token: str, user_id: str, payload: dict) -> dict:
    resp = requests.post(
        f"{MEDIUM_API}/users/{user_id}/posts",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    if resp.status_code == 401:
        print("ERROR: Invalid or expired token.")
        sys.exit(1)
    if not resp.ok:
        print(f"ERROR: Medium API returned {resp.status_code}")
        print(resp.text)
        sys.exit(1)
    return resp.json()["data"]


# ── Published log ─────────────────────────────────────────────────────────────

def log_published(record: dict) -> None:
    PUBLISHED_LOG.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if PUBLISHED_LOG.exists():
        existing = json.loads(PUBLISHED_LOG.read_text())
    existing.append(record)
    PUBLISHED_LOG.write_text(json.dumps(existing, indent=2, ensure_ascii=False))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Publish Markdown to Medium")
    parser.add_argument("--input", required=True, type=Path, help="Path to .md file")
    parser.add_argument("--canonical-url", help="Canonical URL of original post")
    parser.add_argument("--tags", help="Comma-separated tags (max 5)")
    parser.add_argument("--token", choices=["personal", "app"], default="personal",
                        help="Which token to use (default: personal)")
    parser.add_argument("--status", choices=["draft", "public", "unlisted"],
                        default="draft", help="Publish status (default: draft)")
    parser.add_argument("--title", help="Override post title")
    args = parser.parse_args()

    # Pick token
    if args.token == "app":
        token = os.getenv("MEDIUM_DEVELOPER_TOKEN")
        token_label = "developer app"
    else:
        token = os.getenv("MEDIUM_INTEGRATION_TOKEN")
        token_label = "personal"

    if not token:
        var = "MEDIUM_DEVELOPER_TOKEN" if args.token == "app" else "MEDIUM_INTEGRATION_TOKEN"
        print(f"ERROR: {var} not set in .env")
        sys.exit(1)

    # Read file
    if not args.input.exists():
        print(f"ERROR: File not found: {args.input}")
        sys.exit(1)

    raw = args.input.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)

    # Resolve title (CLI > front-matter > H1)
    title = args.title or meta.get("title") or extract_title(body)
    if not title:
        print("ERROR: No title found. Add a # H1, front-matter title:, or --title")
        sys.exit(1)

    # Resolve tags (CLI > front-matter; max 5)
    if args.tags:
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    elif meta.get("tags"):
        raw_tags = meta["tags"]
        tags = raw_tags if isinstance(raw_tags, list) else [t.strip() for t in str(raw_tags).split(",")]
    else:
        tags = []
    tags = tags[:5]

    # Resolve canonical URL (CLI > front-matter)
    canonical_url = args.canonical_url or meta.get("canonical_url") or meta.get("canonical-url")

    # Resolve status: front-matter wins if set, otherwise use CLI arg
    status = meta.get("status") or args.status

    # Build payload
    payload = {
        "title": title,
        "contentFormat": "markdown",
        "content": raw,          # send full file including front-matter — Medium ignores it
        "publishStatus": status,
    }
    if tags:
        payload["tags"] = tags
    if canonical_url:
        payload["canonicalUrl"] = canonical_url

    # Show plan
    print(f"\nPublishing to Medium")
    print(f"  File:          {args.input}")
    print(f"  Title:         {title}")
    print(f"  Status:        {status}")
    print(f"  Tags:          {', '.join(tags) or '(none)'}")
    print(f"  Canonical URL: {canonical_url or '(none)'}")
    print(f"  Token:         {token_label}")
    print()

    # Authenticate
    user = get_user(token)
    print(f"  Authenticated as: {user.get('name')} (@{user.get('username')})")

    # Publish
    post = create_post(token, user["id"], payload)
    post_url = post.get("url", "")

    # Log
    log_published({
        "title": title,
        "medium_url": post_url,
        "medium_id": post.get("id"),
        "canonical_url": canonical_url,
        "source_file": str(args.input),
        "status": status,
        "tags": tags,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "token_used": token_label,
    })

    print(f"\n  Post URL: {post_url}")
    print(f"  Log:      {PUBLISHED_LOG}")
    print()

    return post_url


if __name__ == "__main__":
    main()
