#!/usr/bin/env python3
"""Compact design-system grounding text for Claude prompts (carousel, worksheet).

Sourced from the same repo files that feed v1/design-system/ (the read-only mirror
bundle synced to the "Breath Network Design System" claude.ai/design project) —
brand_kit.yaml via lib.niche_config.load_brand_base, and the worksheet shell's
:root token block. This module does NOT read v1/design-system/ card HTML itself
(the mirror is generated FROM these sources — reading it back would be circular
noise); the directory is only checked as the fail-soft gate, since if the mirror
is missing there are no cards for a human to QA output against.

Entry points:
  carousel_reference(niche_key) -> str   (generate_carousel.py)
  worksheet_reference() -> str           (generate_worksheet_html.py)

Both return "" if v1/design-system/ is missing or a source can't be read —
callers then behave exactly as before this reference existed.
"""

import re
from pathlib import Path

from lib.niche_config import load_brand_base

REPO = Path(__file__).resolve().parent.parent.parent
DESIGN_SYSTEM_DIR = REPO / "design-system"
WORKSHEET_SHELL = REPO / "scripts" / "templates" / "worksheet_shell.html"

_QA_NOTE = (
    "\n\nThese are grounding notes, not the full visual spec — the rendered reference "
    'cards live in the "Breath Network Design System" claude.ai/design project; QA '
    "output against those cards, not just this text."
)

_HEADER = "## DESIGN SYSTEM REFERENCE (grounding — tokens are law, no off-palette colors)\n\n"


_COLLAGE_SKIN_NOTE = {
    "data_science_tech": (
        "notebook/kraft-paper texture with torn-edge screenshot proof-cards "
        "(rotated, drop-shadowed, washi-tape accent) — reads technical/credible"
    ),
    "life_self_dev": (
        "personal-photo background on hook/CTA slides with rotated sticker-highlight "
        "text blocks — reads personal/narrative"
    ),
    "poetry_quotes": (
        "softer literary notebook texture, no screenshots or photos, subtle rotation "
        "and quiet doodles — stays purely typographic"
    ),
}


def carousel_reference(niche_key: str) -> str:
    """Archetype spine + collage-skin note for the niche. "" if mirror absent."""
    if not DESIGN_SYSTEM_DIR.exists():
        return ""
    try:
        brand = load_brand_base(niche_key)
    except Exception:
        return ""
    gradient = (
        f"linear-gradient(165deg, {brand['dark_color']} 0%, "
        f"{brand['primary']} 50%, {brand['light']} 100%)"
    )
    skin_note = _COLLAGE_SKIN_NOTE.get(niche_key, _COLLAGE_SKIN_NOTE["life_self_dev"])
    return (
        _HEADER
        + "Slide-role archetype spine (see the Carousel Archetypes cards). Every slide uses "
        + "the Collage Visual System (highlight-block hierarchy + rotated card layer + reused "
        + f"doodle set, per-niche skin — this niche: {skin_note}), never a flat solid-color "
        + "field:\n"
        + "- Hook slide: LIGHT_BG collage, uppercase kicker + bold hook headline with "
        + "highlight-block emphasis; the headline is the biggest thing on the slide.\n"
        + "- Body slide(s): DARK_BG collage, kicker + short body copy — one idea per slide, "
        + "progress bar grows slide by slide.\n"
        + f"- CTA slide (final): brand gradient `{gradient}`, no swipe arrow, full "
        + f"progress bar, CTA button referencing {brand['handle']}"
        + (" — EXCEPT Life, whose CTA slide uses its photo background + scrim instead of "
           "the gradient (see niche skin above)." if niche_key == "life_self_dev" else ".")
        + "\n"
        + "Alternate LIGHT_BG / DARK_BG collage slides between hook and CTA for rhythm; the "
        + "gradient is reserved for emphasis + the final CTA slide (photo+scrim for Life)."
        + _QA_NOTE
    )


def worksheet_reference() -> str:
    """Breath Network shell token-vocabulary guard. "" if mirror or shell absent."""
    if not DESIGN_SYSTEM_DIR.exists() or not WORKSHEET_SHELL.exists():
        return ""
    try:
        text = WORKSHEET_SHELL.read_text(encoding="utf-8")
    except OSError:
        return ""
    match = re.search(r":root\s*\{(.*?)\}", text, re.S)
    if not match:
        return ""
    pairs = re.findall(r"(--[\w-]+):\s*([^;]+);", match.group(1))
    color_tokens = ", ".join(f"{k}={v.strip()}" for k, v in pairs if not k.startswith("--font"))
    if not color_tokens:
        return ""
    return (
        _HEADER
        + "Stay strictly on the Breath Network worksheet shell spec — the fixed shell "
        + "template already carries all CSS. Your content_html must never introduce new "
        + "hex values, inline styles, or colors outside the shell's ink/bone/sky/ochre/ember "
        + f"vocabulary: {color_tokens}."
        + _QA_NOTE
    )
