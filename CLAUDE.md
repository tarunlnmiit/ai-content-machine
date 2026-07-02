# CLAUDE.md

Guidance for Claude Code in this repository.

## What this project is

Content creation and publishing system: ideation → production (video/blog) → repurposing → scheduled auto-publish. **All active code lives in `v1/` — root-level dirs are legacy/content storage.** There is no root `scripts/` implementation; orchestrators, generators, and libs are in `v1/scripts/`.

## Creator Profile

**CREATOR:** Tarun Gupta — 10-year data scientist and content creator
**NICHES:** Data Science/Tech · Life & Self-Development · Poetry/Quotes
**VOICE:** Analytical but warm, personal examples, no jargon without context
**BANNED WORDS:** "In conclusion", "Dive into", "Leverage", "Game-changer", "Synergy"

**PLATFORMS & ACCOUNTS:**

| Platform   | Account / URL |
|------------|---------------|
| Twitter/X  | [@mistakenlyhuman](https://twitter.com/mistakenlyhuman) — DROPPED from pipeline |
| Instagram  | [@mistakenlyhuman](https://instagram.com/mistakenlyhuman) |
| LinkedIn   | [tarun-gupta-in](https://www.linkedin.com/in/tarun-gupta-in/) |
| Medium     | [@tarun-gupta](https://medium.com/@tarun-gupta) |
| YouTube    | [@breathofdatascience](https://youtube.com/@breathofdatascience) · [@breathoflife_](https://youtube.com/@breathoflife_) · [@breathofpoetry](https://youtube.com/@breathofpoetry) · [@breathofrelaxingsounds](https://youtube.com/@breathofrelaxingsounds) |
| Substack   | breathofdatascience · breathofpoetry · thisisbreathoflife (.substack.com) — live, not actively publishing |
| Podcast    | Breath of Life · Breath of Poetry (Spotify) |

## Pipeline entry points (all in `v1/scripts/`)

| Command | What it does |
|---|---|
| `python3 v1/scripts/run_video_pipeline.py --raw <file> --manifest <m.json>` | V2 video: trim → storyboard → HyperFrames per-beat compositions → FFmpeg composite → MP4. Phase markers `.phase_N_done`; `--restart-from N`. Reels: run `v1/scripts/prepare_reel_script.py` first. Doc: `v1/docs/v2-pipeline.md`. Beat look bibles: `v1/data/kb/design/{ds,life,poetry}_design.md` (`## SHORT-FORM OVERRIDES` for reels). |
| `python3 v1/scripts/run_blog_pipeline.py --input <blog.md>` (or `--topic ... --niche <ds\|life\|poetry>`) | ALL non-video derivatives in one idempotent run: posts, social images+carousel, deck, IG reel brief, thumbnail, worksheet (DS/Life), then stages via `load_posts`. `--force`, `--no-stage`, `--skip-thumbnail`. Doc: `docs/blog-pipeline.md`. |
| `python3 v1/scripts/run_voiceover_week.py` | Voiceover-first lane: audio-only VO → B-roll montage long-form + auto portrait shorts, captions burned by hyperframes. Doc: `docs/voiceover-runner.md`. |
| `python3 v1/scripts/scheduler.py` | Auto-publish daemon (APScheduler): fires `posts` rows in `data/scheduling.db` where `status='pending'` and due; syncs tracker. |

Manual steps that remain: record video, ~10-min content approval, thumbnail Canva pass, push/deploy worksheet links, replying to comments/DMs. Human to-dos land in `content/derivatives/{week}/{slug}/manual_steps.md`.

## Claude usage rules

- **All pipeline Claude calls = `claude -p` CLI subprocess on subscription OAuth (no API key).** Python callers use `v1/scripts/lib/claude_cli.py` (disk cache at `.cache/claude/`); new shell callers use `v1/scripts/headless_claude.sh`. The raw `anthropic` SDK with `ANTHROPIC_API_KEY_FREE` is used ONLY by the analytics/scoring scripts (`idea_scorer.py`, `generate_viral_reel_brief.py`).
- **Model routing:** single source of truth `v1/scripts/lib/niche_config.py:MODEL_BY_TASK`, resolved via `model_for(task)`. Never hardcode model IDs in call sites; add a task key instead.
- **Model tiers (2026-07):** Fable 5 (`claude-fable-5`) ONLY for `hero_blog` — quality-critical, weekly, low-volume; it burns Max 5x limits fast and single turns can run minutes (article timeouts are 900s). Sonnet 5 (`claude-sonnet-5`) is the workhorse (beat_html, scene_plan, repurpose, buffer, html_asset, retrofit, shorts_meta, reel_hook, custom_scene) — near-Opus quality, Sonnet-tier limits; also used by `idea_scorer.py` on the API-key path (judgment-heavy, tiny volume). Opus 4.8 for storyboard/reel_script. Haiku ONLY for mechanical classification (metadata task, video_trim segments, fetch_videos relevance, publish_medium) — never for user-facing copy, code generation, or judgment calls. If output quality dips after a model upgrade, loosen over-prescriptive prompt scaffolding before reverting the model.
- **Concurrency budget:** max 3 parallel `claude -p` sessions (Max 5x limit convention — see `generate_buffer.py`). Render fan-out (no Claude) may go higher.
- **Per-stage timeout budget:** beat HTML ≤ 300s, scene plan 360s / short-batch 600s, small text calls 60–120s. Times out twice at budget → prompt too big, split it; don't raise the timeout.
- **Retry with backoff ONLY on transient failures** (timeout/429/529/overloaded), max 2 retries (5s, 15s). **On 401 / `INVALID_ACCESS_TOKEN`, STOP immediately** — strip `ANTHROPIC_API_KEY*`, `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN`, `ANTHROPIC_BASE_URL` from the subprocess env so the CLI uses subscription OAuth (see `hf_beat_builder._call_claude`).
- **Version prompts, don't copy-paste them** — big generation prompts live in code (`hf_beat_builder._compose_prompt`, `hyperframes_render.py`, `generate_scene_plans.build_prompt`) and KB files (`v1/data/kb/design/*.md`). Edit the source.

## Content Rules

- **TRACKER FIRST:** check `output/trackers/annual-tracker-2026.xlsx` (one sheet per month; columns incl. ISO Week, Slug, Posting Date, Niche, Content Title, Status) before writing — no repeat angles within 90 days per niche. After publishing, set Status='Published' for the slug's rows.
- **KB FIRST:** read `data/kb/master_brief.md` before content decisions.
- **VIRALITY ENGINE (automatic):** `v1/scripts/lib/virality.py` injects hook+CTA+guardrail into every generator, routed by niche: poetry/life → `data/kb/voice/`, DS/`--project` → `data/kb/reels/`. Caption/thumbnail formulas: `data/kb/reels/06_mavgpt_caption_formula.md`, `data/kb/voice/{life,poetry}_formula.md`. Edit KB markdown to change behavior.
- **REEL FORMULA:** short-form follows `data/kb/viral_reel_formula.md` (5-beat structure) + hook taxonomy `data/kb/twitter_hook_patterns.json`. Never skip hook re-record/regenerate.
- **PROJECTS REGISTRY:** build-in-public projects in `data/kb/projects.json` (`autopilot`, `free_tool_ds` DM `FLOW`, `free_tool_life` DM `SYSTEM`). `idea_scorer.py:weekly_project_reel()` auto-adds one tool reel per niche to `data/ideas/weekly_ideas.md`. Use `--project <key>` on generators.
- **HONESTY GUARDRAIL:** never overclaim what a tool does.
- **RAW TAKE (Life, 4×/week):** Hinglish raw-opinion Shorts; questions in `data/kb/raw_take_questions.json`; auto-surfaced by `idea_scorer.py:weekly_raw_take_batch`. Spec: `docs/raw-take-format.md`. Additive lane, replaces nothing.
- **WORKSHEETS:** auto-generated end-to-end (`generate_worksheet_html.py`, "Breath Network" shell, headless-Chrome PDF). DS/Life only; CTAs injected via `inject_worksheet_ctas.py`. Push/deploy for gated link stays manual.
- **IMAGES:** `lib/image_decision.py` weighs AI vs stock per blog; override `--image {auto,stock,ai}`.
- **STAR ATTRIBUTION:** UTM-tag repo links via `lib/utm.py`; `collect_analytics.py` tracks star deltas.

## Distribution

One piece → per-platform derivatives → staged by `load_posts.py` into `data/scheduling.db` → fired by `scheduler.py`. **LinkedIn ACTIVE. Instagram/Threads via Meta Graph API; Facebook mirrors IG. Twitter DROPPED. Reels → IG Reels + YT Shorts only.** Meta tokens: `docs/one-time-platform-setup.md`. Canonical model: `docs/pipeline-2026.md`.

## Platform Constraints

- LinkedIn: poll options ≤30 chars; blog/repo link in pinned first comment, never post body.
- Instagram Graph API: Reels/single image/carousel only; needs a public media URL (host asset first); Stories not API-publishable.
- Worksheet delivery = owned-audience email capture (Substack retired), DS & Life only.

## Folder Map (verified)

```
v1/
  scripts/          # ALL active code: orchestrators, generators
    lib/            # claude_cli.py, niche_config.py, virality.py, schedule_calc.py, content_paths.py, ...
  data/kb/design/   # beat look bibles per niche
  graphify-out/     # knowledge graph — GRAPH_REPORT.md lives HERE (not repo root)
  docs/             # v2-pipeline.md
assets/             # media by type, ISO-week (2026-Wnn/) subfolders: raw/ broll/ hyperframes/ video/ slides/ social_posts/ ...
content/            # blogs/ derivatives/ reels/ buffer/ archive/ — ISO-week grouped; derivatives hold schedule.json + manual_steps.md
data/               # kb/ ideas/ analytics/ scheduling.db
output/             # trackers/ worksheets/ scheduled/ animations/ visuals/ — ISO-week grouped
prompts/            # reusable prompt templates (repurposing_agent.md)
docs/               # operating guides (blog-pipeline.md, pipeline-2026.md, day guides)
remotion/public/    # broll/ videos/ captions/ edit-plans/ by week
```

Does NOT exist (common ENOENT sources): root `graphify-out/`, root `scripts/` code, `v1/agents/`, `reference/lessons/`.

ISO-week convention: `YYYY-Wnn/` subfolders everywhere; `v1/scripts/lib/schedule_calc.py:get_iso_week()` + `lib/content_paths.py` for path construction.

## Operational Rules

- **UPDATE GUIDES ALWAYS:** any change to scripts/pipeline/workflow → update the matching doc in `docs/` (or `v1/docs/`) before finishing.
- **Development protocol:** use Read/Edit/Write tools (not cat/grep/sed for file edits); targeted edits, never full-file dumps; ambiguous request → ask one specific question; large tasks → plan, halt for approval, then execute.

## graphify

Knowledge graph at `v1/graphify-out/`. ALWAYS read `v1/graphify-out/GRAPH_REPORT.md` before grep/glob exploration or codebase questions. Prefer `graphify query|path|explain` for cross-module questions. After modifying code: `graphify update .` from `v1/`.

## macOS notes

- No `tac` (use `tail -r`); no GNU `timeout` (bash watchdog — see `headless_claude.sh` — or `gtimeout`).
- ffmpeg/ffprobe at `/opt/homebrew/bin/` (hardcoded in `run_video_pipeline.py`); SessionStart env-doctor hook reports if missing.

## Spaced path rule

Repo path contains spaces (`.../Making It Big/Claude/content-machine`). **Always quote the full absolute path; NEVER `cd` inside compound commands** — run tools with absolute quoted paths.

## Environment

`.env` holds `ANTHROPIC_API_KEY_FREE` (analytics scripts only) and `GOOGLE_CONSOLE_API_KEY`. Pipeline Claude calls need NO key (subscription OAuth). Optional: `GITHUB_REPOS`/`GITHUB_TOKEN` for star tracking.

`.mcp.json` contains NO literal secrets — it references `${SUBSTACK_*}` and `${TWITTER_MCP_*}` env vars whose values live in `.env` (gitignored). For the Substack/Twitter MCP servers to authenticate, those vars must be in the environment when Claude Code launches: `set -a; source .env; set +a` in the shell first (or export them in your shell profile). Never paste secret values back into `.mcp.json`; it is gitignored — keep it that way.
