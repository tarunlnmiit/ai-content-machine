# ⚡ AI CONTENT CREATION MACHINE
## The Complete Playbook v11

> ⚠️ **Distribution is now MANUAL — this doc predates that change.** Wherever this playbook
> says **Publer**, **Metricool**, an aggregator **CSV**, or "APScheduler fires everything to all
> platforms automatically," that is no longer true. Current model: Instagram / Facebook / Threads /
> Twitter are posted **by hand** in-app; LinkedIn can be staged into `scheduling.db` via
> `scripts/load_posts.py` for the `scheduler.py` API path but is **held manual until employer
> clearance** (daemon stays off). `derivatives_to_metricool.py` has been deleted. Authoritative
> flow: `docs/weekly-runner.md` Step 22 and `docs/daily/friday.md`.

**Architecture · Tool Stack · Existing Platform Integration · 7-Day Build Guide · Weekly SOP**

Claude Code Pro · Canva Pro · 7 Platforms · 3 Niches · ~$51/mo  
Built for a Senior Data Scientist · M4 Mac Mini · Leveraging Existing Content + Audience

---

## How to Use This Document

| Part | What It Covers | When to Read |
|------|---------------|--------------|
| Part 1 — Architecture | How the system works, data flows, agent design | Before you build anything |
| Part 2 — Tool Stack | Every tool, cost, and MCP connection | Day 0 setup |
| Part 3 — Existing Platforms | Wiring Notion, YouTube, Twitter/X, Instagram, Substack, Medium into Claude Code | Day 1–2 |
| Part 4 — 7-Day Build | Step-by-step daily instructions with exact commands | Days 1 through 7 |
| Part 5 — Weekly SOP | Your repeatable weekly workflow after the build | Every week after Day 7 |
| Part 6 — Reference | Cost breakdown, command cheatsheet, prompt templates | Ongoing |

---

> **📌 READ THIS FIRST**
> Do not skip Part 3. Your existing content in Notion, YouTube, Instagram, Twitter/X, Substack, and Medium is your biggest competitive advantage. Wiring it into Claude Code means the system learns from what already worked for your audience — not from scratch.

---

> **✅ How Scripts Call Claude — Three Engines, Three Roles**
> 
> Scripts in this system use three AI backends matched to task type:
> - **`claude -p` (Pro subscription):** blog writing only — `produce_blog.py`. Routes through your Claude Code Pro subscription. No API key needed.
> - **Claude Haiku (free Anthropic API key):** `repurpose_blog.py` and `thumbnail_brief.py`. Uses Anthropic SDK directly. Better JSON reliability and hook quality than local models for audience-facing content.
> - **Ollama — gemma4:e2b (local, zero cost):** `idea_scorer.py`, `build_knowledge_base.py` (fallback), `collect_analytics.py`. High-frequency tasks that would drain API quotas.
> 
> `produce_blog.py` makes 2 `claude -p` calls per blog run (one for the blog, one for the 3-sentence summary). That is 6 `claude -p` calls per week total (Mon + Tue + Wed, 2 each). Well within Pro limits.

---

## PART 1 — System Architecture

### 1.1 The Core Principle

One weekly recording session + three blog topics = 50+ pieces of distributed content. Every asset produced is derived from something you recorded or wrote. Nothing is fabricated from thin air. The system multiplies your effort — it never replaces your voice or thinking.

> **🧠 INTELLIGENCE HIERARCHY**  
> Claude Code reads your existing content (Notion DB) + platform performance (YouTube Analytics, Twitter/X, Instagram) + external trends (RSS feeds from subreddits, YouTube trending, Google Trends) before producing anything new. Your history is its primary training signal.

### 1.2 End-to-End Data Flow

| Stage | Input | Process | Output | Who Does It |
|-------|-------|---------|--------|-------------|
| 0. Intelligence | Notion DB + platform analytics + trend data | `build_knowledge_base.py` reads all MCPs | `master_brief.md` — your content context file | Automated (cron, Sunday night) |
| 1. Ideation | `master_brief.md` + scraped trends | Research scripts score + rank ideas | `weekly_ideas.md` — top 3 per niche | Automated → You pick 3 (10 min Monday) |
| 2. Writing | Approved topics (Mon–Wed) | 1 blog/day via `claude -p` — Mon=DS, Tue=Life, Wed=Poetry | 2,500–3,500 word blog per niche | Mon 10 min + Tue 10 min + Wed 10 min |
| 3. Repurposing | Finished blog | `repurpose_blog.py` via Haiku API — DS repurposed Tue, Life+Poetry Wed | 7 derivative files per blog (21 total) | Tue 5 min + Wed 10 min |
| 4. Design | Derivative content + briefs | Canva Bulk Create from CSV | Thumbnails, carousels, quote cards, slides | Canva auto (5 min review) |
| 5. Recording | Blog scripts | You record once per topic | 3 videos + 2 podcast episodes/week | You (2.5 hrs Thursday) |
| 6. Publishing | All assets approved | `load_posts.py` → SQLite DB → APScheduler daemon fires posts | Twitter + LinkedIn direct API, Instagram + Facebook via Publer | Automatic — APScheduler runs continuously |
| 7. Analytics | Platform performance data | `collect_analytics.py` → summary | `weekly_insights.md` — what worked | Automated (Sunday 8pm) |

### 1.3 Agent Architecture

Five specialist agents orchestrated by Claude Code. Each agent has a defined prompt file, defined input schema, and defined output format.

| Agent | Prompt File | Primary Model | Key Input | Key Output |
|-------|------------|---------------|-----------|------------|
| Research Agent | *(no prompt file — Python scripts only)* | Ollama — gemma4:e2b | Scraped data + master_brief.md | weekly_ideas.md ranked list |
| Writing Agent | `prompts/writing_agent.md` | claude -p ONLY (Pro subscription) | Approved idea + voice guide | 2,500–3,500 word blog Markdown |
| Repurposing Agent | `prompts/repurposing_agent.md` | Claude Haiku (free API key) | Finished blog | JSON with 7 derivative formats |
| Visual Agent | *(thumbnail_brief.py script — no separate prompt file)* | Claude Haiku (free API key) | Blog title + niche | thumbnail_brief.json + slide CSV |
| Distribution Agent | *(no prompt file — pure API scripts)* | No LLM — pure API | Publishing checklist | Scheduled posts on all platforms |
| Analytics Agent | *(no prompt file — Python scripts only)* | Ollama — gemma4:e2b | Performance CSVs | weekly_insights.md plain-English summary |

### 1.4 Content Multiplication Matrix

Every blog produces these derivatives automatically via the Repurposing Agent:

