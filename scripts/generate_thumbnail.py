#!/usr/bin/env python3
"""Generate YouTube thumbnail via three pipelines:

  1. Canva AI (MCP)  → output/visuals/{week}/{slug}_thumb_canva.png  [--canva]
  2. Claude → HTML → Playwright PNG  → assets/thumbnails/{slug}_thumbnail.png
  3. Remotion still Thumbnail         → output/visuals/{week}/{slug}_thumb_{variant}.png

Default (no flags): runs HTML + Remotion pipelines.
Use --canva to run Canva AI pipeline (recommended — produces face+hook thumbnails).

Usage:
    # Canva AI (new, recommended):
    python3 scripts/generate_thumbnail.py --blog content/blogs/2026-W25/2026-06-16_...md --canva
    python3 scripts/generate_thumbnail.py --blog ... --canva --hook "Setup That Breaks Everything"
    python3 scripts/generate_thumbnail.py --blog ... --canva --face assets/raw/2026-W25/thumbs/{slug}_face_01.jpg

    # HTML + Remotion (existing):
    python3 scripts/generate_thumbnail.py --blog content/blogs/2026-W25/2026-06-16_...md
    python3 scripts/generate_thumbnail.py --blog path/to/blog.md --export
    python3 scripts/generate_thumbnail.py --topic "5 Python tricks" --niche ds
    python3 scripts/generate_thumbnail.py --blog ... --variants a b --bg-type gradient
    python3 scripts/generate_thumbnail.py --blog ... --skip-remotion
    python3 scripts/generate_thumbnail.py --blog ... --skip-html

Canva pipeline requires the `claude` CLI in PATH with Canva MCP configured.
CTR targets: Canva+face ≥ 5% | HTML-only ~1.5% | Remotion text-only ~0.5%
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
from lib.virality import caption_formula_digest  # noqa: E402
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
            norm_slug = slug.replace("_", "-")
            norm_dir = d.name.replace("_", "-")
            if not (norm_slug in norm_dir or norm_dir in norm_slug):
                continue
            for brief_name in ("thumbnail_brief.json", "claude_design_brief.json"):
                brief_path = d / brief_name
                if brief_path.exists():
                    try:
                        return json.loads(brief_path.read_text())
                    except json.JSONDecodeError:
                        return None
    return None


def _derivatives_slug(slug: str) -> str:
    """Strip format suffixes (_yt, _reel, _blog) added by script filenames."""
    import re
    return re.sub(r"_(yt|reel|blog|short)$", "", slug)


def find_yt_title(slug: str) -> str | None:
    """Find youtube title from derivatives/youtube_metadata.json matching slug."""
    lookup = _derivatives_slug(slug)
    for week_dir in DERIVATIVES_DIR.iterdir():
        if not week_dir.is_dir():
            continue
        meta_path = week_dir / lookup / "youtube_metadata.json"
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


def build_html_prompt(brand: dict, content: str, brief: dict | None,
                      niche_key: str | None = None) -> str:
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

        digest = caption_formula_digest(niche_key)
        if digest:
            brief_section += (
                "\n\n## Per-niche thumbnail rule (authoritative — from the niche caption formula)\n\n"
                + digest
                + "\n\n(Apply the 'thumbnail:' rule above: DS = state the OUTCOME not the topic; "
                "Life = a declarative text-wall claim, not a question; "
                "Poetry = the first line of the poem as a standalone scroll-stopping phrase.)"
            )

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
    prompt = build_html_prompt(brand, content, brief, niche_key)
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


# ── Canva AI pipeline ───────────────────────────────────────────────────────

CANVA_BRAND_KIT_ID = "kAHIa-g_t3o"  # "Deep Breath" brand kit

# Niche → Canva design context (mirrors data/brand/brand_kit.yaml)
_CANVA_NICHE_CFG: dict[str, dict] = {
    "data_science_tech": {
        "short": "ds",
        "brand": "Breath of Data Science",
        "channel": "@breathofdatascience",
        "accent": "#6B8FA8",
        "pop": "#f97316",
        "font": "Space Grotesk",
        "style": "technical, sharp, modern tech YouTuber — Fireship / TechLead energy",
    },
    "life_self_dev": {
        "short": "life",
        "brand": "Breath of Life",
        "channel": "@breathoflife_",
        "accent": "#E8705A",
        "pop": "#f59e0b",
        "font": "Lora + Nunito Sans",
        "style": "warm, personal, story-driven — journal entry that grabs you",
    },
    "poetry_quotes": {
        "short": "poetry",
        "brand": "Breath of Poetry",
        "channel": "@breathofpoetry",
        "accent": "#B89850",
        "pop": "#a78bfa",
        "font": "Playfair Display",
        "style": "editorial, premium, literary — poetry book cover",
    },
}


def _canva_query(niche_key: str, hook: str, face_path: Path | None) -> str:
    """Build detailed Canva AI query with brand + CTR requirements."""
    cfg = _CANVA_NICHE_CFG.get(niche_key, _CANVA_NICHE_CFG["data_science_tech"])
    face_part = (
        "Composite a provided face photo (surprised / shocked reaction expression) "
        "prominently — 40–60% of the frame, left or right side."
        if face_path
        else "Leave a prominent clear zone (40–60% of frame, left or right) "
             "with contrasting bg for a face photo to be added manually."
    )
    return (
        f"YouTube thumbnail for '{cfg['brand']}' channel ({cfg['channel']}). "
        f"Hook text (DOMINANT — must fill ≥35% of canvas width, bold, huge): \"{hook}\". "
        f"Background: #1E1B2E dark navy. Accent: {cfg['accent']}. Pop color: {cfg['pop']}. "
        f"Font: {cfg['font']}, extra-bold. "
        f"Visual style: {cfg['style']}. "
        f"{face_part} "
        f"Left/right split composition: face one side, giant hook text other side. "
        f"NO diagrams. NO charts. NO framework boxes. NO 'Tutorial X/Y' numbering. "
        f"Hook text readable at 120px wide (mobile thumbnail size). "
        f"Modern, high-contrast, 5%+ CTR design."
    )


def _canva_claude_prompt(niche_key: str, hook: str, slug: str, out_path: Path, face_path: Path | None) -> str:
    """Prompt for claude --print to execute Canva MCP calls and produce the thumbnail."""
    query = _canva_query(niche_key, hook, face_path)
    face_step = (
        f"\n   - asset_ids: upload the face photo at {face_path} first, get asset ID, pass here"
        if face_path and face_path.exists()
        else ""
    )
    return f"""Generate a YouTube thumbnail using the Canva MCP.

