#!/usr/bin/env python3
"""
LinkedIn OAuth 2.0 flow — obtains access token and person URN.
Saves LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_URN to .env.

Prerequisites:
  1. Go to developer.linkedin.com → create app (or use existing)
  2. Under "Auth" tab → add redirect URL: http://localhost:8080/callback
  3. Request products: "Share on LinkedIn" + "Sign In with LinkedIn using OpenID Connect"
  4. Copy Client ID → LINKEDIN_API_KEY in .env
  5. Copy Client Secret → LINKEDIN_CLIENT_SECRET in .env
  6. Run: python3 scripts/linkedin_auth.py

Token lifetime: 60 days. Re-run when post_linkedin.py returns 401.
"""

import os
import sys
import json
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Thread

import requests
from dotenv import load_dotenv

REPO = Path(__file__).parent.parent
load_dotenv(REPO / ".env")

REDIRECT_URI  = "http://localhost:8080/callback"
AUTH_URL      = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL     = "https://www.linkedin.com/oauth/v2/accessToken"
PROFILE_URL   = "https://api.linkedin.com/v2/me"
SCOPES        = ["openid", "profile", "w_member_social"]

_auth_code: str | None = None


class _CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            _auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
                <html><body style="font-family:sans-serif;padding:40px">
                <h2>&#10003; Authorised</h2>
                <p>Return to your terminal. You can close this tab.</p>
                </body></html>
            """)
        else:
            error = params.get("error_description", ["Unknown error"])[0]
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"<html><body><h2>Error: {error}</h2></body></html>".encode())

    def log_message(self, *args):
        pass  # suppress server logs


def exchange_code(code: str, client_id: str, client_secret: str) -> str:
    resp = requests.post(TOKEN_URL, data={
        "grant_type":    "authorization_code",
        "code":          code,
        "redirect_uri":  REDIRECT_URI,
        "client_id":     client_id,
        "client_secret": client_secret,
    }, timeout=15)
    resp.raise_for_status()
    return resp.json()["access_token"]


def fetch_person_urn(token: str) -> str:
    resp = requests.get(
        PROFILE_URL,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    resp.raise_for_status()
    person_id = resp.json()["id"]
    return f"urn:li:person:{person_id}"


def update_env(key: str, value: str):
    """Update or append a key=value line in .env."""
    env_path = REPO / ".env"
    lines = env_path.read_text(encoding="utf-8").splitlines()
    found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f'{key}="{value}"'
            found = True
            break
    if not found:
        lines.append(f'{key}="{value}"')
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    client_id     = os.getenv("LINKEDIN_API_KEY")
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")

    if not client_id:
        sys.exit(
            "LINKEDIN_API_KEY not set in .env\n"
            "Get it from developer.linkedin.com → your app → Auth tab → Client ID"
        )
    if not client_secret:
        sys.exit(
            "LINKEDIN_CLIENT_SECRET not set in .env\n"
            "Get it from developer.linkedin.com → your app → Auth tab → Client Secret\n"
            "Add to .env: LINKEDIN_CLIENT_SECRET=\"your_secret\""
        )

    # Build auth URL
    params = urllib.parse.urlencode({
        "response_type": "code",
        "client_id":     client_id,
        "redirect_uri":  REDIRECT_URI,
        "scope":         " ".join(SCOPES),
        "state":         "content_machine_auth",
    })
    auth_url = f"{AUTH_URL}?{params}"

    # Start local callback server in background thread
    server = HTTPServer(("localhost", 8080), _CallbackHandler)
    thread = Thread(target=server.handle_request, daemon=True)
    thread.start()

    print("\nLinkedIn OAuth")
    print("─" * 40)
    print("Opening browser for authorisation...")
    print(f"If browser doesn't open, visit:\n{auth_url}\n")
    webbrowser.open(auth_url)

    thread.join(timeout=120)
    server.server_close()

    if not _auth_code:
        sys.exit("No auth code received within 120 seconds. Try again.")

    print("Auth code received. Exchanging for token...")
    token = exchange_code(_auth_code, client_id, client_secret)

    print("Fetching person URN...")
    person_urn = fetch_person_urn(token)

    update_env("LINKEDIN_ACCESS_TOKEN", token)
    update_env("LINKEDIN_PERSON_URN",   person_urn)

    print(f"\n✓ LINKEDIN_ACCESS_TOKEN saved to .env")
    print(f"✓ LINKEDIN_PERSON_URN: {person_urn}")
    print(f"\nToken valid for ~60 days. Re-run this script when post_linkedin.py returns 401.")


if __name__ == "__main__":
    main()
