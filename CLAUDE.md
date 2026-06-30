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
- **PROJECTS REGISTRY:** Build-in-public projects live in `data/kb/projects.json` — repo, UTM
  campaign, DM keyword, weekly cadence, honesty guardrail, per-channel plan. Current: `autopilot`
  (job-hunt), `free_tool_ds` (Claude + n8n nightly agent, DM keyword `FLOW`), `free_tool_life`
  (Claude + Notion brain-dump→system, DM keyword `SYSTEM`). The weekly comment→DM **tool reels are
  baked into the idea machine** — `scripts/idea_scorer.py:weekly_project_reel()` auto-adds one tool
  reel per niche (DS/Life) to `data/ideas/weekly_ideas.md`, rotating `cadence.angle_rotation` by ISO
  week. Produce one with `--project free_tool_ds|free_tool_life` on the reel/derivative generators.
- **HONESTY GUARDRAIL:** State what a tool actually does. Never overclaim (e.g. don't say a job
  tool "auto-applies" if it only drafts). Overclaiming kills trust and invites roasting.
- **RAW TAKE (Life, 4×/week, additive lane):** Hinglish raw-opinion Shorts — "Someone asked me: Q"
  → unscripted opinion → landing line; IG Reel (@mistakenlyhuman) + Breath of Life Short.
  Batch-recorded. Questions live in `data/kb/raw_take_questions.json`; the idea machine
  (`scripts/idea_scorer.py:weekly_raw_take_batch`) auto-surfaces the week's 4 under Life in
  `weekly_ideas.md`, rotating by ISO week. Spec/guardrails: `docs/raw-take-format.md`. Does NOT
  replace the weekly blog / long-form / 9 reels — it's a separate low-cost lane.
- **V2 VIDEO PIPELINE (2026-06-24):** `python3 v1/scripts/run_video_pipeline.py --raw <file> --manifest <manifest.json>` runs the entire production: trim → storyboard (Opus) → HyperFrames compositions per beat (Haiku) → FFmpeg composite → final MP4. No DaVinci, no manual stops. For reels, first run `v1/scripts/prepare_reel_script.py` to generate the 5-beat script and manifest. Canonical doc: `v1/docs/v2-pipeline.md`. Beat look bibles: `v1/data/kb/design/{ds,life,poetry}_design.md` (each has a `## SHORT-FORM OVERRIDES` section for reels). All Claude calls use `claude -p` CLI subprocess — no API key.
- **VOICEOVER-FIRST LANE (additive, 2026-06-21):** Record an **audio-only voiceover** (no face)
  and `scripts/run_voiceover_week.py` builds a full-screen **B-roll-montage** long-form (landscape)
  + auto-detected **portrait shorts**, with Remotion overlay scenes and **captions burned by
  hyperframes** (drops standalone "so", raised `--caption-y`, `--no-captions` toggle). New Remotion
  composition `VoiceoverEdit` (`VoiceoverLong`/`VoiceoverShort`, `kind:"voiceover"` EditPlan).
  B-roll keywords come from the transcript, not the script. Does NOT replace the talking-head
  pipeline. Canonical doc: `docs/voiceover-runner.md`.
- **ONE-COMMAND BLOG PIPELINE (2026-06-21):** `scripts/run_blog_pipeline.py --input <blog.md>`
  (or `--topic "..." --niche <ds|life|poetry>` to write the blog first) produces ALL non-video
  derivatives + media in one idempotent run: text posts (`repurpose_blog`), social images+carousel,
  slide deck, IG reel brief, thumbnail brief+HTML, **worksheet (DS/Life)**, then stages via
  `load_posts`. `--force` redoes all; `--no-stage`/`--skip-thumbnail` opt-outs. **Videos excluded**
  (separate `run_voiceover_week.py`). Thumbnail Canva pass stays manual. Doc:
  `docs/blog-pipeline.md`.
- **WORKSHEET = AUTO, CLAUDE-DESIGNED (2026-06-30):** Worksheets (DS/Life) are now generated
  end-to-end in code — NO Canva. `scripts/generate_worksheet_html.py -i <blog.md>` runs the outline
  (`generate_worksheet_outline.py`) if needed, makes ONE `claude -p` call for the section content,
  fills the fixed "Breath Network" CSS shell (`scripts/templates/worksheet_{shell,section}.html`),
  and renders the PDF via headless Chrome (`scripts/lib/html_pdf.py`, system Chrome → Playwright
  fallback). `produce_blog.py` and `run_blog_pipeline.py` call it automatically for DS/Life
  (`--no-worksheet` to skip), then rebuild the manifest. Manifest title comes from the worksheet
  JSON `title`. Push/deploy to make the gated link live stays manual.
- **MANUAL-STEPS SIDECAR + AI-vs-STOCK IMAGE (2026-06-30):** `produce_blog.py` writes all human
  to-dos to `content/derivatives/{week}/{full_slug}/manual_steps.md` (keyed by slug — SEO title/desc,
  INSERT actions, worksheet link, image decision, publish cmd) instead of dumping them to the blog or
  console; the console just points to the file. For images it weighs **AI vs stock** per blog
  (`scripts/lib/image_decision.py`): if AI wins it emits a ready-to-paste editorial prompt (saved in
  the sidecar) and skips the Pexels fetch; else fetches stock as before. Override with
  `--image {auto,stock,ai}` (default `auto`).
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
  reels/
    2026-Wnn/     # Viral reel briefs — recording plans for standalone reels (generate_viral_reel_brief.py)
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
    2026-Wnn/     # upload_shorts.sh, design prompts (auto-publish via scheduler.py daemon — see docs/pipeline-2026.md)
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
  reels/      # Viral reel briefs — recording plans for standalone reels (generate_viral_reel_brief.py)
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
