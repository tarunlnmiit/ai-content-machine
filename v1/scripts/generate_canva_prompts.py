#!/usr/bin/env python3
"""
Generate Canva AI Text to Image prompts from thumbnail_brief.json files.
Reads all content/derivatives/*/thumbnail_brief.json
Writes output/scheduled/canva_prompts.md — copy-paste ready for Canva AI (THUMBNAILS only).

For SLIDE DECK prompts, see: prompts/canva_slide_prompts.md

Usage:
    python3 scripts/generate_canva_prompts.py
    python3 scripts/generate_canva_prompts.py --slug my-blog-slug
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).parent.parent

# Niche-specific style modifiers for Canva Text to Image
NICHE_STYLE = {
    "data_science_tech": (
        "Cinematic composition: layered geometric grids fading into deep space, "
        "with flowing data streams and abstract circuit pathways. Foreground features "
        "crystalline data nodes connected by glowing lines. Midground: blurred code "
        "fragments and mathematical equations. Background: infinite dark navy void "
        "with faint star-like data points. Lighting: cool blue-white neon glow with "
        "volumetric rays cutting through haze. Atmosphere: tech-noir, corporate, "
        "sophisticated. Film grain: light. Depth of field: shallow, focus on nodes. "
        "Color grading: cool tones, high contrast, cinematic. Mood: analytical, "
        "powerful, mysterious. Art style: digital illustration, sci-fi, hyper-detailed. "
        "16:9 aspect ratio. No text, no people, no faces."
    ),
    "life_self_dev": (
        "Warm, intimate composition: soft-focus abstract landscape with layered "
        "atmospheric depth. Foreground: organic textures like fabric, water ripples, "
        "or paper. Midground: warm bokeh circles in terracotta, gold, and cream tones. "
        "Background: subtle gradient fading to deep navy-black. Lighting: golden hour "
        "side-light with soft shadows, creating dimensional warmth. Atmosphere: "
        "introspective, peaceful, hopeful. Film grain: subtle. Depth of field: shallow, "
        "dreamy. Color grading: warm, desaturated with rich accent colors. Mood: "
        "emotional growth, quiet strength, personal reflection. Art style: fine art "
        "photography, watercolor blend, soft impressionism. 16:9 aspect ratio. No text, "
        "no people, no faces."
    ),
    "poetry_quotes": (
        "Artistic, ethereal composition: abstract ink wash blending with watercolor. "
        "Foreground: delicate ink splatters and brush strokes suggesting movement and "
        "emotion. Midground: layered translucent shapes in gold, cream, and midnight "
        "navy creating depth. Background: misty, dreamlike atmosphere with subtle "
        "golden halos. Lighting: soft, diffused glow with gentle highlights on texture. "
        "Atmosphere: poetic, melancholic, contemplative, mystical. Film grain: visible, "
        "adds character. Depth of field: soft, painterly. Color grading: moody, artistic, "
        "emphasizing golds against deep tones. Mood: literary, introspective, artistic "
        "expression. Art style: contemporary abstract art, ink painting, mixed media. "
        "16:9 aspect ratio. No text, no people, no faces."
    ),
}

NICHE_LABEL = {
    "data_science_tech": "Data Science / Tech",
    "life_self_dev": "Life & Self-Dev",
    "poetry_quotes": "Poetry / Quotes",
}

CANVA_STEPS = """\
Steps in Canva (Using Your Brand Template + Canva AI):
  1. Open your YT Thumbnail brand template (1280×720) in Canva
  2. Create a new layer below text elements for AI background
  3. Apps → Magic Media → Text to Image
  4. Paste the detailed Text to Image prompt below into the search box
  5. Review 2-3 generated options — pick the one closest to your vision
  6. Generate → Click to insert
  7. Resize/position the AI background to cover entire canvas
  8. Set background layer opacity to 20-30% (allows your template design to show through)
  9. Apply colour_palette hex codes to text layers (ensure contrast over background)
  10. Adjust text shadow/outline if needed for readability
  11. Export PNG → assets/thumbnails/{slug}_thumb.png
  12. Magic Resize → 1080×1080 (IG Post) + 1080×1920 (IG Story) → export both

TIP: If Canva AI result doesn't match vision, regenerate 2-3 more times or use stock fallback."""


def hex_to_name(hex_code: str) -> str:
    """Map brand hex to readable name for prompt context."""
    mapping = {
        "#1C1C2E": "deep midnight navy",
        "#E8E0D5": "warm off-white",
        "#7C9CB0": "steel blue-grey",
        "#C9A96E": "antique gold",
        "#E8745A": "terracotta coral",
    }
    return mapping.get(hex_code.upper(), hex_code)