| Source Blog | YouTube | LinkedIn | Twitter/X | Instagram | Podcast | Medium | Substack |
|-------------|---------|----------|-----------|-----------|---------|--------|----------|
| Data Science | Full video + Shorts | Long post + PDF carousel | 15-tweet thread | Carousel + Reel | ❌ | Republish | Summary |
| Life & Dev | Full video + Shorts | Long post | Thread | Reel + Stories | Full episode | Republish | Story |
| Poetry | Spoken word clip | Quote cards | Quote thread | Reel + Stories | Reading episode | Republish | Weekly verse |

### 1.5 Human Checkpoints (~45–60 min/week total)

| Day | Your Task | Time | Can Skip? |
|-----|-----------|------|-----------|
| Monday | Pick 3 topics + produce DS blog + fill personal sections | 25 min | No |
| Tuesday | Produce Life blog + fill personal + repurpose DS blog | 30 min | No |
| Wednesday | Produce Poetry blog + fill personal + repurpose Life & Poetry + design | 45 min | No |
| Thursday | Record all videos and podcast episodes | 2.5 hrs | No — your voice is the product |
| Friday | Run `load_posts.py`, QA Publer queue | 15 min | No |
| Sunday | Read `weekly_insights.md` | 5 min | Recommended |

---

## PART 2 — Tool Stack & Budget

### 2.1 Core Stack

| Tool | Role | Monthly Cost | Status |
|------|------|-------------|--------|
| Claude Code Pro | Primary AI engine — writing, coding, orchestration, MCPs | $20 | Purchase |
| Canva Pro | Thumbnails, carousels, slides, quote cards, Bulk Create | $0 | Already owned |
| Publer Pro | Instagram + Facebook scheduling only (Twitter and LinkedIn post directly via API) | $12 | Purchase |
| Opus Clip Starter | Auto-extract 5–7 short clips from each long video | $19 | Purchase |
| Adobe Podcast Enhance | AI noise removal and voice levelling — free web tool | $0 | Free |
| CapCut Desktop | Video editing with auto-captions | $0 | Free |
| Spotify for Podcasters | Podcast hosting and distribution | $0 | Free |
| Beehiiv | Newsletter hosting | $0 | Free |
| Ollama + gemma4:e2b | Local LLM — idea scoring, analytics summaries | $0 | Install Day 1 |
| **TOTAL** | | **~$51/month** | $99 under $150 budget |

### 2.2 Free APIs and Tools

| Tool | Role | Priority | Limit |
|------|------|----------|-------|
| YouTube Data API v3 | Trend research + channel analytics + video upload | Primary | 10,000 units/day |
| Subreddit RSS feeds | Idea scraping — no API key, no auth required | Primary | None — unrestricted |
| Reddit API (PRAW) | Enhanced post scoring (upvotes, comments) on top of RSS | Optional | 60 req/min |
| Pexels API | Stock footage and images for B-roll | Primary | 200 req/hour |
| Medium API | Auto-publish blog to Medium | Primary | No hard limit |
| Twitter/X API (Basic) | Read tweet history + post threads directly | Primary | 1,500 tweets/month write |
| LinkedIn API | Post articles and carousels directly | Primary | Requires app approval |
| Instagram Graph API | Read post analytics + post via Publer bridge | Via Publer | Subject to Meta limits |
| Notion API | Read/write your content database via official MCP | Primary | 1000 req/min |
| Google Trends (pytrends) | Unofficial Trends API for topic validation | Secondary | Informal limit |
| APScheduler | SQLite-backed post scheduler — no external service needed | Core infrastructure | No limit — runs locally |

> **📡 RSS First — Reddit API Optional**  
> Every subreddit has a public RSS feed at `reddit.com/r/SUBREDDIT_NAME/.rss`. No auth, no approval. The Reddit API (PRAW) adds upvote and comment counts on top of RSS, but RSS alone gives everything needed for trend detection.

### 2.3 MCP Connections Overview

| MCP | Connects To | What Claude Code Can Do |
|-----|-------------|------------------------|
| Notion (official) | Your entire Notion workspace | Read Contents DB; create new content pages; update Status and Notes after publishing; search by Topic or Publish Date |
| Filesystem | ~/content-machine folder | Read/write all scripts, prompts, output files, analytics, SQLite scheduling DB |
| GitHub | Your prompt library repo | Version-control all prompts, pull updates, commit changes |
| Google Drive | Drive + Docs + Sheets | Save content, read analytics sheets, create documents |
| YouTube API Scripts | Your YouTube channel | fetch_youtube_analytics.py pulls watch time, CTR, top videos; upload_youtube.py uploads and schedules |
| Twitter MCP | Your Twitter/X account | Read tweet history, post threads directly via API, search trending topics |
| Instagram (Composio) | Your Instagram Business account | Read post analytics — posting via Publer for IG and Facebook only |
| Substack (community) | Your Substack publication | Create drafts, manage posts, read subscriber data |
| Chrome DevTools MCP | Your local Chrome browser | Inspect network requests, debug API calls, monitor console logs |

### 2.4 Ollama + Gemma 4: Local AI for Zero-Cost Tasks

Your M4 Mac Mini with 24GB unified memory runs Gemma 4 models locally via Ollama. These handle high-frequency structured AI tasks — idea scoring and analytics summaries — at zero cost and with no quota limits.

> **🧠 Engine Assignment**
> 
> | Task | Engine | Reason |
> |------|--------|--------|
> | produce_blog.py | claude -p (2 calls/run × 3 blogs = **6 calls/week**) | Voice + writing quality — non-negotiable |
> | repurpose_blog.py | Claude Haiku API (~4k tokens/call × 3 = **~12k tokens/week**) | Derivatives go to your audience — Haiku's JSON and hook quality beats local models noticeably |
> | thumbnail_brief.py | Claude Haiku API (~500 tokens/call × 3 = **~1.5k tokens/week**) | Brief quality matters — Haiku outperforms Ollama here |
> | idea_scorer.py | Ollama — gemma4:e2b (local, zero cost) | Runs daily via cron — would drain free key |
> | build_knowledge_base.py | Gemini 2.5 Flash API (primary) + Ollama fallback | 1M context handles full weekly synthesis |
> | collect_analytics.py | Ollama — gemma4:e2b (local, zero cost) | Weekly factual summarisation — Ollama is fine |

**Recommended Models for M4 Mac Mini 24GB:**

| Model | Size | Best For |
|-------|------|---------|
| gemma4:e2b | ~5 GB | All-rounder — fast, reliable JSON output, idea scoring, analytics |
| gemma4:e4b | ~9 GB | Multimodal (text + image), 128K context — visual thumbnail analysis |

**The Ollama HTTP Call Pattern (used in idea_scorer.py):**

```python
# idea_scorer.py uses the Ollama HTTP API directly via requests
import requests

def call_ollama(prompt, model='gemma4:e2b'):
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={'model': model, 'prompt': prompt, 'stream': False},
        timeout=60
    )
    response.raise_for_status()
    return response.json().get('response', '')
```

