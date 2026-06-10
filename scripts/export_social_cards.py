#!/usr/bin/env python3
"""
export_social_cards.py — Export animated social card PNGs via the Remotion render server.

Loops over all derivatives for a given week, calls POST /still for each slug's
SocialCard1x1, SocialCard9x16, and Thumbnail compositions, and saves PNGs to
assets/social_posts/{week}/ and output/visuals/{week}/.

Prerequisites:
  cd remotion/server && npm install
  ts-node index.ts &            # render server on :3001

Usage:
  # Export all 3 niches for a week:
  python3 scripts/export_social_cards.py --week 2026-W24

  # Single niche:
  python3 scripts/export_social_cards.py --week 2026-W24 --niche ds

  # Dry run (print requests, skip HTTP):
  python3 scripts/export_social_cards.py --week 2026-W24 --dry-run

  # Custom render server URL:
  python3 scripts/export_social_cards.py --week 2026-W24 --server http://localhost:3001
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
DERIVATIVES_ROOT = REPO / "content" / "derivatives"
SOCIAL_POSTS_ROOT = REPO / "assets" / "social_posts"
VISUALS_ROOT = REPO / "output" / "visuals"

DEFAULT_SERVER = "http://localhost:3001"
POLL_INTERVAL = 1.0   # seconds between status polls
TIMEOUT_SEC = 120     # max wait per still export

# { compositionId: (output_dir_key, filename_suffix) }
STILL_EXPORTS = [
    ("SocialCard1x1",  "social_posts", "{slug}_social_1x1.png"),
    ("SocialCard9x16", "social_posts", "{slug}_social_9x16.png"),
    ("Thumbnail",      "visuals",      "{slug}_thumb.png"),
]

NICHE_HEADLINES = {
    "ds":      "Data Science insight",
    "life":    "Life & growth insight",
    "poetry":  "Poetry moment",
}

COMPOSITION_PROPS: dict[str, Any] = {
    "SocialCard1x1":  lambda slug, niche, headline: {"headline": headline, "niche": niche},
    "SocialCard9x16": lambda slug, niche, headline: {"headline": headline, "niche": niche},
    "Thumbnail":      lambda slug, niche, headline: {
        "titleText": headline,
        "niche": niche,
        "variant": "a",
        "bgType": "dark",
    },
}


def post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read())


def wait_for_job(server: str, job_id: str, label: str) -> str:
    """Poll until job done. Returns output file path. Raises on failure/timeout."""
    deadline = time.time() + TIMEOUT_SEC
    while time.time() < deadline:
        status = get_json(f"{server}/status/{job_id}")
        if status["status"] == "done":
            return status["outputFile"]
        if status["status"] == "failed":
            raise RuntimeError(f"{label} failed: {status.get('error', 'unknown')}")
        time.sleep(POLL_INTERVAL)
    raise TimeoutError(f"{label} timed out after {TIMEOUT_SEC}s")


def discover_slugs(week: str, niche_filter: str | None) -> list[dict]:
    """Return list of {slug, niche, headline} for derivatives in the week."""
    week_dir = DERIVATIVES_ROOT / week
    if not week_dir.exists():
        print(f"ERROR: {week_dir} not found", file=sys.stderr)
        sys.exit(1)

    slugs = []
    for slug_dir in sorted(week_dir.iterdir()):
        if not slug_dir.is_dir():
            continue
        slug = slug_dir.name

        # Infer niche from slug (format: YYYY-MM-DD_niche_subniche_slug)
        parts = slug.split("_")
        niche = parts[1] if len(parts) > 1 else "ds"
        if niche not in ("ds", "life", "poetry"):
            niche = "ds"

        if niche_filter and niche != niche_filter:
            continue

        # Try to get headline from schedule.json
        schedule_path = slug_dir / "schedule.json"
        headline = NICHE_HEADLINES.get(niche, "Content insight")
        if schedule_path.exists():
            try:
                sched = json.loads(schedule_path.read_text())
                headline = sched.get("title") or sched.get("headline") or headline
            except (json.JSONDecodeError, KeyError):
                pass

        slugs.append({"slug": slug, "niche": niche, "headline": headline})

    return slugs


def export_stills(server: str, week: str, slugs: list[dict], dry_run: bool) -> None:
    total = len(slugs) * len(STILL_EXPORTS)
    done = 0

    for item in slugs:
        slug = item["slug"]
        niche = item["niche"]
        headline = item["headline"]

        for composition_id, dir_key, filename_tpl in STILL_EXPORTS:
            filename = filename_tpl.format(slug=slug)

            if dir_key == "social_posts":
                out_dir = SOCIAL_POSTS_ROOT / week
            else:
                out_dir = VISUALS_ROOT / week

            out_path = out_dir / filename
            props_fn = COMPOSITION_PROPS.get(composition_id)
            input_props = props_fn(slug, niche, headline) if props_fn else {}

            label = f"{slug} / {composition_id}"
            print(f"  [{done+1}/{total}] {label} → {out_path.relative_to(REPO)}")

            if dry_run:
                done += 1
                continue

            out_dir.mkdir(parents=True, exist_ok=True)

            try:
                resp = post_json(f"{server}/still", {
                    "compositionId": composition_id,
                    "inputProps": input_props,
                    "outputFile": str(out_path),
                    "frame": 0,
                })
                job_id = resp["jobId"]
                wait_for_job(server, job_id, label)
                print(f"      ✓ done")
            except urllib.error.URLError as exc:
                print(f"      ERROR: cannot reach render server — {exc}", file=sys.stderr)
                print("      Start server first: cd remotion/server && ts-node index.ts &", file=sys.stderr)
                sys.exit(1)
            except (RuntimeError, TimeoutError) as exc:
                print(f"      ERROR: {exc}", file=sys.stderr)

            done += 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Export social card PNGs via Remotion render server")
    parser.add_argument("--week", required=True, help="ISO week e.g. 2026-W24")
    parser.add_argument("--niche", choices=["ds", "life", "poetry"], help="Export one niche only")
    parser.add_argument("--server", default=DEFAULT_SERVER, help=f"Render server URL (default: {DEFAULT_SERVER})")
    parser.add_argument("--dry-run", action="store_true", help="Print requests without exporting")
    args = parser.parse_args()

    slugs = discover_slugs(args.week, args.niche)

    if not slugs:
        print(f"No derivatives found for week {args.week}" +
              (f" / niche {args.niche}" if args.niche else ""))
        sys.exit(0)

    niche_tag = f" ({args.niche})" if args.niche else ""
    mode_tag = " [dry-run]" if args.dry_run else ""
    print(f"Exporting {len(slugs)} slug(s) × {len(STILL_EXPORTS)} stills — week {args.week}{niche_tag}{mode_tag}")

    export_stills(args.server, args.week, slugs, args.dry_run)

    if args.dry_run:
        print("\n[dry-run] No files written.")
    else:
        print(f"\nDone. PNGs in:")
        print(f"  {(SOCIAL_POSTS_ROOT / args.week).relative_to(REPO)}/")
        print(f"  {(VISUALS_ROOT / args.week).relative_to(REPO)}/")


if __name__ == "__main__":
    main()
