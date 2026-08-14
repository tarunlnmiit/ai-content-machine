# CLAUDE.md

Guidance for Claude Code in this repo.

## What this project is

Content creation + publishing system: ideation → production (video/blog) → repurposing → scheduled auto-publish. **All active code lives in `v1/` — root-level dirs are legacy/content storage.** There is no root `scripts/` implementation; orchestrators, generators, and libs are in `v1/scripts/`.

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

## Pipeline entry points (all in `v1/scripts/`)

| Command | What it does |
|---|---|
| `python3 v1/scripts/run_video_pipeline.py --raw <file> --manifest <m.json>` | V2 video: trim → storyboard → HyperFrames per-beat compositions → FFmpeg composite → MP4. Phase markers `.phase_N_done`; resume with `--restart-from N`. For reels, run `v1/scripts/prepare_reel_script.py` first. Doc: `v1/docs/guides/v2-pipeline.md`. Beat look bibles: `v1/data/kb/design/{ds,life,poetry}_design.md` (`## SHORT-FORM OVERRIDES` section for reels). |
| `python3 v1/scripts/run_blog_pipeline.py --input <blog.md>` (or `--topic ... --niche <ds\|life\|poetry>`) | ALL non-video derivatives in one idempotent run: posts, social images + carousel, deck, IG reel brief, thumbnail, worksheet (DS/Life), then stages via `load_posts`. Flags: `--force`, `--no-stage`, `--skip-thumbnail`. Doc: `v1/docs/guides/blog-pipeline.md`. |
| `python3 v1/scripts/dashboard.py` → http://localhost:8765 | **Operator dashboard** — run/monitor the whole weekly loop from one page: prep buttons (analytics→ideas→pack→menu), menu checkboxes (writes weekly_menu.md), inbox slicing, per-clip composite/trim, episode assembly, review + approvals.json. Localhost-only; NO publish endpoints (guardrail). |
| **RAW-SESSION LANE (primary video lane, 2026-07):** `generate_prompt_pack.py` → record greenscreen → `slice_raw_session.py --input <raw> --week <W>` → `composite_greenscreen.py --input <clip> --niche <n>` → `video_trim.py` → reels (phases 3–6) + `assemble_episode.py --week <W> --niche <n>` | Unscripted Q&A: the spoken question is the slice marker + hook. ALL ENGLISH. Episodes route to per-niche channels. Doc: `v1/docs/guides/raw-session-lane.md`. Runbooks for Opus/Sonnet/Haiku: `v1/docs/runbooks/`. |
| `python3 v1/scripts/run_voiceover_week.py` | Voiceover-first lane (PAUSED 2026-07 — see pipeline-2026.md v2 addendum): audio-only VO → B-roll montage long-form + auto portrait shorts. Doc: `v1/docs/guides/voiceover-runner.md`. |
| `python3 v1/scripts/build_vault.py` | **Run after adding content.** Rebuilds Obsidian vault at `vault/`: adds YAML frontmatter to new `.md` files, refreshes `Home.md` + `Index/*.md`. Idempotent; never overwrites existing frontmatter keys or touches bodies. Flags: `--dry-run`, `--check` (exit 1 if any file lacks frontmatter), `--force-rewrite` (recompute derived keys), `--vault-only`, `--self-check`. Doc: `v1/docs/guides/obsidian-vault.md`. |
| `python3 v1/scripts/reconcile_blog_social.py [--niche ds\|life\|poetry] [--next] [--gaps] [--apply]` | Reconciles Medium articles (upstream) against derived IG carousels/reels (downstream); flags proposed matches and gaps. `/reconcile-blog-social --refresh` scrapes fresh 2026 IG posts via Chrome first; `--apply` writes tracker updates (then rerun `generate_tracker_html.py`) — omit it for a dry-run report only. |

Manual steps remain: recording video, ~10-min content approval, thumbnail Canva pass, pushing/deploying worksheet links, replying to comments/DMs. Human to-dos land in `v1/content/derivatives/{week}/{slug}/manual_steps.md`.

## Video editing / recut / hyperframes

