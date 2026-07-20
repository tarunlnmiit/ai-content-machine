# CLAUDE.md

Guidance Claude Code this repo.

## What this project is

Content creation + publishing system: ideation → production (video/blog) → repurposing → scheduled auto-publish. **All active code lives `v1/` — root-level dirs legacy/content storage.** No root `scripts/` implementation; orchestrators, generators, libs in `v1/scripts/`.

## Creator Profile

**CREATOR:** Tarun Gupta — 10-year data scientist + content creator
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

## Pipeline entry points (all `v1/scripts/`)

| Command | What it do |
|---|---|
| `python3 v1/scripts/run_video_pipeline.py --raw <file> --manifest <m.json>` | V2 video: trim → storyboard → HyperFrames per-beat compositions → FFmpeg composite → MP4. Phase markers `.phase_N_done`; `--restart-from N`. Reels: run `v1/scripts/prepare_reel_script.py` first. Doc: `v1/docs/v2-pipeline.md`. Beat look bibles: `v1/data/kb/design/{ds,life,poetry}_design.md` (`## SHORT-FORM OVERRIDES` reels). |
| `python3 v1/scripts/run_blog_pipeline.py --input <blog.md>` (or `--topic ... --niche <ds\|life\|poetry>`) | ALL non-video derivatives one idempotent run: posts, social images+carousel, deck, IG reel brief, thumbnail, worksheet (DS/Life), then stages via `load_posts`. `--force`, `--no-stage`, `--skip-thumbnail`. Doc: `docs/blog-pipeline.md`. |
| `python3 v1/scripts/dashboard.py` → http://localhost:8765 | **Operator dashboard** — run/monitor whole weekly loop one page: prep buttons (analytics→ideas→pack→menu), menu checkboxes (writes weekly_menu.md), inbox slicing, per-clip composite/trim, episode assembly, review + approvals.json. Localhost-only; NO publish endpoints (guardrail). |
| **RAW-SESSION LANE (primary video lane, 2026-07):** `generate_prompt_pack.py` → record greenscreen → `slice_raw_session.py --input <raw> --week <W>` → `composite_greenscreen.py --input <clip> --niche <n>` → `video_trim.py` → reels (phases 3–6) + `assemble_episode.py --week <W> --niche <n>` | Unscripted Q&A: spoken question = slice marker + hook. ALL ENGLISH. Episodes route per niche channel. Doc: `v1/docs/guides/raw-session-lane.md`. Runbooks Opus/Sonnet/Haiku: `v1/docs/runbooks/`. |
| `python3 v1/scripts/run_voiceover_week.py` | Voiceover-first lane (PAUSED 2026-07 — see pipeline-2026.md v2 addendum): audio-only VO → B-roll montage long-form + auto portrait shorts. Doc: `docs/voiceover-runner.md`. |
| `python3 v1/scripts/build_vault.py` | **Run after adding content.** Rebuilds Obsidian vault at `vault/`: adds YAML frontmatter new `.md` files, refreshes `Home.md` + `Index/*.md`. Idempotent; never overwrites existing frontmatter keys or touches bodies. `--dry-run`, `--check` (exit 1 if any file lacks frontmatter), `--force-rewrite` (recompute derived keys), `--vault-only`, `--self-check`. Doc: `docs/guides/obsidian-vault.md`. |

Manual steps remain: record video, ~10-min content approval, thumbnail Canva pass, push/deploy worksheet links, replying comments/DMs. Human to-dos land `content/derivatives/{week}/{slug}/manual_steps.md`.

## Video editing / recut / hyperframes

- **Before ANY video trim, clap/silence/retake removal, overlay/recut, or hyperframes render job, invoke `video-edit-playbook` skill** (`.claude/skills/video-edit-playbook/SKILL.md`) — session-validated thresholds (clap attack-ratio detection, silence trims), machine env traps (broken `hyperframes transcribe`, silent renders needing audio mux, snapshot dir wipe), hard verification gates. Non-negotiable non-Fable models.

## Claude usage rules

