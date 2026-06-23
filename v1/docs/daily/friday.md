> ⚠️ **PIPELINE UPDATED 2026-06-20 — canonical model: [`docs/pipeline-2026.md`](../pipeline-2026.md).**
> Twitter **dropped**. Instagram / Threads **auto-publish** via the Meta Graph API (`scripts/scheduler.py`); Facebook mirrors Instagram; LinkedIn **active** (employer cleared) with the blog link in the **pinned first comment**. Reels → **Instagram Reels + YouTube Shorts only**, ≈9 **distinct** reels/week (not ~56). 3 long-form (1/niche). Poetry short = **poem only**; poetry Medium = poem + 150–350w essay. Worksheet email CTA (DS/Life) is the owned channel (Substack retired). Run `python3 scripts/weekly_winners.py` before producing. Only manual steps left: record · ~10-min approve · reply to comments/DMs.
>
> Where any step below disagrees with this banner or the canonical doc, the canonical doc wins.

# Friday — Stage + Plan All Social Posts (~45 min)

Videos are live on YouTube from Thursday. Today: stage LinkedIn into the scheduler DB, gather the blog URLs you'll need for captions, and set the reminders/queue for posting next week. **No Metricool, no Publer, no CSV** — Instagram / Facebook / Threads / Twitter are posted **manually in-app** in each niche's engagement window. LinkedIn stays manual too until employer clearance (the scheduler/API path exists but is dormant).

**Pivot rule:** Today you plan content produced THIS week. It posts NEXT week. Blogs + videos already went live this week (Wed/Thu). Social posts (IG, Threads, Twitter, LinkedIn) fire in week N+1 — that's what today's staging + reminders set up.

> **Reference docs:**
> - Instagram virality (saves ÷ views, DM automation, 2-hour window): this doc + `docs/one-time-platform-setup.md`
> - LinkedIn virality (hook formula, first-comment strategy): this doc + `docs/one-time-platform-setup.md`
> - Twitter virality (thread hooks, 24-hour loop): this doc + `docs/one-time-platform-setup.md`
> - Medium virality (read ratio, title formulas, publication submissions): `prompts/medium-virality-prompt.md`
> - YouTube virality (CTR, AVD, Shorts loop-ability): `prompts/youtube-virality-prompt.md`
> - Podcast virality (Spotify completion rate, cross-promotion funnel): `prompts/podcast-virality-prompt.md`
> - Repurposing agent (blog → all platform derivatives): `prompts/repurposing_agent.md`
> - Anything slipped today? Handle it tomorrow: `docs/saturday.md`

## Friday at a glance

| Time | Action | Output |
|------|--------|--------|
| 9:00 AM | Stage LinkedIn + gather blog URLs | `load_posts.py` → `scheduling.db` (LinkedIn staged, held manual) |
| 9:15 AM | Confirm static captions/images ready | `instagram_caption.txt` / `threads_post.txt` per slug |
| 9:30 AM | Set IG/Threads posting reminders | Calendar reminders per niche window (next week) |
| 9:45 AM | Queue Twitter threads | Reminders set or MCP posted manually |
| 10:00 AM | Final verification | Reminders + LinkedIn DB queue confirmed |

---

## Step 1 — Stage LinkedIn + gather blog URLs (5 min)

Stage **this week's content** for next week (the +1 pivot rule):

```bash
python3 scripts/load_posts.py
```

This reads all `content/derivatives/{week}/*/schedule.json` and:
- Inserts LinkedIn posts into `data/scheduling.db` (the `scheduler.py` API path — **held manual until employer clearance**, so the daemon stays off until then)
- Emits `output/scheduled/upload_shorts.sh` (pre-filled Shorts upload commands)
- **No Metricool/Publer CSV** — IG / FB / Threads are posted by hand (Step 2 below)

### Gather the Medium URLs you'll paste into captions

