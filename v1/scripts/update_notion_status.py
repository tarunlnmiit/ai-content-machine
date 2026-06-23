#!/usr/bin/env python3
"""Update Notion Contents DB row after publishing.

Finds row by title (fuzzy match) and updates Status + URL + Description.

Env:
  NOTION_INTEGRATION_SECRET — Notion integration token
  NOTION_CONTENTS_DB_ID     — Contents database UUID

Usage:
  python3 scripts/update_notion_status.py --title "Why I Quit Pandas" --status Published --url https://medium.com/...
  python3 scripts/update_notion_status.py --title "Poem Slug" --status "Ready to publish"
  python3 scripts/update_notion_status.py --title "..." --status Published --url https://... --note "1.2k views first day"

Valid status values (per Contents DB schema):
  Idea | Started | Script | Editing | Ready to publish | Uploaded | Published | Archived
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

import requests

REPO = Path(__file__).resolve().parent.parent
NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

VALID_STATUS = {
    "Idea", "Started", "Script", "Editing",
    "Ready to publish", "Uploaded", "Published", "Archived",
}


def load_env():
    env_file = REPO / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def find_page(token: str, db_id: str, title_query: str) -> Optional[dict]:
    """Find first page whose title contains title_query (case-insensitive)."""
    needle = title_query.strip().lower()
    cursor = None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        r = requests.post(
            f"{NOTION_API}/databases/{db_id}/query",
            headers=headers(token), json=body, timeout=20,
        )
        r.raise_for_status()
        data = r.json()
        for page in data.get("results", []):
            props = page.get("properties", {})
            # find title property (type=title)
            for _, val in props.items():
                if val.get("type") == "title":
                    parts = val.get("title", [])
                    text = "".join(p.get("plain_text", "") for p in parts).lower()
                    if needle in text:
                        return page
                    break
        if not data.get("has_more"):
            return None
        cursor = data.get("next_cursor")


def detect_props(page: dict) -> dict:
    """Return mapping of {role: prop_name} for status/url/description on this page's DB."""
    out = {}
    for name, val in page.get("properties", {}).items():
        t = val.get("type")
        if t == "status" and "status" not in out:
            out["status"] = name
        elif t == "select" and name.lower() == "status" and "status" not in out:
            out["status"] = name
            out["status_type"] = "select"
        elif t == "url" and "url" not in out:
            out["url"] = name
        elif t == "rich_text" and val.get("type") and "description" not in out:
            if name.lower() in {"description", "notes", "note"}:
                out["description"] = name
    return out


def build_patch(page: dict, status: Optional[str], url: Optional[str], note: Optional[str]) -> dict:
    props_meta = detect_props(page)
    patch = {}
    if status:
        prop_name = props_meta.get("status")
        if not prop_name:
            sys.exit("no status property on DB")
        # default to status type unless explicitly select
        is_select = page["properties"][prop_name].get("type") == "select"
        key = "select" if is_select else "status"
        patch[prop_name] = {key: {"name": status}}
    if url:
        prop_name = props_meta.get("url")
        if prop_name:
            patch[prop_name] = {"url": url}
    if note:
        prop_name = props_meta.get("description")
        if prop_name:
            patch[prop_name] = {"rich_text": [{"text": {"content": note}}]}
    return patch


def update_page(token: str, page_id: str, patch: dict) -> bool:
    r = requests.patch(
        f"{NOTION_API}/pages/{page_id}",
        headers=headers(token), json={"properties": patch}, timeout=20,
    )
    if r.status_code not in (200, 201):
        print(f"update failed {r.status_code}: {r.text[:300]}")
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True, help="title substring to find row")
    ap.add_argument("--status", help=f"new status. one of: {sorted(VALID_STATUS)}")
    ap.add_argument("--url", help="published URL")
    ap.add_argument("--note", help="append to Description/Notes")
    ap.add_argument("--db", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.status and args.status not in VALID_STATUS:
        sys.exit(f"invalid status. use one of: {sorted(VALID_STATUS)}")

    load_env()
    token = os.environ.get("NOTION_INTEGRATION_SECRET")
    if not token:
        sys.exit("missing NOTION_INTEGRATION_SECRET")
    db_id = args.db or os.environ.get("NOTION_CONTENTS_DB_ID")
    if not db_id:
        sys.exit("missing NOTION_CONTENTS_DB_ID (or pass --db)")

    page = find_page(token, db_id, args.title)
    if not page:
        sys.exit(f"no row matches title containing: {args.title!r}")
    print(f"found page: {page['id']}")

    patch = build_patch(page, args.status, args.url, args.note)
    if not patch:
        sys.exit("nothing to update (pass --status / --url / --note)")

    if args.dry_run:
        import json as _json
        print("would patch:", _json.dumps(patch, indent=2))
        return

    if update_page(token, page["id"], patch):
        print(f"updated {len(patch)} field(s)")


if __name__ == "__main__":
    main()