- **Before ANY video trim, clap/silence/retake removal, overlay/recut, or hyperframes render job, invoke the `video-edit-playbook` skill** (`.claude/skills/video-edit-playbook/SKILL.md`) — session-validated thresholds (clap attack-ratio detection, silence trims), machine env traps (broken `hyperframes transcribe`, silent renders needing audio mux, snapshot dir wipe), hard verification gates. Non-negotiable for non-Fable models.

## Brag videos (/brag skill)

- **Output location override for this repo:** the `/brag` plugin skill defaults to writing `brag-output/` (or a timestamped variant) at the current working directory. In this repo, after Step 4 renders `brag.mp4`/`brag.jpg`/`brag-plan.md`/`share-copy.txt`, move those four files into `v1/assets/brag_videos/<ISO-week>/<blog-slug>_brag.{mp4,jpg}`, `<blog-slug>_brag-plan.md`, `<blog-slug>_share-copy.txt` (ISO week = the week folder the source blog lives under in `v1/content/blogs/`) and delete the leftover `brag-output*/` scratch directory (its `composition/` build source is not kept). If multiple takes are produced for the same blog, the canonical pick keeps the bare `_brag.*` name; other takes get `_brag-alt-<tag>.*`.

**Quality rules (2026 research-validated, IG-focused):**
- Seamless loop: punchline's final frame must visually match the hook's opening frame (same layout/palette/position) — farms the rewatch signal.
- Hook: pattern-interrupt or bold-claim, 5-8 words max, kinetic text entrance on screen within 1.5s. Never a calm static title-card open.
- Music: first beat lands within 2-3s — no fade-in intros; beat-sync cues from the skill's cue metadata.
- Duration: default 15-18s; up to 25s only when the punchline genuinely needs it.
- CTA: punchline card or share-copy includes a "send this to a friend" or comment-a-keyword CTA (DM-sends are the top share signal).
- Cover: `brag.jpg` poster frame keeps all critical text/graphics inside the central 1080x1080 safe zone (IG grid crops 3:4).
- Kinetic text everywhere: no static-holding text cards; every key text element animates in/out — applies to ALL tone presets, including polished/default.
- Grounding artifact: every video includes at least one REAL artifact — blog-essay subjects get a screenshot of the published page/headline; tools get a real UI frame — never 100% abstract graphics.
- Essay-subject adaptation: when the subject is a blog essay (not an app), skip the skill's user-flow lane; build from pull-quote cards + the published-headline proof card + the grounding screenshot.

## Carousels (/carousel skill)

- Interactive IG carousel designer at `.claude/skills/carousel/SKILL.md` — walks hook choice (3 candidates, different playbook drivers) → outline approval → `generate_carousel.py --outline` → export → tracker update. Use it instead of calling `generate_carousel.py` blind.

## Claude usage rules

- **All pipeline Claude calls = `claude -p` CLI subprocess on subscription OAuth (no API key).** Python callers use `v1/scripts/lib/claude_cli.py` (disk cache `.cache/claude/`); new shell callers use `v1/scripts/headless_claude.sh`. The API-key path is retired (2026-07): `idea_scorer.py` now goes through `claude_cli.call_claude`. Only `generate_viral_reel_brief.py` still imports the raw `anthropic` SDK with `ANTHROPIC_API_KEY_FREE` — that key is no longer in `.env`, so the script is currently non-functional.
- **Model routing:** single source of truth is `v1/scripts/lib/niche_config.py:MODEL_BY_TASK`, resolved via `model_for(task)`. Never hardcode model IDs at call sites; add a task key instead.
- **Model tiers (2026-07):** Fable 5 (`claude-fable-5`) ONLY for `hero_blog` — quality-critical, weekly, low-volume; burns Max 5x limits fast, single turns run minutes (article timeouts 900s). Sonnet 5 (`claude-sonnet-5`) is the workhorse (beat_html, scene_plan, repurpose, buffer, html_asset, retrofit, shorts_meta, reel_hook, custom_scene) — near-Opus quality at Sonnet-tier limits. Opus 4.8 for storyboard/reel_script. Haiku ONLY for mechanical classification (`metadata` is the only Haiku task key in MODEL_BY_TASK) — never user-facing copy, code gen, or judgment calls. If output quality dips after a model upgrade, loosen over-prescriptive prompt scaffolding before reverting the model.
- **Concurrency budget:** max 3 parallel `claude -p` sessions (Max 5x limit convention — see `generate_buffer.py`). Render fan-out (no Claude) may go higher.
- **Per-stage timeout budget:** beat HTML ≤ 300s, scene plan 360s / short-batch 600s, small text calls 60–120s. If a stage times out twice at budget, the prompt is too big — split it; don't raise the timeout.
- **Retry backoff ONLY on transient failures** (timeout/429/529/overloaded), max 2 retries (5s, 15s). **On 401 / `INVALID_ACCESS_TOKEN`, STOP immediately** — strip `ANTHROPIC_API_KEY*`, `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN`, `ANTHROPIC_BASE_URL` from the subprocess env so the CLI uses subscription OAuth (see `hf_beat_builder._call_claude`).
- **Version prompts, don't copy-paste** — big generation prompts live in code (`hf_beat_builder.py`, `hyperframes_render.py`, `generate_scene_plans.build_prompt`) + KB files (`v1/data/kb/design/*.md`). Edit the source.

