#!/usr/bin/env python3
"""Generate Instagram Reel brief for a piece of content.

For each blog slug, produces:
  content/derivatives/{week}/{slug}/ig_reel_brief.md

The brief contains:
  - Account routing (@breathofdatascience or @mistakenlyhuman)
  - 3 hook options (specific, irresistible — not vague)
  - Best clip timestamps (from SRT if available)
  - Instagram caption (100-150 words)
  - DM keyword for CTA ("Comment X and I'll send you the link")
  - 5 hashtags

Pipeline position: run AFTER clip_shorts.py has cut the clips.

Usage:
  python3 scripts/generate_ig_reel_brief.py --slug 2026-05-25_data_science_tech_python-for-data-science-tutorial-210 --week 2026-W22
  python3 scripts/generate_ig_reel_brief.py --week 2026-W22        # all 3 niches
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.claude_cli import call_claude  # noqa: E402
from lib.niche_config import model_for  # noqa: E402
from lib.virality import virality_block  # noqa: E402


# ── Account routing ────────────────────────────────────────────────────────────

NICHE_TO_ACCOUNT = {
    "data_science_tech": "@breathofdatascience",
    "life_self_dev":     "@mistakenlyhuman",
    "poetry_quotes":     "@mistakenlyhuman",
}

NICHE_TO_FORMAT = {
    "data_science_tech": "tutorial-clip",      # screen recording + talking head clip
    "life_self_dev":     "talking-head",       # personal story, analytical-human angle
    "poetry_quotes":     "spoken-word",        # spoken word over hyperframe video
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def detect_niche(slug: str) -> str | None:
    """Detect niche from slug filename."""
    for niche in NICHE_TO_ACCOUNT:
        if niche in slug:
            return niche
    return None


def read_blog(week: str, slug: str) -> str:
    path = REPO / "content" / "blogs" / week / f"{slug}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    # Try matching by partial name
    blog_dir = REPO / "content" / "blogs" / week
    for f in blog_dir.glob(f"*{slug[:40]}*.md"):
        return f.read_text(encoding="utf-8")
    return ""


def read_srt(week: str, slug: str) -> str:
    """Read SRT from video/edited folder if available."""
    edited = REPO / "assets" / "video" / "edited"
    for srt in (edited / week).glob(f"*{slug[:40]}*.srt"):
        return srt.read_text(encoding="utf-8")
    # Also check without week subfolder
    for srt in edited.glob(f"*{slug[:40]}*.srt"):
        return srt.read_text(encoding="utf-8")
    return ""


def shorts_exist(week: str, slug: str) -> list[str]:
    """List any already-cut shorts for this slug."""
    shorts_dir = REPO / "assets" / "video" / "edited" / "shorts"
    found = []
    for f in shorts_dir.glob(f"*{slug[:40]}*short*.mp4") if shorts_dir.exists() else []:
        found.append(f.name)
    # Also check hyperframes
    hf_dir = REPO / "assets" / "hyperframes" / week
    for f in (hf_dir.glob(f"*short*.mp4") if hf_dir.exists() else []):
        if slug[:30] in f.name or slug[:30].replace("_", "-") in f.name:
            found.append(f.name)
    return found


# ── Claude prompt ──────────────────────────────────────────────────────────────

BRIEF_PROMPT = """You are writing an Instagram Reel brief for a content creator.

Creator: Tarun Gupta (@{account})
Niche: {niche_label}
Content format: {fmt}
Blog title / topic: extracted below

HOOK PRINCIPLES (non-negotiable):
- Every hook must be SPECIFIC. A number, a result, a named consequence — not a vague promise.
- The hook must make the next 3 seconds feel inevitable to watch. Not fear. Not exaggeration. Just specificity that creates genuine curiosity.
- Bad: "This Python mistake will ruin your code." Good: "Python concatenated my strings instead of adding them — no error, just a wrong answer I trusted for a week."
- Bad: "Men don't talk about mental health." Good: "I called my parents drowning in anxiety. They said: 'First find another job before quitting.'"
- Hooks for DS: lead with the specific error, result, or before/after. Hooks for Life: lead with the specific moment, not the lesson.

