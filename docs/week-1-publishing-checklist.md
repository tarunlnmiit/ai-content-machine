# Week 1 Publishing Checklist
**Week: Jun 9–13, 2026**

---

## Schedule Reference

### Long-form, blogs, social

| Content | Platform | Day | Time IST |
|---------|----------|-----|----------|
| Life LinkedIn post | LinkedIn | Mon Jun 9 | 12 PM |
| Life Twitter thread | Twitter/X | Mon Jun 9 | 1 PM |
| IG carousel (Life) | Instagram | Tue Jun 10 | 8 AM |
| Life Video (long-form) + Blog + Newsletter | YouTube / Substack+Medium / Beehiiv | Tue Jun 10 | 2 PM |
| DS LinkedIn post | LinkedIn | Wed Jun 11 | 12 PM |
| DS Twitter thread | Twitter/X | Wed Jun 11 | 1 PM |
| IG carousel (DS) | Instagram | Wed Jun 11 | 8 AM |
| DS Video (long-form) + Blog + Newsletter | YouTube / Substack+Medium / Beehiiv | Thu Jun 12 | 6 PM |
| Poetry LinkedIn post | LinkedIn | Fri Jun 13 | 11 AM |
| Poetry Twitter thread | Twitter/X | Fri Jun 13 | 12 PM |
| Poetry Video (long-form) + Blog + Newsletter | YouTube / Substack+Medium / Beehiiv | Fri Jun 13 | 3 PM |

### Shorts — all niches (up to 14 per channel, 2/day Mon–Sun)

| Slot | Day | Time IST | DS | Life | Poetry |
|------|-----|----------|----|------|--------|
| 0 | Mon Jun 9 | 10 AM | short_00 | short_00 | short_00 |
| 1 | Mon Jun 9 | 8 PM | short_01 | short_01 | short_01 |
| 2 | Tue Jun 10 | 10 AM | short_02 | short_02 | short_02 |
| 3 | Tue Jun 10 | 8 PM | short_03 | short_03 ★ post-long-form | short_03 |
| 4 | Wed Jun 11 | 10 AM | short_04 | short_04 | short_04 |
| 5 | Wed Jun 11 | 8 PM | short_05 | short_05 | short_05 |
| 6 | Thu Jun 12 | 10 AM | short_06 | short_06 | short_06 |
| 7 | Thu Jun 12 | 9 PM | short_07 ★ post-long-form | short_07 | short_07 |
| 8 | Fri Jun 13 | 10 AM | short_08 | short_08 | short_08 |
| 9 | Fri Jun 13 | 8 PM | short_09 | short_09 | short_09 ★ post-long-form |
| 10 | Sat Jun 14 | 10 AM | short_10 | short_10 | short_10 |
| 11 | Sat Jun 14 | 8 PM | short_11 | short_11 | short_11 |
| 12 | Sun Jun 15 | 10 AM | short_12 | short_12 | short_12 |
| 13 | Sun Jun 15 | 8 PM | short_13 | short_13 | short_13 |

★ = first slot after the long-form goes live for that niche. Slots before ★ are standalone teasers. Slots after ★ should have the live video URL in their description (update retroactively via YouTube Studio if needed). Empty slots (no short_NN file) are skipped by the loop in STEP 2d.

---

## STEP 1 — Clean up duplicate shorts (if needed)

Check for duplicates created by old cp+clip commands:

```bash
ls "assets/video/edited/shorts/" | grep -E "2026-05-21-ds-complete-python|2026-05-21-life-habits|2026-05-21-poetry-when-dreams"
```

If anything shows up, delete:

```bash
find "assets/video/edited" \( \
  -name "2026-05-21-ds-complete-python-110*" \
  -o -name "2026-05-21-life-habits-engine*" \
  -o -name "2026-05-21-poetry-when-dreams*" \
) -delete
```

- [ ] Done / nothing to delete

---

## STEP 2 — YouTube uploads (queue all now, go live on schedule)

All videos upload as private and auto-publish at the `--publish-at` time.
Run from project root: `cd "/Users/tarungupta/Making It Big/Claude/content-machine"`

---

### STEP 2a — DS long-form (Thu Jun 12, 6 PM IST)

**Title options** — current title is browse/impressions optimised (curiosity hook).
For a new channel, search traffic matters more early on. Pick one:

| Option | Title | Best for |
|--------|-------|----------|
| A (current) | Why Your Python Setup Matters More Than Your First Code | Browse / suggested / CTR |
| B (search) | Python for Data Science 2026 — Setup & Foundations (Tutorial 1/10) | Search ranking |
| C (hybrid) | Python for Data Science Beginners 2026 — Stop Setting Up Wrong (Tutorial 1/10) | Both |
| D (problem) | The Python Setup Mistake That Kills Most Data Science Projects | High CTR, mid search |

Recommendation: **Option C** if channel has <5k subs. **Option A** if algorithm already suggests your videos.
Update `--title` in the command below before running.

```bash
DS_DESC=$(cat <<'EOF'
Most Python tutorials start with syntax. This one starts with setup — because bad environment setup is why most data science projects fail silently.

In this video (Tutorial 1/10):
- Why setup matters before syntax
- Virtual environments in 3 commands (Windows/Mac/Linux)
- Computational thinking: the mental model behind every program
- Your first real program using actual data structures
- How to read error messages as feedback, not failures

Timestamps:
0:00 Why Setup Matters
2:45 The Two Ways to Learn Python
5:15 Virtual Environment Setup (Windows/Mac/Linux)
8:30 Computational Thinking: The Mental Model
12:00 Your First Real Program (Code Walkthrough)
16:15 Reading Error Messages
19:00 What''s Next

This is Tutorial 1 of 10 in the Python for Data Science series.

Full breakdown + code: https://breathofdatascience.substack.com

Connect with me:
Twitter/X: https://twitter.com/mistakenlyhuman
Instagram: https://instagram.com/mistakenlyhuman
LinkedIn: https://www.linkedin.com/in/tarun-gupta-in/
Newsletter: https://breathofdatascience.substack.com

Other channels:
Life & Growth: https://youtube.com/@breathoflife_
Poetry: https://youtube.com/@breathofpoetry
EOF
)

python3 scripts/upload_youtube.py \
  --channel "Breath of Data Science" \
  --video "assets/hyperframes/2026-05-30_ds-2026-05-22_2026-05-21-data-science-tech-complete-python-course-2026-beg_yt-aug.mp4" \
  --title "Python for Data Science Beginners 2026 — Stop Setting Up Wrong (Tutorial 1/10)" \
  --description "$DS_DESC" \
  --tags "Python,DataScience,PythonTutorial,DataScienceTutorial,BeginnerPython,PythonForDataScience,MachineLearning,Programming,CodingForBeginners,PythonCourse,LearnPython,DataScience2026,PythonSetup,VirtualEnvironment,ComputationalThinking,PythonFundamentals,DataAnalysis,EnvironmentSetup,Python2026,DataScienceForBeginners,PythonBasics,TechTutorial,JupyterNotebook,DataScientist,PythonProjects,Coding" \
  --category 28 \
  --publish-at "2026-06-12T18:00:00+05:30"
```

- [x] Uploaded — https://youtu.be/XBw0vuzACuA · long_form_url written to DS metadata

---

### STEP 2b — Life long-form (Tue Jun 10, 2 PM IST)

```bash
LIFE_DESC=$(cat <<'EOF'
Your habits feel consistent but your big goals feel stuck. The problem isn't willpower — it's that your habits are disconnected from each other.

In this video:
- Why isolated habits fail even when you're consistent
- The 3-category structure that makes habits connect (foundation, work, reflection)
- How to use feedback loops to see which habits actually move the needle
- Why a well-built system requires less discipline, not more
- The iteration mindset that turns a routine into an engine

If you've read Atomic Habits and still feel stuck — this is the missing layer.

Full breakdown: https://thisisbreathoflife.substack.com

Connect with me:
Twitter/X: https://twitter.com/mistakenlyhuman
Instagram: https://instagram.com/mistakenlyhuman
LinkedIn: https://www.linkedin.com/in/tarun-gupta-in/
Newsletter: https://thisisbreathoflife.substack.com

Other channels:
Data Science: https://youtube.com/@breathofdatascience
Poetry: https://youtube.com/@breathofpoetry
EOF
)

python3 scripts/upload_youtube.py \
  --channel "Breath of Life" \
  --video "assets/hyperframes/2026-05-30_life-2026-05-21_life_self_dev_how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals-aug.mp4" \
  --title "How to Turn Your Habits Into a System That Actually Works" \
  --description "$LIFE_DESC" \
  --tags "Habits,Productivity,SystemsThinking,PersonalGrowth,GoalSetting,HabitTracking,SelfImprovement,Discipline,Momentum,HabitBuilding,BetterHabits,AtomicHabits,LifeSystems,PersonalDevelopment,MorningRoutine,HabitStacking,GrowthMindset,FocusAndProductivity,LifeHacks,SelfDevelopment,Motivation,TimeManagement,GoalAchievement,MindsetShift,DailyRoutine" \
  --category 22 \
  --publish-at "2026-06-10T14:00:00+05:30"
```