def build_text_to_image_prompt(brief: dict) -> str:
    niche = brief.get("niche", "data_science_tech")
    mood = brief.get("background_mood", "dark abstract")
    palette = brief.get("colour_palette", [])
    style = NICHE_STYLE.get(niche, NICHE_STYLE["data_science_tech"])

    color_desc = ", ".join(hex_to_name(h) for h in palette if h)

    prompt = f"{mood}, {color_desc} color palette, {style}"
    return prompt


def build_stock_fallback(brief: dict) -> str:
    search = brief.get("canva_search_term", "")
    mood = brief.get("background_mood", "")
    return f'{search} — mood: {mood}'


def format_brief_section(brief: dict) -> str:
    slug = brief.get("blog_slug", "unknown")
    title = brief.get("blog_title", "")
    niche = brief.get("niche", "data_science_tech")
    main_text = brief.get("main_text", "")
    sub_text = brief.get("sub_text", "")
    palette = brief.get("colour_palette", [])

    text_to_image = build_text_to_image_prompt(brief)
    stock_fallback = build_stock_fallback(brief)

    palette_display = "  |  ".join(
        f"{h} ({hex_to_name(h)})" for h in palette if h
    )

    steps = CANVA_STEPS.replace("{slug}", slug)

    lines = [
        f"## {NICHE_LABEL.get(niche, niche)} — `{slug}`",
        f"**Blog:** {title}",
        "",
        "### Thumbnail text",
        f"- **Main text (ALL CAPS):** {main_text}",
        f"- **Sub text:** {sub_text}",
        "",
        "### Colour palette",
        f"`{palette_display}`",
        "",
        "### Canva AI — Text to Image prompt",
        "```",
        text_to_image,
        "```",
        "",
        "### Canva stock fallback (if Text to Image result is poor)",
        f"Search: `{stock_fallback}`",
        "",
        "### Steps",
        steps,
    ]
    return "\n".join(lines)


def collect_briefs(slug_filter: str | None = None) -> list[dict]:
    deriv_dir = REPO / "content" / "derivatives"
    if not deriv_dir.exists():
        return []

    briefs = []
    dirs = sorted(deriv_dir.iterdir())
    for d in dirs:
        if not d.is_dir():
            continue
        if slug_filter and slug_filter.replace("_", "-") not in d.name.replace("_", "-"):
            continue
        brief_path = d / "thumbnail_brief.json"
        if not brief_path.exists():
            continue
        try:
            brief = json.loads(brief_path.read_text(encoding="utf-8"))
            briefs.append(brief)
        except json.JSONDecodeError as e:
            print(f"[warn] Could not parse {brief_path}: {e}")

    return briefs


def main():
    parser = argparse.ArgumentParser(description="Generate Canva AI prompts from thumbnail briefs.")
    parser.add_argument("--slug", default=None, help="Filter to a specific slug (substring match)")
    args = parser.parse_args()

    briefs = collect_briefs(args.slug)

    if not briefs:
        target = f"slug containing '{args.slug}'" if args.slug else "any derivative folder"
        print(f"No thumbnail_brief.json found for {target}.")
        print("Run thumbnail_brief.py first:")
        print("  python3 scripts/thumbnail_brief.py --input content/blogs/YOUR_BLOG.md")
        return

    sections = [
        "# Canva AI Prompts — Thumbnails",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Blogs: {len(briefs)}",
        "",
        "> **For SLIDE DECK prompts:** See `prompts/canva_slide_prompts.md`",
        "",
        "---",
        "",
        "## How to use",
        "For each blog below:",
        "1. Copy the **Text to Image prompt** → paste into Canva Apps → Magic Media → Text to Image",
        "2. If result is poor, use the **stock fallback** search term instead",
        "3. Place result as background at 15% opacity",
        "4. Type the **main_text** and **sub_text** into the brand template text boxes",
        "5. Apply hex codes from **colour palette** to text layers",
        "6. Export + Magic Resize",
        "",
        "---",
        "",
    ]

    for brief in briefs:
        sections.append(format_brief_section(brief))
        sections.append("")
        sections.append("---")
        sections.append("")

    output = "\n".join(sections)

    out_dir = REPO / "output" / "scheduled"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "canva_prompts.md"
    out_path.write_text(output, encoding="utf-8")

    print(f"Saved: {out_path.relative_to(REPO)}")
    print(f"Blogs: {len(briefs)}")
    print()
    for b in briefs:
        niche = NICHE_LABEL.get(b.get("niche", ""), b.get("niche", ""))
        print(f"  [{niche}] {b.get('blog_slug', '?')}")
        print(f"    Main: {b.get('main_text', '')}")
        print(f"    Sub:  {b.get('sub_text', '')}")
        print()


if __name__ == "__main__":
    main()
