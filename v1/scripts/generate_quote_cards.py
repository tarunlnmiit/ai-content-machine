#!/usr/bin/env python3
"""
Read all instagram_caption.txt files from content/derivatives/*/
Extract the 3 best quotes per blog (under 120 chars, from caption_body or hook_line).
Output output/scheduled/quote_cards.csv for Canva Bulk Create.

CSV columns: slug, niche, quote_text, attribution_line, handle
"""

import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
HANDLE = "@mistakenlyhuman"
MAX_QUOTE_LEN = 120


def extract_quotes_from_caption(caption_text: str, slug: str) -> list[str]:
    """
    Pull quote candidates from instagram_caption.txt.
    Format written by repurpose_blog.py:
      Format: ...
      Why: ...
      (blank)
      hook_line
      (blank)
      caption_body
      (blank)
      Slides: ...
      (blank)
      #hashtags
    """
    lines = caption_text.splitlines()
    candidates = []

    in_body = False
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("Format:") or line.startswith("Why:") or line.startswith("Slides:") or line.startswith("#"):
            in_body = False
            continue
        # hook line and body paragraphs are our candidates
        if not line.startswith("Format") and not line.startswith("Why") and not line.startswith("#"):
            if len(line) >= 30:  # skip very short lines
                candidates.append(line)

    # Score: prefer lines that feel quotable —
    # complete sentences, no "Format/Why/Slides" prefix, right length
    quotes = []
    for c in candidates:
        clean = re.sub(r"^\d+\.\s*", "", c).strip()  # strip leading numbers
        if 30 <= len(clean) <= MAX_QUOTE_LEN and not clean.startswith(("Format", "Why", "Slide", "#")):
            quotes.append(clean)

    # Deduplicate, keep best 3
    seen = set()
    unique = []
    for q in quotes:
        if q not in seen:
            seen.add(q)
            unique.append(q)
        if len(unique) == 3:
            break

    return unique


def detect_niche(slug: str) -> str:
    if "data_science" in slug:
        return "Data Science / Tech"
    if "life_self" in slug:
        return "Life & Self-Development"
    if "poetry" in slug:
        return "Poetry / Quotes"
    return "General"


def attribution_for_niche(niche: str) -> str:
    mapping = {
        "Data Science / Tech": "Tarun Gupta · Data Scientist",
        "Life & Self-Development": "Tarun Gupta",
        "Poetry / Quotes": "Tarun Gupta · @mistakenlyhuman",
    }
    return mapping.get(niche, "Tarun Gupta")


def main():
    deriv_dir = REPO / "content" / "derivatives"
    if not deriv_dir.exists():
        sys.exit("content/derivatives/ not found — run repurpose_blog.py first")

    caption_files = sorted(deriv_dir.glob("*/instagram_caption.txt"))
    if not caption_files:
        sys.exit("No instagram_caption.txt files found — run repurpose_blog.py first")

    rows = []
    for caption_path in caption_files:
        slug = caption_path.parent.name
        niche = detect_niche(slug)
        attribution = attribution_for_niche(niche)

        caption_text = caption_path.read_text(encoding="utf-8")
        quotes = extract_quotes_from_caption(caption_text, slug)

        if not quotes:
            print(f"  Warning: no quotable lines found in {slug} — skipping")
            continue

        for quote in quotes:
            rows.append({
                "slug": slug,
                "niche": niche,
                "quote_text": quote,
                "attribution_line": f"— {attribution}",
                "handle": HANDLE,
            })

        print(f"  {slug}: {len(quotes)} quote(s) extracted")

    if not rows:
        sys.exit("No quotes extracted from any caption file.")

    out_dir = REPO / "output" / "scheduled"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "quote_cards.csv"

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["slug", "niche", "quote_text", "attribution_line", "handle"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved: {out_path.relative_to(REPO)}")
    print(f"Total quote cards: {len(rows)} (across {len(caption_files)} blog(s))")
    print("\nNext: Canva → IG Story — Quote template → Apps → Bulk Create → upload quote_cards.csv")
    print("Map columns: quote_text → quote box, attribution_line → attribution, handle → handle")


if __name__ == "__main__":
    main()
