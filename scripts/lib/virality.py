#!/usr/bin/env python3
"""Two-layer virality engine — injects proven hook/CTA/guardrail intelligence into prompts.

Routes each niche to the right knowledge base:
  - poetry / life  -> VOICE KB  (data/kb/voice/)      : emotional, feel-seen, permission
  - data science   -> REELS KB  (data/kb/reels/)      : build/teach archetypes
  - --project set  -> REELS KB + project context (build-in-public)

Reads the KB at runtime so the creator's hand-edits to the .md/.json take effect. Blocks are
COMPACT (names + one-liners, never whole files) to avoid prompt bloat / buffer truncation.

Usage:
    from lib.virality import virality_block
    prompt = virality_block("blog", niche="poetry") + "\\n\\n" + agent_prompt
"""

import json
from pathlib import Path
from typing import Optional

from lib.niche_config import NICHE_MAP

REPO = Path(__file__).resolve().parent.parent.parent
KB = REPO / "data" / "kb"
VOICE_DIR = KB / "voice"
REELS_DIR = KB / "reels"
HOOKS_JSON = KB / "twitter_hook_patterns.json"
PROJECTS_JSON = KB / "projects.json"

# Niches that use the emotional Voice KB (canonical names).
VOICE_NICHES = {"poetry_quotes", "life_self_dev"}

# Short hook key per canonical niche (matches twitter_hook_patterns use_for).
_HOOK_KEY = {"poetry_quotes": "poetry", "life_self_dev": "life", "data_science_tech": "ds"}

# Stable spine — applies to every niche/format. No "proof" wording (tech-only concept).
_SPINE = (
    "VIRALITY SPINE: open with a scroll-stopping hook in the very first line; "
    "be specific over abstract (concrete nouns, numbers, lived moments); "
    "drive exactly ONE clear call-to-action; never overclaim."
)

_FIVE_BEAT = (
    "5-BEAT SHORT STRUCTURE: (1) Hook 0-3s — bold/legible-muted; (2) Problem — name the pain; "
    "(3) Reveal/turn — show it, don't tell; (4) Payoff — why it matters; (5) ONE CTA. "
    "First scene = the hook; final scene = the single CTA."
)

_VOICE_GUARDRAIL = (
    "AUTHENTICITY: no toxic positivity (don't bow real pain with a silver lining), "
    "no manufactured urgency, every personal story must be true, at least one concrete specific "
    "detail, end on permission/naming — not a prescription or hard sell."
)

_TECH_GUARDRAIL = (
    "HONESTY: state only what you can show on screen (never overclaim a tool's ability); "
    "no income-claim headlines; any referenced repo/tool must exist and be linkable."
)

# CTA cue per content type (the ONE action that fits the format).
_CTA = {
    "blog": "CTA: one clear next step (subscribe / read the full piece).",
    "yt_script": "CTA: one spoken action at the end (subscribe / comment a keyword).",
    "carousel": "CTA: the final slide is the single call-to-action (save / share / follow).",
    "slide_deck": "CTA: close on one action.",
    "social_image": "CTA: one action in the caption.",
    "shorts_caption": "CTA: ONE concrete action, not 'subtle' (comment a keyword / read the blog).",
    "shorts_meta": "CTA: description ends with one concrete action.",
    "scene_plan_short": "CTA: the final scene is one keyword/action.",
    "scene_plan_overlay": "CTA: reinforce one action.",
    "clip_select": "Pick clips whose first 3s match a hook archetype and that resolve to one payoff.",
    "thread": "CTA: final post = one link/action.",
    "newsletter": "CTA: one action (reply / read).",
}


def _norm(niche: Optional[str]) -> str:
    return NICHE_MAP.get(niche or "", niche or "")


def is_voice_niche(niche: Optional[str]) -> bool:
    return _norm(niche) in VOICE_NICHES


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _h3_headings(md: str) -> list[str]:
    """Extract '### Name' headings (the archetype names) from a hook-library markdown."""
    out = []
    for line in md.splitlines():
        if line.startswith("### "):
            out.append(line[4:].strip())
    return out


def load_voice_hooks(niche: str) -> list[dict]:
    """Hook categories from twitter_hook_patterns.json applicable to this niche."""
    key = _HOOK_KEY.get(_norm(niche))
    if not key or not HOOKS_JSON.exists():
        return []
    try:
        data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [c for c in data.get("categories", []) if key in c.get("use_for", [])]


