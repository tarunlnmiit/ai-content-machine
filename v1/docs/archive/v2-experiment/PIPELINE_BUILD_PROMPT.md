---
title: "Content Machine v2 — Claude Code Build Prompt"
type: doc
slug: pipeline-build-prompt
tags: [content/doc]
---
# Content Machine v2 — Claude Code Build Prompt

Paste this entire file into Claude Code as your first message when starting the build session.

---

## Context

You are building the v2 content pipeline for a 10-year data scientist and content creator (Tarun Gupta). The repo is at the root of this workspace. A full v1 pipeline already exists in `v1/` — it has ~100 scripts, working lib utilities, and a live scheduling/publishing system. **Do not touch v1.** Build v2 alongside it.

Read these v1 files before writing a single line of code:

```
v1/scripts/lib/claude_cli.py       # Claude CLI wrapper with caching + retries — REUSE AS-IS
v1/scripts/lib/schedule_calc.py    # ISO week calc + publish time scheduling — REUSE AS-IS
v1/scripts/lib/content_paths.py    # Centralized path construction — REUSE AS-IS
v1/scripts/lib/niche_config.py     # Niche aliases/normalization — REUSE AS-IS
v1/scripts/lib/hashtags.py         # Hashtag generation — REUSE AS-IS
v1/scripts/lib/virality.py         # v1 engine — READ FOR UNDERSTANDING ONLY, do not import in v2
v1/scripts/run_blog_pipeline.py    # Read prompt patterns only
v1/scripts/repurpose_blog.py       # Read prompt patterns only
v1/data/kb/master_brief.md         # Creator voice + brand brief
v1/data/kb/viral_reel_formula.md   # 5-beat reel structure (reference only)
v1/output/trackers/annual-tracker-2026.xlsx  # Content tracker (source of truth)
CLAUDE.md                          # Project rules — read and follow
```

**Important:** v2 ships its own virality engine (`v2/scripts/lib/virality/`). Do not import `v1/scripts/lib/virality.py` anywhere in v2 code. Read it to understand the problem it solves, then build something better.

---

## What to Build

A **single daily entry point** that Tarun runs each morning. It tells him exactly what to do today, runs research once per week (cached), then generates content using Claude CLI with virality already baked in.

**Core principle:** Research runs once on Sunday, is cached for the week, and feeds every day's generation. Tarun does not repeat research manually.

---

## Pipeline Architecture

```
v2/
  scripts/
    daily.py              ← ENTRY POINT: "what do I do today?"
    weekly_research.py    ← runs Sunday, caches research brief for the whole week
    blog_generator.py     ← niche + research brief → full blog via Claude CLI
    derivatives.py        ← blog → all CC derivatives (carousel, LI post, LI deck, IG reel brief)
    viral_reel.py         ← separate track: research → viral reel script + IG/YT short
    tracker_sync.py       ← read/update annual-tracker-2026.xlsx
    lib/
      research.py         ← fetches Google Suggest + Medium RSS + YouTube, curates brief
      angle_picker.py     ← presents 3 research-backed angle options, user picks one
      virality/           ← NEW virality engine (see full spec below)
        __init__.py
        signals.py        ← fetches live signals (Google, Medium, YouTube)
        patterns.py       ← extracts hook patterns from live data via Claude CLI
        scorer.py         ← scores candidate angles against live signals
        blocks.py         ← generates platform-specific virality blocks
        cache.py          ← weekly cache management for signal data
```

---

## Script Specifications

### `daily.py` — The one command Tarun runs each morning

```
python v2/scripts/daily.py [--date YYYY-MM-DD] [--niche ds|life|poetry]
```

**What it does:**
1. Reads today's date, determines the day of week
2. Consults the tracker to show what's due today (blog day? viral reel day? derivatives of yesterday's blog?)
3. Checks if weekly research cache exists for this week (`v2/cache/research_YYYY-Wnn_<niche>.json`). If not, runs `weekly_research.py` automatically.
4. Prints a clear **daily briefing** to the terminal:
   - What's due today (blog? reel? both? derivatives?)
   - Which niche
   - Top 3 research-backed angles (pre-scored by virality)
   - Estimated time for each step
5. Prompts: "Which angle? (1/2/3 or type your own):"
6. Runs the appropriate generator(s) based on the schedule

