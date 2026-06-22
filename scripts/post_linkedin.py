#!/usr/bin/env python3
"""
Post text / document to LinkedIn via LinkedIn API v2.
Credential: LINKEDIN_ACCESS_TOKEN from .env
             LINKEDIN_PERSON_URN from .env (format: urn:li:person:XXXXXXXX)

Get access token:
  1. Create app at developer.linkedin.com
  2. Request scopes: r_liteprofile + w_member_social
  3. Run OAuth flow → save token to .env as LINKEDIN_ACCESS_TOKEN
  4. Get your person URN: curl -H "Authorization: Bearer TOKEN" https://api.linkedin.com/v2/me
     → copy 'id' field, format as urn:li:person:{id}

Usage (standalone):
    python3 scripts/post_linkedin.py --post-file content/derivatives/{slug}/linkedin_post.txt
    python3 scripts/post_linkedin.py --post-file path/to/post.txt --image assets/thumbnails/slug.png
    python3 scripts/post_linkedin.py --post-file path/to/caption.txt --document assets/slides/slug.pdf --doc-title "My Slide Deck"
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO = Path(__file__).parent.parent
DB_PATH = REPO / "data" / "scheduling.db"
load_dotenv(REPO / ".env")

LI_API = "https://api.linkedin.com/v2"


def get_credentials() -> tuple[str, str]:
    token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    urn = os.getenv("LINKEDIN_PERSON_URN")

    if not token:
        sys.exit(
            "LINKEDIN_ACCESS_TOKEN not set in .env\n"
            "Get it via OAuth at developer.linkedin.com — see script docstring."
        )
    if not urn:
        sys.exit(
            "LINKEDIN_PERSON_URN not set in .env\n"
            "Format: urn:li:person:XXXXXXXX\n"
            f"Find your ID: curl -H 'Authorization: Bearer {token[:20]}...' {LI_API}/me"
        )
    return token, urn


def upload_image(token: str, urn: str, image_path: Path) -> str:
    """Register image upload + upload binary. Returns asset URN."""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Step 1: register upload
    reg_payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": urn,
            "serviceRelationships": [{
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent",
            }],
        }
    }
    reg = requests.post(f"{LI_API}/assets?action=registerUpload", headers=headers, json=reg_payload)
    reg.raise_for_status()
    reg_data = reg.json()

    upload_url = reg_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset_urn = reg_data["value"]["asset"]

    # Step 2: upload binary
    with open(image_path, "rb") as f:
        img_data = f.read()
    upload_resp = requests.put(
        upload_url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"},
        data=img_data,
    )
    upload_resp.raise_for_status()
    return asset_urn


def post_text(token: str, urn: str, text: str, image_path: Path | None = None,
             scheduled_unix_ms: int | None = None) -> str:
    """Post to LinkedIn. Returns post URN.

    scheduled_unix_ms: Unix epoch milliseconds — LinkedIn holds the post and publishes
    it natively. Must be >= 10 min from now. Omit to publish immediately.
    """
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "X-Restli-Protocol-Version": "2.0.0"}

    payload = {
        "author": urn,
        "lifecycleState": "SCHEDULED" if scheduled_unix_ms else "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    if scheduled_unix_ms:
        payload["scheduledPublishTime"] = scheduled_unix_ms

    if image_path and image_path.exists():
        print(f"  Uploading image: {image_path.name} ...", end=" ", flush=True)
        asset_urn = upload_image(token, urn, image_path)
        print("OK")
        payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
        payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
            "status": "READY",
            "description": {"text": ""},
            "media": asset_urn,
            "title": {"text": ""},
        }]

    resp = requests.post(f"{LI_API}/ugcPosts", headers=headers, json=payload)
    resp.raise_for_status()
    return resp.headers.get("x-restli-id", "unknown")


def upload_document(token: str, urn: str, pdf_path: Path) -> str:
    """Register document upload + upload PDF binary. Returns asset URN."""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    reg_payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-document"],
            "owner": urn,
            "serviceRelationships": [{
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent",
            }],
        }
    }
    reg = requests.post(f"{LI_API}/assets?action=registerUpload", headers=headers, json=reg_payload)
    reg.raise_for_status()
    reg_data = reg.json()

    upload_url = reg_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset_urn = reg_data["value"]["asset"]

    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
    upload_resp = requests.put(
        upload_url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"},
        data=pdf_data,
    )
    upload_resp.raise_for_status()
    return asset_urn


def post_document(token: str, urn: str, text: str, pdf_path: Path, title: str,
                  scheduled_unix_ms: int | None = None) -> str:
    """Post a PDF document to LinkedIn. Returns post URN."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    print(f"  Uploading document: {pdf_path.name} ...", end=" ", flush=True)
    asset_urn = upload_document(token, urn, pdf_path)
    print("OK")

    payload = {
        "author": urn,
        "lifecycleState": "SCHEDULED" if scheduled_unix_ms else "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "DOCUMENT",
                "media": [{
                    "status": "READY",
                    "media": asset_urn,
                    "title": {"text": title},
                }],
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    if scheduled_unix_ms:
        payload["scheduledPublishTime"] = scheduled_unix_ms

    resp = requests.post(f"{LI_API}/ugcPosts", headers=headers, json=payload)
    resp.raise_for_status()
    return resp.headers.get("x-restli-id", "unknown")


def post_comment(token: str, urn: str, post_urn: str, text: str) -> str:
    """Add a comment to a freshly created post (used for the pinned first comment
    carrying the blog link — LinkedIn suppresses reach on body links).

    Returns the comment id, or raises requests.HTTPError.
    """
    from urllib.parse import quote

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    encoded = quote(post_urn, safe="")
    payload = {"actor": urn, "object": post_urn, "message": {"text": text}}
    resp = requests.post(
        f"{LI_API}/socialActions/{encoded}/comments", headers=headers, json=payload
    )
    resp.raise_for_status()
    return resp.json().get("id", "unknown")


def _log_result(db_post_id: int | None, status: str, detail: dict):
    if db_post_id is None or not DB_PATH.exists():
        return
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE posts SET status=?, posted_at=?, metadata_json=? WHERE id=?",
        (status, datetime.now(timezone.utc).isoformat(), json.dumps(detail), db_post_id),
    )
    conn.commit()
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Post to LinkedIn.")
    parser.add_argument("--post-file", required=True, help="Path to linkedin_post.txt")
    parser.add_argument("--image", help="Optional image path (PNG/JPG)")
    parser.add_argument("--document", help="Optional PDF path — posts as a document/slide deck")
    parser.add_argument("--doc-title", default="", help="Title shown on the document card")
    parser.add_argument("--dry-run", action="store_true", help="Print post without publishing")
    args = parser.parse_args()

    post_path = Path(args.post_file)
    if not post_path.is_absolute():
        post_path = REPO / post_path
    if not post_path.exists():
        sys.exit(f"File not found: {post_path}")

    text = post_path.read_text(encoding="utf-8").strip()
    image_path = Path(args.image) if args.image else None
    doc_path = Path(args.document) if args.document else None

    print(f"Post ({len(text)} chars):\n{text[:200]}{'...' if len(text) > 200 else ''}\n")
    if image_path:
        print(f"Image: {image_path}")
    if doc_path:
        print(f"Document: {doc_path}")

    if args.dry_run:
        print("Dry run — nothing posted.")
        return

    token, urn = get_credentials()
    print("Posting to LinkedIn ...", end=" ", flush=True)

    try:
        if doc_path and doc_path.exists():
            post_urn = post_document(token, urn, text, doc_path, args.doc_title or doc_path.stem)
        else:
            post_urn = post_text(token, urn, text, image_path)
        print("OK")
        print(f"Post URN: {post_urn}")
        _log_result(None, "posted", {"post_urn": post_urn})
    except requests.HTTPError as e:
        print(f"FAILED: {e.response.status_code} — {e.response.text[:200]}", file=sys.stderr)
        _log_result(None, "failed", {"error": str(e)})
        sys.exit(1)


if __name__ == "__main__":
    main()
