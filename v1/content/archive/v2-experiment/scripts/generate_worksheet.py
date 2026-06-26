#!/usr/bin/env python3
"""
generate_worksheet.py
Generate a printable + Vercel-hostable worksheet from a blog post.
DS and Life niches only — Poetry is excluded.

Usage:
    python v2/scripts/generate_worksheet.py --blog v2/content/blogs/2026-W26/2026-06-23_ds_....md
    python v2/scripts/generate_worksheet.py --blog <path> --niche life

Output:
    v2/output/worksheets/YYYY-Wnn/<slug>-worksheet.html
    → Deploy to Vercel → paste URL into derivatives as the CTA

Requirements: Claude CLI installed and authenticated (`claude` in PATH)
"""

import argparse
import re
import subprocess
import sys
import threading
import time
from datetime import date, timedelta
from pathlib import Path


# ══════════════════════════════════════════════════════════════════════════════
# PATHS
# ══════════════════════════════════════════════════════════════════════════════

V2_ROOT        = Path(__file__).resolve().parent.parent
WORKSHEETS_DIR = V2_ROOT / "output" / "worksheets"


# ══════════════════════════════════════════════════════════════════════════════
# NICHE CONFIG
# ══════════════════════════════════════════════════════════════════════════════

NICHE_CONFIG = {
    "ds": {
        "label":        "Data Science / Tech",
        "accent":       "#2563eb",          # blue
        "accent_light": "#dbeafe",
        "reader":       "mid-career data scientists",
        "cta_verb":     "Apply this to your work",
        "worksheet_style": (
            "Practical and structured. Think: a senior colleague gave you a framework "
            "and now you're filling it out at your desk. No fluff. Every question "
            "should produce something immediately usable at work."
        ),
    },
    "life": {
        "label":        "Life & Self-Development",
        "accent":       "#059669",          # green
        "accent_light": "#d1fae5",
        "reader":       "people working on themselves",
        "cta_verb":     "Make this personal",
        "worksheet_style": (
            "Warm and introspective. Think: a journal prompt from a friend who knows you well. "
            "Personal, not clinical. The tone should make honest self-reflection feel safe, not scary."
        ),
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# CLAUDE CLI
# ══════════════════════════════════════════════════════════════════════════════

def call_claude(prompt: str, label: str = "Calling Claude") -> str:
    result: dict = {"stdout": "", "stderr": "", "code": None}
    done = threading.Event()

    def _run() -> None:
        try:
            r = subprocess.run(
                ["claude", "-p", prompt],
                capture_output=True, text=True, timeout=300,
            )
            result["stdout"] = r.stdout
            result["stderr"] = r.stderr
            result["code"]   = r.returncode
        except subprocess.TimeoutExpired:
            result["stderr"] = "Claude CLI timed out after 5 minutes."
            result["code"]   = 1
        except Exception as exc:
            result["stderr"] = str(exc)
            result["code"]   = 1
        finally:
            done.set()

    threading.Thread(target=_run, daemon=True).start()

    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    start  = time.time()
    i      = 0
    while not done.wait(timeout=0.1):
        elapsed = int(time.time() - start)
        m, s = divmod(elapsed, 60)
        print(f"\r  {frames[i % len(frames)]}  {label} ... {m:02d}:{s:02d}", end="", flush=True)
        i += 1

    elapsed = int(time.time() - start)
    m, s = divmod(elapsed, 60)
    print(f"\r  ✓  {label} — {m:02d}:{s:02d}                    ")

    if result["code"] != 0:
        print(f"\nERROR from Claude CLI:\n{result['stderr'][-400:]}", file=sys.stderr)
        sys.exit(1)

    return result["stdout"].strip()


# ══════════════════════════════════════════════════════════════════════════════
# FILE I/O
# ══════════════════════════════════════════════════════════════════════════════

def get_iso_week(d: date) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def slugify(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", text.lower())
    s = re.sub(r"\s+", "-", s.strip())
    return s[:55]


def read_blog(path: Path) -> tuple[str, str]:
    """Return (title, full_content) from a blog markdown file."""
    content = path.read_text(encoding="utf-8")
    title = ""
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            title = stripped.lstrip("#").strip()
            # Strip alt-title line if present
            title = title.split("*Alt")[0].strip()
            break
    return title, content


def detect_niche(path: Path) -> str | None:
    """Infer niche from filename: YYYY-MM-DD_<niche>_slug.md"""
    parts = path.stem.split("_")
    if len(parts) >= 2 and parts[1] in ("ds", "life"):
        return parts[1]
    return None


# ══════════════════════════════════════════════════════════════════════════════
# PROMPT BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

DS_WORKSHEET_PROMPT = """\
You are creating a practical worksheet for data scientists based on this blog post.

Blog title: {title}
Blog content:
{content}

Generate worksheet content with EXACTLY these 5 sections.
Write the content only — no HTML, no markdown headers, just the raw text for each section.

SECTION 1: WHERE DO YOU STAND? (Self-assessment)
3 questions that make the reader honestly rate their current situation.
Each question should be answerable with a 1–5 scale or a short written response.
Make them specific to the blog's topic — not generic.

SECTION 2: YOUR BIGGEST TAKEAWAY
Complete this sentence: "The one thing from this article that changes how I think about [topic] is..."
Then: "I used to believe ___, but now I think ___."

SECTION 3: THIS WEEK'S ACTIONS
3 specific, concrete things to do in the next 7 days based on what this blog taught.
Each action must be completable in under 2 hours.
Format: checkbox + action + why it matters (one sentence).

SECTION 4: THE 30-DAY EXPERIMENT
One specific behaviour to track or change for 30 days, directly from the blog's insight.
Include: what to do, how to measure it, and what success looks like.

SECTION 5: SHARE YOUR RESULT
A 2-sentence social post template the reader can fill in and share after completing the experiment.
Format: "I tried [experiment] for 30 days. Here's what happened: ___"

Keep every section tight. No fluff. Every word should earn its place.
"""

LIFE_WORKSHEET_PROMPT = """\
You are creating a personal reflection worksheet based on this blog post.

Blog title: {title}
Blog content:
{content}

Generate worksheet content with EXACTLY these 5 sections.
Write the content only — no HTML, no markdown headers, just the raw text for each section.
Tone: warm, honest, gently challenging. Like a good friend asking the right questions.

SECTION 1: HONEST CHECK-IN
3 reflection questions that help the reader see where they actually are right now.
Not aspirational — honest. Make them feel seen, not judged.

SECTION 2: WHAT THIS MEANS FOR ME
"Reading this, what hit me hardest was ___."
"The part I've been avoiding is ___."
"What I wish someone had told me earlier: ___."

SECTION 3: THE ONE THING I'LL CHANGE
A single, specific commitment. Not a list — one thing.
Format: "Starting [day], I will ___ instead of ___, because ___."
Then: "I'll know it's working when ___."

SECTION 4: 30-DAY CHECK-IN GRID
A simple daily tracker for the one change above.
7 columns (Mon–Sun) × 4 rows (weeks 1–4).
Each cell: a tiny checkbox or circle to fill in.
Include 3 "anchor questions" to reflect on at the end of each week.

SECTION 5: A MONTH FROM NOW
"One month from now, if I keep this up, ___."
"The person who benefits most from this change is ___."
"What I want to remember about why I started: ___."
"""


def build_worksheet_prompt(niche_key: str, title: str, content: str) -> str:
    template = DS_WORKSHEET_PROMPT if niche_key == "ds" else LIFE_WORKSHEET_PROMPT
    # Truncate blog content to ~3000 chars to keep prompt manageable
    content_snippet = content[:3000] + ("..." if len(content) > 3000 else "")
    return template.format(title=title, content=content_snippet)


# ══════════════════════════════════════════════════════════════════════════════
# HTML TEMPLATE
# ══════════════════════════════════════════════════════════════════════════════

def parse_sections(raw: str) -> list[tuple[str, str]]:
    """
    Parse Claude's output into (section_title, section_body) pairs.
    Handles both 'SECTION N: TITLE' format and plain numbered headers.
    """
    sections: list[tuple[str, str]] = []
    current_title = ""
    current_lines: list[str] = []

    for line in raw.splitlines():
        stripped = line.strip()
        # Match "SECTION 1: WHERE DO YOU STAND?" or "1. WHERE DO YOU STAND?"
        m = re.match(r"^(?:SECTION\s+\d+\s*:\s*|[\d]+\.\s+)(.+)$", stripped, re.IGNORECASE)
        if m and stripped.upper() == stripped or m and stripped.startswith("SECTION"):
            if current_title:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = m.group(1).title() if m else stripped
            current_lines = []
        else:
            current_lines.append(line)

    if current_title:
        sections.append((current_title, "\n".join(current_lines).strip()))

    # Fallback: split on blank lines if parsing produced nothing useful
    if len(sections) < 3:
        chunks = re.split(r"\n{2,}", raw.strip())
        sections = []
        for i, chunk in enumerate(chunks[:5], 1):
            lines = chunk.strip().splitlines()
            title = lines[0] if lines else f"Section {i}"
            body  = "\n".join(lines[1:]).strip() if len(lines) > 1 else chunk.strip()
            sections.append((title, body))

    return sections


def body_to_html(body: str) -> str:
    """Convert plain text body to simple HTML — preserve line breaks, detect checkboxes."""
    lines = body.splitlines()
    html_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            html_lines.append("<br>")
            continue
        # Checkbox lines
        if stripped.startswith(("□", "☐", "[ ]", "- [ ]", "* [ ]")):
            text = re.sub(r"^[□☐\[\]\-\*\s]+", "", stripped)
            html_lines.append(
                f'<label class="cb-row"><input type="checkbox"> <span>{text}</span></label>'
            )
        # Scale questions (contain 1–5 or similar)
        elif re.search(r"\b1[-–]5\b", stripped):
            html_lines.append(f'<p class="question">{stripped}</p>')
            html_lines.append('<div class="scale"><span>1</span><span>2</span><span>3</span>'
                              '<span>4</span><span>5</span></div>')
        # Fill-in-the-blank lines (contain ___)
        elif "___" in stripped:
            html = re.sub(r"_{3,}", '<span class="blank"></span>', stripped)
            html_lines.append(f'<p class="fill">{html}</p>')
        else:
            html_lines.append(f'<p>{stripped}</p>')
    return "\n".join(html_lines)


def build_tracker_grid() -> str:
    """Build the 30-day Mon–Sun × 4 weeks tracker grid."""
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    rows = ""
    for week in range(1, 5):
        cells = "".join(
            f'<td><div class="day-box"><div class="day-label">{d}</div>'
            f'<div class="day-check"></div></div></td>'
            for d in days
        )
        rows += f"<tr><td class='week-label'>Week {week}</td>{cells}</tr>\n"
    return f"""
<div class="tracker-wrap">
  <table class="tracker">
    <thead><tr>
      <th></th>{''.join(f'<th>{d}</th>' for d in days)}
    </tr></thead>
    <tbody>{rows}</tbody>
  </table>
</div>"""


def render_html(
    niche_key: str,
    blog_title: str,
    sections: list[tuple[str, str]],
    blog_url: str = "",
) -> str:
    cfg      = NICHE_CONFIG[niche_key]
    accent   = cfg["accent"]
    accent_l = cfg["accent_light"]
    label    = cfg["label"]
    today    = date.today().strftime("%B %Y")

    section_icons = ["📍", "💡", "✅", "📅", "📣"]

    section_html = ""
    for i, (title, body) in enumerate(sections):
        icon  = section_icons[i] if i < len(section_icons) else "▸"
        # Inject tracker grid into section 4 (30-day) for Life niche
        if niche_key == "life" and i == 3:
            content_html = build_tracker_grid()
            if body.strip():
                content_html = body_to_html(body) + content_html
        else:
            content_html = body_to_html(body)

        section_html += f"""
<section class="ws-section">
  <h2><span class="icon">{icon}</span> {title}</h2>
  <div class="section-body">
    {content_html}
  </div>
</section>"""

    blog_link_html = (
        f'<a href="{blog_url}" class="blog-link" target="_blank">← Read the full article</a>'
        if blog_url else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Worksheet: {blog_title}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --accent:   {accent};
    --accent-l: {accent_l};
    --text:     #111827;
    --muted:    #6b7280;
    --border:   #e5e7eb;
    --radius:   8px;
  }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    color: var(--text);
    background: #f9fafb;
    padding: 2rem 1rem;
    line-height: 1.6;
  }}

  .container {{
    max-width: 760px;
    margin: 0 auto;
    background: white;
    border-radius: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,.08);
    overflow: hidden;
  }}

  /* Header */
  .ws-header {{
    background: var(--accent);
    color: white;
    padding: 2.5rem 2rem 2rem;
  }}
  .ws-header .label {{
    font-size: .75rem;
    font-weight: 600;
    letter-spacing: .1em;
    text-transform: uppercase;
    opacity: .8;
    margin-bottom: .5rem;
  }}
  .ws-header h1 {{
    font-size: 1.5rem;
    font-weight: 700;
    line-height: 1.3;
    margin-bottom: .75rem;
  }}
  .ws-header .meta {{
    font-size: .8rem;
    opacity: .75;
  }}

  /* Blog link */
  .blog-link {{
    display: inline-block;
    margin: 1.25rem 2rem 0;
    font-size: .8rem;
    color: var(--accent);
    text-decoration: none;
    font-weight: 500;
  }}
  .blog-link:hover {{ text-decoration: underline; }}

  /* Name field */
  .name-row {{
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.25rem 2rem;
    border-bottom: 1px solid var(--border);
    font-size: .85rem;
    color: var(--muted);
  }}
  .name-row input {{
    border: none;
    border-bottom: 1.5px solid var(--border);
    outline: none;
    flex: 1;
    font-size: .95rem;
    padding: .25rem 0;
    color: var(--text);
    background: transparent;
  }}

  /* Sections */
  .ws-section {{
    padding: 1.75rem 2rem;
    border-bottom: 1px solid var(--border);
  }}
  .ws-section:last-child {{ border-bottom: none; }}
  .ws-section h2 {{
    font-size: 1rem;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: .5rem;
  }}
  .ws-section .icon {{ font-size: 1.1rem; }}

  .section-body p {{
    font-size: .9rem;
    margin-bottom: .75rem;
    color: #374151;
  }}
  .section-body br {{ display: block; margin: .5rem 0; content: ""; }}

  /* Questions */
  .question {{
    font-weight: 500;
    color: var(--text) !important;
    margin-top: 1rem !important;
  }}

  /* Scale */
  .scale {{
    display: flex;
    gap: .5rem;
    margin: .5rem 0 1.25rem;
  }}
  .scale span {{
    width: 2rem;
    height: 2rem;
    border: 1.5px solid var(--border);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: .8rem;
    color: var(--muted);
    cursor: pointer;
    transition: all .15s;
  }}
  .scale span:hover {{
    border-color: var(--accent);
    background: var(--accent-l);
    color: var(--accent);
  }}

  /* Fill-in-the-blank */
  .fill {{ font-style: italic; }}
  .blank {{
    display: inline-block;
    min-width: 8rem;
    border-bottom: 1.5px solid #9ca3af;
    margin: 0 .25rem;
    vertical-align: bottom;
  }}

  /* Checkboxes */
  .cb-row {{
    display: flex;
    align-items: flex-start;
    gap: .6rem;
    margin-bottom: .6rem;
    cursor: pointer;
    font-size: .9rem;
  }}
  .cb-row input {{ margin-top: .2rem; accent-color: var(--accent); }}

  /* 30-day tracker */
  .tracker-wrap {{
    overflow-x: auto;
    margin-top: 1rem;
  }}
  .tracker {{
    width: 100%;
    border-collapse: collapse;
    font-size: .75rem;
  }}
  .tracker th, .tracker td {{
    border: 1px solid var(--border);
    padding: .3rem .4rem;
    text-align: center;
  }}
  .tracker th {{
    background: var(--accent-l);
    color: var(--accent);
    font-weight: 600;
  }}
  .week-label {{
    font-weight: 600;
    color: var(--muted);
    white-space: nowrap;
    text-align: left !important;
    padding-left: .6rem !important;
  }}
  .day-box {{ display: flex; flex-direction: column; align-items: center; gap: .2rem; }}
  .day-label {{ font-size: .65rem; color: var(--muted); }}
  .day-check {{
    width: 1.2rem;
    height: 1.2rem;
    border: 1.5px solid var(--border);
    border-radius: 3px;
  }}

  /* Footer */
  .ws-footer {{
    padding: 1.5rem 2rem;
    background: #f9fafb;
    font-size: .78rem;
    color: var(--muted);
    text-align: center;
    border-top: 1px solid var(--border);
  }}
  .ws-footer a {{ color: var(--accent); text-decoration: none; }}

  /* Print */
  @media print {{
    body {{ background: white; padding: 0; }}
    .container {{ box-shadow: none; border-radius: 0; }}
    .scale span:hover {{ border-color: var(--border); background: none; color: var(--muted); }}
    a {{ color: inherit; }}
  }}