**The Ollama Python library pattern (for scripts that use it):**

```python
# Install once: pip install ollama
import ollama

def call_ollama(prompt, model='gemma4:e2b'):
    response = ollama.chat(
        model=model,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response['message']['content']
```

### 2.5 Gemini 2.5 Flash — Weekly Synthesis Engine

Your free Gemini API key gives access to Gemini 2.5 Flash with a 1 million token context window. This slots into exactly one script: `build_knowledge_base.py`, which runs once per week on Sunday night.

**Free Tier:**
- Context window: 1 million tokens
- Rate limits: 10 requests/minute, 250 requests/day
- Weekly usage: 1 request — well within limits

> ⚠️ **Important:** Always use model name `gemini-2.5-flash` in API calls. Do not use `gemini-2.0-flash` (deprecated, shuts down June 1, 2026) or `gemini-3-flash-preview` (incorrect name).

**The correct Python call pattern using the new google.genai SDK:**

```python
# build_knowledge_base.py — synthesis step
# Install: pip install google-genai python-dotenv
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

combined_prompt = f"""
NOTION ARCHIVE: {notion_data}
YOUTUBE INSIGHTS: {yt_data}
TWITTER PATTERNS: {twitter_data}
INSTAGRAM INSIGHTS: {ig_data}
TRENDS: {trends_data}

Synthesise into master_brief.md with sections: topics_covered, what_worked,
hook_patterns, ig_format, rising_trends, content_gaps.
"""

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=combined_prompt
)
result = response.text

# Fallback if API hits rate limit:
# except Exception:
#     result = call_ollama(combined_prompt, model='gemma4:e4b')
```

Get your API key at aistudio.google.com.

### 2.6 Instagram Insights — Metric-Based Format Selection

`data/kb/ig_insights.json` is generated by `scripts/generate_ig_insights.py`. It analyses your existing `instagram_posts.json` engagement data (views, reach, saves, likes, shares, comments) to determine which format — carousel, reel, or single-image — performs best per niche.

**Run once to generate:**
```bash
python3 scripts/generate_ig_insights.py
```

This uses no AI — pure metric analysis. The file is read by `repurpose_blog.py` to automatically pick the right IG format per niche. Regenerate whenever you want refreshed recommendations (monthly is sufficient).

### 2.7 gemma4:e4b Multimodal — Optional Visual Analysis

gemma4:e4b accepts image inputs alongside text. This is useful for two optional tasks:

1. **Thumbnail CTR pattern extraction** — feed top 20 YouTube thumbnails + CTR data. gemma4:e4b identifies which visual elements correlate with above-average performance. Output saved to `data/kb/thumbnail_patterns.json`.
2. **Pre-publish thumbnail review** — upload a new thumbnail in the Streamlit Content Review tab. gemma4:e4b compares it against `thumbnail_patterns.json` and flags weaknesses.

These are **optional enhancements** — the core system works without them.

```python
# Multimodal call — text + image, runs entirely locally
import ollama

def analyse_image(image_path, prompt):
    response = ollama.chat(
        model='gemma4:e4b',
        messages=[{'role': 'user', 'content': prompt, 'images': [image_path]}]
    )
    return response['message']['content']
```

### 2.8 Streamlit Local Dashboard

A Streamlit app running locally gives you a browser-based control panel for the entire system.

| Tab | What It Shows | Key Action |
|-----|--------------|-----------|
| Monday — Topic Picker | master_brief.md + weekly_ideas.md side by side | 3 topic input fields + Confirm button writes topics.json |
| Content Review | Each blog with [PERSONAL_INSERT] sections highlighted | Approve button triggers repurpose_blog.py automatically |
| Publishing Queue | SQLite posts table — scheduled, when, which platform | Reschedule, delete, or manually add a post |
| Analytics | Charts from performance.csv — views, engagement by platform | Weekly insights summary rendered as formatted text |
| Logs | Live tail of cron output, script logs, APScheduler activity | Refresh button + error highlighting for failed posts |

```bash
streamlit run dashboard/app.py   # opens at localhost:8501
```

---

## PART 3 — Existing Platform Integration

### 3.1 The master_brief.md — Your Intelligence Hub

Every Sunday at 10pm, `build_knowledge_base.py` queries every connected platform and writes `data/kb/master_brief.md`. This file is injected into every Writing Agent call.

| Section | Source | Signal Extracted |
|---------|--------|-----------------|
| Content Archive | Notion MCP | Published items — check Name, Topic, Publish Date to prevent repeating angles covered in last 90 days |
| YouTube Winners | YouTube Analytics API | Top 20 videos by watch time + CTR — what format/length/topic your audience prefers |
| Hook Patterns | Twitter MCP / twitter_hook_patterns.json | Opening hooks that drove highest engagement |
| Visual Patterns | ig_insights.json (metric analysis) | Which post types (carousel vs reel vs story) get most saves and profile visits |
| Audience Questions | Subreddit RSS feeds + YouTube comments | Real questions your niche audience is asking this week |
| Trend Signals | pytrends + YouTube trending | Topics rising right now in your 3 niches |
| Gap Analysis | Claude synthesis of all above | Topics your audience wants that you haven't covered yet |

### 3.2 Notion Integration

**1. Install the Notion MCP:**
```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
```

**2. Verify your Notion Contents Database has these properties:**

| Property | Type | Purpose |
|----------|------|---------|
| Name | Title | Content title — primary identifier |
| Status | Status | Idea → Started / Script / Editing / Uploaded / Ready to publish → Published / Archived |
| Type | Select | Post, Podcast, Video, Article, Blog post, Shorts, Poem, Reel, Slidedeck, Poll |
| Topic | Select | Life, Poetry, Tech — maps to your 3 niches |
| Publish Date | Date | Scheduled or actual publish date — used for 90-day recency check |
| Platforms | Relation | Linked to Platforms DB |
| Content Topics | Relation | Linked to Content Topics DB |
| Posting schedule | Relation | Linked to Posting schedule DB |
| Day of Week | Rollup | Rolled up from Posting schedule |
| Posting Time | Rollup | Rolled up from Posting schedule |
| Assigned To | Person | Who is responsible for this content |
| Notes | Text | Engagement scores, post-publish notes, context |
| Description | Text | Brief description of the content angle |

### 3.3 YouTube Integration

`scripts/fetch_youtube_analytics.py` pulls watch time, CTR, top videos, and subscriber data. `scripts/upload_youtube.py` uploads and schedules via YouTube Data API v3.

Required in `.env`:
```
GOOGLE_CONSOLE_API_KEY=your_key
```

### 3.4 Twitter/X Integration

**Build your hook pattern library (once-only):**

If your Twitter archive is available: go to Settings → Your Account → Download an archive of your data. Unzip and place `tweets.js` in `data/twitter-archive/`. Then in a Claude Code session:

