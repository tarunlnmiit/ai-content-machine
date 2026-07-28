---
title: "Content Tracker (v1)"
type: doc
slug: content-tracker
tags: [content/doc]
---
# Content Tracker (v1)

Source of truth for every piece of content across the pipeline — blog, Medium, LinkedIn,
carousel, reel, longform video, worksheet. Hand-edited by Tarun (and Claude on his behalf).

- **Key:** the slug on each `## ` line. For a piece with no confidently-matched blog file,
  the key is `ORPHAN:<name>`.
- **One row per piece.** Never delete a row — update fields (especially `medium.status`,
  `linkedin.status`, `reel.status`, `worksheet.status`) in place as things change.
- `—` (em dash) means unknown / not yet set. Never invent a value — leave it `—`.
- Auto-detected columns (blog path, carousel path, worksheet PDF, reel script/video,
  derivatives folder) are **not stored here** — they live only in the generated HTML view.
- Regenerate the HTML view after any edit to this file:
  `python3 v1/scripts/generate_tracker_html.py`

**Status vocabularies** (a value outside these is rejected):

| Field | Values |
|---|---|
| `medium.status` | submitted · accepted · declined · published · withdrawn · draft · self-publishing |
| `linkedin.status` | posted · scheduled · pending · none |
| `carousel.status` | none · created · scheduled · posted |
| `reel.status` | script · rendered · scheduled · posted · none |
| `longform.status` | none · script · assembled · scheduled · published |
| `worksheet.status` | none · generated · deployed |

`*.url`, `reel.ig`, `reel.yt` are **link** columns — a full `https://…` or `—`, never a date.

**Updating a row without hand-editing this file:**

```bash
python3 v1/scripts/dashboard.py     # → localhost:8765/tracker — edit the table directly
```

The table is editable like a spreadsheet: statuses are dropdowns, links and refs are text
inputs, `+ note` appends to the history. Each edit saves instantly to this file and
regenerates the HTML. No Claude call — validation is deterministic, so a status can only ever
be one of its listed values and a link column can only ever hold a URL.

Headless equivalent:
```bash
python3 v1/scripts/update_tracker.py <slug-or-title> --set carousel.status=posted \
                                                     --set carousel.url=https://...
python3 v1/scripts/update_tracker.py <slug-or-title> --append-note "Published on X."
```

Guarantees on every path: `title`/`week`/`niche`/`date` are immutable; `notes` is append-only
(never rewritten); an edit that would touch another record or break parsing is aborted before
anything is written. `flags` is read-only in the table — edit it here.

---

## 2026-06-26_data_science_tech_what-hiring-managers-think-when-they-see-your-ds-github-2026
title:            What Hiring Managers Actually Think When They See Your Data Science GitHub in 2026
week:             W26
niche:            ds
date:             2026-06-26
medium.pub:       DataDrivenInvestor
medium.status:    published
medium.submitted: 2026-06-26
medium.url:       —
medium.method:    Add-to-publication (already contributing)
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      rendered
reel.cta:         —
reel.ig:          created
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  ✅ PUBLISHED. DSC not accepting new writers (confirmed 2026-07-03) — pulled. AI in Plain English skipped — W27 piece already queued there. HackerNoon ruled out — off Medium (confirmed 2026-07-03). Routed to DataDrivenInvestor — career/hiring angle fits, already contributing.
  brag video: plan drafted, tone=wrycontrarian, hook=Contrarian + Authority reversal
  reel: 2026-07-27 selected for today's IG reel (Haiku explore + Fable advisory) — asset at v1/assets/brag_videos/2026-W26/2026-06-26_data_science_tech_what-hiring-managers-think-when-they-see-your-ds-github-2026_brag.mp4

## 2026-06-26_life_self_dev_ive-done-the-same-3-step-morning-routine-for-2-years_betterhumans
title:            How to Build a Wake-Up Ritual That Survives Real Life
week:             W26
niche:            life
date:             2026-06-26
medium.pub:       Publishous
medium.status:    published
medium.submitted: 2026-07-10
medium.url:       —
medium.method:    New pub submission — https://medium.com/publishous
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  ✅ PUBLISHED 2026-07-14 (confirmed via Medium submissions outbox 2026-07-16). History: declined by Mind Cafe (2026-06-30) under variant title *"...Survives a Real Life"*; also submitted to Change Your Mind Change Your Life (CMCML) — quiet since 2026-05-29, not dead just slow, no ETA, that submission left standing/unconfirmed. Rerouted to Publishous to keep momentum — published there. Personal Growth Project ruled out — dead since Apr 2025. Practice in Public ruled out — no confirmed link/slug (2026-07-10).

## 2026-06-26_poetry_quotes_i-wrote-a-poem-every-time-life-broke-me-heres-what-the-words
title:            The Room No One Entered
week:             W26
niche:            poetry
date:             2026-06-26
medium.pub:       Humans Are Stories (own pub)
medium.status:    self-publishing
medium.submitted: 2026-06-26
medium.url:       —
medium.method:    Add to own publication (Tarun is Editor)
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  Decision: all poetry goes to his own pub — no external poetry-pub gatekeeping or dead-pub hunting.
  brag video: plan drafted, tone=restrained, hook=Hyper-specificity + Pattern interrupt

