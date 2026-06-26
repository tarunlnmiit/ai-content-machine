#!/usr/bin/env python3
"""
generate_blog.py
Research what's working in your niche right now, then write a viral blog post.

Usage:
    python v2/scripts/generate_blog.py --niche ds
    python v2/scripts/generate_blog.py --niche ds --topic "your angle"
    python v2/scripts/generate_blog.py --niche ds --dry-run

Requirements: Claude CLI installed and authenticated (`claude` in PATH)
Output:       v2/content/blogs/YYYY-Wnn/<date>_<niche>_<slug>.md
"""

import argparse
import json
import re
import subprocess
import sys
import threading
import time
import urllib.request
import urllib.parse
from datetime import date, timedelta
from pathlib import Path


# ══════════════════════════════════════════════════════════════════════════════
# PATHS
# ══════════════════════════════════════════════════════════════════════════════

V2_ROOT   = Path(__file__).resolve().parent.parent          # content-machine/v2/
BLOGS_DIR = V2_ROOT / "content" / "blogs"


# ══════════════════════════════════════════════════════════════════════════════
# NICHE CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

NICHE_CONFIG = {
    "ds": {
        "label": "Data Science / Tech",
        "word_count": "1200 to 1800",
        "format_note": (
            "Full-length blog post: intro, 3–5 sections with concrete examples, strong ending. "
            "Each section has a hook subheading and at least one specific number or story."
        ),
        "google_seeds": [
            "data scientist career 2026",
            "data science vs AI engineering",
            "agentic AI for data scientists",
            "Claude for data scientists",
            "data scientist skills 2026",
            "machine learning job market 2026",
            "AI replacing data scientists",
            "python tips for data scientists",
        ],
        "medium_feeds": [
            "https://medium.com/feed/tag/data-science",
            "https://medium.com/feed/data-science-collective",
        ],
        "competitors": (
            # YouTube
            "StatQuest/Josh Starmer (stats + ML explained visually — benchmark for clarity), "
            "3Blue1Brown (6.7M subs — visual math/ML storytelling, very high bar), "
            "Ken Jee (250K YT — career + projects, closest to build-in-public angle), "
            "Luke Barousse (employer-focused DA/DS, grounded in job market reality), "
            "Krish Naik (practical tutorials, large Indian audience — similar demographic to yours), "
            # Instagram — DS/AI lane
            "mavgpt / Maverick Maltin (933K IG — his TOP posts: Claude+Higgsfield MCP 19.1K likes/15.4K comments, "
            "Claude+Metricool MCP 5.8K likes/9.4K comments; formula = revelation hook + 3-step setup + specific outcome + comment→DM CTA; "
            "mass-market AI productivity, NOT DS-specific — your edge is the 10-year practitioner lens he lacks), "
            "Jonathan Acuña 'Doctor AI' (178K IG, 1972 posts — agency/B2B automation, GoHighLevel replacement, "
            "daily livestreams; very different audience from yours — skip unless you go B2B), "
            "tessa.fairbrook (17K IG, 39 posts — purely Claude-specific carousels; "
            "high per-post engagement suggests strong niche pull; most direct competitor for your Claude/free-tool content), "
            "datascienceinfo (210K IG — trend-focused aggregator)"
        ),
        "your_edge": (
            "mavgpt is the ceiling in AI productivity but is mass-market and non-technical — no DS career depth. "
            "Tessa is your most direct competitor in the Claude lane, but she has no practitioner voice or career angle. "
            "Jonathan is a different audience entirely (agencies, not learners) — minimal overlap. "
            "Krish Naik has the Indian audience but is tutorial-first, not introspective. "
            "Ken Jee is closest in voice but lacks 10-year depth and the Indian immigrant lens. "
            "THE GAP nobody fills: a 10-year DS practitioner writing honestly about what the job actually feels like — "
            "the AI anxiety, the career pivots, the real day-to-day with Claude and Python — "
            "from an Indian perspective, with warmth and no hype. Write into that gap."
        ),
        "target_reader": "mid-career data scientists anxious about AI's impact on their jobs",
        "seo_focus":     "data science career, AI tools for data scientists, python data science",
        "publishing":    "Medium (medium.com/@tarun-gupta)",
        "voice_note":    "analytical but warm — a colleague being honest, not a teacher explaining",
    },
    "life": {
        "label": "Life & Self-Development",
        "word_count": "1000 to 1500",
        "format_note": (
            "Personal essay style: open with a real moment from your life, not a generic statement. "
            "3–4 sections. Honest, warm, specific. Reads like you're talking to a friend, not a reader."
        ),
        "google_seeds": [
            "self improvement habits 2026",
            "mindset shift that changed my life",
            "how to stop overthinking",
            "building discipline without motivation",
            "personal growth advice",
            "productivity system that actually works",
        ],
        "medium_feeds": [
            "https://medium.com/feed/tag/self-improvement",
            "https://medium.com/feed/tag/productivity",
            "https://medium.com/feed/tag/personal-development",
        ],
        "competitors": (
            "Ali Abdaal (science-backed productivity, massive audience, very polished), "
            "Huberman Lab (neuroscience-based health/behaviour, very high trust + production), "
            "Mel Robbins (5.5M YT — anxiety, habits, motivation, mainstream appeal), "
            "Improvement Pill (bite-sized habit/mindset, viral series format), "
            "Healthy Gamer / Dr. K (psychology for young men, emotional depth — closest in emotional register), "
            "Tom Bilyeu / Impact Theory (interviews + mindset, heavy production), "
            "Jay Shetty (purpose + mindset, massive reach, very produced), "
            "@ankurwarikoo (~9M+ IG/YT — India's top self-dev creator; text-wall thumbnails where the thumbnail IS the claim; "
            "teaches mechanisms not inspiration — every piece answers 'why does this keep happening to me?' and names it; "
            "product in first pinned comment not caption; closes flat and instructional, zero motivational crescendo; zero hashtags), "
            "@joeykidney (~500K — emotional-logical hybrid; vulnerability disarmer: admits he reasoned his way to the emotion "
            "rather than lived it — this builds more credibility than performed empathy; "
            "community CTA: 'help each other in the comments / this is a safe space'; "
            "DM keyword monetization; essay-as-caption for heavy topics; 2.4M grief reel)"
        ),
        "your_edge": (
            "Every major competitor is either heavily produced (Huberman, Tom Bilyeu), purely English (Ali Abdaal), "
            "or teaches without an analytical-then-emotional arc. "
            "Ankur teaches mechanisms but stays rational. Joey does emotional-logical hybrid but has no data/career lens. "
            "Dr. K has emotional depth but not the Indian immigrant experience. "
            "Tarun's gap: the analytical identity IS the disarmer. "
            "'I don't do feelings content. I work with data. And I ran the numbers on this. Here's what I found.' "
            "Write the thing the reader feels but can't articulate, arrived at through logic — not performance."
        ),
        "target_reader": "25–35 year olds stuck between where they are and where they want to be",
        "seo_focus":     "self improvement, mindset, productivity habits, personal growth",
        "publishing":    "Medium (medium.com/@tarun-gupta)",
        "voice_note":    "warm and personal — raw take, real stories, no performance",
    },
    "poetry": {
        "label": "Poetry & Quotes",
        "word_count": "400 to 700",
        "format_note": (
            "A single poem (12–30 lines) followed by 150–300 words of personal context: "
            "what triggered it, what it cost to write, what the creator hopes the reader feels. "
            "Do NOT write an essay. The poem is the main event. The context is intimate, not analytical."
        ),
        "google_seeds": [
            "modern poetry about feelings",
            "poetry about anxiety and overthinking",
            "poems about loneliness and belonging",
            "contemporary love poems",
            "poetry about identity and home",
            "short poems that hit hard",
            "spoken word poetry mental health",
        ],
        "medium_feeds": [
            "https://medium.com/feed/tag/poetry",
            "https://medium.com/feed/tag/creative-writing",
        ],
        "competitors": (
            "rupi kaur (defines the instapoet aesthetic — minimal, lowercase, image+text — now ubiquitous), "
            "Button Poetry (spoken word standard — 'OCD' by Neil Hilborn hit 16M views, raw performance energy), "
            "alexelle (1.5M IG — healing-focused, very accessible), "
            "wordporn (broadest literary reach — quotes + prose, aggregator), "
            "Poetry Foundation + Poets.org (institutional — classic + contemporary readings), "
            "poetsofinstagram (community aggregator), "
            "@christi.steyn (1.2M IG — bestselling author, spoken-word; CORE MECHANIC: projective surface — "
            "poem describes a feeling so precisely the reader projects their own story; 370K reel 'gifts' = "
            "'I would X but Y' structure + ONE mundane line inside the tenderness ('bird language is not on duolingo') + "
            "full poem in caption as save trigger; permission close outperforms sad close; zero hashtags; "
            "DM keyword: comment VOWS for custom wedding vows), "
            "@joeykidney (~500K — forwarding mechanic: 'I am proud you are my mother' 5 words = 209K likes on Mother's Day — "
            "became a card people gave; non-announcing poem (prose format, no 'poem by', avoids poetry-niche penalty); "
            "cinematic: dark bg, amber text overlay, tight close-up; seasonal timing doubles the mechanic)"
        ),
        "your_edge": (
            "Rupi kaur's aesthetic is now the default — copied to death. "
            "Christi and Joey represent the real bar: projective surface (Christi) and forwarding mechanic (Joey). "
            "Neither brings bilingual emotional depth or a data scientist's precision. "
            "Tarun's gap: English precision carrying an Indian emotional register — feeling things in two languages "
            "gives texture none of the above have. "
            "And the 10-year DS identity lets him reach emotional truths through logic and numbers, "
            "which lands as credible in a way that pure performance poetry does not. "
            "Write the poem that only someone who thinks in one language, feels in another, "
            "and has spent a decade in data could write."
        ),
        "target_reader": "people who feel things deeply and rarely find words that match",
        "seo_focus":     "poetry, emotional poetry, spoken word, self-expression",
        "publishing":    "Medium (medium.com/@tarun-gupta)",
        "voice_note":    "lyrical, slow, emotionally precise — never rushed",
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# VIRALITY KNOWLEDGE BASE
# (Medium audit + IG saved collection analysis — June 2026)
# ══════════════════════════════════════════════════════════════════════════════

WHAT_WORKS = """
━━━ MEDIUM PERFORMANCE DATA (75 articles audited, June 2026) ━━━
Curation threshold: >50% read ratio. Patterns are universal across all niches.

CURATION ZONE (≥50% read ratio):
  55% — "I Wish I Had Known This Way to Process My Thoughts"   → Named discovery
  54% — "Data Quality & Measurement Process Assessment"        → Specific problem + stakes
  52% — "Zero Frequency Problem"                               → Named concept + tension

STRONG PERFORMERS (40–49%):
  44% — "How You Can Have Sustainably High Levels of Dopamine" → Counter-intuitive + specific
  44% — "Structuring a NodeJS API in an efficient way"         → "Efficient way" pattern for tech
  44% — "The Need For Closure"                                 → Emotional precision naming
  41% — "JavaScript's Magical Tips Every Developer Should Remember" → Listicle + specific qualifier
  41% — "You Are Setting Yourself for Hurt by Expecting Help from Others" → Provocation + truth

EARNINGS INSIGHT (the $40/1K anomaly):
  "If You Are a Serious Poet, Stop Writing Poetry Online" — 31% read ratio but $140.81 earned
  = $40/1K views vs $4/1K for 2019 tutorial back-catalogue.
  Provocation brings curators even at lower read ratios. A challenging premise earns more than
  a clear explanation.

2019 SEO PARADOX (warning):
  The 15 most-viewed articles are 2019 tutorials — high view counts from SEO but 22–32% read ratios.
  They built the audience but won't get curated. Post-2021 emotional/opinionated pieces earn more
  per view. Do NOT optimise for SEO views at the cost of read ratio.

DANGER ZONE (<25% read ratio — never use these patterns):
   5% — "You People Have Misused My Good Nature"               → Vague rant, no reader value
  15% — "What is Love? What is Hate?"                          → Double generic question, no tension
  18% — "Therapy Taught Me About Expectation Management"       → Overused therapy framing + abstract
  19% — "How Being Stuck in a Situation Can Do Wonders"        → Vague paradox, no concrete anchor
  20% — "Understanding Decision Tree Classifier"               → Pure label, zero tension
  21% — "Here's My Secret Sauce on How to Be Consistent"       → Exhausted phrase ("secret sauce")

━━━ INSTAGRAM VIRALITY DATA (saved collection, June 2026) ━━━
Top performing posts by engagement — what's actually working on IG right now:
  19.1K likes · 15.4K comments — mavgpt: "You can now connect Claude to [tool]" + 3-step setup
  17.7K likes ·  8.8K comments — cindie.zhu: "Claude skills that turn Claude into a creator studio"
  17.2K likes ·  1.1K saves    — katecore.ai: free AI tools resource carousel
   5.8K likes ·  9.4K comments — mavgpt: Claude + Metricool MCP for scheduling/analytics/competitor spy
     821 likes ·  2.0K comments — tenfoldmarc: "spy on competitors with Claude" (comment rate 243%)

KEY INSIGHT: Comment count exceeds like count on the top reel posts — the comment→DM CTA
drives this. It's the dominant engagement model in this space.

━━━ HOOK PATTERNS THAT DRIVE HIGH ENGAGEMENT (from IG data) ━━━
  • Revelation    "You can now [thing that sounds impossible/new]"
  • Theft         "STEAL THESE [PROMPTS/TIPS/TOOLS] 👇"
  • Urgency       "You need to SAVE this right now ❗️"
  • Spy angle     "I let Claude spy on my competitor's strategy — here's what it found"
  • Setup speed   "Here's how to set it up in 30 seconds:" → numbered steps → result

SPECIFICITY RULE: Never say "a few minutes" — say "30 seconds". Never say "many followers" —
say "185,000 followers in 4 months". Specific numbers signal credibility instantly.

━━━ UNIVERSAL TITLE PATTERNS THAT WORK (Medium + IG both) ━━━
  • Named discovery    "I Wish I Had Known..." / "Nobody Told Me..."
  • Specific stakes    Name the exact problem + what it costs the reader
  • Named concept      Give the idea a memorable label readers will repeat
  • Honest framing     "the real / actual / honest way to..."
  • Provocation        "Stop [doing the thing everyone says to do]"
  • Personal milestone "After [N years/months], here's what actually changed"
  • Fear/anxiety       Make the reader feel they're missing something critical right now

━━━ TITLE RULES — CLICKBAIT THAT'S ALSO CREDIBLE ━━━
The title must do TWO things simultaneously:
  1. Signal exactly who this is for (right reader self-selects in)
  2. Create tension, fear, curiosity, or urgency (they MUST click)

A title that describes content without tension FAILS. Rewrite until removing
the tension would make the title useless as a click driver.

Good tension levers:
  → Fear of missing out       "The Skill That's Quietly Separating DS Careers Right Now"
  → Fear of being wrong       "You're Using Claude Wrong — Here's What Actually Works"
  → Anxiety about the future  "What Happens to Data Scientists Who Don't Adapt in the Next 12 Months"
  → Curiosity gap             "The One Thing mavgpt Does That Nobody Talks About"
  → Counterintuitive claim    "Why the Best Data Scientists Are Using Less Python in 2026"
  → Insider knowledge         "I Spent 10 Years in DS. Here's What They Don't Tell You at the Start"

TITLE PATTERNS THAT KILL:
  • "Understanding X"                    (pure label)
  • "What is X? What is Y?"             (double generic question)
  • "Secret sauce", "game-changer"      (exhausted phrases)
  • "Tutorial 1/10" in cold titles      (series numbers kill cold traffic)

BANNED WORDS: "In conclusion" · "Dive into" · "Leverage" · "Game-changer" · "Synergy"
"""

FIVE_LEVERS = """
FIVE VIRALITY LEVERS — apply every single one:

  1. TITLE
     Signals the right reader AND creates tension simultaneously.
     If it describes the content without tension, it fails. Rewrite.

  2. FIRST PARAGRAPH
     Open with the specific incident, number, or counter-intuitive fact.
     Test: remove the first paragraph — if the article reads fine without it,
     it's throat-clearing. Rewrite until removing it would genuinely hurt.

  3. SUBHEADINGS AS HOOKS
     Every subheading pulls a skimmer into reading that section.
     ✓ "The Bug That Cost Me 3 Days"     ✗ "The Problem"
     ✓ "What I Stopped Doing in Year 7"  ✗ "Key Insight"

  4. [QUOTABLE] SENTENCE
     One sentence a stranger would screenshot and send to a friend.
     Mark it exactly: [QUOTABLE] — it feeds into the IG reel hook.

  5. ENDING
     Quotable line, genuine question, or a one-line implication.
     Never a bullet recap. Never "Let me know your thoughts."
"""

SEO_RULES = """
SEO (for Medium + Google discoverability):
  • Primary keyword appears naturally in the title
  • 2–3 high-intent phrases from the Google signals woven into the body
  • Primary keyword appears once in the first 150 words
  • Secondary keywords can appear in subheadings where they fit naturally
  • Never keyword-stuff — if it reads awkwardly, remove it
"""


# ══════════════════════════════════════════════════════════════════════════════
# RESEARCH — fetch live signals
# ══════════════════════════════════════════════════════════════════════════════

def fetch_google_suggest(seeds: list[str]) -> list[str]:
    """Pull autocomplete suggestions from Google. No API key needed."""
    results: set[str] = set()
    for query in seeds:
        try:
            url = (
                "http://suggestqueries.google.com/complete/search"
                f"?client=firefox&q={urllib.parse.quote(query)}"
            )
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read())
                results.update(data[1])
        except Exception:
            pass
    return sorted(results)[:20]


def fetch_medium_titles(feeds: list[str]) -> list[str]:
    """Pull recent article titles from Medium RSS feeds."""
    titles: list[str] = []
    seen: set[str] = set()

    # Words that indicate it's a feed/channel name, not an article title
    noise = {"medium", "data science collective", "towards data science",
             "towards ai", "data science", "self improvement", "poetry"}

    for url in feeds:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                xml = resp.read().decode("utf-8", errors="ignore")

            # CDATA titles (standard Medium RSS format)
            for m in re.finditer(r"<title><!\[CDATA\[(.*?)]]></title>", xml):
                t = m.group(1).strip()
                tl = t.lower()
                if len(t) > 20 and t not in seen and tl not in noise:
                    seen.add(t)
                    titles.append(t)

        except Exception:
            pass

    return titles[:25]


# ══════════════════════════════════════════════════════════════════════════════
# PROMPT BUILDER
# ══════════════════════════════════════════════════════════════════════════════

def suggest_topics(
    niche_key: str,
    google_signals: list[str],
    medium_titles: list[str],
    recent_titles: list[str],
) -> list[str]:
    """Ask Claude for 5 topic options based on live signals."""
    cfg = NICHE_CONFIG[niche_key]
    covered      = "\n".join(f"  • {t}" for t in recent_titles) or "  None yet"
    google_block = "\n".join(f"  • {s}" for s in google_signals) or "  (unavailable)"
    medium_block = "\n".join(f"  • {t}" for t in medium_titles)  or "  (unavailable)"

    prompt = f"""\
Suggest 5 blog topic angles for this creator.

Creator: Tarun Gupta — {cfg['label']}
Edge: {cfg['your_edge']}
Target reader: {cfg['target_reader']}

ALREADY COVERED — last 90 days (do not repeat these or close variants):
{covered}

GOOGLE SIGNALS — what people are searching this week:
{google_block}

TOP MEDIUM TITLES THIS WEEK:
{medium_block}

Generate exactly 5 topic angles that:
- Have not been covered recently
- Have clear demand from the signals above
- Fit this creator's voice and edge
- Would each score >50% read ratio on Medium
- Are meaningfully different from each other (different hooks, emotions, angles)

Reply with exactly this format — no headers, no explanation, just the 5 lines:
1. [topic angle]
2. [topic angle]
3. [topic angle]
4. [topic angle]
5. [topic angle]
"""
    raw = call_claude(prompt, label="Generating topic options")

    topics: list[str] = []
    for line in raw.splitlines():
        line = line.strip()
        # Match lines starting with "1." through "5."
        if line and line[0].isdigit() and "." in line[:3]:
            topic = line.split(".", 1)[1].strip()
            if topic:
                topics.append(topic)

    # Fallback: return whatever lines we got even if parsing was imperfect
    if not topics:
        topics = [l.strip() for l in raw.splitlines() if l.strip()]

    return topics[:5]


def select_topic(topics: list[str], niche_label: str) -> str:
    """Show the 5 options, let Tarun pick one by number."""
    print(f"\n{'─'*54}")
    print(f"  {niche_label} — pick a topic for today")
    print(f"{'─'*54}")
    for i, t in enumerate(topics, 1):
        print(f"  {i}. {t}")
    print(f"{'─'*54}\n")

    while True:
        try:
            raw = input(f"  Your pick (1–{len(topics)}): ").strip()
            idx = int(raw) - 1
            if 0 <= idx < len(topics):
                return topics[idx]
        except (ValueError, EOFError):
            pass
        print(f"  Enter a number between 1 and {len(topics)}.")


def suggest_titles(
    niche_key: str,
    topic: str,
    creator_input: str,
    google_signals: list[str],
) -> list[str]:
    """Generate 5 title options across different tension levers."""
    cfg = NICHE_CONFIG[niche_key]
    top_keywords = ", ".join(google_signals[:6]) or "(unavailable)"
    creator_context = f"Creator's personal angle: {creator_input}" if creator_input else ""

    prompt = f"""\
Generate 5 clickbait-but-credible blog title options for this creator.

Niche:         {cfg['label']}
Topic:         {topic}
Target reader: {cfg['target_reader']}
{creator_context}
Keywords with real search demand this week: {top_keywords}

Each title must use a DIFFERENT tension lever:
1. [FEAR]           — reader fears they're missing something critical right now
2. [ANXIETY]        — taps into career/life anxiety the target reader already feels
3. [CURIOSITY GAP]  — opens a loop they must click to close
4. [COUNTERINTUITIVE] — challenges something they think they know
5. [INSIDER]        — positions this as information they cannot get elsewhere

Rules every title must follow:
- Signals exactly who it's for (right reader self-selects in)
- Creates enough tension that NOT clicking feels like a loss
- Includes the primary keyword naturally — not forced
- Under 85 characters where possible
- No: "game-changer", "leverage", "dive into", "secret sauce", "In conclusion"

Reply with exactly this — no labels, no explanation, just 5 lines:
1. [title]
2. [title]
3. [title]
4. [title]
5. [title]
"""
    raw = call_claude(prompt, label="Generating title options")

    titles: list[str] = []
    for line in raw.splitlines():
        line = line.strip()
        if line and line[0].isdigit() and "." in line[:3]:
            title = line.split(".", 1)[1].strip()
            if title:
                titles.append(title)

    if not titles:
        titles = [l.strip() for l in raw.splitlines() if l.strip()]

    return titles[:5]


def select_title(titles: list[str], topic: str) -> str:
    """Show the 5 title options, let Tarun pick one by number."""
    levers = ["FEAR", "ANXIETY", "CURIOSITY GAP", "COUNTERINTUITIVE", "INSIDER"]
    print(f"\n{'─'*54}")
    print(f"  Pick a title  ·  Topic: {topic[:45]}{'…' if len(topic) > 45 else ''}")
    print(f"{'─'*54}")
    for i, title in enumerate(titles):
        lever = levers[i] if i < len(levers) else f"OPTION {i+1}"
        print(f"  {i+1}. [{lever}]")
        print(f"     {title}")
        print()
    print(f"{'─'*54}\n")

    while True:
        try:
            raw = input(f"  Your pick (1–{len(titles)}): ").strip()
            idx = int(raw) - 1
            if 0 <= idx < len(titles):
                return titles[idx]
        except (ValueError, EOFError):
            pass
        print(f"  Enter a number between 1 and {len(titles)}.")


def get_creator_input(topic: str, niche_label: str) -> str:
    """Show the confirmed topic, ask Tarun for his thoughts on it."""
    print(f"\n{'─'*54}")
    print(f"  Topic : {topic}")
    print(f"{'─'*54}")
    print("  Any personal thoughts on this topic to weave in?")
    print("  Press Enter twice when done. Just Enter once to skip.\n")

    lines: list[str] = []
    while True:
        try:
            line = input("  > ")
        except EOFError:
            break
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)

    while lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines).strip()