```
Read data/twitter-archive/tweets.js — find my 50 highest-engagement tweets.
Extract the opening hook patterns. Group into 8 categories.
Save as data/kb/twitter_hook_patterns.json with examples per category.
```

> ⚠️ **Twitter Archive Unavailable?** Twitter archives can take 24–48 hours to prepare and may be unavailable for some accounts. If you cannot get your archive, skip this step. `repurposing_agent.md` contains embedded fallback hook patterns that cover all 6 categories. Once your archive arrives, run the above to upgrade to your personalised patterns.

### 3.5 Instagram Integration

`data/kb/ig_insights.json` is generated from `data/analytics/instagram_posts.json` by `scripts/generate_ig_insights.py`. No image analysis required — pure metric-based format recommendations per niche.

```bash
python3 scripts/generate_ig_insights.py
# Saves data/kb/ig_insights.json
# Prints best format per niche based on your actual engagement data
```

---

## PART 4 — 7-Day Build Plan

| Day | Focus | Est. Time | Key Deliverable |
|-----|-------|-----------|----------------|
| Day 1 | Foundation — Claude Code + folder + CLAUDE.md + MCPs | 4 hrs | Fully configured Claude Code workspace |
| Day 2 | Research + Knowledge Base pipeline | 4 hrs | Daily idea scraper running on cron + knowledge base built |
| Day 3 | Writing + Repurposing agents | 5 hrs | First 3 blogs + 21 derivative files produced |
| Day 4 | Canva design pipeline | 3 hrs | Thumbnails, slides, quote cards automated via Bulk Create |
| Day 5 | Distribution automation | 4 hrs | load_posts.py + APScheduler sends everything to all platforms |
| Day 6 | First full production run | 5 hrs | First week of content recorded, processed, and scheduled |
| Day 7 | SOP + analytics + recurring tasks | 3 hrs | System fully on autopilot with weekly cadence locked in |

---

### DAY 1 — Foundation: Setup & Configuration (~4 hours)

> **📋 BEFORE YOU START DAY 1**  
> Create accounts (Publer for IG/FB only, Composio, Beehiiv, Pexels), gather all API keys into `~/.env`, install Node.js 18+, Python 3.11+, and `pip install feedparser tweepy apscheduler streamlit pandas plotly`. This includes your free Anthropic API key from console.anthropic.com and your free Gemini API key from aistudio.google.com. Takes 30–45 minutes.

**Prerequisites Checklist:**
- ☐ Claude Code Pro purchased — install: `npm install -g @anthropic-ai/claude-code`
- ☐ Logged into Claude Code — run: `claude auth login`
- ☐ YouTube Data API v3 AND YouTube Analytics API enabled at console.cloud.google.com
- ☐ Reddit RSS test — open reddit.com/r/datascience/.rss in browser, confirm it returns XML
- ☐ Reddit API (optional) — apply at reddit.com/prefs/apps if you want enhanced scoring
- ☐ Publer Pro connected to Instagram and Facebook only (not Twitter or LinkedIn)
- ☐ Twitter/X Developer account + API keys at developer.twitter.com — OAuth 2.0 credentials
- ☐ LinkedIn Developer app at developer.linkedin.com — request r_liteprofile + w_member_social scopes
- ☐ Composio account with Instagram Business connected
- ☐ Pexels API key from pexels.com/api
- ☐ Substack credentials and Medium Integration Token in `~/.env`
- ☐ Free Anthropic API key (`ANTHROPIC_API_KEY`) in `~/.env` — get from console.anthropic.com
- ☐ `pip install anthropic` — needed for Haiku API calls in repurpose and thumbnail scripts
- ☐ Free Gemini API key (`GEMINI_API_KEY`) in `~/.env` — get from aistudio.google.com
- ☐ `pip install google-genai` — needed for Gemini Flash calls in build_knowledge_base.py
- ☐ CapCut Desktop downloaded
- ☐ Ollama installed — download from ollama.ai

**Step 1 — Create folder structure:**
```bash
cd ~
mkdir -p content-machine/{scripts,agents,prompts,content/{blogs,scripts,derivatives,archive},assets/{thumbnails,audio,video/edited},output/{scheduled,published},data/{ideas,kb,analytics}}
```

**Step 2 — Authenticate Claude Code:**
```bash
npm install -g @anthropic-ai/claude-code
claude auth login
# Verify:
claude -p "Write a haiku about data science"
```

**Step 3 — Install Ollama and pull Gemma 4:**
```bash
# Download Ollama from ollama.ai → Install for macOS
ollama --version

# Pull models
ollama pull gemma4:e2b   # fast all-rounder (~7.9GB)
ollama pull gemma4:e4b   # multimodal workhorse (~9.6GB)

# Install Python library (for scripts that use it)
pip install ollama

# Test
ollama run gemma4:e2b "List 3 trending topics in data science. Be brief."

# Auto-start Ollama on shell open
echo 'pgrep ollama > /dev/null || ollama serve &' >> ~/.zshrc
source ~/.zshrc

# Verify serving:
curl http://localhost:11434/api/tags
```

**Step 4 — Connect all MCP servers:**
```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem ~/content-machine
claude mcp add github -- npx -y @modelcontextprotocol/server-github
claude mcp add gdrive -- npx -y @modelcontextprotocol/server-gdrive
claude mcp add youtube -- npx -y @modelcontextprotocol/server-youtube
claude mcp add twitter -- npx -y @enescinar/twitter-mcp \
  --env TWITTER_API_KEY=$TWITTER_API_KEY \
  --env TWITTER_API_SECRET=$TWITTER_API_SECRET \
  --env TWITTER_ACCESS_TOKEN=$TWITTER_ACCESS_TOKEN \
  --env TWITTER_ACCESS_TOKEN_SECRET=$TWITTER_ACCESS_TOKEN_SECRET
claude mcp add instagram -- "YOUR_COMPOSIO_MCP_URL" --headers "X-API-Key:YOUR_KEY"

# Verify:
claude mcp list
```

**Step 5 — Write CLAUDE.md:**
```bash
cd ~/content-machine && claude
```
Inside the session, ask Claude Code to generate CLAUDE.md with your name, niches, voice rules, banned words, platforms, accounts, Notion rule, and KB file reference.

**Day 1 Checklist:**
- ☐ Folder structure created — `find ~/content-machine -type d`
- ☐ Claude Code authenticated — `claude -p` test works
- ☐ Ollama running — `ollama run gemma4:e2b` returns response
- ☐ gemma4:e2b and gemma4:e4b pulled
- ☐ All 7 MCP servers connected — `claude mcp list`
- ☐ CLAUDE.md written and personally reviewed

---

### DAY 2 — Research + Knowledge Base Pipeline (~4 hours)

**Step 5 — Build your Twitter hook pattern library (once-only, if archive available):**