## Content Rules

- **TRACKER FIRST:** check `v1/docs/content-tracker.md` (slug-keyed source of truth; `content-tracker.html` is generated — rerun `generate_tracker_html.py` after edits) before writing — no repeat angles within 90 days per niche. After publishing, set the slug's status to Published.
- **KB FIRST:** read `v1/data/kb/master_brief.md` before content decisions.
- **VIRALITY ENGINE (automatic):** `v1/scripts/lib/virality.py` injects hook+CTA+guardrail into every generator, routed by niche: poetry/life → `v1/data/kb/voice/`, DS/`--project` → `v1/data/kb/reels/`. Caption/thumbnail formulas: `v1/data/kb/reels/06_mavgpt_caption_formula.md`, `v1/data/kb/voice/{life,poetry}_formula.md`. Edit the KB markdown to change behavior.
- **REEL FORMULA:** short-form follows `v1/data/kb/viral_reel_formula.md` (5-beat structure) + hook taxonomy `v1/data/kb/twitter_hook_patterns.json`. Never skip the hook on re-record/regenerate.
- **PROJECTS REGISTRY:** build-in-public projects live in `v1/data/kb/projects.json` (`autopilot`, `free_tool_ds` DM `FLOW`, `free_tool_life` DM `SYSTEM`, `inbox_to_action`). `idea_scorer.py:weekly_project_reel()` auto-adds one tool reel per niche to `v1/data/ideas/weekly_ideas.md`. Use `--project <key>` on generators.
- **HONESTY GUARDRAIL:** never overclaim what a tool does.
- **RAW TAKE (Life, 4×/week):** Hinglish raw-opinion Shorts; questions in `v1/data/kb/raw_take_questions.json`; auto-surfaced by `idea_scorer.py:weekly_raw_take_batch`. Spec: `v1/docs/guides/raw-take-format.md`. Additive lane, replaces nothing.
- **WORKSHEETS:** auto-generated end-to-end (`generate_worksheet_html.py`, "Breath Network" shell, headless-Chrome PDF). DS/Life only; CTAs injected via `inject_worksheet_ctas.py`. Push/deploy of the gated link stays manual.
- **IMAGES:** `lib/image_decision.py` weighs AI vs stock per blog; override with `--image {auto,stock,ai}`.
- **STAR ATTRIBUTION:** UTM-tag repo links via `lib/utm.py`; `collect_analytics.py` tracks star deltas.

## Distribution

One piece → per-platform derivatives → staged by `load_posts.py` into `v1/data/scheduling.db` → fired by `scheduler.py`. **LinkedIn ACTIVE. Instagram/Threads via Meta Graph API; Facebook mirrors IG. Twitter DROPPED. Reels → IG Reels + YT Shorts only.** Meta tokens: `v1/docs/setup/one-time-platform-setup.md`. Canonical model: `v1/docs/guides/pipeline-2026.md`.

## Platform Constraints