- [x] Uploaded — https://youtu.be/NxJdOjboY0M · long_form_url written to Life metadata

---

### STEP 2c — Poetry long-form (Fri Jun 13, 3 PM IST)

```bash
POETRY_DESC=$(cat <<'EOF'
There's a difference between someone who keeps you safe and someone who makes you feel alive. Real love is when those stop being a choice.

This is a poetry essay — a poem read slowly, then unpacked. The poem imagines the moment you picture someone being loved by your people. Your family. Your mama. And what that means.

What we explore:
- Why safety alone becomes a cage
- Why aliveness without safety is reckless
- The specific moment real integration happens
- What it means to dissolve in someone's arms and still feel more yourself

Read the full essay: https://breathofpoetry.substack.com

Connect with me:
Twitter/X: https://twitter.com/mistakenlyhuman
Instagram: https://instagram.com/mistakenlyhuman
LinkedIn: https://www.linkedin.com/in/tarun-gupta-in/
Poetry newsletter: https://breathofpoetry.substack.com

Other channels:
Data Science: https://youtube.com/@breathofdatascience
Life & Growth: https://youtube.com/@breathoflife_
EOF
)

python3 scripts/upload_youtube.py \
  --channel "Breath of Poetry" \
  --video "assets/hyperframes/2026-05-30_poetry-2026-05-22_2026-05-21-poetry-quotes-when-dreams-speak-of-love-aug.mp4" \
  --title "Safe and Alive: A Poetry Essay on Real Love" \
  --description "$POETRY_DESC" \
  --tags "Poetry,Love,PoetryEssay,SpokenWord,Relationships,Vulnerability,Intimacy,PoetryReading,EmotionalHealing,SelfDevelopment,Growth,PoetryLovers,WordsAboutLove,HealingPoetry,LovePoetry,RealLove,Attachment,EmotionalIntelligence,PoetryVideo,Mindfulness,InnerWork,LoveAndLife,PoetryChannel,SoulfulContent,Heartfelt" \
  --category 22 \
  --publish-at "2026-06-13T15:00:00+05:30"
```

- [x] Uploaded — https://youtu.be/EnvEEZhdcUg · long_form_url written to Poetry metadata

---

### STEP 2d — Shorts: all niches (up to 14 per channel, Mon Jun 9 – Sun Jun 15)

2 shorts per day per channel × 7 days = 14 max per niche. Upload all available shorts now; YouTube schedules them at the assigned times. Slots before the long-form are teasers (standalone). After the long-form is live, add the video URL to descriptions retroactively if needed.

**Slot → publish time mapping (same for all niches):**

| short_NN | Day | Time IST | ISO timestamp |
|----------|-----|----------|---------------|
| short_00 | Mon Jun 9 | 10 AM | `2026-06-09T10:00:00+05:30` |
| short_01 | Mon Jun 9 | 8 PM | `2026-06-09T20:00:00+05:30` |
| short_02 | Tue Jun 10 | 10 AM | `2026-06-10T10:00:00+05:30` |
| short_03 | Tue Jun 10 | 8 PM | `2026-06-10T20:00:00+05:30` |
| short_04 | Wed Jun 11 | 10 AM | `2026-06-11T10:00:00+05:30` |
| short_05 | Wed Jun 11 | 8 PM | `2026-06-11T20:00:00+05:30` |
| short_06 | Thu Jun 12 | 10 AM | `2026-06-12T10:00:00+05:30` |
| short_07 | Thu Jun 12 | 9 PM | `2026-06-12T21:00:00+05:30` |
| short_08 | Fri Jun 13 | 10 AM | `2026-06-13T10:00:00+05:30` |
| short_09 | Fri Jun 13 | 8 PM | `2026-06-13T20:00:00+05:30` |
| short_10 | Sat Jun 14 | 10 AM | `2026-06-14T10:00:00+05:30` |
| short_11 | Sat Jun 14 | 8 PM | `2026-06-14T20:00:00+05:30` |
| short_12 | Sun Jun 15 | 10 AM | `2026-06-15T10:00:00+05:30` |
| short_13 | Sun Jun 15 | 8 PM | `2026-06-15T20:00:00+05:30` |

