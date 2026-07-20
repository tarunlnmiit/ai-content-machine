---
title: "Sunday — Analytics (~15 min)"
type: doc
slug: sunday
tags: [content/doc]
---
> ⚠️ **PIPELINE UPDATED 2026-06-20 — canonical model: [`docs/pipeline-2026.md`](pipeline-2026.md).**
> Twitter **dropped**. Instagram / Threads **auto-publish** via the Meta Graph API (`scripts/scheduler.py`); Facebook mirrors Instagram; LinkedIn **active** (employer cleared) with the blog link in the **pinned first comment**. Reels → **Instagram Reels + YouTube Shorts only**, ≈9 **distinct** reels/week (not ~56). 3 long-form (1/niche). Poetry short = **poem only**; poetry Medium = poem + 150–350w essay. Worksheet email CTA (DS/Life) is the owned channel (Substack retired). Run `python3 scripts/weekly_winners.py` before producing. Only manual steps left: record · ~10-min approve · reply to comments/DMs.
>
> Where any step below disagrees with this banner or the canonical doc, the canonical doc wins.

# Sunday — Analytics (~15 min)

Auto-runs at 8pm and 10pm produce everything you need. Your job: read them, sync ideas to Notion, verify the scheduler is healthy.

## What runs automatically

| Time | Script | Output |
|------|--------|--------|
| 6:00 AM | `scripts/daily_ideas.sh` | `data/ideas/weekly_ideas.md` |
| 8:00 PM | `scripts/collect_analytics.py` | `data/analytics/weekly_insights.md` |
| 10:00 PM | `scripts/build_knowledge_base.py` | `data/kb/master_brief.md` |
| Continuous | `scripts/scheduler.py` | Fires pending LinkedIn posts every 60s |

> **Automation setup docs:** These scripts run via launchd. If they're not firing, see `docs/launchd-daily-ideas.md` (6 AM ideas job) and `docs/launchd-build-kb.md` (10 PM KB build job) for the plist files, installation steps, and debugging commands.

---

## Step 1 — 48-hour analytics check for this week's reels (~15 min)

This is the most important 15 minutes of the week. You are checking two North Star metrics for each reel posted this week. These numbers tell you whether the content machine is working.

**The two metrics that matter:**

| Metric | What it measures | Target |
|--------|-----------------|--------|
| **Saves ÷ Views** | Content quality score — did people bookmark it? | > 3% |
| **Non-follower reach %** | Distribution score — did it reach beyond your audience? | > 50% |

Everything else (likes, comments, follower count) is a vanity metric. These two are the only signals worth tracking.

---

### 1a. Check each reel posted this week

**This week's reels posted on:** (fill in from your posting schedule)
- DS Reel: @breathofdatascience — posted [Day, Time]
- Life Reel: @mistakenlyhuman — posted [Day, Time]
- Poetry Reel: @mistakenlyhuman — posted [Day, Time]

**For each reel, do this:**

1. Open Instagram on your phone
2. Go to the reel post → tap the three dots (⋯) → **View Insights**
3. Note these exact numbers:

| Field | Where to find it | What to record |
|-------|-----------------|----------------|
| Views | Top of Insights | Total plays |
| Saves | Under "Interactions" | Number of bookmarks |
| Shares | Under "Interactions" | Number of shares (DMs + reshares) |
| Accounts reached | Under "Reach" | Total unique accounts |
| Non-followers reached | Under "Reach" | Non-follower % (or calculate: non-follower accounts ÷ total accounts × 100) |
| Comments | Under "Interactions" | Count |
| DMs from keyword | Check SuperProfile dashboard | Count of triggered DMs |

4. Calculate Saves ÷ Views:
   - Open your phone calculator
   - Saves ÷ Views × 100 = your quality score
   - Example: 45 saves ÷ 1,200 views × 100 = 3.75% ✅

---

### 1b. Decision matrix — what to do based on results

**DS Reel results:**

| Result | What it means | Action |
|--------|--------------|--------|
| Saves/Views > 3% AND non-follower reach > 50% | Strong reel, algorithm is distributing it | Do: repeat the hook style next week. Note the topic angle in `research_log.txt`. |
| Saves/Views > 3% BUT non-follower reach < 50% | Content quality is good, but distribution is stuck in your existing audience | Do: check if you posted within peak window. Check if Stories cross-post happened. The hook may not be compelling enough to share — rewrite hook formula next Tuesday. |
| Saves/Views < 3% BUT non-follower reach > 50% | Algorithm is distributing it but content isn't resonating (people watch but don't save) | Do: the hook worked but the content didn't deliver on the promise. Review the body of the reel — was the "shareable moment" genuinely surprising? |
| Saves/Views < 3% AND non-follower reach < 50% | Weak reel — algorithm suppressed it | Do: do NOT repost it. Identify what failed: hook too vague? No text overlays? Posted wrong time? Log the failure and change one variable next week. |

