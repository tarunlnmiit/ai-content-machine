# Scripts Index

> 100+ scripts live flat here. Use this index to find the right one.
> `lib/` contains shared utilities imported by these scripts — don't run lib files directly.

---

## The main commands (90% of your usage)

```bash
# 1. Generate reel script before recording
python3 scripts/prepare_reel_script.py --from blog <blog.md> --niche ds --slug <slug>
python3 scripts/prepare_reel_script.py --from tool 2026-W26 --niche ds --project free_tool_ds --slug <slug>

# 2. Run the full V2 video pipeline after recording
python3 scripts/run_video_pipeline.py --raw assets/raw/<file>.mov --manifest <manifest.json>

# 3. Run the blog pipeline (all derivatives from one blog)
python3 scripts/run_blog_pipeline.py --input content/blogs/<week>/<slug>.md

# 4. Run the voiceover week pipeline
python3 scripts/run_voiceover_week.py --audio assets/audio/<file>.m4a --niche ds --slug <slug>

# 5. Stage posts for publishing
python3 scripts/load_posts.py

# 6. Score and surface weekly ideas
python3 scripts/idea_scorer.py
```

---

## Video production — V2 pipeline (use these)

| Script | What it does |
|---|---|
| `prepare_reel_script.py` | Generate 5-beat reel script + manifest.json before recording |
| `run_video_pipeline.py` | **Master V2 pipeline**: raw → trim → storyboard → HF → final MP4 |
| `hyperframes_pipeline.py` | HyperFrames phase only (beat builds + renders + FFmpeg composite) |
| `video_trim.py` | Trim silence, retakes, fillers from raw recording |
| `run_voiceover_week.py` | Voiceover-first lane: m4a → long-form + portrait shorts |
| `prepare_voiceover_edit.py` | Prep step for voiceover edits |
| `hyperframes_render.py` | Lower-level HF render helper |

## Video production — legacy (pre-V2, still works)

| Script | What it does |
|---|---|
| `prepare_remotion_edit.py` | Old Remotion-based edit prep |
| `auto_edit.py` | Automated silence cut + edit (old pipeline) |
| `create_vertical_reels.py` | Old vertical reel creator |
| `render_week.py` | Batch render a week of Remotion animations |
| `render_overlay_scenes.py` | Render Remotion overlay scenes |
| `render_shorts_batch.py` | Batch shorts render |
| `bake_overlays.py` | Bake overlays into video |
| `clip_shorts.py` | Clip shorts from long-form |
| `generate_viral_reel_brief.py` | Brief for recording standalone reels (pre-V2) |

---

## Content generation

| Script | What it does |
|---|---|
| `run_blog_pipeline.py` | **One command** → all blog derivatives + media |
| `produce_blog.py` | Generate blog post from topic |
| `repurpose_blog.py` | Repurpose blog → social text posts |
| `idea_scorer.py` | Score + surface weekly ideas per niche |
| `generate_yt_script.py` | YouTube script from blog |
| `generate_ig_reel_brief.py` | IG reel brief from blog |
| `generate_carousel.py` | Carousel HTML from blog |
| `generate_slide_deck.py` | Slide deck HTML from blog |
| `generate_worksheet_outline.py` | Worksheet outline (DS/Life only) |
| `generate_thumbnail.py` | Thumbnail brief |
| `ghostwrite.py` | Ghostwrite content variant |

## Exports & social assets

| Script | What it does |
|---|---|
| `generate_social_images.py` | Social images per platform |
| `export_html_deck.py` | Export HTML slide deck |
| `export_social_cards.py` | Export social cards |
| `generate_canva_prompts.py` | Canva design prompts |
| `generate_design_prompts.py` | Design prompts for AI image generation |
| `generate_captions.py` | Generate captions |
| `generate_shorts_meta.py` | Shorts metadata (title, description) |
| `inject_worksheet_ctas.py` | Inject worksheet URLs into captions |

---

## Publishing & distribution