```bash
# Check which slugs are missing Medium URLs in schedule.json
python3 -c "
import json, glob
for f in glob.glob('content/derivatives/{week}/*/schedule.json'):
    d = json.load(open(f))
    if not d.get('medium_url'):
        print('MISSING medium_url:', f.split('/')[-2][:50])
"
```

Add any missing URL so it's recorded for your captions:
```bash
python3 scripts/update_schedule.py \
  --slug {slug} --week {week} \
  --medium-url 'https://medium.com/@tarun-gupta/your-post-slug'
```

---

## Step 2 — Post static content manually (IG / FB / Threads) (~10 min)

No Metricool, no Publer, no CSV import. For each slug, post by hand in the niche's window:

- **Instagram / Facebook:** caption from `content/derivatives/{week}/{slug}/instagram_caption.txt`; image from `assets/social_posts/{week}/{slug}_instagram.png` (carousels: `slide_outline.json` slides). Paste the Medium URL inline ("Full post 👉 …").
- **Threads:** body from `content/derivatives/{week}/{slug}/threads_post.txt` — post as-is (it reads differently from the IG caption by design).

Post in the engagement window and reply to early comments (see Step 2c). Don't pre-schedule — the 2-hour window only works if you're present.

### Expected posting schedule for next week

| Niche | Platform | Day | Time IST |
|-------|---------|-----|---------|
| Life | Instagram + Facebook | Tue | 8:00 AM |
| Life | Threads | Tue | 8:00 PM |
| Life | LinkedIn | Tue | 8:00 AM *(manual until clearance)* |
| DS | Instagram + Facebook | Wed | 8:00 AM |
| DS | Threads | Wed | 8:00 PM |
| DS | LinkedIn | Tue | 8:00 AM *(manual until clearance)* |
| Poetry | Instagram + Facebook | Fri | 10:00 AM |
| Poetry | Threads | Fri | 12:00 PM |
| Poetry | LinkedIn | Tue | 8:00 AM *(manual until clearance)* |

### Manual-posting reminders

| Watch for | Fix |
|-----------|-----|
| Wrong week | Content created this week posts NEXT week (+1 offset) — set reminders for next week's days |
| Image not ready | Confirm `assets/social_posts/{week}/{slug}_instagram.png` exists before the posting window |
| Caption missing blog link | Paste the Medium URL inline ("Full post 👉 …") when you post |

---

## Step 2b — Post Instagram Reels (NEW — ~10 min)

Instagram Reels are posted manually and natively in the IG app — separate from static posts and carousels (those are Step 2). Render the short first, then post in-app.

### Check that reel briefs exist

```bash
# Verify ig_reel_brief.md was generated for each slug
for slug_dir in content/derivatives/2026-W{nn}/*/; do
  if [ -f "${slug_dir}ig_reel_brief.md" ]; then
    echo "✓ $(basename $slug_dir)"
  else
    echo "✗ MISSING: $(basename $slug_dir)"
  fi
done
```

If missing, generate now:
```bash
python3 scripts/generate_ig_reel_brief.py --week 2026-W{nn}
```

### Reel rendering + posting workflow (once per week per account)

Text overlays are rendered automatically via Remotion using the `[TEXT_OVERLAY]` tags annotated in the script on Tuesday. DaVinci Resolve handles the underlying edit; Remotion bakes overlays onto the vertical clip. No manual overlay work in any other tool.

**Step 1 — Confirm overlay scene plan exists (generated Tuesday)**

```bash
ls remotion/public/scene-plans/{week}/{ds_slug}_overlay.json
ls remotion/public/scene-plans/{week}/{life_slug}_overlay.json
ls remotion/public/scene-plans/{week}/{poetry_slug}_overlay.json
```

If any are missing, regenerate from the annotated script:
```bash
python3 scripts/generate_scene_plans.py \
  --script content/scripts/{week}/{slug}_reel.md \
  --niche {ds|life|poetry} --week {week} --mode overlay
```

**Step 2 — Confirm vertical clips exist (generated Thursday)**