- LinkedIn: poll options ≤30 chars; blog/repo link goes in a pinned first comment, never the post body.
- Instagram Graph API: Reels/single image/carousel only; needs a public media URL (host the asset first); Stories are not API-publishable.
- Worksheet delivery = owned-audience email capture (Substack retired), DS & Life only.

## Folder Map (verified)

```
v1/                 # EVERYTHING active lives here
  scripts/          # ALL active code: orchestrators, generators
    lib/            # claude_cli.py, niche_config.py, virality.py, schedule_calc.py, content_paths.py, ...
  data/             # kb/ (incl. kb/design/ beat look bibles) ideas/ analytics/ scheduling.db
  graphify-out/     # knowledge graph — GRAPH_REPORT.md lives HERE (not repo root)
  docs/             # guides/ (blog-pipeline, pipeline-2026, v2-pipeline, ...) setup/ runbooks/ archive/ content-tracker.md
  assets/           # media by type, ISO-week (2026-Wnn/) subfolders: raw/ broll/ hyperframes/ video/ slides/ social_posts/ ...
  content/          # blogs/ derivatives/ reels/ buffer/ archive/ — ISO-week grouped; derivatives hold schedule.json + manual_steps.md
  output/           # worksheets/ published/ review/ animations/ — ISO-week grouped
  prompts/          # reusable prompt templates (repurposing_agent.md)
  remotion/public/  # broll/ videos/ captions/ edit-plans/ by week
data/               # ROOT, legacy: analytics/ only
output/             # ROOT, legacy: published/ only
videos/, experiments/  # ROOT, legacy media/scratch
```

`vault/` sits at repo root (sibling of `v1/`) — Obsidian vault with four relative symlinks into real dirs (`Content`→`v1/content`, `KB`→`v1/data/kb`, `Docs`→`v1/docs`, `Prompts`→`v1/prompts`) plus generated `Home.md` + `Index/`. Not a copy: edits there hit the real files. Out of scope for every generator (all root-glob at `v1/`).

Does NOT exist (common ENOENT sources): root `graphify-out/`, root `scripts/` code, `v1/agents/`, `reference/lessons/`.

ISO-week convention: `YYYY-Wnn/` subfolders everywhere; `v1/scripts/lib/schedule_calc.py:get_iso_week()` + `lib/content_paths.py` handle path construction.

## Operational Rules

- **UPDATE GUIDES ALWAYS:** any change to scripts/pipeline/workflow → update the matching doc in `v1/docs/` before finishing.
- **Development protocol:** use Read/Edit/Write tools (not cat/grep/sed file edits); targeted edits, never full-file dumps; ambiguous request → ask one specific question; large tasks → plan, halt for approval, then execute.

## graphify

Knowledge graph at `v1/graphify-out/`. ALWAYS read `v1/graphify-out/GRAPH_REPORT.md` before grep/glob exploration or codebase questions. Prefer `graphify query|path|explain` for cross-module questions. After modifying code: `graphify update .` from `v1/`.

## macOS notes

- No `tac` (use `tail -r`); no GNU `timeout` (bash watchdog — see `headless_claude.sh` — or `gtimeout`).
- ffmpeg/ffprobe at `/opt/homebrew/bin/` (hardcoded in `run_video_pipeline.py`); SessionStart env-doctor hook reports if missing.

## Spaced path rule

Repo path contains spaces (`.../Making It Big/Claude/content-machine`). **Always quote the full absolute path; NEVER `cd` inside compound commands** — run tools with absolute quoted paths.

## Environment

`.env` holds `GOOGLE_CONSOLE_API_KEY` + the `SUBSTACK_*`/`TWITTER_MCP_*` MCP creds. `ANTHROPIC_API_KEY_FREE` retired 2026-07 (removed from `.env`); ALL Claude calls use subscription OAuth — no Anthropic key anywhere.

`.mcp.json` contains NO literal secrets — it references `${SUBSTACK_*}` and `${TWITTER_MCP_*}` env vars whose values live in `.env` (gitignored). For the Substack/Twitter MCP servers to authenticate, those vars must be in the environment when Claude Code launches: `set -a; source .env; set +a` in the shell first (or export via shell profile). Never paste secret values back into `.mcp.json`; it's gitignored — keep it that way.
