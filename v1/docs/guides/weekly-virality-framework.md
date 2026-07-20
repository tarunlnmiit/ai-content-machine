---
title: "Weekly Virality Framework"
type: doc
slug: weekly-virality-framework
tags: [content/doc]
---
# Weekly Virality Framework
*End-to-end playbook for applying virality to every platform, every content type, every niche*

**How to use:** Run this document top to bottom on a week's draft content before anything is published or scheduled. Each section audits one platform. Each section has a worked example using W22 (2026-05-25 to 2026-06-01) as the reference — replace W22 content details with your current week.

**W22 content reference:**
- DS: `content/blogs/2026-W22/2026-05-25_data_science_tech_python-for-data-science-tutorial-210.md`
- Life: `content/blogs/2026-W22/2026-05-26_life_self_dev_mental-health-openness-and-breaking-stigmas.md`
- Poetry: `content/blogs/2026-W22/2026-05-27_poetry_quotes_intoxicated-senses.md`

**Full prompt library (read before running any section):**
- Medium: `prompts/medium-virality-prompt.md`
- YouTube: `prompts/youtube-virality-prompt.md`
- Podcast: `prompts/podcast-virality-prompt.md`
- Repurposing agent: `prompts/repurposing_agent.md`
- Reel formula (5-beat, reverse-engineered from 38k-view reel): `data/kb/viral_reel_formula.md`
- Twitter hook patterns: `data/kb/twitter_hook_patterns.json`
- Voice KB (Life/Poetry virality): `data/kb/voice/INDEX.md`
- Reels KB (DS/build-in-public virality): `data/kb/reels/INDEX.md`

---

## Platform virality targets — quick reference

| Platform | Primary metric | Target | Kill threshold |
|----------|---------------|--------|----------------|
| Medium | Read ratio | ≥ 40% curation zone, ≥ 50% curated | < 25% = rewrite title + first para |
| YouTube long-form | CTR + AVD | CTR ≥ 5%, AVD ≥ 50% | CTR < 2% = replace thumbnail |
| YouTube Shorts | Like/view ratio | ≥ 5%; avg viewed ≥ 80% | < 3% = recut hook |
| Instagram Reels | Saves ÷ views | ≥ 3%; shares ≥ 1% | 0 saves after 24h = boost or rework hook |
| Twitter | Replies + retweets | Thread: ≥ 5 replies; RT/impression ≥ 1% | No replies after 2h = hook failed |
| LinkedIn | Comments | ≥ 3 comments in first hour | 0 comments = rewrite hook |
| Podcast | Completion rate | ≥ 65% per episode | < 50% = opener didn't hook |

---

## Phase 0 — Pre-flight (15 min)

Run this before touching any content. Skipping this is how you repeat angles and miss obvious title improvements.

### 0a. Read the KB files

```bash
# Life/Poetry: read the voice KB index before any Life or Poetry content decisions
cat data/kb/voice/INDEX.md

# DS/build-in-public: read the reels KB index before any DS content decisions
cat data/kb/reels/INDEX.md
```

These files contain virality principles distilled from high-performing pieces in each niche. They update the algorithm in your head before you start applying it.

### 0b. Notion angle check

```bash
python3 scripts/query_notion_recent.py --days 90 --niche ds
python3 scripts/query_notion_recent.py --days 90 --niche life
python3 scripts/query_notion_recent.py --days 90 --niche poetry
```

Any angle published in the last 90 days is off the table. If this week's draft overlaps — reframe the angle, not the topic. "The type error that makes your analysis wrong without crashing" and "Python data types tutorial" are the same topic, different angles. One has CTR. The other doesn't.

### 0c. Confirm week

```bash
python3 -c "from scripts.lib.schedule_calc import get_iso_week; from datetime import date; print(get_iso_week(str(date.today())))"
```

Confirm the three blog files exist and slugs match:
```bash
python3 scripts/list_week_content.py {week} --plan
```

---

## Phase 1 — Medium Blog Virality

**Full framework:** `prompts/medium-virality-prompt.md`
**Performance data:** `data/analytics/medium-stats-2026.md`

Medium's distribution algorithm is driven by **read ratio** — the percentage of people who open and read to the end. Curation zone: ≥ 50%. Strong: 40–49%. Danger zone: < 25%.

