---
title: "Content Machine — Docs Index"
type: doc
slug: readme
tags: [content/doc]
---
# Content Machine — Docs Index

> Start here. Pick the doc for what you're doing right now. Close everything else.

---

## Run the dashboard (operator UI)

```bash
python3 v1/scripts/dashboard.py               # → http://localhost:8765
python3 v1/scripts/dashboard.py --port 8801   # if 8765 is taken
python3 v1/scripts/dashboard.py --no-reload   # pin the running code
```

Localhost-only, no publish endpoints by design. Two pages:

| URL | What it's for |
|---|---|
| `localhost:8765/` | Weekly loop: prep buttons (analytics → ideas → pack → menu), menu checkboxes, inbox slicing, per-clip composite/trim, episode assembly, review + approvals |
| `localhost:8765/tracker` | **Content tracker** — every piece across Medium / LinkedIn / carousel / reel / longform / worksheet |

The tracker table is **editable in place**: statuses are dropdowns, links and refs are text
inputs, `+ note` appends to a record's history. Each edit writes straight to
`docs/content-tracker.md` and regenerates the view. No Claude call, no save button.

**Auto-reloads on code change.** Edit any `scripts/*.py` the server has imported and it
re-execs itself in place — same PID, same port, no manual restart. A reload waits until no
job is running, so it can never kill a composite or episode render mid-flight. `--no-reload`
turns it off. (Browser state isn't affected; just refresh if you changed the page template.)

Details → [`content-tracker.md`](content-tracker.md) · [`guides/weekly-operating-guide.md`](guides/weekly-operating-guide.md)

---

## Reading order (open these, in this order)

| # | When | File |
|---|---|---|
| 1 | **Every week — start here** | [`guides/weekly-operating-guide.md`](guides/weekly-operating-guide.md) |
| 2 | **Running the pipeline** | [`guides/pipeline-2026.md`](guides/pipeline-2026.md) |
| 3 | **Before recording** | [`guides/recording-guide.md`](guides/recording-guide.md) |
| 4 | **After recording — V2 pipeline** | [`guides/v2-pipeline.md`](guides/v2-pipeline.md) |
| 5 | **Blog → all derivatives** | [`guides/blog-pipeline.md`](guides/blog-pipeline.md) |
| 6 | **Voiceover (no face) videos** | [`guides/voiceover-runner.md`](guides/voiceover-runner.md) |
| 7 | **Raw-take / Hinglish Shorts** | [`guides/raw-take-format.md`](guides/raw-take-format.md) |
| 8 | **Saturday + Sunday batch** | [`guides/saturday.md`](guides/saturday.md) · [`guides/sunday.md`](guides/sunday.md) |

---

## guides/ — living operational docs

| File | What it covers |
|---|---|
| `weekly-operating-guide.md` | Master weekly workflow |
| `pipeline-2026.md` | Distribution model: auto-publish daemon, channels, LinkedIn rules |
| `v2-pipeline.md` | **V2 video pipeline** — HyperFrames + AI storyboard, all commands |
| `recording-guide.md` | How to record talking heads and voiceovers |
| `voiceover-runner.md` | Audio-only voiceover lane (no face) |
| `blog-pipeline.md` | `run_blog_pipeline.py` — one command for all blog derivatives |
| `raw-take-format.md` | Hinglish Shorts format + guardrails |
| `weekly-runner.md` | Week-by-week runner steps |
| `weekly-virality-framework.md` | Virality engine, hook patterns, build-in-public cadence |
| `video-production-guide.md` | Legacy DaVinci notes (pre-V2 reference only) |
| `analytics-driven-pipeline-2026.md` | Analytics collection + feedback loop |
| `medium-repurposing-guide.md` | Medium-specific repurposing rules |
| `super-profile-setup.md` | SuperProfile / CreatorFlow comment→DM setup |
| `saturday.md` | Saturday batch steps |
| `sunday.md` | Sunday prep steps |

## setup/ — read once, then forget

| File | What it covers |
|---|---|
| `one-time-platform-setup.md` | Meta tokens, LinkedIn auth, API keys |
| `launchd-build-kb.md` | macOS launchd for KB daemon |
| `launchd-daily-ideas.md` | macOS launchd for daily ideas daemon |

Launchd `.plist` files → `../config/launchd/`

## archive/ — historical only

Week-specific plans, audits, old checklists. V2 experiment reference → `archive/v2-experiment/`.

---

Identity, banned words, niches → repo-root `CLAUDE.md`.

---

## Notion Integration Flow

Notion is the **single source of truth** for content state. Scripts read ideas from it, write status back to it.

### Ideas IN (automated)

```
launchd 6am → daily_ideas.sh
  ├─ rss_scraper.py        → data/ideas/external_<date>.json
  ├─ youtube_fetch.py      → data/ideas/youtube_<date>.json
  ├─ reddit_scraper.py     → data/ideas/reddit_<date>.json
  └─ google_suggest.py     → data/ideas/suggest_<date>.json
                            ↓
                     idea_scorer.py  (dedup + score + content filter)
                            ↓
                  data/ideas/weekly_ideas.md  (top N per niche)
                            ↓
                  sync_ideas_to_notion.py
                            ↓
                  Notion Contents DB
                  Status="Idea"  Topic={Tech|Life|Poetry}
```

Run manually:
```bash
python3 scripts/sync_ideas_to_notion.py            # uses .env DB ID
python3 scripts/sync_ideas_to_notion.py --dry-run  # preview
```

### Content OUT (manual trigger, automated write-back)

```
You pick row in Notion → mark Status="Started"
        ↓
produce_blog.py / auto_edit.py / clip_shorts.py
        ↓
Outputs: content/blogs/, assets/video/edited/, output/scheduled/
        ↓
publish_medium.py / upload_youtube.py / scheduler.py
        ↓
update_notion_status.py  (closes the loop)
        ↓
Notion Contents DB row:
  Status="Published"
  URL=<published link>
  Description+="<engagement note>"
```

After any publish:
```bash
python3 scripts/update_notion_status.py \
  --title "<title substring>" \
  --status Published \
  --url https://medium.com/... \
  --note "1.2k views first day"
```

Valid Status values: `Idea | Started | Script | Editing | Ready to publish | Uploaded | Published | Archived`

---

## Required .env Variables

```
ANTHROPIC_API_KEY_FREE=sk-ant-...
GOOGLE_CONSOLE_API_KEY=...
NOTION_INTEGRATION_SECRET=ntn_...
NOTION_CONTENTS_DB_ID=<uuid of Contents DB>
```

No DB ID hardcoded in scripts — `.env` is the single source.

---

## Script Map

| Script | Reads | Writes | When |
|--------|-------|--------|------|
| `rss_scraper.py` | RSS feeds | `data/ideas/external_<date>.json` | launchd 6am |
| `idea_scorer.py` | `data/ideas/*.json` | `data/ideas/weekly_ideas.md` | daily |
| `sync_ideas_to_notion.py` | weekly_ideas.md | Notion DB | Sunday + daily |
| `produce_blog.py` | KB + topic (opt `--listicle N` for Top-N) | `content/blogs/<slug>.md` | Mon/Tue/Wed |
| `auto_edit.py` | raw video + script | `assets/video/edited/<slug>.mp4` | Thu/Fri/Sat |
| `clip_shorts.py` | edited video | `assets/video/edited/shorts/{slug}_short_NN.mp4` | post-edit |
| `repurpose_blog.py` | blog markdown | Medium/Substack/LinkedIn drafts | post-blog |
| `publish_medium.py` | blog markdown | Medium API | Sat |
| `upload_youtube.py` | edited video | YouTube API | Thu/Fri |
| `scheduler.py` | `scheduling.db` | platform APIs | continuous (launchd) |
| `update_notion_status.py` | — | Notion DB row | post-publish |

---

## Hardcoded → Config Migration Status

| Was hardcoded | Now in | Status |
|---------------|--------|--------|
| Notion Contents DB ID | `.env` `NOTION_CONTENTS_DB_ID` | ✅ done |
| Niche names (Tech/Life/Poetry) | `sync_ideas_to_notion.py` `NICHE_TO_TOPIC` | kept (schema-bound) |
| Banned words list | `CLAUDE.md` | kept (identity) |
| Platform handles | `CLAUDE.md` | kept (identity) |