</style>
</head>
<body>
<div class="container">

  <div class="ws-header">
    <div class="label">{label} · Worksheet</div>
    <h1>{blog_title}</h1>
    <div class="meta">Tarun Gupta · {today}</div>
  </div>

  {blog_link_html}

  <div class="name-row">
    <span>Name:</span>
    <input type="text" placeholder="Your name">
    <span>Date:</span>
    <input type="text" placeholder="Today's date">
  </div>

  {section_html}

  <div class="ws-footer">
    Created with <a href="https://medium.com/@tarun-gupta" target="_blank">Tarun Gupta</a>
    · Print this page or fill it in digitally
  </div>

</div>
</body>
</html>"""


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a worksheet from a blog post (DS and Life niches only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python v2/scripts/generate_worksheet.py --blog v2/content/blogs/2026-W26/2026-06-23_ds_....md\n"
            "  python v2/scripts/generate_worksheet.py --blog <path> --niche life\n"
        ),
    )
    parser.add_argument("--blog",  required=True, help="Path to the blog .md file")
    parser.add_argument("--niche", choices=["ds", "life"], default=None,
                        help="Override niche detection (auto-detected from filename if omitted)")
    parser.add_argument("--blog-url", default="",
                        help="Published Medium URL to link back from the worksheet")
    args = parser.parse_args()

    blog_path = Path(args.blog)
    if not blog_path.exists():
        print(f"ERROR: Blog file not found: {blog_path}", file=sys.stderr)
        sys.exit(1)

    # Detect niche
    niche = args.niche or detect_niche(blog_path)
    if not niche:
        print(
            "ERROR: Could not detect niche from filename. Pass --niche ds or --niche life.",
            file=sys.stderr,
        )
        sys.exit(1)
    if niche == "poetry":
        print("ERROR: Worksheets are not generated for the poetry niche.", file=sys.stderr)
        sys.exit(1)

    cfg     = NICHE_CONFIG[niche]
    divider = "─" * 54

    print(f"\n{divider}")
    print(f"  Worksheet Generator  ·  {cfg['label']}")
    print(f"  Blog: {blog_path.name}")
    print(divider)

    # Read blog
    print("\n  Reading blog ...", end=" ", flush=True)
    title, content = read_blog(blog_path)
    print(f"done  ({len(content.split())} words)")
    print(f"  Title: {title[:70]}{'…' if len(title) > 70 else ''}")

    # Generate worksheet content via Claude
    print()
    prompt   = build_worksheet_prompt(niche, title, content)
    raw      = call_claude(prompt, label="Generating worksheet content")

    # Parse + render
    print("  Rendering HTML ...", end=" ", flush=True)
    sections = parse_sections(raw)
    html     = render_html(niche, title, sections, blog_url=args.blog_url)
    print("done")

    # Save
    today   = date.today()
    week    = get_iso_week(today)
    slug    = slugify(title)
    out_dir = WORKSHEETS_DIR / week
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{today}_{niche}_{slug}-worksheet.html"
    out_path.write_text(html, encoding="utf-8")

    print(f"\n{divider}")
    print(f"  ✓  {out_path.relative_to(V2_ROOT.parent)}")
    print(f"     {len(sections)} sections · {len(html.split())} words of HTML")
    print(divider)
    print()
    print("  Next steps:")
    print("  1. Open the HTML file and check it looks right")
    print("  2. Deploy to Vercel:  vercel deploy --prod")
    print("  3. Copy the Vercel URL and pass it to generate_derivatives.py --worksheet-url <url>")
    print()


if __name__ == "__main__":
    main()
