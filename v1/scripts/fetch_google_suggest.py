#!/usr/bin/env python3
"""Google/YouTube autocomplete scraper — surfaces what real people search.

No API key. Uses public suggestqueries endpoint.

Expands seed terms with a-z prefixes + question modifiers (how/why/what/when).
Output: data/ideas/suggest_YYYY-MM-DD.json
"""

import argparse
import json
import string
import time
from datetime import datetime
from pathlib import Path

import requests

REPO = Path(__file__).parent.parent
ENDPOINT = "https://suggestqueries.google.com/complete/search"

SEEDS = {
    "data_science_tech": [
        "data science", "machine learning", "python", "mlops",
        "data analytics", "data engineering", "ai for",
    ],
    "life_self_dev": [
        "how to be", "how to stop", "why am i",
        "self improvement", "mental health", "psychology of",
        "life lessons", "habits to", "productivity",
        "why do i feel", "scared of", "signs you are",
        "nobody tells you", "what happens when", "how to stop being afraid",
        "anxiety about", "why i can't", "things you didn't know about yourself",
        "truth about", "what nobody tells you", "afraid of being",
    ],
    "poetry_quotes": [
        "poem about", "quote about", "poetry on",
        "best quotes", "deep poem",
        "poem about fear", "poem about being broken", "poem about loneliness",
        "poem about toxic", "dark poem", "poem about pain", "poem about grief",
        "quotes about being lost", "quotes about feeling empty",
        "poem about anxiety", "poem about trauma", "poem about missing someone",
    ],
}

QUESTION_MODS = ["how", "why", "what", "when", "should i", "can i", "is it"]


def fetch_suggest(query: str, client: str = "firefox", ds: str = "") -> list:
    """Return autocomplete suggestions for query. ds='yt' → YouTube."""
    params = {"client": client, "q": query}
    if ds:
        params["ds"] = ds
    try:
        resp = requests.get(ENDPOINT, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        return data[1] if len(data) > 1 else []
    except Exception as err:
        print(f"  warn: '{query}' → {err}")
        return []


def expand_seed(seed: str, source: str = "google") -> list:
    """Expand seed with a-z + question prefix variants."""
    ds = "yt" if source == "youtube" else ""
    results = set()

    # Base
    results.update(fetch_suggest(seed, ds=ds))
    time.sleep(0.15)

    # a-z suffix expansion
    for letter in string.ascii_lowercase:
        sugg = fetch_suggest(f"{seed} {letter}", ds=ds)
        results.update(sugg)
        time.sleep(0.1)

    # Question modifier prefixes
    for q in QUESTION_MODS:
        sugg = fetch_suggest(f"{q} {seed}", ds=ds)
        results.update(sugg)
        time.sleep(0.1)

    return sorted(results)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["google", "youtube", "both"], default="both")
    ap.add_argument("--niche", choices=list(SEEDS.keys()) + ["all"], default="all")
    ap.add_argument("--output-dir", default=str(REPO / "data" / "ideas"))
    ap.add_argument("--quick", action="store_true", help="Skip a-z expansion (much faster)")
    args = ap.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    sources = ["google", "youtube"] if args.source == "both" else [args.source]
    niches = list(SEEDS.keys()) if args.niche == "all" else [args.niche]

    results = {}
    for niche in niches:
        results[niche] = {}
        print(f"\n[{niche}]")
        for seed in SEEDS[niche]:
            results[niche][seed] = {}
            for src in sources:
                print(f"  {src}: '{seed}'")
                if args.quick:
                    ds = "yt" if src == "youtube" else ""
                    results[niche][seed][src] = fetch_suggest(seed, ds=ds)
                else:
                    results[niche][seed][src] = expand_seed(seed, src)
                print(f"    → {len(results[niche][seed][src])} suggestions")

    date = datetime.now().strftime("%Y-%m-%d")
    out_file = out_dir / f"suggest_{date}.json"
    out_file.write_text(json.dumps(results, indent=2))

    total = sum(
        len(s) for niche_d in results.values()
        for seed_d in niche_d.values() for s in seed_d.values()
    )
    print(f"\n✓ {total} suggestions → {out_file}")


if __name__ == "__main__":
    main()
