#!/usr/bin/env python3
"""
Generate final Canva AI 2.0 conversational prompts from current week's blogs + derivatives.

Reads:
  - content/blogs/*.md (this week's blogs)
  - content/derivatives/*/thumbnail_brief.json (metadata)
  - prompts/canva_ai_2_0_workflow.md (prompt templates)

Outputs: output/scheduled/canva_ai_2_0_final_prompts.md (ready-to-paste for Canva AI 2.0)

Usage:
    python3 scripts/generate_canva_ai_2_0_prompts.py
    python3 scripts/generate_canva_ai_2_0_prompts.py --slug my-blog-slug
    python3 scripts/generate_canva_ai_2_0_prompts.py --brand-kit "Deep Breath"
"""

import argparse
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

REPO = Path(__file__).parent.parent

NICHE_MAP = {
    "data_science_tech": "Data Science/Tech",
    "life_self_dev": "Life & Self-Dev",
    "poetry_quotes": "Poetry & Quotes",
}

NICHE_STYLES = {
    "data_science_tech": "digital art, 3D models, neon accents, dark navy, geometric style",
    "life_self_dev": "warm photography style, golden light, soft focus, minimal",
    "poetry_quotes": "watercolor, ink wash, dreamy, contemplative, artistic",
}


def extract_niche_from_filename(filename: str) -> str:
    """Extract niche from blog filename: YYYY-MM-DD_{niche}_slug.md"""
    if "data_science_tech" in filename:
        return "data_science_tech"
    elif "life_self_dev" in filename:
        return "life_self_dev"
    elif "poetry_quotes" in filename:
        return "poetry_quotes"
    return "data_science_tech"


def extract_slug(filename: str) -> str:
    """Extract slug from blog filename (remove .md)"""
    return filename.replace(".md", "")


def extract_quote_from_blog(blog_path: Path) -> str:
    """Extract first block quote from blog markdown or standalone quoted line"""
    content = blog_path.read_text(encoding="utf-8")

    # Try markdown block quote: > quoted text
    matches = re.findall(r'^> (.+)$', content, re.MULTILINE)
    if matches:
        return matches[0].strip()

    # Try quoted lines (text in quotes)
    matches = re.findall(r'"([^"]+)"', content)
    if matches:
        return matches[0].strip()

    # Try single-line quote patterns: 'quoted' or *quoted* or **quoted**
    matches = re.findall(r'[\'"`]([^\'"`]{20,})[\'"`]', content)
    if matches:
        return matches[0].strip()

    return "[Quote to be extracted]"


