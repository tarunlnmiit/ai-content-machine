#!/usr/bin/env python3
"""
Post text / document to LinkedIn via LinkedIn REST API (LinkedIn-Version: 202401).
Approved product: "Share on LinkedIn" — endpoints /rest/posts, /rest/images, /rest/documents.

Credentials in .env:
  LINKEDIN_ACCESS_TOKEN  — OAuth Bearer token with w_member_social scope
  LINKEDIN_PERSON_URN    — urn:li:person:{id}

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
from urllib.parse import quote

import requests
from dotenv import load_dotenv

REPO = Path(__file__).parent.parent
DB_PATH = REPO / "data" / "scheduling.db"
load_dotenv(REPO / ".env")

LI_REST = "https://api.linkedin.com/rest"
LI_VERSION = "202506"


def _rest_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "LinkedIn-Version": LI_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
    }


def _normalize_urn(urn: str) -> str:
    """REST API needs urn:li:person:{encoded_id}. Strip member: prefix if stored incorrectly."""
    # member: numeric IDs don't work — LINKEDIN_PERSON_URN must be the encoded person URN
    return urn.replace("urn:li:member:", "urn:li:person:")


def get_credentials() -> tuple[str, str]:
    token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    urn = os.getenv("LINKEDIN_PERSON_URN")

    if not token:
        raise RuntimeError(
            "LINKEDIN_ACCESS_TOKEN not set in .env\n"
            "Get it via OAuth at developer.linkedin.com — see script docstring."
        )
    if not urn:
        raise RuntimeError(
            "LINKEDIN_PERSON_URN not set in .env\n"
            "Format: urn:li:person:XXXXXXXX"
        )
    return token, _normalize_urn(urn)


def upload_image(token: str, urn: str, image_path: Path) -> str:
    """Initialize image upload + upload binary. Returns urn:li:image:XXXXX."""
    headers = _rest_headers(token)

    init = requests.post(
        f"{LI_REST}/images?action=initializeUpload",
        headers=headers,
        json={"initializeUploadRequest": {"owner": urn}},
    )
    init.raise_for_status()
    data = init.json()["value"]
    upload_url = data["uploadUrl"]
    image_urn = data["image"]

    with open(image_path, "rb") as f:
        img_data = f.read()
    put = requests.put(
        upload_url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"},
        data=img_data,
    )
    put.raise_for_status()
    return image_urn


def upload_document(token: str, urn: str, pdf_path: Path) -> str:
    """Initialize document upload + upload PDF binary. Returns urn:li:document:XXXXX."""
    headers = _rest_headers(token)

    init = requests.post(
        f"{LI_REST}/documents?action=initializeUpload",
        headers=headers,
        json={"initializeUploadRequest": {"owner": urn}},
    )
    init.raise_for_status()
    data = init.json()["value"]
    upload_url = data["uploadUrl"]
    doc_urn = data["document"]

    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
    put = requests.put(
        upload_url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"},
        data=pdf_data,
    )
    put.raise_for_status()
    return doc_urn


def _distribution() -> dict:
    return {
        "feedDistribution": "MAIN_FEED",
        "targetEntities": [],
        "thirdPartyDistributionChannels": [],
    }


def post_text(token: str, urn: str, text: str, image_path: Path | None = None,
              scheduled_unix_ms: int | None = None) -> str:
    """Post text (optionally with image) to LinkedIn. Returns post URN."""
    headers = _rest_headers(token)
    urn = _normalize_urn(urn)

    payload: dict = {
        "author": urn,
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": _distribution(),
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    if image_path and image_path.exists():
        print(f"  Uploading image: {image_path.name} ...", end=" ", flush=True)
        image_urn = upload_image(token, urn, image_path)
        print("OK")
        payload["content"] = {
            "media": {
                "title": image_path.stem,
                "id": image_urn,
            }
        }

    resp = requests.post(f"{LI_REST}/posts", headers=headers, json=payload)
    resp.raise_for_status()
    return resp.headers.get("x-restli-id") or resp.headers.get("X-RestLi-Id", "unknown")


def post_document(token: str, urn: str, text: str, pdf_path: Path, title: str,
                  scheduled_unix_ms: int | None = None) -> str:
    """Post a PDF document to LinkedIn. Returns post URN."""
    headers = _rest_headers(token)
    urn = _normalize_urn(urn)

    print(f"  Uploading document: {pdf_path.name} ...", end=" ", flush=True)
    doc_urn = upload_document(token, urn, pdf_path)
    print("OK")

    payload = {
        "author": urn,
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": _distribution(),
        "content": {
            "media": {
                "title": title or pdf_path.stem,
                "id": doc_urn,
            }
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    resp = requests.post(f"{LI_REST}/posts", headers=headers, json=payload)
    resp.raise_for_status()
    return resp.headers.get("x-restli-id") or resp.headers.get("X-RestLi-Id", "unknown")


def post_comment(token: str, urn: str, post_urn: str, text: str) -> str:
    """Add a comment to a post. Returns comment id or raises HTTPError."""
    headers = _rest_headers(token)
    urn = _normalize_urn(urn)
    encoded = quote(post_urn, safe="")

    payload = {"actor": urn, "message": {"text": text}}
    resp = requests.post(
        f"{LI_REST}/socialActions/{encoded}/comments",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    return resp.headers.get("x-restli-id") or resp.json().get("id", "unknown")


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
    parser = argparse.ArgumentParser(description="Post to LinkedIn (REST API v202401).")
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

    try:
        token, urn = get_credentials()
    except RuntimeError as e:
        sys.exit(str(e))

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
        print(f"FAILED: {e.response.status_code} — {e.response.text[:300]}", file=sys.stderr)
        _log_result(None, "failed", {"error": str(e)})
        sys.exit(1)


if __name__ == "__main__":
    main()
