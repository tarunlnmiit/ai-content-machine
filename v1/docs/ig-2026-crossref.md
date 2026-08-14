---
title: "Instagram 2026 Cross-Reference"
type: doc
slug: ig-2026-crossref
tags: [content/doc]
---
# Instagram 2026 Cross-Reference

_Built 2026-08-14. One-off analysis doc — not generated, safe to hand-edit._

Joins live Instagram posts (scraped via Claude in Chrome, 2026-08-14) against
[`content-tracker.md`](content-tracker.md) (the carousel/reel tracker) and
[`medium-article-tracker.md`](medium-article-tracker.md) / `data/analytics/medium-stats-2026-08-11.json`.

**Scope:** 35 IG posts published in 2026 across the two accounts.
`@mistakenlyhuman` 25 posts (2026-06-15 → 07-30); `@breathofdatascience` 10 posts (2026-06-13 → 07-27).
Prior `@mistakenlyhuman` post before this batch is 2023-03-09 — a three-year gap, so 2026 is complete.

**Method:** Instagram permits no outbound links in captions, so no Medium URL is extractable.
Tracker-slug matches come from caption↔title overlap plus `reel.ref` / notes evidence in the tracker;
Medium URLs come from the analytics snapshot. Confidence is marked on every row. `—` means no counterpart
found — never an invented value.

Raw scrape JSON: `scratchpad/ig_mistakenlyhuman_2026.json`, `scratchpad/ig_breathofdatascience_2026.json`.

---

## @breathofdatascience — 10 posts

