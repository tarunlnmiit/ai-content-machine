#!/usr/bin/env python3
"""
Consolidate ideas from all sources (Reddit, YouTube, external RSS, Google/YT suggest).
Deduplicate, apply novelty penalty vs archive, rank top N per niche (default 5).
Write data/ideas/weekly_ideas.md.
Use Ollama (gemma4:e2b) for classification.
"""

import argparse
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

import requests
from _console import console, progress_bar


# Per-niche off-topic filters — drop items matching these patterns.
# Reason: Medium tag pages (e.g. /tag/poetry) attract AI/tech essays
# that abuse tags for reach. Strict regex to keep niche relevance.
NICHE_BLOCKLIST = {
    "poetry_quotes": re.compile(
        # Tech / AI bleed (Medium /tag/poetry abuse)
        r"\b(AI|GPT|ChatGPT|LLM|Claude|Anthropic|OpenAI|machine learning|"
        r"agent|crypto|bitcoin|startup|saas|stripe|kubernetes|docker|api)\b|"
        # Off-niche content categories
        r"\b(ASMR|fanfic|fanfiction|songwriter|songwriting|lyrics|"
        r"taylor swift|beyonc[eé]|kanye|drake|"
        # Reviews / pop culture
        r"netflix|hbo|movie review|tv show|anime|kdrama|"
        # Politics / news
        r"trump|biden|election|congress|senate|"
        # Writing craft (not poetry itself)
        r"how to write|writing tips|writing prompt|world.?building|"
        # Academic / philosophy treatises (long-form essays, not poems)
        r"discourse|treatise|hermeneutic|exegesis|"
        # Marketing / business bleed
        r"marketing|seo|conversion|funnel|monetiz|substack growth)\b",
        re.IGNORECASE,
    ),
    "life_self_dev": re.compile(
        r"\b(AI|GPT|ChatGPT|LLM|crypto|bitcoin|kubernetes|docker)\b",
        re.IGNORECASE,
    ),
}


HASHTAG_SPAM = re.compile(r"(#\w+\s*){3,}")
ACADEMIC_ESSAY = re.compile(
    r"\b(and the (American|Western|Modern|Eastern)|"
    r"reception of|reading of|analysis of|study of|"
    r"in the (works|poetry|writing) of|"
    r"imagination|hermeneutic|exegesis|literary criticism)\b",
    re.IGNORECASE,
)


def passes_blocklist(item: dict) -> bool:
    """Return False if item matches niche blocklist."""
    niche = item.get("niche", "")
    title = item.get("title", "")
    haystack = f"{title} {item.get('summary','')}"

    pattern = NICHE_BLOCKLIST.get(niche)
    if pattern and pattern.search(haystack):
        return False

    # Poetry-specific structural filters
    if niche == "poetry_quotes":
        if HASHTAG_SPAM.search(title):
            return False
        if ACADEMIC_ESSAY.search(title):
            return False
    return True


def load_json_files(directory):
    all_ideas = []
    path = Path(directory)
    for json_file in path.glob("*.json"):
        try:
            data = json.loads(json_file.read_text())
            stem = json_file.stem

            # Format 1: suggest_*.json → {niche: {seed: {source: [strings]}}}
            if stem.startswith("suggest_") and isinstance(data, dict):
                for niche, seeds in data.items():
                    if not isinstance(seeds, dict):
                        continue
                    for seed, srcs in seeds.items():
                        if not isinstance(srcs, dict):
                            continue
                        for src_name, suggestions in srcs.items():
                            if not isinstance(suggestions, list):
                                continue
                            for s in suggestions:
                                if not isinstance(s, str) or len(s) < 8:
                                    continue
                                all_ideas.append({
                                    "title": s,
                                    "url": "",
                                    "source": f"{stem}_{src_name}",
                                    "niche": niche,
                                    "score": 0.7,  # autocomplete = decent baseline
                                })
                continue

            # Format 2: standard {niche: [items]} or list
            if isinstance(data, dict):
                for niche, items in data.items():
                    if isinstance(items, list):
                        for item in items:
                            if not isinstance(item, dict):
                                continue
                            item["source"] = item.get("source", stem)
                            item["niche"] = niche
                            # Boost external feeds w/ engagement signals
                            if "score" not in item:
                                pts = item.get("points", 0)
                                reacts = item.get("reactions", 0)
                                comments = item.get("comments", 0)
                                if pts or reacts or comments:
                                    item["score"] = (pts + reacts + comments * 0.5) / 50.0
                                else:
                                    item["score"] = 0.6  # generic feed item
                            all_ideas.append(item)
            else:
                all_ideas.extend(data)
        except Exception as e:
            console.print(f"[warn]Error loading {json_file}: {e}[/warn]")
    return all_ideas