---

#### DS shorts — @breathofdatascience

```bash
DS_SLUG="2026-05-21_data_science_tech_complete-python-course-2026-beginner-to-advance-tutorial-110"
DS_TIMES=(
  "2026-06-09T10:00:00+05:30"
  "2026-06-09T20:00:00+05:30"
  "2026-06-10T10:00:00+05:30"
  "2026-06-10T20:00:00+05:30"
  "2026-06-11T10:00:00+05:30"
  "2026-06-11T20:00:00+05:30"
  "2026-06-12T10:00:00+05:30"
  "2026-06-12T21:00:00+05:30"
  "2026-06-13T10:00:00+05:30"
  "2026-06-13T20:00:00+05:30"
  "2026-06-14T10:00:00+05:30"
  "2026-06-14T20:00:00+05:30"
  "2026-06-15T10:00:00+05:30"
  "2026-06-15T20:00:00+05:30"
)

i=0
for f in $(ls assets/video/edited/shorts/*data-science-tech*complete-python*short_*.mp4 2>/dev/null | sort); do
  python3 scripts/upload_youtube.py \
    --channel "Breath of Data Science" \
    --video "$f" \
    --shorts \
    --slug "$DS_SLUG" \
    --publish-at "${DS_TIMES[$i]}" \
    --pin-longform-comment
  ((i++))
done
```

- [ ] DS shorts uploaded — count matches `ls assets/video/edited/shorts/*data-science-tech*complete-python*short_*.mp4 | wc -l`

---

#### Life shorts — @breathoflife_

```bash
LIFE_SLUG="2026-05-21_life_self_dev_how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals"
LIFE_TIMES=(
  "2026-06-09T10:00:00+05:30"
  "2026-06-09T20:00:00+05:30"
  "2026-06-10T10:00:00+05:30"
  "2026-06-10T20:00:00+05:30"
  "2026-06-11T10:00:00+05:30"
  "2026-06-11T20:00:00+05:30"
  "2026-06-12T10:00:00+05:30"
  "2026-06-12T21:00:00+05:30"
  "2026-06-13T10:00:00+05:30"
  "2026-06-13T20:00:00+05:30"
  "2026-06-14T10:00:00+05:30"
  "2026-06-14T20:00:00+05:30"
  "2026-06-15T10:00:00+05:30"
  "2026-06-15T20:00:00+05:30"
)

i=0
for f in $(ls assets/video/edited/shorts/*life*habits-into-an-engine*short_*.mp4 2>/dev/null | sort); do
  python3 scripts/upload_youtube.py \
    --channel "Breath of Life" \
    --video "$f" \
    --shorts \
    --slug "$LIFE_SLUG" \
    --publish-at "${LIFE_TIMES[$i]}" \
    --pin-longform-comment
  ((i++))
done
```

- [ ] Life shorts uploaded — count matches `ls assets/video/edited/shorts/*life*habits-into-an-engine*short_*.mp4 | wc -l`

---

#### Poetry shorts — @breathofpoetry

```bash
POETRY_SLUG="2026-05-21_poetry_quotes_when-dreams-speak-of-love"
POETRY_TIMES=(
  "2026-06-09T10:00:00+05:30"
  "2026-06-09T20:00:00+05:30"
  "2026-06-10T10:00:00+05:30"
  "2026-06-10T20:00:00+05:30"
  "2026-06-11T10:00:00+05:30"
  "2026-06-11T20:00:00+05:30"
  "2026-06-12T10:00:00+05:30"
  "2026-06-12T21:00:00+05:30"
  "2026-06-13T10:00:00+05:30"
  "2026-06-13T20:00:00+05:30"
  "2026-06-14T10:00:00+05:30"
  "2026-06-14T20:00:00+05:30"
  "2026-06-15T10:00:00+05:30"
  "2026-06-15T20:00:00+05:30"
)

i=0
for f in $(ls assets/video/edited/shorts/*poetry*when-dreams-speak-of-love*short_*.mp4 2>/dev/null | sort); do
  python3 scripts/upload_youtube.py \
    --channel "Breath of Poetry" \
    --video "$f" \
    --shorts \
    --slug "$POETRY_SLUG" \
    --publish-at "${POETRY_TIMES[$i]}" \
    --pin-longform-comment
  ((i++))
done
```