```bash
ls assets/video/edited/shorts/{week}/{ds_slug}_short_00.mp4
ls assets/video/edited/shorts/{week}/{life_slug}_short_00.mp4
ls assets/video/edited/shorts/{week}/{poetry_slug}_short_00.mp4
```

If missing, see `docs/daily/thursday.md` Step 2 for `create_vertical_reels.py`.

**Step 3 — Render shorts with overlays via Remotion**

There is no `VerticalReel` composition. Shorts come in two formats — pick per piece (overlay text is burned in by the composition either way):

```bash
# Path A — clip-based vertical reels (talking-head segments, from Step 2 create_vertical_reels.py)
#   → assets/video/edited/shorts/{week}/{slug}_short_NN.mp4   (already produced)

# Path B — Remotion motion shorts (per-slot scene plans listed in shorts_manifest.json)
python3 scripts/render_shorts_batch.py --week {week} --niche ds      # then life, poetry
#   → output/animations/{week}/{slug}_s{NN}.mp4
```

Output: `assets/video/edited/shorts/{week}/` (Path A) or `output/animations/{week}/*_s*.mp4` (Path B).

**Step 4 — Post on Instagram**

| Reel | Account | Post Day | Time IST |
|------|---------|---------|---------|
| DS | @breathofdatascience | Wednesday | 8:00 AM |
| Life | @mistakenlyhuman | Tuesday | 7:00 PM |
| Poetry | @mistakenlyhuman | Thursday | 8:00 PM |

For each reel:
1. Instagram → + → Reel → select the short from Step 3: clip-based `assets/video/edited/shorts/{week}/{slug}_short_NN.mp4` or motion `output/animations/{week}/{slug}_s{NN}.mp4`
2. Add trending audio natively in the Instagram app (Audio button during posting, 10–20% volume) — do not bake audio into the file
3. Paste caption from `ig_reel_brief.md`
4. Cover image: pick the frame where the hook overlay is visible
5. Post manually (do not schedule Reels — post in the engagement window)

### Reels vs. static posts — timing rule

| Content | Account | Day | Time IST |
|---------|---------|-----|---------|
| DS Reel | @breathofdatascience | Wednesday | 8:00 AM |
| Life Reel | @mistakenlyhuman | Tuesday | 7:00 PM |
| Poetry Reel | @mistakenlyhuman | Thursday | 8:00 PM |

> Reels and static posts should NOT go live on the same day for the same account — the algorithm splits attention. Stagger them by 1–2 days.

### DM keyword setup (one-time + check weekly)

> **Full SuperProfile configuration:** `docs/super-profile-setup.md` — covers both accounts (@mistakenlyhuman and @breathofdatascience), link-in-bio folder structure, keyword automation setup, and auto-DM message templates.