**Niche schedule (from strategy doc):**
- DS blog: Mon + Thu
- Life blog: Tue + Fri
- Poetry blog: Wed + Sat
- DS viral reel: Tue + Fri
- Life viral reel: Mon + Thu
- Derivatives (CC): generated same day as blog, no recording needed

**Day types:**
- Blog day → `weekly_research.py` (if not cached) → angle picker → `blog_generator.py` → `derivatives.py`
- Viral reel day → `weekly_research.py` (if not cached) → `viral_reel.py`
- Both (overlapping days) → blog first, then reel

---

### `weekly_research.py` — Runs once, feeds the whole week

```
python v2/scripts/weekly_research.py --niche ds|life|poetry [--week YYYY-Wnn]
```

**What it does:**
1. Calls `v2/scripts/lib/virality/signals.py` to fetch live signals for the niche
2. Calls `v2/scripts/lib/virality/patterns.py` to extract hook patterns from the live data
3. Reads the tracker to extract all Content Titles published in the last 90 days (avoid-list)
4. Calls `v2/scripts/lib/virality/scorer.py` to score all candidate angles
5. Produces a **research brief** (`v2/cache/research_YYYY-Wnn_<niche>.json`):
   ```json
   {
     "week": "2026-W26",
     "niche": "ds",
     "generated_at": "...",
     "signals": {
       "google_suggest": ["..."],
       "medium_top_titles": [{"title": "...", "pub_date": "...", "url": "..."}],
       "youtube_trending": [{"title": "...", "channel": "...", "views_approx": "..."}]
     },
     "extracted_patterns": {
       "hook_structures": ["Number + credential + contrast", "Counter-intuitive claim", "..."],
       "high_signal_words": ["agentic", "10 years", "actually", "job market", "..."],
       "title_formulas": ["I [did X] for [N years]. Here's what [Y] actually [did/changed].", "..."]
     },
     "trending_angles": [
       {"title": "...", "source": "medium|google|youtube", "score": 1.45, "avoid": false},
       ...
     ],
     "avoid_angles": ["Python Data Types...", "..."],
     "top_3": [...]
   }
   ```
6. Cache TTL: 7 days. Never re-fetches within the same week unless `--force`.

**Reuse from v1:**
- `v1/scripts/lib/schedule_calc.py:get_iso_week()` — for cache key only

---

### `blog_generator.py` — Niche + angle → full blog

```
python v2/scripts/blog_generator.py --niche ds|life|poetry --angle "chosen angle or title"
```

