#!/Users/tarungupta/miniconda3/envs/content_engine_env/bin/python3.14
"""
publish_medium.py — Publish a Markdown blog post to Medium.

USAGE:
    python3 scripts/publish_medium.py --input content/blogs/my-post.md
    python3 scripts/publish_medium.py --input content/blogs/my-post.md --canonical-url https://mysite.com/my-post
    python3 scripts/publish_medium.py --input content/blogs/my-post.md --tags "python,data,ai"
    python3 scripts/publish_medium.py --input content/blogs/my-post.md --token app   # use developer token
    python3 scripts/publish_medium.py --input content/blogs/my-post.md --status public
    python3 scripts/publish_medium.py --input content/blogs/my-post.md --publication humans-are-stories
    python3 scripts/publish_medium.py --input content/blogs/my-post.md --publication "Humans Are Stories"
    python3 scripts/publish_medium.py --input content/blogs/my-post.md --no-auto-tags  # skip auto-selection

OPTIONS:
    --input PATH              Path to Markdown blog file (required)
    --canonical-url URL       Original post URL (overrides front-matter)
    --tags TAG1,TAG2          Comma-separated tags (overrides front-matter; max 5)
    --no-auto-tags            Skip auto-tag selection (for scripted/CI use)
    --token personal|app      Which token to use (default: personal)
    --status STATUS           draft | public | unlisted (default: draft)
    --title TEXT              Override post title
    --publication NAME_OR_SLUG  Publication name or URL slug (e.g. "humans-are-stories")
                              Omit to publish to your personal profile.

FRONT-MATTER (optional YAML block at top of .md file):
    ---
    title: My Post Title
    tags: [python, data, ai]
    canonical_url: https://mysite.com/my-post
    status: draft
    publication: humans-are-stories
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
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

MEDIUM_API = "https://api.medium.com/v1"
PUBLISHED_LOG = Path("output/published/medium_posts.json")
MEDIUM_TAGS_FILE = Path("data/brand/medium_tags.txt")


def _load_allowed_tags() -> list[str]:
    if MEDIUM_TAGS_FILE.exists():
        return [line.strip() for line in MEDIUM_TAGS_FILE.read_text().splitlines() if line.strip()]
    return ["technology", "data-science", "programming", "writing", "life",
            "self-improvement", "artificial-intelligence", "python", "productivity", "mental-health"]


def auto_select_tags(blog_text: str) -> list[str]:
    allowed = _load_allowed_tags()
    tags_list = ", ".join(allowed)
    prompt = (
        "Select exactly 5 tags from the allowed list that best match this blog post. "
        "Return ONLY a comma-separated list of exactly 5 tags, no explanation.\n\n"
        f"Allowed tags: {tags_list}\n\n"
        f"Blog (first 2000 chars):\n{blog_text[:2000]}"
    )
    result = subprocess.run(
        ["claude", "--model", "claude-haiku-4-5-20251001", "--print", "-p", prompt],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        print(f"  Warning: Claude CLI failed — {result.stderr.strip()[:100]}")
        return []
    return [t.strip() for t in result.stdout.strip().split(",") if t.strip()][:5]


def confirm_tags(proposed: list[str]) -> list[str]:
    print(f"\n  Auto-selected tags: {', '.join(proposed) or '(none)'}")
    ans = input("  Confirm tags? [Y/n/edit]: ").strip().lower()
    if ans in ("", "y", "yes"):
        return proposed
    if ans in ("n", "no"):
        return []
    raw = input("  Enter tags (comma-separated, max 5): ").strip()
    return [t.strip() for t in raw.split(",") if t.strip()][:5]


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


def get_publications(token: str, user_id: str) -> list[dict]:
    resp = requests.get(
        f"{MEDIUM_API}/users/{user_id}/publications",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    if resp.status_code == 401:
        print("ERROR: Invalid or expired token.")
        sys.exit(1)
    resp.raise_for_status()
    return resp.json().get("data", [])


def find_publication(pubs: list[dict], query: str) -> dict | None:
    """Match query against publication name (case-insensitive) or URL slug."""
    query_lower = query.lower().strip()
    for pub in pubs:
        name_match = pub.get("name", "").lower() == query_lower
        slug = pub.get("url", "").rstrip("/").split("/")[-1]
        slug_match = slug.lower() == query_lower
        if name_match or slug_match:
            return pub
    return None


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


def create_publication_post(token: str, pub_id: str, payload: dict) -> dict:
    resp = requests.post(
        f"{MEDIUM_API}/publications/{pub_id}/posts",
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
    parser.add_argument("--publication", help="Publication name or URL slug (omit to publish to profile)")
    parser.add_argument("--no-auto-tags", action="store_true",
                        help="Skip auto-tag selection when no tags provided")
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

    if not tags and not args.no_auto_tags:
        print("  No tags provided — auto-selecting via Claude Haiku...")
        proposed = auto_select_tags(body)
        if proposed:
            tags = confirm_tags(proposed)

    if not tags:
        print("ERROR: No tags selected. Provide --tags, add tags to front-matter, or confirm auto-selection.")
        sys.exit(1)

    # Resolve canonical URL (CLI > front-matter)
    canonical_url = args.canonical_url or meta.get("canonical_url") or meta.get("canonical-url")

    # Resolve status: front-matter wins if set, otherwise use CLI arg
    status = meta.get("status") or args.status

    # Resolve publication target (CLI > front-matter)
    publication_query = args.publication or meta.get("publication")

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

    # Authenticate
    user = get_user(token)

    # Resolve publication if requested
    pub_name = None
    pub_id = None
    if publication_query:
        pubs = get_publications(token, user["id"])
        matched = find_publication(pubs, publication_query)
        if not matched:
            available = ", ".join(p.get("name", "") for p in pubs) or "(none)"
            print(f"ERROR: Publication not found: {publication_query!r}")
            print(f"  Your publications: {available}")
            sys.exit(1)
        pub_name = matched.get("name")
        pub_id = matched.get("id")

    # Show plan
    target = f"publication: {pub_name}" if pub_name else "personal profile"
    print(f"\nPublishing to Medium")
    print(f"  File:          {args.input}")
    print(f"  Title:         {title}")
    print(f"  Target:        {target}")
    print(f"  Status:        {status}")
    print(f"  Tags:          {', '.join(tags) or '(none)'}")
    print(f"  Canonical URL: {canonical_url or '(none)'}")
    print(f"  Token:         {token_label}")
    print()

    print(f"  Authenticated as: {user.get('name')} (@{user.get('username')})")

    # Publish
    if pub_id:
        post = create_publication_post(token, pub_id, payload)
    else:
        post = create_post(token, user["id"], payload)
    post_url = post.get("url", "")

    # Log
    log_published({
        "title": title,
        "medium_url": post_url,
        "medium_id": post.get("id"),
        "canonical_url": canonical_url,
        "publication": pub_name,
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