Five levers on every article:
1. **Title** — creates tension AND signals clearly who it's for
2. **First paragraph** — passes the removal test (if paragraph 1 can be deleted without losing meaning, it's throat-clearing)
3. **Subheadings** — hooks that pull skimmers in, not section labels
4. **Quotable sentence** — the line a reader would highlight or DM to a friend
5. **Ending** — lands with weight; no summary, no "share this with someone who needs it"

### DS — Tutorial 2/10 virality audit

**Current title:** "Python for Data Science: Tutorial 2/10 — Variables, Data Types, and the Structures That Actually Matter"

**Problem:** "(Tutorial 2/10)" signals series commitment to cold readers. "Variables, Data Types, and the Structures That Actually Matter" is a description, not tension. Cold readers don't click descriptions — they click problems.

**Virality-optimized title:**
> "The Type Error That Makes Your Analysis Wrong Without Crashing"

Why this works: names a specific fear (silent wrong answer), contains a paradox (wrong without crashing), and implies the reader is vulnerable to this right now. Passes the "would I click this?" test even if I didn't know the author.

Backup title if publishing inside a series:
> "Python for Data Science #2 — The Bug That Gives Wrong Answers With No Error"

**First paragraph test:** The current hook passes — "Your analysis will give you a wrong answer someday. Not an error. Not a crash. A perfectly confident wrong number." Remove it and the piece loses its entire setup. Keep it exactly as written.

**Subheadings audit:**
- "The Four Primitives: What Python Actually Holds" → pass (specific, signals something to learn)
- "Lists: The Workhorse of Sequences" → borderline (informational, not a hook — improve to: "Why `[1:3]` Never Gives You What You Think")
- "Dictionaries: How Data Science Thinks About Records" → improve to: "Lists Give You Sequences. Dicts Give You Rows."
- "Functions: Writing Code You Can Actually Reuse" → pass (specific benefit)

**Quotable sentence:**
> "Every silent bug in data analysis traces back to the same root: the programmer didn't understand what kind of thing they were holding."

Mark this `[QUOTABLE]` in the draft. This is the line for the Twitter quote-tweet, Instagram carousel frame 2, and the LinkedIn post pull-quote.

**Ending check:** Current ending — "Tutorial 3 brings NumPy — these structures scale to millions of rows." — is a teaser, not a landing. Add one weight-bearing line before the teaser:
> "Every pipeline you'll ever build rests on these four things. Not the libraries. These."
> Tutorial 3 brings NumPy — where these structures scale to millions of rows.

**Tags (Medium):** Python · Data Science · Programming · Tutorial · Machine Learning

**Publication to submit:** Towards Data Science (TDS) — submit this article; it's a clear TDS fit. Instructions: `prompts/medium-virality-prompt.md` → "Publications" section.

---

### Life — Mental Health virality audit

**Current title:** "The Lie We Inherited About Strength" — **keep this**. It passes every test: names a specific claim (inherited), contains tension (lie), signals a niche (strength/mental health). Read ratio prediction: 42–48%.

**First paragraph test:** "Break a bone, and people sign your cast. Tell someone you haven't slept in three weeks because your chest feels like it's caving in — and the room goes quiet." — passes. Vivid, specific contrast, personal. Do not touch.

**Subheadings audit:**
- "Why We'll Admit a Sprained Ankle Before We Admit We're Drowning" → strong (names the exact behavior)
- "The Therapy Misconception That's Quietly Destroying People" → strong (specific threat)
- "The Specific Weight Men Are Carrying" → weaken (vague "weight"). Improve: "Why Men's Silence Has a Different Kind of Lethality"
- "What Breaking the Silence Actually Looks Like" → acceptable

**Quotable sentence:**
> "We hand someone drowning a map of the shoreline instead of a rope."

This is the sentence. Mark `[QUOTABLE]`. Use on: Twitter single tweet, Instagram caption, LinkedIn pull-quote. It's short, visual, and exact.

**Second quotable (backup):**
> "Strength that requires silence is just brittleness waiting for the right amount of pressure."

**Ending check:** Current ending is strong — "The wall of silence doesn't fall in one motion. But it's already cracking — every time one of us chooses honesty over the performance of being fine." Keep it. Don't add anything.

**Tags (Medium):** Mental Health · Self Improvement · Men's Mental Health · Psychology · Personal Development

**Publication to submit:** The Ascent or P.S. I Love You. The Ascent for the growth angle; P.S. I Love You for the emotional vulnerability angle. Both are strong fits.

---

### Poetry — Intoxicated Senses virality audit

**Current title:** "The Hangover That Won't Lift" — strong. Specific metaphor, names a duration (won't lift), implies the reader knows this feeling. Keep.

**Format check:** Now in minimal format (hook + poem + 2-line close). ✅

**Hook check:** "There's a specific kind of madness that doesn't announce itself. One day you're fine. The next, someone's laugh is living rent-free in your head..." — passes. Names the exact sensation.

**Close check:** "The hangover metaphor works because it has an endpoint. This doesn't." — one observation, no summary, no lesson. ✅

**Quotable from the poem:**
> "leaving me without a ground to stand on / or a sky to cover my head with"

Use this as the Instagram caption, Twitter excerpt, and YouTube Short overlay text.

**Tags (Medium):** Poetry · Love · Mental Health · Creative Writing · Relationships

**Publication:** P.S. I Love You. Submit after publishing to personal profile.

---

### Medium checklist — run before publishing

```bash
# DS + Life:
# [ ] Title creates tension AND signals who it's for
# [ ] First paragraph passes removal test
# [ ] [QUOTABLE] sentence marked in draft
# [ ] Subheadings are hooks, not labels (not descriptions)
# [ ] Ending lands — no summary, no "share this"
# [ ] Tags: 5 filled (first tag is most weighted)
# [ ] Publication submission queued (DS → TDS, Life → The Ascent or P.S. I Love You)

# Poetry (minimal format — different rules):
# [ ] Format: hook (2–3 lines) → poem as blockquotes → close (1–2 lines) → podcast CTA
# [ ] Hook names a specific sensation — NOT a topic description
# [ ] Close is one honest observation — no lesson, no takeaway, no reflection section
# [ ] NO subheadings (minimal format has none — don't add them)
# [ ] Tags: 5 filled (Poetry, Love, Mental Health, Creative Writing, Relationships)
# [ ] Publication submission queued → P.S. I Love You
```

---

## Phase 2 — YouTube Long-Form Virality

**Full framework:** `prompts/youtube-virality-prompt.md`

Primary YouTube metrics: **CTR** (target ≥ 5%) and **AVD** (target ≥ 50%). These two metrics control distribution. Non-subscriber views ≥ 40% of total views indicates the algorithm is pushing you beyond your existing audience — this is the breakout signal to watch for.

The thumbnail and title determine CTR. The first 30 seconds determine whether CTR becomes watch time or bounce. The pattern interrupt at 2–3 minutes is the AVD cliff — this is where most channels lose 40% of viewers.

### DS — Tutorial 2/10

**Title (virality-optimized):**
> "Python Gave Me a Wrong Answer With No Error (Here's Why)"

Why: front-loads the anomaly ("wrong answer with no error"), makes viewer ask "wait, how?" — that question is the click. Avoid "(Tutorial 2/10)" in title — it signals series entry cost. Put it in description and pinned comment instead.

Alternative if you want to keep series numbering visible:
> "#2 — The Python Bug That Gives Wrong Numbers Silently"

**Thumbnail brief:**
- Hook text: "NO ERROR. WRONG NUMBER." (two lines, white on dark navy)
- Face: confused/frustrated expression — looking at screen with furrowed brow
- Screen element: show `"2835"` in big text on a monitor (the concatenated "answer")
- Accent color: orange warning indicator in corner
- Generate: `python3 scripts/generate_thumbnail.py --niche ds --hook "NO ERROR. WRONG NUMBER." --slug python-for-data-science-tutorial-210 --week 2026-W22 --canva`

**Hook (first 30 seconds) — exact script:**
```
OPEN ON: Terminal or IDE — type this live as you say it:
"I'm going to show you a Python script that runs perfectly, produces no errors, and gives you a completely wrong answer."
[RUN the code — show "2835" output]
"The column was labeled 'age'. I summed it. Python reported a number. I moved on.
Except the column was stored as strings — Python didn't add 28 + 35 + 42. It concatenated them."
[Show: "2835" highlighted, then show what 28+35+42 should be: 105]
"No error. No warning. A number plausible enough to fool you — and anyone reading your report."
"Tutorial 2 is about exactly this: the invisible layer that decides whether your data science code is actually correct."
```

**Pattern interrupt at 2–3 min (AVD cliff):**
At the transition from primitives to lists, insert a live demo interruption:
```
"Before we move to lists — let me show you the exact moment this bit me in a real project."
[Switch to a real notebook, show a simplified version of a string-sum bug in a dataset]
"This is why type-checking is not optional for data scientists."
[Zoom in on the wrong output, then the fix]
```
This is a perspective shift (theory → real failure) that resets viewer attention.

**End screens:**
- At 0:20 before end: show Tutorial 3/10 card — "Next: NumPy — where these structures scale to a million rows."
- Subscribe button: appears at 0:45
- Say out loud: "Tutorial 3 drops [day]. Subscribe so you don't miss the part where this all snaps together."

**Description formula:**
```
The type error that produces a wrong answer with no crash — and how to catch it.

In this tutorial:
0:00 — The silent bug that fools your analysis
2:15 — The four Python primitives every data scientist uses
8:30 — Lists: sequences, slicing, comprehensions
16:40 — Dictionaries: from single records to full datasets
24:10 — Functions: writing reusable analysis code
30:00 — Real pipeline example using all four

📄 Full write-up: medium.com/@tarun-gupta/[slug]
📊 Free worksheet: [worksheet URL from inject_worksheet_ctas.py]
🔔 Tutorial 1: [URL] | Tutorial 3: coming [date]

This is Tutorial 2 of a 10-part Python for Data Science series built for people who want to understand what their code is actually doing.

#Python #DataScience #PythonTutorial #DataAnalysis
```

**Tags:** Python, Data Science, Python Tutorial, Python for beginners, data types Python, Python lists, Python dictionaries, Python functions, data science tutorial, learn Python

---

### Life — Mental Health blog

**Title (virality-optimized):**
> "I White-Knuckled Life for 3 Years. Here's What I Was Actually Running From."

Why: "I white-knuckled" is a confession (builds trust), "here's what I was actually running from" promises a reveal — the viewer wants to know what it was. Emotional and specific.

Alternative:
> "The Lie About Strength That's Keeping Men Silent"

**Thumbnail brief:**
- Hook text: "I STOPPED SAYING I'M FINE"
- Face: direct, honest eye contact — not performed vulnerability, just direct
- Background: warm dark tones, single person
- Accent: coral #E8705A
- Generate: `python3 scripts/generate_thumbnail.py --niche life --hook "I STOPPED SAYING I'M FINE" --slug mental-health-openness-and-breaking-stigmas --week 2026-W22 --canva`

**Hook (first 30 seconds):**
```
"Break a bone, and people sign your cast."
[pause — let it land]
"Tell someone you haven't slept in three weeks because your chest feels like it's caving in — and the room goes quiet."
[pause]
"Or worse: 'Have you tried going outside more?'"
[direct to camera]
"I'm going to talk about the thing we inherited about strength — the definition that's quietly destroying people — and what it actually looks like to build something different."
```

**Pattern interrupt at 2–3 min:**
Transition from the structural/historical framing to personal confession:
```
"For years, I white-knuckled it."
[shift closer to camera, lower energy]
"Passive-aggressive in meetings. Rude to people I cared about. Waking at 3 AM in mental loops I couldn't switch off. I told myself that was the cost of ambition."
"It wasn't. It was a person who needed help and had no framework for asking for it."
```
Perspective shift: from sociology to personal admission. This is where viewers stop scrolling.

**End screens:** No series — end with: "Every week I write about the parts of life we usually talk around. Subscribe if you want honest self-development, not motivational content."

**Description formula:**
```
The definition of strength we inherited — and why it's costing people their lives.

0:00 — The broken bone vs. the caving chest
4:00 — Why stigma isn't malicious — it's inherited
10:20 — The night I called my parents and got budgeting advice
17:00 — The trainer/therapist paradox
22:30 — What vulnerability actually looks like in practice
28:00 — One conversation at a time

📄 Full piece: medium.com/@tarun-gupta/the-lie-we-inherited-about-strength
🎙️ Podcast version: Breath of Life on Spotify → [URL]

#MentalHealth #MensMentalHealth #SelfDevelopment #Stigma #Vulnerability
```

---

### Poetry — Intoxicated Senses

**Title:**
> "The Hangover That Won't Lift | Intoxicated Senses (spoken word)"

Format: [emotional descriptor] | [poem title] | (spoken word) — this signals the genre to the algorithm and to potential viewers browsing spoken word content.

Alternative:
> "When Love Starts Feeling Like Physics (spoken word poem)"

**Thumbnail brief:**
- Hook text: "LOVE HAS TAKEN AWAY MY SENSES"
- Face: contemplative, lyrical — not sad, more internally absent
- OR atmospheric AI portrait if no face photo yet (editorial style, golden tones)
- Background: dark, soft blur
- Accent: golden #B89850
- Generate: `python3 scripts/generate_thumbnail.py --niche poetry --hook "LOVE HAS TAKEN AWAY MY SENSES" --slug intoxicated-senses --week 2026-W22 --canva`

**Hook (first 30 seconds):**
```
[Direct to camera, slow delivery]
"There's a specific kind of madness that doesn't announce itself."
[pause — 2 seconds]
"One day you're fine. The next, someone's laugh is living rent-free in your head —
and the part of your brain that's supposed to run the show has quietly handed over the keys."
[slow transition — begin poem]
"This is Intoxicated Senses."
[begin reading]
```

**Pattern interrupt:** Poetry videos are shorter — the pause between the hook and the poem IS the pattern interrupt. Hold 1–2 seconds of silence before the first line. Silence is the pattern interrupt in spoken word.

**End screen:**
- At 0:10 before end: show subscribe button
- Say out loud: "Follow Breath of Poetry for new poems every week."
- No series card — Poetry doesn't use series numbering.

**Description:**
```
There's a specific kind of madness that doesn't announce itself. This is a reading of "Intoxicated Senses" — a poem about the hangover love leaves behind.

📄 Full poem: medium.com/@tarun-gupta/the-hangover-that-wont-lift
🎙️ Podcast version: Breath of Poetry → [URL]

#SpokenWord #Poetry #Love #Poem #SpokenWordPoetry
```

**Tags:** Spoken word, Poetry, Love poem, Spoken word poetry, Poem reading, Poetry reading, Intoxicated senses, Breath of Poetry, love and loss, emotional poetry

---

### YouTube long-form checklist

```
# Per video, confirm before uploading:
# [ ] Title front-loads the hook (pain, anomaly, or confession in first 4 words)
# [ ] Thumbnail: face visible, hook text ≤ 5 words, passes thumbnail-replacement-backlog.md checklist
# [ ] First 30s: hook delivered, no "welcome to my channel," viewer knows what they'll get
# [ ] Pattern interrupt scripted at 2–3 min mark
# [ ] End screen: series teaser voiced aloud (DS) or subscribe prompt voiced aloud (Life/Poetry)
# [ ] Description: timestamps present (DS/Life — skip for Poetry, video IS the poem), Medium link
# [ ] Description: worksheet link present (DS/Life only); podcast link present (Life/Poetry only)
# [ ] Tags: 8–10 filled (DS/Life) or 10 filled (Poetry), first tag is primary keyword
```

---

## Phase 3 — Shorts + Reels Virality

**Full formula:** `data/kb/viral_reel_formula.md` (5-beat structure, reverse-engineered from 38k-view reel)
**Hook patterns:** `data/kb/twitter_hook_patterns.json` (applies to Short hooks too)

Every Short runs the 5-beat structure:
1. **Hook (0–3s):** Text overlay + spoken hook. Must force a stop. No greeting, no context-setting.
2. **Problem (3–15s):** Expand the problem or paradox introduced in the hook.
3. **Reveal + proof (15–35s):** The specific insight or demonstration. The "oh" moment.
4. **Payoff (35–50s):** The implication or resolution. What the viewer walks away knowing.
5. **CTA (50–60s):** One ask. Series (DS), follow (all), or "full piece in bio" (Life/Poetry).

**Three mandatory text overlays** (burns into every Short):
- Overlay 1 (0–3s): The hook in 3–5 words. High contrast on screen.
- Overlay 2 (~20s): The key insight in one line. Appears at the "reveal" beat.
- Overlay 3 (~50s): The CTA. "Full post in bio" or "@breathofdatascience" or series number.

### DS Short — The Type Error Bug

**Format:** Screen recording (show the code live)

**5 beats:**
```
[0–3s] TEXT OVERLAY: "PYTHON IS LYING TO YOU"
Spoken: "Python just gave me the wrong answer. Perfectly. With no error."
[Show: print("28" + "35") → "2835"]

[3–15s] TEXT OVERLAY: "THIS IS HOW BAD DATA SCIENCE HAPPENS"
Spoken: "This column is labeled 'age'. I summed it. Python reported a number. I moved on.
Except it was stored as strings — Python didn't add 28 + 35. It concatenated them."
[Show: "2835" — wrong. Then show: 28 + 35 = 63 — right.]

[15–35s] TEXT OVERLAY: "USE type() TO CATCH IT"
Spoken: "Here's how to catch this before it ruins a report."
[Show: type("28") → str; int("28") + int("35") → 63]
"Any data from a CSV arrives as a string until you convert it. Always."

[35–50s] TEXT OVERLAY: "type() IS NOT OPTIONAL IN DATA SCIENCE"
Spoken: "Every silent bug I've ever shipped traced back to this: not knowing what type I was holding."

[50–60s] TEXT OVERLAY: "Tutorial 2 → link in bio"
Spoken: "Tutorial 2 covers this and the three structures every data pipeline uses. Link in bio."
```

**Caption (Instagram/YouTube):**
```
Python gave me the wrong answer. No error. No warning. Just a confident lie.

The bug: CSV column labeled "age" stored as strings. Python didn't add 28 + 35. It concatenated: "2835".

This is why type() isn't optional. From Tutorial 2 of my Python for Data Science series.

Tutorial 1 → Tutorial 2 → link in bio. Next: NumPy.

#Python #DataScience #PythonTips #LearnPython #CodingMistakes
```

**Loop signal:** End frame shows the code output `"2835"` — this triggers the viewer to replay to understand how it happened. The unresolved confusion at the start is what creates the loop.

---

### Life Short — The Trainer/Therapist Paradox

**Format:** Talking head, direct camera

**5 beats:**
```
[0–3s] TEXT OVERLAY: "THERAPIST = PERSONAL TRAINER"
Spoken: "Nobody mocks you for hiring a personal trainer to get physically stronger."

[3–15s] TEXT OVERLAY: "BUT MENTION A THERAPIST..."
Spoken: "Mention a therapist and suddenly you're 'not strong enough to handle your own life.'
Same logic. Same structure. Completely different social response.
That inconsistency tells you exactly where the stigma lives."

[15–35s] TEXT OVERLAY: "INHERITED. NOT EARNED."
Spoken: "We inherited this. 'Real men don't cry.' 'Therapy is for people who can't cope.'
These scripts got reinforced in living rooms and locker rooms until nobody noticed them anymore.
But they have a cost."

[35–50s] TEXT OVERLAY: "SILENCE ≠ STRENGTH"
Spoken: "Strength that requires silence is just brittleness waiting for the right amount of pressure."

[50–60s] TEXT OVERLAY: "Full piece → link in bio"
Spoken: "Full piece is called 'The Lie We Inherited About Strength.' Link in bio."
```

**Caption:**
```
Nobody mocks you for hiring a personal trainer. But mention a therapist — suddenly you're "not strong enough."

Same logic. Completely different social response.

That inconsistency is exactly where the stigma lives.

"Strength that requires silence is just brittleness waiting for the right amount of pressure."

Full piece: The Lie We Inherited About Strength → link in bio.

#MentalHealth #MensMentalHealth #Therapy #SelfDevelopment #BreakTheStigma
```

**Loop signal:** End on the quotable line — "Strength that requires silence is just brittleness..." — leave it hanging. No resolution. Viewer replays to capture the quote.

---

### Poetry Short — Intoxicated Senses

**Format:** Talking head + B-roll (atmospheric — moth near flame, waves, etc.)

**5 beats (this niche uses poetry's natural rhythm as the beat structure):**
```
[0–3s] TEXT OVERLAY: "A MADNESS THAT DOESN'T ANNOUNCE ITSELF"
Spoken (to camera): "There's a specific kind of madness that doesn't announce itself."
[pause — 2 full seconds]

[3–15s] TEXT OVERLAY: "SOMEONE'S LAUGH LIVING RENT-FREE"
Spoken: "One day you're fine. The next, someone's laugh is living rent-free in your head —
and the part of your brain that's supposed to run the show has quietly handed over the keys."

[15–35s] TEXT OVERLAY: "LEAVING ME WITHOUT A GROUND TO STAND ON"
Read poem: "Love has taken away / all my senses / like that of alcohol /
effects of booze reside for a short period / but your intoxication / doesn't want to go away —"
[B-roll: moth near candle, slow motion]

[35–50s] TEXT OVERLAY: "OR A SKY TO COVER MY HEAD WITH"
Continue: "leaving me without a ground to stand on / or a sky to cover my head with"
[Hold on B-roll: waves, shore]

[50–60s] TEXT OVERLAY: "follow for more · Breath of Poetry"
Spoken: "This is Breath of Poetry. Follow if this stayed with you."
```

**Caption:**
```
"leaving me without a ground to stand on
or a sky to cover my head with"

— Intoxicated Senses

There's a specific kind of intoxication that doesn't schedule a checkout time.

Full poem → link in bio. Also a podcast on Spotify (Breath of Poetry).

#SpokenWord #Poetry #Love #SpokenWordPoetry #Poem
```

**Loop signal:** Poetry Shorts loop naturally — the emotional ambiguity at the end ("or a sky to cover my head with") is unresolved. Viewer replays for the feeling, not the information.

---

### Shorts/Reels checklist

```
# Per Short, confirm before posting:
# [ ] Hook overlay text appears in first 3 seconds
# [ ] No greeting, no "hey guys," no context before the hook
# [ ] 3 mandatory text overlays present (hook, key insight, CTA)
# [ ] 5-beat structure followed (hook → problem → reveal → payoff → CTA)
# [ ] Caption: starts with hook (not a description of the video), ends with CTA
# [ ] Loop signal present: unresolved question, quote, or visual that earns a replay
# [ ] Tags: 5 hashtags maximum; first 2 are primary niche tags
```

---

## Phase 4 — Twitter/X Virality

**Hook patterns:** `data/kb/twitter_hook_patterns.json` — load this before writing any thread.
**Platform constraint:** Twitter threads and polls CANNOT be scheduled — must post manually.

Twitter virality is almost entirely driven by the first tweet. If the first tweet doesn't get engagement in the first 2 hours, the thread dies. The hook tweet must force a reply or retweet before the user reads anything else.

Hook tweet formulas that work (from `data/kb/twitter_hook_patterns.json`):
- Counterintuitive claim: "Python is about to give you a perfectly wrong answer. No error. No warning."
- Specific personal failure: "I shipped a data science report with a wrong number that Python generated without crashing."
- Emotional precision: "We hand someone drowning a map of the shoreline instead of a rope."
- Paradox: "Nobody mocks you for hiring a trainer. Mention a therapist and suddenly you're weak."

### DS — Tutorial 2/10 thread

**Thread structure (8 tweets):**
```
Tweet 1 (HOOK):
Python is about to give you a perfectly wrong answer.

No error.
No warning.
Just a confident lie.

Here's the silent bug that fools every beginner's analysis: 🧵

---

Tweet 2 (THE BUG):
You load a CSV with an "age" column.
You sum it.
Python reports a number.
You move on.

Except the column was stored as strings.

Python didn't add 28 + 35 + 42.
It concatenated them: "283542"

No error. Wrong answer.

---

Tweet 3 (THE DEMONSTRATION):
>>> print("28" + "35")
"2835"

Not 63. 

Python treats string "28" completely differently from integer 28.
This is type behavior — and it trips up every data scientist.

---

Tweet 4 (THE FIX):
Two lines that fix this forever:

print(type(raw_value))  → <class 'str'>
age = int(raw_value)    → now it adds correctly

Rule: any data from a CSV, API, or user input arrives as a string until you explicitly convert it.

---

Tweet 5 (DEEPER):
The four conversion functions you'll use constantly:

int("42")     → 42
float("42.5") → 42.5
str(42)       → "42"
bool(0)       → False (0, "", [] all evaluate False)

---

Tweet 6 (INSIGHT):
This is why senior data scientists type-check at ingestion, not after analysis.

Finding a type bug after the report is in front of stakeholders is very different from finding it in the first 5 lines.

Build the habit early.

---

Tweet 7 (BROADER):
Every silent bug in data analysis traces back to the same root:

The programmer didn't know what kind of thing they were holding.

Types encode intention. Once you see this, you can't unsee it.

---

Tweet 8 (CTA):
This is covered in depth (with lists, dicts, functions) in Tutorial 2 of my Python for Data Science series.

10 tutorials. Real analysis code. No fluff.

Tutorial 2 → [Medium link]
Tutorial 1 (if you missed it) → [Medium link]
```

**Posting note:** Post manually. Reply to Tweet 1 with Tweet 2, and so on — threads must be built by replying, not scheduling.

---

### Life — Mental Health thread

**Thread structure (6 tweets):**
```
Tweet 1 (HOOK):
Break a bone and people sign your cast.

Say you haven't slept in 3 weeks because your chest feels like it's caving in —

and the room goes quiet.

Or worse: "Have you tried going outside more?"

🧵 On the lie we inherited about strength.

---

Tweet 2 (THE MECHANISM):
Mental health stigma isn't individual cruelty.

It's inherited. Passed down like outdated furniture nobody uses but nobody throws away.

"Real men don't cry."
"Therapy is for people who can't handle life."

These scripts got reinforced until they became wallpaper nobody notices anymore.

---

Tweet 3 (PERSONAL):
For years, I white-knuckled it.

Passive-aggressive in meetings. Rude to people I cared about. Waking at 3 AM running mental loops I couldn't switch off.

I told myself that was just the cost of ambition.

It wasn't. It was a person who needed help and had no framework for asking for it.

---

Tweet 4 (THE PARADOX):
Nobody mocks you for hiring a personal trainer to get physically stronger.

Mention a therapist and suddenly you're "not strong enough to handle your own life."

Same logic. Same structure.

Completely different social response.

---

Tweet 5 (THE QUOTABLE):
We hand someone drowning a map of the shoreline instead of a rope.

Not because we're cruel. Because we were never taught to hold the rope.

---

Tweet 6 (CTA):
The definition of strength we inherited is broken.

The version worth building is different — it says "I'm not okay" without treating that as defeat.

Full piece: "The Lie We Inherited About Strength" → [Medium link]
```

---

### Poetry — Intoxicated Senses

Poetry on Twitter works best as a single standalone tweet (the poem excerpt) or a very short thread (hook → poem → one reflection). Long poetry threads lose people.

**Single tweet (preferred):**
```
"leaving me without a ground to stand on
or a sky to cover my head with"

There's a specific kind of intoxication that doesn't schedule a checkout time.

— Intoxicated Senses

Full poem → [Medium link]
```

**Alternative (2-tweet thread):**
```
Tweet 1:
There's a specific kind of madness that doesn't announce itself.

One day you're fine. The next, someone's laugh is living rent-free in your head.

This poem is about that hangover.

---

Tweet 2:
"Love has taken away
all my senses
like that of alcohol —

leaving me without a ground to stand on
or a sky to cover my head with"

Intoxicated Senses → [Medium link]
```

---

### Twitter checklist

```
# [ ] Hook tweet contains a counterintuitive claim, paradox, or emotional precision line
# [ ] No thread starts with "Hey everyone" or "A thread on X:"
# [ ] Threads and polls noted for manual posting (cannot schedule)
# [ ] Reply to own tweet to build thread — do not use scheduling tool for thread structure
# [ ] Poetry: single tweet or 2-tweet max (not a full thread)
# [ ] First tweet posted in the engagement window (≥ 3 replies to other accounts in the 10 min before)
```

---

## Phase 5 — LinkedIn Virality

**Platform constraint:** LinkedIn poll options max 30 characters each. LinkedIn is held **manual until employer clearance** (staged in `scheduling.db`, daemon off).

LinkedIn distributes based on early comments. The algorithm shows your post to a small batch first — if that batch engages in the first hour, it gets shown to more. The hook line must force a comment or reaction before the reader reaches the second line.

Hook formulas that work on LinkedIn:
- Personal failure confession: "I built a 12-page analytics report. The answer was wrong. Python never complained."
- Counterintuitive professional claim: "The best data scientists I know don't have complex systems. They have simple habits they never skip."
- Specific professional paradox: "Nobody questions you for hiring a personal trainer. Mention a therapist and you lose professional credibility."

### DS — Tutorial 2/10 LinkedIn post

```
I built an analytics report that was completely wrong.

Python never said a word.

The column was labeled "age." I summed it. Python returned a number. I moved on.

Except the values were stored as strings. Python didn't add 28 + 35. It concatenated: "2835".

No error. No crash. Just a plausible-looking wrong answer waiting to embarrass me in front of a stakeholder.

This is the silent bug that traps every beginner data scientist — and most intermediate ones.

The fix is two lines:
• print(type(your_column))
• cast explicitly: int(value), float(value)

Rule: anything from a CSV, API, or user input arrives as a string until you convert it. Always.

Tutorial 2 of my Python for Data Science series covers this in full — plus lists, dictionaries, and functions. The three structures that make up 90% of what data scientists actually write before they open Pandas.

Link in bio. Tutorial 3 drops [date].

What's the worst silent bug you've ever shipped? I'll start: this exact one, in a client-facing engagement report. 🙃
```

**Notes:** End with a question that invites comments. This is what triggers LinkedIn's distribution expansion. The question must be easy to answer honestly — not "what do you think?" but "what's YOUR worst silent bug?"

---

### Life — Mental Health LinkedIn post

```
Nobody mocks you for hiring a personal trainer to get stronger.

Mention a therapist and suddenly you're "not strong enough to handle your own life."

Same logic. Same structure.

Completely different social response.

That inconsistency doesn't happen randomly. It's inherited — passed down through workplaces and living rooms until it became invisible. But the cost isn't invisible. Globally, men die by suicide at significantly higher rates than women. That's the downstream result of a long chain of "I'm fine."

I spent years white-knuckling it. The kind of exhaustion that isn't physical. The 3 AM mental loops that go nowhere. I told myself that was just ambition.

It wasn't.

The version of strength worth building says: "I'm not okay" without treating that as defeat. It hires a therapist for the same reason it hires a trainer. It asks "how are you?" and actually means it.

Full piece: "The Lie We Inherited About Strength" → link in bio.

When did asking for help stop feeling like failure? I'm genuinely asking.
```

---

---

### Poetry — LinkedIn

**Poetry does not have a LinkedIn post.** The niche (personal poetry, love, emotional interiority) doesn't translate to LinkedIn's professional context. A poem about romantic intoxication posted to a professional network creates a tonal mismatch that hurts brand perception on both channels. Skip LinkedIn for Poetry every week — this is intentional, not an oversight.

---

### LinkedIn checklist

```
# [ ] Hook line (first 2 lines) works as a standalone tweet — forces a stop
# [ ] Post is 200–400 words (LinkedIn sweet spot)
# [ ] Ends with a question that's easy to answer honestly
# [ ] No bullet points in the hook section — use them only in the middle
# [ ] Tags: 3–5 hashtags at the bottom (not inline)
# [ ] LinkedIn: held manual until employer clearance (staged in scheduling.db, daemon off)
# [ ] If poll: options are ≤ 30 characters each
```

---

## Phase 6 — Podcast Virality (Life + Poetry only)

**Full framework:** `prompts/podcast-virality-prompt.md`

Podcast growth lives or dies on two metrics: **completion rate** (target ≥ 65%) and **listener-to-follower conversion** (new listener plays episode → follows show). The first 60 seconds determine completion rate. The episode title determines whether a new listener even taps play.

The same hook rules from Instagram and Medium apply here. Episode titles must contain one of: specific incident, specific counter-intuitive observation, or named emotional experience. Never: episode numbers as titles, vague topic labels, question titles with obvious answers.

### Life — Mental Health episode (Breath of Life)

**Episode title:**
> "I White-Knuckled Life for Three Years. Here's What I Was Really Running From."

Why: "white-knuckled" is specific and physical (visceral), "here's what I was really running from" promises a reveal. Cold listeners tap this.

Backup:
> "I Called My Parents When I Was Drowning in Anxiety. They Gave Me Budgeting Tips."
(This is from the actual personal story in the blog — extremely specific, creates immediate empathy and dark humor.)

**Description (5-line structure):**
```
I white-knuckled life for three years. Passive-aggressive in meetings, rude to people I cared about, waking at 3 AM in loops I couldn't shut off. I told myself that was ambition.

It wasn't. It was a person who needed help with no framework for asking.

This episode is about the lie we inherited about strength — the script that says silence is the cost of being capable — and what it actually looks like to rewrite it.

Full piece: medium.com/@tarun-gupta/the-lie-we-inherited-about-strength

Follow Breath of Life for new episodes every week.
```

**Intro script (first 90 seconds):**
```
[No intro music, straight to voice]

"Break a bone, and people sign your cast. They hold the door. They say: take it easy.

Tell someone you haven't slept in three weeks because your chest feels like it's caving in —
and the room goes quiet.

Or worse: 'Have you tried going outside more?'

[pause — 2 seconds]

I've watched men I genuinely care about disappear into silence. A close friend going through a brutal breakup. Another drowning in financial pressure. I'd ask how they were doing. They'd say it's nothing. Their eyes said otherwise.

And I get it. Because I did the same thing.

For years, I white-knuckled it. And this episode is about what that was actually costing — and the definition of strength that I think is worth building instead."

[continue into body]
```

---

### Poetry — Intoxicated Senses episode (Breath of Poetry)

**Episode title:**
> "The Hangover That Won't Lift"

Why: short, specific metaphor, names a duration. Anyone who has felt this will tap play. It works for a poetry episode because the title is the hook — you don't explain it, you feel it.

Backup:
> "Intoxicated Senses — A Poem About the Hangover Love Leaves Behind"

**Description (5-line structure):**
```
There's a specific kind of madness that doesn't announce itself. One day you're fine. The next, someone's laugh is living rent-free in your head — and the part of your brain that's supposed to run the show has quietly handed over the keys.

This is a reading of "Intoxicated Senses" — a poem about the hangover that love leaves behind.

Full poem: medium.com/@tarun-gupta/the-hangover-that-wont-lift

Follow Breath of Poetry for weekly poems and readings.
```

**Intro script (first 90 seconds):**
```
[No music intro — straight to voice]

"There's a specific kind of madness that doesn't announce itself."
[2-second pause]
"One day you're fine. The next, someone's laugh is living rent-free in your head.
Their specific laugh. At something specific. From a specific afternoon.
The part of your brain that's supposed to run the show has quietly handed over the keys.

The trouble isn't the feeling. It's what comes after — when you realize you've been running on a hangover you didn't consent to."

[pause]

"This is Intoxicated Senses."

[begin reading the poem, slowly — each line separate]
```

---

### Podcast checklist

```
# [ ] Episode title: specific incident, counter-intuitive, or named emotional experience — never a topic label
# [ ] First word of the episode is the hook — no "welcome back," no "hey everyone"
# [ ] Reason-to-stay planted in first 60 seconds (what will the listener get by the end?)
# [ ] Description: first 2 lines are the hook (these appear in Spotify previews)
# [ ] Description line 4: "Full piece: medium.com/@tarun-gupta/[slug]"
# [ ] Description line 5: "Follow [show name] for new episodes every week"
# [ ] No intro music that runs longer than 5 seconds before voice begins
```

---

## Phase 7 — Derivatives + Scheduling

### Distribute (manual — no Metricool/Publer)

After all six platforms are audited and copy is finalized, distribution is **manual**. There is no
CSV bridge. Post each derivative file by hand in its window (`instagram_caption.txt`,
`threads_post.txt`, `twitter_thread.md`); optionally stage LinkedIn into `scheduling.db` via
`scripts/load_posts.py`.

**LinkedIn:** held **manual until employer clearance** (the `scheduler.py` daemon stays off).
**Twitter threads and polls:** cannot be scheduled — post manually.

### Platform schedule (W22 reference)

| Day | Platform | Content |
|-----|----------|---------|
| Wednesday | Medium | Publish all 3 blogs (DS, Life, Poetry) |
| Wednesday | YouTube | Upload all 3 long-form videos |
| Thursday | Instagram | DS Short + Life Short posted as Reels |
| Thursday | Instagram | Poetry Short posted as Reel |
| Thursday | Twitter/X | DS thread (manual) |
| Friday | Twitter/X | Life thread (manual) |
| Friday | Twitter/X | Poetry single tweet (manual) |
| Friday | LinkedIn | DS post |
| Friday | LinkedIn | Life post |
| Friday | LinkedIn | Poetry — skip (niche mismatch, see Phase 5) |
| Saturday | Podcast | Upload Life + Poetry episodes |

Reference: `docs/daily/thursday.md`, `docs/daily/friday.md`, `docs/daily/saturday.md`

### Verify derivatives exist

```bash
# Confirm each slug has the per-platform files you'll post manually
for d in content/derivatives/2026-W22/*/; do
  echo "$(basename "$d"):"
  for f in instagram_caption.txt threads_post.txt twitter_thread.md linkedin_post.txt; do
    [ -f "$d$f" ] && echo "  ✓ $f" || echo "  ✗ MISSING $f"
  done
done
```

---

## Phase 8 — Final Virality Audit

Run this as the last step before any content goes live. It's a 15-minute pass over every deliverable.

### Pre-publish checklist — Medium

```
DS:
[ ] Title: "The Type Error That Makes Your Analysis Wrong Without Crashing" (or approved variant)
[ ] First paragraph: hook passes removal test
[ ] [QUOTABLE] marked in draft
[ ] Tags: Python, Data Science, Programming, Tutorial, Machine Learning
[ ] TDS submission queued

Life:
[ ] Title: "The Lie We Inherited About Strength"
[ ] Quotable: "We hand someone drowning a map of the shoreline instead of a rope." — marked [QUOTABLE]
[ ] Tags: Mental Health, Self Improvement, Men's Mental Health, Psychology, Personal Development
[ ] The Ascent or P.S. I Love You submission queued

Poetry:
[ ] Format: hook → poem → 2-line close → podcast CTA (NO reflections, NO analysis)
[ ] Tags: Poetry, Love, Mental Health, Creative Writing, Relationships
[ ] P.S. I Love You submission queued
```

### Pre-upload checklist — YouTube

```
All three videos:
[ ] Thumbnail: face visible, hook text ≤ 5 words, dark navy background
[ ] Thumbnail generated with: python3 scripts/generate_thumbnail.py --canva
[ ] Title front-loads the hook (pain/anomaly/confession in first 4 words)
[ ] Description: timestamps, Medium link, podcast link (Life/Poetry), worksheet link (DS/Life)
[ ] Tags: 8-10 filled
[ ] End screen added (Tutorial teaser for DS, subscribe prompt for Life/Poetry)
[ ] Thursday upload blocking gate in thursday.md: face ✓ / hook text ✓ / no series number ✓
```

### Pre-post checklist — Shorts/Reels

```
All three Shorts:
[ ] Hook overlay text in first 3 seconds
[ ] 3 mandatory text overlays present
[ ] Caption starts with the hook (not a description)
[ ] Loop signal built in (unresolved quote, code output, or emotional line)
[ ] Hashtags: 5 max, first 2 are primary niche tags
```

### Pre-post checklist — Twitter/LinkedIn/Podcast

```
Twitter:
[ ] Hook tweet: counterintuitive claim, paradox, or emotional precision — stands alone
[ ] Threads flagged for manual posting
[ ] Poetry: single tweet or 2-tweet max

LinkedIn:
[ ] Hook line works as a standalone tweet
[ ] Ends with an answerable question (not "what do you think?")
[ ] LinkedIn held manual until employer clearance (daemon off)

Podcast:
[ ] Episode title: specific incident or named emotional experience
[ ] First word is the hook — no preamble
[ ] Description: hook in first 2 lines, Medium link in line 4
```

---

## Appendix — Reference Map

All files this framework references. Keep these current; the framework reads them at runtime.

### Prompt files
| File | Purpose |
|------|---------|
| `prompts/medium-virality-prompt.md` | Full Medium virality framework + 75-article performance dataset |
| `prompts/youtube-virality-prompt.md` | YouTube long-form + Shorts virality framework |
| `prompts/podcast-virality-prompt.md` | Spotify podcast growth framework |
| `prompts/repurposing_agent.md` | Converts one blog into all-channel derivatives |
| `prompts/writing_agent.md` | Long-form blog writing agent (DS/Life) |
| `prompts/ghostwriter_agent.md` | Converts notes/transcript to blog |
| `prompts/podcast_agent.md` | Generates Life + Poetry YT script + podcast script |
| `prompts/yt_screen_script_agent.md` | DS screen-recording script agent |

### Knowledge base
| File | Purpose |
|------|---------|
| `data/kb/viral_reel_formula.md` | 5-beat reel formula (reverse-engineered from 38k-view reel) |
| `data/kb/twitter_hook_patterns.json` | Hook pattern taxonomy for Twitter and Shorts |
| `data/kb/voice/INDEX.md` | Virality principles for Life/Poetry niche |
| `data/kb/reels/INDEX.md` | Virality principles for DS/build-in-public niche |
| `data/kb/projects.json` | Build-in-public projects (angle, DM keyword, cadence) |
| `data/analytics/medium-stats-2026.md` | 75-article read ratio dataset — use for title benchmarking |

### Daily operating docs
| File | Purpose |
|------|---------|
| `docs/daily/monday.md` | Blog generation day (includes Step 3 poetry format guidance) |
| `docs/daily/tuesday.md` | Script generation day (includes Step 2d thumbnail hook extraction) |
| `docs/daily/wednesday.md` | Publish day (Medium + shoot) |
| `docs/daily/thursday.md` | Upload + Shorts + schedule day — includes blocking thumbnail gate |
| `docs/daily/friday.md` | Caption + LinkedIn + Twitter day |
| `docs/daily/saturday.md` | Podcast upload + catch-up |
| `docs/one-time-platform-setup.md` | One-time profile/bio/link-in-bio setup |

### Virality infrastructure
| File | Purpose |
|------|---------|
| `docs/thumbnail-replacement-backlog.md` | All existing videos needing face thumbnails + ready commands |
| `docs/weekly-operating-guide.md` | CTR Mandates table + full weekly rhythm |
| `scripts/generate_thumbnail.py` | Generates Canva thumbnails (--canva flag) |
| `scripts/load_posts.py` | Stages LinkedIn into scheduling.db (IG/FB/Threads are manual) |
| `scripts/inject_worksheet_ctas.py` | Injects worksheet URLs into DS/Life captions |
| `scripts/lib/virality.py` | Virality block injected into every generator automatically |
