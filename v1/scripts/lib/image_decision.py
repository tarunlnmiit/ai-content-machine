"""Decide whether a blog is better served by an AI-generated editorial image or a
stock photo — and, when AI wins, emit a ready-to-paste prompt per image slot.

Uses the shared Claude CLI. Returns a structured dict; the caller routes the
stock-fetch vs AI-prompt path and records the decision in the manual-steps sidecar.
"""

from __future__ import annotations

import json
import re

from lib.claude_cli import call_claude

# Per-niche brand direction for the AI image prompt (matches the worksheet/thumbnail palettes).
_NICHE_ART = {
    "ds": "dark-luxury editorial tech; near-black navy (#0A0E1A) background, single electric-cyan (#00D4FF) accent",
    "life": "warm editorial; deep warm shadows, soft amber (#FF6B35) accent, intimate and human",
    "poetry": "moody literary; ink-navy (#18152A) background, candlelight-gold (#B89850) accent, atmospheric",
}

_MARKER_RE = re.compile(r"\[IMAGE_INSERT:\s*([^|\]]+?)\s*(?:\|\s*([^\]]*))?\]")


def parse_markers(blog_text: str) -> list[dict]:
    """Extract IMAGE_INSERT slots → [{search, caption}]."""
    out = []
    for m in _MARKER_RE.finditer(blog_text):
        out.append({"search": (m.group(1) or "").strip(), "caption": (m.group(2) or "").strip()})
    return out


def decide_image(blog_text: str, niche: str, markers: list[dict], force: str | None = None) -> dict:
    """Return {recommendation: 'ai'|'stock', reason: str, prompts: [{slot, prompt}]}.

    `prompts` is populated only when recommendation == 'ai' (one per marker).
    `force` overrides the recommendation: 'stock' skips the model call; 'ai' requires
    the model to produce a prompt for every slot.
    """
    if not markers:
        return {"recommendation": "stock", "reason": "no image slots", "prompts": []}
    if force == "stock":
        return {"recommendation": "stock", "reason": "forced (--image stock)", "prompts": []}

    art = _NICHE_ART.get(niche, _NICHE_ART["ds"])
    force_line = (
        "\nThe user REQUIRES an AI image — set recommendation to \"ai\" and write a prompt for every slot.\n"
        if force == "ai" else ""
    )
    slots = "\n".join(
        f"  {i+1}. search='{m['search']}' caption='{m['caption']}'" for i, m in enumerate(markers)
    )
    prompt = f"""\
You are an art director for Tarun Gupta's blog (niche: {niche}). Decide whether THIS
post is better served by an AI-generated editorial image or by a stock photo.

Prefer AI when the post is conceptual/abstract, brand-specific, or benefits from a
single strong metaphor stock can't capture. Prefer STOCK when a literal real-world
photo (a person, a place, a concrete object) reads more authentic and AI would look
generic or uncanny.{force_line}

Blog (excerpt):
<<<BLOG
{blog_text[:6000]}
BLOG

Image slots needed ({len(markers)}):
{slots}

If you choose AI, write ONE editorial prompt per slot in this art direction:
{art}; cinematic, premium-magazine quality; NO text, NO logos, NO human faces;
include scene, style, palette, composition (leave negative space for a headline),
and a NEGATIVE PROMPTS line.

Return ONLY a JSON object:
{{
  "recommendation": "ai" | "stock",
  "reason": "one or two sentences",
  "prompts": [ {{ "slot": "<the slot's caption or search>", "prompt": "<full image prompt>" }} ]
}}
If recommendation is "stock", return "prompts": []. No markdown fences, just JSON.
"""
    try:
        raw = call_claude(prompt, cache=True, timeout=120, temperature=0.6,
                          progress_label="image art-direction")
        raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
        raw = re.sub(r"\s*```$", "", raw)
        data = json.loads(raw)
    except Exception as e:  # noqa: BLE001 — never block the blog on this
        return {"recommendation": "stock", "reason": f"decision failed ({e}); defaulting to stock", "prompts": []}

    rec = "ai" if str(data.get("recommendation", "")).lower() == "ai" else "stock"
    return {
        "recommendation": rec,
        "reason": data.get("reason", ""),
        "prompts": data.get("prompts", []) if rec == "ai" else [],
    }
