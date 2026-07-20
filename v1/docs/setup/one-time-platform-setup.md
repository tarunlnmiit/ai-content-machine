---
title: "One-Time Platform Setup — Instagram, LinkedIn, Threads + Meta Graph API"
type: doc
slug: one-time-platform-setup
tags: [content/doc]
---
# One-Time Platform Setup — Instagram, LinkedIn, Threads + Meta Graph API

Do each section below once. These settings persist and compound over time. Most creators skip this and wonder why their content doesn't grow — the profile is the landing page. If someone finds a reel, thread, or post compelling, they immediately tap your profile. What they see in the next 5 seconds determines whether they follow.

> **Twitter/X is dropped** from the pipeline (dead in analytics). The Twitter/X profile section below is kept for reference only — no action needed.

---

## Meta Graph API — auto-publish credentials (Instagram / Facebook / Threads)

This is what lets the `scheduler.py` daemon auto-publish instead of you posting by hand.
Do it once; tokens are long-lived. See `scripts/lib/meta_graph.py` for how they're used.

1. **Convert IG to a Business/Creator account** (above) and **link it to a Facebook Page**
   (Meta Business Suite → Settings → Accounts). IG content-publishing requires this link.
2. **Create a Meta app** at developers.facebook.com → My Apps → Create App (type "Business").
   Add the products: *Instagram Graph API*, *Facebook Login*, and *Threads API*.
3. **Generate a long-lived access token** with scopes:
   `instagram_basic, instagram_content_publish, pages_read_engagement, pages_manage_posts`
   (Graph API Explorer → exchange the short-lived token for a 60-day token, then refresh).
4. **Find your IDs:** `IG_USER_ID` (Graph API: `me/accounts` → page → `instagram_business_account`),
   `META_PAGE_ID` (the linked Page), and for Threads `THREADS_USER_ID` + a separate
   `THREADS_ACCESS_TOKEN` (Threads API has its own token flow).
5. **Put them in `.env`:**
   ```
   META_GRAPH_VERSION=v21.0
   META_ACCESS_TOKEN=...
   IG_USER_ID=...
   META_PAGE_ID=...
   THREADS_ACCESS_TOKEN=...
   THREADS_USER_ID=...
   ```
6. **Verify:** start the daemon — `scheduler.py` logs a credential check at startup
   (`instagram=ok / facebook=ok / threads=ok`). Only platforms with valid creds fire.

Reminder (honesty guardrail): IG publishes **Reels / single image / carousel** and ingests
from a **public media URL** (host the asset first — Drive). IG Stories are not API-publishable;
keep those manual. Recording, the ~10-min approval, and comment/DM replies stay human.

---

## Instagram — @mistakenlyhuman + @breathofdatascience

Do these steps for BOTH accounts separately.

### 1. Account type → Professional (Creator)

1. Instagram → Profile → ☰ (top right) → Settings → Account
2. Tap **Switch to Professional Account**
3. Choose **Creator** (not Business — Creator gives you better analytics and DM categorisation)
4. Category: select the closest fit
   - @breathofdatascience → "Education"
   - @mistakenlyhuman → "Personal Blog"
5. Keep account public
6. Connect to a Facebook Page if prompted (optional — enables cross-posting to Facebook)

Why: Creator accounts unlock Instagram Insights (saves ÷ views, non-follower reach %) which are the two metrics you track every Sunday. Without a Creator account, those numbers are hidden.

---

### 2. Bio formula — 150 character limit, every word earns its place

**Formula:** `[What you do] → [Who it's for] → [What they get]` + single CTA line + link

**@breathofdatascience — current bio rewrite:**
```
Data science, simplified.
Python • ML • Real projects
10 years → your shortcut
↓ Free resources
[link-in-bio URL]
```

**@mistakenlyhuman — current bio rewrite:**
```
Writing about the things we feel but don't say.
Life · Mental health · Poetry
↓ Read the full pieces
[link-in-bio URL]
```

**Rules:**
- No emojis cluttering the first line — the first line is your headline, not decoration
- The link goes to a link-in-bio page (not directly to Medium or Substack — you want one hub)
- Add a line break before the link CTA so it's visually separate
- Do NOT put your email in the bio — it wastes character space

---

### 3. Link-in-bio setup