def build_prompt(
    niche_key: str,
    topic_seed: str,
    google_signals: list[str],
    medium_titles: list[str],
    recent_titles: list[str],
    creator_input: str = "",
    chosen_title: str = "",
) -> str:
    cfg = NICHE_CONFIG[niche_key]

    topic_block = (
        f"CREATOR'S ANGLE (write the blog around this):\n  {topic_seed}"
        if topic_seed
        else "No angle specified — pick the highest-virality angle from the live signals below."
    )

    if recent_titles:
        covered = "\n".join(f"  • {t}" for t in recent_titles)
        recent_block = (
            f"ANGLES ALREADY COVERED — last 90 days (do not repeat these or close variants):\n{covered}"
        )
    else:
        recent_block = "ANGLES ALREADY COVERED — none yet (first blog!)"

    if creator_input:
        input_block = (
            f"CREATOR'S THOUGHTS ON THIS TOPIC — weave these into the blog:\n"
            f"  These are Tarun's personal thoughts and perspective. Polish the language freely,\n"
            f"  but preserve every idea and viewpoint exactly as he's expressed it.\n"
            f"  They should read as a natural part of the blog — not a quoted insert, not a separate section.\n\n"
            + "\n".join(f"  {line}" for line in creator_input.splitlines())
        )
    else:
        input_block = ""

    google_block = "\n".join(f"  • {s}" for s in google_signals) or "  (unavailable)"
    medium_block = "\n".join(f"  • {t}" for t in medium_titles)   or "  (unavailable)"

    return f"""\
You are ghostwriting a viral Medium blog post for this creator:

CREATOR PROFILE
  Name:          Tarun Gupta
  Niche:         {cfg['label']}
  Background:    10 years as a practitioner — not a course creator, an actual {cfg['label']} professional
  Voice:         {cfg['voice_note']}
  Target reader: {cfg['target_reader']}
  Publishing:    {cfg['publishing']}

DIFFERENTIATION
  Competitors:   {cfg['competitors']}
  Creator's edge that none of them have:
    {cfg['your_edge']}
  The blog must feel like it could ONLY come from this creator.
  Study what the competitors do — then find the gap they're leaving open.

{topic_block}

{recent_block}
{(chr(10) + input_block + chr(10)) if input_block else ""}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LIVE SIGNALS — what's working RIGHT NOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Google (what people are actively searching this week):
{google_block}

Top Medium titles published this week in this niche:
{medium_block}

Study the Medium titles above: the framing, emotional register, specificity.
Replicate the structure and angle that's working — in this creator's voice.
Use the Google signals to find which keywords to target.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT WORKS — from real data
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{WHAT_WORKS}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VIRALITY LEVERS — apply all five
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{FIVE_LEVERS}

━━━━━━━━━━━━━━━━━━━━
SEO
━━━━━━━━━━━━━━━━━━━━
{SEO_RULES}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT — use exactly this structure:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FORMAT RULES FOR THIS NICHE:
  Target length: {cfg['word_count']} words
  {cfg['format_note']}

{f'# {chosen_title}' if chosen_title else '''# [TITLE — must satisfy BOTH rules simultaneously:
#   1. Signals exactly who this is for (right reader self-selects in)
#   2. Creates tension, fear, curiosity, or urgency (they MUST click)
# Bad: "How to Use Claude for Data Science" — describes content, no tension
# Good: "I've Been a Data Scientist for 10 Years. Claude Just Changed How I Think About My Job."
# Test: Would someone anxious about their career stop scrolling? If not, rewrite.]'''}
{'# ← USE THIS EXACT TITLE. Do not alter a single word.' if chosen_title else ''}
*Alt subtitles: [2–3 subtitle options — different emotional hooks for the same title]*

**[Subtitle — one sentence that qualifies exactly who this is for and what they'll get]**

---

[Body]
[Never open with "In today's world..." or "As a data scientist..." — start with the specific incident]
[Subheadings are hooks, not labels — see FIVE_LEVERS above]
[At least one concrete number or specific example per section]
[Mark one sentence exactly: [QUOTABLE] — the line someone would screenshot and send to a friend]
[2–3 Google signal phrases woven in naturally, never forced]

---

*[CTA — end with a debate-inviting question the target reader has a strong opinion on.
 For DS/Life niches: also mention the free worksheet (Vercel URL will be injected by the
 derivatives script when built — for now write: "Get the free worksheet: [WORKSHEET_URL]")]*
"""