- **All pipeline Claude calls = `claude -p` CLI subprocess on subscription OAuth (no API key).** Python callers use `v1/scripts/lib/claude_cli.py` (disk cache `.cache/claude/`); new shell callers use `v1/scripts/headless_claude.sh`. Raw `anthropic` SDK w/ `ANTHROPIC_API_KEY_FREE` used ONLY analytics/scoring scripts (`idea_scorer.py`, `generate_viral_reel_brief.py`).
- **Model routing:** single source truth `v1/scripts/lib/niche_config.py:MODEL_BY_TASK`, resolved via `model_for(task)`. Never hardcode model IDs call sites; add task key instead.
- **Model tiers (2026-07):** Fable 5 (`claude-fable-5`) ONLY `hero_blog` — quality-critical, weekly, low-volume; burns Max 5x limits fast, single turns run minutes (article timeouts 900s). Sonnet 5 (`claude-sonnet-5`) workhorse (beat_html, scene_plan, repurpose, buffer, html_asset, retrofit, shorts_meta, reel_hook, custom_scene) — near-Opus quality, Sonnet-tier limits; also used `idea_scorer.py` API-key path (judgment-heavy, tiny volume). Opus 4.8 storyboard/reel_script. Haiku ONLY mechanical classification (metadata task, video_trim segments, fetch_videos relevance, publish_medium) — never user-facing copy, code gen, judgment calls. Output quality dips after model upgrade → loosen over-prescriptive prompt scaffolding before reverting model.
- **Concurrency budget:** max 3 parallel `claude -p` sessions (Max 5x limit convention — see `generate_buffer.py`). Render fan-out (no Claude) may go higher.
- **Per-stage timeout budget:** beat HTML ≤ 300s, scene plan 360s / short-batch 600s, small text calls 60–120s. Times out twice at budget → prompt too big, split it; don't raise timeout.
- **Retry backoff ONLY transient failures** (timeout/429/529/overloaded), max 2 retries (5s, 15s). **On 401 / `INVALID_ACCESS_TOKEN`, STOP immediately** — strip `ANTHROPIC_API_KEY*`, `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN`, `ANTHROPIC_BASE_URL` subprocess env so CLI uses subscription OAuth (see `hf_beat_builder._call_claude`).
- **Version prompts, don't copy-paste** — big generation prompts live code (`hf_beat_builder._compose_prompt`, `hyperframes_render.py`, `generate_scene_plans.build_prompt`) + KB files (`v1/data/kb/design/*.md`). Edit source.

## Content Rules

- **TRACKER FIRST:** check `output/trackers/annual-tracker-2026.xlsx` (one sheet/month; columns incl. ISO Week, Slug, Posting Date, Niche, Content Title, Status) before writing — no repeat angles within 90 days/niche. After publishing, set Status='Published' slug's rows.
- **KB FIRST:** read `data/kb/master_brief.md` before content decisions.
- **VIRALITY ENGINE (automatic):** `v1/scripts/lib/virality.py` injects hook+CTA+guardrail every generator, routed niche: poetry/life → `data/kb/voice/`, DS/`--project` → `data/kb/reels/`. Caption/thumbnail formulas: `data/kb/reels/06_mavgpt_caption_formula.md`, `data/kb/voice/{life,poetry}_formula.md`. Edit KB markdown change behavior.
- **REEL FORMULA:** short-form follows `data/kb/viral_reel_formula.md` (5-beat structure) + hook taxonomy `data/kb/twitter_hook_patterns.json`. Never skip hook re-record/regenerate.
- **PROJECTS REGISTRY:** build-in-public projects `data/kb/projects.json` (`autopilot`, `free_tool_ds` DM `FLOW`, `free_tool_life` DM `SYSTEM`). `idea_scorer.py:weekly_project_reel()` auto-adds one tool reel/niche to `data/ideas/weekly_ideas.md`. Use `--project <key>` on generators.
- **HONESTY GUARDRAIL:** never overclaim what tool does.
- **RAW TAKE (Life, 4×/week):** Hinglish raw-opinion Shorts; questions `data/kb/raw_take_questions.json`; auto-surfaced `idea_scorer.py:weekly_raw_take_batch`. Spec: `docs/raw-take-format.md`. Additive lane, replaces nothing.
- **WORKSHEETS:** auto-generated end-to-end (`generate_worksheet_html.py`, "Breath Network" shell, headless-Chrome PDF). DS/Life only; CTAs injected via `inject_worksheet_ctas.py`. Push/deploy gated link stays manual.
- **IMAGES:** `lib/image_decision.py` weighs AI vs stock per blog; override `--image {auto,stock,ai}`.
- **STAR ATTRIBUTION:** UTM-tag repo links via `lib/utm.py`; `collect_analytics.py` tracks star deltas.

