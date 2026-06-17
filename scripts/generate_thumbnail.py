#!/usr/bin/env python3
"""Generate YouTube thumbnail via two parallel pipelines:

  1. Claude → HTML → Playwright PNG  (assets/thumbnails/{slug}_thumbnail.png)
  2. Remotion still Thumbnail          (output/visuals/{week}/{slug}_thumb_{variant}.png)

Both run by default. Use --skip-html or --skip-remotion to run only one.

Usage:
    python3 scripts/generate_thumbnail.py --blog content/blogs/2026-W25/2026-06-16_...md
    python3 scripts/generate_thumbnail.py --blog path/to/blog.md --export
    python3 scripts/generate_thumbnail.py --topic "5 Python tricks" --niche ds
    python3 scripts/generate_thumbnail.py --blog ... --variants a b --bg-type gradient
    python3 scripts/generate_thumbnail.py --blog ... --skip-remotion
    python3 scripts/generate_thumbnail.py --blog ... --skip-html
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from _console import console  # noqa: E402
from lib.claude_cli import call_claude  # noqa: E402
from lib.niche_config import NICHE_MAP, load_brand_base, model_for  # noqa: E402
from lib.schedule_calc import get_iso_week  # noqa: E402
from lib.slug import slugify  # noqa: E402

REMOTION_DIR = REPO / "remotion"
THUMBNAIL_DIR = REPO / "assets" / "thumbnails"
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)
DERIVATIVES_DIR = REPO / "content" / "derivatives"

_REMOTION_NICHE_MAP = {
    "data_science": "ds",
    "tech": "ds",
    "life": "life",
    "self_dev": "life",
    "poetry": "poetry",
    "quotes": "poetry",
}

# ── niche helpers ────────────────────────────────────────────────────────────

def load_brand(niche_key: str) -> dict:
    return load_brand_base(niche_key)


def detect_niche_from_path(path: Path) -> str:
    name = path.stem.lower()
    if "data_science_tech" in name or "_ds_" in name:
        return "data_science_tech"
    if "life_self_dev" in name or "_life_" in name:
        return "life_self_dev"
    if "poetry_quotes" in name or "_poetry_" in name:
        return "poetry_quotes"
    return "data_science_tech"


def infer_remotion_niche(slug: str) -> str:
    for part in slug.split("_")[1:4]:
        if part in _REMOTION_NICHE_MAP:
            return _REMOTION_NICHE_MAP[part]
    return "ds"


# ── derivatives helpers ──────────────────────────────────────────────────────

def find_thumbnail_brief(slug: str) -> dict | None:
    for week_dir in DERIVATIVES_DIR.iterdir():
        if not week_dir.is_dir():
            continue
        for d in week_dir.iterdir():
            if not d.is_dir():
                continue
            brief_path = d / "thumbnail_brief.json"
            norm_slug = slug.replace("_", "-")
            norm_dir = d.name.replace("_", "-")
            if brief_path.exists() and (norm_slug in norm_dir or norm_dir in norm_slug):
                try:
                    return json.loads(brief_path.read_text())
                except json.JSONDecodeError:
                    return None
    return None


def find_yt_title(slug: str) -> str | None:
    """Find youtube title from derivatives/youtube_metadata.json matching slug."""
    for week_dir in DERIVATIVES_DIR.iterdir():
        if not week_dir.is_dir():
            continue
        meta_path = week_dir / slug / "youtube_metadata.json"
        if meta_path.exists():
            data = json.loads(meta_path.read_text())
            return data.get("title", "").strip() or None
    return None


# ── Claude HTML pipeline ─────────────────────────────────────────────────────

THUMBNAIL_SYSTEM = """You are a YouTube thumbnail conversion specialist. Your job is to design thumbnails that drive clicks — thumbnails that stop a viewer mid-scroll on a crowded recommendations feed.

## Brand identity

- Channel: {brand_name} ({handle})
- Fonts: {font_heading} (headings), {font_body} (body)
- Niche tone: {tone}

