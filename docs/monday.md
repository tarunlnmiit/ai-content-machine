# Monday — DS Blog Production (~25 min)

## Step 0 — Check buffer first (1 min)

```bash
ls content/buffer/week-1/data_science_tech/*_meta.md 2>/dev/null
```

**Buffer has content?** → Skip Steps 1–4. Use buffer files directly:
- Script: `content/buffer/week-1/data_science_tech/*_youtube_script.md`
- Blog: `content/buffer/week-1/data_science_tech/*_substack_post.md`
- Social: `content/buffer/week-1/data_science_tech/*_social_copy.md`

Jump straight to Tuesday (Life blog) or rest. After consuming: log in Notion as `Script`, then check if Sunday buffer replenishment happened (must be at 4 weeks before this Monday ends).

**No buffer?** → Proceed with Steps 1–4 below. Alert: buffer should never be empty — check Sunday Step 7.

---

## Step 1 — Pick topic (5 min)

Preferred — pick from Notion Contents DB (`Status=Idea`, `Topic=Tech`):
- Synced Sunday by `scripts/sync_ideas_to_notion.py`
- Update picked row's `Status` → `In Progress`

Or local file:
```bash
cat data/ideas/weekly_ideas.md
# Read top 5 DS ideas. Pick one.

# Optional — refresh sources manually before picking:
python3 scripts/rss_scraper.py                    # Reddit (10 DS subs incl mlops, analytics)
python3 scripts/fetch_external_feeds.py           # HN, arXiv, Medium tags, DEV.to, GitHub trending
python3 scripts/fetch_google_suggest.py --quick   # Google + YouTube autocomplete
python3 scripts/idea_scorer.py                    # rescore + rewrite weekly_ideas.md
python3 scripts/sync_ideas_to_notion.py           # push to Notion
```

## Step 2 — Produce blog (~2 min running)

Option A — topic only:
```bash
python3 scripts/produce_blog.py --topic 'YOUR TOPIC' --niche ds
python3 scripts/produce_blog.py --topic 'YOUR TOPIC' --niche ds --humanize
```

Listicle mode — force a Top-N structure (e.g. "Top 5 Python Libraries..."):
```bash
python3 scripts/produce_blog.py --topic 'Python libraries every DS should know' --niche ds --listicle 5
python3 scripts/produce_blog.py --topic 'mistakes that wreck your week' --niche life --listicle 3 --humanize
```
- `--listicle N` (N ≥ 2): produces a numbered Top-N blog. Title starts with "Top N", body has exactly N H2 item sections, balanced length.
- Works for any niche. Skip flag for default narrative structure.

Option B — have transcript/notes/draft:
```bash
python3 scripts/ghostwrite.py --source path/to/notes.txt --niche ds
python3 scripts/ghostwrite.py --source transcript.txt --niche ds --voice analytical --desire clarity
python3 scripts/ghostwrite.py --source notes.md --niche ds --topic 'YOUR TOPIC'
```

Saves to: `content/blogs/YYYY-MM-DD_data_science_tech_{slug}.md`

Voice options: `analytical` (default) · `conversational` · `deletion` · `decision`
Desire options: `success` · `clarity` · `status` · `tribe` · `fear` · `enjoyment`

## Step 3 — Fill personal sections (10 min)
```bash
grep -rn 'PERSONAL_INSERT' content/blogs/
# Open blog, replace every [PERSONAL_INSERT] with real memory/story
```

## Step 4 — Add images (5 min)
```bash
# Preview first
python3 scripts/fetch_images.py --input content/blogs/[monday_ds_blog].md --dry-run

# Auto-fetch from Pexels
python3 scripts/fetch_images.py --input content/blogs/[monday_ds_blog].md

# Manual swap (e.g. marker 1)
python3 scripts/fetch_images.py --input content/blogs/[monday_ds_blog].md --manual 1 --image ~/path/to/photo.jpg --alt "Caption"
```

Marker format:
```
[IMAGE_INSERT: laptop with python code]
[IMAGE_INSERT: laptop with python code | My workspace in 2023]
```

Images → `content/blogs/{stem}_images/` · Map → `content/blogs/{stem}_images/IMAGE_MAP.md`

---

## After production — buffer or keep live?

```bash
python3 scripts/push_to_buffer.py --auto --dry-run   # preview
python3 scripts/push_to_buffer.py --auto              # run
```
→ Decision logic + file naming: [_buffer_decision.md](_buffer_decision.md)

