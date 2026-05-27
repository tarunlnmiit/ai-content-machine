#!/usr/bin/env python3
"""Generate 4-week content buffer from data/buffer/topics.yaml.

For each topic:
  1. YouTube script
  2. Substack post (blog)
  3. Social copy bundle (Twitter thread + LinkedIn + Instagram)

Saves to content/buffer/week-{N}/{niche}/ and syncs to Notion (status=Script).

Usage:
  python3 scripts/generate_buffer.py
  python3 scripts/generate_buffer.py --dry-run       # preview only, no files/Notion
  python3 scripts/generate_buffer.py --week 2        # single week
  python3 scripts/generate_buffer.py --niche ds      # single niche (ds|life|poetry)
  python3 scripts/generate_buffer.py --no-notion     # generate files, skip Notion
  python3 scripts/generate_buffer.py --force         # overwrite existing files

Env (for Notion sync):
  NOTION_INTEGRATION_SECRET
  NOTION_CONTENTS_DB_ID
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

import requests
import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from _console import console, spinner  # noqa: E402
from lib.claude_cli import call_claude  # noqa: E402
from lib.text_normalizer import normalize as stm_normalize  # noqa: E402

BRAND_KIT_FILE = REPO / "data" / "brand" / "brand_kit.yaml"

def _load_niche_config() -> tuple[dict, dict]:
    """Load per-niche AutoTune temperatures and models from brand_kit.yaml."""
    if not BRAND_KIT_FILE.exists():
        return {}, {}
    kit = yaml.safe_load(BRAND_KIT_FILE.read_text())
    niches = kit.get("niches", {})
    temps = {k: v.get("claude_temperature") for k, v in niches.items()}
    models = {k: v.get("claude_model") for k, v in niches.items()}
    return temps, models

NICHE_TEMPS, NICHE_MODELS = _load_niche_config()

TOPICS_FILE = REPO / "data" / "buffer" / "topics.yaml"
KB_FILE = REPO / "data" / "kb" / "master_brief.md"
BUFFER_DIR = REPO / "content" / "buffer"

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
BUFFER_STATUS = "Script"

NICHE_LABELS = {
    "data_science_tech": "Data Science/Tech",
    "life_self_dev": "Life & Self-Development",
    "poetry_quotes": "Poetry/Quotes",
}

NICHE_TO_TOPIC = {
    "data_science_tech": "Tech",
    "life_self_dev": "Life",
    "poetry_quotes": "Poetry",
}

NICHE_KEYS = {
    "ds": "data_science_tech",
    "life": "life_self_dev",
    "poetry": "poetry_quotes",
}

CREATOR_VOICE = """
You are writing for Tarun Gupta — 10-year data scientist and content creator.
Voice: analytical but warm, personal examples, no jargon without context.
BANNED WORDS: "In conclusion", "Dive into", "Leverage", "Game-changer", "Synergy".
"""


# ── Prompt builders ──────────────────────────────────────────────────────────

def youtube_script_prompt(niche: str, topic: str, angle: str, kb: str) -> str:
    label = NICHE_LABELS[niche]
    is_poetry = niche == "poetry_quotes"

    if is_poetry:
        format_note = (
            "Format: YouTube Short / Reel script.\n"
            "Structure: Hook (0-3s spoken line) → Poem body (60-90s) → CTA.\n"
            "Word count: 150-250 words total.\n"
            "Tone: lyrical, atmospheric, emotionally resonant."
        )
    else:
        format_note = (
            "Format: YouTube video script (8-12 minutes).\n"
            "Structure: Hook (30s) → Problem/Context (1min) → Main content (6-8min, "
            "3-4 sections with examples) → Takeaway (1min) → CTA (30s).\n"
            "Include [B-ROLL] and [SCREEN RECORDING] cues where relevant.\n"
            "Tone: conversational, data-backed, personal examples."
        )

    return f"""{CREATOR_VOICE}

## Knowledge Base
{kb}

## Task: YouTube Script

Niche: {label}
Topic: {topic}
Angle: {angle}

{format_note}

Write the complete script now. No preamble.
"""


def substack_prompt(niche: str, topic: str, angle: str, kb: str) -> str:
    label = NICHE_LABELS[niche]
    is_poetry = niche == "poetry_quotes"

    if is_poetry:
        word_note = "800-1000 words. Lyrical economy — every line earns its place."
    else:
        word_note = "1200-1800 words. Data-backed, personal examples, actionable."

    return f"""{CREATOR_VOICE}

## Knowledge Base
{kb}

## Task: Substack / Blog Post

Niche: {label}
Topic: {topic}
Angle: {angle}

Word count: {word_note}
Structure: Headline → Hook → Context → 3-4 main sections → Takeaway → CTA.
Include a compelling subject line at the top (for Substack email).

Write the complete post now. No preamble.
"""


def social_copy_prompt(niche: str, topic: str, angle: str, kb: str) -> str:
    label = NICHE_LABELS[niche]

    return f"""{CREATOR_VOICE}

## Knowledge Base
{kb}

## Task: Social Copy Bundle

