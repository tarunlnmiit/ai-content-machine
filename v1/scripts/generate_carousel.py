#!/usr/bin/env python3
"""Generate an Instagram carousel HTML from a blog post or topic.

Reads brand kit from data/brand/brand_kit.yaml.
Outputs a self-contained HTML to assets/carousels/{week}/{slug}_carousel.html.
Export to 1080×1350 PNGs via --export (requires playwright).

Usage:
  python3 scripts/generate_carousel.py --blog content/blogs/2026-05-21_data_science_tech_X.md
  python3 scripts/generate_carousel.py --topic "5 Python tricks for data scientists" --niche ds
  python3 scripts/generate_carousel.py --blog path/to/blog.md --export
  python3 scripts/generate_carousel.py --blog path/to/blog.md --slides 7

Slide count defaults to model-decided (5-10, based on content depth) — pass --slides N to
force an exact count. Export always emits exactly as many PNGs as slides exist in the HTML.

Niche shortcuts: ds | life | poetry
"""

import argparse
import base64
import json
import re
import sys
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from _console import console  # noqa: E402
from lib.claude_cli import call_claude  # noqa: E402
from lib.design_system_ref import carousel_reference  # noqa: E402
from lib.niche_config import NICHE_MAP, load_brand_base, model_for  # noqa: E402
from lib.virality import virality_block, project_keys  # noqa: E402
from lib.schedule_calc import get_iso_week  # noqa: E402

BRAND_KIT = REPO / "data" / "brand" / "brand_kit.yaml"
CAROUSEL_DIR = REPO / "assets" / "carousels"
CAROUSEL_DIR.mkdir(parents=True, exist_ok=True)


def slug_week(slug: str) -> str:
    """ISO week bucket for a slug — date-prefixed for --blog runs, else today's week."""
    date_match = re.match(r"^\d{4}-\d{2}-\d{2}", slug)
    return get_iso_week(date_match.group()) if date_match else get_iso_week(date.today().isoformat())

# Carousel-authoritative playbook (LOCAL ONLY / gitignored — never committed).
# When present, it governs hook/structure/tone/caption/pacing over house style;
# the honesty guardrail still holds.
CAROUSEL_PLAYBOOK = REPO / "data" / "kb" / "reels" / "07_carousel_structure_playbook.md"


def load_brand(niche_key: str) -> dict:
    return {**load_brand_base(niche_key), "light_border": "#D6D0C4"}


def detect_niche_from_path(path: Path) -> str:
    name = path.stem.lower()
    if "data_science_tech" in name or "_ds_" in name:
        return "data_science_tech"
    if "life_self_dev" in name or "_life_" in name:
        return "life_self_dev"
    if "poetry_quotes" in name or "_poetry_" in name:
        return "poetry_quotes"
    return "data_science_tech"


