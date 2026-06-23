# Plan: Teasers + Backlinks from Existing Published YouTube / Medium

## Context

The creator already has published long-form **YouTube videos** and **Medium blogs**. They want, for each existing piece, either:
1. **Create new content** — a short "copy of the entire thing" (a condensed teaser/summary) for social, ending with a **link back to the original** (UTM-tagged), then schedule/distribute it; **or**
2. **Tag existing content** — inject the UTM backlink into already-generated derivative posts without regenerating copy.

Confirmed choices:
- **Source list = pasted URLs** (a `urls.txt` or `--url`). No Notion dependency.
- **Text source = fetch from URL** (firecrawl scrape for Medium article body; transcript API for YouTube), with local file fallback when the piece already exists in the repo.

### Reuse facts found during exploration
- `scripts/repurpose_blog.py` already turns a blog into 10 derivative files via `prompts/repurposing_agent.md`; has `format_twitter_thread / format_linkedin / format_instagram / format_threads / format_newsletter` and JSON-retry `call_with_retry`.
- `scripts/lib/utm.py` → `build_utm_url(base_url, *, source, medium, campaign, content)` and `campaign_links(...)`. **Exists but nothing injects backlinks into post text today** — this is the core gap.
- **Distribution = manual.** The creator schedules each post by hand on the platforms. So output is **files only** — copy-paste-ready derivative `.txt`/`.json` with the backlink already in the body. No Metricool/Publer/CSV/scheduler leg.
- `lib/content_paths.derivatives_dir(date_str, slug)` for week-foldered output. `schedule_calc.write_schedule_json` optional (suggested post dates only — not required for manual posting).
- `scripts/lib/hashtags.py:build_hashtags`, `scripts/lib/virality.py:virality_block`, `scripts/lib/slug.py:slugify` reused as-is.
- Local-text fallbacks: Medium → `output/published/medium_posts.json` maps `medium_url → source_file` (`content/blogs/...md`); YouTube → `content/scripts/{week}/{slug}_yt.md` when present.

---

## Feature — `teaser_from_published`

### 1. Fetch layer — new `scripts/lib/fetch_published.py`
- `classify_url(url) -> "video" | "blog"` (youtube.com/youtu.be → video; else blog).
- `fetch_youtube(url) -> {title, channel, video_id, text}` — transcript via **`youtube-transcript-api`** (new dep); title/channel via YouTube oEmbed (`https://www.youtube.com/oembed?url=...`). No API key needed for either.
- `fetch_medium(url) -> {title, subtitle, text}` — **firecrawl** scrape (`FIRECRAWL_API_KEY` already in env) returning article markdown; fallback to `requests` + readability if key absent.
- `local_fallback(url) -> Path | None` — match against `output/published/medium_posts.json` source_file and `content/scripts/**/*_yt.md`; use local text if found (skip network).
- Returns a uniform `PublishedPiece` dataclass: `{url, kind, title, niche, text, slug, date}`.
- **Niche**: from optional column in `urls.txt`, else infer from fetched text via a one-line Claude classify (reuse `model_for`), else default by YouTube channel handle.

### 2. Teaser prompt — new `prompts/teaser_agent.md`
- Compact agent: input = full text of ONE published piece; output = **short teaser** per platform that summarizes the WHOLE piece and drives a click to `[LINK]`.
- Reuse voice rules + BANNED WORDS (from CLAUDE.md) + `virality_block(content_type, niche, project_key)`.
- Output JSON subset (teaser-sized, not the full 10-derivative schema):
  ```json
  {
    "source_title": "...", "niche": "...",
    "twitter_teaser": {"hook_type": "...", "tweets": ["...", "..."], "hashtags": ["..."]},
    "linkedin_teaser": {"opening_line": "...", "body": "<=120 words", "hashtags": ["..."]},
    "instagram_teaser": {"hook_line": "...", "caption_body": "<=80 words", "hashtags": ["..."]},
    "threads_teaser": {"body": "<=300 chars", "hashtags": ["..."]},
    "newsletter_teaser": {"subject_line": "...", "body": "<=120 words ending [LINK]"}
  }
  ```