- [ ] Poetry shorts uploaded — count matches `ls assets/video/edited/shorts/*poetry*when-dreams-speak-of-love*short_*.mp4 | wc -l`

---

## STEP 3 — Create Substack drafts (do this with Claude — do NOT publish yet)

Tell Claude: "Create Substack drafts for week 1 — DS, Life, Poetry. Save as draft."
Claude reads from `content/buffer/week-1/` and creates via MCP.
Publish manually at scheduled times (Tue 2 PM / Thu 6 PM / Fri 3 PM IST).

Sources:
- DS: `content/buffer/week-1/data_science_tech/complete-python-course-2026-beginner-to-advance-tutorial-110_substack_post.md`
- Life: `content/buffer/week-1/life_self_dev/how-i-turned-my-habits-into-an-engine_substack_post.md`
- Poetry: `content/buffer/week-1/poetry_quotes/when-dreams-speak-of-love_substack_post.md`

After publishing each Substack post, copy the live URL — needed for Medium in STEP 4.

- [ ] DS draft created on breathofdatascience.substack.com — publish Thu Jun 12, 6 PM IST
- [ ] Life draft created on thisisbreathoflife.substack.com — publish Tue Jun 10, 2 PM IST
- [ ] Poetry draft created on breathofpoetry.substack.com — publish Fri Jun 13, 3 PM IST

---

## STEP 4 — Publish to Medium (at scheduled time)

Run after each Substack post goes live. Use `--publication humans-are-stories` to target the publication, or omit it to publish to personal profile.

**Tue Jun 10, 2 PM — Life:**
```bash
python3 scripts/publish_medium.py \
  --input "content/blogs/2026-05-21_life_self_dev_how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals.md" \
  --canonical-url <live-life-substack-url> \
  --publication humans-are-stories \
  --status public
```

**Thu Jun 12, 6 PM — DS:**
```bash
python3 scripts/publish_medium.py \
  --input "content/blogs/2026-05-21_data_science_tech_complete-python-course-2026-beginner-to-advance-tutorial-110.md" \
  --canonical-url <live-ds-substack-url> \
  --publication humans-are-stories \
  --status public
```

**Fri Jun 13, 3 PM — Poetry:**
```bash
python3 scripts/publish_medium.py \
  --input "content/blogs/2026-05-21_poetry_quotes_when-dreams-speak-of-love.md" \
  --canonical-url <live-poetry-substack-url> \
  --publication humans-are-stories \
  --status public
```

- [ ] Life published to Medium (humans-are-stories) with canonical URL — Tue Jun 10, 2 PM IST
- [ ] DS published to Medium (humans-are-stories) with canonical URL — Thu Jun 12, 6 PM IST
- [ ] Poetry published to Medium (humans-are-stories) with canonical URL — Fri Jun 13, 3 PM IST

---

## STEP 5 — Initialize scheduler + load all posts

```bash
python3 scripts/db_setup.py
```

```bash
python3 scripts/load_posts.py
```

What `load_posts.py` does:
- **LinkedIn posts** → inserted into `data/scheduling.db`
- **Metricool CSVs** generated with:
  - Medium blog URLs auto-injected into captions: "Full post 👉 {url}"
  - Images auto-populated from `schedule.json` if available (skipped if missing)
- **Prompts** (if running interactively):
  - Blog URL per niche (Medium only — skips if found in `medium_posts.json`)
  - Image URL per post with local image (Google Drive/Dropbox public link)
  - Saves both to `schedule.json` for re-runs (idempotent)

Outputs:
- `data/scheduling.db` — LinkedIn posts queued
- `output/scheduled/metricool_mistakenlyhuman.csv` — Account 1: IG + Facebook + Threads (Life + Poetry)
- `output/scheduled/metricool_breathofds.csv` — Account 2: IG + Facebook + Threads (DS only)

```bash
python3 scripts/scheduler.py &
```

Verify running:
```bash
pgrep -f scheduler.py
```

- [ ] db_setup.py ran without errors
- [ ] load_posts.py ran — Metricool CSVs present in output/scheduled/
- [ ] scheduler.py daemon running (pgrep shows PID)

Verify LinkedIn posts are queued (3 rows expected — one per niche):