CAROUSEL_SYSTEM = """You are an Instagram carousel design system for {brand_name} ({handle}).

## Brand Kit (pre-configured — do not ask for these)

- Handle: {handle}
- Brand name: {brand_name}
- Tone: {tone}
- Font heading: {font_heading}
- Font body: {font_body}
- Font style: {font_style}

## Color Palette (6-token — use exactly these values)

```
BRAND_PRIMARY  = "{primary}"
BRAND_LIGHT    = "{light}"
BRAND_DARK     = "{dark_color}"
LIGHT_BG       = "{light_bg}"
LIGHT_BORDER   = "{light_border}"
DARK_BG        = "{dark_bg}"
```

Brand gradient: `linear-gradient(165deg, {dark_color} 0%, {primary} 50%, {light} 100%)`

## Output format

Return the carousel as HTML text in your reply. Do NOT use any tools, do NOT write or edit
files on disk, and do NOT ask for permission — the calling script captures your stdout and
writes the file itself. Emit the code directly.

Generate a single, fully self-contained HTML file (no external dependencies except Google Fonts CDN).

## REQUIRED CSS class names (export pipeline depends on these — DO NOT rename)

- Outer Instagram frame:    `class="ig-frame"`
- Carousel viewport:        `class="carousel-viewport"`
- Sliding track (flex row): `class="carousel-track"`
- Each individual slide:    `class="slide"` (add modifiers as extra classes, e.g. `class="slide dark"`)
- Progress bar row (in EVERY slide): `<div class="progress-row">` containing one
  `<div class="progress-seg"><div class="fill"></div></div>` per slide in the deck (same N
  segments repeated on every slide). Filled state = the inner `.fill` at `width:100%`.
  The export pipeline sets each slide's progress fill from that slide's own index — do not
  rely on scroll/JS `current` state for the fill; just emit the empty segment structure
  (`.fill` at `width:0%`) per slide and the pipeline bakes the correct fill per slide at
  export time.

JS must translate `.carousel-track` by `translateX(-N * 420px)` where N is slide index.

The carousel must:
- Be exactly 420px wide (ig-frame width)
- Use 4:5 aspect ratio slides (420×525px viewport)
- Alternate LIGHT_BG and DARK_BG backgrounds for visual rhythm
- Include progress bar on every slide (fills as slides progress)
- Include swipe arrow on every slide EXCEPT the last
- Last slide: no arrow, full progress bar, CTA button
- Include Instagram frame wrapper with header, dots, action icons, caption
- Include pointer/touch drag interaction for preview

## REQUIRED ELEMENTS (not optional — CSS rules alone do not satisfy this; the elements must
## actually be placed in the markup on every applicable slide)

- `<span class="follow-tag">Tap to follow →</span>` (wording may vary) — pinned top-right.
  Render this element on EVERY slide EXCEPT the last.
- `<span class="save-tag">Save this post for later</span>` (or "SAVE THIS ↓") — pinned
  bottom-right. Render this element on every content slide.
- Final-slide comment-a-keyword CTA button, per the Carousel Playbook's CTA mechanics (§6).

Defining `.follow-tag`/`.save-tag` CSS but never placing the elements is a failure — both the
CSS rule AND the rendered element on the applicable slides are required.

### Fixed overlay positions (MANDATORY — applies identically to LIGHT and DARK slides)

Every `.slide` is `position:relative`. The overlay elements below are ABSOLUTELY positioned at
EXACT corners with an inset of at least 18px, and NO TWO of them may share a corner or overlap:

- Slide counter badge (e.g. "3 / 8"): **TOP-LEFT** — `top:18px; left:18px;`
- `.follow-tag` ("Tap to follow →"): **TOP-RIGHT** — `top:18px; right:18px;` (opposite corner
  from the badge). Present every slide except the last.
- Swipe arrow (the → circle): **vertically CENTERED on the RIGHT edge** —
  `top:50%; transform:translateY(-50%); right:18px;`. NEVER place it in a bottom corner — that
  frees the bottom-right for the save tag. Present every slide except the last.
- `.save-tag` ("Save this ↓"): **BOTTOM-RIGHT** — `bottom:18px; right:18px;`

Badge (top-left) and follow-tag (top-right) sit in opposite top corners; the swipe arrow is
center-right so it never collides with the bottom-right save-tag. These exact anchors are
required on both light and dark backgrounds.

## Slide sequence ({slide_count_label} slides)

Slide roles, count, hook, structure, tone, caption, and CTA follow the **Carousel Playbook**
above — its structural spine (§1: Cover → Problem/reframe → Credibility/proof → Value body →
Recap/thesis → CTA, including the optional Credibility and Recap slots), its first-3-seconds
law + 6-driver hook taxonomy (§2-3), and its CTA mechanics (§6). {slide_count_target_line}

Visual rhythm (not content): see the Collage Visual System below — it replaces flat LIGHT_BG/
DARK_BG fills with textured/photo collage slides. The final CTA slide (no swipe arrow there) uses
the brand gradient by default — EXCEPT where the niche skin below specifies a different CTA
treatment (Life uses its photo background + scrim on the CTA slide instead of the gradient).

## Components to use

Progress bar, swipe arrow, tag labels, logo lockup (use brand initial '{initial}' in circle),
feature list rows, numbered steps, prompt/quote boxes — exactly as specified in standard carousel design patterns.

Content padding: `0 36px`. Bottom-aligned slides: `0 36px 52px` (clear progress bar).

## Collage Visual System (replaces flat-fill slides — mandatory)

Do NOT ship a slide as a single flat `LIGHT_BG`/`DARK_BG`/gradient field with text typeset
directly on it. Every slide uses a **collage treatment**: a textured or photo background layer,
with content sitting inside rotated, shadowed card/sticker elements on top. This is the primary
fix for "plain, nothing eye-catching" — texture and off-grid placement read as intentional design,
a flat color field reads as a template.

Two techniques, used together on every slide:

1. **Highlight-block typography** — the 1-2 words/numbers that matter most in a headline or line
   of body copy are wrapped in `<span class="hl">...</span>` (or `class="hl orange"` for a second
   accent color) with a solid highlight-color background, `padding:2px 6px`, `border-radius:3px`.
   This is the hierarchy mechanism — which words get a highlight ranks their importance. Do not
   rely on font-size alone for hierarchy.
2. **Rotated card layer** — text content (headline, body copy, stat boxes) sits inside one or more
   `<div>` cards with `transform:rotate(-3deg)` to `rotate(3deg)`, `border-radius`, `box-shadow`,
   slightly overlapping neighboring cards, varied widths. Never grid-aligned, never perfectly
   centered — off-kilter placement is what reads as handmade rather than templated.
3. **Reused doodle set** — define 4-5 small inline `<svg>` motifs once (a star, a squiggle arrow,
   a dot cluster, and 1-2 more from the niche skin below) and reuse the SAME motifs across every
   slide, in different corners/positions. A small reused set reads as a system; scattering random
   clip-art reads as clutter.

{visual_skin}

{asset_instructions}

The REQUIRED CSS class names, fixed overlay positions (badge/follow-tag/swipe-arrow/save-tag),
and progress-bar structure from the sections above are UNCHANGED by this collage system — the
collage layer sits *inside* each `.slide`, on top of or alongside the mandatory overlay elements,
never replacing or covering them.

## Export script

After the HTML, include a fenced Python code block containing the Playwright export script
that exports each slide as 1080×1350px PNG using device_scale_factor=1080/420, targeting the
`assets/carousels/slides/` directory. This is code TEXT for the caller to save — do not run it
or write any files yourself.

## Task

{slide_count_task_line}
Output the complete, copy-pasteable HTML directly in your reply as text — no preamble, no
tool use, no file writes, no asking questions.
"""