## Distribution

One piece → per-platform derivatives → staged by `load_posts.py` into `data/scheduling.db` → fired by `scheduler.py`. **LinkedIn ACTIVE. Instagram/Threads via Meta Graph API; Facebook mirrors IG. Twitter DROPPED. Reels → IG Reels + YT Shorts only.** Meta tokens: `docs/one-time-platform-setup.md`. Canonical model: `docs/pipeline-2026.md`.

## Platform Constraints

- LinkedIn: poll options ≤30 chars; blog/repo link pinned first comment, never post body.
- Instagram Graph API: Reels/single image/carousel only; needs public media URL (host asset first); Stories not API-publishable.
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

`vault/` sits repo root (sibling `v1/`) — Obsidian vault, four relative symlinks into real dirs (`Content`→`v1/content`, `KB`→`v1/data/kb`, `Docs`→`v1/docs`, `Prompts`→`v1/prompts`) plus generated `Home.md` + `Index/`. Not copy: edits there hit real files. Out of scope every generator (all root-glob at `v1/`).

Does NOT exist (common ENOENT sources): root `graphify-out/`, root `scripts/` code, `v1/agents/`, `reference/lessons/`.

ISO-week convention: `YYYY-Wnn/` subfolders everywhere; `v1/scripts/lib/schedule_calc.py:get_iso_week()` + `lib/content_paths.py` path construction.

## Operational Rules

- **UPDATE GUIDES ALWAYS:** any change scripts/pipeline/workflow → update matching doc `docs/` (or `v1/docs/`) before finishing.
- **Development protocol:** use Read/Edit/Write tools (not cat/grep/sed file edits); targeted edits, never full-file dumps; ambiguous request → ask one specific question; large tasks → plan, halt approval, then execute.

## graphify

Knowledge graph at `v1/graphify-out/`. ALWAYS read `v1/graphify-out/GRAPH_REPORT.md` before grep/glob exploration or codebase questions. Prefer `graphify query|path|explain` cross-module questions. After modifying code: `graphify update .` from `v1/`.

## macOS notes

- No `tac` (use `tail -r`); no GNU `timeout` (bash watchdog — see `headless_claude.sh` — or `gtimeout`).
- ffmpeg/ffprobe at `/opt/homebrew/bin/` (hardcoded `run_video_pipeline.py`); SessionStart env-doctor hook reports if missing.

## Spaced path rule

Repo path contains spaces (`.../Making It Big/Claude/content-machine`). **Always quote full absolute path; NEVER `cd` inside compound commands** — run tools absolute quoted paths.

## Environment

`.env` holds `ANTHROPIC_API_KEY_FREE` (analytics scripts only) + `GOOGLE_CONSOLE_API_KEY`. Pipeline Claude calls need NO key (subscription OAuth). Optional: `GITHUB_REPOS`/`GITHUB_TOKEN` star tracking.

`.mcp.json` contains NO literal secrets — references `${SUBSTACK_*}` and `${TWITTER_MCP_*}` env vars whose values live `.env` (gitignored). For Substack/Twitter MCP servers authenticate, those vars must be in environment when Claude Code launches: `set -a; source .env; set +a` shell first (or export shell profile). Never paste secret values back into `.mcp.json`; it's gitignored — keep it that way.