## Color palette

```
BRAND_PRIMARY  = "{primary}"
BRAND_LIGHT    = "{light}"
BRAND_DARK     = "{dark_color}"
DARK_BG        = "{dark_bg}"
LIGHT_BG       = "{light_bg}"
```

**Important:** For YouTube thumbnails, push saturation higher than brand defaults. Add electric/neon variants of BRAND_PRIMARY when needed for impact. A flat on-brand color that no one clicks is worse than a slightly off-brand color that gets 8% CTR.

## YouTube thumbnail psychology (follow every rule)

### The 120px rule
A thumbnail is viewed at ~120px wide on mobile. Your main headline must be **fully readable at that size**. This means:
- Minimum 100px font size for the main text on a 1280px canvas
- Maximum 4 words in the main headline
- Hard black or near-white text — never mid-tone, never colored text on colored background
- No decorative fonts that blur at small sizes

### The 3-element rule
Effective thumbnails have exactly 3 things that compete for attention — no more:
1. ONE dominant visual (big shape, number, before/after, chart, bold graphic element)
2. ONE headline (max 4 words, massive, high contrast)
3. ONE supporting context element (sub-text, badge, brand mark)
Everything else is noise. Remove it.

### Curiosity gap + emotion
Pick ONE of these proven emotional triggers and design toward it:
- **Mistake/warning:** "You're doing X wrong" energy — red accents, X marks, warning aesthetics
- **Revelation/secret:** "I didn't know this existed" — bright reveal lighting, gradient exposure
- **Number payoff:** Big number that makes you go "wait, really?" — huge isolated stat
- **Before/after contrast:** Side-by-side panels with extreme visual contrast
- **Tutorial authority:** "This is the exact thing you need" — clean code + bold result

### Visual elements that drive clicks
Use these concrete elements (pure CSS, no external images):
- **Giant number callout:** 200-400px isolated stat in a high-contrast circle/slab
- **Diagonal split:** Hard 45° diagonal dividing the canvas into two high-contrast zones
- **Code slab:** Dark terminal block with syntax-highlighted fake code (yellow/green on near-black)
- **Warning badge:** Red/orange hexagon or circle with ⚠ or ✕ symbol
- **Reveal gradient:** One side dark, one side light — text on the transition
- **Chart outline:** Simplified bar/line chart in 3-4 bars using brand colors — readable at 120px

### Colors for impact
- Background: always DARK_BG or near-black
- Main text: pure white `#FFFFFF` or warm white `#F5F0E8` — nothing else
- Accent: BRAND_LIGHT or push it 30% brighter/more saturated than the brand value
- Danger/warning accent: `#FF4444` or `#FF6B35` — use when the emotional trigger is mistake/warning
- Number callout background: high contrast slab — BRAND_PRIMARY at full saturation

## Technical output

Generate a SINGLE, fully self-contained HTML file. No external dependencies except Google Fonts CDN.

- `body {{ margin:0; padding:0; overflow:hidden; width:1280px; height:720px; }}`
- Root `.thumbnail` div exactly 1280×720, overflow:hidden
- All text z-index ≥ 20. All decorative elements z-index ≤ 5.
- No JavaScript. No `position:fixed`. No viewport units.
- Google Fonts: load only {font_heading} and {font_body}

## Brand mark (always include, never let it compete)

Bottom-left corner, small (14-16px): channel initial in a 28px circle (BRAND_PRIMARY fill) + handle text in muted gray. z-index: 30. This must never distract from the main 3 elements.

## Task

{brief_section}

Output the thumbnail HTML immediately. No preamble. Only the HTML.
"""


def build_html_prompt(brand: dict, content: str, brief: dict | None) -> str:
    if brief:
        brief_section = f"""## Thumbnail brief (copy is final — do not rewrite)

main_text: {brief.get('main_text', '')}
sub_text: {brief.get('sub_text', '')}
background_mood: {brief.get('background_mood', '')}
colour_palette: {', '.join(brief.get('colour_palette', []))}