CAPTION RULES (niche-specific — the virality formula above is authoritative):
- DS: Caption IS the product. Line 1 = 'Comment KEYWORD and I'll send you [deliverable] 👆'. Then the full steps/prompts/tools verbatim as a numbered list. NOT a teaser. Longer than 150 words is fine when the value requires it. Honesty guardrail: claim only what's shown.
- Life: Extract the single most precise mechanism insight and make it the entire caption (Mode C). OR write a 5-sentence essay+vulnerability for heavy emotional topics. Close flat/instructional — no motivational crescendo. Product NEVER in caption.
- Poetry: Full poem verbatim (save trigger — people screenshot and send it). OR a single devastating line + emoji. NEVER explain the poem in the caption. Permission close outperforms sad close.
- All niches: No banned words: "In conclusion", "Dive into", "Leverage", "Game-changer", "Synergy"

DM KEYWORD:
- DS: One word tied to the tool/outcome (e.g. FLOW, PROMPTS, SETUP, CLAUDE). Drives the comment→DM CTA that makes comment count exceed like count.
- Life: Use for product/resource delivery only (e.g. BOOK, SYSTEM). Not for every post.
- Poetry: Use for seasonal/relational pieces (e.g. VOWS for wedding poems). Otherwise no keyword.
- Must relate directly to the content.

HASHTAGS: 5 tags. Mix: 2 mid-tier niche (50K–500K posts), 2 broad niche, 1 branded.
- DS: #python, #datascience, #learnpython, #pythontutorial, #breathofdatascience
- Life: #mentalhealth, #selfawareness, #personalgrowth, #mistakenlyhuman (branded)
- Poetry: #poetry, #poetrylovers, #poem, #breathofpoetry (branded)

---

BLOG CONTENT (first 3000 chars):
{blog_excerpt}

{srt_section}

---

Return ONLY valid JSON. No prose before or after. Schema:
{{
  "account": "@breathofdatascience or @mistakenlyhuman",
  "format": "tutorial-clip | talking-head | spoken-word",
  "hooks": [
    {{"option": 1, "text": "...", "strength_note": "why this works"}},
    {{"option": 2, "text": "...", "strength_note": "why this works"}},
    {{"option": 3, "text": "...", "strength_note": "why this works"}}
  ],
  "best_clip_timestamps": [
    {{"start": "MM:SS", "end": "MM:SS", "why": "..."}}
  ],
  "caption": "...",
  "dm_keyword": "WORD",
  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "posting_note": "one-line tip specific to this piece"
}}
"""


def build_prompt(account: str, niche: str, blog: str, srt: str,
                 project_key: str | None = None,
                 master_brief: str | None = None) -> str:
    niche_labels = {
        "data_science_tech": "Data Science / Tech (@breathofdatascience)",
        "life_self_dev":     "Life & Self-Development (@mistakenlyhuman)",
        "poetry_quotes":     "Poetry / Quotes (@mistakenlyhuman)",
    }
    fmt = NICHE_TO_FORMAT.get(niche, "talking-head")
    srt_section = ""
    if srt:
        lines = srt.strip().split("\n")[:120]  # first ~4 min of captions
        srt_section = "SRT TRANSCRIPT (first 4 minutes):\n" + "\n".join(lines)

    prompt = BRIEF_PROMPT.format(
        account=account,
        niche_label=niche_labels.get(niche, niche),
        fmt=fmt,
        blog_excerpt=blog[:3000],
        srt_section=srt_section,
    )

    # Per-niche caption/thumbnail virality formula (mavgpt for DS, voice formulas for life/poetry).
    virality = virality_block("instagram_caption", niche, project_key)
    if virality:
        prompt = (
            "## Virality / caption formula (this niche — apply to the caption + hook)\n\n"
            + virality + "\n\n" + prompt
        )

    # Competition intelligence + what's working — gives context for hook angle selection.
    if master_brief:
        prompt = (
            "## Master Brief (creator voice, competition, what's working June 2026)\n\n"
            + master_brief + "\n\n" + prompt
        )

    return prompt


# ── Output formatter ───────────────────────────────────────────────────────────

def brief_to_markdown(data: dict, slug: str, week: str, niche: str, existing_shorts: list[str]) -> str:
    hooks_md = "\n".join(
        f"**Option {h['option']}:** {h['text']}\n> _{h.get('strength_note', '')}_"
        for h in data.get("hooks", [])
    )
    timestamps_md = "\n".join(
        f"- `{t['start']} → {t['end']}` — {t.get('why', '')}"
        for t in data.get("best_clip_timestamps", [])
    )
    shorts_md = ""
    if existing_shorts:
        shorts_md = "\n### Already-cut clips\n" + "\n".join(f"- `{s}`" for s in existing_shorts[:6])

    hashtags = " ".join(data.get("hashtags", []))
    clip_cmd = (
        f"python3 scripts/clip_shorts.py \\\n"
        f"  --slug {slug} \\\n"
        f"  --count 3"
    )
    if niche == "data_science_tech":
        clip_cmd += " \\\n  --smart-crop"

    return f"""# Instagram Reel Brief — {slug}

