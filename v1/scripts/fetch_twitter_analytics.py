#!/Users/tarungupta/miniconda3/envs/content_engine_env/bin/python3.14
"""
fetch_twitter_analytics.py — Pull tweet analytics for @mistakenlyhuman via Apify.

USAGE:
    python3 scripts/fetch_twitter_analytics.py   # incremental (new tweets only)

First run fetches all historical tweets; subsequent runs fetch only new ones.

OUTPUTS:
    data/analytics/twitter_tweets.json   — all tweets with engagement metrics
    data/analytics/twitter_state.json    — last run state for incremental updates
"""

import requests
import time
import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")
ACTOR_ID = "CJdippxWmn9uRfooo"

BASE_URL = "https://api.apify.com/v2"
DATA_FILE = Path("data/analytics/twitter_tweets.json")
STATE_FILE = Path("data/analytics/twitter_state.json")


# --------------------------
# STATE MANAGEMENT
# --------------------------
def load_state():
    if not STATE_FILE.exists():
        return None
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(latest_date):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump({"last_since": latest_date}, f)


# --------------------------
# APIFY FUNCTIONS
# --------------------------
def run_actor(input_payload):
    url = f"{BASE_URL}/acts/{ACTOR_ID}/runs?token={APIFY_TOKEN}"
    res = requests.post(url, json=input_payload)
    res.raise_for_status()
    return res.json()["data"]["id"]


def wait_for_run(run_id):
    url = f"{BASE_URL}/actor-runs/{run_id}?token={APIFY_TOKEN}"
    while True:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()["data"]
        status = data["status"]
        print(f"Status: {status}")
        if status in ["SUCCEEDED", "FAILED", "ABORTED"]:
            return data
        time.sleep(5)


def fetch_results(dataset_id):
    url = f"{BASE_URL}/datasets/{dataset_id}/items"
    params = {"token": APIFY_TOKEN, "clean": "true", "format": "json"}
    res = requests.get(url, params=params)
    res.raise_for_status()
    return res.json()


# --------------------------
# DATA HELPERS
# --------------------------
def load_existing_data():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def deduplicate(existing, new):
    existing_ids = {t["id"] for t in existing if "id" in t}
    return existing + [t for t in new if t.get("id") not in existing_ids]


def get_latest_date(tweets):
    dates = [t.get("createdAt") for t in tweets if t.get("createdAt")]
    return max(dates) if dates else None


# --------------------------
# MAIN LOGIC
# --------------------------
if __name__ == "__main__":

    state = load_state()

    if state:
        print("Incremental run")
        since = state["last_since"]
    else:
        print("First full run")
        since = "2006-01-01_00:00:00_UTC"

    now = datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S_UTC")

    input_payload = {
        "searchTerms": [
            f"from:mistakenlyhuman since:{since} until:{now}"
        ],
        "lang": "en"
    }

    print("Running actor...")
    run_id = run_actor(input_payload)

    run_data = wait_for_run(run_id)

    if run_data["status"] != "SUCCEEDED":
        print("Run failed")
        exit()

    dataset_id = run_data["defaultDatasetId"]

    print("Fetching tweets...")
    new_tweets = fetch_results(dataset_id)

    print(f"Fetched {len(new_tweets)} new tweets")

    existing = load_existing_data()
    combined = deduplicate(existing, new_tweets)
    save_data(combined)

    latest_date = get_latest_date(combined)
    if latest_date:
        save_state(latest_date)

    print(f"Done. Total tweets in database: {len(combined)}")