- Every platform body ends with the `[LINK]` placeholder (replaced with the UTM backlink in step 3).

### 3. Backlink injection — reuse `scripts/lib/utm.py`
- For each platform, build `build_utm_url(canonical_url, source=<platform>, medium=<post|thread|short|newsletter>, campaign=<--campaign default "evergreen-repurpose" or project utm_campaign>, content=slug)`.
- Replace `[LINK]` in each teaser body with the platform-specific UTM URL. Append URL as the closing line where the format expects it (twitter closing tweet, threads/IG/LinkedIn/newsletter tail).

### 4. Orchestrator — new `scripts/teaser_from_published.py`
**Create mode (default):**
- Args: `--urls urls.txt` | `--url URL` ; optional `--niche`, `--project`, `--campaign`, `--platforms`, `--dry-run`.
- `urls.txt` line format: `url[, niche][, project]` (niche/project optional).
- For each URL: fetch piece → call teaser agent (`call_with_retry` pattern) → inject UTM backlinks → write copy-paste-ready files into `content/derivatives/{week}/{slug}/`:
  - per-platform `.txt` (`twitter_teaser.txt`, `linkedin_teaser.txt`, `instagram_teaser.txt`, `threads_teaser.txt`, `newsletter_teaser.txt`), each with the UTM backlink in-body, and
  - a single `teasers.md` bundle (all platforms in one file) for fast manual posting.
- Optional `write_schedule_json` for **suggested** post dates only (manual posting — not required).
- No CSV / scheduler step (manual distribution).

**Tag-existing mode:** `--inject-link <derivatives_dir> --url <canonical>`
- `inject_backlink(deriv_dir, url, campaign, slug)`: for each present platform file, append a UTM backlink line (platform-correct `source`). **Idempotent** — skip if the file already contains `utm_campaign`. No copy regeneration. Satisfies "tag them in existing content."

---

## Files

**New:** `scripts/teaser_from_published.py`, `scripts/lib/fetch_published.py`, `prompts/teaser_agent.md`
**Reuse (no change):** `scripts/lib/utm.py`, `scripts/lib/content_paths.py`, `scripts/lib/hashtags.py`, `scripts/lib/virality.py`, `scripts/lib/slug.py`, `scripts/lib/niche_config.py`, `scripts/lib/claude_cli.py` (+ `schedule_calc.py` only if suggested dates wanted)
**Maybe reuse:** `repurpose_blog.py` formatters (import if shape matches; else small local formatters)
**Not used:** Metricool/Publer/CSV/`load_posts.py` — distribution is manual.

## New dependency
- `youtube-transcript-api` (PyPI) for YouTube transcripts. Firecrawl uses `FIRECRAWL_API_KEY` already present.

## Docs (CLAUDE.md mandate)
- `docs/medium-repurposing-guide.md` — add the "teaser from existing published piece + backlink" flow + both modes.
- `docs/weekly-operating-guide.md` setup — register `teaser_from_published.py`, note `youtube-transcript-api` install.
- Run `graphify update .` after code changes.

## Verification
1. **Medium fetch + teaser (dry-run):** `python3 scripts/teaser_from_published.py --url <medium_url> --niche life --dry-run` → prints fetched title + per-platform teaser, each ending with a UTM URL containing `utm_source`, `utm_campaign`, `utm_content=<slug>`.
2. **YouTube fetch:** `python3 scripts/teaser_from_published.py --url <youtube_url> --niche ds --dry-run` → transcript pulled, teaser generated.
3. **Write (files only):** real run → per-platform `.txt` + `teasers.md` appear under `content/derivatives/{week}/{slug}/`, each with the UTM backlink in-body, copy-paste ready for manual posting.
4. **Tag existing (idempotent):** `--inject-link content/derivatives/<week>/<slug> --url <canonical>` appends backlinks; re-running makes no further change.
5. **Batch:** `--urls urls.txt` with mixed YouTube + Medium lines processes all.