**Week:** {week}
**Account:** {data.get('account', NICHE_TO_ACCOUNT.get(niche, '?'))}
**Format:** {data.get('format', NICHE_TO_FORMAT.get(niche, '?'))}

---

## Hooks (pick one — use as first spoken line AND as text overlay)

{hooks_md}

---

## Best clip timestamps

{timestamps_md if timestamps_md else "_Run clip_shorts.py to auto-identify clips._"}
{shorts_md}

---

## Instagram caption

```
{data.get('caption', '')}

Comment **{data.get('dm_keyword', 'LINK')}** and I'll send you the full post. 👇
{hashtags}
```

---

## DM keyword

`{data.get('dm_keyword', 'LINK')}` — set this in SuperProfile/CreatorFlow as the trigger word.

---

## Production command

```bash
# 1. Cut clips (if not already done)
{clip_cmd}

# 2. Clips output to:
#    assets/video/edited/shorts/{slug}_short_00.mp4  (and _01, _02)

# 3. Add trending audio in CapCut or Instagram native editor before posting
```

---

## Posting note

{data.get('posting_note', '')}

---

_Generated by generate_ig_reel_brief.py — edit hooks/caption to match your voice before posting._
"""


# ── Main ───────────────────────────────────────────────────────────────────────

def process_slug(week: str, slug: str, project_key: str | None = None,
                 master_brief: str | None = None) -> bool:
    niche = detect_niche(slug)
    if not niche:
        print(f"  ⚠ Could not detect niche for {slug} — skipping")
        return False

    account = NICHE_TO_ACCOUNT[niche]
    print(f"\n→ {slug}")
    print(f"  niche: {niche} | account: {account}")

    blog = read_blog(week, slug)
    if not blog:
        print(f"  ⚠ Blog not found for {slug}")
        return False

    srt = read_srt(week, slug)
    existing_shorts = shorts_exist(week, slug)
    if existing_shorts:
        print(f"  clips already exist: {len(existing_shorts)}")

    prompt = build_prompt(account, niche, blog, srt, project_key, master_brief=master_brief)
    print("  calling Claude…")
    try:
        raw = call_claude(prompt, cache=True, model=model_for("scene_plan"), timeout=120).strip()
    except RuntimeError as e:
        print(f"  Claude error: {e}")
        return False

    # Parse JSON
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        print(f"  ⚠ No JSON in Claude output:\n{raw[:300]}")
        return False
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        print(f"  ⚠ JSON parse error: {e}")
        return False

    # Write brief
    out_dir = REPO / "content" / "derivatives" / week / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    brief_path = out_dir / "ig_reel_brief.md"
    brief_path.write_text(brief_to_markdown(data, slug, week, niche, existing_shorts))
    print(f"  ✓ {brief_path.relative_to(REPO)}")
    return True


def find_slugs_for_week(week: str) -> list[str]:
    blog_dir = REPO / "content" / "blogs" / week
    if not blog_dir.exists():
        return []
    return sorted(
        f.stem for f in blog_dir.glob("*.md")
        if not f.name.startswith(".")
    )


def main():
    ap = argparse.ArgumentParser(description="Generate Instagram Reel brief for a content piece.")
    ap.add_argument("--slug", help="Blog slug (filename without .md extension)")
    ap.add_argument("--week", required=True, help="ISO week, e.g. 2026-W22")
    ap.add_argument("--project", default=None, help="Build-in-public project key (data/kb/projects.json)")
    args = ap.parse_args()

    # Load master brief for competition + channel intelligence
    master_brief_path = REPO / "data" / "kb" / "master_brief.md"
    master_brief = master_brief_path.read_text(encoding="utf-8") if master_brief_path.exists() else None
    if not master_brief:
        print("  ⚠ master_brief.md not found — competition intelligence unavailable")

    if args.slug:
        slugs = [args.slug]
    else:
        slugs = find_slugs_for_week(args.week)
        if not slugs:
            print(f"No blog files found in content/blogs/{args.week}/")
            sys.exit(1)
        print(f"Found {len(slugs)} slugs in {args.week}")

    ok = sum(process_slug(args.week, s, args.project, master_brief=master_brief) for s in slugs)
    print(f"\n✓ Done: {ok}/{len(slugs)} briefs generated")
    print(f"  → content/derivatives/{args.week}/*/ig_reel_brief.md")


if __name__ == "__main__":
    main()