**Life Reel results:** Same decision matrix. Life-specific context: Life reels perform best 7–9 PM IST. If saves are low, check posting time first.

**Poetry Reel results:** Poetry uses saves + shares (not DM count) as its metric. Non-follower reach > 50% is the key signal. Saves/Views > 5% is the target for poetry (higher bar — poetry is niche, the saved audience matters more than views).

---

### 1c. Log your observations

```bash
echo "" >> data/analytics/research_log.txt
echo "=== $(date '+%Y-%m-%d') ===" >> data/analytics/research_log.txt
```

For each reel, write one line using this exact format:

```bash
# Replace all values with your actual numbers:
echo "DS [@breathofdatascience]: views=1200 saves=45 saves_rate=3.75% nonfollow_reach=62% DM_triggers=18 → RESULT: [STRONG/WEAK/DISTRIBUTION_STUCK/BODY_WEAK]" >> data/analytics/research_log.txt

echo "Life [@mistakenlyhuman]: views=800 saves=28 saves_rate=3.5% nonfollow_reach=55% DM_triggers=12 → RESULT: [STRONG/WEAK/DISTRIBUTION_STUCK/BODY_WEAK]" >> data/analytics/research_log.txt

echo "Poetry [@mistakenlyhuman]: views=500 saves=30 saves_rate=6% nonfollow_reach=48% → RESULT: [STRONG/WEAK/DISTRIBUTION_STUCK/BODY_WEAK]" >> data/analytics/research_log.txt
```

Also note:
- Which hook option did you use? (Hook 1, 2, or 3 from the `ig_reel_brief.md`)
- Did you complete the 2-hour engagement window? (Y/N)
- Did you do same-day cross-platform distribution? (Y/N)

These variables help you isolate what's working week over week.

---

### 1d. Read the automated insights file (after 8pm)

```bash
cat data/analytics/weekly_insights.md
```

Cross-reference with your manual notes above. If the automated insights show a short that blew up this week on YouTube — note the hook structure and add it to your weekly ideas for replication.

---

## Step 1e — What to carry forward into Monday

Based on the analytics check above, decide:

**Repeat → stronger:** Which hook style produced the best saves/views rate this week? Use the same structure (specific number / specific result / named moment) for the same niche next week.

**Kill → don't repeat:** Which topics or formats fell below 1.5% saves/views AND below 30% non-follower reach? Don't produce that format again until you understand why.

**Double down:** Any niche that hit > 5% saves/views rate this week gets a second piece next week if the topic backlog supports it.

Write this as a 3-line note at the bottom of `data/analytics/research_log.txt`:
```bash
echo "→ REPEAT next week: [hook style/format that worked]" >> data/analytics/research_log.txt
echo "→ KILL: [what failed]" >> data/analytics/research_log.txt
echo "→ DOUBLE DOWN: [niche/format to invest more in]" >> data/analytics/research_log.txt
```

---

## Step 1e-b — Spotify podcast analytics check (~5 min)