- Login to [SuperProfile](https://superprofile.bio) or CreatorFlow
- Add the DM keyword from the reel brief (e.g. `TYPES`, `STIGMA`, `POEM`)
- Link it to the relevant blog URL
- Verify the auto-reply message is on brand (no "Hey! Here's your link 😊 🔗" — write it in your voice)

---

## Step 2c — First 2-hour engagement window (MANDATORY — the most important step on this page)

The Instagram algorithm decides whether to distribute your reel beyond your existing followers based almost entirely on what happens in the first 2 hours after posting. DM shares are weighted 3–5× more than likes. Saves are weighted more than comments. Your job in this window is to signal to the algorithm that this content resonates.

**When a reel goes live:** Set a 2-hour timer on your phone immediately. Do not close Instagram.

### What to do during the 2-hour window:

**Every comment — respond within the first 2 hours:**
- Reply to EVERY comment, even single-word ones ("🔥" → "Thank you! Which part resonated?")
- Ask a follow-up question in your replies to generate more activity
- Heart every comment you can't respond to in full
- The goal is to keep the comment thread active — each reply extends the algorithmic window

**Every DM from the keyword trigger:**
- When someone comments the keyword (e.g. `TYPES`), SuperProfile auto-sends the blog link
- Check your DMs and verify the auto-DM fired correctly
- If someone DMs you directly (not via keyword), respond personally — not with the auto-DM text

**Stories cross-post:**
- Within 30 minutes of posting the reel: share it to your Stories
- On Stories, add a text sticker: "New reel dropped 👆 Swipe up" (or "Link in bio")
- This sends your existing followers to the reel, boosting early watch time

**Do NOT:**
- Post another reel or static post within the 2-hour window on the same account (splits attention)
- Ignore comments for 2+ hours after posting
- Close the app and come back the next day

### 2-hour window checklist (run immediately after each reel post):

- [ ] Timer set: 2 hours from right now
- [ ] Reel shared to Stories within 30 minutes
- [ ] At 30 min: replied to all comments so far
- [ ] At 60 min: replied to all new comments, checked DM auto-trigger is firing
- [ ] At 90 min: replied to all new comments
- [ ] At 2 hours: final reply sweep, timer off

**Which reels get this treatment:**
| Reel | Account | Post day | 2-hour window |
|------|---------|----------|--------------|
| DS Reel | @breathofdatascience | Wednesday 8:00 AM | 8:00–10:00 AM IST |
| Life Reel | @mistakenlyhuman | Tuesday 7:00 PM | 7:00–9:00 PM IST |
| Poetry Reel | @mistakenlyhuman | Thursday 8:00 PM | 8:00–10:00 PM IST |

These are the posting times from Step 2b. The 2-hour window runs immediately after each one.

---

## Step 2d — Cross-platform distribution (same day as each reel post)

Each reel gets distributed to other platforms on the same day it posts. Do this within 2 hours of posting the reel (during the engagement window above).

### For DS Reel (@breathofdatascience):

1. **Stories** (already done in Step 2c above)
2. **Threads**: go to @breathofdatascience on Threads → New post → paste the reel caption from `ig_reel_brief.md` → add "New reel on IG 👆" at the top → post
3. **Twitter/X thread**: DS threads go live when you're active (no fixed slot) — if engagement is high in the 2-hour window, post the DS twitter thread now from `content/derivatives/{week}/{ds_slug}/twitter_thread.txt`

### For Life Reel (@mistakenlyhuman):

1. **Stories** (done in Step 2c above)
2. **Threads**: go to @mistakenlyhuman on Threads → New post → paste Life caption from `ig_reel_brief.md` → add "New reel on IG 👆" at the top → post

### For Poetry Reel (@mistakenlyhuman):

1. **Stories** (done in Step 2c above)
2. **Threads**: go to @mistakenlyhuman on Threads → paste Poetry caption → "New reel on IG 👆" → post
3. **No comment keyword for poetry** — poetry CTA is "Save this 🤍", not a DM trigger. No SuperProfile setup needed.

### Why same-day distribution matters:

Threads and Stories shares generate link-clicks back to the reel. Each click from outside Instagram signals to the algorithm that the reel has external demand — this expands distribution to non-followers. Do it on the same day (not the next morning). Late cross-posts don't get the same distribution boost because the algorithm's decision window for that reel has already closed.

---

## Step 3 — LinkedIn: manual until clearance (5 min)

> **Current model:** LinkedIn is posted **manually** until employer clearance. `load_posts.py` stages the posts into `scheduling.db`, but the `scheduler.py` daemon stays **off** so nothing auto-fires. Until cleared: at the Tuesday 8:00 AM slot, post each `linkedin_post.txt` by hand, then run the first-comment strategy (Step 3b). The scheduler steps below document the API path for **after** clearance — leave the daemon stopped until then.

LinkedIn posts are handled by `scheduler.py` (direct API) once enabled — never Metricool.

### Check scheduler is running

```bash
ps aux | grep 'scheduler.py' | grep -v grep
```

Not running? Start it:
```bash
nohup python3 scripts/scheduler.py > data/analytics/scheduler.log 2>&1 &
echo "Scheduler started, PID: $!"
```

Or via launchd (preferred — survives reboots):
```bash
launchctl load ~/Library/LaunchAgents/com.contentmachine.scheduler.plist
launchctl list | grep contentmachine
```

### Check what's queued for next week

```bash
sqlite3 data/scheduling.db \
  "SELECT platform, scheduled_at, substr(content_text,1,80) AS preview
   FROM posts
   WHERE status='pending' AND platform='linkedin'
   ORDER BY scheduled_at
   LIMIT 10"
```

Expected: 3 rows (one per niche), all scheduled for next Tuesday ~8:00 AM IST.

### If LinkedIn posts are missing from DB

Re-run `load_posts.py` — it re-inserts missing entries:
```bash
python3 scripts/load_posts.py
sqlite3 data/scheduling.db \
  "SELECT COUNT(*) FROM posts WHERE status='pending' AND platform='linkedin'"
# Should return 3
```

### Check recent scheduler activity

```bash
tail -30 data/analytics/scheduler.log
```

Look for `[POST]` lines for linkedin. If seeing `FAILED: 401` → LinkedIn token expired:
```bash
python3 scripts/auth_linkedin.py --refresh
```

LinkedIn tokens expire every 60 days — add a calendar reminder.

---

## Step 3b — LinkedIn first-comment strategy (MANDATORY — do this Tuesday 8:00 AM)

LinkedIn's algorithm suppresses posts that contain external links in the post body. The `linkedin_post.txt` generated by `repurpose_blog.py` does NOT include the blog link in the body — this is intentional. The link goes in the **first comment**, posted immediately after the scheduler fires the post.

**When:** Tuesday 8:00 AM IST — the moment `scheduler.py` posts the LinkedIn content.

**What to do:**

Set a phone alarm for **Tuesday 7:58 AM IST**. When it fires:

1. Open LinkedIn on your phone or browser
2. Find the post that just went live (it will be at the top of your profile feed)
3. Tap "Add a comment"
4. Type exactly: `Full post 👉 [Medium URL for this niche]`
   - DS → medium.com/@tarun-gupta/{ds_slug}
   - Life → medium.com/@tarun-gupta/{life_slug}
   - Poetry → medium.com/@tarun-gupta/{poetry_slug}
5. Post the comment
6. Immediately "like" your own comment (this pins it to the top of the comment section)

Do this for ALL THREE posts (DS, Life, Poetry — all fire Tuesday 8:00 AM IST).

### LinkedIn engagement window — first 60 minutes (Tuesday 8:00–9:00 AM)

LinkedIn's algorithm evaluates early engagement heavily. The first 60 minutes of a post's life determine whether it gets pushed to your 2nd-degree connections.

During the window:
- Reply to every comment within the hour — even single-word reactions ("Thanks! Which part resonated most with you?")
- Do NOT edit the post after publishing — LinkedIn penalizes edits within the first 2 hours (resets distribution)
- Do NOT post another piece of content on the same platform within this window

### What counts as a "good" LinkedIn engagement signal:

| Signal | Weight | What it means |
|--------|--------|--------------|
| Comments | High | Someone had a reaction strong enough to type |
| Reposts | Very high | Someone vouched for you to their audience |
| Reactions (not just Like) | Medium | Insightful/Love = stronger than Like |
| Dwell time | High (invisible) | LinkedIn tracks how long people stop on your post |
| Link clicks | Medium | External traffic signal |

The one you can influence most: **comments**. Reply to generate reply chains — each reply re-exposes the post to the commenter's network.

---

## Step 4 — Queue Twitter threads + engagement strategy (~15 min)

Twitter/X threads are posted manually — scheduled tools flatten voice and context.

### Life thread — post Mon 1:00 PM IST (next week)

```bash
cat content/derivatives/{week}/{life_slug}/twitter_thread.txt
```

Before posting: verify tweet 1 has the `[TWITTER_HOOK: validated]` tag from Tuesday's audit. If it doesn't, re-read tweet 1 and check it follows the hook formula (bold claim or specific incident ending with 🧵). Rewrite tweet 1 if needed — the rest of the thread can stay as-is.

Open Twitter/X:
- New tweet → type tweet 1 → click "Add another tweet" → paste/type tweet 2 → repeat
- **OR** use the MCP tool to post immediately:
  ```
  mcp__twitter-mcp__post_tweet
    text: "[tweet 1 text]"
  ```
  Then post subsequent tweets as replies to tweet 1.

Set a calendar reminder for **next Mon 1:00 PM IST**.

### Twitter first-hour engagement — Life thread (Monday 1:00–2:00 PM)

Set a second reminder: **Monday 1:00 PM IST + 60 minutes**. During that hour:
- Reply to every reply on the thread — especially tweet 1 replies (those are people who read the hook but not the thread)
- Like every reply
- If engagement is high (5+ replies in 30 minutes), quote-tweet your own thread with a 1-sentence summary: "The short version if you don't have 3 minutes: [one sentence]" — this re-exposes the thread to your followers a second time
- Do NOT post anything else on Twitter during this window

### 24-hour retweet loop — all threads

24 hours after any thread posts, if it got ≥ 3 replies:
```bash
# Check which threads are 24 hours old and worth re-amplifying:
cat data/analytics/research_log.txt | tail -20
```

Quote-tweet (retweet with comment) your own thread with the most engaging tweet from the thread — usually the `[SHAREABLE_MOMENT]` line. Format:
> "The line that got the most reactions from this thread: [the line]
> Full thread: [link to tweet 1]"

This is the Twitter equivalent of the Instagram 2-hour window — a second algorithmic push 24 hours later.

### Poetry thread — post Fri 12:00 PM IST (next week)

```bash
cat content/derivatives/{week}/{poetry_slug}/twitter_thread.txt
```

Poetry thread format:
1. Opening couplet or striking image description (tweet 1 — the hook)
2. The poem excerpt (2–3 tweets)
3. Context: what inspired the poem
4. Personal reflection
5. CTA: "Read the full piece → [link]" (or save CTA — "Save this if it found you at the right time")

Set a calendar reminder for **next Fri 12:00 PM IST**.
Same first-hour engagement rules as Life thread above.

### DS thread — no fixed slot (post when you're active)

DS Twitter audience responds better to spontaneous hot-takes than scheduled threads. Read `content/derivatives/{week}/{ds_slug}/twitter_thread.txt` for the draft. Post it when you're active in the timeline and can reply to comments within the first hour — blank-scheduling it when you're offline loses the engagement window entirely. Only post the DS thread when you have 60 minutes free to engage.

### Pin your best thread of the week

After Sunday's analytics check, identify which thread got the most replies or retweets this week. Go to that tweet → tap the three dots → **Pin to profile**. Replace the previous pinned tweet. Your pinned tweet is the first thing new followers see — keep it your most compelling recent work.

---

## Step 5 — Final verification checklist (5 min)

### Posting reminders set (next week)

Confirm calendar reminders exist for each manual post in its window:
- Tue: Life IG/FB (8 AM) + Life Threads (8 PM) + Life LinkedIn (8 AM, manual)
- Wed: DS IG/FB (8 AM) + DS Threads (8 PM) + DS LinkedIn (manual)
- Fri: Poetry IG/FB (10 AM) + Poetry Threads (12 PM) + Poetry LinkedIn (manual)

### DB queue (LinkedIn staged)

```bash
sqlite3 data/scheduling.db \
  "SELECT platform, COUNT(*) AS count, MIN(scheduled_at) AS first
   FROM posts WHERE status='pending'
   GROUP BY platform ORDER BY first"
```

Expected: linkedin rows = 3 (staged; daemon stays off until clearance).

### File artifacts

```bash
ls -la output/scheduled/
# upload_shorts.sh — modified today (YouTube Shorts upload commands)
# (no metricool_*.csv — distribution is manual now)
```

### End-of-week checklist

- [ ] Static captions/images ready (IG `instagram_caption.txt` + `_instagram.png`, Threads `threads_post.txt`)
- [ ] Reminders set for next-week posting windows (Tue/Wed/Fri per niche)
- [ ] LinkedIn queue has 3 pending posts in DB (scheduler daemon OFF until clearance)
- [ ] Twitter reminders set: Life Mon 1 PM, Poetry Fri 12 PM (both next week)
- [ ] YouTube videos uploaded and scheduled (done Thursday)
- [ ] Shorts queue active — 2/day Mon–Sun (done Thursday)
- [ ] Notion status updated: Status → Uploaded for all 3 content items
- [ ] Week archived to `/Volumes/Archive` (Step 7)

---

## Step 6 — Buffer depth check (~5 min)

Run every Friday to ensure buffer never drops below 4 weeks per niche before the weekend.

```bash
for niche in data_science_tech life_self_dev poetry_quotes; do
  count=$(ls content/buffer/week-*/${niche}/*_meta.md 2>/dev/null | wc -l | tr -d ' ')
  echo "$niche: ${count}/4"
done
```

All at 4 → done, weekend free.

Any niche < 4 → replenish now:
```bash
# 1. Open data/buffer/topics.yaml — fill empty week slots
#    Check Notion first: python3 scripts/query_notion_recent.py --days 90

# 2. Preview:
conda run -n content_engine_env python3 scripts/generate_buffer.py --dry-run

# 3. Generate:
conda run -n content_engine_env python3 scripts/generate_buffer.py
# Or targeted:
conda run -n content_engine_env python3 scripts/generate_buffer.py --niche poetry
conda run -n content_engine_env python3 scripts/generate_buffer.py --week 4
```

AutoTune temps: DS=0.4, Life=0.85, Poetry=1.15.

Also refresh the content tracker:
```bash
python3 scripts/sync_tracker.py
# → data/content_tracker.csv updated with this week's final state

python3 scripts/generate_posting_tracker.py --year 2026
# → output/trackers/annual-tracker-2026.xlsx updated with new content titles
```

---

## Step 7 — Archive week to external drive (~2 min)

Move all week content off the internal SSD to `/Volumes/Archive`. Run **after** uploads and scheduling are confirmed complete.

```bash
# 1. Connect the Archive drive — verify it's mounted
ls /Volumes/Archive

# 2. Dry run first — see what will move
python3 scripts/archive_week.py \
  --repo "/Users/tarungupta/Making It Big/Claude/content-machine" \
  --week 2026-W24 \
  --dry-run

# 3. Move for real
python3 scripts/archive_week.py \
  --repo "/Users/tarungupta/Making It Big/Claude/content-machine" \
  --week 2026-W24
```

Replace `2026-W24` with the current ISO week. Script auto-discovers every `2026-Wnn/` subfolder across the repo (assets, content, output, remotion/public, etc.) and moves them all.

**What gets archived:**
- `assets/hyperframes/`, `assets/raw/`, `assets/social_posts/`, `assets/slides/`, `assets/carousels/`, `assets/video/`, `assets/stories/`, `assets/thumbnails/`, `assets/teleprompter/`
- `content/blogs/`, `content/scripts/`, `content/derivatives/`, `content/worksheets/`, `content/prompts/`
- `output/animations/`, `output/worksheets/`, `output/scheduled/`
- `remotion/public/broll/`, `remotion/public/captions/`, `remotion/public/edit-plans/`, `remotion/public/scene-plans/`, `remotion/public/videos/`

**Destination:** `/Volumes/Archive/content-archive/{year}/W{nn}/`
**Manifest + log** written to same destination folder.

If drive not available, skip and run next time the drive is connected. Use `--copy` to keep source files (backup mode instead of archive).
