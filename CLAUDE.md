# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Creator Profile

**CREATOR:** Tarun Gupta — 10-year data scientist and content creator

**NICHES:** Data Science/Tech · Life & Self-Development · Poetry/Quotes

**VOICE:** Analytical but warm, personal examples, no jargon without context

**BANNED WORDS:** "In conclusion", "Dive into", "Leverage", "Game-changer", "Synergy"

**PLATFORMS & ACCOUNTS:**

| Platform   | Account / URL |
|------------|---------------|
| Twitter/X  | [@mistakenlyhuman](https://twitter.com/mistakenlyhuman) |
| Instagram  | [@mistakenlyhuman](https://instagram.com/mistakenlyhuman) |
| LinkedIn   | [tarun-gupta-in](https://www.linkedin.com/in/tarun-gupta-in/) |
| Medium     | [@tarun-gupta](https://medium.com/@tarun-gupta) |
| YouTube    | [@breathofdatascience](https://youtube.com/@breathofdatascience) · [@breathoflife_](https://youtube.com/@breathoflife_) · [@breathofpoetry](https://youtube.com/@breathofpoetry) · [@breathofrelaxingsounds](https://youtube.com/@breathofrelaxingsounds) |
| Substack   | [breathofdatascience.substack.com](https://breathofdatascience.substack.com) · [breathofpoetry.substack.com](https://breathofpoetry.substack.com) · [thisisbreathoflife.substack.com](https://thisisbreathoflife.substack.com) |
| Podcast    | [Breath of Life (Spotify)](https://open.spotify.com/show/26d2VlDaSD0bf6tucQucie) · [Breath of Poetry (Spotify)](https://open.spotify.com/show/0d7GfbQsYPc4t0idLhpYWT) |

## Operational Rules

- **UPDATE GUIDES ALWAYS:** After ANY change to scripts, pipeline, workflow, or tools — update the relevant docs in `docs/` before finishing. Guides that describe the changed thing must reflect the new reality. Never leave docs stale.
  - Script changed → update `docs/video-production-guide.md` or relevant day guide
  - New tool/command added → add to setup section of `docs/weekly-operating-guide.md`
  - Workflow step changed → update the day guide (`docs/saturday.md`, `docs/friday.md`, etc.)

## Content Rules

- **NOTION FIRST:** Always query Notion Contents DB before writing — avoid angles covered last 90 days
- **KB FIRST:** Always read `data/kb/master_brief.md` before any content decisions
- **NO REPEAT ANGLES:** Check Notion Status='Published' + Publish Date for recency before choosing angle

## Folder Map

```
agents/           # Agent definitions for automated content tasks
assets/
  audio/          # Raw audio files
  thumbnails/     # Thumbnail assets
  video/edited/   # Edited video exports
content/
  scripts/        # Video scripts or prompt inputs
  blogs/          # Long-form blog posts
  derivatives/    # Repurposed/shortened content from originals
  archive/        # Retired or completed content
data/
  analytics/      # Raw platform analytics exports (YouTube, Twitter, Instagram, Medium)
  ideas/          # Content ideas database
  kb/             # Knowledge base — master_brief.md, insights, hook patterns
docs/             # Internal documentation (launchd, setup guides)
documentation/    # Playbook docs
output/
  scheduled/      # Content queued for publishing
  published/      # Released content records
prompts/          # Reusable prompt templates
scripts/          # Automation scripts for workflow tasks
```

## Project Purpose

This is a content creation and management system designed to organize a creator's full workflow — from ideation through production, repurposing, and publishing — with Claude AI and Google APIs as core integrations.

## Environment

API credentials are stored in `.env`:
- `ANTHROPIC_API_KEY_FREE` — Anthropic Claude API
- `GOOGLE_CONSOLE_API_KEY` — Google APIs (Search Console, YouTube, etc.)

## Directory Structure and Intent

```
agents/       # Agent definitions for automated content tasks
assets/       # Raw and edited media (audio/, thumbnails/, video/edited/)
content/      # Written content organized by stage
  scripts/    # Video scripts or prompt inputs
  blogs/      # Long-form blog posts
  derivatives/ # Repurposed/shortened content from originals
  archive/    # Retired or completed content
data/
  ideas/      # Content ideas database
  kb/         # Knowledge base (background context, research)
  analytics/  # Performance metrics and tracking data
output/
  scheduled/  # Content queued for publishing
  published/  # Released content records
prompts/      # Reusable prompt templates
scripts/      # Automation scripts for workflow tasks
```

## NOTION CONTENT DATABASE (Contents DB — id `df13d49a-bbfc-40cd-a8f1-d4fb98d2d4ec`)

Schema:
- **Name** (title) · **Status** (Idea/Started/Script/Editing/Ready to publish/Uploaded/Published/Archived) · **Topic** (Tech/Life/Poetry) · **URL** · **Description**

Sync top ideas to DB: `python3 scripts/sync_ideas_to_notion.py` (Sunday step 6).

Before writing any blog or content, ALWAYS:
1. Query Notion Contents DB filtering Status = 'Published' for this topic/niche
2. Check Name and Topic fields to list angles already covered in last 90 days (use Publish Date for recency)
3. Review Description and Notes fields for context on past coverage
4. Identify what has NOT been said yet — write ONLY from the unexplored angle
5. After publishing, update the item's Status to 'Published', set Publish Date, and log engagement in the Notes field

## Development Status

This project is currently a scaffold — directories exist but implementation files (scripts, agents, automation) are not yet built. When adding code, prefer Python or Node.js consistent with whatever is introduced first.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- ALWAYS read graphify-out/GRAPH_REPORT.md before reading any source files, running grep/glob searches, or answering codebase questions. The graph is your primary map of the codebase.
- IF graphify-out/wiki/index.md EXISTS, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
