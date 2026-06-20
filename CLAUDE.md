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
| Substack   | [breathofdatascience.substack.com](https://breathofdatascience.substack.com) · [breathofpoetry.substack.com](https://breathofpoetry.substack.com) · [thisisbreathoflife.substack.com](https://thisisbreathoflife.substack.com) ← accounts live, not actively publishing |
| Podcast    | [Breath of Life (Spotify)](https://open.spotify.com/show/26d2VlDaSD0bf6tucQucie) · [Breath of Poetry (Spotify)](https://open.spotify.com/show/0d7GfbQsYPc4t0idLhpYWT) |

## Operational Rules

- **UPDATE GUIDES ALWAYS:** After ANY change to scripts, pipeline, workflow, or tools — update the relevant docs in `docs/` before finishing. Guides that describe the changed thing must reflect the new reality. Never leave docs stale.
  - Script changed → update `docs/video-production-guide.md` or relevant day guide
  - New tool/command added → add to setup section of `docs/weekly-operating-guide.md`
  - Workflow step changed → update the day guide (`docs/saturday.md`, `docs/friday.md`, etc.)

## Content Rules

- **TRACKER FIRST:** Always check `output/trackers/annual-tracker-2026.xlsx` before writing — avoid angles covered last 90 days
- **KB FIRST:** Always read `data/kb/master_brief.md` before any content decisions
- **NO REPEAT ANGLES:** Read Content Title + Niche + Posting Date from the tracker; flag any overlap within 90 days

## Virality & Build-in-Public Projects

- **VIRALITY ENGINE (automatic):** `scripts/lib/virality.py` injects a compact virality block
  (hook + ONE CTA + specificity + guardrail) into EVERY generator + both shorts pipelines, routed
  by niche: **poetry/life → `data/kb/voice/`** (emotional, feel-seen), **DS / `--project` →
  `data/kb/reels/`** (build/teach). Topic selection is virality-weighted in `scripts/idea_scorer.py`.
  Pass `--project <key>` to any generator to layer in a build-in-public project's pitch/angle/DM.
  Edit the KB markdown to change behavior — the engine reads it at runtime.
  For caption content types (IG/shorts caption, social image, overlay scene plan) it also injects a
  **per-niche caption/thumbnail formula** — the `## Engine digest (compact)` section of
  `data/kb/reels/06_mavgpt_caption_formula.md` (DS: caption-IS-product, comment→DM CTA, full value
  verbatim, outcome thumbnail), `data/kb/voice/life_formula.md`, and `data/kb/voice/poetry_formula.md`.
- **REEL FORMULA:** For any short-form reel/Short, follow `data/kb/viral_reel_formula.md`
  (5-beat structure reverse-engineered from a reel that hit 38,501 views / 1.1k saves). Use its hook
  taxonomy (`data/kb/twitter_hook_patterns.json`) and the beat→Remotion-scene map. Never skip the
  hook re-record/regenerate step — first 3 seconds decide everything.
- **PROJECTS REGISTRY:** Build-in-public projects (e.g. autopilot-jobhunt) live in
  `data/kb/projects.json` — repo, UTM campaign, DM keyword, weekly cadence, honesty guardrail,
  per-channel plan. Read it before producing project content; rotate `cadence.angle_rotation`.
- **HONESTY GUARDRAIL:** State what a tool actually does. Never overclaim (e.g. don't say a job
  tool "auto-applies" if it only drafts). Overclaiming kills trust and invites roasting.
- **DISTRIBUTION (auto-publish daemon — "subtract to focus", 2026):** One piece → viable
  channels via `prompts/repurposing_agent.md` → per-platform derivatives → staged by
  `scripts/load_posts.py` → fired by the `scripts/scheduler.py` daemon. **LinkedIn is ACTIVE**
  (employer cleared). **Instagram / Threads** auto-publish via the Meta Graph API
  (`scripts/post_instagram.py`, `post_threads.py`, `scripts/lib/meta_graph.py`); **Facebook**
  mirrors from Instagram. **Twitter is DROPPED** (dead in analytics). Reels go to **Instagram
  Reels + YouTube Shorts only** (not LinkedIn/Twitter). The only manual steps left: record the
  video, a ~10-min content approval, and replying to comments/DMs. Excluded: Hacker News +
  Reddit (blocked). Meta tokens: see `docs/one-time-platform-setup.md`. Canonical model:
  `docs/pipeline-2026.md`.
- **STAR ATTRIBUTION:** Tag every repo link with UTM params via `scripts/lib/utm.py`.
  `scripts/collect_analytics.py` tracks GitHub stars + 7-day delta so you can see which piece
  drove stars (set `GITHUB_REPOS` env, optional `GITHUB_TOKEN`).

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
    2026-Wnn/     # upload_shorts.sh, design prompts (distribution is manual — no Metricool/Publer CSVs)
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

## CONTENT TRACKER (annual-tracker-2026.xlsx)

File: `output/trackers/annual-tracker-2026.xlsx`
Sheets: one per month (May, Jun, Jul … Dec)
Columns: ISO Week · Slug · Day · Date · Posting Date · Time · Niche · Platform · Format · Content Title · Status · ✓

Before writing any blog or content, ALWAYS:
1. Read all monthly sheets; filter rows where Posting Date is within the last 90 days
2. Group by Niche (DS / Life / Poetry) — list all unique Content Titles in that window
3. Compare new angle against that list — if the angle is covered, pick a different one
4. After publishing, update the Status field to 'Published' for all rows matching that Slug

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
- **LinkedIn link placement:** blog/repo link goes in the **pinned first comment**, never the post body (body links suppress reach)
- **Instagram (Graph API):** publishes Reels / single image / carousel only; ingests from a **public media URL** (not local bytes) — host the asset first. Stories are not API-publishable.
- **Twitter:** DROPPED from the pipeline (no derivatives, polls, or staging)
- **Worksheet delivery:** DS & Life niches only; URLs auto-injected into captions via `scripts/inject_worksheet_ctas.py` (W22 onwards; retroactive support available). This is the **owned-audience email capture** (Substack retired)

## Development Status

This project is currently a scaffold — directories exist but implementation files (scripts, agents, automation) are not yet built. When adding code, prefer Python or Node.js consistent with whatever is introduced first.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- ALWAYS read graphify-out/GRAPH_REPORT.md before reading any source files, running grep/glob searches, or answering codebase questions. The graph is your primary map of the codebase.
- IF graphify-out/wiki/index.md EXISTS, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
