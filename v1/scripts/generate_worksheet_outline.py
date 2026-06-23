#!/usr/bin/env python3
"""Generate worksheet outline JSON + Canva design prompt from a blog post.

Outputs:
  content/worksheets/{week}/{slug}_worksheet.json
  content/prompts/{week}/{slug}_worksheet_prompt.txt

Usage:
    python3 scripts/generate_worksheet_outline.py -i content/blogs/2026-W25/slug.md
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.claude_cli import call_claude  # noqa: E402
from lib.schedule_calc import get_iso_week  # noqa: E402

NICHE_MAP = {
    "data_science_tech": {
        "type": "practice_guide",
        "section_count": 5,
        "temperature": 0.4,
        "prompt_style": "string",
    },
    "life_self_dev": {
        "type": "action_guide",
        "section_count": 4,
        "temperature": 0.85,
        "prompt_style": "list",
    },
}

DS_CANVA_TEMPLATE = """\
Create a professional worksheet PDF (A4, landscape) for "{title}"

Layout:
- Header (top 20%): Title + tagline about the topic
- {n} sections in vertical stack, each with:
  - Section number + title (bold, #1-{n})
  - Bulleted prompts or template code
  - Space for handwritten notes on right side

Colors: Dark blue (#1E3A8A) headers, light gray background, monospace font for code

Sections:
{sections}
Footer: "🔗 Get the full guide + practice exercises at the link in bio"
"""

LIFE_CANVA_TEMPLATE = """\
Create a reflective worksheet PDF (A4, portrait) for "{title}"

Layout:
- Header (top 15%): Soft gradient background. Title + subtitle about personal growth.
- {n} sections vertically stacked, each with:
  - Section title (warm orange or teal accent)
  - Reflective prompt in italics
  - Blank space for handwritten response (30-50% of section height)
  - Dividing line between sections

Colors: Warm cream background (#FFFBF0), teal accents (#0D9488), dark gray text

Sections:
{sections}
Footer: "Reply with your answers — your reflections help others find their entry point."

Optional: Soft watercolor accent in corner.
"""


def detect_niche(slug: str) -> str | None:
    if "data_science_tech" in slug:
        return "data_science_tech"
    if "life_self_dev" in slug:
        return "life_self_dev"
    return None


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def build_claude_prompt(blog_text: str, niche_key: str, niche_cfg: dict) -> str:
    if niche_key == "data_science_tech":
        voice = "Data Science & Tech creator. Analytical, concrete, practical. Audience: aspiring data scientists and Python learners."
        prompt_schema = '"prompt": "Hands-on exercise or reflection as a single string"'
        prompt_rule = "Each section prompt is a single string describing one concrete hands-on exercise"
    else:
        voice = "Life & Self-Development creator. Warm, personal, reflective. Audience: people working on habits, productivity, and personal growth."
        prompt_schema = '"prompt": ["Question or exercise 1", "Question or exercise 2", ...]'
        prompt_rule = "Each section prompt is a list of 3-5 focused questions or exercises"

    n = niche_cfg["section_count"]
    worksheet_type = niche_cfg["type"]

    return f"""You are creating a companion worksheet for a blog post. Creator voice: {voice}

Return ONLY valid JSON matching this exact schema, no markdown, no explanation:
{{
  "type": "{worksheet_type}",
  "niche": "{niche_key}",
  "title": "Concise, action-oriented worksheet title (not the same as the blog title)",
  "sections": [
    {{
      "title": "Section title",
      {prompt_schema}
    }}
  ],
  "cta": "One sentence engaging call-to-action inviting readers to share results",
  "engage_potential": "high or very_high"
}}

Rules:
- Exactly {n} sections
- {prompt_rule}
- Root every section in specific content from the blog — no generic advice
- Banned phrases: "In conclusion", "Dive into", "Leverage", "Game-changer", "Synergy"
- CTA must invite a concrete, specific response (not just "let me know your thoughts")

Blog post:
{blog_text[:8000]}
"""


def build_canva_prompt(worksheet: dict, niche_key: str) -> str:
    sections_text = ""
    for i, s in enumerate(worksheet.get("sections", []), 1):
        prompt = s["prompt"]
        if isinstance(prompt, list):
            body = "\n   ".join(f"- {p}" for p in prompt)
        else:
            body = prompt
        sections_text += f"{i}. {s['title']}\n   {body}\n\n"

    n = len(worksheet.get("sections", []))
    title = worksheet.get("title", "")

    if niche_key == "data_science_tech":
        return DS_CANVA_TEMPLATE.format(title=title, n=n, sections=sections_text)
    else:
        return LIFE_CANVA_TEMPLATE.format(title=title, n=n, sections=sections_text)


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate worksheet outline from a blog post.")
    ap.add_argument("-i", "--input", required=True, help="Path to blog markdown file")
    args = ap.parse_args()

    blog_path = Path(args.input)
    if not blog_path.is_absolute():
        blog_path = REPO / blog_path
    if not blog_path.exists():
        sys.exit(f"File not found: {blog_path}")

    slug = blog_path.stem
    niche_key = detect_niche(slug)
    if not niche_key:
        sys.exit(
            f"Cannot detect niche from slug: {slug}\n"
            "Expected 'data_science_tech' or 'life_self_dev' in filename."
        )

    niche_cfg = NICHE_MAP[niche_key]
    date_str = slug[:10]
    week = get_iso_week(date_str)

    print(f"=== generate_worksheet_outline: {slug} ===")
    print(f"    niche={niche_key}  week={week}")

    blog_text = blog_path.read_text(encoding="utf-8")
    prompt = build_claude_prompt(blog_text, niche_key, niche_cfg)

    print("\n[1/2] generating worksheet outline via Claude…")
    worksheet: dict | None = None
    for attempt in range(2):
        if attempt == 1:
            prompt = (
                "Return ONLY a raw JSON object. No markdown. No explanation. "
                "Start with { and end with }.\n\n" + prompt
            )
            print("  JSON parse failed — retrying with stricter instruction")
        try:
            raw = call_claude(
                prompt,
                cache=True,
                timeout=120,
                temperature=niche_cfg["temperature"],
                progress_label="worksheet outline",
            )
            worksheet = _extract_json(raw)
            break
        except json.JSONDecodeError:
            if attempt == 0:
                continue
            sys.exit("JSON parse failed after retry. Run with CLAUDE_DEBUG=1 to inspect raw output.")
        except RuntimeError as e:
            sys.exit(f"Claude call failed: {e}")

    if worksheet is None:
        sys.exit("No output from Claude.")

    worksheet["blog_file"] = str(blog_path.relative_to(REPO))
    worksheet["slug"] = slug

    worksheets_dir = REPO / "content" / "worksheets" / week
    worksheets_dir.mkdir(parents=True, exist_ok=True)
    json_out = worksheets_dir / f"{slug}_worksheet.json"
    json_out.write_text(json.dumps(worksheet, indent=2, ensure_ascii=False), encoding="utf-8")

    canva_txt = build_canva_prompt(worksheet, niche_key)
    prompts_dir = REPO / "content" / "prompts" / week
    prompts_dir.mkdir(parents=True, exist_ok=True)
    prompt_out = prompts_dir / f"{slug}_worksheet_prompt.txt"
    prompt_out.write_text(canva_txt, encoding="utf-8")

    print(f"\n[2/2] done")
    print(f"  JSON:  {json_out.relative_to(REPO)}")
    print(f"  Canva: {prompt_out.relative_to(REPO)}")
    print(f"\n  Title: {worksheet.get('title', '')}")
    print(f"  Sections: {len(worksheet.get('sections', []))}")
    print(f"  Engage potential: {worksheet.get('engage_potential', '')}")


if __name__ == "__main__":
    main()
