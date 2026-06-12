# Content Machine — Docs Hub

Single entry point. Pick path by question.

| Question | Go to |
|----------|-------|
| What do I do today? | [weekly-operating-guide.md](weekly-operating-guide.md) → daily file |
| I have free Sunday — batch a week? | [sunday-batch.md](sunday-batch.md) |
| How does video editing work? | [video-production-guide.md](video-production-guide.md) |
| How does Medium repurposing work? | [medium-repurposing-guide.md](medium-repurposing-guide.md) |
| How do I set up automation (launchd)? | [launchd-daily-ideas.md](launchd-daily-ideas.md) · [launchd-build-kb.md](launchd-build-kb.md) |
| Where did the weekend mini-courses go? | Separate repo: [`tarunlnmiit/course-machine`](https://github.com/tarunlnmiit/course-machine) (extracted 2026-06-11, see [repo-split-plan.md](repo-split-plan.md)) |

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
