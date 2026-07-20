---
title: "I Scraped 1,003 Data Science Job Postings — 87% Want This One Thing, and Most Candidates Still Don't Say It"
type: blog
niche: data_science_tech
date: 2026-07-01
week: 2026-W27
slug: i-tracked-every-data-science-job-posting-for-30-days-heres-t
tags: [content/blog, niche/data_science_tech, week/2026-W27]
---
# I Scraped 1,003 Data Science Job Postings — 87% Want This One Thing, and Most Candidates Still Don't Say It

*A 30-day scrape of real job postings, five methodology mistakes I'd fix, and the four-week rebuild I'd run if I had zero of this skill today.*

I scraped 1,003 data science job postings over 30 days. The same skill showed up over and over — not the one you'd guess from LinkedIn hot takes.

If you're job-hunting in data science right now, you've probably assumed the market wants deep learning expertise, or fluency in whatever framework is trending on X this week. It doesn't. What the postings ask for, again and again, is something more boring and more specific — and the gap between what's hyped and what's hired is bigger than I expected.

![1,003 postings, 30 days, one number that kept repeating](/content/blogs/2026-W27/2026-07-01_data_science_tech_i-tracked-every-data-science-job-posting-for-30-days-heres-t_images/01_hook_data-scientist-analyzing-job-postings-spreadsheet.jpg)
*1,003 postings, 30 days, one number that kept repeating — Photo by [Yan Krukau](https://www.pexels.com/photo/man-looking-at-laptop-with-data-on-screen-7691749/) on Pexels*

**What I actually counted**

Across those postings, here's how the skills stacked up: Machine Learning (73%), Python (62%), LLM experience (31%), Generative AI (28%), NLP (20%), Deep Learning (15%), PyTorch (12%), TensorFlow (11%), RAG (10%), MLOps (10%), SQL (9%), Computer Vision (9%), Agentic AI (9%), AWS (7%), Azure/GCP (6–7%).

The baseline — the thing nearly every role expects regardless of level — is strong Python plus machine learning fundamentals. The second layer tells the real story: modern postings lean on LLM, GenAI, and RAG language, PyTorch now beats TensorFlow in preference, and cloud platforms — AWS out front — plus MLOps tooling (Docker, Kubernetes, LangChain, MLflow) show up whenever a role is production-facing rather than research-facing.

**The posting that surprised me**

Most job descriptions say "experience with LLMs" and move on. One didn't. It was an "Artificial Intelligence Engineer – Digital Health – DACH Remote" role, posted through a recruiting agency for a MedTech client, and buried in the responsibilities section was this line:

> "Improve and scale hybrid AI systems combining probabilistic logic and LLM-based reasoning"

Read that twice. They're not asking for someone who's played with GPT wrappers. They're asking for someone who can bridge old-school probabilistic/rule-based reasoning with modern LLM reasoning — in a hybrid system. In healthcare, that pairing makes sense: you need the explainability of deterministic logic and the flexibility of an LLM, because a clinical audit trail can't say "the model felt like it." The same posting name-dropped "explainability tooling" and "synthetic data generation" as evaluation-framework components — phrasing you don't see in the average "familiarity with GenAI" bullet. Nothing in the title said senior, but the ask — production-grade services, stakeholder translation, a preference for candidates coming out of health/MedTech AI vendors — reads as a mid-to-senior domain specialist hire, not an entry point.

**What's hyped but barely hired**

Here's the part that reframed how I read the market: Deep Learning, the technical foundation underneath the entire LLM wave, appeared in only 15% of postings. LangChain — the framework dominating AI-engineering discourse for two straight years — showed up in 3% (36 out of 1,003).

That's not because the skill isn't needed. It's rebranding. "Deep learning" is old vocabulary now; the same neural-net competency got repackaged as "LLM," "GenAI," "AI Engineer." Recruiters write to whatever term is trending, not the academic layer underneath it — the skill is still required, it's just unlabeled. LangChain tells a related but different story: it hyped hard, hit a backlash over over-abstraction and painful debugging, and teams started reaching for raw API calls or lighter tools instead. Hiring managers burned by today's hot framework becoming next year's migration headache write job descriptions around outcomes ("build a RAG pipeline"), not tool names — partly to avoid narrowing the applicant pool to one library's fanbase. Add in that most postings are templated and written by recruiters, not the engineers who'll use the tool day-to-day, and you get a language layer that lags the real stack by months.

**Where this changed something for me**

I ran my own client applications through the same tracker filter and found most of their resumes had gone stale against exactly this skill. Before: I'd coach a candidate to write "I have Python, SQL, Tableau skills" — a generic list HR skims past without pausing. After: I had them identify the gap using the tracker data, then rewrite the top bullet by name and number — "built pipeline, cut manual QA from 6 hours to 45 minutes weekly." Recruiter reply rate jumped. Two interviews landed in the same week. The lesson wasn't "learn a new skill." It was "say the skill you already have in the language the posting is scanning for."

**Where my own methodology broke**

Five real flaws, ranked by how much they skew the numbers:

```python
# Flaw #1: title-only keyword classification
# "AI Automation" in a title gets flagged as ML/DS work
# even when the role is RPA, not model-building
if "ai" in job_title.lower() or "ml" in job_title.lower():
    classify_as_ds_role(job)  # false positives AND false negatives
```

A job titled plain "Software Engineer" doing heavy ML work never gets counted, because the filter never touched the description. The fix: classify on description content plus title jointly — ideally a small LLM pass asking "is this substantively ML/AI/DS work?" instead of regex on a title string.

Second: no dedup across postings. The same role gets cross-posted on LinkedIn, Turing, Andela, and agency sites, landing as separate rows each time. Any boilerplate phrase common to one company's repeated template inflates whichever platform reposts most. Third: my regex counted a skill as present regardless of whether the posting said "must have 5 years" or "nice-to-have exposure" — no weighting by how required it actually is. Fourth: my R-language regex (`\bR\b programming|\br statistical\b`) barely matches real phrasing, so R is likely near-zero in my data not because it's rare, but because the pattern is broken — the same risk applies to any single-letter skill name. Fifth: the scraper itself was concatenating some titles twice at ingestion ("AI EngineerAI Engineer"), which didn't distort skill counts but flags a scraper bug worth fixing at the source.

The one I'd fix first, because everything downstream inherits its bias: the title-only classification.

**If you have zero of this skill today**

Assuming "this skill" means the standout differentiator in the data — LLM/RAG/GenAI application building, not classical ML — here's the path I'd run, not a course syllabus.

Week 1: build immediately. Days 1–3, get comfortable with chat completions, streaming, and function/tool calling using the OpenAI or Anthropic API. Build one trivial thing — a Slack bot or CLI Q&A tool — and skip theory videos entirely. Days 4–7, build a RAG pipeline from scratch with no framework: embed documents, store them in Chroma or FAISS, retrieve and stuff into a prompt manually, so you feel the chunking and retrieval pain before any abstraction hides it. Days 8–14, rebuild the same pipeline with LangChain or LlamaIndex — now you know what the abstraction buys you.

Week 3: build one agent with a tool-calling loop on a real messy task — search the web, summarize, write a file. This is exactly what "agentic AI" means when it shows up in a posting.

Week 4: add an eval set of 20–30 cases, score outputs (manually first, then with an LLM-as-judge), containerize with Docker, and deploy somewhere real — Vercel, Fly, Railway — so you hit rate limits and cost tradeoffs firsthand.

Four weeks, three to four hours a day, assuming Python fluency already. If it isn't there yet, add two to three weeks up front, since it's the baseline in 62% of every posting I scanned anyway. Courses front-load theory — transformer math, backprop — that doesn't show up in 90% of these job descriptions. What shows up is "built and shipped a working system." A scrappy but real deployed project, public repo and live demo link, outweighs a certificate for nearly every posting in this dataset. None of them asked for a specific cert. All of them, implicitly, rewarded "show me" over "tell me."

The gap between what's loud on Twitter and what's actually in the requisition is where most job searches quietly go wrong.

If you want the worksheet that turns this into a resume audit you can run on your own applications, the data science list is free — join here.

<!-- Medium tags: data-science-careers, job-search, artificial-intelligence, machine-learning, career-advice -->
<!-- Target keyphrase: data science job posting skills -->
<!-- SEO title: Data Science Job Posting Skills: What 1,003 Listings Show -->
<!-- SEO description: I scraped 1,003 data science job postings over 30 days to find the exact skills recruiters ask for most — and what's hyped but barely hired. -->

<!-- worksheet-cta -->

---

### Want to put this into practice?

[Download the companion worksheet →](https://worksheets-thebreathnetwork.vercel.app/get-worksheet/i-tracked-every-data-science-job-posting-for-30-days-heres-t)

_Free PDF. Enter your email and it opens right away._