# ══════════════════════════════════════════════════════════════════════════════
# CLAUDE CLI
# ══════════════════════════════════════════════════════════════════════════════

def call_claude(prompt: str, label: str = "Calling Claude") -> str:
    """Run Claude CLI in a background thread; show a spinner + elapsed time while waiting."""
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


def get_recent_titles(days: int = 90) -> list[str]:
    """Return titles of blogs written in the last N days (all niches)."""
    cutoff = date.today() - timedelta(days=days)
    titles: list[str] = []

    if not BLOGS_DIR.exists():
        return titles

    for md_file in sorted(BLOGS_DIR.rglob("*.md")):
        # Filename format: YYYY-MM-DD_niche_slug.md
        date_part = md_file.stem[:10]
        try:
            if date.fromisoformat(date_part) < cutoff:
                continue
        except ValueError:
            continue

        # Pull title from the first # heading in the file
        try:
            for line in md_file.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if stripped.startswith("#"):
                    titles.append(stripped.lstrip("#").strip())
                    break
        except Exception:
            pass

    return titles


def save_blog(content: str, niche_key: str) -> Path:
    today    = date.today()
    week     = get_iso_week(today)
    headline = content.split("\n")[0].lstrip("#").strip()
    slug     = f"{today}_{niche_key}_{slugify(headline)}"

    out_dir  = BLOGS_DIR / week
    out_dir.mkdir(parents=True, exist_ok=True)

    path = out_dir / f"{slug}.md"
    path.write_text(content, encoding="utf-8")
    return path


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a viral blog post using live research + Claude CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python v2/scripts/generate_blog.py --niche ds\n"
            "  python v2/scripts/generate_blog.py --niche ds --topic 'AI and the DS job market'\n"
            "  python v2/scripts/generate_blog.py --niche life --dry-run\n"
        ),
    )
    parser.add_argument("--niche",   choices=["ds", "life", "poetry"], required=True)
    parser.add_argument("--topic",   default="", help="Optional topic seed")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the prompt only — do not call Claude")
    args = parser.parse_args()

    cfg = NICHE_CONFIG[args.niche]
    divider = "─" * 54

    print(f"\n{divider}")
    print(f"  Blog Generator  ·  {cfg['label']}")
    print(divider)

    # Step 1 — Research
    print("\n[1/3] Checking recent blogs   ...", end=" ", flush=True)
    recent = get_recent_titles(days=90)
    print(f"{len(recent)} found (last 90 days)")

    print("[2/3] Fetching Google signals ...", end=" ", flush=True)
    google = fetch_google_suggest(cfg["google_seeds"])
    print(f"{len(google)} found")

    print("[3/3] Fetching Medium titles  ...", end=" ", flush=True)
    medium = fetch_medium_titles(cfg["medium_feeds"])
    print(f"{len(medium)} found")

    # Step 2 — Determine topic
    if args.topic:
        topic = args.topic
    else:
        print()
        topics = suggest_topics(args.niche, google, medium, recent)
        topic = select_topic(topics, cfg["label"])

    creator_input = get_creator_input(topic, cfg["label"])

    # Step 3 — Title selection
    print()
    titles = suggest_titles(args.niche, topic, creator_input, google)
    chosen_title = select_title(titles, topic)

    # Step 4 — Build prompt
    prompt = build_prompt(args.niche, topic, google, medium, recent, creator_input, chosen_title)

    if args.dry_run:
        print(f"\n{'─'*54}")
        print("  DRY RUN — prompt only (Claude not called)")
        print(f"{'─'*54}\n")
        print(prompt)
        return

    # Step 4 — Generate
    print()
    blog = call_claude(prompt, label="Writing blog")

    # Step 5 — Save
    path  = save_blog(blog, args.niche)
    words = len(blog.split())

    print(f"\n{divider}")
    print(f"  ✓  {path.relative_to(V2_ROOT.parent)}")
    print(f"     {words} words")
    print(divider)

    # Preview first non-empty lines
    print()
    for line in blog.split("\n"):
        if line.strip():
            print(f"  {line}")
        if sum(1 for l in blog.split("\n")[:blog.split("\n").index(line)+1] if l.strip()) >= 4:
            break
    print()


if __name__ == "__main__":
    main()