def string_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def deduplicate(ideas, threshold=0.75):
    deduplicated, seen = [], []
    for idea in ideas:
        title = idea.get("title", "")
        if not any(string_similarity(title, s) >= threshold for s in seen):
            deduplicated.append(idea)
            seen.append(title)
    return deduplicated


def load_archive_titles(archive_dir="data/kb"):
    titles = []
    master = Path(archive_dir) / "master_brief.md"
    if master.exists():
        for line in master.read_text().splitlines():
            if line.startswith("## ") or line.startswith("### "):
                titles.append(line.strip("#").strip())
    return titles


def _source_family(source: str) -> str:
    """Group source names into families for rank normalization."""
    s = (source or "").lower()
    if s.startswith("reddit_"):
        return "reddit"
    if s.startswith("youtube_"):
        return "youtube"
    if s.startswith("suggest_"):
        return "suggest"
    if "hn" in s or "algolia" in s:
        return "hn"
    if "arxiv" in s:
        return "arxiv"
    if "medium" in s:
        return "medium"
    if "devto" in s:
        return "devto"
    if "github" in s:
        return "github"
    if "goodreads" in s or "poets" in s:
        return "external_other"
    return "other"


def apply_rank_score(ideas):
    """Convert raw scores into per-source rank percentile.

    Why: HN points (50+) vs Reddit recency (~1.5) skew naive blending.
    Within each (niche, source_family) group, rank items and assign
    percentile 1.0 = best, 0.0 = worst. Final score = percentile.
    Then niches blend evenly across families.
    """
    groups = {}
    for idea in ideas:
        key = (idea.get("niche", ""), _source_family(idea.get("source", "")))
        groups.setdefault(key, []).append(idea)

    for key, items in groups.items():
        items.sort(key=lambda x: x.get("score", 0) or 0, reverse=True)
        n = len(items)
        for rank, idea in enumerate(items):
            idea["rank_score"] = 1.0 - (rank / max(n - 1, 1))
    return ideas


def apply_novelty_penalty(ideas, archive_titles, penalty=0.5):
    """Apply novelty penalty on rank-normalized score."""
    for idea in ideas:
        title = idea.get("title", "")
        max_sim = max((string_similarity(title, a) for a in archive_titles), default=0)
        base = idea.get("rank_score", idea.get("score", 0) or 0.5)
        idea["novelty_adjusted_score"] = base * penalty if max_sim > 0.6 else base
    return ideas


def classify_idea(title: str, niche: str) -> str:
    prompt = f"Classify this content idea into a brief category (1-3 words):\nNiche: {niche}\nIdea: {title}\nCategory:"

    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "gemma4:e2b", "prompt": prompt, "stream": False},
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("response", "").strip().split("\n")[0][:50]
        console.print(f"[warn]Ollama HTTP {resp.status_code}[/warn]")
    except Exception as e:
        console.print(f"[warn]Ollama error: {e}[/warn]")

    return "uncategorized"