Niche: {label}
Topic: {topic}
Angle: {angle}

Generate all three in sequence, clearly labelled:

---
### TWITTER THREAD
- 5-8 tweets
- Tweet 1: hook (max 280 chars, no hashtags)
- Tweets 2-7: one insight each, concrete
- Final tweet: CTA or reflection
- Add (1/N) numbering

---
### LINKEDIN POST
- 150-250 words
- Opens with a bold statement, not a question
- 3-4 short paragraphs
- 3-5 relevant hashtags at end

---
### INSTAGRAM CAPTION
- 100-150 words
- Hook in first line (visible before "more")
- Personal, warm tone
- 5-8 hashtags at end

Write all three now. No preamble.
"""


# ── File I/O ─────────────────────────────────────────────────────────────────

def save_content(week: int, niche: str, topic: str, content_type: str, text: str, force: bool) -> Path:
    slug = topic.lower().strip().replace(" ", "-")[:50]
    out_dir = BUFFER_DIR / f"week-{week}" / niche
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{slug}_{content_type}.md"

    if path.exists() and not force:
        console.print(f"  [dim]skip (exists): {path.relative_to(REPO)}[/dim]")
        return path

    path.write_text(text, encoding="utf-8")
    console.print(f"  [green]saved:[/green] {path.relative_to(REPO)}")
    return path


def write_meta(week: int, niche: str, topic: str, angle: str, force: bool) -> None:
    slug = topic.lower().strip().replace(" ", "-")[:50]
    out_dir = BUFFER_DIR / f"week-{week}" / niche
    out_dir.mkdir(parents=True, exist_ok=True)
    meta_path = out_dir / f"{slug}_meta.md"

    if meta_path.exists() and not force:
        return

    meta_path.write_text(
        f"# {topic}\n\n**Niche:** {NICHE_LABELS[niche]}\n**Week:** {week}\n**Angle:** {angle}\n**Status:** Buffer\n",
        encoding="utf-8",
    )


# ── Notion sync ──────────────────────────────────────────────────────────────

def load_env() -> tuple[str, str]:
    env_file = REPO / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip('"'))

    token = os.environ.get("NOTION_INTEGRATION_SECRET", "")
    db_id = os.environ.get("NOTION_CONTENTS_DB_ID", "")
    return token, db_id


def notion_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def fetch_existing_titles(token: str, db_id: str) -> set[str]:
    seen: set[str] = set()
    payload: dict = {"page_size": 100}
    while True:
        r = requests.post(
            f"{NOTION_API}/databases/{db_id}/query",
            headers=notion_headers(token),
            json=payload,
            timeout=15,
        )
        if r.status_code != 200:
            console.print(f"  [warn]Notion query failed {r.status_code}[/warn]")
            return seen
        data = r.json()
        for page in data.get("results", []):
            for prop in page.get("properties", {}).values():
                if prop.get("type") == "title":
                    for chunk in prop.get("title", []):
                        seen.add(chunk.get("plain_text", "").lower().strip())
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]
    return seen


def get_db_schema(token: str, db_id: str) -> dict:
    r = requests.get(
        f"{NOTION_API}/databases/{db_id}",
        headers=notion_headers(token),
        timeout=10,
    )
    r.raise_for_status()
    return r.json().get("properties", {})


def detect_prop_map(schema: dict) -> dict:
    out = {"title": None, "status": None, "topic": None, "description": None}
    for name, meta in schema.items():
        t = meta.get("type")
        lname = name.lower()
        if t == "title" and not out["title"]:
            out["title"] = name
        elif t in ("status", "select") and "status" in lname and not out["status"]:
            out["status"] = (name, t)
        elif t == "select" and "topic" in lname and not out["topic"]:
            out["topic"] = name
        elif t in ("rich_text", "text") and "desc" in lname and not out["description"]:
            out["description"] = name
    return out


def create_notion_page(
    token: str,
    db_id: str,
    prop_map: dict,
    niche: str,
    topic: str,
    angle: str,
    week: int,
) -> Optional[str]:
    props: dict = {}

    if prop_map["title"]:
        props[prop_map["title"]] = {
            "title": [{"text": {"content": f"[W{week}] {topic}"}}]
        }

    if prop_map["status"]:
        name, ptype = prop_map["status"]
        props[name] = {ptype: {"name": BUFFER_STATUS}}

    if prop_map["topic"]:
        topic_val = NICHE_TO_TOPIC.get(niche, "")
        if topic_val:
            props[prop_map["topic"]] = {"select": {"name": topic_val}}

    if prop_map["description"]:
        desc = f"Buffer Week {week} | Angle: {angle}"
        props[prop_map["description"]] = {
            "rich_text": [{"text": {"content": desc}}]
        }

    r = requests.post(
        f"{NOTION_API}/pages",
        headers=notion_headers(token),
        json={"parent": {"database_id": db_id}, "properties": props},
        timeout=15,
    )
    if r.status_code in (200, 201):
        return r.json().get("id")
    console.print(f"  [warn]Notion create failed {r.status_code}: {r.text[:200]}[/warn]")
    return None


# ── Core generation ───────────────────────────────────────────────────────────

def generate_topic(
    week: int,
    niche: str,
    topic: str,
    angle: str,
    kb: str,
    dry_run: bool,
    force: bool,
    no_notion: bool,
    notion_state: Optional[dict],
) -> None:
    label = NICHE_LABELS[niche]
    console.print(f"\n[bold cyan]Week {week} · {label}[/bold cyan]")
    console.print(f"  Topic: {topic}")
    console.print(f"  Angle: {angle}")

    if dry_run:
        console.print("  [dim](dry-run — skipping generation)[/dim]")
        return

    write_meta(week, niche, topic, angle, force)

    temp = NICHE_TEMPS.get(niche)
    model = NICHE_MODELS.get(niche)

    with spinner(f"YouTube script..."):
        yt_script = call_claude(
            youtube_script_prompt(niche, topic, angle, kb),
            cache=True,
            timeout=300,
            temperature=temp,
            model=model,
        )
        yt_script = stm_normalize(yt_script)
    save_content(week, niche, topic, "youtube_script", yt_script, force)

    with spinner(f"Substack post..."):
        sub_post = call_claude(
            substack_prompt(niche, topic, angle, kb),
            cache=True,
            timeout=300,
            temperature=temp,
            model=model,
        )
        sub_post = stm_normalize(sub_post)
    save_content(week, niche, topic, "substack_post", sub_post, force)

    with spinner(f"Social copy..."):
        social = call_claude(
            social_copy_prompt(niche, topic, angle, kb),
            cache=True,
            timeout=180,
            temperature=temp,
            model=model,
        )
        social = stm_normalize(social)
    save_content(week, niche, topic, "social_copy", social, force)

    if no_notion or notion_state is None:
        return

    title_key = f"[w{week}] {topic}".lower().strip()
    if title_key in notion_state["existing"]:
        console.print("  [dim]Notion: already exists, skipped[/dim]")
        return

    page_id = create_notion_page(
        notion_state["token"],
        notion_state["db_id"],
        notion_state["prop_map"],
        niche,
        topic,
        angle,
        week,
    )
    if page_id:
        console.print(f"  [green]Notion: created page {page_id[:8]}...[/green]")
        notion_state["existing"].add(title_key)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="Generate 4-week content buffer")
    ap.add_argument("--dry-run", action="store_true", help="Preview only, no files or Notion")
    ap.add_argument("--week", type=int, choices=[1, 2, 3, 4], help="Process single week")
    ap.add_argument("--niche", choices=["ds", "life", "poetry"], help="Process single niche")
    ap.add_argument("--no-notion", action="store_true", help="Skip Notion sync")
    ap.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = ap.parse_args()

    if not TOPICS_FILE.exists():
        sys.exit(f"Missing topics file: {TOPICS_FILE}")

    data = yaml.safe_load(TOPICS_FILE.read_text())
    weeks = data.get("weeks", [])

    kb = KB_FILE.read_text(encoding="utf-8") if KB_FILE.exists() else ""

    # Notion setup
    notion_state = None
    if not args.no_notion and not args.dry_run:
        token, db_id = load_env()
        if token and db_id:
            try:
                schema = get_db_schema(token, db_id)
                prop_map = detect_prop_map(schema)
                existing = fetch_existing_titles(token, db_id)
                notion_state = {
                    "token": token,
                    "db_id": db_id,
                    "prop_map": prop_map,
                    "existing": existing,
                }
                console.print(f"[dim]Notion: connected, {len(existing)} existing pages[/dim]")
            except Exception as e:
                console.print(f"[warn]Notion setup failed: {e} — skipping sync[/warn]")
        else:
            console.print("[warn]Notion creds missing — skipping sync[/warn]")

    niche_filter = NICHE_KEYS.get(args.niche) if args.niche else None

    total = generated = skipped = 0

    for week_data in weeks:
        week_num = week_data.get("week")
        if args.week and week_num != args.week:
            continue

        for niche_key in ["data_science_tech", "life_self_dev", "poetry_quotes"]:
            if niche_filter and niche_filter != niche_key:
                continue

            entry = week_data.get(niche_key, {}) or {}
            topic = (entry.get("topic") or "").strip()
            angle = (entry.get("angle") or "").strip()

            total += 1

            if not topic:
                console.print(f"\n[dim]Week {week_num} · {NICHE_LABELS[niche_key]}: empty — skip[/dim]")
                skipped += 1
                continue

            try:
                generate_topic(
                    week=week_num,
                    niche=niche_key,
                    topic=topic,
                    angle=angle,
                    kb=kb,
                    dry_run=args.dry_run,
                    force=args.force,
                    no_notion=args.no_notion,
                    notion_state=notion_state,
                )
                generated += 1
            except Exception as e:
                console.print(f"  [error]Failed: {e}[/error]")
                skipped += 1

    console.print(f"\n[bold]Done.[/bold] {generated}/{total} generated, {skipped} skipped.")
    if not args.dry_run and generated:
        console.print(f"Files at: {BUFFER_DIR.relative_to(REPO)}/")


if __name__ == "__main__":
    main()