# Playbook-recommended slide-count range (floor/ceiling — see 07 §1/§4).
MIN_SLIDES, MAX_SLIDES = 5, 10

# Per-niche collage "skin" — validated against 3 reference IG carousels + 2 proof slides
# (2026-07-16): DS = notebook/torn-card/screenshot style, Life = personal-photo/sticker style,
# Poetry = softer literary notebook variant. Same underlying mechanic (highlight-block + rotated
# cards + doodle set from the Collage Visual System above), different skin per niche.
VISUAL_SKINS = {
    "data_science_tech": """### Niche skin: notebook + torn-card proof (DS)

Background: kraft/notebook paper texture — `repeating-linear-gradient(0deg, transparent 0 27px,
{light_border} 27px 28px)` over `{light_bg}` (or a darker kraft tone for DARK_BG slides).
Doodle set: hand-drawn star outline, a curved arrow, a 3-dot cluster — stroke color {dark_color}.
Proof card (use on value/credibility slides where the content shows a result, metric, or code):
a rotated (-2 to -3deg) white card holding an `<img>`, `border-radius:6px`,
`box-shadow:0 18px 34px rgba(0,0,0,0.28)`, a torn-edge look via
`clip-path:polygon(0% 2%,3% 0%,22% 1%,41% 0%,60% 1%,79% 0%,97% 1%,100% 3%,99% 20%,100% 40%,
99% 60%,100% 80%,99% 97%,97% 100%,78% 99%,60% 100%,40% 99%,21% 100%,3% 99%,0% 97%,1% 80%,
0% 60%,1% 40%,0% 20%)`, and a small rotated washi-tape rectangle overlapping its top edge.""",
    "life_self_dev": """### Niche skin: personal photo + sticker text (Life)

Background: on the hook slide AND the final CTA slide, use the shared `.slide-photo-bg` class
(see asset instructions below) as a full-bleed photo background with a subtle top/bottom gradient
scrim (`linear-gradient(180deg, rgba(20,14,10,0.15) 0%, transparent 30%, transparent 65%,
rgba(20,14,10,0.35) 100%)`) for text legibility — this REPLACES the brand-gradient CTA background
for this niche only (the CTA slide still has no swipe arrow, full progress bar, and the CTA
button, just on the photo+scrim instead of the gradient). Other slides use kraft/cream `{light_bg}`
or `{dark_bg}` per the usual rhythm. Doodle set: star outline, small heart, a squiggle curve —
white stroke on photo slides, {dark_color} elsewhere. Sticker text: instead of one headline block, break
the hook into 2-3 short phrase chunks, each its own rotated pill/sticker
(`background:{primary}` or `{light}`, `border-radius:8px`, `box-shadow:0 8px 18px rgba(0,0,0,0.18)`,
rotate -3 to 2deg), stacked with slight overlap — this is the highlight-block rule applied at
phrase level instead of word level.""",
    "poetry_quotes": """### Niche skin: soft literary notebook (Poetry)

Background: a softer, lighter-contrast notebook/textured-paper wash than the DS skin — same
`repeating-linear-gradient` ruled-line technique but thinner, lower-opacity lines, warm cream tone.
No screenshots, no photo background — poetry stays purely typographic. Doodle set: a feather or
quill outline, a gentle wave/curve line, small dot cluster — soft, minimal, never more than 2
doodles per slide. Highlight-blocks and rotated cards apply as usual, but keep rotation subtle
(-1.5 to 1.5deg) and card shadows soft — the tone is quiet/literary, not busy/loud.""",
}