Request your Twitter archive: Settings → Your Account → Download an archive of your data. Takes 24–48 hours. When it arrives, unzip and place in `data/twitter-archive/`, then run in Claude Code:

```
Read data/twitter-archive/tweets.js — find my 50 highest-engagement tweets.
Extract the opening hook patterns. Group into 8 categories.
Save as data/kb/twitter_hook_patterns.json with examples per category.
```

> ⚠️ **If archive is unavailable:** Skip this step. `repurposing_agent.md` contains embedded fallback hook patterns. Request the archive when convenient — it's a one-time setup.

**Step 6 — Ask Claude Code to write all research scripts:**

```
Write the following scripts in scripts/:

rss_scraper.py — RSS feed scraper for 9 subreddits (3 per niche).
Fetches reddit.com/r/SUBREDDIT/.rss — no API key required.
Parse with feedparser. Score by title keyword match + recency decay.
Optionally enrich with PRAW upvote counts if API access available.
Save top 5 per niche to data/ideas/reddit_YYYY-MM-DD.json

youtube_scraper.py — YouTube Data API v3.
Search trending in 3 niches, last 7 days.
Score by engagement rate = (likes+comments)/views.
Save top 10 to data/ideas/youtube_YYYY-MM-DD.json

idea_scorer.py — Consolidate all sources. Deduplicate, apply novelty penalty
vs Notion archive, rank top 3 per niche, write data/ideas/weekly_ideas.md.
Use Ollama (gemma4:e2b) via HTTP POST to localhost:11434/api/generate.

build_knowledge_base.py — Reads: Notion, YouTube, Twitter, Instagram, trends.
Synthesis step uses Gemini 2.5 Flash (model: 'gemini-2.5-flash') via
google.genai Client: client = genai.Client(api_key=...).
Writes: data/kb/master_brief.md.
Fallback if Gemini unavailable: gemma4:e4b via Ollama.

generate_ig_insights.py — Reads data/analytics/instagram_posts.json,
calculates save-weighted engagement scores per format (reel/carousel/single-image),
outputs niche recommendations to data/kb/ig_insights.json. No AI — pure metrics.
```

**Step 7 — Run everything once manually:**
```bash
python3 scripts/rss_scraper.py && echo 'RSS OK'
python3 scripts/youtube_scraper.py && echo 'YouTube OK'
python3 scripts/idea_scorer.py && echo 'Scorer OK'
python3 scripts/build_knowledge_base.py && echo 'KB OK'
python3 scripts/generate_ig_insights.py && echo 'IG Insights OK'

cat data/ideas/weekly_ideas.md
cat data/kb/master_brief.md
cat data/kb/ig_insights.json
```

**Step 8 — Set up cron jobs:**
```bash
# Find full paths first:
which python3   # e.g. /usr/bin/python3
which claude    # e.g. /Users/yourname/.npm-global/bin/claude

crontab -e
```

Add:
```bash
# Daily research (6 AM): Reddit + YouTube scrape + idea scoring
0 6 * * * cd ~/content-machine && /FULL/PATH/python3 scripts/rss_scraper.py && /FULL/PATH/python3 scripts/youtube_scraper.py && /FULL/PATH/python3 scripts/idea_scorer.py >> data/analytics/research_log.txt 2>&1

# Weekly synthesis (Sunday 10 PM): Build knowledge base
0 22 * * 0 cd ~/content-machine && /FULL/PATH/python3 scripts/build_knowledge_base.py >> data/analytics/kb_log.txt 2>&1
```

> ⚠️ **Cron PATH issue:** Cron runs in a minimal shell without your `~/.zshrc` or `~/.bash_profile`. Always use full absolute paths for python3 and claude. Find them with `which python3` and `which claude`.

**Day 2 Checklist:**
- ☐ Twitter archive requested (or skip noted — archive may take 24–48 hrs to arrive)
- ☐ `twitter_hook_patterns.json` built (or deferred — embedded fallback active in repurposing_agent.md)
- ☐ All 5 scripts run without errors
- ☐ `weekly_ideas.md` contains real, ranked ideas
- ☐ `master_brief.md` contains insights from your real platform data
- ☐ `ig_insights.json` exists in data/kb/
- ☐ Both cron jobs active — `crontab -l`

---

### DAY 3 — Writing + Repurposing Agents (~5 hours)

**Step 9 — Build the prompt library:**

```
Create prompts/writing_agent.md —
  Incorporates voice rules from CLAUDE.md.
  Always reads data/kb/master_brief.md before writing.
  Queries Notion for existing coverage before choosing angle.
  Structure: Hook(150w) Context(200w) 4xSections(400w) Takeaway(200w) CTA(100w).
  Marks personal anecdote spots with [PERSONAL_INSERT].
  Output: clean Markdown.

Create prompts/repurposing_agent.md —
  Takes full blog. Outputs valid JSON with keys:
  twitter_thread, linkedin_post, instagram_caption,
  newsletter_summary, slide_outline, youtube_metadata, polls.
  Uses twitter_hook_patterns.json for thread openers (embedded fallback if absent).
  Uses ig_insights.json to choose IG format (embedded fallback if absent).

Create prompts/podcast_agent.md —
  Life and Poetry niches only. Conversational, 20-25 min.
  No bullet points — natural speech patterns throughout.
```

> **🔑 Three-Engine Architecture**
> - `claude -p` (Pro): blog writing only — 2 calls per blog (blog + summary) × 3 blogs = **6 calls/week**
> - Claude Haiku (free API key): repurposing + thumbnail briefs — ~13,500 tokens/week
> - Ollama (local, zero cost): idea scoring, KB synthesis fallback, analytics

**Step 10 — Write produce_blog.py:**

```
Write scripts/produce_blog.py that:
- Accepts: --topic 'topic' --niche ds|life|poetry
- Reads: prompts/writing_agent.md and data/kb/master_brief.md
- Builds combined prompt: writing_agent.md + master_brief.md + topic
- Calls claude -p via subprocess (1st call — generates blog):
  result = subprocess.run(['claude', '-p', combined_prompt], capture_output=True, text=True)
- Saves blog to: content/blogs/YYYY-MM-DD_{niche}_{slug}.md
- Makes a 2nd claude -p call to generate a 3-sentence summary of the blog
- Prints: word count and 3-sentence summary when done
```

**Step 11 — Write repurpose_blog.py:**