## 2026-06-30_data_science_tech_the-free-local-ai-setup-that-replaced-my-200month-data-scien
title:            The Free Local AI Setup That Replaced My $200/Month Data Science Stack
week:             W27
niche:            ds
date:             2026-06-30
medium.pub:       AI in Plain English
medium.status:    published
medium.submitted: 2026-06-30
medium.url:       —
medium.method:    In Plain English network (Discord/community route)
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  ✅ PUBLISHED 2026-06-30. First piece live via the In Plain English network (unlocks Python/JS/AI in Plain English + Stackademic for future DS posts). DSC W26 still pending — not re-submitted there.
  brag video: plan drafted, tone=yc-parody, hook=Contrarian + Timeframe tension

## 2026-06-30_life_self_dev_the-5-minute-habit-that-replaced-3-hours-of-self-help-conten
title:            The 3 Hours You Spend on Self-Help Content Are Making You Worse at Self-Improvement
week:             W27
niche:            life
date:             2026-06-30
medium.pub:       ILLUMINATION
medium.status:    published
medium.submitted: 2026-07-06
medium.url:       —
medium.method:    Add-to-publication
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      rendered
reel.cta:         —
reel.ig:          created
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  ✅ PUBLISHED. Curious found dead (2026-07-06) — pulled. Resubmitted to ILLUMINATION, contrarian self-improvement essay fits.
  reel: 2026-07-27 selected for today's IG reel (Haiku explore + Fable advisory), best of 5 rendered variants ("quiet-admission" deadpan take) — asset at v1/assets/brag_videos/2026-W27/2026-06-30_life_self_dev_the-5-minute-habit-that-replaced-3-hours-of-self-help-conten_brag.mp4

## 2026-07-01_data_science_tech_i-tracked-every-data-science-job-posting-for-30-days-heres-t
title:            I Scraped 1,003 Data Science Job Postings — 87% Want This One Thing, and Most Candidates Still…
week:             W27
niche:            ds
date:             2026-07-01
medium.pub:       Artificial Intelligence in Plain English
medium.status:    published
medium.submitted: 2026-07-01
medium.url:       —
medium.method:    In Plain English network (already a writer)
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  ✅ PUBLISHED 2026-07-07 (verified via Medium submissions outbox 2026-07-16). Data-heavy job-market piece (1,003 postings scraped). Network home already unlocked via the 06-30 published piece. DSC W26 still pending.
  brag video: plan drafted, tone=cinematic, hook=Hyper-specificity + Numbered list

## 2026-07-01_life_self_dev_i-tracked-90-days-of-productive-mornings-data-show-real-trig
title:            I Woke at 6AM Every Day for 90 Days. The Data Said Wake Time Was Never the Point.
week:             W27
niche:            life
date:             2026-07-01
medium.pub:       Know Thyself Heal Thyself
medium.status:    published
medium.submitted: 2026-07-14
medium.url:       —
medium.method:    Add-to-publication (already a writer)
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  ✅ PUBLISHED 2026-07-15 (verified via Medium submissions outbox 2026-07-16). Kick Ass At Life gone quiet (no posts since 2026-06-05, editor likely on hiatus) — pulled, resubmitted to Know Thyself Heal Thyself.

## 2026-07-06_data_science_tech_the-local-ai-agent-i-built-in-a-weekend-now-does-the-grunt-w
title:            I Built a Local AI Agent That Does a Junior Analyst's Grunt Work in 4 Minutes
week:             W28
niche:            ds
date:             2026-07-06
medium.pub:       Technology Hits
medium.status:    published
medium.submitted: 2026-07-06
medium.url:       —
medium.method:    New pub submission
linkedin.status:  —
linkedin.url:     —
carousel.status:  created
carousel.url:     —
reel.ref:         2026-07-06_data_science_tech_the-local-ai-agent-i-built-in-a-weekend
reel.status:      script
reel.cta:         AGENT
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  ✅ PUBLISHED 2026-07-06 (verified via Medium submissions outbox 2026-07-16). AI Advances declined + zipBoard dead (07-06) — resubmitted to Technology Hits.
  brag video: plan drafted, tone=deadpan, hook=Contradiction + Hyper-specificity

## 2026-07-06_life_self_dev_your-overloaded-self-improvement-schedule-is-slowly-making-y
title:            Your Self-Improvement Schedule Is Slowly Making You Someone You Don't Recognize
week:             W28
niche:            life
date:             2026-07-06
medium.pub:       Write A Catalyst
medium.status:    submitted
medium.submitted: 2026-07-06
medium.url:       —
medium.method:    New pub submission
linkedin.status:  —
linkedin.url:     —
carousel.status:  created
carousel.url:     —
reel.ref:         2026-07-06_life_self_dev_your-overloaded-self-improvement-schedule
reel.status:      script
reel.cta:         AUDIT
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     33
flags:            —
notes: |
  Pending review on Medium (verified via submissions outbox 2026-07-16). Be Yourself confirmed dead (no posts since 2025) — pulled, resubmitted to Write A Catalyst (productivity/self-growth crossover).
  brag video: plan drafted, tone=yc-parody, hook=Contradiction + Authority reversal