def _slide_count_strings(slides: int | None) -> dict:
    """Build the three slide-count phrases used in CAROUSEL_SYSTEM.

    slides=None means "let the model decide" within the playbook's 5-10 range,
    based on how much the content actually needs — not a fixed round number.
    """
    if slides is None:
        return {
            "slide_count_label": f"{MIN_SLIDES}-{MAX_SLIDES}, model-selected",
            "slide_count_target_line": (
                f"Choose the slide count ({MIN_SLIDES}-{MAX_SLIDES}) that best fits how much "
                "this content needs — a quick tip earns fewer slides than a full framework. "
                "Don't default to a round number just because it's common."
            ),
            "slide_count_task_line": (
                f"Create an Instagram carousel with the slide count ({MIN_SLIDES}-{MAX_SLIDES}) "
                "that best fits the content below."
            ),
        }
    return {
        "slide_count_label": str(slides),
        "slide_count_target_line": f"Adapt the sequence to the content. {MIN_SLIDES}-{MAX_SLIDES} slides acceptable, {slides} target.",
        "slide_count_task_line": f"Create a {slides}-slide Instagram carousel based on the content below.",
    }


def _asset_instructions(niche_key: str, proof_count: int, has_bg_photo: bool) -> str:
    """Tell Claude whether real-asset placeholder markers are usable this run.

    Claude cannot reliably emit base64 image data as output text (a single screenshot
    is tens of thousands of tokens) — real assets are always injected by the calling
    script AFTER generation, by substring-replacing a literal placeholder marker.
    Claude's only job is to emit the marker in the right spot, or skip the real-asset
    element entirely if no source image was supplied for this run.
    """
    lines = ["### Real-asset placeholders — read carefully\n"]
    lines.append(
        "Do NOT attempt to embed actual image bytes/base64 data yourself — you cannot "
        "reliably produce that much output. Real images are injected by the calling "
        "script AFTER you return, by replacing a literal placeholder string. Your only "
        "job is to place the placeholder marker text exactly where the image belongs."
    )
    if niche_key == "data_science_tech":
        if proof_count > 0:
            markers = ", ".join(f'"__DS_PROOF_{i}__"' for i in range(1, proof_count + 1))
            lines.append(
                f"{proof_count} proof image(s) are available this run. Use up to {proof_count} "
                f"proof card(s) (see niche skin above), setting each `<img>`'s `src` to one of "
                f"these literal placeholder strings, in order, one per card: {markers}. "
                "Do not reuse a marker twice; do not invent new marker names."
            )
        else:
            lines.append(
                "No proof images are available this run — do NOT include a proof-card `<img>` "
                "element at all. Use the notebook/highlight-block/doodle techniques only."
            )
    elif niche_key == "life_self_dev":
        if has_bg_photo:
            lines.append(
                "A background photo is available this run. Define it ONCE in `<style>` as "
                '`.slide-photo-bg{background-image:url("__LIFE_BG__");background-size:cover;'
                'background-position:center 20%;}` — a single occurrence of the marker — then '
                "apply the `slide-photo-bg` class to the slide(s) that use it (typically the "
                "hook and CTA slides). NEVER inline the marker as a per-slide `background-image` "
                "or `<img src>` more than once — that would repeat the same asset payload on "
                "every slide it appears on and bloat the file.\n"
                "CSS COLLISION WARNING (a real failure mode — read carefully): `slide-photo-bg` "
                "must be the ONLY class besides `slide`/`dark`/`light` on that element. Do NOT "
                "add a second custom class (e.g. `photo-bg`) to the same slide, and do NOT write "
                "any other CSS rule targeting that slide (by tag, by another class, or by "
                "`.slide.<anything>`) that sets the `background` SHORTHAND property — a shorthand "
                "`background:` declaration resets `background-image` to `none` even if it's "
                "defined earlier/later or with lower specificity, silently hiding the photo. If "
                "you want a fallback color for a slow image load, put it as `background-color:` "
                "(not `background:`) inside the SAME `.slide-photo-bg` rule, never a separate one."
            )
        else:
            lines.append(
                "No background photo is available this run — do NOT reference `__LIFE_BG__` or "
                "any photo background. Use kraft/cream backgrounds with the sticker-text "
                "technique only."
            )
    else:
        lines.append("No real-asset markers apply to this niche — CSS/SVG techniques only.")
    return "\n".join(lines)