| IG date | Type | IG post | Tracker slug | Tracker says | Medium article | Conf |
|---|---|---|---|---|---|---|
| 06-13 | Reel | [DZhkDvoxtt2](https://www.instagram.com/breathofdatascience/reel/DZhkDvoxtt2/) | `ORPHAN:automated-job-hunting-script` | reel.status `none` | [How I Stopped Doom-Scrolling Job Boards](https://medium.com/illumination/how-i-stopped-doom-scrolling-job-boards-a6f84286a9e3) (06-13) | high |
| 06-15 | Carousel | [DZmm2tvD2mF](https://www.instagram.com/breathofdatascience/p/DZmm2tvD2mF/) | — (no tutorial-1 row) | — | [Python for Data Science](https://medium.com/@tarun-gupta/python-for-data-science-f05524d76808) (06-15) | med |
| 06-20 | Carousel | [DZzRFK3DYPf](https://www.instagram.com/breathofdatascience/p/DZzRFK3DYPf/) | — (byte-identical repost of above) | — | same | med |
| 06-21 | Reel | [DZ1hEo1RX-D](https://www.instagram.com/breathofdatascience/reel/DZ1hEo1RX-D/) | `ORPHAN:claude-primitive-beast-token-cut` | reel.status `none` | — (no Medium piece) | med ⚠ |
| 06-25 | Reel | [DZ_04ObRvEx](https://www.instagram.com/breathofdatascience/reel/DZ_04ObRvEx/) | `2026-05-31_data_science_tech_the-one-skill-that-makes-you-good-at-ai` | reel.status `script` | [The One Skill That Makes You Good at AI](https://medium.com/illumination/the-one-skill-that-makes-you-good-at-ai-its-not-what-you-think-ab03dc03a523) (05-31) | med |
| 07-07 | Carousel | [Daf2IdKgZ_l](https://www.instagram.com/breathofdatascience/p/Daf2IdKgZ_l/) | `2026-07-06_data_science_tech_the-local-ai-agent-i-built-in-a-weekend-now-does-the-grunt-w` | carousel.status `created` | [I Built a Local AI Agent…](https://medium.com/technology-hits/i-built-a-local-ai-agent-that-does-a-junior-analysts-grunt-work-in-4-minutes-1a36ccdce51d) (07-06) | high |
| 07-14 | Reel | [DaKD2koRE9U](https://www.instagram.com/breathofdatascience/reel/DaKD2koRE9U/) | — (no row) | — | — | — |
| 07-20 | Carousel | [DbA_1_9D33z](https://www.instagram.com/breathofdatascience/p/DbA_1_9D33z/) | `2026-05-31_data_science_tech_the-one-skill-that-makes-you-good-at-ai` | carousel.status `scheduled` | same as 06-25 | med |
| 07-23 | Carousel | [DbIuOnSH0iU](https://www.instagram.com/breathofdatascience/p/DbIuOnSH0iU/) | `2026-05-25_data_science_tech_python-for-data-science-tutorial-210` | carousel.status `scheduled` | [Python Silently Lied to You](https://medium.com/technology-hits/python-silently-lied-to-you-and-you-didnt-notice-2393bcab9c79) (06-18) | high |
| 07-27 | Reel | [DbS6jHPmNTF](https://www.instagram.com/breathofdatascience/reel/DbS6jHPmNTF/) | `2026-06-26_data_science_tech_what-hiring-managers-think-when-they-see-your-ds-github-2026` | reel.status `rendered`, reel.ig `created` | [What Hiring Managers Actually Think…](https://medium.com/datadriveninvestor/what-hiring-managers-actually-think-when-they-see-your-data-science-github-in-2026-e83bdacea453) (07-08) | high |

The 07-27 match is corroborated by that row's own note: _"reel: 2026-07-27 selected for today's IG reel"_.

⚠ The 06-21 match is contested. The caption — _"I cut Claude's replies ~65% with one command… Comment
'tokens' and I'll send you the skill"_ — fits `ORPHAN:claude-primitive-beast-token-cut` (2026-06-22,
caveman mode = one command) better than the competing `ORPHAN:6-github-repos-that-slash-claude-code-tokens`
(2026-06-21, plural repos). Both ORPHAN rows have empty `notes` and no `reel.ref`, so nothing in the
tracker settles it. Confirm before writing a status.

## @mistakenlyhuman — 25 posts (10 captioned)

| IG date | Type | IG post | Tracker slug | Tracker says | Medium article | Conf |
|---|---|---|---|---|---|---|
| 06-16 | Carousel | [DZpqksgjP9v](https://www.instagram.com/mistakenlyhuman/p/DZpqksgjP9v/) | `ORPHAN:safe-and-alive` | carousel.status `none` | [Safe and Alive](https://medium.com/writers-blokke/safe-and-alive-df6660f49a19) (07-02) | high |
| 06-17 | Carousel | [DZqryR2jfAN](https://www.instagram.com/mistakenlyhuman/p/DZqryR2jfAN/) | same (byte-identical repost) | same | same | high |
| 06-18 | Carousel | [DZtsCdFkv1h](https://www.instagram.com/mistakenlyhuman/p/DZtsCdFkv1h/) | `ORPHAN:how-i-turned-my-habits-into-an-engine` | carousel.status `none` | [How I Turned My Habits into an "Engine"](https://medium.com/hello-love/how-i-turned-my-habits-into-an-engine-to-get-me-to-my-goals-bec9f9402ec6) (06-15) | high |
| 06-19 | Carousel | [DZwQ1zjjcML](https://www.instagram.com/mistakenlyhuman/p/DZwQ1zjjcML/) | same (byte-identical repost) | same | same | high |
| 07-09 | Carousel | [Dakx96Oj6ps](https://www.instagram.com/mistakenlyhuman/p/Dakx96Oj6ps/) | `2026-07-06_life_self_dev_your-overloaded-self-improvement-schedule-is-slowly-making-y` | carousel.status `created` | [Your Self-Improvement Schedule…](https://medium.com/write-a-catalyst/your-self-improvement-schedule-is-slowly-making-you-someone-you-dont-recognize-1f54c98806ce) (07-26) | high |
| 07-20 | Carousel | [DbAZemRD003](https://www.instagram.com/mistakenlyhuman/p/DbAZemRD003/) | `2026-05-26_life_self_dev_mental-health-openness-and-breaking-stigmas` | carousel.status `posted` ✓ | [The Silent Killer No One Talks About](https://aninjusticemag.com/the-silent-killer-no-one-talks-about-and-its-not-what-you-think-4680ca8fd155) (06-19) | high |
| 07-23 | Carousel | [DbJC0yDjNym](https://www.instagram.com/mistakenlyhuman/p/DbJC0yDjNym/) | `2026-05-27_poetry_quotes_intoxicated-senses` | carousel.status `scheduled` | [You're Not in Love. You're Hungover.](https://medium.com/weeds-wildflowers/youre-not-in-love-you-re-hungover-6dee883b512f) (06-16) | high |
| 07-27 | Carousel | [DbSs68vj1Qo](https://www.instagram.com/mistakenlyhuman/p/DbSs68vj1Qo/) | `ORPHAN:pushkar-photo-carousel` (or `ORPHAN:pushkar-musician-reel`) | carousel.status `created` | — (no Medium piece) | med |
| 07-28 | Reel | [DbVz85-jYsK](https://www.instagram.com/mistakenlyhuman/reel/DbVz85-jYsK/) | `2026-06-30_life_self_dev_the-5-minute-habit-that-replaced-3-hours-of-self-help-conten` | reel.status `rendered`, reel.ig `created` | [The 3 Hours You Spend on Self-Help Content…](https://medium.com/illumination/the-3-hours-you-spend-on-self-help-content-are-making-you-worse-at-self-improvement-8dc595da2109) (07-14) | high |
| 07-30 | Reel | [DbbEct1Dby5](https://www.instagram.com/mistakenlyhuman/reel/DbbEct1Dby5/) | `ORPHAN:pushkar-fish-poem` ("Birds Don't Look Back") | reel.status `rendered`, reel.ig `—` | — (no Medium piece) | high |

### 15 captionless June reels — unmatchable

Dated 2026-06-15 → 06-21, no caption text on the post page (copy lives as in-video overlay only), so
there is nothing to match against a tracker title:

`DZnQECBlNZ4` `DZlpD_qgVph` `DZp03ixEXRL` `DZoN2ypjdOE` `DZsZp0gm0vx` `DZqyqsnjAK4` `DZu-cL2D6hC`
`DZtXcnFiCL3` `DZxjPhGFK5n` `DZv8PqtG4u6` `DZ0IBcZgZ-b` (caption is `❤` only) `DZyhCD2Fay7`
`DZ2s1U3AWNV` `DZ2s1obkvJe` `DZ1F3yRCUgc`

Counts verified programmatically: 25 total = 10 captioned + 15 captionless.

---

## Tracker gaps this exposes

Nothing below has been written to `content-tracker.md` — these are proposed edits awaiting Tarun's call.

### 1. Rows posted on Instagram that the tracker doesn't reflect

| Slug | Field | Current | Should be |
|---|---|---|---|
| `ORPHAN:automated-job-hunting-script` | reel.status / reel.ig | `none` / `—` | `posted` / IG URL |
| `ORPHAN:claude-primitive-beast-token-cut` | reel.status / reel.ig | `none` / `—` | `posted` / IG URL |
| `2026-05-31_..._the-one-skill-that-makes-you-good-at-ai` | carousel.status, reel.status | `scheduled`, `script` | `posted` (both, two IG assets) |
| `2026-07-06_..._the-local-ai-agent-i-built-in-a-weekend…` | carousel.status | `created` | `posted` |
| `2026-05-25_..._python-for-data-science-tutorial-210` | carousel.status | `scheduled` | `posted` |
| `2026-06-26_..._what-hiring-managers-think…` | reel.ig | `created` | IG URL |
| `ORPHAN:safe-and-alive` | carousel.status | `none` | `posted` |
| `ORPHAN:how-i-turned-my-habits-into-an-engine` | carousel.status | `none` | `posted` |
| `2026-07-06_life_self_dev_your-overloaded-self-improvement-schedule…` | carousel.status | `created` | `posted` |
| `2026-05-27_poetry_quotes_intoxicated-senses` | carousel.status | `scheduled` | `posted` |
| `ORPHAN:pushkar-photo-carousel` | carousel.status | `created` | `posted` |
| `ORPHAN:pushkar-fish-poem` | reel.status / reel.ig | `rendered` / `—` | `posted` / IG URL |
| `2026-06-30_life_self_dev_the-5-minute-habit…` | reel.ig | `created` | IG URL |

### 2. `reel.ig` holds non-URL values in three rows

The tracker header states `reel.ig` is a **link** column — "a full `https://…` or `—`, never a date".
Three rows violate it: two hold the literal string `created`
(`2026-06-26_..._what-hiring-managers…`, `2026-06-30_life_self_dev_the-5-minute-habit…`) and one holds
a sentence (`ORPHAN:pushkar-musician-reel` → `not publishing — creator decision 2026-07-20`).
Real IG URLs are now available for the first two.

### 3. Duplicate rows for the same Medium article

Two articles have both a slug row and an ORPHAN row:

| Article | Slug row | ORPHAN row |
|---|---|---|
| Python Silently Lied to You | `2026-05-25_..._python-for-data-science-tutorial-210` | `ORPHAN:python-silently-lied-to-you` |
| The Silent Killer No One Talks About | `2026-05-26_life_self_dev_mental-health-openness-and-breaking-stigmas` | `ORPHAN:the-silent-killer-no-one-talks-about` |

In both cases the slug row carries the working title and the ORPHAN row the published Medium title.
Merging them is a judgement call — the tracker says never delete a row.

Separately, two published Medium pieces exist **only** as ORPHAN rows, with no blog slug behind them:
`ORPHAN:safe-and-alive` and `ORPHAN:how-i-turned-my-habits-into-an-engine`. Both have a posted IG
carousel, so they are real published pieces that never got a slug row.

### 4. `medium.url` is `—` on published rows where the URL is known

Ten of the rows above are `medium.status: published` with `medium.url: —`, even though
`data/analytics/medium-stats-2026-08-11.json` carries the canonical URL. The Medium URLs in the tables
above can backfill them.

### 5. Instagram analytics fetch is silently broken

`data/analytics/instagram_posts.json` last entry is **2023-03-09** despite `instagram_state.json`
recording `last_run: 2026-03-28`. The incremental Graph API fetch has been returning nothing for
three years' worth of posts — which is why this cross-reference needed a browser scrape.

### 6. A production note shipped into a live caption

`DZpqksgjP9v` (06-16) and `DZqryR2jfAN` (06-17) both open with
`Why: Emotional narrative arc with intimate visuals...`. Their captions are byte-identical (642 chars,
same MD5), so it is one asset posted twice rather than two separate leaks — but that asset is public
with the internal note attached.

---

## Coverage

- **18 of 35** IG posts map to a 2026 Medium article.
- **20 of 35** map to a `content-tracker.md` row.
- **15** are unmappable captionless reels.
- **18 of 33** 2026 Medium articles have no IG post at all: The One-Word Test (08-04) · Pandas Isn't a
  Beginner Library (08-05) · The Career-Killing Meeting Habit (08-11) · Your "Production" MLOps Pipeline
  (07-30) · A Junior Beat a 10-Year ML Veteran (07-28) · What Interviewers Actually Write (07-23) ·
  Stop Trusting Your Gut (07-22) · The Skill Every High-Performer Has (07-21) · You Don't Need
  Mastodon.py (07-17) · Ten Years Of Independence (07-16) · I Woke at 6AM for 90 Days (07-15) · How to
  Build a Wake-Up Ritual (07-13) · Everyone Building RAG (07-11) · I Scraped 1,003 DS Job Postings
  (07-07) · You're Still Paying $200/Month for AI Tools (06-30) · The Room No One Entered (06-26) ·
  You'll Never Actually Reach This Goal (06-19) · I Deleted Three Weeks of Content (06-08).
