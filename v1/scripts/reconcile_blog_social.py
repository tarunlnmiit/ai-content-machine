#!/usr/bin/env python3
"""Reconcile Medium articles against the Instagram carousels/reels derived from them.

Medium is upstream (the origin); IG carousels/reels are downstream derivatives.
`v1/docs/content-tracker.md` is the spine — every check is against its records,
never against IG or Medium data directly. See `v1/docs/ig-2026-crossref.md` for
the one-off analysis this script formalizes, and `v1/data/ig_post_map.json` for
the persistent shortcode -> tracker-slug map it maintains.

Usage:
    python3 v1/scripts/reconcile_blog_social.py [--niche ds|life|poetry] [--next]
            [--ig-json PATH] [--apply] [--json] [--gaps]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_tracker_html import DASH, DEFAULT_MD, parse_md  # noqa: E402
from lib.content_paths import REPO  # noqa: E402
from lib.tracker_update import set_field  # noqa: E402

IG_MAP_PATH = REPO / "data" / "ig_post_map.json"
MEDIUM_STATS_PATH = REPO / "data" / "analytics" / "medium-stats-2026-08-11.json"

NICHES = ("ds", "life", "poetry")

MATCH_THRESHOLD_LOW = 0.35   # below this: unmatched, do not guess
MATCH_THRESHOLD_HIGH = 0.6   # at/above this: confidence "high", else "med"

STOPWORDS = frozenset({
    "the", "a", "an", "to", "of", "and", "in", "on", "for", "is", "you",
    "your", "i", "it", "this", "that", "with", "at", "how", "why", "what",
    "are", "be", "my", "me", "so", "but", "or", "not", "was", "were",
})

# Seeded from v1/docs/ig-2026-crossref.md (built 2026-08-14). Only unambiguous,
# uncontested matches are seeded here — the doc itself flags several rows as
# contested (06-21 dispute) or ambiguous ("pushkar-photo-carousel" or
# "pushkar-musician-reel") or unmatched ("no row"); those are intentionally
# left out so this script never writes a guess.
# (shortcode, slug, asset, confidence, permalink)
SEED_MATCHES = [
    ("DZhkDvoxtt2", "ORPHAN:automated-job-hunting-script", "reel", "high",
     "https://www.instagram.com/breathofdatascience/reel/DZhkDvoxtt2/"),
    ("DZ_04ObRvEx", "2026-05-31_data_science_tech_the-one-skill-that-makes-you-good-at-ai", "reel", "med",
     "https://www.instagram.com/breathofdatascience/reel/DZ_04ObRvEx/"),
    ("Daf2IdKgZ_l", "2026-07-06_data_science_tech_the-local-ai-agent-i-built-in-a-weekend-now-does-the-grunt-w", "carousel", "high",
     "https://www.instagram.com/breathofdatascience/p/Daf2IdKgZ_l/"),
    ("DbA_1_9D33z", "2026-05-31_data_science_tech_the-one-skill-that-makes-you-good-at-ai", "carousel", "med",
     "https://www.instagram.com/breathofdatascience/p/DbA_1_9D33z/"),
    ("DbIuOnSH0iU", "2026-05-25_data_science_tech_python-for-data-science-tutorial-210", "carousel", "high",
     "https://www.instagram.com/breathofdatascience/p/DbIuOnSH0iU/"),
    ("DbS6jHPmNTF", "2026-06-26_data_science_tech_what-hiring-managers-think-when-they-see-your-ds-github-2026", "reel", "high",
     "https://www.instagram.com/breathofdatascience/reel/DbS6jHPmNTF/"),
    ("DZpqksgjP9v", "ORPHAN:safe-and-alive", "carousel", "high",
     "https://www.instagram.com/mistakenlyhuman/p/DZpqksgjP9v/"),
    ("DZqryR2jfAN", "ORPHAN:safe-and-alive", "carousel", "high",
     "https://www.instagram.com/mistakenlyhuman/p/DZqryR2jfAN/"),
    ("DZtsCdFkv1h", "ORPHAN:how-i-turned-my-habits-into-an-engine", "carousel", "high",
     "https://www.instagram.com/mistakenlyhuman/p/DZtsCdFkv1h/"),
    ("DZwQ1zjjcML", "ORPHAN:how-i-turned-my-habits-into-an-engine", "carousel", "high",
     "https://www.instagram.com/mistakenlyhuman/p/DZwQ1zjjcML/"),
    ("Dakx96Oj6ps", "2026-07-06_life_self_dev_your-overloaded-self-improvement-schedule-is-slowly-making-y", "carousel", "high",
     "https://www.instagram.com/mistakenlyhuman/p/Dakx96Oj6ps/"),
    ("DbAZemRD003", "2026-05-26_life_self_dev_mental-health-openness-and-breaking-stigmas", "carousel", "high",
     "https://www.instagram.com/mistakenlyhuman/p/DbAZemRD003/"),
    ("DbJC0yDjNym", "2026-05-27_poetry_quotes_intoxicated-senses", "carousel", "high",
     "https://www.instagram.com/mistakenlyhuman/p/DbJC0yDjNym/"),
    ("DbVz85-jYsK", "2026-06-30_life_self_dev_the-5-minute-habit-that-replaced-3-hours-of-self-help-conten", "reel", "high",
     "https://www.instagram.com/mistakenlyhuman/reel/DbVz85-jYsK/"),
    ("DbbEct1Dby5", "ORPHAN:pushkar-fish-poem", "reel", "high",
     "https://www.instagram.com/mistakenlyhuman/reel/DbbEct1Dby5/"),
]
SEED_SOURCE = "verified-2026-08-14"


# ── asset state (three-way: posted / in-progress / missing) ─────────────────
#
# "Built" (created/scheduled/script/rendered) is not "posted". The whole point
# of this reconciliation is catching the gap between the two, so the two must
# never collapse into one bucket.

ASSET_FIELDS = {
    "carousel": ("carousel.status", "carousel.url"),
    "reel": ("reel.status", "reel.ig"),
}


def asset_state(status: str) -> str:
    """posted | in-progress | missing, from a raw carousel.status/reel.status value."""
    if status == "posted":
        return "posted"
    if status in (DASH, "none", ""):
        return "missing"
    return "in-progress"


def display_status(status: str) -> str:
    """Table-cell rendering: the real status if there is one, else 'MISSING'."""
    return "MISSING" if status in (DASH, "none", "") else status


def missing_detail(record: dict[str, str]) -> list[dict[str, str]]:
    """Assets that are not posted, with their raw status and state."""
    details = []
    for asset, (status_field, _) in ASSET_FIELDS.items():
        status = record.get(status_field, DASH)
        if status == "posted":
            continue
        details.append({"asset": asset, "status": status, "state": asset_state(status)})
    return details


# ── tracker loading ─────────────────────────────────────────────────────────

def load_tracker(md_path: Path | None = None) -> list[dict[str, str]]:
    md_path = md_path or DEFAULT_MD
    text = md_path.read_text(encoding="utf-8")
    records, errors = parse_md(text)
    if errors:
        raise RuntimeError(f"tracker does not parse cleanly: {errors[:3]}")
    return records


def unposted_assets(record: dict[str, str]) -> list[str]:
    """Asset names (carousel/reel) not yet posted — includes in-progress and missing."""
    return [d["asset"] for d in missing_detail(record)]


def sort_key(record: dict[str, str]) -> tuple[int, str]:
    """Oldest-published-first; medium.status=published ranks above unpublished."""
    published = record.get("medium.status") == "published"
    return (0 if published else 1, record.get("date", "9999-99-99"))


def queue_for_niche(records: list[dict[str, str]], niche: str) -> list[dict[str, str]]:
    rows = [r for r in records if r["niche"] == niche and unposted_assets(r)]
    return sorted(rows, key=sort_key)


# ── medium stats ─────────────────────────────────────────────────────────────

def load_medium_posts() -> list[dict]:
    if not MEDIUM_STATS_PATH.exists():
        return []
    data = json.loads(MEDIUM_STATS_PATH.read_text(encoding="utf-8"))
    return data.get("posts", [])


def medium_url_for(record: dict[str, str], medium_posts: list[dict]) -> str:
    url = record.get("medium.url", DASH)
    if url != DASH:
        return url
    title = record.get("title", "").strip().lower()
    for post in medium_posts:
        if post.get("title", "").strip().lower() == title:
            return post.get("url", DASH)
    return DASH


# ── ig_post_map persistence ──────────────────────────────────────────────────

def seed_map() -> dict[str, dict]:
    return {
        shortcode: {"slug": slug, "asset": asset, "confidence": conf,
                    "source": SEED_SOURCE, "permalink": permalink}
        for shortcode, slug, asset, conf, permalink in SEED_MATCHES
    }


def load_ig_map() -> dict[str, dict]:
    if IG_MAP_PATH.exists():
        try:
            data = json.loads(IG_MAP_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return seed_map()


def save_ig_map(ig_map: dict[str, dict]) -> None:
    IG_MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
    IG_MAP_PATH.write_text(json.dumps(ig_map, indent=2, sort_keys=True) + "\n", encoding="utf-8")


# ── fuzzy caption/title matching ─────────────────────────────────────────────

def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", text.lower())


def _tokens(text: str) -> set[str]:
    return {t for t in _normalize(text).split() if t and t not in STOPWORDS}


def match_score(caption: str, title: str) -> float:
    title_tokens = _tokens(title)
    if not title_tokens:
        return 0.0
    overlap = len(_tokens(caption) & title_tokens) / len(title_tokens)
    seq = SequenceMatcher(None, _normalize(caption)[:300], _normalize(title)).ratio()
    return max(overlap, seq)


def best_match(caption: str, records: list[dict[str, str]]) -> tuple[str | None, float]:
    best_slug, best_score = None, 0.0
    for record in records:
        score = match_score(caption, record.get("title", ""))
        if score > best_score:
            best_slug, best_score = record["slug"], score
    return best_slug, best_score


def _asset_from_media_type(media_type: str) -> str:
    m = (media_type or "").lower()
    return "reel" if "reel" in m or "video" in m else "carousel"


def merge_ig_json(ig_map: dict[str, dict], posts: list[dict],
                   records: list[dict[str, str]]) -> tuple[list[str], list[dict]]:
    """Merge scraped IG posts into the map. Confirmed shortcodes are sticky —
    never re-inferred. Returns (newly_matched_shortcodes, unmatched_entries)."""
    newly_matched: list[str] = []
    unmatched: list[dict] = []
    for post in posts:
        shortcode = post.get("shortcode")
        if not shortcode or shortcode in ig_map:
            continue
        caption = (post.get("caption") or "").strip()
        if not caption:
            unmatched.append({"shortcode": shortcode, "reason": "no caption"})
            continue
        slug, score = best_match(caption, records)
        if slug is None or score < MATCH_THRESHOLD_LOW:
            unmatched.append({"shortcode": shortcode, "reason": f"low score {score:.2f}"})
            continue
        confidence = "high" if score >= MATCH_THRESHOLD_HIGH else "med"
        ig_map[shortcode] = {
            "slug": slug,
            "asset": _asset_from_media_type(post.get("media_type", "")),
            "confidence": confidence,
            "source": "inferred",
            "permalink": post.get("permalink", DASH),
        }
        newly_matched.append(shortcode)
    return newly_matched, unmatched


# ── proposed tracker updates ─────────────────────────────────────────────────

def proposed_updates(ig_map: dict[str, dict],
                      records: list[dict[str, str]]) -> list[tuple[str, str, str]]:
    """Detect newly-posted assets: any mapped shortcode whose tracker row isn't
    already 'posted'. Deduped per (slug, field) so two shortcodes mapped to the
    same slug/asset (e.g. a repost) don't produce conflicting writes."""
    by_slug = {r["slug"]: r for r in records}
    seen: set[tuple[str, str]] = set()
    proposals: list[tuple[str, str, str]] = []
    for shortcode in sorted(ig_map):
        entry = ig_map[shortcode]
        rec = by_slug.get(entry.get("slug", ""))
        fields = ASSET_FIELDS.get(entry.get("asset", ""))
        if rec is None or fields is None:
            continue
        status_field, url_field = fields
        slug = rec["slug"]
        if (slug, status_field) not in seen and rec.get(status_field) != "posted":
            proposals.append((slug, status_field, "posted"))
            seen.add((slug, status_field))
        permalink = entry.get("permalink")
        if (permalink and permalink != DASH and (slug, url_field) not in seen
                and rec.get(url_field, DASH) != permalink):
            proposals.append((slug, url_field, permalink))
            seen.add((slug, url_field))
    return proposals