def build_prompt(brand: dict, content: str, slides: int | None,
                 niche_key: str = "life_self_dev", project_key: str | None = None,
                 master_brief: str | None = None, playbook: str | None = None,
                 design_system_ref: str | None = None,
                 proof_count: int = 0, has_bg_photo: bool = False) -> str:
    system = CAROUSEL_SYSTEM.format(
        **brand,
        **_slide_count_strings(slides),
        initial=brand["brand_name"][0].upper(),
        visual_skin=VISUAL_SKINS.get(niche_key, VISUAL_SKINS["life_self_dev"]).format(**brand),
        asset_instructions=_asset_instructions(niche_key, proof_count, has_bg_photo),
    )
    # When the playbook is present it OWNS hook/structure/tone/caption/CTA, so suppress the
    # competing house-style directives that virality_block would otherwise inject.
    virality = virality_block("carousel", niche_key, project_key,
                              suppress_house_style=bool(playbook))
    parts = []
    if playbook:
        parts.append(
            "## Carousel Playbook — AUTHORITATIVE\n\n"
            "This playbook governs hook, structure, tone, caption, pacing, and CTA and "
            "OVERRIDES house VOICE/BANNED-WORDS style wherever anything below conflicts. "
            "Its structural spine (§1), first-3-seconds law + 6-driver hook taxonomy (§2-3), "
            "and CTA mechanics (§6, comment-a-keyword → auto-DM) win over any competing "
            "slide sequence, hook list, or CTA stated later in this prompt. The one thing it "
            "does NOT override: factual honesty about the subject — never claim a feature "
            "that doesn't exist.\n\n"
            + playbook
        )
    parts.append(system)
    if design_system_ref:
        parts.append(design_system_ref)
    parts.append(f"## Virality Directives\n\n{virality}")
    if master_brief:
        if playbook:
            parts.append(
                "## Competition Intelligence (reference only)\n\n"
                "Use the market/competitor intel below. IGNORE any Voice / Banned-words / "
                "Tone / hook-pattern / title rules stated here — the Carousel Playbook above "
                "governs style, hooks, and CTA.\n\n"
                + master_brief
            )
        else:
            parts.append(
                "## Master Brief (creator voice, competition intelligence, what's working)\n\n"
                + master_brief
            )
    parts.append(f"## Source content\n\n{content}")
    parts.append("Generate the complete carousel HTML now.")
    return "\n\n---\n\n".join(parts)


from lib.slug import slugify

# Life-niche collage background photos (see Step 0 proof, 2026-07-16). Round-robin rotation
# state persists in a small JSON file next to the assets so consecutive runs vary the photo
# instead of always landing on the same one (avoids a recurring text-over-face crop).
LIFE_BG_DIR = REPO / "assets" / "brand" / "backgrounds"
LIFE_BG_ROTATION_STATE = LIFE_BG_DIR / ".life_bg_rotation_state.json"


def _life_bg_candidates() -> list[Path]:
    def _index(p: Path) -> int:
        m = re.search(r"_(\d+)\.png$", p.name)
        return int(m.group(1)) if m else 1
    return sorted(LIFE_BG_DIR.glob("life_lifestyle_portrait*.png"), key=_index)