```
Write scripts/repurpose_blog.py that:
- Accepts: --input path/to/blog.md
- Reads: prompts/repurposing_agent.md + data/kb/twitter_hook_patterns.json (optional)
  + data/kb/ig_insights.json (optional — graceful fallback if either absent)
- Loads ANTHROPIC_API_KEY from .env using python-dotenv
- Builds combined prompt: repurposing_agent.md + hook patterns + ig insights + blog content
- Primary: calls Claude Haiku via Anthropic SDK:
    from anthropic import Anthropic
    client = Anthropic()
    message = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=4096,
        messages=[{'role': 'user', 'content': combined_prompt}]
    )
- Parses JSON response, saves each key as a separate file:
    content/derivatives/{slug}/twitter_thread.txt
    content/derivatives/{slug}/linkedin_post.txt
    content/derivatives/{slug}/instagram_caption.txt
    content/derivatives/{slug}/newsletter.txt
    content/derivatives/{slug}/slide_outline.json
    content/derivatives/{slug}/youtube_metadata.json
    content/derivatives/{slug}/polls.json
- If JSON parse fails, retry once with explicit JSON-only instruction
- Print token usage at end so you can track against free tier
- Fallback: if Haiku API fails (rate limit / quota / network), automatically retry
  using claude -p subprocess (graceful degradation — system never fully stops)
```

**Step 12 — First production run (Mon/Tue/Wed spread):**

📅 **MONDAY — 2 claude -p calls (DS blog + summary):**
```bash
python3 scripts/produce_blog.py --topic 'YOUR DS TOPIC' --niche ds
grep -rn 'PERSONAL_INSERT' content/blogs/   # fill these now
```

📅 **TUESDAY — 2 claude -p calls (Life blog + summary) + Haiku API (repurpose DS):**
```bash
python3 scripts/produce_blog.py --topic 'YOUR LIFE TOPIC' --niche life
grep -rn 'PERSONAL_INSERT' content/blogs/
python3 scripts/repurpose_blog.py --input content/blogs/[ds_blog].md
```

📅 **WEDNESDAY — 2 claude -p calls (Poetry blog + summary) + Haiku API (repurpose Life + Poetry):**
```bash
python3 scripts/produce_blog.py --topic 'YOUR POETRY TOPIC' --niche poetry
grep -rn 'PERSONAL_INSERT' content/blogs/
python3 scripts/repurpose_blog.py --input content/blogs/[life_blog].md
python3 scripts/repurpose_blog.py --input content/blogs/[poetry_blog].md
# Thumbnail briefs use Ollama — extracting key phrases from existing text
python3 scripts/thumbnail_brief.py --input content/blogs/[ds_blog].md
python3 scripts/thumbnail_brief.py --input content/blogs/[life_blog].md
python3 scripts/thumbnail_brief.py --input content/blogs/[poetry_blog].md
python3 scripts/generate_slides.py        # generates CSVs for all 3
python3 scripts/generate_quote_cards.py  # generates quote card CSV
```

**Day 3 Checklist:**
- ☐ All 3 prompt files created in `prompts/`
- ☐ `produce_blog.py` runs and produces a blog — check word count + [PERSONAL_INSERT] markers
- ☐ `repurpose_blog.py` runs and produces clean JSON parsed into 7 files
- ☐ Mon/Tue/Wed split confirmed — DS only Monday, Life + repurpose DS Tuesday
- ☐ First run complete: 3 blogs produced, all [PERSONAL_INSERT] filled, 21 derivative files exist

---

### DAY 4 — Canva Templates: One-Time Setup (~3 hours)

> **🎨 ONE-TIME SETUP TODAY — AUTO-RUN EVERY WEDNESDAY**  
> Build your Brand Kit and 4 master templates. After this, every Wednesday your scripts generate the CSVs and Canva Bulk Create auto-populates everything in one click.

**Step 13 — Build Canva Brand Kit and master templates:**

1. Open Canva Pro → Brand Kit → add your hex colours, fonts, and logo
2. Create YouTube Thumbnail template (1280×720px) — photo cutout zone + text overlay + background area. Save as Brand Template.
3. Create LinkedIn Carousel template (1080×1080px) — title slide + 4 content slides + CTA slide. Save as Brand Template.
4. Create Instagram Story template (1080×1920px) — quote + attribution + your handle. Save as Brand Template.
5. Create Slide Deck template (1920×1080px) — title slide + content slide with 3 bullet zones. Save as Brand Template.

**Step 14 — Write thumbnail_brief.py and generate_slides.py:**

```
Write scripts/thumbnail_brief.py — reads a blog .md file, calls Claude Haiku via
free API key to generate thumbnail_brief.json:
  from anthropic import Anthropic; client = Anthropic()
  msg = client.messages.create(model='claude-haiku-4-5-20251001', max_tokens=512, ...)
  # ~500 tokens per call, 3 calls/week — negligible free tier usage
  Output: main_text (max 6 words), sub_text (max 10 words),
  background_mood, colour_palette (3 hex codes), canva_search_term.
  Saves to content/derivatives/{slug}/thumbnail_brief.json

Write scripts/generate_slides.py — reads slide_outline.json, outputs CSV:
  slide_number, title, bullet1, bullet2, bullet3.
  Saves to output/scheduled/{slug}_slides.csv

Write scripts/generate_quote_cards.py — reads all 3 instagram_caption.txt files,
  extracts 3 best quotes per blog (under 120 chars),
  builds output/scheduled/quote_cards.csv for Canva Bulk Create.
```

**Step 15 — Create thumbnails (5 minutes each):**

For each of your 3 blogs:
1. Open `thumbnail_brief.json` — read `main_text` and `background_mood`
2. Open your Canva Thumbnail Brand Template
3. Search Canva's stock library using `canva_search_term`
4. Replace background, update text overlay
5. Export as PNG to `assets/thumbnails/{slug}_thumb.png`

**Day 4 Checklist:**
- ☐ Canva Brand Kit configured — colours, fonts, logo
- ☐ 4 Brand Templates built and saved
- ☐ `thumbnail_brief.py`, `generate_slides.py`, `generate_quote_cards.py` run without errors
- ☐ Wednesday design flow tested end-to-end
- ☐ All 3 thumbnails exported to `assets/thumbnails/`

---

### DAY 5 — Distribution Automation (~4 hours)

**Step 16 — Build the SQLite scheduling database:**

```
Create scripts/db_setup.py that initialises data/scheduling.db with this schema:
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,           -- twitter|linkedin|instagram|facebook
    content_text TEXT,
    media_path TEXT,
    scheduled_at DATETIME NOT NULL,
    status TEXT DEFAULT 'pending',    -- pending|posted|failed|cancelled
    thread_parent_id INTEGER,         -- for Twitter thread chaining
    metadata_json TEXT,               -- platform-specific extras
    slug TEXT,                        -- which blog this came from
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    posted_at DATETIME
);

Also create scripts/scheduler.py using APScheduler:
pip install apscheduler
Polls scheduling.db every 60 seconds for rows where:
  scheduled_at <= now AND status = 'pending'
Dispatches each post to the correct publisher function.
Updates status to 'posted' or 'failed' with timestamp.
Sets timezone explicitly: scheduler = BackgroundScheduler(timezone='Asia/Kolkata')
Run as background daemon: nohup python3 scripts/scheduler.py &
```

