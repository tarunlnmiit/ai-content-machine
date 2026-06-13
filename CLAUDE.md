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
  broll/          # B-roll video clips (fetched)
  carousels/      # HTML carousel exports
  hyperframes/
    2026-Wnn/     # ISO-week grouped video renders
  raw/            # Original camera recordings (MOV files)
  reels_video/    # Reel video compilations
  slides/         # HTML slide decks + PDFs + per-post PNG exports
  social_posts/   # Platform-specific social images (Instagram, LinkedIn, Threads, Twitter)
  stories/        # Story video formats
  video/          # Edited full-length videos and shorts
content/
  scripts/        # Video scripts or prompt inputs
  blogs/
    2026-Wnn/     # ISO-week grouped blog posts and image directories
  derivatives/
    2026-Wnn/     # ISO-week grouped slug directories (schedule.json, metadata)
  buffer/         # Pre-scheduling staging (week-1/, week-2/, week-3/ relative structure)
  archive/        # Retired or completed content
data/
  analytics/      # Raw platform analytics exports (YouTube, Twitter, Instagram, Medium)
  ideas/          # Content ideas database
  kb/             # Knowledge base — master_brief.md, insights, hook patterns
docs/             # Internal documentation (launchd, setup guides)
documentation/    # Playbook docs
output/
  animations/
    2026-Wnn/     # Remotion title cards, lower thirds, outros
  scheduled/
    2026-Wnn/     # Metricool CSVs, Publer exports, design prompts
  visuals/        # Blog cover images, HTML assets
  worksheets/
    2026-Wnn/     # PDF worksheets
prompts/          # Reusable prompt templates
remotion/public/  # Remotion project assets
  broll/          # B-roll clips by week
  videos/         # Source videos
  captions/       # SRT/JSON caption files (by week)
  edit-plans/     # Edit metadata (by week)
scripts/          # Automation scripts for workflow tasks
  lib/            # Shared utilities (schedule_calc.py, content_paths.py, etc.)
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
assets/       # Raw and edited media organized by week (2026-Wnn/ subfolders)
  raw/        # Original camera recordings
  hyperframes/ # Processed video renders (grouped by content date, not render date)
  video/      # Edited full-length exports and shorts
  social_posts/ # Platform-specific social media images
  slides/     # Slide decks and exports
content/      # Written content organized by stage
  scripts/    # Video scripts or prompt inputs
  blogs/      # Long-form blog posts (grouped by week in 2026-Wnn/ subfolders)
  derivatives/ # Repurposed content with schedule.json (grouped by week)
  buffer/     # Pre-scheduling staging (week-1/, 2/, 3/ relative numbering)
  archive/    # Retired or completed content
data/
  ideas/      # Content ideas database
  kb/         # Knowledge base (background context, research)
  analytics/  # Performance metrics and tracking data
output/       # Published and scheduled content
  animations/  # Remotion renders (grouped by week)
  scheduled/   # CSVs and scheduling files (grouped by week)
  worksheets/  # PDF worksheets (grouped by week)
prompts/      # Reusable prompt templates
remotion/     # Video editing automation
  public/broll/ # B-roll footage (grouped by week)
scripts/      # Automation scripts
  lib/        # Shared utilities (schedule_calc.py with get_iso_week(), content_paths.py)
```

### ISO-Week Organization

Files are grouped into `YYYY-Wnn/` subfolders (ISO week format) within content-holding directories:
- `2026-W21` covers May 19–25 (dates: 2026-05-21, etc.)
- `2026-W22` covers May 26–Jun 1 (dates: 2026-05-25, 2026-05-26, 2026-05-27, etc.)
- `2026-W23` covers Jun 2–8 (dates: 2026-06-01, 2026-06-04, 2026-06-08, etc.)

This replaces the flat structure where all files lived in a single directory. Key utilities:
- `scripts/lib/schedule_calc.py:get_iso_week(date_str: str) → str` — converts YYYY-MM-DD to YYYY-Wnn
- `scripts/lib/content_paths.py` — centralized path construction (e.g., `derivatives_dir(date_str, slug)`)

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

## Development Protocol (Antigravity V2.0)

**Core directives — always active:**
1. Never use `cat`/`grep`/`sed`/`ls`/bash scripts for file reading — use Read/Edit/Write tools
2. Chunk-based editing only — never output full file contents; issue targeted search-and-replace edits
3. Stop guessing — if request is ambiguous, ask one specific question instead of writing exploratory code
4. No chat clutter — write plans and 100+ line outputs to `.md` artifact files, not the chat window
5. Acknowledge and act — no preambles, no "I understand you want to…"; output the tool call

**Intent modes:**
- **Mode A (Investigatory):** "How does X work?" → search silently, output short answer only
- **Mode B (Fast Path):** small changes → find exact lines → edit → done
- **Mode C (Large Tasks):** silent research → create `implementation_plan.md` → halt for approval → execute with `task.md` checklist → verify build/tests

**After Mode C:** append design pattern used to `system_architecture.md` to prevent session amnesia.

## Platform Constraints

- **LinkedIn poll options:** max 30 characters each
- **Twitter poll options:** max 25 characters each
- **Twitter threads & polls:** CANNOT be scheduled (must post manually)
- **Worksheet delivery:** DS & Life niches only; URLs auto-injected into captions via `scripts/inject_worksheet_ctas.py` (W22 onwards; retroactive support available)

## Development Status

This project is currently a scaffold — directories exist but implementation files (scripts, agents, automation) are not yet built. When adding code, prefer Python or Node.js consistent with whatever is introduced first.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- ALWAYS read graphify-out/GRAPH_REPORT.md before reading any source files, running grep/glob searches, or answering codebase questions. The graph is your primary map of the codebase.
- IF graphify-out/wiki/index.md EXISTS, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
