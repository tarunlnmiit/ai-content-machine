#!/usr/bin/env python3
"""Generate a blog post using claude -p (Claude Pro subscription, no API key needed)."""

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

from _console import console, spinner

REPO = Path(__file__).parent.parent
NICHES = {"ds": "data_science_tech", "life": "life_self_dev", "poetry": "poetry_quotes"}


from lib.slug import slugify
from lib.schedule_calc import write_schedule_json, get_iso_week
from lib.worksheet_cta import worksheet_cta_markdown, has_cta

# Niches that ship a companion worksheet (poetry does not).
WORKSHEET_NICHES = {"ds", "life"}


def load(path: Path) -> str:
    if not path.exists():
        sys.exit(f"Missing: {path}")
    return path.read_text(encoding="utf-8")


def build_listicle_directive(n: int, topic: str, niche: str) -> str:
    """Listicle structure override. Forces top-N format with numbered item sections."""
    if n < 2:
        raise ValueError(f"--listicle count must be >= 2, got {n}")

    poetry_note = ""
    if niche == "poetry":
        poetry_note = (
            "\n- For poetry niche: each item is a distinct poem/quote/theme. "
            "Item bodies stay lyrical, ≤100w each."
        )

    return f"""

---

## LISTICLE OVERRIDE (this OVERRIDES the default structure in the Writing Agent Prompt)

Produce this blog as a **Top {n}** listicle. The title MUST start with "Top {n}" (or "{n} ", e.g. "{n} Ways to..."). Structure exactly:

1. **HOOK** — open with a sharp claim or stat that sets up why these {n} things matter. No throat-clearing.
2. **CONTEXT** — short framing: who this list is for, what criteria the items share, why this order.
3. **THE LIST** — exactly {n} numbered H2 sections:
   - `## 1. <Concrete item name>` ... `## {n}. <Concrete item name>`
   - Each item: one-line claim → 2-4 paragraph body → concrete example, code, or [PERSONAL_INSERT] where appropriate.
   - Order matters: rank by impact, difficulty, or chronology — state which in CONTEXT.
   - Each item body roughly equal length (±25%).
4. **TAKEAWAY** — the pattern that connects all {n} items. Not a recap.
5. **CTA** — one specific next action.

Rules:
- Item count is non-negotiable: exactly {n} items, not {n - 1}, not {n + 1}.
- No "honorable mentions" or "bonus" items appended.
- Item titles are concrete nouns/actions, not vague abstractions.{poetry_note}

Topic to listify: {topic}
"""


def build_prompt(
    writing_agent: str,
    master_brief: str,
    topic: str,
    niche: str,
    listicle: int | None = None,
) -> str:
    niche_label = {
        "ds": "Data Science/Tech",
        "life": "Life & Self-Development",
        "poetry": "Poetry/Quotes",
    }[niche]
    word_count_constraint = (
        "\n**Word count: 800–1,000 words total. Every section must be shorter than usual. "
        "Hook ≤100w, Context ≤150w, each Section ≤150w, Takeaway ≤100w, CTA ≤80w. "
        "Lyrical economy — cut anything that does not earn its line.**"
        if niche == "poetry" else ""
    )
    listicle_block = build_listicle_directive(listicle, topic, niche) if listicle else ""

    return f"""{writing_agent}

---

## Knowledge Base (master_brief.md)

{master_brief}

---

## Task

Niche: {niche_label}
Topic: {topic}
{word_count_constraint}

Follow every instruction in the Writing Agent Prompt above.
Complete all pre-writing steps (Notion query note: operate as if you have reviewed recent published posts and confirmed this angle is unexplored — focus on writing).
Produce the full blog post in clean Markdown, structured exactly as specified.

**MANDATORY REQUIREMENTS (no exceptions):**
1. Include at least 1 `[IMAGE_INSERT: concrete pexels search term]` marker in the blog body.
2. For poetry niche: embed the complete poem (if one is core to the topic) in one unbroken blockquote block right after the HOOK.
{listicle_block}"""


def run_claude(prompt: str, timeout: int, description: str) -> str:
    with spinner() as progress:
        task = progress.add_task(description)
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True, text=True, timeout=timeout,
        )
        progress.update(task, description=f"[success]{description} — done[/success]")

    if result.returncode != 0:
        console.print(f"[error]claude error:[/error] {result.stderr.strip()}")
        sys.exit(1)
    if not result.stdout.strip():
        console.print("[error]claude returned empty output[/error]")
        sys.exit(1)
    return result.stdout.strip()


HUMANIZE_PROMPT = """\
You are an editor performing a humanization pass on a blog post.

Apply these fixes — no exceptions:

1. Remove all AI tells:
   - Correlative constructions: "X aren't just Y, they're Z" → rewrite as direct claim
   - Filler hedges: might, could, perhaps, seems, possibly → commit or cut
   - Overused words: just, actually, basically, simply, really → cut or replace
   - Transition overuse: Furthermore, Moreover, Additionally, It's worth noting → cut or natural alternative
   - Throat-clearing openers: "In this post..." / "Today we'll..." → delete, start with substance

2. Strengthen weak sentences:
   - Passive → active voice
   - Vague claims → specific ones (if specific data isn't in text, mark with [SPECIFIC_NEEDED])
   - Long compound sentences → two short ones where rhythm improves

3. Preserve everything else exactly:
   - All [PERSONAL_INSERT], [CODE_INSERT], [IMAGE_INSERT] markers — do not touch
   - All Markdown structure, headings, code blocks
   - The author's voice, opinions, and specific examples
   - Word count within ±10%

Return ONLY the revised blog post. No preamble. No explanation.

---

Blog post to humanize:

"""


