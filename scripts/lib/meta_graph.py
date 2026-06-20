#!/usr/bin/env python3
"""Shared Meta Graph API client for Instagram / Facebook / Threads auto-publish.

Why: the content machine moved IG / FB / Threads from manual in-app posting to
API publishing so the scheduler daemon can fire everything (see
docs/one-time-platform-setup.md). This module centralises token handling, the
HTTP call, and credential validation so each post_*.py stays small.

Required env (.env) — see docs/one-time-platform-setup.md for how to obtain them:
    META_GRAPH_VERSION      optional, default "v21.0"
    META_ACCESS_TOKEN       long-lived Page/User token (IG + FB publishing)
    IG_USER_ID              Instagram Business/Creator account id
    META_PAGE_ID            Facebook Page id (only if publishing to FB directly)
    THREADS_ACCESS_TOKEN    Threads long-lived token
    THREADS_USER_ID         Threads user id

Honesty guardrail: IG content-publishing supports Reels, single image, and
carousel for Business/Creator accounts only. IG Stories and some Reel features
are NOT API-publishable — those stay manual. Never claim full hands-off posting.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO = Path(__file__).resolve().parent.parent.parent
load_dotenv(REPO / ".env")

GRAPH_VERSION = os.environ.get("META_GRAPH_VERSION", "v21.0")
GRAPH_ROOT = f"https://graph.facebook.com/{GRAPH_VERSION}"
THREADS_ROOT = f"https://graph.threads.net/{GRAPH_VERSION}"

DEFAULT_TIMEOUT = 60


class MetaGraphError(RuntimeError):
    """Raised when a Graph API call fails or required credentials are missing."""


def require_env(*names: str) -> dict[str, str]:
    """Return the named env vars, raising MetaGraphError listing any that are missing."""
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        raise MetaGraphError(
            "Missing required env var(s): "
            + ", ".join(missing)
            + " — see docs/one-time-platform-setup.md"
        )
    return {n: os.environ[n] for n in names}


def graph_post(path: str, params: dict, *, root: str = GRAPH_ROOT,
               timeout: int = DEFAULT_TIMEOUT) -> dict:
    """POST to a Graph endpoint. Raises MetaGraphError on non-2xx or API error."""
    url = f"{root}/{path.lstrip('/')}"
    resp = requests.post(url, data=params, timeout=timeout)
    return _parse(resp, url)


def graph_get(path: str, params: dict, *, root: str = GRAPH_ROOT,
              timeout: int = DEFAULT_TIMEOUT) -> dict:
    """GET from a Graph endpoint. Raises MetaGraphError on non-2xx or API error."""
    url = f"{root}/{path.lstrip('/')}"
    resp = requests.get(url, params=params, timeout=timeout)
    return _parse(resp, url)


def _parse(resp: requests.Response, url: str) -> dict:
    try:
        data = resp.json()
    except ValueError:
        raise MetaGraphError(f"Non-JSON response from {url}: {resp.text[:300]}")
    if resp.status_code >= 400 or "error" in data:
        err = data.get("error", {})
        raise MetaGraphError(
            f"Graph API error from {url}: "
            f"{err.get('message', resp.text[:300])} (code {err.get('code')})"
        )
    return data


def wait_for_container(container_id: str, token: str, *, root: str = GRAPH_ROOT,
                       attempts: int = 20, delay: int = 6) -> None:
    """Poll a media container until status_code == FINISHED (IG/Threads async ingest).

    Reels and video posts ingest asynchronously — publishing before the container
    is FINISHED returns an error. Raises MetaGraphError on ERROR or timeout.
    """
    for _ in range(attempts):
        status = graph_get(
            container_id,
            {"fields": "status_code,status", "access_token": token},
            root=root,
        )
        code = status.get("status_code")
        if code == "FINISHED":
            return
        if code == "ERROR":
            raise MetaGraphError(f"Media container {container_id} failed: {status}")
        time.sleep(delay)
    raise MetaGraphError(
        f"Media container {container_id} not FINISHED after {attempts * delay}s"
    )


def validate_credentials() -> dict[str, bool]:
    """Best-effort startup check: which platforms have working credentials.

    Returns {"instagram": bool, "facebook": bool, "threads": bool}. Never raises —
    the daemon logs the result and only the platforms with valid creds will fire.
    """
    status = {"instagram": False, "facebook": False, "threads": False}
    token = os.environ.get("META_ACCESS_TOKEN")
    ig_id = os.environ.get("IG_USER_ID")
    page_id = os.environ.get("META_PAGE_ID")
    th_token = os.environ.get("THREADS_ACCESS_TOKEN")
    th_id = os.environ.get("THREADS_USER_ID")

    if token and ig_id:
        try:
            graph_get(ig_id, {"fields": "id", "access_token": token})
            status["instagram"] = True
        except MetaGraphError:
            pass
    if token and page_id:
        try:
            graph_get(page_id, {"fields": "id", "access_token": token})
            status["facebook"] = True
        except MetaGraphError:
            pass
    if th_token and th_id:
        try:
            graph_get(th_id, {"fields": "id", "access_token": th_token}, root=THREADS_ROOT)
            status["threads"] = True
        except MetaGraphError:
            pass
    return status