def apply_updates(proposals: list[tuple[str, str, str]]) -> list[dict]:
    results = []
    for slug, field, value in proposals:
        try:
            results.append(set_field(slug, field, value))
        except (KeyError, ValueError, RuntimeError) as e:
            results.append({"slug": slug, "field": field, "error": str(e)})
    return results


# ── report rendering ─────────────────────────────────────────────────────────

def asset_counts(records: list[dict[str, str]], niches: tuple[str, ...]) -> dict[str, dict[str, int]]:
    """Per-asset posted/in-progress/missing counts, computed from the tracker."""
    counts = {asset: {"posted": 0, "in-progress": 0, "missing": 0} for asset in ASSET_FIELDS}
    for r in records:
        if r["niche"] not in niches:
            continue
        for asset, (status_field, _) in ASSET_FIELDS.items():
            counts[asset][asset_state(r.get(status_field, DASH))] += 1
    return counts


def build_report(records: list[dict[str, str]], ig_map: dict[str, dict],
                  niches: tuple[str, ...], gaps_only: bool) -> str:
    matched_slugs = {v["slug"] for v in ig_map.values()}
    lines = ["# Blog -> Social Reconciliation Report", ""]
    for niche in niches:
        rows = [r for r in records if r["niche"] == niche]
        if not rows:
            continue
        gaps = [r for r in rows if unposted_assets(r)]
        display_rows = gaps if gaps_only else rows
        lines.append(f"## {niche} ({len(rows)} articles, {len(gaps)} not fully posted)")
        lines.append("")
        lines.append("| Slug | Title | Medium | Carousel | Reel |")
        lines.append("|---|---|---|---|---|")
        for r in sorted(display_rows, key=sort_key):
            carousel = display_status(r.get("carousel.status", DASH))
            reel = display_status(r.get("reel.status", DASH))
            title = r["title"][:70]
            lines.append(f"| {r['slug']} | {title} | {r.get('medium.status', DASH)} | {carousel} | {reel} |")
        lines.append("")
    total = sum(1 for r in records if r["niche"] in niches)
    total_gaps = sum(1 for r in records if r["niche"] in niches and unposted_assets(r))
    lines.append(f"**Totals:** {total} tracker records, {total_gaps} not fully posted (carousel and/or reel).")
    for asset, c in asset_counts(records, niches).items():
        lines.append(f"**{asset}:** {c['posted']} posted, {c['in-progress']} in-progress, {c['missing']} missing.")
    lines.append(f"**IG map:** {len(ig_map)} shortcodes tracked, {len(matched_slugs)} distinct slugs matched.")
    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--niche", choices=NICHES)
    parser.add_argument("--next", action="store_true", dest="next_")
    parser.add_argument("--ig-json", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json_out")
    parser.add_argument("--gaps", action="store_true")
    args = parser.parse_args(argv)

    if args.next_ and not args.niche:
        parser.error("--next requires --niche")

    records = load_tracker()
    ig_map = load_ig_map()
    medium_posts = load_medium_posts()

    newly_matched: list[str] = []
    unmatched: list[dict] = []
    if args.ig_json:
        posts = json.loads(args.ig_json.read_text(encoding="utf-8"))
        newly_matched, unmatched = merge_ig_json(ig_map, posts, records)
        save_ig_map(ig_map)

    applied: list[dict] = []
    proposals: list[tuple[str, str, str]] = []
    if args.ig_json or args.apply:
        proposals = proposed_updates(ig_map, records)
        if args.apply:
            applied = apply_updates(proposals)

    if args.next_:
        queue = queue_for_niche(records, args.niche)
        if not queue:
            if args.json_out:
                print(json.dumps({"niche": args.niche, "next": None}))
            else:
                print(f"No gaps in queue for niche={args.niche}.")
            return 0
        r = queue[0]
        missing = missing_detail(r)
        result = {
            "title": r["title"],
            "slug": r["slug"],
            "medium_url": medium_url_for(r, medium_posts),
            "missing": missing,
        }
        if args.json_out:
            print(json.dumps(result))
        else:
            print(f"Next ({args.niche}): {result['title']}")
            print(f"Slug: {result['slug']}")
            print(f"Medium URL: {result['medium_url']}")
            parts = [
                f"{d['asset']} ({d['status']})" if d["state"] == "missing"
                else f"{d['asset']} ({d['status']} — built, not posted)"
                for d in missing
            ]
            print(f"Missing: {', '.join(parts)}")
        return 0

    niches = (args.niche,) if args.niche else NICHES

    if args.json_out:
        rows = [r for r in records if r["niche"] in niches
                and (not args.gaps or unposted_assets(r))]
        out = {
            "records": [{"slug": r["slug"], "title": r["title"], "niche": r["niche"],
                         "medium_status": r.get("medium.status", DASH),
                         "missing": missing_detail(r)} for r in rows],
            "asset_counts": asset_counts(records, niches),
            "ig_map_size": len(ig_map),
            "newly_matched": newly_matched,
            "unmatched": unmatched,
            "proposals": [{"slug": s, "field": f, "value": v} for s, f, v in proposals],
            "applied": applied,
        }
        print(json.dumps(out, indent=2))
        return 0

    print(build_report(records, ig_map, niches, args.gaps))
    if newly_matched:
        print(f"\nNewly matched from --ig-json: {len(newly_matched)}")
    if unmatched:
        print(f"Unmatched IG posts: {len(unmatched)}")
        for u in unmatched:
            print(f"  - {u['shortcode']}: {u['reason']}")
    if proposals and not args.apply:
        print(f"\nProposed updates ({len(proposals)}, not applied — pass --apply to write):")
        for slug, field, value in proposals:
            print(f"  - {slug}: {field} = {value}")
    if applied:
        print(f"\nApplied {len(applied)} update(s):")
        for res in applied:
            if "error" in res:
                print(f"  ! {res['slug']}.{res['field']}: {res['error']}")
            else:
                print(f"  - {res['slug']}.{res.get('field')}: {res.get('old')} -> {res.get('new')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