Go to [podcasters.spotify.com](https://podcasters.spotify.com) → select each show → Analytics.

**The one metric that matters most: episode completion rate.**
Spotify's recommendation algorithm is almost entirely driven by this. If listeners finish your
episodes, Spotify pushes you to similar listeners. If they drop at 30%, it stops.

**Check both shows — Breath of Life + Breath of Poetry:**

| Metric | Where | Target |
|--------|-------|--------|
| Streams | Overview → Streams | Growing week-over-week |
| Listeners | Overview → Listeners | Unique listeners (≠ streams) |
| Completion rate | Episode detail → Performance | **> 65%** |
| Followers gained | Audience → Followers | Any growth |
| Saves | Episode detail | Any saves = strong quality signal |

**Decision matrix:**

| Result | What it means | Action |
|--------|--------------|--------|
| Completion rate < 50% | Opener didn't hook or episode ran too long | Check the drop-off timestamp in Spotify analytics — that's exactly where you lost them. Fix the opening for next week. |
| Completion rate 50–65% | Passable — hook landed but pacing dragged | Tighten the middle third. Vary pace — slower for emotional beats, faster for transitions. |
| Completion rate > 65% | This episode's structure worked | Replicate the opening format next week (same hook style, same pacing). |
| Completion rate > 70% | Strong episode — Spotify will recommend it | Share this episode again on Instagram this week. It's your best acquisition tool. |
| Spike in followers after one episode | That episode is your top-of-funnel piece | Re-share it on Instagram (Story + audiogram post) and link it in the Medium bio. |
| Any saves | Strong quality signal | Note the episode topic/hook style — replicate it. |

**Log your results:**
```bash
echo "" >> data/analytics/research_log.txt
echo "SPOTIFY-Life: streams=X listeners=Y completion=Z% followers=+N saves=M → [STRONG/WEAK/OPENER_FAILED]" >> data/analytics/research_log.txt
echo "SPOTIFY-Poetry: streams=X listeners=Y completion=Z% followers=+N saves=M → [STRONG/WEAK/OPENER_FAILED]" >> data/analytics/research_log.txt
```

---

## Step 1f — LinkedIn analytics check (~5 min)

LinkedIn analytics are available in the app under your profile → Analytics, or in the Creator Analytics dashboard if Creator Mode is on.

**For each of the 3 LinkedIn posts that fired this week (Tuesday 8:00 AM IST):**

1. Go to the post → tap "X impressions" below the post text
2. Note these numbers:

| Metric | Where to find | Target |
|--------|--------------|--------|
| Impressions | Post analytics page | > 500 for a new account; > 2,000 for 500+ connections |
| Comments | Visible on post | > 5 comments = healthy; > 15 = algorithm is amplifying |
| Reposts | Visible on post | Even 1 repost = strong signal (someone vouched for you) |
| Reactions | Visible on post | "Insightful" and "Love" outweigh plain "Like" |
| Post link clicks | Post analytics page | > 20 = people are reading the blog |

**Decision matrix:**

| Result | What it means | Action |
|--------|--------------|--------|
| > 2,000 impressions + > 5 comments | Strong post, algorithm distributing | Repeat this post format and hook style next week |
| > 2,000 impressions + 0–2 comments | Good reach, weak engagement — hook landed but body didn't compel a response | End the post with a specific question next time ("Have you hit this? 👇") |
| < 500 impressions + any comments | Algorithm suppressed it — likely because the hook failed | Rewrite the first line using Tuesday's hook formula. Check: did you post the first comment with the blog link within 5 minutes? Did you edit the post within 2 hours? |
| > 5 reposts on any post | This post is spreading beyond your network | Immediately reply to anyone who reposted to build the relationship |

**Log your results:**
```bash
echo "LI-DS: impressions=X comments=Y reposts=Z clicks=W → [STRONG/WEAK/SUPPRESSED]" >> data/analytics/research_log.txt
echo "LI-Life: impressions=X comments=Y reposts=Z clicks=W → [STRONG/WEAK/SUPPRESSED]" >> data/analytics/research_log.txt
echo "LI-Poetry: impressions=X comments=Y reposts=Z clicks=W → [STRONG/WEAK/SUPPRESSED]" >> data/analytics/research_log.txt
```

---

## Step 1g — Twitter/X analytics check (~5 min)

Go to [analytics.twitter.com](https://analytics.twitter.com) or open each thread on Twitter and tap the chart icon under tweet 1.

**For each thread posted this week (Life Mon 1 PM, Poetry Fri 12 PM, DS when active):**

| Metric | Where to find | Target |
|--------|--------------|--------|
| Impressions | Tweet analytics | > 500 for a new account |
| Replies | Visible on tweet | > 3 replies = thread is resonating |
| Retweets | Visible on tweet | Even 1 retweet = amplification |
| Link clicks | Tweet analytics | > 10 = people are reading the blog |
| Profile visits | Tweet analytics | Spikes here = thread drove new audience interest |

**Decision matrix:**

| Result | What it means | Action |
|--------|--------------|--------|
| > 500 impressions + > 3 replies | Thread is working — hook and body both landed | Repeat this tweet 1 formula next week for the same niche |
| > 500 impressions + 0 replies | Impressions but no engagement — people saw it but didn't respond | Tweet 1 was too mild. Add a more direct question or more provocative claim. |
| < 200 impressions | Thread wasn't distributed — likely posted when you weren't active to engage | Only post threads when you have 60 minutes to engage immediately after |
| Any thread with > 5 retweets | Breakout — this topic/format has legs | Pin this thread to your profile (three dots → Pin). Write a follow-up thread on the same angle next week. |

**Did you do the 24-hour quote-retweet?** (from Friday Step 4 — quote-tweet your best-performing tweet 24 hours later)
- Yes → note whether it got additional engagement
- No → check if it's still within 48 hours; if so, do it now

**Log your results:**
```bash
echo "TW-Life: impressions=X replies=Y retweets=Z → [STRONG/WEAK/SUPPRESSED]" >> data/analytics/research_log.txt
echo "TW-Poetry: impressions=X replies=Y retweets=Z → [STRONG/WEAK/SUPPRESSED]" >> data/analytics/research_log.txt
echo "TW-DS: impressions=X replies=Y retweets=Z → [STRONG/WEAK/SUPPRESSED]" >> data/analytics/research_log.txt
```

---

## Step 2 — Read knowledge base (after 10pm, ~5 min)

```bash
cat data/kb/master_brief.md
```

**This is the primary input for Monday's topic picks.** It contains what's performing, under-served angles, hook patterns with high engagement, and what not to repeat. Read it Sunday night or Monday morning before picking topics.

---

## Step 3 — Sync ideas to Notion (~3 min)

```bash
python3 scripts/sync_ideas_to_notion.py --dry-run   # preview
python3 scripts/sync_ideas_to_notion.py             # sync
```

Pushes this week's `weekly_ideas.md` entries to Notion Contents DB as `Idea` rows.

---

## Step 4 — Verify scheduler (1 min)

```bash
launchctl list | grep contentmachine
tail -5 data/analytics/scheduler.log
sqlite3 data/scheduling.db \
  "SELECT COUNT(*) FROM posts WHERE status='pending' AND platform='linkedin'"
# Should be ≥ 3 (next week's LinkedIn posts)
```

If LinkedIn count = 0: run `python3 scripts/load_posts.py` on Monday.

---

## Step 5 — Evergreen teasers (optional, ~10 min)

The week's analytics surface which old pieces still pull. Turn a couple into teasers + backlinks
and post them by hand this week. Pick the back-catalogue winners from `weekly_insights.md`.

```bash
python3 scripts/teaser_from_published.py --url <youtube-or-medium-url> --dry-run   # preview
python3 scripts/teaser_from_published.py --urls urls.txt                            # batch
```

Output → `content/derivatives/{week}/{slug}/` (`*_teaser.txt` + `teasers.md` bundle), each with a
UTM backlink. Tag-existing instead: `--inject-link content/derivatives/{week}/{slug} --url <url>`.
Full reference: `docs/medium-repurposing-guide.md`.

---

## Checklist

**Spotify podcasts:**
- [ ] Breath of Life: completion rate checked + logged (target > 65%)
- [ ] Breath of Poetry: completion rate checked + logged (target > 65%)
- [ ] Follower changes noted for both shows
- [ ] Any saves on either show noted
- [ ] Drop-off timestamp checked if completion rate < 50%
- [ ] High-completion episode flagged for re-share if > 70%

**Instagram reels:**
- [ ] DS reel: saves ÷ views calculated, result logged (STRONG / WEAK / DISTRIBUTION_STUCK / BODY_WEAK)
- [ ] Life reel: saves ÷ views calculated, result logged
- [ ] Poetry reel: saves ÷ views calculated, result logged
- [ ] Non-follower reach % noted for all 3 reels
- [ ] DM trigger count checked in SuperProfile for DS + Life
- [ ] `research_log.txt` updated with this week's reel results

**LinkedIn:**
- [ ] DS post: impressions + comments + reposts logged
- [ ] Life post: impressions + comments + reposts logged
- [ ] Poetry post: impressions + comments + reposts logged
- [ ] First-comment with blog link was posted within 5 min of scheduler firing (Y/N)

**Twitter:**
- [ ] Life thread: impressions + replies + retweets logged
- [ ] Poetry thread: impressions + replies + retweets logged
- [ ] DS thread: impressions + replies + retweets logged
- [ ] 24-hour quote-retweet done for any thread with ≥ 3 replies
- [ ] Best thread of the week pinned to profile

**Carry-forward:**
- [ ] REPEAT / KILL / DOUBLE DOWN decision written to `research_log.txt` (covers all 3 platforms)
- [ ] `weekly_insights.md` read (after 8pm)
- [ ] `master_brief.md` read — ready for Monday topic picks
- [ ] Ideas synced to Notion
- [ ] Scheduler running, LinkedIn queue ≥ 3 pending
- [ ] (Optional) 1–2 evergreen teasers generated from back catalogue