## 2026-07-10_data_science_tech_i-asked-5-senior-engineers-to-explain-a-vector-database-with
title:            Everyone Building RAG Is Getting Vector Databases Wrong
week:             W28
niche:            ds
date:             2026-07-10
medium.pub:       SYNERGY
medium.status:    published
medium.submitted: 2026-07-10
medium.url:       https://medium.com/@tarun-gupta/dfb2706068a1
medium.method:    Add-to-publication (secured, unused this week)
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  ✅ PUBLISHED 2026-07-12 (verified via Medium submissions outbox 2026-07-16). Technology Hits already holds W28 DS submission (07-06) — avoided stacking, routed to secured-but-unused SYNERGY. Worksheet: The Vector DB Readiness Checklist.
  brag video: plan drafted, tone=polished, hook=Curiosity gap + Contrarian

## 2026-07-10_life_self_dev_high-emotional-intelligence-at-work-isnt-about-being-nice-it
title:            The Skill Every High-Performer Has That Nobody Taught You in Any Meeting
week:             W28
niche:            life
date:             2026-07-10
medium.pub:       Mind Cafe
medium.status:    submitted
medium.submitted: 2026-07-10
medium.url:       —
medium.method:    Add-to-publication (secured, unused this week)
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     32
flags:            —
notes: |
  Pending review on Medium (verified via submissions outbox 2026-07-16). Write A Catalyst already holds W28 Life submission (07-06) — avoided stacking, routed to secured-but-unused Mind Cafe. Worksheet: The Ten-Second Rule.
  brag video: plan drafted, tone=deadpan, hook=Cold open + Contrarian

## 2026-06-08_data_science_tech_i-deleted-three-weeks-of-content
title:            I Deleted Three Weeks of Content
week:             W24
niche:            ds
date:             2026-06-08
medium.pub:       ILLUMINATION
medium.status:    published
medium.submitted: 2026-06-08
medium.url:       —
medium.method:    Backfilled from Medium submissions outbox (2026-07-16) — pre-tracker piece, no submission record
linkedin.status:  —
linkedin.url:     —
carousel.status:  created
carousel.url:     —
reel.ref:         2026-06-08_data_science_tech_i-deleted-three-weeks-of-content
reel.status:      script
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  ✅ PUBLISHED 2026-06-08. Reclassified Life→DS/Tech (2026-07-16): content is a git/dev-tools recovery story, not self-dev — carousel/reel regenerated under DS niche.
  brag video: plan drafted, tone=cinematic, hook=Cold open + Negativity bias

