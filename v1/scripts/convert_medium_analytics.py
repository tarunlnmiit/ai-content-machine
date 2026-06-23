import argparse
import json
import csv
import datetime
import requests
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:14b"  # or "llama3.1:8b"
BATCH_SIZE = 10        # articles per Ollama call to stay within context window
# ─────────────────────────────────────────────────────────────────────────────

def parse_directly(data: list) -> list[dict]:
    rows = []
    for edge in data:
        node = edge["node"]
        views = node["totalStats"]["views"] or 0
        reads = node["totalStats"]["reads"] or 0
        ratio = round(reads / views, 2) if views > 0 else 0
        e = node["earnings"]["total"]
        earnings = round(e["units"] + e["nanos"] / 1_000_000_000, 2)
        pub = datetime.datetime.fromtimestamp(
            node["firstPublishedAt"] / 1000
        ).strftime("%Y-%m-%d")
        collection = node["collection"]["name"] if node.get("collection") else ""
        rows.append({
            "title": node["title"],
            "views": views,
            "reads": reads,
            "read_ratio": ratio,
            "earnings_usd": earnings,
            "published_date": pub,
            "collection": collection,
            "url": node["mediumUrl"],
        })
    return rows


def _ollama_parse_batch(batch: list) -> list[dict]:
    prompt = f"""You are a data parser. Extract article stats from this Medium GraphQL JSON.
Return ONLY a JSON array, no explanation, no markdown, no backticks.

Each item in the input has a "node" key. Extract these fields per article:
- title (string)
- views (integer, from totalStats.views)
- reads (integer, from totalStats.reads)
- read_ratio (float, reads/views rounded to 2 decimals, 0 if views=0)
- earnings_usd (float, earnings.total.units + earnings.total.nanos/1000000000, rounded to 2 decimals)
- published_date (string YYYY-MM-DD, converted from firstPublishedAt millisecond timestamp)
- collection (string, collection.name or empty string if null)
- url (string, mediumUrl)

Input JSON:
{json.dumps(batch)}

Return only the JSON array:"""

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    })
    response.raise_for_status()
    raw = response.json()["response"].strip()
    if not raw:
        raise ValueError("Ollama returned an empty response for this batch")
    return json.loads(raw)


def parse_with_ollama(data: list) -> list[dict]:
    rows = []
    total = len(data)
    num_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
    for i in range(0, total, BATCH_SIZE):
        batch = data[i:i + BATCH_SIZE]
        print(f"  batch {i // BATCH_SIZE + 1}/{num_batches} ({len(batch)} articles)...")
        rows.extend(_ollama_parse_batch(batch))
    return rows


def main():
    parser = argparse.ArgumentParser(description="Convert Medium stats JSON to CSV")
    parser.add_argument("json_path", nargs="?",
                        default=str(Path(__file__).parent.parent / "data" / "analytics" / "medium-stats-all.json"),
                        help="Path to Medium stats JSON file")
    parser.add_argument("--ollama", action="store_true",
                        help="Use Ollama LLM for parsing (default: direct parse)")
    args = parser.parse_args()

    print(f"Reading {args.json_path}...")
    raw = Path(args.json_path).read_text()
    data = json.loads(raw)

    if args.ollama:
        print(f"Parsing with Ollama ({MODEL}) in batches of {BATCH_SIZE}...")
        rows = parse_with_ollama(data)
    else:
        print(f"Parsing {len(data)} articles directly...")
        rows = parse_directly(data)

    rows.sort(key=lambda x: x["views"], reverse=True)

    month = datetime.datetime.now().strftime("%Y-%m")
    analytics_dir = Path(__file__).parent.parent / "data" / "analytics"
    output_path = str(analytics_dir / f"medium-stats-{month}.csv")

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"✓ Saved {len(rows)} articles → {output_path}")
    print(f"\nTop 5 by views:")
    for r in rows[:5]:
        print(f"  {r['views']:>6} views  ${r['earnings_usd']:>7.2f}  {r['title'][:55]}")


if __name__ == "__main__":
    main()