**What it does:**
1. Reads the research brief from cache
2. Reads `v1/data/kb/master_brief.md` (creator voice)
3. Calls `v2/scripts/lib/virality/blocks.py:virality_block("medium_blog", niche=niche, research_brief=brief)` to get the platform-specific virality block
4. Constructs a single Claude CLI prompt that includes:
   - Creator voice brief (from master_brief)
   - Virality block (hook taxonomy, guardrail, CTA)
   - Research context (what's trending, what to avoid)
   - The chosen angle
   - Output format instructions (Medium-ready markdown, 1200–1800 words, no banned words)
5. Calls `v1/scripts/lib/claude_cli.py:call_claude()` with `temperature=0.85` for DS, `1.0` for Life, `1.15` for Poetry
6. Saves output to `v2/content/blogs/YYYY-Wnn/<slug>.md`
7. Prints path + word count

**Output format the prompt must request:**
```
# [Title]

[Subtitle / deck — one sentence]

---

[Body — Medium-ready markdown, personal voice, specific examples, no headers with "In conclusion" or banned words]

---

*[CTA line — follow, comment, etc.]*
```

**Banned words to inject into the prompt:**
`"In conclusion", "Dive into", "Leverage", "Game-changer", "Synergy"`

---

### `derivatives.py` — Blog → all CC platform content

```
python v2/scripts/derivatives.py --blog v2/content/blogs/YYYY-Wnn/<slug>.md --niche ds|life|poetry
```

**What it does — generates all "CC" (Claude-created, no recording needed) derivatives:**

For each derivative, reads the blog, constructs a targeted prompt with `virality_block()` for that content type, calls Claude CLI, saves to the right path.

| Derivative | Output | virality_block platform key | Path |
|---|---|---|---|
| IG Carousel (10 slides) | JSON → will render via Canva/HTML | `"ig_carousel"` | `v2/assets/carousels/YYYY-Wnn/<slug>_carousel.json` |
| LinkedIn Post | Markdown | `"linkedin_post"` | `v2/content/derivatives/YYYY-Wnn/<slug>/linkedin_post.md` |
| LinkedIn Slide Deck (5–7 slides) | JSON | `"linkedin_deck"` | `v2/content/derivatives/YYYY-Wnn/<slug>/linkedin_deck.json` |
| IG Reel Brief | Markdown (hook, 5-beat outline, CTA) | `"ig_reel"` | `v2/content/derivatives/YYYY-Wnn/<slug>/reel_brief.md` |

Each derivative gets the platform-specific virality block from `v2/scripts/lib/virality/blocks.py:virality_block(platform, niche, research_brief)`.

**LinkedIn post rules:**
- Blog/repo link goes in the **first comment**, never the post body
- Poll options max 30 characters each
- Post body = value only, no link

**Reuse from v1:**
- `v1/scripts/repurpose_blog.py` — read it, understand its prompt patterns, reuse what works
- `v1/scripts/lib/hashtags.py` — for IG/LinkedIn hashtags

---

### `viral_reel.py` — Separate track: research → reel script

```
python v2/scripts/viral_reel.py --niche ds|life [--type recreate|tool_hack]
```

Two reel types (from strategy doc):
1. `recreate` — recreate a trending reel with original CTA
2. `tool_hack` — reel about a tool/life hack with CTA

**What it does:**
1. Reads research cache for the niche
2. Picks the highest-virality trending angle appropriate for short-form (score from scorer.py)
3. Reads `v1/data/kb/viral_reel_formula.md` (5-beat structure, for reference)
4. Calls `virality_block("ig_reel", niche, research_brief)` — platform-specific block from v2 engine
5. Generates: hook (3 options to pick from), 5-beat script, overlay scene plan, CTA
6. Saves to `v2/content/scripts/YYYY-Wnn/<slug>_reel.md`

---

### `tracker_sync.py` — Read/update the tracker

```
python v2/scripts/tracker_sync.py --action read|update --slug <slug> --status <status>
```

Wraps openpyxl reads/writes to `v1/output/trackers/annual-tracker-2026.xlsx`.

- `read`: returns today's scheduled content + last 90 days of DS/Life/Poetry titles (for angle deduplication)
- `update`: sets Status field for a given slug to Published/Scheduled/etc.

---

### `lib/research.py` — Fetch + curate research

Internal module used by `weekly_research.py`.

```python
def fetch_google_suggest(seed_queries: list[str]) -> list[str]: ...
def fetch_medium_rss(feed_urls: list[str]) -> list[dict]: ...  # returns [{title, url, pub_date}]
def curate_brief(raw_signals: list[dict], avoid_list: list[str], niche: str) -> dict: ...
```

For `fetch_google_suggest`: use `http://suggestqueries.google.com/complete/search?client=firefox&q=<query>` — returns JSON with suggestions, no API key needed.

For `fetch_medium_rss`: use `feedparser` or raw urllib to parse Medium RSS. Extract title + pub_date + link.

---

### `lib/angle_picker.py` — Terminal UI for picking an angle

```python
def pick_angle(top_3: list[dict]) -> str: ...
```

Prints numbered list of 3 pre-ranked angles with virality scores, prompts user to pick 1/2/3 or type a custom angle. Returns the chosen angle string.

---

## New Virality Engine Spec — `v2/scripts/lib/virality/`

This is the core differentiator of v2. Unlike v1's static KB files and hardcoded trigger words, this engine fetches live signals weekly, extracts patterns from real performance data using Claude, and outputs a different instruction block depending on the platform. Build it as a standalone package.

---

### `signals.py` — Live signal fetcher

```python
# ─── DS NICHE CONTEXT (baked in from channel discovery + Medium audit) ────────
#
# Competitor landscape (Instagram/YouTube DS):
#   mavgpt (933K IG)       — mass-market AI productivity, comment→DM CTA model.
#                            Caption formula already reverse-engineered in v1 KB.
#                            Tarun's edge: depth + career narrative vs. tips format.
#   Ken Jee (250K YT)      — projects + career, closest voice match.
#   Luke Barousse           — what employers want, DA/DS overlap.
#   tessa.fairbrook (17K IG, 39 posts) — Claude-specific carousels, high per-post
#                            engagement. Direct competitor in free_tool_ds lane.
#                            Must be more story-driven to differentiate.
#   imjonathanacuna (178K) — agency/B2B automation, different audience entirely.
#
# Tarun's differentiator that NONE of the above have:
#   10-year practitioner perspective + Indian/Hinglish authenticity +
#   data science CAREER survival angle + emotional honesty about the field.
#
# Medium read ratio data (75 real articles audited June 2026):
#   Curation threshold = >50% read ratio.
#   Top performers: "I Wish I Had Known..." (55%), "Data Quality & Measurement
#     Process Assessment" (54%), "Zero Frequency Problem" (52%).
#   Strong (40-49%): "Structuring a NodeJS API in an efficient way" (44%).
#   Highest earnings/view: provocation-first titles — even 31% ratio can earn $140.
#   Danger zone: "Understanding X" (20%), double-question format (15%),
#     "secret sauce" / "consistent" phrasing (21%), pure label titles.
#   The 2019 SEO tutorial paradox: highest views, lowest read ratios (22-32%),
#     lowest earnings per view. Don't optimise for that pattern.
#
# DS YouTube Shorts that actually worked (@breathofdatascience):
#   "Why Your Code Breaks in Docker" (32 views)
#   "The First Skill Python Tutorials Skip" (27 views)
#   "Reading Python Errors" (21 views)
#   Pattern: specific problem statement, practitioner frustration framing.
#   Series numbering (Tutorial 1/10) kills cold traffic — avoid in titles.
#   Shorts consistently outperform long-form until channel has pre-warmed audience.
#
# Five virality levers (from Medium audit, injected into every DS generation):
#   1. Title — signals the RIGHT reader AND creates tension simultaneously.
#   2. First paragraph — open with specific incident or counter-intuitive fact.
#      Remove-first-paragraph test: if article reads fine without it, it's filler.
#   3. Subheadings as hooks — "The Bug That Cost Me 3 Days" not "The Problem".
#   4. [QUOTABLE] sentence — the one line a stranger would screenshot.
#   5. Ending — quotable sentence, question, or one-line implication.
#      Never bullet recap. Never "Let me know your thoughts."
#
# Publishing workflow: Substack-first (breathofdatascience.substack.com),
#   then Medium cross-post with --canonical-url pointing to Substack.
# ─────────────────────────────────────────────────────────────────────────────

NICHE_SEEDS = {
    "ds": {
        "google": [
            "data scientist career 2026",
            "data science vs AI engineering",
            "agentic AI data science",
            "Claude for data scientists",
            "data scientist skills 2026",
            "python data science tutorial",
            "data science job market 2026",
        ],
        "medium_rss": [
            "https://medium.com/feed/tag/data-science",
            "https://medium.com/feed/data-science-collective",
            "https://medium.com/feed/towards-data-science",
        ],
        "youtube_search": [
            "data science career advice 2026",
            "AI tools for data scientists",
            "python for data science beginners",
            "data scientist vs AI engineer",
        ],
        # Competitor channels to monitor for angle gaps (do NOT copy — find the gap):
        "competitor_channels": ["@KenJee_ds", "@LukeBarousse", "@mavgpt", "@tessa.fairbrook"],
    },
    "life": {
        "google": ["self improvement 2026", "productivity habits", "mindset shift", "personal growth"],
        "medium_rss": [
            "https://medium.com/feed/tag/self-improvement",
            "https://medium.com/feed/tag/productivity",
            "https://medium.com/feed/tag/personal-development",
        ],
        "youtube_search": ["self improvement 2026", "mindset habits", "productivity tips"],
    },
    "poetry": {
        "google": ["poetry 2026", "spoken word trending", "emotional poetry"],
        "medium_rss": [
            "https://medium.com/feed/tag/poetry",
            "https://medium.com/feed/tag/creative-writing",
        ],
        "youtube_search": ["poetry spoken word 2026", "emotional poetry"],
    },
}
```

**`fetch_google_suggest(queries: list[str]) -> list[str]`**
- URL: `http://suggestqueries.google.com/complete/search?client=firefox&q=<query>`
- No API key needed, returns JSON array. Parse `[1]` for suggestions list.
- Deduplicate across all queries. Return flat list of suggestion strings.

**`fetch_medium_rss(feed_urls: list[str]) -> list[dict]`**
- Use `feedparser`. For each entry return `{title, url, pub_date, tags}`.
- Sort by pub_date descending. Return top 30 across all feeds.
- Medium RSS does NOT include clap counts — use title/pub_date/tags only as signal.

**`fetch_youtube_trending(search_terms: list[str]) -> list[dict]`**
- Use YouTube Data API v3 search endpoint (`GOOGLE_CONSOLE_API_KEY` from `.env`).
- Search each term, type=video, order=relevance, publishedAfter=7 days ago.
- Return `{title, channel, view_count, like_count, published_at}` for top 5 per term.
- If API key unavailable or quota exceeded: fall back to scraping `https://www.youtube.com/results?search_query=<term>&sp=EgIIAQ%3D%3D` (upload date filter) for titles only.
- Deduplicate. Return top 20.

---

### `patterns.py` — Hook pattern extractor

Receives the raw signals dict and uses Claude CLI to extract reusable patterns.

```python
def extract_patterns(signals: dict, niche: str) -> dict:
    """
    Takes raw signals (Google suggestions, Medium titles, YouTube titles).
    Calls Claude CLI once to extract:
      - hook_structures: title-level structures (e.g. "N things I learned after X years")
      - high_signal_words: words/phrases appearing frequently in top titles
      - title_formulas: fill-in-the-blank templates extracted from actual top titles
      - emotional_triggers: for life/poetry — the emotional register that appears most
    Returns a dict. Cached as part of the weekly research brief.
    """
```

**The Claude CLI prompt this sends (construct it dynamically, injecting niche context):**

For DS niche, the prompt includes a hardcoded differentiation block before the signal data:

```
You are a content virality analyst for a data science creator with these specifics:
- 10 years as a practitioner (not a teacher or educator — an actual data scientist)
- Indian perspective, Hinglish-capable voice, emotional honesty about the field
- Audience: mid-career data scientists anxious about AI's impact on their jobs
- Competitors to differentiate FROM: mavgpt (AI tips, mass-market), Ken Jee (projects),
  Luke Barousse (employer-focused), tessa.fairbrook (Claude carousels).
  None of them write from 10 years of real DS practice with career survival honesty.

What has worked in THIS creator's own content (real Medium read ratio data):
- Named discovery pattern ("I Wish I Had Known...", 55% read ratio)
- Specific technical problem ("Data Quality & Measurement...", 54%)
- Named concept with tension ("Zero Frequency Problem", 52%)
- Efficiency framing ("...in an efficient way", 44%)
- Provocation-first even at lower read ratio still earns more per view

What has FAILED in this creator's content:
- Pure label titles ("Understanding X", 20%)
- Double generic question format ("What is X? What is Y?", 15%)
- Exhausted phrases ("secret sauce", "be consistent", 21%)
- Series numbering in titles kills cold traffic

Here are the top-performing titles this week in the data science niche across
Medium, Google search suggestions, and YouTube.

MEDIUM TITLES (last 7 days):
[list]

GOOGLE SUGGEST (what people are searching):
[list]

YOUTUBE TITLES (most relevant this week):
[list]

Extract the following in JSON:
{
  "hook_structures": [
    // 5-8 structural patterns found in multiple top titles
    // e.g. "Personal credential + time frame + contrast (what you thought vs reality)"
    // Prioritise structures that ALSO appear in this creator's top-performing history
    // Be abstract — these are templates, not specific titles
  ],
  "high_signal_words": [
    // 10-15 words or short phrases appearing across sources with high engagement
    // Must feel credible from a 10-year practitioner — no overclaiming
    // e.g. ["agentic", "10 years", "actually", "nobody tells you", "replaced", "honest"]
  ],
  "title_formulas": [
    // 3-5 fill-in-the-blank title templates
    // At least one must use the Named Discovery pattern
    // At least one must use Specific Technical Problem framing
    // e.g. "I [did X] for [N years]. Here's what [topic] actually [did/changed/taught me]."
  ],
  "emotional_register": "[curiosity|fear|aspiration|validation|urgency]",
  "differentiation_angle": "// One sentence: what gap in this week's trending content can this creator fill that mavgpt/Ken Jee/Luke Barousse cannot?"
}

Return only valid JSON. No commentary.
```

Use `call_claude(prompt, cache=True, ttl_days=7, temperature=0.3)` — analytical task, low temperature.

---

### `scorer.py` — Angle scorer

```python
def score_angles(candidate_angles: list[str], patterns: dict, signals: dict, avoid_list: list[str]) -> list[dict]:
    """
    Scores each candidate angle (from Medium titles + Google suggestions + user ideas)
    against the extracted patterns and signals.

    Scoring factors (0.0–1.0 each, weighted):
      - signal_overlap (0.35): how many high_signal_words appear in the candidate title
      - structure_match (0.30): does the title match one of the extracted hook_structures
      - search_intent (0.20): does the title echo a Google suggest phrase
      - novelty (0.15): is this NOT in the avoid_list (last 90 days tracker)

    Final score = weighted sum, normalized to [0, 1].
    Returns sorted list: [{title, score, matched_structure, signal_words_found, source}]
    """
```

No Claude CLI call here — pure Python scoring. Fast and deterministic.

---

### `blocks.py` — Platform-specific virality block generator

This is what every generator script calls. It returns a formatted string that goes into the Claude CLI prompt for content generation.

```python
PLATFORMS = ["medium_blog", "linkedin_post", "linkedin_deck", "ig_carousel", "ig_reel", "yt_short"]

def virality_block(platform: str, niche: str, research_brief: dict) -> str:
    """
    Returns a compact, platform-specific virality instruction block.
    Every content generation prompt must start with this.
    """
```

**What each platform block must contain:**

`medium_blog` (DS niche specifics baked in from real audit data):
- Title must use one of: Named Discovery / Specific Technical Problem / Named Concept with tension / Efficiency framing / Provocation-first. Never: pure label, double-question, exhausted phrases.
- Hook instruction: use the week's top `hook_structures` + `title_formulas` from patterns. The differentiation_angle from patterns.py must be visible in the angle.
- Voice: 10-year practitioner — not a teacher explaining basics, a colleague being honest. Analytical but warm. Personal credential is the credential, not a badge to display.
- Remove-first-paragraph test: if the article reads fine without the first paragraph, rewrite it. Open with the specific incident or counter-intuitive fact, never with context-setting.
- Subheadings must be hooks, not labels. "The Bug That Cost Me 3 Days" not "The Problem." Every subheading must pull a skimmer into reading the section.
- Mark one sentence [QUOTABLE] — the one line a stranger would screenshot.
- Ending: quotable sentence, a genuine question, or a one-line implication. Never a bullet recap. Never "Let me know your thoughts."
- Structure: hook → specific incident → insight → counterintuitive twist → [QUOTABLE] line → CTA
- CTA: follow + comment prompt that invites debate, not validation. Ask a question that a 5-year DS would disagree about.
- Length: 1200–1800 words. Curation threshold on Medium is >50% read ratio — pacing matters more than word count.
- Publishing: Substack-first (breathofdatascience.substack.com). Medium cross-post uses --canonical-url.
- Banned words: `"In conclusion", "Dive into", "Leverage", "Game-changer", "Synergy"`

`linkedin_post`:
- Hook: first line must stop scroll — use `high_signal_words`, no link, no emoji spam
- Format: short paragraphs (2–3 lines max), white space is engagement
- Link rule: NEVER in post body — goes in first comment
- Poll optional (max 30 chars per option)
- CTA: drive to comment (not link click) — "What's your take?" or "Comment X for the full breakdown"
- Length: 150–300 words

`linkedin_deck`:
- Slide 1: bold claim (use a `title_formula` from patterns)
- Slides 2–6: one proof point per slide, stat or story each
- Final slide: single CTA — follow + comment keyword
- Each slide: headline (≤8 words) + 1–2 supporting lines

`ig_carousel`:
- Slide 1 = hook slide: big text, single idea, matches the week's `emotional_register`
- Slides 2–9: one insight per slide, short sentence + visual cue description
- Slide 10 = CTA slide: "Save this" + "Follow for [value prop]"
- Each slide: ≤15 words of text content

`ig_reel` (DS niche: informed by real Shorts performance data):
- First 3 seconds: state the practitioner frustration or specific problem — not a question, a statement. Proven DS hooks: "Why Your Code Breaks in Docker", "The First Skill Python Tutorials Skip", "Reading Python Errors". Pattern = specific problem a working DS hits, not a learning topic.
- 5-beat structure: Hook → Problem (name the exact frustration) → Reveal (what you actually do after 10 years) → Payoff (the counter-intuitive truth) → CTA
- CTA: comment a keyword → DM (mavgpt model, already in pipeline). For free_tool_ds project: keyword = FLOW. For free_tool_life: keyword = SYSTEM.
- Tone: confident practitioner sharing the thing nobody told you — not a teacher, a colleague
- No series numbering in titles or hooks — kills cold traffic
- No: talking to camera for more than 30 seconds without a visual cut

`yt_short`:
- First frame: bold text overlay — must be readable in thumbnail
- Hook spoken in first 2 seconds
- No intro: start mid-sentence or mid-action
- End on a cliffhanger or hard CTA (subscribe/watch next)
- Max 55 seconds scripted

---

### `cache.py` — Cache management

```python
CACHE_DIR = Path("v2/cache")
SIGNAL_TTL_DAYS = 7

def signal_cache_path(niche: str, week: str) -> Path: ...
def is_cache_fresh(path: Path) -> bool: ...   # checks TTL
def write_cache(data: dict, path: Path): ...
def read_cache(path: Path) -> dict: ...
```

Cache is JSON files in `v2/cache/`. Filename: `research_<YYYY-Wnn>_<niche>.json`.

---

## Implementation Rules

1. **Reuse v1 infra libs** — import `claude_cli`, `schedule_calc`, `content_paths`, `hashtags`, `niche_config` from `v1/scripts/lib/` via `sys.path.insert`. Do not copy-paste.
2. **Never import v1 virality.py** — v2 has its own engine. Read v1 virality.py for context, then close it.
3. **All Claude CLI calls via `v1/scripts/lib/claude_cli.py:call_claude()`** — never shell out to `claude` directly.
4. **Research cache is king** — `weekly_research.py` runs once. `daily.py` reads from cache. Never re-fetch if cache exists and is < 7 days old.
5. **Every generator starts with `virality_block(platform, niche, research_brief)`** — this is non-negotiable. The research brief is passed in so the block is live-signal-informed, not static.
6. **Tracker before writing** — `tracker_sync.py read` runs before any generation and its avoid_list feeds the scorer.
7. **Paths via content_paths.py** — all file paths follow v1 conventions, extended for v2 subdirectory.
8. **No full-file outputs in chat** — write iteratively using targeted edits.
9. **Error handling** — every script exits gracefully with a clear message if cache missing, tracker unreadable, or API quota exceeded (fall back, never crash).

---

## Build Order

Build in this order — each step depends on the previous:

1. `lib/virality/cache.py` — cache I/O only, no dependencies
2. `lib/virality/signals.py` — live fetchers (Google, Medium, YouTube)
3. `lib/virality/patterns.py` — Claude CLI pattern extractor
4. `lib/virality/scorer.py` — pure Python scorer, no Claude
5. `lib/virality/blocks.py` — platform-specific block generator
6. `lib/virality/__init__.py` — exports: `virality_block`, `score_angles`
7. `tracker_sync.py` — tracker read/write
8. `lib/research.py` — curates brief (wraps signals + patterns + scorer)
9. `weekly_research.py` — orchestrates research pipeline, writes cache
10. `lib/angle_picker.py` — terminal UI
11. `blog_generator.py` — blog via Claude CLI + v2 virality
12. `derivatives.py` — all CC derivatives via Claude CLI + v2 virality
13. `viral_reel.py` — reel script via Claude CLI + v2 virality
14. `daily.py` — orchestrates everything

After each step, test in isolation before moving to the next.

---

## Test Commands (run these after building)

```bash
# 1. Fetch research for DS (this week)
python v2/scripts/weekly_research.py --niche ds

# 2. Check cache was written
cat v2/cache/research_$(python -c "from v1.scripts.lib.schedule_calc import get_iso_week; from datetime import date; print(get_iso_week(str(date.today())))")_ds.json | python -m json.tool | head -40

# 3. Run daily briefing (dry run, no generation)
python v2/scripts/daily.py --dry-run

# 4. Generate a blog (pick angle 1)
python v2/scripts/blog_generator.py --niche ds --angle "What 10 years in data science actually taught me about AI"

# 5. Generate all derivatives from that blog
python v2/scripts/derivatives.py --blog v2/content/blogs/$(python -c "from v1.scripts.lib.schedule_calc import get_iso_week; from datetime import date; print(get_iso_week(str(date.today())))")/$(ls v2/content/blogs/**/*.md 2>/dev/null | tail -1 | xargs basename) --niche ds
```

---

## Done When

- [ ] `python v2/scripts/daily.py` runs without error and prints a briefing for today
- [ ] Weekly research cache is written to `v2/cache/`
- [ ] Blog is generated with virality block visible in the prompt (confirm via `--verbose`)
- [ ] All 4 derivatives are written to the correct paths
- [ ] No v1 files were modified