| Script | What it does |
|---|---|
| `scheduler.py` | **Auto-publish daemon** — runs continuously (launchd) |
| `load_posts.py` | Stage posts into buffer for scheduler |
| `post_instagram.py` | Post to Instagram (Graph API) |
| `post_threads.py` | Post to Threads |
| `post_linkedin.py` | Post to LinkedIn |
| `post_facebook.py` | Mirror to Facebook from Instagram |
| `publish_medium.py` | Publish to Medium |
| `upload_youtube.py` | Upload to YouTube |
| `upload_youtube_shorts_batch.py` | Batch upload Shorts |
| `push_to_buffer.py` | Push to Buffer |
| `push_linkedin_schedule.py` | Push LinkedIn schedule |

---

## Analytics

| Script | What it does |
|---|---|
| `collect_analytics.py` | Collect GitHub stars + 7-day delta |
| `fetch_youtube_analytics.py` | Pull YouTube analytics |
| `fetch_twitter_analytics.py` | Pull Twitter analytics export |
| `convert_medium_analytics.py` | Convert Medium analytics CSV |
| `generate_ig_insights.py` | Generate IG insights report |
| `weekly_winners.py` | Surface best-performing content |
| `youtube_scraper.py` | Scrape YouTube competitor data |
| `scrape_instagram_trends.py` | Scrape IG trends |

---

## Fetchers & data collection

| Script | What it does |
|---|---|
| `auto_generate_broll.py` | Auto-fetch B-roll for transcript keywords |
| `fetch_images.py` | Fetch images |
| `fetch_videos.py` | Fetch video assets |
| `download_bgm.py` | Download background music |
| `fetch_external_feeds.py` | Fetch RSS/external feeds |
| `fetch_google_suggest.py` | Fetch Google Suggest data |
| `rss_scraper.py` | Scrape RSS feeds for ideas |

---

## Utilities & maintenance

| Script | What it does |
|---|---|
| `archive_week.py` | Archive a completed week |
| `organize_iso_weeks.sh` | Reorganize files into ISO week folders |
| `sync_tracker.py` | Sync annual-tracker-2026.xlsx |
| `generate_posting_tracker.py` | Generate posting tracker |
| `list_week_content.py` | List all content for a given week |
| `migrate_to_weekly.py` | Migrate old content to ISO week structure |
| `reorganize_hyperframes.py` | Reorganize HyperFrames render dirs |
| `update_notion_status.py` | Update Notion row status after publish |
| `update_yt_description.py` | Update YouTube video description |
| `worksheet_links.py` | Generate worksheet download links |
| `utm.py` (in lib/) | UTM parameter builder |

---

## Setup & one-time scripts

| Script | What it does |
|---|---|
| `db_setup.py` | Initialize scheduling database |
| `linkedin_auth.py` | LinkedIn OAuth setup |
| `build_knowledge_base.py` | Build/update knowledge base from sources |
| `sync_ideas_to_notion.py` | Sync ideas to Notion DB |

---

## lib/ — shared utilities (imported, not run directly)

| Module | What it provides |
|---|---|
| `content_paths.py` | Canonical path construction (`derivatives_dir`, etc.) |
| `schedule_calc.py` | `get_iso_week(date_str)` and scheduling utilities |
| `niche_config.py` | Niche→canonical name mapping |
| `virality.py` | Virality block injection (hook + CTA + guardrail) |
| `storyboard_gen.py` | AI storyboard generation (Claude Opus) |
| `hf_beat_builder.py` | HyperFrames beat composition generator |
| `hf_validator.py` | HyperFrames render output validator |
| `video_utils.py` | FFmpeg wrappers: `probe_duration`, `run_ffmpeg`, `crop_vertical` |
| `meta_graph.py` | Meta Graph API client (IG, Threads, Facebook) |
| `slug.py` | Slug generation |
| `hashtags.py` | Hashtag generation per niche |
| `tracker.py` | Tracker read/write helpers |
| `utm.py` | UTM parameter builder |
| `claude_cli.py` | `claude -p` CLI subprocess wrapper |
| `content_paths.py` | Path constants and constructors |