**Step 17 — Write all publishing scripts:**

```
scripts/post_twitter.py — reads TWITTER_CLIENT_ID + TWITTER_CLIENT_SECRET from .env.
  Uses OAuth 2.0 via tweepy. Accepts thread as list of tweet strings, posts in sequence.
  Each tweet replies to previous using in_reply_to_tweet_id.
  Returns list of posted tweet IDs. Logs to scheduling.db.

scripts/post_linkedin.py — reads LINKEDIN_ACCESS_TOKEN from .env.
  Posts text + optional image via LinkedIn API.
  Logs to scheduling.db.

scripts/load_posts.py — reads all 21 derivative files from content/derivatives/,
  calculates optimal post times per platform, inserts rows into scheduling.db.
  Twitter: Mon 9am, Tue 7pm. LinkedIn: Tue 8am, Thu 12pm.
  Instagram + Facebook: handled via Publer — generates Publer-import CSV.
```

**Day 5 Checklist:**
- ☐ `db_setup.py` creates `scheduling.db` without errors
- ☐ `scheduler.py` runs as background daemon
- ☐ `post_twitter.py` posts a test tweet
- ☐ `post_linkedin.py` posts a test LinkedIn update
- ☐ `load_posts.py` populates scheduling.db from derivative files
- ☐ Publer connected and queue verified

---

### DAY 6 — First Full Production Run (~5 hours)

Run the complete Mon–Fri sequence for real. Record all 3 videos + 2 podcast episodes on Thursday. Run `load_posts.py` on Friday. Verify APScheduler is running and posts fire correctly.

**Day 6 Checklist:**
- ☐ 3 blogs produced and [PERSONAL_INSERT] filled
- ☐ 21 derivative files in `content/derivatives/`
- ☐ All thumbnails, slides, quote cards exported from Canva
- ☐ All videos recorded and uploaded to `assets/video/edited/`
- ☐ Audio enhanced via Adobe Podcast Enhance
- ☐ `load_posts.py` run — scheduling.db populated
- ☐ APScheduler daemon running — `ps aux | grep scheduler`
- ☐ First Twitter thread + LinkedIn post fired successfully

---

### DAY 7 — SOP + Analytics (~3 hours)

**Step 18 — Set up analytics collection:**

```
Write scripts/collect_analytics.py that:
- Reads YouTube analytics via YouTube Data API v3
- Reads Twitter metrics via Twitter MCP
- Reads Instagram insights from instagram_posts.json (refreshed via Composio)
- Uses Ollama gemma4:e2b to generate a plain-English summary
- Saves to data/analytics/weekly_insights.md
Runs automatically via cron at Sunday 8pm.
```

Add to crontab:
```bash
0 20 * * 0 cd ~/content-machine && /FULL/PATH/python3 scripts/collect_analytics.py >> data/analytics/analytics_log.txt 2>&1
```

**Step 19 — Lock in the weekly SOP (Part 5 review):**

Read Part 5 below. Run through it once manually. Confirm all steps take the expected time. Note anything that needs automation or simplification.

**Day 7 Checklist:**
- ☐ `collect_analytics.py` runs and writes `weekly_insights.md`
- ☐ Analytics cron job active
- ☐ Streamlit dashboard running at localhost:8501
- ☐ Weekly SOP internalized — you can run the full week without looking at this doc

---

## PART 5 — Weekly Operating Procedure

**⏱️ TOTAL WEEKLY TIME: ~4 hours**

| Day | Your Task | Time | Commands | Machine Does Automatically |
|-----|-----------|------|----------|---------------------------|
| Monday | Pick topics + DS blog | 25 min | `cat data/ideas/weekly_ideas.md` → pick 3 topics<br>`python3 scripts/produce_blog.py --niche ds`<br>`grep -rn PERSONAL_INSERT content/blogs/` | RSS + YouTube scraper ran overnight; idea_scorer.py ranked ideas |
| Tuesday | Life blog + repurpose DS | 30 min | `python3 scripts/produce_blog.py --niche life`<br>`grep -rn PERSONAL_INSERT content/blogs/`<br>`python3 scripts/repurpose_blog.py --input [ds_blog].md` | claude -p: 2 calls (Life blog + summary); Haiku API: DS repurposing |
| Wednesday | Poetry blog + repurpose all + design | 45 min | `python3 scripts/produce_blog.py --niche poetry`<br>`grep -rn PERSONAL_INSERT content/blogs/`<br>`python3 scripts/repurpose_blog.py --input [life_blog].md`<br>`python3 scripts/repurpose_blog.py --input [poetry_blog].md`<br>thumbnail_brief × 3, generate_slides, quote_cards<br>Canva Bulk Create → export | claude -p: 2 calls (Poetry blog + summary); Haiku API: repurpose × 2 (~8k tokens) + thumbnails × 3 (~1.5k tokens) |
| Thursday | Record all content | 2.5 hrs | Record 3 videos + 2 podcasts<br>Adobe Podcast Enhance all audio<br>CapCut edit, drop files into `assets/` | — |
| Friday | QA + load schedule | 20 min | Review Streamlit Publishing Queue tab<br>`python3 scripts/load_posts.py`<br>`python3 scripts/upload_youtube.py × 2`<br>Verify APScheduler is running | APScheduler fires Twitter + LinkedIn posts automatically; Publer handles Instagram + Facebook |
| Sunday | Analytics review | 10 min | Read `data/analytics/weekly_insights.md` | `collect_analytics.py` runs at 8pm; `build_knowledge_base.py` runs at 10pm |

**Monthly Tasks (30 min, once a month):**
- Export Medium stats CSV: medium.com/me/stats → Export → drop in `data/analytics/`
- Update Notion performance scores on published content items
- Refresh prompt library: ask Claude Code to read all `prompts/` and analytics data, suggest improvements
- Review and prune cron jobs: `crontab -l` to verify all are still running
- Assess upgrade path (see Part 6.4)

---

## PART 6 — Quick Reference

### 6.1 Full Monthly Cost Breakdown

| Tool | Role | Monthly Cost |
|------|------|-------------|
| Claude Code Pro | AI engine, interactive sessions, all `claude -p` script calls | $20 |
| Canva Pro | Thumbnails, carousels, slides, Bulk Create | $0 (owned) |
| Publer Pro | Instagram + Facebook scheduling only | $12 |
| Opus Clip Starter | Auto short-clip extraction from videos | $19 |
| All APIs (YouTube, RSS, Pexels, Notion, Twitter, LinkedIn) | Research + direct publishing | $0 Free |
| Streamlit + APScheduler + SQLite | Local dashboard + scheduling infrastructure | $0 Free |
| CapCut Desktop | Video editing | $0 Free |
| Adobe Podcast Enhance | Audio cleanup | $0 Free |
| Spotify for Podcasters | Podcast hosting | $0 Free |
| Beehiiv | Newsletter | $0 Free |
| Composio | Instagram Graph API bridge | $0 (free tier) |
| **TOTAL** | | **$51/month** |

