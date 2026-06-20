#!/usr/bin/env python3
"""Turn an already-published YouTube video or Medium blog into short teasers + backlinks.

Distribution is manual — this writes copy-paste-ready files only (no CSV/scheduler).

Create mode (default):
    python3 scripts/teaser_from_published.py --url https://medium.com/@x/post --niche life
    python3 scripts/teaser_from_published.py --url https://youtu.be/abc123 --niche ds
    python3 scripts/teaser_from_published.py --urls urls.txt          # batch (mixed)
    python3 scripts/teaser_from_published.py --url ... --dry-run       # print, don't write

  urls.txt line format:  url[, niche][, project]   (niche/project optional, '#' comments ok)

Tag-existing mode (inject a UTM backlink into already-generated derivative files):
    python3 scripts/teaser_from_published.py --inject-link content/derivatives/2026-W24/<slug> \
        --url https://medium.com/@x/post

Output per piece → content/derivatives/{week}/{slug}/:
    linkedin_teaser.txt, instagram_teaser.txt,
    threads_teaser.txt, newsletter_teaser.txt, teasers.md (bundle), source.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, urlencode, urlunparse, parse_qsl

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from _console import console  # noqa: E402
from lib.fetch_published import fetch, FetchError  # noqa: E402
from lib.claude_cli import call_claude  # noqa: E402
from lib.niche_config import model_for  # noqa: E402
from lib.virality import virality_block, project_keys  # noqa: E402
from lib.hashtags import hashtag_line  # noqa: E402
from lib.utm import build_utm_url, PLATFORMS  # noqa: E402
from lib.content_paths import derivatives_dir  # noqa: E402

DEFAULT_CAMPAIGN = "evergreen-repurpose"
PLATFORM_ORDER = ["linkedin", "instagram", "threads", "newsletter"]
TEASER_FILES = {p: f"{p}_teaser.txt" for p in PLATFORM_ORDER}

# platform → (utm_source, utm_medium). Newsletter is not a UTM source → handled manually.
_UTM_MAP = {
    "linkedin": ("linkedin", "post"),
    "instagram": ("instagram", "post"),
    "threads": ("threads", "post"),
}


# ── Backlinks ──────────────────────────────────────────────────────────────

def backlink(url: str, platform: str, campaign: str, content: str) -> str:
    """UTM-tagged backlink for a platform. Newsletter/unknown tagged manually."""
    if platform in _UTM_MAP:
        source, medium = _UTM_MAP[platform]
        return build_utm_url(url, source=source, medium=medium, campaign=campaign, content=content)
    parts = urlparse(url)
    query = dict(parse_qsl(parts.query))
    query.update({"utm_medium": platform, "utm_campaign": campaign, "utm_content": content})
    return urlunparse(parts._replace(query=urlencode(query)))


def _apply_link(text: str, link: str) -> str:
    """Replace the literal [LINK] token, or append the link if absent."""
    if "[LINK]" in text:
        return text.replace("[LINK]", link)
    return (text.rstrip() + "\n\n" + link).strip()


# ── Prompt + parse ─────────────────────────────────────────────────────────

def extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    m = re.search(r"\{.*\}", text, re.DOTALL)
    return json.loads(m.group(0) if m else text)


def build_prompt(agent: str, niche: str, project: str | None, title: str, body: str) -> str:
    sections = [agent]
    virality = virality_block("thread", niche, project)
    if virality:
        sections.append("## Virality Directives\n\n" + virality)
    sections.append(f"## Published piece to teaser\n\nTITLE: {title}\n\n{body[:16000]}")
    sections.append("Return ONLY the JSON object. No markdown, no code fences.")
    return "\n\n---\n\n".join(sections)


# ── Formatters (one per platform) ──────────────────────────────────────────

def _fmt_linkedin(d: dict, niche: str, link: str) -> str:
    body = _apply_link(d.get("body", ""), link)
    lines = [d.get("opening_line", ""), "", body]
    tags = hashtag_line(niche, "linkedin", d.get("hashtags"))
    if tags:
        lines += ["", tags]
    return "\n".join(lines).strip()


def _fmt_instagram(d: dict, niche: str, link: str) -> str:
    body = _apply_link(d.get("caption_body", ""), link)
    lines = [d.get("hook_line", ""), "", body]
    tags = hashtag_line(niche, "instagram", d.get("hashtags"))
    if tags:
        lines += ["", tags]
    return "\n".join(lines).strip()


def _fmt_threads(d: dict, niche: str, link: str) -> str:
    body = _apply_link(d.get("body", ""), link)
    tags = hashtag_line(niche, "threads", d.get("hashtags"))
    if tags:
        body = (body.rstrip() + "\n\n" + tags).strip()
    return body


def _fmt_newsletter(d: dict, niche: str, link: str) -> str:
    body = _apply_link(d.get("body", ""), link)
    return (
        f"Subject: {d.get('subject_line', '')}\n"
        f"Preview: {d.get('preview_text', '')}\n\n{body}"
    )


_FORMATTERS = {
    "linkedin": ("linkedin_teaser", _fmt_linkedin),
    "instagram": ("instagram_teaser", _fmt_instagram),
    "threads": ("threads_teaser", _fmt_threads),
    "newsletter": ("newsletter_teaser", _fmt_newsletter),
}


def render_platforms(data: dict, niche: str, url: str, campaign: str, slug: str,
                     platforms: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for platform in platforms:
        key, fmt = _FORMATTERS[platform]
        section = data.get(key)
        if not isinstance(section, dict):
            console.print(f"  [warn]missing '{key}' — skipping {platform}[/warn]")
            continue
        link = backlink(url, platform, campaign, slug)
        rendered = fmt(section, niche, link)
        if rendered.strip():
            out[platform] = rendered
    return out


# ── Create mode ────────────────────────────────────────────────────────────

def process_url(url: str, niche_hint: str | None, project: str | None, campaign: str,
                platforms: list[str], agent: str, dry_run: bool) -> None:
    console.rule(f"[info]{url}[/info]")
    try:
        piece = fetch(url, niche_hint)
    except FetchError as e:
        console.print(f"  [error]fetch failed: {e}[/error]")
        return

    console.print(f"  {piece.kind} · niche={piece.niche} · {len(piece.text):,} chars · slug={piece.slug}")
    prompt = build_prompt(agent, piece.niche, project, piece.title, piece.text)
    raw = call_claude(prompt, cache=True, model=model_for("repurpose"), timeout=300,
                      stream=True, progress_label=f"Teasers ({piece.niche})")
    try:
        data = extract_json(raw)
    except json.JSONDecodeError as e:
        console.print(f"  [error]JSON parse failed: {e}[/error]\n{raw[:300]}")
        return

    rendered = render_platforms(data, piece.niche, url, campaign, piece.slug, platforms)
    if not rendered:
        console.print("  [error]no teasers rendered[/error]")
        return

    if dry_run:
        for platform, text in rendered.items():
            console.rule(f"[dim]{platform}[/dim]")
            console.print(text)
        return

    out_dir = derivatives_dir(piece.date, piece.slug)
    out_dir.mkdir(parents=True, exist_ok=True)
    for platform, text in rendered.items():
        (out_dir / TEASER_FILES[platform]).write_text(text + "\n", encoding="utf-8")

    bundle = [f"# Teasers — {piece.title}\n\nSource: {url}\n"]
    for platform in PLATFORM_ORDER:
        if platform in rendered:
            bundle.append(f"\n## {platform}\n\n{rendered[platform]}\n")
    (out_dir / "teasers.md").write_text("\n".join(bundle), encoding="utf-8")
    (out_dir / "source.json").write_text(json.dumps({
        "url": url, "kind": piece.kind, "title": piece.title,
        "niche": piece.niche, "slug": piece.slug, "date": piece.date,
        "campaign": campaign,
    }, indent=2), encoding="utf-8")

    console.print(f"  [success]✓ {len(rendered)} teasers → {out_dir.relative_to(REPO)}[/success]")


# ── Tag-existing mode ──────────────────────────────────────────────────────

def _platform_of(filename: str) -> str | None:
    for platform in PLATFORM_ORDER:
        if platform in filename:
            return platform
    return None


def inject_link(deriv_dir: Path, url: str, campaign: str) -> None:
    if not deriv_dir.exists():
        sys.exit(f"derivatives dir not found: {deriv_dir}")
    slug = deriv_dir.name
    touched = 0
    for f in sorted(deriv_dir.glob("*.txt")):
        platform = _platform_of(f.name)
        if not platform:
            continue
        text = f.read_text(encoding="utf-8")
        if "utm_campaign" in text:  # idempotent
            continue
        link = backlink(url, platform, campaign, slug)
        f.write_text(text.rstrip() + "\n\n" + link + "\n", encoding="utf-8")
        console.print(f"  [success]+ {f.name}[/success]")
        touched += 1
    console.print(f"  {touched} file(s) tagged" if touched else "  nothing to tag (already tagged?)")


# ── Inputs ─────────────────────────────────────────────────────────────────

def parse_urls_file(path: Path) -> list[tuple[str, str | None, str | None]]:
    rows: list[tuple[str, str | None, str | None]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",")]
        url = parts[0]
        niche = parts[1] if len(parts) > 1 and parts[1] else None
        project = parts[2] if len(parts) > 2 and parts[2] else None
        rows.append((url, niche, project))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description="Teasers + backlinks from published YT/Medium URLs")
    ap.add_argument("--url", help="single published URL")
    ap.add_argument("--urls", type=Path, help="file of URLs (one per line: url[, niche][, project])")
    ap.add_argument("--niche", choices=["ds", "life", "poetry"], help="override niche")
    ap.add_argument("--project", help="build-in-public project key (data/kb/projects.json)")
    ap.add_argument("--campaign", default=DEFAULT_CAMPAIGN, help=f"UTM campaign (default {DEFAULT_CAMPAIGN})")
    ap.add_argument("--platforms", nargs="+", choices=PLATFORM_ORDER, default=PLATFORM_ORDER)
    ap.add_argument("--inject-link", type=Path, metavar="DERIV_DIR",
                    help="tag mode: append UTM backlink to existing derivative files in this dir")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.project and args.project not in project_keys():
        ap.error(f"--project must be one of: {', '.join(project_keys()) or '(none defined)'}")

    # Tag-existing mode
    if args.inject_link:
        if not args.url:
            ap.error("--inject-link requires --url (the canonical link to inject)")
        inject_link(args.inject_link, args.url, args.campaign)
        return

    # Create mode
    if not args.url and not args.urls:
        ap.error("provide --url or --urls (or --inject-link DIR --url ...)")

    agent = (REPO / "prompts" / "teaser_agent.md").read_text(encoding="utf-8")
    rows = ([(args.url, args.niche, args.project)] if args.url
            else parse_urls_file(args.urls))

    for url, niche, project in rows:
        process_url(url, args.niche or niche, args.project or project,
                    args.campaign, args.platforms, agent, args.dry_run)


if __name__ == "__main__":
    main()
