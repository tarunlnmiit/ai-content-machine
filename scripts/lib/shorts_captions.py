#!/usr/bin/env python3
"""Generate per-shot social captions + hashtags for Shorts/Reels.

Used by clip_shorts.py and render_shorts_batch.py after video output.
Writes a Markdown file mapping each shot to platform captions.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from lib.claude_cli import call_claude
from lib.hashtags import build_hashtags
from lib.virality import virality_block

NICHE_TEMPERATURES = {"ds": 0.4, "life": 0.85, "poetry": 1.15}

NICHE_VOICES = {
    "ds": (
        "Data Science & Tech creator. Voice: analytical but warm, concrete examples, "
        "no jargon without explanation. Audience: aspiring data scientists, Python learners."
    ),
    "life": (
        "Life & Self-Development creator. Voice: warm, personal, reflective. "
        "Audience: people working on habits, productivity, and personal growth."
    ),
    "poetry": (
        "Poetry & Quotes creator. Voice: lyrical, evocative, emotionally resonant. "
        "Audience: readers who love words, metaphor, and emotional depth."
    ),
}

BANNED_WORDS = '"In conclusion", "Dive into", "Leverage", "Game-changer", "Synergy"'


def detect_niche(slug: str) -> str:
    s = slug.lower()
    if "data_science" in s or "data-science" in s or "python" in s or "_tech" in s:
        return "ds"
    if "poetry" in s or "quotes" in s:
        return "poetry"
    return "life"


def _build_prompt(hook_text: str, niche: str, shot_index: int,
                  project_key: str | None = None) -> str:
    voice = NICHE_VOICES.get(niche, NICHE_VOICES["life"])
    virality = virality_block("shorts_caption", niche, project_key)
    return f"""You are writing social media captions for a Shorts/Reels video clip.

{virality}

Creator context: {voice}
Banned words: {BANNED_WORDS}

SELF-CONTAINED: This caption, title, and description must read standalone. The
viewer may never have seen the long-form or any sibling short. Never write "part
N", "continued", "in the previous short", or "watch the full video to
understand". Sell THIS clip as a complete piece. (A CTA pointing to the full
video for MORE is fine; requiring it to UNDERSTAND is not.)

This is shot #{shot_index + 1}. The clip's hook / opening line:
"{hook_text}"

Write captions for 3 platforms. Return ONLY valid JSON, no markdown, no explanation:
{{
  "instagram": {{
    "caption": "Hook line + 2-3 sentence body. Conversational, value-forward.",
    "hashtags": ["tag1", "tag2", "tag3"]
  }},
  "youtube_shorts": {{
    "title": "Under 60 characters. Hook in first 3 words.",
    "description": "2-3 punchy sentences ending with ONE concrete CTA (e.g. 'Read the full piece', 'Comment a keyword') — not vague.",
    "hashtags": ["Shorts", "tag1", "tag2"]
  }},
  "threads": {{
    "caption": "One punchy sentence. Max 280 chars.",
    "hashtags": ["tag1", "tag2"]
  }}
}}"""


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def generate_shot_captions(hook_text: str, niche: str, shot_index: int,
                           project_key: str | None = None) -> dict | None:
    """Call Claude and return {instagram, youtube_shorts, threads} dict. None on failure."""
    temperature = NICHE_TEMPERATURES.get(niche, 0.85)
    prompt = _build_prompt(hook_text, niche, shot_index, project_key)

    for attempt in range(2):
        if attempt == 1:
            prompt = (
                "Return ONLY a raw JSON object. No markdown. No explanation. "
                "Start with { and end with }.\n\n" + prompt
            )
        try:
            raw = call_claude(
                prompt,
                cache=True,
                timeout=90,
                temperature=temperature,
                progress_label=f"captions shot {shot_index + 1}",
            )
            data = _extract_json(raw)
            # Merge Claude hashtags with niche pool per platform
            for platform in ("instagram", "youtube_shorts", "threads"):
                plat_data = data.get(platform, {})
                claude_tags = plat_data.get("hashtags", [])
                plat_data["hashtags"] = build_hashtags(niche, platform, claude_tags)
            return data
        except (json.JSONDecodeError, RuntimeError) as e:
            if attempt == 0:
                continue
            print(f"  [captions] shot {shot_index + 1} failed: {e}")
            return None
    return None


def _format_md(slug: str, shots: list[dict]) -> str:
    lines = [
        f"# Shorts Captions — {slug}",
        f"Generated: {date.today().isoformat()}",
        "",
    ]
    for shot in shots:
        idx = shot["index"]
        hook = shot.get("hook_text", "")[:100]
        captions = shot.get("captions")

        lines += ["---", "", f'## Shot {idx + 1:02d} — "{hook}"', ""]

        if not captions:
            lines += ["_Caption generation failed for this shot._", ""]
            continue

        ig = captions.get("instagram", {})
        ig_tags = " ".join(f"#{t}" for t in ig.get("hashtags", []))
        lines += [
            "### Instagram Reels",
            ig.get("caption", ""),
            "",
            ig_tags,
            "",
        ]

        yt = captions.get("youtube_shorts", {})
        yt_tags = ", ".join(yt.get("hashtags", []))
        lines += [
            "### YouTube Shorts",
            f"**Title:** {yt.get('title', '')}",
            f"**Description:** {yt.get('description', '')}",
            f"**Tags:** {yt_tags}",
            "",
        ]

        th = captions.get("threads", {})
        th_tags = " ".join(f"#{t}" for t in th.get("hashtags", []))
        lines += [
            "### Threads / Twitter",
            f"{th.get('caption', '')} {th_tags}".strip(),
            "",
        ]

    return "\n".join(lines)


def generate_and_write_captions(
    shots: list[dict],
    slug: str,
    niche: str,
    out_path: Path,
    project_key: str | None = None,
) -> Path:
    """Generate captions for all shots and write .md file.

    shots: list of {"index": int, "hook_text": str}
    Returns out_path.
    """
    print(f"\n[captions] generating for {len(shots)} shot(s)…")
    enriched = []
    for shot in shots:
        print(f"  shot {shot['index'] + 1}/{len(shots)}: {shot.get('hook_text', '')[:60]}")
        captions = generate_shot_captions(shot["hook_text"], niche, shot["index"], project_key)
        enriched.append({**shot, "captions": captions})

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(_format_md(slug, enriched), encoding="utf-8")
    print(f"[captions] → {out_path}")
    return out_path