### 6.2 Command Cheatsheet

| Task | Command |
|------|---------|
| Open Claude Code in project | `cd ~/content-machine && claude` |
| Run daily research (manual) | `python3 scripts/rss_scraper.py && python3 scripts/youtube_scraper.py && python3 scripts/idea_scorer.py` |
| Build knowledge base (manual) | `python3 scripts/build_knowledge_base.py` |
| Produce a blog | `python3 scripts/produce_blog.py --topic 'TOPIC' --niche ds\|life\|poetry` |
| Repurpose a blog | `python3 scripts/repurpose_blog.py --input content/blogs/FILENAME.md` |
| Generate thumbnail brief | `python3 scripts/thumbnail_brief.py --input content/blogs/FILENAME.md` |
| Generate slides CSV | `python3 scripts/generate_slides.py --slug SLUG` |
| Generate IG insights | `python3 scripts/generate_ig_insights.py` |
| Upload video to YouTube | `python3 scripts/upload_youtube.py --video assets/video/edited/FILE.mp4 --slug SLUG` |
| Publish to Medium | `python3 scripts/publish_medium.py --input content/blogs/FILE.md --canonical-url URL` |
| Load posts into schedule | `python3 scripts/load_posts.py` |
| Check scheduling DB | `sqlite3 data/scheduling.db 'SELECT platform, scheduled_at, status, substr(content_text,1,60) FROM posts ORDER BY scheduled_at'` |
| Start APScheduler daemon | `nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &` |
| Open Streamlit dashboard | `streamlit run dashboard/app.py` |
| Collect analytics | `python3 scripts/collect_analytics.py` |
| Check all cron jobs | `crontab -l` |
| Find personal insert markers | `grep -rn 'PERSONAL_INSERT' content/blogs/` |
| Check MCP connections | `claude mcp list` |
| Push changes to GitHub | `cd ~/content-machine && git add scripts/ prompts/ CLAUDE.md && git commit -m 'update' && git push` |

### 6.3 Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| Claude Code loses context mid-session | Session too long | Break into shorter sessions. Split tasks across separate `claude` invocations. |
| RSS scraper returns empty feed | Subreddit name typo or Reddit server issue | `curl https://www.reddit.com/r/datascience/.rss \| head -50`. If empty, add `headers={'User-Agent': 'content-machine/1.0'}`. |
| YouTube API quota exceeded | Hit 10,000 units/day free limit | Reduce scraping frequency or request quota increase at console.cloud.google.com. |
| Publer fails to post to Instagram | Instagram Graph API token expired | Reconnect Instagram in Publer settings — tokens expire every 60 days. |
| Twitter post fails with 403 | OAuth token missing write access | Re-authenticate tweepy with write permissions. Verify Twitter app has Read+Write at developer.twitter.com. |
| LinkedIn post fails with 401 | Access token expired | LinkedIn tokens expire after 60 days. Re-run OAuth flow: `python3 scripts/linkedin_auth.py`. |
| APScheduler fires post at wrong time | Timezone mismatch | Set timezone explicitly: `BackgroundScheduler(timezone='Asia/Kolkata')` |
| Streamlit shows blank Publishing Queue | scheduling.db not found or empty | Run `python3 scripts/db_setup.py` first, then `python3 scripts/load_posts.py`. |
| master_brief.md is empty or generic | One or more platform MCPs disconnected | `claude mcp list` — reconnect any showing errors. |
| Blog sounds generic | [PERSONAL_INSERT] markers not filled | Always run `grep -rn 'PERSONAL_INSERT' content/blogs/` before approving a blog. |
| Ollama call times out or hangs | Ollama server not running | `ollama serve &`. Verify: `curl http://localhost:11434/api/tags` |
| repurpose_blog.py JSON parse fails | Model output wrapped in markdown | Script retries once automatically with explicit JSON instruction. If still fails, fallback chain activates. |
| repurpose_blog.py Haiku API fails | Rate limit or quota exhausted | Script falls back to `claude -p` subprocess automatically. Check usage at console.anthropic.com. |
| Free API key hits rate limit | Too many requests in short window | Add `time.sleep(2)` between consecutive Haiku calls in scripts that loop. |
| Gemini 2.5 Flash returns 429 | Weekly cron ran multiple times | Check aistudio.google.com for usage. build_knowledge_base.py falls back to Ollama gemma4:e4b. |
| Cron jobs not running | macOS sleep or permissions | System Preferences → Battery → disable sleep. `sudo chmod +x scripts/*.sh` |
| `ollama` command not found in cron | Cron uses minimal PATH | Use full path in cron: `/usr/local/bin/ollama`. Find with: `which ollama` |
| `claude` command not found in cron | Cron uses minimal PATH | Use full path. Find with: `which claude`. |
| build_knowledge_base.py Gemini error | Wrong SDK version | Ensure `pip install google-genai` (new SDK). Import: `from google import genai`. Not `google.generativeai`. |

### 6.4 Upgrade Path (Month 2+)

| Upgrade | What It Adds | Cost | Add When |
|---------|-------------|------|----------|
| HeyGen Lite (AI Avatar) | Talking head video for days you can't record | $29/mo | After YouTube hits 100 subscribers |
| Opus Clip (already in stack) | Auto-extract 5–7 short clips per video | $19/mo (budgeted) | Day 1 of Month 2 |
| Anthropic API key (paid) | Direct API access — faster, no Pro usage limit concerns | $15–20/mo usage | When you hit claude -p usage limits |
| Perplexity Pro | AI-powered research with citations | $20/mo | When research depth becomes a bottleneck |
| Descript Pro | Transcript-based video editing — faster than CapCut | $24/mo | When video editing takes more than 3 hrs/week |
| Riverside.fm Standard | Studio-quality local podcast recording | $15/mo | When audio quality becomes a priority |

---

## The Most Important Thing

The bottleneck is never the tools — it is consistency. Build the simplest version that ships real content every week. Your data science instincts will push you to over-engineer this system. Resist that. Ship first, optimise second. The system gets smarter with every week of real data it accumulates from your actual audience.

---

*Playbook v11 — corrections applied from v10. Key changes: fixed engine assignments (Haiku API primary for repurposing, not Ollama), corrected Gemini SDK syntax (google.genai, not google.generativeai), clarified produce_blog.py makes 2 claude -p calls per run (6/week total), removed nonexistent --engine flag from repurpose_blog.py, corrected ig_insights.json source (metric analysis, not image AI), updated agent architecture table (no prompt files for Research/Distribution/Analytics agents), noted Twitter archive may be unavailable with fallback guidance, standardised model name to gemini-2.5-flash throughout.*