def score_ideas(output_dir="data/ideas", top_n=5):
    console.rule("[info]Idea Scorer[/info]")

    with progress_bar() as progress:
        load_task = progress.add_task("Loading ideas", total=None)
        ideas = load_json_files(output_dir)
        progress.update(load_task, description=f"Loaded {len(ideas)} ideas", completed=1, total=1)

        filter_task = progress.add_task("Filtering off-topic", total=None)
        before = len(ideas)
        ideas = [i for i in ideas if passes_blocklist(i)]
        progress.update(filter_task, description=f"Filtered: {before} → {len(ideas)} ideas", completed=1, total=1)

        dedup_task = progress.add_task("Deduplicating", total=None)
        ideas = deduplicate(ideas)
        progress.update(dedup_task, description=f"After dedup: {len(ideas)} ideas", completed=1, total=1)

        rank_task = progress.add_task("Rank-normalizing per source", total=None)
        ideas = apply_rank_score(ideas)
        progress.update(rank_task, description="Rank-normalized", completed=1, total=1)

        archive_task = progress.add_task("Loading archive", total=None)
        archive_titles = load_archive_titles()
        progress.update(archive_task, description=f"Archive has {len(archive_titles)} titles", completed=1, total=1)

        novelty_task = progress.add_task("Applying novelty penalty", total=None)
        ideas = apply_novelty_penalty(ideas, archive_titles)
        progress.update(novelty_task, completed=1, total=1)

        # Group by niche
        by_niche = {}
        for idea in ideas:
            niche = idea.get("niche", "unknown")
            by_niche.setdefault(niche, []).append(idea)

        # Count top-N classifications needed
        total_to_classify = sum(min(top_n, len(v)) for v in by_niche.values())
        classify_task = progress.add_task("Classifying ideas", total=total_to_classify)

        # Build top-N per niche, then classify all in parallel
        top_by_niche = {
            niche: sorted(ideas, key=lambda x: x.get("novelty_adjusted_score", 0), reverse=True)[:top_n]
            for niche, ideas in by_niche.items()
        }

        all_pairs = [(idea, niche) for niche, ideas in top_by_niche.items() for idea in ideas]
        futures = {}
        with ThreadPoolExecutor(max_workers=5) as ex:
            for idea, niche in all_pairs:
                fut = ex.submit(classify_idea, idea["title"], niche)
                futures[fut] = idea
            for fut in as_completed(futures):
                futures[fut]["category"] = fut.result()
                progress.update(classify_task, description=f"Classified {futures[fut].get('category','')[:30]}")
                progress.advance(classify_task)

        final_ideas = top_by_niche

    # Generate markdown report
    lines = ["# Weekly Ideas Report", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
    for niche, ideas_list in final_ideas.items():
        lines.append(f"## {niche.replace('_', ' ').title()}")
        lines.append("")
        for i, idea in enumerate(ideas_list, 1):
            lines += [
                f"### {i}. {idea.get('title', 'Untitled')}",
                f"- **Score:** {idea.get('novelty_adjusted_score', 0):.3f}",
                f"- **Category:** {idea.get('category', 'uncategorized')}",
                f"- **Source:** {idea.get('source', 'unknown')}",
            ]
            if "url" in idea:
                lines.append(f"- **URL:** {idea['url']}")
            lines.append("")

    out = Path("data/ideas") / "weekly_ideas.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")

    console.print(f"\n[success]✓ Saved to {out}[/success]")
    for niche, ideas_list in final_ideas.items():
        console.print(f"  [niche]{niche}[/niche]:")
        for i, idea in enumerate(ideas_list, 1):
            console.print(f"    {i}. [dim]{idea['title'][:65]}[/dim] ({idea.get('novelty_adjusted_score',0):.3f})")

    return final_ideas


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=5, help="Top N ideas per niche (default 5)")
    ap.add_argument("--dir", default="data/ideas")
    args = ap.parse_args()
    score_ideas(output_dir=args.dir, top_n=args.top)
