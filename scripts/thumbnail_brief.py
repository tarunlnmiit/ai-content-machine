#!/usr/bin/env python3
"""
Generate thumbnail_brief.json for a blog post using Claude Haiku.
~500 tokens per call via free Anthropic API key.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO = Path(__file__).parent.parent
load_dotenv(REPO / ".env")

BRAND_PALETTE = {
    "dark_bg": "#1C1C2E",
    "text_primary": "#E8E0D5",
    "steel_breath": "#7C9CB0",
    "antique_gold": "#C9A96E",
    "terracotta": "#E8745A",
}

NICHE_ACCENT = {
    "data_science_tech": "#7C9CB0",
    "life_self_dev": "#E8745A",
    "poetry_quotes": "#C9A96E",
}

PROMPT_TEMPLATE = """You are a YouTube thumbnail copywriter for a data scientist and content creator named Tarun Gupta.

Blog niche: {niche}
Blog title: {title}
Blog excerpt (first 400 words):
{excerpt}

Brand palette (always use from this set only):
- Background: #1C1C2E
- Text primary: #E8E0D5
- Steel blue-grey: #7C9CB0
- Antique gold: #C9A96E
- Terracotta: #E8745A

Return ONLY valid JSON with exactly these keys. No markdown. No explanation.

{{
  "main_text": "max 6 words, punchy, viewer stops scrolling — ALL CAPS",
  "sub_text": "max 10 words, clarifies or adds intrigue — Title Case",
  "background_mood": "one phrase describing the visual mood (e.g. 'dark tech grid', 'warm sunset blur', 'minimal dark abstract')",
  "colour_palette": ["#HEX1 for main_text", "#HEX2 for sub_text", "#HEX3 for accent element"],
  "canva_search_term": "2-3 word Canva stock image search term for background texture"
}}

Rules:
- main_text: speaks to pain, curiosity, or a surprising claim — not a description
- colour_palette[0] must be the niche accent: {niche_accent}
- colour_palette[1]: #E8E0D5
- colour_palette[2]: #1C1C2E (dark background)
- canva_search_term: abstract, dark-themed, no faces"""


from lib.slug import slugify


def detect_niche(slug: str, path: str) -> str:
    combined = (slug + path).lower()
    if "data_science" in combined or "_ds_" in combined:
        return "data_science_tech"
    if "life_self" in combined or "_life_" in combined:
        return "life_self_dev"
    if "poetry" in combined or "_poetry_" in combined:
        return "poetry_quotes"
    return "data_science_tech"


def extract_title(content: str) -> str:
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return content.splitlines()[0][:80] if content else "Untitled"


def main():
    parser = argparse.ArgumentParser(description="Generate thumbnail brief via Claude Haiku.")
    parser.add_argument("--input", required=True, help="Path to blog .md file")
    args = parser.parse_args()

    blog_path = Path(args.input)
    if not blog_path.is_absolute():
        blog_path = REPO / blog_path
    if not blog_path.exists():
        sys.exit(f"File not found: {blog_path}")

    content = blog_path.read_text(encoding="utf-8")
    title = extract_title(content)
    excerpt = " ".join(content.split()[:300])

    slug = blog_path.stem
    niche = detect_niche(slug, str(blog_path))
    niche_accent = NICHE_ACCENT.get(niche, "#7C9CB0")

    prompt = PROMPT_TEMPLATE.format(
        niche=niche.replace("_", " "),
        title=title,
        excerpt=excerpt,
        niche_accent=niche_accent,
    )

    print(f"Blog: {blog_path.name}")
    print(f"Niche: {niche} | Accent: {niche_accent}")

    raw = None
    tokens_used = {"input": 0, "output": 0}

    # Backend: claude -p (Claude Max subscription)
    if raw is None:
        try:
            print("Calling claude -p ...", end=" ", flush=True)
            result = subprocess.run(
                ["claude", "-p", prompt],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode != 0 or not result.stdout.strip():
                raise RuntimeError(result.stderr.strip())
            raw = result.stdout.strip()
            print("OK")
        except Exception as e:
            sys.exit(f"All backends failed: {e}")

    # Strip markdown fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        brief = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.exit(f"JSON parse failed: {e}\nRaw output:\n{raw}")

    # Inject metadata
    brief["niche"] = niche
    brief["blog_slug"] = slug
    brief["blog_title"] = title
    brief["tokens_used"] = tokens_used

    out_dir = REPO / "content" / "derivatives" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "thumbnail_brief.json"
    out_path.write_text(json.dumps(brief, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nSaved: {out_path.relative_to(REPO)}")
    print(f"Main text:  {brief.get('main_text')}")
    print(f"Sub text:   {brief.get('sub_text')}")
    print(f"Mood:       {brief.get('background_mood')}")
    print(f"Search:     {brief.get('canva_search_term')}")
    print(f"Palette:    {brief.get('colour_palette')}")
    if tokens_used["input"] == 0 and tokens_used["output"] == 0:
        print("Tokens:     N/A (claude -p subprocess)")
    else:
        print(f"Tokens:     {tokens_used['input']} in / {tokens_used['output']} out")


if __name__ == "__main__":
    main()