def load_project(key: Optional[str]) -> Optional[dict]:
    if not key or not PROJECTS_JSON.exists():
        return None
    try:
        data = json.loads(PROJECTS_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    for p in data.get("projects", []):
        if p.get("key") == key:
            return p
    return None


def project_keys() -> list[str]:
    """All valid project keys from projects.json (for --project validation)."""
    if not PROJECTS_JSON.exists():
        return []
    try:
        data = json.loads(PROJECTS_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [p.get("key") for p in data.get("projects", []) if p.get("key")]


def _project_block(p: dict) -> str:
    angle = ""
    rot = (p.get("cadence") or {}).get("angle_rotation") or []
    if rot:
        angle = f" This week's angle: {rot[0]}."
    return (
        f"PROJECT {p.get('name', p.get('key'))}: {p.get('pitch', '')} "
        f"Guardrail: {p.get('honesty_guardrail', '')} "
        f"CTA keyword: {p.get('dm_keyword', '')}.{angle}"
    )


# Trigger lexicons derived from the hook libraries (voice = emotional; tech = build/teach).
# Used to give candidate topics a small virality lift in idea_scorer.
_VOICE_TRIGGERS = {
    # Original
    "why", "what", "how", "nobody", "everyone", "stop", "never", "always",
    "alone", "loneliness", "grief", "habit", "habits", "fail", "failed", "afraid",
    "enough", "quiet", "honest", "mask", "lonely", "lost", "stay",
    # Fear
    "scared", "terrified", "dying", "broken", "destroyed", "toxic", "abuse",
    "trauma", "danger", "warning", "worst", "fear", "terrible", "nightmare",
    # Curiosity gap
    "secret", "nobody", "hidden", "lied", "actually", "real", "truth", "know",
    "realize", "found", "admit", "confess",
    # FOMO / urgency
    "before", "missing", "wasted", "regret", "late", "mistake", "wrong", "already",
    # Strong emotion
    "hate", "angry", "hurt", "betrayed", "abandoned", "unloved", "pain", "ache",
    "empty", "numb", "hollow", "rage", "shattered",
}
_TECH_TRIGGERS = {
    "free", "vs", "secret", "ways", "way", "build", "built", "automate", "automated",
    "top", "guide", "mcp", "claude", "tokens", "token", "local", "agent", "skill",
}


def topic_virality_multiplier(
    title: str, niche: Optional[str], past_keywords: Optional[set] = None
) -> float:
    """Score a candidate topic for viral potential. Returns a multiplier ~[1.0, 1.55].

    - hook-signal: title contains a niche-appropriate trigger word (voice vs tech).
    - past-performer: token overlap with what has actually performed (past_keywords),
      cross-niche and data-grounded.
    """
    words = {w.strip(".,:!?\"'").lower() for w in (title or "").split()}
    triggers = _VOICE_TRIGGERS if is_voice_niche(niche) else _TECH_TRIGGERS
    mult = 1.0
    if words & triggers:
        mult += 0.25 if is_voice_niche(niche) else 0.15
    if past_keywords:
        overlap = len(words & past_keywords)
        mult += min(0.40, 0.08 * overlap)
    return mult


def virality_block(content_type: str, niche: Optional[str], project_key: Optional[str] = None) -> str:
    """Compact virality instruction block for a generator prompt.

    Routes poetry/life -> Voice KB, ds/project -> Reels KB. Returns "" if KB is unavailable.
    """
    parts: list[str] = [_SPINE]

    if is_voice_niche(niche):
        # Emotional layer (always for poetry/life — never the tech KB, even with a project;
        # the project block still appends below). Prefer voice/01 archetype names.
        archetypes = _h3_headings(_read(VOICE_DIR / "01_hook_library.md"))
        if not archetypes:
            archetypes = [c["name"] for c in load_voice_hooks(niche)]
        if archetypes:
            parts.append("EMOTIONAL HOOKS (pick one, test 2-3): " + "; ".join(archetypes[:6]) + ".")
        parts.append(_VOICE_GUARDRAIL)
    else:
        # Tech/build layer (ds, or any niche when a project is set).
        archetypes = _h3_headings(_read(REELS_DIR / "01_hook_library.md"))
        if archetypes:
            parts.append("BUILD/TEACH HOOKS (pick one): " + "; ".join(archetypes[:6]) + ".")
        parts.append(_TECH_GUARDRAIL)

    if content_type in ("clip_select", "scene_plan_short"):
        parts.append(_FIVE_BEAT)

    proj = load_project(project_key)
    if proj:
        parts.append(_project_block(proj))

    cta = _CTA.get(content_type)
    if cta:
        parts.append(cta)

    return "\n".join(parts)
