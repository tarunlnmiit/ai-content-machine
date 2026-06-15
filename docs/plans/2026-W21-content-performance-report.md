# Plan — W21 Content Performance Report (3 pieces: Medium + YT long form)

## Context

"W21" is the **content label** (folder `2026-W21`, dated 2026-05-21), but the pieces actually **published in W24** (last week). So this is NOT a historical-window backfill — the performance data is recent and live-fetchable. We just need each W21 piece's **published destination**, then pull current stats (which reflect since-W24 performance).

The earlier now-locked-collector problem is **moot** — no `collect_analytics.py` window surgery needed.

### The 3 W21 pieces (one per niche)
| Niche | Slug | YT channel | Blog |
|---|---|---|---|
| DS | `complete-python-course-2026-beginner-to-advance-tutorial-110` | Breath of Data Science | Medium |
| Life | `how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals` | Breath of Life | Medium |
| Poetry | `when-dreams-speak-of-love` | Breath of Poetry | Medium |

### Where published URLs are
Not in Notion, not on disk (derivative folders empty). **Must come from the user.**

### Scope (confirmed)
- **Blog = Medium only.**
- **YT long form = user pastes 3 URLs.**

## Inputs needed from user (blocking)

1. **3 YouTube long-form video URLs** (one per piece). I extract video IDs and self-serve all YT stats — channel IDs + `GOOGLE_CONSOLE_API_KEY` (Data API) and OAuth creds (Analytics API) are present in `.env`.
2. **Fresh Medium stats JSON** → save to `data/analytics/medium-stats-all.json`. Must be Medium's GraphQL stats array (same shape the existing file uses: `node.{title, totalStats.views/reads, earnings.total, firstPublishedAt, collection, mediumUrl}`), covering the W24-published posts. The current file is from March 2026 — stale, lacks these posts.
   - Medium has **no per-post stats API**. Without this export I can only scrape public claps/responses, not views/reads/earnings.

## Approach

Add a small, reusable script `scripts/report_content_performance.py` (reuses YT helpers from `collect_analytics.py:fetch_youtube_channel_stats` / `fetch_youtube_recent_videos` and the Analytics-API query pattern from `fetch_youtube_analytics.py`) that:

1. Takes the 3 YouTube video IDs (CLI args or a small inline map) + the slug→Medium-URL map.
2. **YouTube** per video: Data API (views, likes, comments) + Analytics API since publish date (watch time, avg view duration, % retention, top traffic sources).
3. **Medium** per piece: match the post in `medium-stats-all.json` by `mediumUrl` → views, reads, read-ratio, earnings, published date (reuse `convert_medium_analytics.py:parse_directly`).
4. Emit `data/analytics/weekly_insights_2026-W21.md` — a per-piece table (niche · YT views/watch-time/retention · Medium views/reads/read-ratio/earnings), without clobbering the live `weekly_insights.md` (W23).

If a single throwaway report is preferred over a committed script, I can assemble the same markdown ad-hoc from API calls + the Medium JSON — say the word.

## Representative files
- `scripts/report_content_performance.py` (new)
- Reuse: `scripts/collect_analytics.py` (YT Data-API helpers), `scripts/fetch_youtube_analytics.py` (Analytics-API date-range query), `scripts/convert_medium_analytics.py:parse_directly` (Medium JSON → rows).

## Verification
- `data/analytics/weekly_insights_2026-W21.md` exists; live `weekly_insights.md` (W23) untouched.
- Each of the 3 pieces shows non-null YT stats matching the pasted video IDs (spot-check one video's view count against the YT page).
- Medium rows match by URL; published dates fall in W24 (confirms we pulled the right, fresh posts).

## Limitations
- **Medium** depends entirely on the user providing a fresh stats JSON; otherwise blog metrics are claps-only.
- YouTube channel-level cumulative stats are point-in-time NOW; per-video "since publish" metrics are the meaningful ones here (publish ≈ W24, so they already capture the full live window).

## Docs to update (per CLAUDE.md "UPDATE GUIDES ALWAYS")
- `docs/sunday.md` — note the per-asset report path for content published in a later week than its label.