```bash
sqlite3 data/scheduling.db "SELECT slug, scheduled_at FROM posts WHERE platform='linkedin' AND status='pending' ORDER BY scheduled_at;"
```

- [ ] DS LinkedIn queued in scheduling.db
- [ ] Life LinkedIn queued in scheduling.db
- [ ] Poetry LinkedIn queued in scheduling.db

---

## STEP 6 — Import Metricool CSVs (week of Jun 16–20 — one week after long-forms)

> **Pivot:** social posts (IG, FB, Threads) publish the week AFTER YouTube/Substack/Medium.

Run `load_posts.py` first if CSVs not yet generated (STEP 5). CSVs schedule automatically to the correct dates (week_offset=1 baked in).

**Before import:** Check if images were populated in the CSVs:
```bash
python3 -c "import csv; r=list(csv.DictReader(open('output/scheduled/metricool_mistakenlyhuman.csv')))[0]; print(f'Has images: {r[\"Picture Url 1\"]}')"
```

If `Picture Url 1` is empty, you either skipped the prompt or ran non-interactively. Add image URLs manually in Metricool after import (Google Drive public link or Dropbox public link).

**Account 1 — mistakenlyhuman** (Life + Poetry: IG + Facebook + Threads):
1. Open Metricool → Planner → Import CSV
2. Import `output/scheduled/metricool_mistakenlyhuman.csv`

**Account 2 — Breath of Data Science** (DS: IG + Facebook + Threads):
3. Switch to Breath of DS brand in Metricool
4. Import `output/scheduled/metricool_breathofds.csv`

Blog URLs are already injected in captions ("Full post 👉 {url}"). Images populate automatically if saved to `schedule.json` during `load_posts.py` — add manually only if missing.

Scheduled dates in the CSVs:
- 🟢 Life IG/FB: **Tue Jun 17, 8 AM** · Threads: **Tue Jun 17, 8 PM**
- 🔵 DS IG/FB: **Wed Jun 18, 8 AM** · Threads: **Wed Jun 18, 8 PM**
- 🟣 Poetry IG/FB: **Fri Jun 20, 10 AM** · Threads: **Fri Jun 20, 12 PM**

- [ ] mistakenlyhuman Metricool CSV imported (Life + Poetry IG/FB + Threads)
- [ ] Breath of DS Metricool CSV imported (DS IG/FB + Threads)
- [ ] Verified images in CSVs or manually added to Metricool

---

## STEP 7 — Twitter threads (manual in Publer)

Source files: `content/derivatives/{slug}/twitter_thread.txt`

- DS: `content/derivatives/2026-05-21_data_science_tech_complete-python-course-2026-beginner-to-advance-tutorial-110/twitter_thread.txt`
- Life: `content/derivatives/2026-05-21_life_self_dev_how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals/twitter_thread.txt`
- Poetry: `content/derivatives/2026-05-21_poetry_quotes_when-dreams-speak-of-love/twitter_thread.txt`

Twitter threads publish the week AFTER the long-form (pivot rule). Schedule manually in Metricool or post directly.

- Life: **Mon Jun 16, 1 PM IST** *(recurring reminder set — fires every Monday)*
- DS: **Wed Jun 18, 1 PM IST** *(manual)*
- Poetry: **Fri Jun 20, 12 PM IST** *(recurring reminder set — fires every Friday)*

- [ ] Life Twitter thread posted — Mon Jun 16, 1 PM IST
- [ ] DS Twitter thread posted — Wed Jun 18, 1 PM IST
- [ ] Poetry Twitter thread posted — Fri Jun 20, 12 PM IST

---

## STEP 8 — Notion status updates

Run after each piece goes live:

```bash
python3 scripts/update_notion_status.py \
  --slug "complete-python-course-2026-beginner-to-advance-tutorial-110" \
  --status "Published" --publish-date "2026-06-12"
```

```bash
python3 scripts/update_notion_status.py \
  --slug "how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals" \
  --status "Published" --publish-date "2026-06-10"
```

```bash
python3 scripts/update_notion_status.py \
  --slug "when-dreams-speak-of-love" \
  --status "Published" --publish-date "2026-06-13"
```

- [ ] DS Notion status → Published
- [ ] Life Notion status → Published
- [ ] Poetry Notion status → Published

---

## Buffer note

After week 1 ships → 2 weeks remain (weeks 2+3). Need week 4 before next Saturday:
```bash
python3 scripts/generate_buffer.py --week 4
```