## 2026-05-31_data_science_tech_the-one-skill-that-makes-you-good-at-ai
title:            The One Skill That Makes You Good at AI (It's Not What You Think)
week:             W22
niche:            ds
date:             2026-05-31
medium.pub:       ILLUMINATION
medium.status:    published
medium.submitted: 2026-05-31
medium.url:       https://medium.com/illumination/the-one-skill-that-makes-you-good-at-ai-its-not-what-you-think-ab03dc03a523
medium.method:    Backfilled from Medium submissions outbox (2026-07-16) — pre-tracker piece, no submission record
linkedin.status:  —
linkedin.url:     —
carousel.status:  scheduled
carousel.url:     —
reel.ref:         2026-05-31_data_science_tech_the-one-skill-that-makes-you-good-at-ai
reel.status:      script
reel.cta:         AI
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  script
longform.url:     —
worksheet.status: deployed
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  ✅ PUBLISHED 2026-05-31.
  https://payhip.com/NovelPromptCo
  brag video: plan drafted, tone=polished, hook=Contrarian + Curiosity gap

## 2026-07-16_data_science_tech_building-a-mastodon-automation-bot-using-python-and-streamli
title:            You Don't Need Mastodon.py to Automate Toots — Just `requests` and 40 Lines
week:             W29
niche:            ds
date:             2026-07-16
medium.pub:       Technology Hits
medium.status:    submitted
medium.submitted: 2026-07-16
medium.url:       https://medium.com/@tarun-gupta/e43cd7dc9d1d
medium.method:    Add-to-publication
linkedin.status:  —
linkedin.url:     —
carousel.status:  created
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: deployed
worksheet.url:    —
source_draft:     2
flags:            —
notes: |
  Submitted as Medium draft 2026-07-16. From drafts-completion batch (source Medium draft: 'Building a Mastodon Automation Bot Using Python and Streamlit'); worksheet live.
  brag video: plan drafted, tone=yc-parody, hook=Contrarian + Hyper-specificity

## 2026-07-16_life_self_dev_what-leaving-home-at-eighteen-actually-cost-me-ten-years-lat
title:            Ten Years Of Independence Taught Me Two Things I Blame My Parents For. I Can Only Write One.
week:             W29
niche:            life
date:             2026-07-16
medium.pub:       ILLUMINATION
medium.status:    published
medium.submitted: 2026-07-16
medium.url:       https://medium.com/illumination/ten-years-of-independence-taught-me-two-things-i-blame-my-parents-for-af812b212af0
medium.method:    Add-to-publication
linkedin.status:  —
linkedin.url:     —
carousel.status:  created
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         LETTER
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: deployed
worksheet.url:    —
source_draft:     7
flags:            —
notes: |
  ✅ PUBLISHED (confirmed by Tarun 2026-07-17). From drafts-completion batch (source Medium draft: 'Dear 16 year old Tarun,'); worksheet live.

## 2026-07-14_data_science_tech_i-built-a-production-grade-mlops-pipeline-in-one-weekend-wit
title:            I Built a Production-Grade MLOps Pipeline in One Weekend With Nothing But Free Tools
week:             W29
niche:            ds
date:             2026-07-14
medium.pub:       TBD (proposed: SYNERGY)
medium.status:    draft
medium.submitted: —
medium.url:       https://medium.com/@tarun-gupta/1e612f081b18
medium.method:    TBD
linkedin.status:  —
linkedin.url:     —
carousel.status:  created
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  Produced 2026-07-14, not yet submitted. Secured pub SYNERGY last used 07-10 — avoids stacking with Mastodon piece (proposed Technology Hits).
  brag video: plan drafted, tone=deadpan, hook=Negativity bias + Curiosity gap

## 2026-07-14_life_self_dev_how-to-make-better-decisions-under-pressure-without-ever-tru
title:            How to Make Better Decisions Under Pressure Without Ever Truly Trusting Yourself
week:             W29
niche:            life
date:             2026-07-14
medium.pub:       TBD (proposed: Write A Catalyst)
medium.status:    draft
medium.submitted: —
medium.url:       https://medium.com/@tarun-gupta/a591a021c2f9
medium.method:    TBD
linkedin.status:  —
linkedin.url:     —
carousel.status:  created
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  Produced 2026-07-14, not yet submitted. Write A Catalyst last used 07-06, productivity/self-growth fit — avoids stacking with Mind Cafe (pending) and Know Thyself Heal Thyself (used 07-14).
  brag video: plan drafted, tone=cinematicdata, hook=Contrarian + Hyper-specificity

## 2026-07-17_life_self_dev_understanding-who-truly-cares-a-guide-to-valuing-real-connec
title:            The Person You're Begging To Notice You Isn't The Problem. This Is.
week:             W29
niche:            life
date:             2026-07-17
medium.pub:       Thoughts And Ideas
medium.status:    submitted
medium.submitted: 2026-07-17
medium.url:       —
medium.method:    Add-to-publication (already contributing)
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         2026-07-17_life_self_dev_the-person-youre-begging-to-notice
reel.status:      none
reel.cta:         LETTER
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: generated
worksheet.url:    —
source_draft:     34
flags:            —
notes: |
  Submitted 2026-07-17. Produced same day from Medium drafts-completion batch (row 34, source draft: 'Understanding Who Truly Cares: A Guide to Valuing Real Connections'); carousel live, worksheet generated but not yet deployed (Vercel push pending — 404 as of 07-17). Mind Cafe + Write A Catalyst ruled out — each already had a piece pending review. ILLUMINATION already used W29 (Ten Years piece, published). First piece submitted to Thoughts And Ideas (26K followers) — new secured home, unused before this.
  brag video: plan drafted, tone=cinematic, hook=Hyper-specificity + Authority reversal

## 2026-06-16_data_science_tech_ai-prompt-anatomy-travel
title:            I Stopped Googling Travel Guides. I Interrogated an AI Instead — Here's the Exact Prompt That Worked
week:             W25
niche:            life
date:             2026-06-16
medium.pub:       ILLUMINATION
medium.status:    published
medium.submitted: 2026-06-16
medium.url:       —
medium.method:    Backfilled from Medium submissions outbox (2026-07-16) — pre-tracker piece, no submission record
linkedin.status:  —
linkedin.url:     —
carousel.status:  created
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            ? niche conflict — tracker says Life, blog file slug says data_science_tech. Confirm with Tarun.
notes: |
  ✅ PUBLISHED 2026-06-16.
  brag video: plan drafted, tone=app-store, hook=POV + Hyper-specificity

## ORPHAN:safe-and-alive
title:            Safe and Alive
week:             W27
niche:            life
date:             —
medium.pub:       Writers' Blokke
medium.status:    published
medium.submitted: 2026-07-02
medium.url:       —
medium.method:    Backfilled from Medium submissions outbox (2026-07-16) — pre-tracker piece, no submission record
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            ? pre-pipeline piece — no blog file in repo
notes: |
  ✅ PUBLISHED 2026-07-02.

## ORPHAN:youll-never-actually-reach-this-goal
title:            You'll Never Actually Reach This Goal — And That's Exactly the Point
week:             W25
niche:            life
date:             —
medium.pub:       Mind Cafe
medium.status:    published
medium.submitted: 2026-06-19
medium.url:       —
medium.method:    Backfilled from Medium submissions outbox (2026-07-16) — pre-tracker piece, no submission record
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            ? pre-pipeline piece — no blog file in repo
notes: |
  ✅ PUBLISHED 2026-06-19.

## ORPHAN:the-silent-killer-no-one-talks-about
title:            The Silent Killer No One Talks About (And It's Not What You Think)
week:             W25
niche:            life
date:             —
medium.pub:       An Injustice!
medium.status:    published
medium.submitted: 2026-06-19
medium.url:       —
medium.method:    Backfilled from Medium submissions outbox (2026-07-16) — pre-tracker piece, no submission record
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            ? pre-pipeline piece — no blog file in repo
notes: |
  ✅ PUBLISHED 2026-06-19.

## ORPHAN:how-i-stopped-doom-scrolling-job-boards
title:            How I Stopped Doom-Scrolling Job Boards
week:             W24
niche:            life
date:             —
medium.pub:       ILLUMINATION
medium.status:    published
medium.submitted: 2026-06-13
medium.url:       —
medium.method:    Backfilled from Medium submissions outbox (2026-07-16) — pre-tracker piece, no submission record
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            ? pre-pipeline piece — no blog file in repo
notes: |
  ✅ PUBLISHED 2026-06-13.

## ORPHAN:python-silently-lied-to-you
title:            Python Silently Lied to You (And You Didn't Notice)
week:             W25
niche:            ds
date:             —
medium.pub:       Technology Hits
medium.status:    published
medium.submitted: 2026-06-18
medium.url:       —
medium.method:    Backfilled from Medium submissions outbox (2026-07-16) — pre-tracker piece, no submission record
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            ? possible match 2026-05-25_data_science_tech_python-for-data-science-tutorial-210 (H1 "The Type Error That Makes Your Analysis Wrong Without Crashing") — dates disagree (W22 file vs W25 row). NOT auto-linked. Confirm with Tarun.
notes: |
  ✅ PUBLISHED 2026-06-18.

## ORPHAN:youre-not-in-love-youre-hungover
title:            You're Not in Love. You're Hungover.
week:             W25
niche:            life
date:             —
medium.pub:       Weeds & Wildflowers
medium.status:    published
medium.submitted: 2026-06-16
medium.url:       —
medium.method:    Backfilled from Medium submissions outbox (2026-07-16) — pre-tracker piece, no submission record
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            ? possible match 2026-05-27_poetry_quotes_intoxicated-senses (H1 "The Hangover That Won't Lift") — niche disagrees (row Life / file poetry). NOT auto-linked. Confirm with Tarun.
notes: |
  ✅ PUBLISHED 2026-06-16.

## ORPHAN:how-i-turned-my-habits-into-an-engine
title:            How I Turned My Habits into an "Engine" to Get Me to My Goals
week:             W25
niche:            life
date:             —
medium.pub:       Hello, Love
medium.status:    published
medium.submitted: 2026-06-15
medium.url:       —
medium.method:    Backfilled from Medium submissions outbox (2026-07-16) — pre-tracker piece, no submission record
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            ? no exact H1 match; candidates 2026-06-16_life_self_dev_recursive-self-improvement / 2026-06-08_life_self_dev_the-simple-habit-that-changed-my-productivity. NOT auto-linked. Confirm with Tarun.
notes: |
  ✅ PUBLISHED 2026-06-15.

## ORPHAN:python-for-data-science-withdrawn
title:            Python for Data Science
week:             W25
niche:            ds
date:             —
medium.pub:       DataSeries
medium.status:    withdrawn
medium.submitted: 2026-06-15
medium.url:       —
medium.method:    Backfilled from Medium submissions outbox (2026-07-16) — pre-tracker piece, no submission record
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            ? ambiguous across 5 tutorial blog files. Withdrawn on Medium. NOT auto-linked. Confirm with Tarun.
notes: |
  Withdrawn on Medium (status confirmed via submissions outbox 2026-07-16).

## 2026-05-25_data_science_tech_python-for-data-science-tutorial-210
title:            The Type Error That Makes Your Analysis Wrong Without Crashing
week:             W22
niche:            ds
date:             2026-05-25
medium.pub:       Technology Hits
medium.status:    published
medium.submitted: 2026-06-18
medium.url:       https://medium.com/technology-hits/python-silently-lied-to-you-and-you-didnt-notice-2393bcab9c79
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  scheduled
carousel.url:     —
reel.ref:         —
reel.status:      script
reel.cta:         TYPES
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  script
longform.url:     —
worksheet.status: deployed
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  https://worksheets-thebreathnetwork.vercel.app/get-worksheet?slug=python-for-data-science-tutorial-210&source=post_page-----2393bcab9c79---------------------------------------
  brag video: plan drafted, tone=deadpan, hook=Negativity bias + Pattern interrupt

## 2026-05-26_life_self_dev_mental-health-openness-and-breaking-stigmas
title:            The Lie We Inherited About Strength
week:             W22
niche:            life
date:             2026-05-26
medium.pub:       An Injustice!
medium.status:    published
medium.submitted: 2026-06-19
medium.url:       https://aninjusticemag.com/the-silent-killer-no-one-talks-about-and-its-not-what-you-think-4680ca8fd155
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  posted
carousel.url:     —
reel.ref:         —
reel.status:      script
reel.cta:         ASK
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  script
longform.url:     —
worksheet.status: deployed
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  https://worksheets-thebreathnetwork.vercel.app/get-worksheet?slug=mental-health-openness-and-breaking-stigmas&source=post_page-----4680ca8fd155---------------------------------------

## 2026-05-27_poetry_quotes_intoxicated-senses
title:            The Hangover That Won't Lift
week:             W22
niche:            poetry
date:             2026-05-27
medium.pub:       Weeds & Wildflowers
medium.status:    published
medium.submitted: 2026-06-16
medium.url:       https://medium.com/weeds-wildflowers/youre-not-in-love-you-re-hungover-6dee883b512f
medium.method:    —
linkedin.status:  none
linkedin.url:     —
carousel.status:  scheduled
carousel.url:     —
reel.ref:         —
reel.status:      script
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  script
longform.url:     —
worksheet.status: none
worksheet.url:    —
source_draft:     —
flags:            ? title sourced from YAML frontmatter `title:` field — file has no markdown H1 (`# `) line.
notes: |
  brag video: plan drafted, tone=cinematic, hook=Cold open + Contradiction

## 2026-06-01_data_science_tech_python-for-data-science-tutorial-310
title:            Python for Data Science: Tutorial 3/10 — NumPy and the Art of Thinking in Arrays
week:             W23
niche:            ds
date:             2026-06-01
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  created
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  brag video: plan drafted, tone=default, hook=Transformation evidence + Timeframe tension

## 2026-06-01_life_self_dev_the-cost-of-carrying-things-nobody-sees
title:            The Cost of Carrying Things Nobody Sees
week:             W23
niche:            life
date:             2026-06-01
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  created
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  brag video: plan drafted, tone=polished, hook=POV + Curiosity gap

## 2026-06-01_poetry_quotes_looking-at-the-world-through-a-reflective-lens
title:            Only to Make Themselves Happy
week:             W23
niche:            poetry
date:             2026-06-01
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  created
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            ? title sourced from YAML frontmatter `title:` field — file has no markdown H1 (`# `) line.
notes: |
  brag video: plan drafted, tone=deadpan, hook=Contrarian + Negativity bias

## 2026-06-08_life_self_dev_the-simple-habit-that-changed-my-productivity
title:            7 Simple Habits That Quietly Rewired My Productivity
week:             W24
niche:            life
date:             2026-06-08
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  created
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  brag video: plan drafted, tone=app-store, hook=Numbered list + Contrarian

## 2026-06-08_poetry_quotes_poetry-dips-its-fingers-in-every-colour
title:            Every Colour Has a Feeling
week:             W24
niche:            poetry
date:             2026-06-08
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  created
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            ? title sourced from YAML frontmatter `title:` field — file has no markdown H1 (`# `) line.
notes: |
  brag video: plan drafted, tone=polished, hook=Authority reversal + Transformation evidence

## 2026-06-10_data_science_tech_python-for-data-science-tutorial-4-pandas-for-data-analysis
title:            Python for Data Science: Tutorial 4/10 — Pandas for Data Analysis
week:             W24
niche:            ds
date:             2026-06-10
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  created
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  brag video: plan drafted, tone=polished, hook=Transformation evidence

## 2026-06-16_data_science_tech_python-for-data-science-tutorial-5-out-of-10-for-visualizati
title:            Python for Data Science — Tutorial 5/10: Making Your Data Tell a Story with Matplotlib and Seaborn
week:             W25
niche:            ds
date:             2026-06-16
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  created
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  brag video: plan drafted, tone=default, hook=Authority reversal + Negativity bias

## 2026-06-16_life_self_dev_recursive-self-improvement
title:            5 Loops That Make Self-Improvement Self-Sustaining
week:             W25
niche:            life
date:             2026-06-16
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  created
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  brag video: plan drafted, tone=systemsdiagram, hook=Curiosity gap + Contrarian

## 2026-06-16_poetry_quotes_you-have-gotta-dance-like-there-is-nobody-watching
title:            Dance When the Playlist Ends
week:             W25
niche:            poetry
date:             2026-06-16
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  created
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            ? title sourced from YAML frontmatter `title:` field — file has no markdown H1 (`# `) line.
notes: |
  brag video: plan drafted, tone=kinetic, hook=POV + Cold open

## 2026-06-23_ds_the-ml-skill-agentic-ai-bootcamps-wont-teach-you-but-re
title:            The ML Skill Agentic AI Bootcamps Won't Teach You (But Replaces You If You Skip It)
week:             W26
niche:            ds
date:             2026-06-23
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  brag video: plan drafted, tone=ominous, hook=Negativity bias + Hyper-specificity

## 2026-06-26_life_self_dev_ive-done-the-same-3-step-morning-routine-for-2-years
title:            I've Done the Same 3-Step Morning Routine for 2 Years. Here's Why I'll Never Change It.
week:             W26
niche:            life
date:             2026-06-26
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  brag video: plan drafted, tone=cinematic, hook=Hyper-specificity + Pattern interrupt

## ORPHAN:inbox-to-action
title:            Inbox to Action
week:             W28
niche:            ds
date:             —
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         2026-07-20_ds_tech_inbox-to-action
reel.status:      script
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  —

## ORPHAN:6-github-repos-that-slash-claude-code-tokens
title:            6 GitHub Repos That Slash Claude Code Tokens
week:             W25
niche:            ds
date:             2026-06-21
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  —

## ORPHAN:automated-job-hunting-script
title:            I Automated Job Hunting
week:             W25
niche:            ds
date:             2026-06-21
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  —

## ORPHAN:claude-primitive-beast-token-cut
title:            I Turned Claude Into a Primitive Beast
week:             W25
niche:            ds
date:             2026-06-22
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  —

## ORPHAN:grief-does-not-end-it-changes-shape-and-learns-to-live-besid
title:            Grief Does Not End, It Changes Shape and Learns to Live Besid…
week:             —
niche:            poetry
date:             —
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  —

## ORPHAN:how-i-gained-clarity-by-writing-my-decisions-down-before-i-m
title:            Write It Before You Decide It
week:             —
niche:            life
date:             —
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  —

## ORPHAN:the-one-question-i-ask-before-every-big-decision
title:            The One Question I Ask Before Every Big Decision
week:             —
niche:            life
date:             —
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  —

## ORPHAN:the-weekend-build-that-taught-me-more-than-6-months-of-tutor
title:            The Weekend Build That Taught Me More Than 6 Months of Tutor…
week:             —
niche:            ds
date:             —
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  —

## ORPHAN:pandas-for-data-analysis-load-filter-clean-aggregate-4-essen
title:            Pandas for Data Analysis: Load, Filter, Clean, Aggregate — 4 Essentials
week:             W24
niche:            ds
date:             —
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  —

## ORPHAN:dear-16-year-old-tarun
title:            Dear 16 Year Old Tarun
week:             W29
niche:            life
date:             2026-07-16
medium.pub:       ILLUMINATION
medium.status:    published
medium.submitted: 2026-07-17
medium.url:       https://medium.com/illumination/ten-years-of-independence-taught-me-two-things-i-blame-my-parents-for-af812b212af0
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  scheduled
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         LETTER
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: deployed
worksheet.url:    —
source_draft:     —
flags:            ? superseded by 2026-07-16_life_self_dev_what-leaving-home-at-eighteen-actually-cost-me-ten-years-lat (same underlying draft #7, retitled/reworked for full blog structure). Carousel not regenerated under the new slug — confirm with Tarun whether to regenerate or discard.
notes: |
  —

## ORPHAN:fable-mode-plugin
title:            Fable Mode Plugin
week:             W29
niche:            ds
date:             2026-07-13
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         2026-07-13_ds_tech_fable-mode-plugin
reel.status:      script
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            ? reel-only artifact — no blog, no Medium row (news-timed build-in-public reel per script header: github.com/tarunlnmiit/fable-mode).
notes: |
  —

## ORPHAN:python-for-data-science-tutorial-410
title:            Python Data Visualization
week:             W24
niche:            ds
date:             2026-06-08
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            ? not in spec's known ORPHAN list — found via listing. Filename suggests "tutorial 4/10" but the carousel's own <title> is "Python Data Visualization Carousel" — likely an early/mislabeled draft superseded by 2026-06-16_data_science_tech_python-for-data-science-tutorial-5-out-of-10-for-visualizati (Tutorial 5/10, Matplotlib/Seaborn). NOT auto-linked. Confirm with Tarun.
notes: |
  —

## ORPHAN:inbox-to-action-one-command-triages-your-gmail-inbox-in-a-si
title:            Inbox to Action: One Command Triages Your Gmail Inbox in a Si…
week:             —
niche:            ds
date:             —
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            ? not in spec's known ORPHAN list — found via listing. Possible duplicate/variant export of ORPHAN:inbox-to-action (same project, per carousel <title> "Breath of Data Science — Carousel: inbox-to-action"). NOT auto-linked. Confirm with Tarun.
notes: |
  —

## ORPHAN:statusline-plus
title:            statusline-plus
week:             W30
niche:            ds
date:             2026-07-20
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         2026-07-20_ds_tech_statusline-plus
reel.status:      script
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            ? reel-only artifact — no blog, no Medium row (news-timed build-in-public reel per script header: github.com/tarunlnmiit/statusline-plus). Not yet in data/kb/projects.json — add project entry before scheduling a recurring cadence.
notes: |
  —

## ORPHAN:pushkar-musician-reel
title:            The Best Part of Pushkar Wasn't a Place
week:             W30
niche:            life
date:             2026-07-21
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         v1/assets/hyperframes/2026-07-20_2026-W30_life_pushkar-voice-memo_FINAL.mp4
reel.status:      cancelled
reel.cta:         PUSHKAR
reel.ig:          not publishing — creator decision 2026-07-20
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            ? reel-only artifact — no blog, IG-only, W30 Pushkar trip. Recording pending — see manual_steps.md.
notes: |
  Voice memo not yet recorded. [PERSONAL_INSERT]/[CONFIRM] markers in the script must be resolved before recording. Publish gated on manual_steps.md.

## ORPHAN:pushkar-fish-poem
title:            Birds Don't Look Back
week:             W30
niche:            poetry
date:             2026-07-23
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         v1/assets/hyperframes/2026-07-19_2026-W30_poetry_pushkar_FINAL.mp4
reel.status:      rendered
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            ? reel-only artifact — no blog, IG-only, W30 Pushkar trip. Text-over-B-roll poetry reel, no face/VO.
notes: |
  Final render done (49s). Caption = poem prose block, zero hashtags. Publish gated on manual_steps.md.

## ORPHAN:pushkar-photo-carousel
title:            More Photos of Us Laughing Than of the Lake
week:             W30
niche:            life
date:             2026-07-25
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  created
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         save + caption comment prompt
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            ? reel-only artifact — no blog, IG-only, W30 Pushkar trip. 7-slide carousel.
notes: |
  Slides exported: v1/assets/carousels/slides/2026-W30/2026-07-25_life_pushkar-carousel/ (slide_1–7.png). HTML: v1/assets/carousels/2026-W30/2026-07-25_life_pushkar-carousel_carousel.html. Copy file has 4 [CONFIRM] + 2 [PERSONAL_INSERT] markers Tarun must resolve before publish — see manual_steps.md.

---

## Publications ruled out (do not retry)
- **Better Humans** — not accepting new writers as of 2026-06-26.
- **The Ascent** — dead; last post 2021.
- **Poets Unlimited** — ceased operation.
- **The Junction** — dead; last post Sep 2022.
- **Scribe** — dead (confirmed by Tarun 2026-06-26, despite stale "recent post" metadata).
- **Data Science Collective** — not accepting new writer submissions as of 2026-07-03. W26 piece pulled, resubmitted to AI in Plain English network instead.
- **HackerNoon** — off Medium (confirmed by Tarun 2026-07-03), same move as Towards Data Science. Remove from DS/Tech contributing list.
- **Curious** — dead as of 2026-07-06 (Tarun confirmed). Remove from Life contributing list.
- **Be Yourself** — dead as of 2026-07-06 (no posts since 2025, Tarun confirmed). Remove from Life contributing list.
- **AI Advances** — declined submission 2026-07-06. Don't retry same piece; other pieces may still fit, use judgment.
- **zipBoard** — dead as of 2026-07-06 (Tarun confirmed). Remove from DS/Tech contributing list.
- **The Personal Growth Project** — dead since April 2025 (Tarun confirmed 2026-07-10). Remove from Life contributing list.
- **Practice in Public** — no findable/confirmed pub link (Tarun couldn't locate it 2026-07-10); doc slug was flagged `(verify)`, never confirmed live. Remove from Life contributing list until a real link surfaces.

> **Poetry policy:** all poetry self-published to **Humans Are Stories** (Tarun's own pub, he's Editor). Stop hunting external poetry pubs.

## Homes secured per niche (cap ~4 each, then go deep)
- **DS/Tech:** The Startup, DataDrivenInvestor, DataSeries, SYNERGY ✓ *(first piece submitted 07-10)*, Technology Hits ✓ *(first piece submitted 07-06)* · AI in Plain English ✓ *(first piece PUBLISHED 06-30 — network home: Python/JS/AI in Plain English + Stackademic)* — Data Science Collective + HackerNoon ruled out (07-03: not accepting / off Medium); AI Advances declined (07-06); zipBoard dead (07-06).
- **Life:** Mind Cafe ✓ *(piece submitted 07-10, declined 06-30 on a different piece)*, Change Your Mind Change Your Life, ILLUMINATION ✓ *(first piece submitted 07-06)*, Kick Ass At Life *(already contributing)*, Write A Catalyst ✓ *(first piece submitted 07-06)*, Thoughts And Ideas ✓ *(first piece submitted 07-17)* — Curious + Be Yourself ruled out (07-06: dead).
- **Poetry:** CRY Magazine, Other Doors, The Lark, Writers' Blokke, iPoetry, Humans Are Stories *(already contributing)*

## Daily routine
Each day we produce blogs → I surface **3 new pubs** matched to that day's pieces (no repeats of secured/ruled-out), verify they're live + accepting, then guideline-pass the article before submit. Reference list: `docs/medium-publications-to-join.md`.
