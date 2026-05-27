#!/usr/bin/env python3
"""Sync top ideas from data/ideas/weekly_ideas.md → Notion Contents DB.

For each idea not already present (by title match), creates a Backlog row.
Existing rows untouched.

Env:
  NOTION_INTEGRATION_SECRET — Notion internal integration token (required)
  NOTION_CONTENTS_DB_ID     — Contents database UUID (required unless --db given)

Usage:
  python3 scripts/sync_ideas_to_notion.py
  python3 scripts/sync_ideas_to_notion.py --dry-run
  python3 scripts/sync_ideas_to_notion.py --db <DB_ID>  # override env
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

import requests

REPO = Path(__file__).resolve().parent.parent
NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# Map weekly_ideas.md section heading → Notion Topic select option (must exist in DB)
NICHE_TO_TOPIC = {
    "data science tech": "Tech",
    "life self dev": "Life",
    "poetry quotes": "Poetry",
}

# Notion Status option to set on new rows (must exist in DB)
NEW_ROW_STATUS = "Idea"


def load_env():
    env_file = REPO / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def parse_weekly_ideas(md_path: Path) -> list:
    """Return list of {niche, title, url, source, score}."""
    if not md_path.exists():
        sys.exit(f"missing: {md_path}")
    text = md_path.read_text()

    items = []
    current_niche = None
    current_title = None
    current_meta = {}

    for line in text.splitlines():
        line = line.rstrip()
        if line.startswith("## "):
            current_niche = line[3:].strip().lower()
            continue
        m = re.match(r"^### \d+\.\s+(.*)", line)
        if m:
            if current_title:
                items.append({"niche": current_niche, "title": current_title, **current_meta})
            current_title = m.group(1).strip()
            current_meta = {}
            continue
        m = re.match(r"^- \*\*(\w+):\*\*\s*(.*)", line)
        if m:
            key = m.group(1).lower()
            current_meta[key] = m.group(2).strip()

    if current_title:
        items.append({"niche": current_niche, "title": current_title, **current_meta})

    return items


def notion_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def fetch_db_schema(token: str, db_id: str) -> dict:
    r = requests.get(f"{NOTION_API}/databases/{db_id}", headers=notion_headers(token), timeout=15)
    r.raise_for_status()
    return r.json()


def fetch_existing_titles(token: str, db_id: str, title_prop: str) -> set:
    """Query DB, paginate, collect all title values lowercase."""
    seen = set()
    start_cursor = None
    while True:
        body = {"page_size": 100}
        if start_cursor:
            body["start_cursor"] = start_cursor
        r = requests.post(
            f"{NOTION_API}/databases/{db_id}/query",
            headers=notion_headers(token), json=body, timeout=20,
        )
        if r.status_code != 200:
            print(f"  query failed {r.status_code}: {r.text[:300]}")
            return seen
        data = r.json()
        for page in data.get("results", []):
            props = page.get("properties", {})
            tp = props.get(title_prop, {})
            for tt in tp.get("title", []):
                seen.add(tt.get("plain_text", "").strip().lower())
        if not data.get("has_more"):
            break
        start_cursor = data.get("next_cursor")
    return seen


def detect_property_names(schema: dict) -> dict:
    """Heuristic: find Title, Status, Topic, URL, Description properties."""
    props = schema.get("properties", {})
    out = {"title": None, "status": None, "topic": None, "url": None, "description": None}
    for name, meta in props.items():
        t = meta.get("type")
        lname = name.lower()
        if t == "title" and out["title"] is None:
            out["title"] = name
        elif t in ("status", "select") and "status" in lname and out["status"] is None:
            out["status"] = (name, t)
        elif t == "select" and "topic" in lname and out["topic"] is None:
            out["topic"] = name
        elif t == "url" and out["url"] is None and "canva" not in lname:
            # Only auto-use a URL property if its name doesn't reference Canva/etc.
            out["url"] = name
        elif t == "rich_text" and lname in ("description", "notes", "summary"):
            if out["description"] is None:
                out["description"] = name
    return out


def build_page_props(item: dict, prop_map: dict) -> dict:
    props = {}
    if prop_map["title"]:
        props[prop_map["title"]] = {
            "title": [{"text": {"content": item["title"][:1900]}}]
        }
    if prop_map["status"]:
        name, ptype = prop_map["status"]
        props[name] = {ptype: {"name": NEW_ROW_STATUS}}
    if prop_map["topic"]:
        topic_val = NICHE_TO_TOPIC.get(item.get("niche", ""), "")
        if topic_val:
            props[prop_map["topic"]] = {"select": {"name": topic_val}}
    if prop_map["url"] and item.get("url"):
        props[prop_map["url"]] = {"url": item["url"]}
    if prop_map["description"]:
        bits = []
        if item.get("source"):
            bits.append(f"source: {item['source']}")
        if item.get("score"):
            bits.append(f"score: {item['score']}")
        if item.get("category"):
            bits.append(f"category: {item['category']}")
        # Embed URL in description if no dedicated URL prop available
        if not prop_map["url"] and item.get("url"):
            bits.append(f"url: {item['url']}")
        if bits:
            props[prop_map["description"]] = {
                "rich_text": [{"text": {"content": " · ".join(bits)[:1900]}}]
            }
    return props


def create_page(token: str, db_id: str, props: dict) -> Optional[str]:
    body = {"parent": {"database_id": db_id}, "properties": props}
    r = requests.post(f"{NOTION_API}/pages", headers=notion_headers(token), json=body, timeout=20)
    if r.status_code in (200, 201):
        return r.json().get("id")
    print(f"  create failed {r.status_code}: {r.text[:300]}")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=None, help="Notion DB ID (defaults to NOTION_CONTENTS_DB_ID env)")
    ap.add_argument("--input", default=str(REPO / "data" / "ideas" / "weekly_ideas.md"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    load_env()
    token = os.environ.get("NOTION_INTEGRATION_SECRET")
    if not token:
        sys.exit("missing NOTION_INTEGRATION_SECRET in .env")

    args.db = args.db or os.environ.get("NOTION_CONTENTS_DB_ID")
    if not args.db:
        sys.exit("missing NOTION_CONTENTS_DB_ID in .env (or pass --db <UUID>)")

    items = parse_weekly_ideas(Path(args.input))
    print(f"parsed {len(items)} ideas from {args.input}")

    print(f"fetch schema for db {args.db}")
    try:
        schema = fetch_db_schema(token, args.db)
    except requests.HTTPError as e:
        sys.exit(f"DB fetch failed: {e}")

    prop_map = detect_property_names(schema)
    print(f"detected props: {json.dumps(prop_map, default=str)}")
    if not prop_map["title"]:
        sys.exit("no title property found — DB schema unexpected")

    existing = fetch_existing_titles(token, args.db, prop_map["title"])
    print(f"existing rows: {len(existing)}")

    created = skipped = failed = 0
    for item in items:
        if item["title"].strip().lower() in existing:
            skipped += 1
            continue
        if args.dry_run:
            print(f"  DRY would create: [{item['niche']}] {item['title'][:70]}")
            created += 1
            continue
        props = build_page_props(item, prop_map)
        if create_page(token, args.db, props):
            print(f"  ✓ {item['title'][:70]}")
            created += 1
        else:
            failed += 1

    print(f"\ndone — created={created} skipped={skipped} failed={failed}")


if __name__ == "__main__":
    main()