def read_thumbnail_brief(slug: str, niche: str) -> dict:
    """Read thumbnail_brief.json for blog. Handles slug format differences & truncation.
    Blog slugs: 2026-05-13_life_self_dev_why-do-most-daily-check-in-habits-fall-apart-after-a-few-day
    Deriv dirs:  2026-05-13-life-self-dev-why-do-most-daily-check-in-habits-f (truncated)
    """
    deriv_dir = REPO / "content" / "derivatives"
    if not deriv_dir.exists():
        return {}

    # Extract date from slug (YYYY-MM-DD)
    date_part = slug.split("_")[0]  # 2026-05-13
    niche_hyphen = niche.replace("_", "-")  # data-science-tech

    # Try exact match first (with underscores converted to hyphens)
    hyphen_slug = slug.replace("_", "-")
    brief_path = deriv_dir / hyphen_slug / "thumbnail_brief.json"
    if brief_path.exists():
        try:
            return json.loads(brief_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    # Find derivative directory matching date + niche (handles truncated slugs)
    for deriv_subdir in sorted(deriv_dir.iterdir()):
        if not deriv_subdir.is_dir():
            continue
        dir_name = deriv_subdir.name

        # Match: starts with date AND contains niche keyword
        if dir_name.startswith(date_part) and niche_hyphen in dir_name:
            brief_path = deriv_subdir / "thumbnail_brief.json"
            if brief_path.exists():
                try:
                    return json.loads(brief_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    pass

    return {}


def hex_to_name(hex_code: str) -> str:
    """Map hex to readable color name"""
    mapping = {
        "#1C1C2E": "deep midnight navy",
        "#E8E0D5": "warm off-white",
        "#7C9CB0": "steel blue-grey",
        "#C9A96E": "antique gold",
        "#E8745A": "terracotta coral",
    }
    return mapping.get(hex_code.upper(), hex_code)


def read_slide_outline(slug: str, niche: str) -> dict:
    """Read slide_outline.json for structured slide content"""
    deriv_dir = REPO / "content" / "derivatives"
    date_part = slug.split("_")[0]
    niche_hyphen = niche.replace("_", "-")

    for deriv_subdir in sorted(deriv_dir.iterdir()):
        if not deriv_subdir.is_dir():
            continue
        if deriv_subdir.name.startswith(date_part) and niche_hyphen in deriv_subdir.name:
            outline_path = deriv_subdir / "slide_outline.json"
            if outline_path.exists():
                try:
                    return json.loads(outline_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    pass
    return {}


def format_slide_content(outline: dict) -> str:
    """Format slide outline into readable prompt content"""
    if not outline or "slides" not in outline:
        return "[Slide content to be populated]"

    slides_text = []
    for slide in outline.get("slides", [])[:10]:  # Limit to 10 slides
        heading = slide.get("heading", "")
        bullets = slide.get("bullet_points", [])
        bullets_str = "\n  - ".join(bullets) if bullets else ""
        slide_str = f"Slide {slide.get('slide_number', '?')}: {heading}\n  - {bullets_str}" if bullets_str else f"Slide {slide.get('slide_number', '?')}: {heading}"
        slides_text.append(slide_str)

    return "\n\n".join(slides_text)


def build_slide_prompt(blog_title: str, slug: str, niche: str, brief: dict, outline: dict, brand_kit: str | None = None) -> str:
    """Build Canva AI 2.0 prompt for slide deck only"""
    main_text = brief.get("main_text", "[MAIN_TEXT]")
    sub_text = brief.get("sub_text", "[SUB_TEXT]")
    palette = brief.get("colour_palette", [])
    style = NICHE_STYLES.get(niche, "")
    slide_content = format_slide_content(outline)

    color_info = ""
    if palette:
        hex1, hex2 = palette[0] if palette else "", (palette[1] if len(palette) > 1 else "")
        if hex1 and hex2:
            color_info = f"{hex1}, {hex2}"
        elif hex1:
            color_info = hex1

    brand_line = f"Apply my '{brand_kit}' brand kit (colors, fonts, design style)." if brand_kit else f"Use {NICHE_MAP[niche]} style from memory library."

    prompt = f"""Create slide deck for my {NICHE_MAP[niche]} blog: "{blog_title}"

Hero slide title: {blog_title}
Main text (ALL CAPS): {main_text}
Sub text: {sub_text}

Slide structure + content (paste exact headings + bullets):
{slide_content}

Style: {style}
Color palette: {color_info}
Blog slug: {slug}

{brand_line}"""

    return prompt


def build_story_prompt(quote: str, niche: str, brief: dict, brand_kit: str | None = None) -> str:
    """Build Canva AI 2.0 prompt for both IG + YT stories (1080×1920 vertical)"""
    palette = brief.get("colour_palette", [])
    style = NICHE_STYLES.get(niche, "")

    color_info = ""
    if palette:
        hex1, hex2 = palette[0] if palette else "", (palette[1] if len(palette) > 1 else "")
        if hex1 and hex2:
            color_info = f"{hex1}, {hex2}"
        elif hex1:
            color_info = hex1

    brand_line = f"Apply my '{brand_kit}' brand kit (colors, fonts, design style)." if brand_kit else f"Use {NICHE_MAP[niche]} style from memory library."

    prompt = f"""Create vertical story (1080×1920) for {NICHE_MAP[niche]} blog

Quote: {quote}
Design: {style}
Color palette: {color_info}

Use this design for both Instagram Story and YouTube Story.

{brand_line}"""

    return prompt


def build_social_posts_prompt(blog_title: str, niche: str, brief: dict, brand_kit: str | None = None) -> str:
    """Build Canva AI 2.0 prompt for all social media posts"""
    main_text = brief.get("main_text", "[MAIN_TEXT]")
    sub_text = brief.get("sub_text", "[SUB_TEXT]")
    palette = brief.get("colour_palette", [])
    style = NICHE_STYLES.get(niche, "")

    color_info = ""
    if palette:
        hex1, hex2 = palette[0] if palette else "", (palette[1] if len(palette) > 1 else "")
        if hex1 and hex2:
            color_info = f"{hex1}, {hex2}"
        elif hex1:
            color_info = hex1

    brand_line = f"Apply my '{brand_kit}' brand kit (colors, fonts, design style)." if brand_kit else f"Use {NICHE_MAP[niche]} style from memory library."

    prompt = f"""Create social media posts for {NICHE_MAP[niche]} blog: "{blog_title}"

Main headline: {main_text}
Supporting text: {sub_text}
Color palette: {color_info}
Style: {style}

Create 4 designs (one per platform):
1. Instagram post (1080×1080)
2. LinkedIn post (1200×675)
3. Twitter/X post (1200×675 or card format)
4. Threads post (1080×1080)

Each should be adaptable to the platform's format and audience.

{brand_line}"""

    return prompt


def build_reel_cover_prompt(main_text: str, slug: str, niche: str, brief: dict, brand_kit: str | None = None) -> str:
    """Build Canva AI 2.0 prompt for reel cover frame (9:16 vertical thumbnail)"""
    palette = brief.get("colour_palette", [])
    style = NICHE_STYLES.get(niche, "")

    color_info = ""
    if palette:
        hex1, hex2 = palette[0] if palette else "", (palette[1] if len(palette) > 1 else "")
        if hex1 and hex2:
            color_info = f"{hex1}, {hex2}"
        elif hex1:
            color_info = hex1

    brand_line = f"Apply my '{brand_kit}' brand kit (colors, fonts, design style)." if brand_kit else f"Use {NICHE_MAP[niche]} style from memory library."

    prompt = f"""Create reel/short cover frame (9:16 vertical) for {NICHE_MAP[niche]} blog

Hook text: {main_text}
Color palette: {color_info}
Style: {style}
Blog slug: {slug}

Design a bold, attention-grabbing vertical thumbnail. Text should be large and readable at thumbnail size.

{brand_line}"""

    return prompt


def get_week_identifier() -> str:
    """Get week identifier: YYYY-W##. Example: 2026-W19"""
    today = datetime.now()
    # ISO week: week 1 is the first week with Thursday in it
    iso_calendar = today.isocalendar()
    year = iso_calendar[0]
    week = iso_calendar[1]
    return f"{year}-W{week:02d}"


def collect_blogs(slug_filter: str | None = None) -> list[dict]:
    """Collect all blogs from content/blogs/ (this week's only)"""
    blogs_dir = REPO / "content" / "blogs"
    if not blogs_dir.exists():
        return []

    blogs = []
    for blog_file in sorted(blogs_dir.glob("*.md")):
        if blog_file.name.startswith("_"):
            continue
        if slug_filter and slug_filter.replace("_", "-") not in blog_file.name.replace("_", "-"):
            continue

        slug = extract_slug(blog_file.name)
        niche = extract_niche_from_filename(blog_file.name)
        title = blog_file.name.replace(".md", "").replace("-", " ").title()

        # Extract actual title from blog if available
        content = blog_file.read_text(encoding="utf-8")
        title_match = re.match(r"^#\s+(.+)$", content, re.MULTILINE)
        if title_match:
            title = title_match.group(1)

        quote = extract_quote_from_blog(blog_file)
        brief = read_thumbnail_brief(slug, niche)
        outline = read_slide_outline(slug, niche)

        blogs.append({
            "filename": blog_file.name,
            "slug": slug,
            "niche": niche,
            "title": title,
            "quote": quote,
            "brief": brief,
            "outline": outline,
        })

    return blogs


def main():
    parser = argparse.ArgumentParser(description="Generate final Canva AI 2.0 prompts.")
    parser.add_argument("--slug", default=None, help="Filter to specific slug (substring match)")
    parser.add_argument("--brand-kit", default=None, help="Brand kit name (e.g., 'Deep Breath'). If not provided, uses memory library reference")
    args = parser.parse_args()

    blogs = collect_blogs(args.slug)

    if not blogs:
        target = f"slug containing '{args.slug}'" if args.slug else "any blogs"
        print(f"No blogs found for {target}.")
        print("Run this from content/blogs/ directory:")
        print("  ls content/blogs/")
        return

    sections = [
        "# Canva AI 2.0 Final Prompts",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Blogs: {len(blogs)}",
        "",
        "Copy each prompt into Canva AI 2.0 chat separately (AI can't batch multiple design types).",
        "Workflow: Slides first → Stories → Social posts",
        "",
        "---",
        "",
    ]

    # SLIDE DECKS
    sections.append("## SLIDE DECKS (10 slides with content)")
    sections.append("")

    for blog in blogs:
        niche = blog["niche"]
        title = blog["title"]
        slug = blog["slug"]
        brief = blog["brief"]
        outline = blog["outline"]

        prompt = build_slide_prompt(title, slug, niche, brief, outline, args.brand_kit)

        sections.append(f"### {NICHE_MAP[niche]} — `{slug}`")
        sections.append("")
        sections.append("```")
        sections.append(prompt)
        sections.append("```")
        sections.append("")

    sections.append("---")
    sections.append("")

    # STORIES (Instagram + YouTube)
    sections.append("## STORIES (1080×1920 vertical — use for both Instagram & YouTube)")
    sections.append("")

    for blog in blogs:
        niche = blog["niche"]
        title = blog["title"]
        slug = blog["slug"]
        quote = blog["quote"]
        brief = blog["brief"]

        prompt = build_story_prompt(quote, niche, brief, args.brand_kit)

        sections.append(f"### {NICHE_MAP[niche]} — `{slug}`")
        sections.append("")
        sections.append("```")
        sections.append(prompt)
        sections.append("```")
        sections.append("")

    sections.append("---")
    sections.append("")

    # SOCIAL MEDIA POSTS
    sections.append("## SOCIAL MEDIA POSTS (Instagram, LinkedIn, Twitter, Threads)")
    sections.append("")

    for blog in blogs:
        niche = blog["niche"]
        title = blog["title"]
        slug = blog["slug"]
        brief = blog["brief"]

        prompt = build_social_posts_prompt(title, niche, brief, args.brand_kit)

        sections.append(f"### {NICHE_MAP[niche]} — `{slug}`")
        sections.append("")
        sections.append("```")
        sections.append(prompt)
        sections.append("```")
        sections.append("")

    sections.append("---")
    sections.append("")

    # REEL COVERS (9:16 vertical thumbnails)
    sections.append("## REEL COVERS (9:16 vertical thumbnails for shorts/reels)")
    sections.append("")

    for blog in blogs:
        niche = blog["niche"]
        slug = blog["slug"]
        brief = blog["brief"]
        main_text = brief.get("main_text", "[MAIN_TEXT]")

        prompt = build_reel_cover_prompt(main_text, slug, niche, brief, args.brand_kit)

        sections.append(f"### {NICHE_MAP[niche]} — `{slug}`")
        sections.append("")
        sections.append("```")
        sections.append(prompt)
        sections.append("```")
        sections.append("")

    sections.append("---")

    output = "\n".join(sections)

    out_dir = REPO / "output" / "scheduled"
    out_dir.mkdir(parents=True, exist_ok=True)

    week_id = get_week_identifier()
    out_filename = f"canva_ai_2_0_final_prompts_{week_id}.md"
    out_path = out_dir / out_filename
    out_path.write_text(output, encoding="utf-8")

    print(f"✓ Saved: {out_path.relative_to(REPO)}")
    print(f"  Blogs: {len(blogs)}")
    print(f"  Week: {week_id}")
    print()
    for blog in blogs:
        print(f"  [{NICHE_MAP[blog['niche']]}] {blog['slug']}")
    print()
    print("Next: Copy each prompt → Canva AI 2.0 chat")


if __name__ == "__main__":
    main()