CANVA QUERY:
{query}

EXECUTE these steps in order:
1. Call generate-design with:
   - design_type: "youtube_thumbnail"
   - brand_kit_id: "{CANVA_BRAND_KIT_ID}"{face_step}
   - query: the CANVA QUERY above
   (do NOT use generate-design-structured — that is presentations only)

2. From the returned candidates, pick the one that best shows:
   - Dark navy background
   - Large bold hook text dominating one side
   - Clear face zone on the other side

3. Call create-design-from-candidate with the chosen candidate_id and job_id.

4. Call export-design with:
   - design_id from step 3
   - format: {{"type": "png", "width": 1280, "height": 720, "export_quality": "pro"}}

5. Output:
   - PNG download URL → user saves to: {out_path}
   - Canva edit URL → user opens to swap in reaction face photo
   - Design ID for future edits
"""


def run_canva_pipeline(
    slug: str,
    niche_key: str,
    hook: str | None,
    face_path: Path | None,
    week: str,
    dry_run: bool,
) -> None:
    """Generate thumbnail via Canva AI (calls claude --print with Canva MCP)."""
    cfg = _CANVA_NICHE_CFG.get(niche_key, _CANVA_NICHE_CFG["data_science_tech"])

    # Resolve hook text
    if not hook:
        yt_title = find_yt_title(slug)
        hook = yt_title[:40] if yt_title else "The Mistake Everyone Makes"
        console.print(f"  [canva] No --hook provided — using: \"{hook}\"")
        console.print("  [canva] Tip: pass --hook \"3-5 words\" for best CTR")

    # Validate face photo
    if face_path and not face_path.exists():
        console.print(f"  [canva] [warn]--face path not found: {face_path} — continuing without[/warn]")
        face_path = None

    # Build output paths
    out_dir = REPO / "output" / "visuals" / week
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{slug}_thumb_canva.png"
    prompt_path = out_dir / f"{slug}_thumb_canva_prompt.md"
    brief_path = out_dir / f"{slug}_thumb_canva_brief.json"

    # Write brief JSON (audit trail)
    import json as _json
    brief = {
        "niche": niche_key,
        "hook": hook,
        "week": week,
        "slug": slug,
        "face": str(face_path) if face_path else None,
        "output_path": str(out_path),
        "brand_kit_id": CANVA_BRAND_KIT_ID,
        "canva_query": _canva_query(niche_key, hook, face_path),
    }
    brief_path.write_text(_json.dumps(brief, indent=2))

    # Write the Claude prompt for reuse
    claude_prompt = _canva_claude_prompt(niche_key, hook, slug, out_path, face_path)
    prompt_path.write_text(
        f"# Canva Thumbnail Prompt — {slug}\n\n"
        f"Niche: {cfg['brand']} | Hook: {hook}\n\n"
        f"Paste into Claude Cowork or run via `claude --print`:\n\n"
        f"```\n{claude_prompt}\n```\n"
    )

    console.print(f"[bold][canva] Generating thumbnail[/bold] — {cfg['brand']} | hook: \"{hook}\"")
    if face_path:
        console.print(f"  [canva] Face photo: {face_path}")
    console.print(f"  [canva] Output target: {out_path.relative_to(REPO)}")

    if dry_run:
        console.print(f"\n[canva] [DRY-RUN] Claude prompt saved to: {prompt_path.relative_to(REPO)}")
        console.print(f"[canva] [DRY-RUN] Run manually: claude --print < {prompt_path}")
        return

    # Try claude CLI (requires claude in PATH + Canva MCP configured)
    claude_bin = subprocess.run(["which", "claude"], capture_output=True, text=True).stdout.strip()
    if not claude_bin:
        console.print("[canva] [warn]`claude` CLI not in PATH — writing prompt for manual execution[/warn]")
        _canva_manual_instructions(prompt_path, out_path, slug)
        return

    console.print("  [canva] Running via `claude --print` ...")
    result = subprocess.run(
        ["claude", "--print", claude_prompt],
        capture_output=True,
        text=True,
        timeout=180,
    )

    if result.returncode == 0:
        console.print(result.stdout)
        console.print(f"\n[green][canva] Done.[/green] Download URL above → save to {out_path.relative_to(REPO)}")
        console.print("[canva] Open the Canva edit URL to swap in your face reaction photo.")
    else:
        console.print(f"[canva] [red]claude CLI failed (exit {result.returncode})[/red]")
        if result.stderr:
            console.print(result.stderr[:500])
        _canva_manual_instructions(prompt_path, out_path, slug)


def _canva_manual_instructions(prompt_path: Path, out_path: Path, slug: str) -> None:
    console.print(f"\n[canva] Manual fallback:")
    console.print(f"  1. Open Claude Cowork")
    console.print(f'  2. Say: "generate thumbnail for {slug} — use the brief at {prompt_path.relative_to(REPO)}"')
    console.print(f"  3. Save the exported PNG to: {out_path.relative_to(REPO)}")


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
    ap = argparse.ArgumentParser(
        description="Generate YouTube thumbnails via Canva AI, Claude HTML, or Remotion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--blog", type=Path, help="Path to blog markdown file")
    src.add_argument("--topic", type=str, help="Topic string (no existing blog)")
    ap.add_argument("--niche", choices=list(NICHE_MAP.keys()), help="Niche (auto-detected from blog path)")
    # Canva pipeline (new)
    ap.add_argument("--canva", action="store_true", help="Run Canva AI pipeline (recommended for CTR)")
    ap.add_argument("--hook", type=str, default=None, help="3-5 word hook text for Canva thumbnail")
    ap.add_argument("--face", type=Path, default=None, help="Reaction photo for Canva composite (Mode B)")
    ap.add_argument("--week", type=str, default=None, help="ISO week override for Canva output, e.g. 2026-W25")
    # HTML pipeline
    ap.add_argument("--export", action="store_true", help="Export HTML → PNG via Playwright")
    ap.add_argument("--force", action="store_true", help="Overwrite existing HTML output")
    # Remotion pipeline
    ap.add_argument("--variants", nargs="+", default=["a", "b", "c"], choices=["a", "b", "c"])
    ap.add_argument("--bg-type", default="dark", choices=["dark", "gradient", "split"])
    ap.add_argument("--dry-run", action="store_true", help="Dry-run (print commands, don't execute)")
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

    # Resolve ISO week for Canva output
    week = args.week or get_iso_week(slug[:10])

    remotion_niche = infer_remotion_niche(slug)
    console.print(f"[bold]slug:[/bold] {slug}  niche={niche_key}  week={week}")

    # ── Canva AI pipeline ────────────────────────────────────────────────────
    if args.canva:
        run_canva_pipeline(
            slug=slug,
            niche_key=niche_key,
            hook=args.hook,
            face_path=args.face,
            week=week,
            dry_run=args.dry_run,
        )
        # Canva pipeline is standalone — skip HTML+Remotion unless explicitly requested
        if not (args.force or not args.skip_html or not args.skip_remotion):
            return

    # ── HTML + Remotion pipelines ────────────────────────────────────────────
    if not args.canva or args.force:
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