def main():
    parser = argparse.ArgumentParser(description="Produce a blog post via Claude Pro.")
    parser.add_argument("--topic", required=True, help="Blog topic or working title")
    parser.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    parser.add_argument(
        "--humanize",
        action="store_true",
        help="Run a post-generation humanization pass to remove AI tells",
    )
    parser.add_argument(
        "--listicle",
        type=int,
        default=None,
        metavar="N",
        help="Produce a Top-N listicle blog (e.g. --listicle 5 for 'Top 5...'). N must be >= 2.",
    )
    args = parser.parse_args()

    if args.listicle is not None and args.listicle < 2:
        parser.error("--listicle N must be >= 2")

    console.rule(f"[info]Blog Producer[/info]")
    console.print(f"Topic: [bold]{args.topic}[/bold]  Niche: [niche]{args.niche}[/niche]")

    writing_agent = load(REPO / "prompts" / "writing_agent.md")
    master_brief  = load(REPO / "data" / "kb" / "master_brief.md")
    combined_prompt = build_prompt(
        writing_agent, master_brief, args.topic, args.niche, listicle=args.listicle
    )
    if args.listicle:
        console.print(f"[info]Listicle mode:[/info] Top {args.listicle}")

    # Step 1 — generate blog
    blog_text = run_claude(combined_prompt, timeout=600,
                           description="Generating blog (2–5 min)...")

    # Validate IMAGE_INSERT present; retry once if missing
    if "[IMAGE_INSERT" not in blog_text:
        console.print("[warn]Warning: No IMAGE_INSERT found. Retrying with reinforced prompt...[/warn]")
        retry_prompt = combined_prompt + "\n\n**CRITICAL: You MUST include at least 1 [IMAGE_INSERT: ...] marker in the blog body.**"
        blog_text = run_claude(retry_prompt, timeout=600, description="Retrying with IMAGE_INSERT enforcement...")
        if "[IMAGE_INSERT" not in blog_text:
            console.print("[warn]⚠ Still no IMAGE_INSERT after retry. Proceeding anyway.[/warn]")

    # Step 1b — humanize (optional)
    if args.humanize:
        blog_text = run_claude(
            HUMANIZE_PROMPT + blog_text,
            timeout=300,
            description="Humanizing (removing AI tells)...",
        )

    # Step 2 — save
    today = date.today().isoformat()
    slug  = slugify(args.topic)
    filename = f"{today}_{NICHES[args.niche]}_{slug}.md"
    week = get_iso_week(today)
    out_dir  = REPO / "content" / "blogs" / week
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename

    # Append worksheet CTA for niches that ship a worksheet (idempotent).
    if args.niche in WORKSHEET_NICHES and not has_cta(blog_text):
        blog_text = blog_text.rstrip() + "\n\n" + worksheet_cta_markdown(slug)

    out_path.write_text(blog_text, encoding="utf-8")

    # Write schedule.json to derivatives dir
    full_slug = f"{today}_{NICHES[args.niche]}_{slug}"
    deriv_dir = REPO / "content" / "derivatives"
    schedule_path = write_schedule_json(full_slug, args.niche, deriv_dir)

    word_count = len(blog_text.split())
    personal_inserts = blog_text.count("[PERSONAL_INSERT")
    code_inserts     = blog_text.count("[CODE_INSERT")
    image_inserts    = blog_text.count("[IMAGE_INSERT")

    console.print(f"\n[success]✓ Saved:[/success] {out_path.relative_to(REPO)}")
    console.print(f"[success]✓ Schedule:[/success] {schedule_path.relative_to(REPO)}")
    console.print(f"  Words:             {word_count:,}")
    console.print(f"  [PERSONAL_INSERT]: {personal_inserts}")
    console.print(f"  [CODE_INSERT]:     {code_inserts}")
    console.print(f"  [IMAGE_INSERT]:    {image_inserts}")

    # Step 3 — summary
    summary_prompt = (
        "Summarise the following blog post in exactly 3 sentences. "
        "Be specific — name the core argument, one key insight, and the takeaway. "
        "No preamble.\n\n" + blog_text[:4000]
    )
    summary = run_claude(summary_prompt, timeout=60, description="Generating summary...")

    console.print("\n[bold]Summary:[/bold]")
    console.print(summary)

    if personal_inserts or code_inserts or image_inserts:
        console.print(
            f"\n[warn]Action needed:[/warn] "
            f"Fill {personal_inserts} [PERSONAL_INSERT], "
            f"{code_inserts} [CODE_INSERT], "
            f"{image_inserts} [IMAGE_INSERT] before repurposing."
        )
        console.print(f"  grep -rn 'INSERT' content/blogs/{week}/{filename}")


if __name__ == "__main__":
    main()