Use [SuperProfile](https://superprofile.bio) (you already have an account for DM automation) or a simple Linktree.

For each account, the link-in-bio page should have:
- **@breathofdatascience:** YouTube channel → Medium → GitHub (if relevant)
- **@mistakenlyhuman:** Medium → Podcast (Spotify)

Order matters — put the destination you want most clicks on first.

After setting up, update both bios with the SuperProfile link. Use the same URL format:
- `superprofile.bio/breathofdatascience`
- `superprofile.bio/mistakenlyhuman`

---

### 4. Highlights — organise your back catalogue

Highlights are visible on your profile below the bio. New visitors browse them before following.

**@breathofdatascience — create these Highlight folders:**
- "Python" — your best Python reels + tips
- "ML Projects" — machine learning explainers
- "Tools" — AI tools, Copilot, LLM reels
- "Resources" — anything where you give away free tools/worksheets

**@mistakenlyhuman — create these Highlight folders:**
- "Mental Health" — your best mental health reels
- "Poetry" — spoken-word clips + poem reveals
- "Life" — self-development reels
- "About" — 1 reel introducing you and what this account is about

**How to create a Highlight:**
1. Go to any Story you've posted (or archive) → tap "Highlight"
2. Create new Highlight → name it → choose cover (use a consistent solid-colour cover per folder)
3. Add relevant past Stories to it

If you haven't posted Stories yet: come back to this after W22 is live.

---

### 5. Instagram Settings → Content preferences

1. Settings → Privacy → Story → Allow message replies: **Everyone**
2. Settings → Privacy → Reels → Allow remixing: **ON** (this lets others remix your reels — free amplification)
3. Settings → Notifications → Direct Messages: **ON** for all (you need to see keyword DMs immediately during the 2-hour window)
4. Settings → Privacy → Comments → Allow comments from: **Everyone** (never restrict this)

---

### 6. Pinned posts (3 slots)

Instagram allows you to pin up to 3 posts to the top of your grid. Pin:
1. Your best-performing reel (highest saves ÷ views)
2. An introduction / "what this account is about" reel
3. Your most shareable piece (the one you'd show a new follower first)

To pin: open the post → three dots (⋯) → **Pin to your profile**

Update the pinned posts monthly or whenever a new reel significantly outperforms old ones.

---

## LinkedIn — linkedin.com/in/tarun-gupta-in

### 1. Turn on Creator Mode

1. Go to your LinkedIn profile
2. Scroll down to "Resources" section
3. Click **Creator mode** → toggle ON

Why: Creator mode changes your profile button from "Connect" to "Follow" — much better for a content creator. It also unlocks LinkedIn Newsletter, LinkedIn Live, and detailed post analytics. Do this immediately.

---

### 2. Headline — not your job title

Your headline appears under your name everywhere on LinkedIn. 99% of people use "Data Scientist at [Company]" — which tells a follower nothing about why to follow you.

**Formula:** `[What you create] for [who] | [platform or result]`

**Rewrite your headline to:**
```
Data Science Content Creator | Making ML & Python concepts actually make sense | @breathofdatascience
```

Or more personal:
```
10-year Data Scientist | I write about the parts of DS they don't teach you | Medium + YouTube + IG
```

**Rules:**
- 220 character limit
- Include at least one keyword people search for ("data science", "Python", "machine learning")
- Include your Medium profile URL so people can find your writing
- No "Passionate about…" or "Helping companies…" — these are filler

---

### 3. About section — first 3 lines are the hook

LinkedIn collapses the About section after 3 lines. The first 3 lines are your only chance to make someone click "see more."

**Apply the same hook rule from Tuesday's Viral Readiness Audit.**

**Current About rewrite — first 3 lines:**
```
I've spent 10 years as a data scientist. Most of what I learned came from breaking things, not courses.

I write about that — the bugs, the failed models, the shortcuts that actually work.

Every week: Python, ML, and data science explained like a colleague who's already made the mistakes.
```

After the first 3 lines (behind "see more"), add:
- Where to find you: "👉 Medium: medium.com/@tarun-gupta"
- YouTube: "@breathofdatascience"
- Instagram: "@breathofdatascience"

---

### 4. Featured section — pin your best work

The Featured section sits prominently on your profile and is the first thing many visitors see after the header.

Add these in order:
1. **Your Medium profile** — add `medium.com/@tarun-gupta` as a "Link" item, write a 1-line description: "Weekly data science breakdowns, every Monday"
2. **Your best-performing LinkedIn post** — tap "+" → "Add a post" → find your highest-engagement post
3. **Your YouTube channel** — add the channel URL as a "Link"

Update Featured whenever a post performs significantly better than the current one in slot 2.

---

### 5. Custom LinkedIn URL

Your URL should already be `linkedin.com/in/tarun-gupta-in`. If not:
1. Profile → Edit profile → scroll to "Edit public profile & URL" (top right)
2. Set it to your name or handle — no numbers, no random characters

---

### 6. Notification settings → tune for engagement

1. Settings → Notifications → Posts, Articles and Videos
   - Comments on your posts: **ON**
   - Reactions to your posts: **ON** (so you can reply quickly during the engagement window)
2. Settings → Notifications → Messages: **ON**

---

### 7. Connection vs. Follow strategy

LinkedIn limits connections to 30,000. Once you're past ~2,000 followers, prioritise **followers** over connections. Creator Mode already sets new visitors to default "Follow" instead of "Connect."

For now: accept all relevant connection requests (data scientists, content creators, tech professionals). Decline or ignore unrelated ones (MLM, recruiters for roles you'd never take).

---

## Twitter/X — @mistakenlyhuman — DROPPED (reference only, no action)

### 1. Profile photo + header

- **Profile photo:** Same as Instagram — visual consistency across platforms builds recognition
- **Header image:** Use a 1500×500px image that communicates your niche. For @mistakenlyhuman: a moody, literary aesthetic image with your Medium handle overlaid. You can export a custom header from Canva.

---

### 2. Bio — 160 characters, keyword-rich

**Formula:** `[What you write about] | [How often / where] | [1 human detail]`

**Rewrite:**
```
Writing about the parts of life we feel but don't say. Poetry + mental health + self-development. New pieces weekly → medium.com/@tarun-gupta
```

Or DS-angle for the handle (if you cross-post DS content here too):
```
Data scientist by day. Writer at night. Python • ML • the human side of data. @breathofdatascience for the tech stuff.
```

**Rules:**
- Include your Medium URL directly in the bio (not in a link-in-bio — Twitter/X shows it prominently)
- Or use the "Website" field on your profile for the link, and keep the bio text clean
- No "DMs open" — it's implied and wastes space

---

### 3. Pinned tweet — your best work, always current

The pinned tweet is the first thing anyone sees when they visit your profile.

**Pin your single best-performing thread.** Not a new one — the one with the most replies or retweets. Rotate it monthly or whenever a new thread significantly outperforms the current pin.

**How to pin:** open the tweet → three dots → **Pin to your profile**

The pinned tweet also doubles as your implicit pitch: "this is the quality of what I write." Make sure it represents you well.

---

### 4. Twitter settings → turn on notifications for replies

1. Settings → Notifications → Filters
   - Quality filter: **OFF** (this filters out accounts with no followers — but those early replies from small accounts still matter for the algorithm)
2. Settings → Notifications → Push notifications → Replies: **ON**
3. Settings → Privacy → Direct Messages → Allow message requests from: **Verified users + people you follow** (limits spam while keeping DMs open for real responses)

---

### 5. Lists — curate your engagement targets

Create one private Twitter List called "Engage" and add 20–30 accounts in your niches (DS Twitter, mental health writers, poetry accounts) that you genuinely find interesting. Every day before posting, spend 5 minutes replying to 3–5 tweets from this list.

Why: replies you leave on other accounts' tweets show up in your followers' feeds ("Tarun replied to X"). It's free amplification and builds relationships with accounts that may retweet you later.

**How to create a list:** Profile → Lists → Create list → name it "Engage" → set to private → add accounts

---

## Summary: do-once checklist

**Instagram — both accounts:**
- [ ] Switched to Creator account
- [ ] Bio rewritten (formula: what + who + what they get + CTA)
- [ ] Link-in-bio page set up on SuperProfile, URL in bio
- [ ] Highlights created with cover images
- [ ] Allow remixing: ON
- [ ] 3 posts pinned to grid

**LinkedIn:**
- [ ] Creator Mode: ON
- [ ] Headline rewritten (value proposition, not job title)
- [ ] About section — first 3 lines are a hook
- [ ] Featured section: Medium link + best post + YouTube
- [ ] Custom URL confirmed: linkedin.com/in/tarun-gupta-in
- [ ] Notifications on for comments and reactions

**Twitter/X:**
- [ ] Profile photo matches Instagram
- [ ] Header image: 1500×500px, on-brand
- [ ] Bio rewritten (160 chars, includes Medium URL)
- [ ] Best thread pinned to profile
- [ ] Quality filter: OFF
- [ ] Reply notifications: ON
- [ ] "Engage" list created with 20–30 accounts

---

*Do this once, then forget it. Review once every 3 months to update pinned posts and Featured section as newer work outperforms old.*
