---
type: script
week: 2026-W28
slug: 1003-data-science-job-postings
platform: yt
tags: [content/script, week/2026-W28]
---
SHOW: Breath of Data Science
EPISODE TITLE (working): I Scraped 1,003 Data Science Job Postings — 87% Want This One Thing
TARGET RUNTIME: ~8 minutes
WORD COUNT: 1,150

<!-- Recording/edit: green-screen talking-head → Palmier Pro composites background → Hyperframes edit run separately by Tarun. This is a DATA-STORY, not a code tutorial → talking-head spine. [PALMIER_BG:] = background direction. [SCREEN:]/[BROLL:] are OPTIONAL loose data-viz cutaway hints for the separate Hyperframes pass (bar charts, quotes, before/after) — NOT a screen-recording shot list and NOT gated on runnable code. -->

[PALMIER_BG: cold dark tech backdrop, deep navy #0a0e1a, faint cyan grid, subtle data-stream motion]

I scraped 1,003 data science job postings over thirty days. And 87% of them wanted the same thing — but it's not the skill you'd guess from your feed. It's not deep learning. It's not whatever framework is trending on X this week. It's more boring than that, and more specific, and once you see it you can't unsee how big the gap is between what's loud online and what actually gets hired.

If you're job-hunting in data science right now, you've probably assumed the market wants the flashy stuff. I assumed that too. So instead of guessing, I let the postings tell me. Thirty days, a thousand real listings, one number that kept repeating. Let me show you what the data actually said — and then the part that genuinely surprised me.

[BROLL: someone scrolling endless job listings late at night, screen glow on their face]

Here's how the skills stacked up. Machine learning showed up in 73% of postings. Python, 62%. Then it drops — LLM experience 31%, generative AI 28%, NLP 20%. Deep learning, only 15%. PyTorch 12, TensorFlow 11 — and notice PyTorch now beats TensorFlow. SQL, weirdly, 9%. Cloud — AWS out front around 7%.

[SCREEN: horizontal bar chart, skills ranked by % of postings — ML 73, Python 62, LLM 31, GenAI 28, NLP 20, DL 15, PyTorch 12, TF 11, RAG 10, MLOps 10, SQL 9]

So the baseline is unglamorous and non-negotiable: strong Python plus machine learning fundamentals. Nearly every role expects it regardless of level. That's the 87% story — machine learning and Python are the thing almost everyone asks for, and most candidates still bury it or say it in language the posting isn't scanning for. The second layer is where it gets interesting: the modern postings lean on LLM, GenAI, and RAG language, and the cloud and MLOps tooling only shows up when a role is production-facing instead of research-facing.

[PAUSE]

Now the posting that stopped me. Most job descriptions say "experience with LLMs" and move on. One didn't. It was an AI Engineer role, digital health, DACH region, remote, posted through an agency for a MedTech client. And buried in the responsibilities was this line.

[SCREEN: pull-quote card — "Improve and scale hybrid AI systems combining probabilistic logic and LLM-based reasoning"]

Read that twice. They're not asking for someone who's played with GPT wrappers. They want someone who can bridge old-school probabilistic, rule-based reasoning with modern LLM reasoning, in one hybrid system. And in healthcare that makes complete sense — you need the explainability of deterministic logic and the flexibility of an LLM, because a clinical audit trail cannot say "the model felt like it." That single posting reads like a mid-to-senior specialist hire hiding under a plain title. That's the signal underneath the noise.

Okay — here's the pattern interrupt, the part that reframed how I read the whole market. Deep learning, the technical foundation under the entire LLM wave, showed up in only 15% of postings. And LangChain — the framework that's dominated AI-engineering discourse for two straight years — showed up in 3%. Thirty-six postings out of a thousand.

[SCREEN: two big numbers side by side — "Deep Learning: 15%" and "LangChain: 3% (36 / 1,003)"]

[PAUSE]

That's not because the skill isn't needed. It's rebranding. "Deep learning" is old vocabulary now — the same neural-net competency got repackaged as LLM, GenAI, AI Engineer. Recruiters write to whatever term is trending, not the academic layer underneath. LangChain is a different story: it hyped hard, hit a backlash over painful debugging and over-abstraction, and teams started reaching for raw API calls instead. So hiring managers write around outcomes — "build a RAG pipeline" — not tool names. Add in that most postings are templated by recruiters, not the engineers who'll use the tool, and you get a language layer that lags the real stack by months. The skill is still required. It's just unlabeled.

[BROLL: a whiteboard with "what's hyped" and "what's hired" as two columns, the gap between them circled]

Here's where this stopped being trivia and changed something. I ran my own client applications through the same filter, and most of their resumes had gone stale against exactly this gap.

[PERSONAL_INSERT: I used to coach candidates to write "I have Python, SQL, and Tableau skills" — that generic list HR skims right past. After the scrape, I had them do one thing: find the gap in the tracker data, then rewrite the top bullet by name and by number. So instead of "Tableau skills," it became "built a pipeline that cut manual QA from six hours to forty-five minutes a week." Same person. Same actual skills. The recruiter reply rate jumped, and two interviews landed in the same week. The lesson wasn't "go learn a new skill." It was "say the skill you already have in the language the posting is scanning for."]

[SCREEN: before/after resume line — Before: "Python, SQL, Tableau skills" → After: "Built pipeline, cut manual QA 6h → 45min/week"]

Now, I have to be honest about where my own methodology broke, because it did, in five real ways. The biggest one: I classified roles on the title alone. A job titled plain "Software Engineer" doing heavy ML work never got counted, because the filter never read the description. That one flaw poisons everything downstream — so if I ran this again, I'd classify on the description content, not the title, ideally with a small LLM pass asking "is this substantively ML work?" The others: no dedup across cross-posted roles, no weighting for must-have versus nice-to-have, a broken regex that basically erased R from my data, and a scraper bug gluing some titles together. I'm telling you this because a number without its flaws is just a vibe.

[BROLL: a terminal scrolling, then a red underline appearing under one line of a config]

So say you have zero of the standout skill — the LLM, RAG, GenAI application building, not classical ML. Here's the path I'd actually run, and it's not a course syllabus. Week one, build immediately — get comfortable with chat completions, streaming, and tool calling, and ship one trivial thing, a Slack bot or a CLI tool. Skip the theory videos. Then build a RAG pipeline from scratch with no framework, so you feel the chunking and retrieval pain before an abstraction hides it — then rebuild the same thing with LangChain or LlamaIndex, so you actually know what the abstraction buys you. Week three, build one agent with a tool-calling loop on a real messy task. Week four, add an eval set, score the outputs, containerize it, and deploy it somewhere real so you hit rate limits and cost tradeoffs firsthand.

Four weeks, three to four hours a day, if your Python's already there. Courses front-load transformer math and backprop that shows up in almost none of these descriptions. What shows up is "built and shipped a working system." A scrappy, deployed project with a public repo and a live demo link outweighs a certificate for nearly every posting in this dataset. None of them asked for a specific cert. All of them, implicitly, rewarded "show me" over "tell me."

[PAUSE]

The gap between what's loud on Twitter and what's actually in the requisition is where most job searches quietly go wrong. So before you go learn the trending thing, go audit what you already have against what's actually being asked.

I turned this whole scrape into a resume-audit worksheet you can run on your own applications — it's free, and the link's in the description. Grab it, run your top three bullets through it, and tell me in the comments which skill you'd been underselling. Subscribe and stick around — next week I'm taking the same 1,003 postings and showing you which three cities and role titles are quietly paying the most for the exact same stack.

[OVERLAY/outro tease if wanted — "Next: where these skills actually pay the most"]

---

## 3 TITLE OPTIONS

1. I Scraped 1,003 Data Science Job Postings — 87% Want This One Thing (search + hook)
2. Data Science Job Skills 2026: What 1,003 Real Postings Actually Ask For (search-optimised)
3. The Skill Every DS Job Wants — and Almost No One Puts on Their Resume (curiosity)

## YOUTUBE DESCRIPTION

I scraped 1,003 data science job postings over 30 days. 87% wanted the same thing — and it's not deep learning, and it's not the framework trending on your feed. Here's what the data actually said, the one posting that surprised me, what's hyped but barely hired, and the 4-week rebuild I'd run to close the gap.

I also break down the five ways my own methodology broke — because a number without its flaws is just a vibe.

📄 Full post: medium.com/@tarun-gupta/afdbc3bd8d99
📸 Instagram: @mistakenlyhuman

📄 FREE RESUME-AUDIT WORKSHEET — run this scrape on your own applications
https://worksheets-thebreathnetwork.vercel.app/get-worksheet/i-tracked-every-data-science-job-posting-for-30-days-heres-t

🔗 SKILL FREQUENCIES (from 1,003 postings)
ML 73% · Python 62% · LLM 31% · GenAI 28% · NLP 20% · Deep Learning 15% · PyTorch 12% · TensorFlow 11% · RAG 10% · MLOps 10% · SQL 9% · LangChain 3%

TIMESTAMPS
00:00 — 1,003 postings, one number that repeated
01:20 — The skill frequencies, ranked
02:40 — The posting that surprised me
04:00 — What's hyped but barely hired
05:30 — How I rewrote one resume bullet
06:30 — Where my methodology broke
07:20 — The 4-week rebuild if you're starting from zero

---
Breath of Data Science: data science, Python, and machine learning explained the way a colleague would — with the mistakes included.

📌 PINNED COMMENT: Which skill had you been underselling on your resume — saying it in generic words instead of the language the posting scans for? Drop it below.

## THUMBNAIL PROMPT (ChatGPT image-gen 2.0 — use my photo, surprise reaction)

Use the provided photo of me. Dark high-contrast tech background, deep navy with faint cyan data-grid glow. Me on the right with a genuine surprised / eyebrows-raised reaction expression, lit with cool blue rim light. On the left, one huge bold number in bright cyan-white sans-serif reading "87%", and a small stylized horizontal bar-chart motif beneath it (a few bars of different lengths). Max 3–4 words of secondary text under the number reading "wanted ONE thing". High contrast, clean, readable at small size, no clutter, no logos.