def _next_life_bg_photo() -> Path | None:
    """Round-robin through all life_lifestyle_portrait*.png photos, one per call."""
    candidates = _life_bg_candidates()
    if not candidates:
        return None
    try:
        last_index = json.loads(LIFE_BG_ROTATION_STATE.read_text()).get("last_index", -1)
    except (OSError, ValueError):
        last_index = -1
    next_index = (last_index + 1) % len(candidates)
    LIFE_BG_ROTATION_STATE.write_text(json.dumps({"last_index": next_index}))
    return candidates[next_index]


def _data_uri(path: Path) -> str:
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode()
    return f"data:{mime};base64,{encoded}"


def _inject_assets(html: str, bg_photo: Path | None, proof_images: list[Path]) -> str:
    """Replace real-asset placeholder markers with base64 data-URIs.

    Claude never emits image bytes — it emits literal marker text (`__LIFE_BG__`,
    `__DS_PROOF_N__`) per the asset instructions in build_prompt/_asset_instructions.
    This is the script-side half of that contract: read the source image once,
    base64-encode it, and substitute it into the marker(s) actually present in the
    returned HTML. Mismatches (marker present but no asset given, or vice versa) are
    warned, not fatal — the output still ships, just without that visual element.
    """
    if bg_photo is not None:
        marker = "__LIFE_BG__"
        count = html.count(marker)
        if count == 0:
            console.print("[warn]--bg-photo given but no __LIFE_BG__ marker found in output — skipped[/warn]")
        else:
            if count > 1:
                console.print(f"[warn]__LIFE_BG__ marker appeared {count}x (expected 1) — injecting into all occurrences[/warn]")
            html = html.replace(marker, _data_uri(bg_photo))
            console.print(f"[green]Injected background photo:[/green] {bg_photo.name}")

    for i, img_path in enumerate(proof_images, start=1):
        marker = f"__DS_PROOF_{i}__"
        if marker not in html:
            console.print(f"[warn]--proof-image #{i} given but no {marker} marker found in output — skipped[/warn]")
            continue
        html = html.replace(marker, _data_uri(img_path))
        console.print(f"[green]Injected proof image {i}:[/green] {img_path.name}")

    return html


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate Instagram carousel HTML")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--blog", type=Path, help="Path to existing blog markdown file")
    src.add_argument("--topic", type=str, help="Topic string (no existing blog)")
    ap.add_argument("--niche", choices=list(NICHE_MAP.keys()), help="Niche (auto-detected from blog path)")
    ap.add_argument("--slides", type=int, default=None,
                     help=f"Number of slides (default: model decides, {MIN_SLIDES}-{MAX_SLIDES} based on content)")
    ap.add_argument("--export", action=argparse.BooleanOptionalAction, default=True, help="Run Playwright export after generation (default: on, use --no-export to skip)")
    ap.add_argument("--force", action="store_true", help="Overwrite existing output")
    ap.add_argument("--project", default=None, help="Build-in-public project key (data/kb/projects.json)")
    ap.add_argument("--proof-image", type=Path, action="append", default=[], dest="proof_images",
                     help="DS niche: real screenshot/dashboard image for a torn-card proof slide (repeatable)")
    ap.add_argument("--bg-photo", type=Path, default=None,
                     help="Life niche: real photo for the collage background (default: "
                          "round-robins through assets/brand/backgrounds/life_lifestyle_portrait*.png, "
                          "use --no-bg-photo to disable)")
    ap.add_argument("--no-bg-photo", action="store_true", help="Disable the Life-niche photo background even if default photos exist")
    args = ap.parse_args()

    if args.project and args.project not in project_keys():
        ap.error(f"--project must be one of: {', '.join(project_keys()) or '(none defined)'}")

    # Resolve niche
    if args.niche:
        niche_key = NICHE_MAP[args.niche]
    elif args.blog:
        niche_key = detect_niche_from_path(args.blog)
    else:
        ap.error("--niche required when using --topic")

    brand = load_brand(niche_key)

    # Resolve the Life-niche background photo: explicit --bg-photo wins, else round-robin
    # through the available default photos (unless --no-bg-photo), life_self_dev niche only.
    bg_photo: Path | None = args.bg_photo
    if bg_photo is None and not args.no_bg_photo and niche_key == "life_self_dev":
        bg_photo = _next_life_bg_photo()
    if bg_photo is not None and not bg_photo.exists():
        ap.error(f"--bg-photo not found: {bg_photo}")
    for img in args.proof_images:
        if not img.exists():
            ap.error(f"--proof-image not found: {img}")

    # Load content
    if args.blog:
        if not args.blog.exists():
            sys.exit(f"Blog not found: {args.blog}")
        content = args.blog.read_text(encoding="utf-8")
        slug = args.blog.stem
    else:
        content = f"Topic: {args.topic}\n\nGenerate carousel content based on this topic."
        slug = slugify(args.topic)

    week_dir = CAROUSEL_DIR / slug_week(slug)
    week_dir.mkdir(parents=True, exist_ok=True)
    out_path = week_dir / f"{slug}_carousel.html"
    if out_path.exists() and not args.force:
        console.print(f"[warn]Exists (use --force to overwrite): {out_path.relative_to(REPO)}[/warn]")
        return

    console.print(f"[bold]Generating carousel[/bold] — {brand['label']}")
    slides_desc = args.slides if args.slides is not None else f"model-decided ({MIN_SLIDES}-{MAX_SLIDES})"
    console.print(f"  Niche: {niche_key} | Slides: {slides_desc} | Temp: {brand['temperature']}")

    master_brief_path = REPO / "data" / "kb" / "master_brief.md"
    master_brief = master_brief_path.read_text(encoding="utf-8") if master_brief_path.exists() else None
    if not master_brief:
        console.print("[warn]master_brief.md not found — competition intelligence unavailable[/warn]")

    playbook = CAROUSEL_PLAYBOOK.read_text(encoding="utf-8") if CAROUSEL_PLAYBOOK.exists() else None
    if playbook:
        console.print(f"  Playbook: 07_carousel_structure_playbook.md loaded ({len(playbook):,} chars, authoritative)")
    else:
        console.print("[warn]07_carousel_structure_playbook.md not found — using house style only[/warn]")

    ds_ref = carousel_reference(niche_key)
    if ds_ref:
        console.print(f"  Design system: reference loaded ({len(ds_ref):,} chars)")
    else:
        console.print("[info]Design system mirror not found — prompt runs without grounding block[/info]")

    prompt = build_prompt(brand, content, args.slides, niche_key=niche_key,
                          project_key=args.project, master_brief=master_brief, playbook=playbook,
                          design_system_ref=ds_ref,
                          proof_count=len(args.proof_images), has_bg_photo=bg_photo is not None)

    console.print(f"  Prompt: {len(prompt):,} chars")
    html = call_claude(
        prompt,
        cache=True,
        model=model_for("html_asset"),
        timeout=600,
        temperature=brand["temperature"],
        normalize=False,  # HTML — don't normalize
        stream=True,
        progress_label=f"Generating carousel HTML ({brand['label']})",
    )

    # Extract HTML block if Claude wraps in markdown
    if "```html" in html:
        start = html.index("```html") + 7
        end = html.index("```", start)
        html_content = html[start:end].strip()
    elif "<!DOCTYPE" in html or "<html" in html:
        html_content = html.strip()
    else:
        html_content = html.strip()

    # When Claude doesn't wrap the HTML in a ```html fence, html_content above is the whole
    # raw response — including the trailing ```python export-script block appended after
    # </html>. That block is saved separately below; strip it from the .html file so stray
    # text doesn't leak into the DOM (HTML5 parsing appends stray post-</html> text to body).
    if "```python" in html_content:
        html_content = html_content[: html_content.index("```python")].rstrip()

    html_content = _inject_assets(html_content, bg_photo=bg_photo, proof_images=args.proof_images)

    out_path.write_text(html_content, encoding="utf-8")
    console.print(f"[green]Saved:[/green] {out_path.relative_to(REPO)}")

    # Extract and save export script if present
    if "```python" in html:
        try:
            py_start = html.index("```python") + 9
            py_end = html.index("```", py_start)
            export_script = html[py_start:py_end].strip()
            export_path = week_dir / f"{slug}_export.py"
            export_path.write_text(export_script, encoding="utf-8")
            console.print(f"[green]Export script:[/green] {export_path.relative_to(REPO)}")
        except ValueError:
            pass

    if args.export:
        _run_playwright_export(out_path, slug, args.slides)


