#!/usr/bin/env python3
"""Single source of truth for niche identity, brand loading, and model routing.

Why: NICHE_MAP was copy-pasted across 8 scripts, load_brand across 4 (with
per-script extras), and model ids were hardcoded in several places. Centralize
the identical parts here; callers extend load_brand_base with their own extras.

Usage:
    from lib.niche_config import NICHE_MAP, load_brand_base, model_for, CREATOR_VOICE
"""

from pathlib import Path
from typing import Optional

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
BRAND_KIT_FILE = REPO / "data" / "brand" / "brand_kit.yaml"

# Short alias + canonical name → canonical niche key.
NICHE_MAP = {
    "ds": "data_science_tech",
    "life": "life_self_dev",
    "poetry": "poetry_quotes",
    "data_science_tech": "data_science_tech",
    "life_self_dev": "life_self_dev",
    "poetry_quotes": "poetry_quotes",
}

CREATOR_VOICE = """
You are writing for Tarun Gupta — 10-year data scientist and content creator.
Voice: analytical but warm, personal examples, no jargon without context.
BANNED WORDS: "In conclusion", "Dive into", "Leverage", "Game-changer", "Synergy".
"""

# Current model ids (see CLAUDE.md / claude-api skill).
FABLE = "claude-fable-5"    # Mythos-class, above Opus — premium limits, minutes-long turns
OPUS = "claude-opus-4-8"
OPUS_5 = "claude-opus-5"    # current Opus — drop-in upgrade from 4.8 at the same pricing
SONNET = "claude-sonnet-5"  # near-Opus coding/agentic quality at Sonnet-tier limits
HAIKU = "claude-haiku-4-5-20251001"

# Task → model routing (Max 5x). Override per-call where a script needs to.
# Opus 4.8 on quality-critical LOW-VOLUME tasks (burns limits fast, long turns).
MODEL_BY_TASK = {
    "hero_blog": OPUS_5,       # produce_blog, ghostwrite — flagship long-form, weekly, quality-critical
    "buffer": SONNET,          # bulk drafts, lower stakes
    "repurpose": SONNET,       # mechanical transform of existing text
    "html_asset": SONNET,      # slides / carousel / social / thumbnail
    "scene_plan": SONNET,      # structured semantic reasoning
    "metadata": HAIKU,         # small classification / hashtags / throwaway
    "shorts_meta": SONNET,     # generate_shorts_meta — user-facing titles/descriptions, drives CTR
    "beat_html": SONNET,       # hf_beat_builder — highest-volume call; Sonnet 5 ≈ Opus on this shape
    "storyboard": OPUS,        # storyboard_gen — beat list from transcript
    "reel_script": OPUS,       # prepare_reel_script — script generation, quality matters
    "reel_hook": SONNET,       # prepare_reel_script — hook selection; first 3s decide everything
    "custom_scene": SONNET,    # generate_custom_scene — TSX codegen; better model = fewer tsc retries
    "retrofit": SONNET,        # retrofit_scene_triggers — transcript trigger re-anchoring
    "analytics_summary": HAIKU,  # collect_analytics — weekly numbers → bullets, mechanical
}


def model_for(task: str, niche: Optional[str] = None) -> str:
    """Return the model id for a pipeline task.

    Everything follows MODEL_BY_TASK (hero_blog included — Opus 5).
    Unknown tasks fall back to Sonnet.
    """
    return MODEL_BY_TASK.get(task, SONNET)


def _load_kit() -> dict:
    return yaml.safe_load(BRAND_KIT_FILE.read_text())


def load_niche_config() -> tuple[dict, dict]:
    """Per-niche AutoTune temperatures and models from brand_kit.yaml."""
    if not BRAND_KIT_FILE.exists():
        return {}, {}
    niches = _load_kit().get("niches", {})
    temps = {k: v.get("claude_temperature") for k, v in niches.items()}
    models = {k: v.get("claude_model") for k, v in niches.items()}
    return temps, models


def load_brand_base(niche_key: str) -> dict:
    """Common brand dict shared by carousel/slide/social/thumbnail generators.

    Callers extend the returned dict with their own extras (e.g. light_border,
    decorative_cue) so output stays byte-identical to the pre-refactor scripts.
    """
    kit = _load_kit()
    niche = kit["niches"][niche_key]
    colors = kit["colors"]
    return {
        "creator": kit["creator"],
        "handle": niche.get("handle", kit["handle"]),
        "brand_name": niche["brand_name"],
        "primary": niche["primary_color"],
        "light": niche["light_color"],
        "dark_color": niche["dark_color"],
        "light_bg": colors["cream"],
        "dark_bg": colors["background"],
        "font_heading": niche["font_heading"],
        "font_body": niche["font_body"],
        "font_style": niche["font_style"],
        "tone": niche["tone"],
        "temperature": niche["claude_temperature"],
        "label": niche["label"],
    }