Use these exact words. Your job is design execution only — pick the emotional trigger from the copy and execute it visually."""
    else:
        brief_section = """## Derive thumbnail copy from source content

Rules for copy:
- main_text: MAX 4 words, ALL CAPS, must create curiosity or show a strong outcome/mistake
  Good: "CHARTS THAT ACTUALLY WORK" / "STOP DOING THIS" / "5 CHARTS, 1 HOUR"
  Bad: "Python For Data Science Tutorial" (too long, zero emotion)
- sub_text: one line, 6-10 words, clarifies the payoff or contrasts with main_text
- Pick ONE emotional trigger: mistake/warning OR revelation OR number payoff OR before/after
- Design everything around that single trigger

Read the source content, pick the strongest angle, derive the copy, then build the HTML."""

    system = THUMBNAIL_SYSTEM.format(**brand, brief_section=brief_section)
    return f"{system}\n\n---\n\n## Source content\n\n{content}\n\n---\n\nGenerate the complete thumbnail HTML now.\n"


def run_html_pipeline(slug: str, niche_key: str, content: str, force: bool, export: bool) -> None:
    brand = load_brand(niche_key)
    out_path = THUMBNAIL_DIR / f"{slug}_thumbnail.html"

    if out_path.exists() and not force:
        console.print(f"[warn]HTML exists (--force to overwrite): {out_path.relative_to(REPO)}[/warn]")
        if export:
            _run_playwright_export(out_path, slug)
        return

    brief = find_thumbnail_brief(slug)
    if brief:
        console.print(f"  [html] Brief: {brief.get('main_text', '')} / {brief.get('sub_text', '')}")
    else:
        console.print("  [html] No brief — Claude will derive copy from content")

    console.print(f"[bold][html] Generating[/bold] — {brand['label']}")
    prompt = build_html_prompt(brand, content, brief)
    html = call_claude(
        prompt,
        cache=True,
        model=model_for("html_asset"),
        timeout=300,
        temperature=brand["temperature"],
        normalize=False,
        stream=True,
        progress_label=f"Generating thumbnail HTML ({brand['label']})",
    )

    if "```html" in html:
        start = html.index("```html") + 7
        end = html.index("```", start)
        html_content = html[start:end].strip()
    elif "<!DOCTYPE" in html or "<html" in html:
        html_content = html.strip()
    else:
        html_content = html.strip()

    out_path.write_text(html_content, encoding="utf-8")
    console.print(f"[green][html] Saved:[/green] {out_path.relative_to(REPO)}")

    if export:
        _run_playwright_export(out_path, slug)


def _run_playwright_export(html_path: Path, slug: str) -> None:
    try:
        import asyncio
        from playwright.async_api import async_playwright
    except ImportError:
        console.print("[warn]playwright not installed — run: pip install playwright && playwright install chromium[/warn]")
        return

    VIEW_W, VIEW_H = 1280, 720

    async def _export() -> None:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(
                viewport={"width": VIEW_W, "height": VIEW_H},
                device_scale_factor=1.0,
            )
            await page.set_content(html_path.read_text(encoding="utf-8"), wait_until="networkidle")
            await page.wait_for_timeout(2000)
            await page.evaluate("""() => {
                document.body.style.cssText = 'margin:0;padding:0;overflow:hidden;width:1280px;height:720px;';
                const root = document.querySelector('.thumbnail');
                if (root) root.style.cssText = 'width:1280px;height:720px;overflow:hidden;';
            }""")
            await page.wait_for_timeout(300)
            out_file = THUMBNAIL_DIR / f"{slug}_thumbnail.png"
            await page.screenshot(
                path=str(out_file),
                clip={"x": 0, "y": 0, "width": VIEW_W, "height": VIEW_H},
            )
            console.print(f"[green][html] PNG exported:[/green] {out_file.relative_to(REPO)}")
            await browser.close()

    import asyncio
    asyncio.run(_export())


# ── Remotion pipeline ────────────────────────────────────────────────────────

def _remotion_output_path(slug: str, variant: str) -> Path:
    week = get_iso_week(slug[:10])
    out_dir = REPO / "output" / "visuals" / week
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"{slug}_thumb_{variant}.png"


def run_remotion_pipeline(
    slug: str,
    title: str | None,
    niche: str,
    variants: list[str],
    bg_type: str,
    dry_run: bool,
) -> None:
    if not title:
        title = find_yt_title(slug)
    if not title:
        console.print(f"[warn][remotion] No youtube_metadata.json title found for {slug} — skipping Remotion[/warn]")
        return

    console.print(f"[bold][remotion] title:[/bold] {title}  niche={niche}  bg={bg_type}")

    for variant in variants:
        out = _remotion_output_path(slug, variant)
        props = json.dumps({"titleText": title, "niche": niche, "variant": variant, "bgType": bg_type})
        cmd = ["npx", "remotion", "still", "Thumbnail", str(out), "--props", props]

        tag = "[DRY-RUN] " if dry_run else ""
        console.print(f"  {tag}[remotion] still Thumbnail/{variant} → {out.name}")
        if dry_run:
            continue

        proc = subprocess.run(cmd, cwd=str(REMOTION_DIR))
        if proc.returncode != 0:
            console.print(f"  [remotion] [red]FAIL[/red] variant={variant}")
        else:
            size_kb = out.stat().st_size // 1024 if out.exists() else 0
            console.print(f"  [remotion] [green]OK[/green] variant={variant} — {size_kb} KB → {out.relative_to(REPO)}")


# ── CLI ──────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="Generate YouTube thumbnails via Claude HTML + Remotion")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--blog", type=Path, help="Path to blog markdown file")
    src.add_argument("--topic", type=str, help="Topic string (no existing blog)")
    ap.add_argument("--niche", choices=list(NICHE_MAP.keys()), help="Niche (auto-detected from blog path)")
    # HTML pipeline
    ap.add_argument("--export", action="store_true", help="Export HTML → PNG via Playwright")
    ap.add_argument("--force", action="store_true", help="Overwrite existing HTML output")
    # Remotion pipeline
    ap.add_argument("--variants", nargs="+", default=["a", "b", "c"], choices=["a", "b", "c"])
    ap.add_argument("--bg-type", default="dark", choices=["dark", "gradient", "split"])
    ap.add_argument("--dry-run", action="store_true", help="Print Remotion commands without running")
    # Flow control
    ap.add_argument("--skip-html", action="store_true", help="Skip Claude HTML pipeline")
    ap.add_argument("--skip-remotion", action="store_true", help="Skip Remotion pipeline")
    args = ap.parse_args()

    # Resolve niche key
    if args.niche:
        niche_key = NICHE_MAP[args.niche]
    elif args.blog:
        niche_key = detect_niche_from_path(args.blog)
    else:
        ap.error("--niche required when using --topic")

    # Load content + slug
    if args.blog:
        if not args.blog.exists():
            sys.exit(f"Blog not found: {args.blog}")
        content = args.blog.read_text(encoding="utf-8")
        slug = args.blog.stem
    else:
        content = f"Topic: {args.topic}\n\nGenerate thumbnail content based on this topic."
        slug = slugify(args.topic)

    remotion_niche = infer_remotion_niche(slug)
    console.print(f"[bold]slug:[/bold] {slug}  html_niche={niche_key}  remotion_niche={remotion_niche}")

    if not args.skip_html:
        run_html_pipeline(slug, niche_key, content, args.force, args.export)

    if not args.skip_remotion:
        run_remotion_pipeline(
            slug=slug,
            title=None,
            niche=remotion_niche,
            variants=args.variants,
            bg_type=args.bg_type,
            dry_run=args.dry_run,
        )


if __name__ == "__main__":
    main()