def _run_playwright_export(html_path: Path, slug: str, requested_slides: int | None) -> None:
    try:
        import asyncio
        from playwright.async_api import async_playwright
    except ImportError:
        console.print("[warn]playwright not installed — run: pip install playwright && playwright install chromium[/warn]")
        return

    week = slug_week(slug)
    slides_dir = CAROUSEL_DIR / "slides" / week / slug
    slides_dir.mkdir(parents=True, exist_ok=True)

    VIEW_W, VIEW_H = 420, 525
    SCALE = 1080 / 420

    async def _export() -> None:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(
                viewport={"width": VIEW_W, "height": VIEW_H},
                device_scale_factor=SCALE,
            )
            await page.set_content(html_path.read_text(encoding="utf-8"), wait_until="networkidle")
            await page.wait_for_timeout(3000)

            track_info = await page.evaluate("""() => {
                document.querySelectorAll('.ig-header,.ig-dots,.ig-dots-nav,.ig-actions,.ig-caption,.ig-follow,.ig-meta,.ig-sub,.bottom-strip')
                    .forEach(el => el.style.display='none');

                // Find Instagram frame
                const frame = document.querySelector('.ig-frame, .ig-phone, [class*="ig-frame"], [class*="phone"]');
                if (frame) frame.style.cssText = 'width:420px;height:525px;max-width:none;border-radius:0;box-shadow:none;overflow:hidden;margin:0;padding:0;';

                // Find viewport
                const vp = document.querySelector('.carousel-viewport, .carousel-wrap, .slides-viewport, [class*="viewport"], [class*="carousel-wrap"]');
                if (vp) vp.style.cssText = 'width:420px;height:525px;aspect-ratio:unset;overflow:hidden;cursor:default;position:relative;';

                document.body.style.cssText = 'padding:0;margin:0;display:block;overflow:hidden;';

                // Find track: try common names, then generic — any parent of multiple .slide children
                let track = document.querySelector('.carousel-track, .slides-track, .track');
                if (!track) {
                    const slides = document.querySelectorAll('[class*="slide"]:not([class*="slide-num"])');
                    if (slides.length > 1) track = slides[0].parentElement;
                }
                if (track) {
                    track.dataset.__exportTrack = '1';
                    return { found: true, tag: track.tagName, cls: track.className, children: track.children.length };
                }
                return { found: false };
            }""")
            if not track_info.get("found"):
                console.print("[warn]Could not locate carousel track — slides will be duplicates[/warn]")
                total_slides = requested_slides or MAX_SLIDES
                console.print(f"[warn]Falling back to {total_slides} slides (requested count, or {MAX_SLIDES} if none was given)[/warn]")
            else:
                total_slides = track_info["children"]
                console.print(f"  Track: <{track_info['tag'].lower()} class=\"{track_info['cls']}\"> ({total_slides} slides found in HTML — exporting exactly this many)")
            await page.wait_for_timeout(500)

            await page.evaluate("""() => {
                const slides = document.querySelectorAll('[data-__export-track="1"] > *');
                slides.forEach((slide, s) => {
                    const row = slide.querySelector('.progress-row, [class*="progress"]');
                    if (!row) return;
                    const segs = row.querySelectorAll(':scope > *');
                    segs.forEach((seg, i) => {
                        const on = i <= s;
                        seg.classList.toggle('filled', on);
                        seg.classList.toggle('active', on);
                        const fill = seg.querySelector('.fill') || seg.firstElementChild;
                        if (fill && fill !== seg) fill.style.width = on ? '100%' : '0%';
                    });
                });
            }""")

            for i in range(total_slides):
                await page.evaluate("""(idx) => {
                    const track = document.querySelector('[data-__export-track="1"]');
                    if (track) {
                        track.style.transition='none';
                        track.style.transform='translateX('+(-idx*420)+'px)';
                    }
                }""", i)
                await page.wait_for_timeout(400)
                out_file = slides_dir / f"slide_{i+1}.png"
                await page.screenshot(
                    path=str(out_file),
                    clip={"x": 0, "y": 0, "width": VIEW_W, "height": VIEW_H},
                )
                console.print(f"  [green]Exported slide {i+1}/{total_slides}[/green]")

            await browser.close()

    asyncio.run(_export())
    console.print(f"[bold]Slides at:[/bold] {slides_dir.relative_to(REPO)}/")


if __name__ == "__main__":
    main()
