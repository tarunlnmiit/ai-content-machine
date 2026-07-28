---
title: "What Interviewers Actually Write in the Feedback Doc After You Leave the Room"
type: blog
niche: data_science_tech
date: 2026-07-21
week: 2026-W30
slug: what-interviewers-actually-write-in-the-feedback-doc-after-y
tags: [content/blog, niche/data_science_tech, week/2026-W30]
---
# What Interviewers Actually Write in the Feedback Doc After You Leave the Room

*You prepped to prove you can build it. They were scoring whether you'd know when not to.*

The phrase that killed the most hires I ever debriefed wasn't "weak on stats." It was "couldn't tell me why they picked that model."

I've sat on the interviewer side of data science hiring for about forty loops, and if you want to know what data science interview feedback actually says, start there. I once wrote almost exactly that about a candidate who nailed the coding round: "Strong implementation, but when I asked why logistic regression over a tree here, the answer was 'it usually works well.' No sense of the tradeoff." That one sentence sank him. Not because the answer was wrong — because it told the room he'd be the kind of hire who ships a model nobody can defend when it breaks in production at 11pm.

![The transcript shows what you said. The feedback doc records what it felt like to be in the room with you.](/content/blogs/2026-W30/2026-07-21_data_science_tech_what-interviewers-actually-write-in-the-feedback-doc-after-y_images/01_hook_manual.png)
*The transcript shows what you said. The feedback doc records what it felt like to be in the room with you.*

Here's the line that does the opposite — the one that saves people. Some version of "walked me through how they'd be wrong." I once wrote: "Candidate volunteered the failure mode before I asked — said the AUC looked too good and suspected leakage from the join." That single line got her the offer over someone with a stronger resume. Because in this job, the person who catches their own leaked feature at midnight is worth more than the person with the cleaner GitHub. Interviewers aren't grading whether you know the answer. They're writing down whether they'd trust your judgment when there's no answer key.

**You're prepping for the wrong exam**

Candidates obsess over the model. Did I pick XGBoost when they wanted a neural net, did I nail the exact regularization term. In forty interviews I can count on one hand the times a feedback doc argued about algorithm choice. What gets written is quieter and more damning: "jumped to modeling before understanding the data," or "couldn't tell me why this metric mattered to the business."

One candidate built a beautiful pipeline for a churn problem and never once asked what churn cost the company. I wrote "strong engineer, but I'm not sure he'd know when to stop," and that line ended his loop. The gap is this: you prep to prove you can build the thing, and we're quietly scoring whether you know which thing is worth building — and when the honest answer is "we don't need a model at all."

**The results that make no sense on paper**

The strongest hire I ever wrote up couldn't finish the SQL question. She blanked on window functions, said so out loud, then reasoned her way to a hacky self-join that technically worked. What I wrote was "thinks in tradeoffs, tells you when she's unsure." The moment that sold me wasn't a right answer — it was her saying "this is O(n²), I'd fix it before it hit production, here's how." The transcript shows a wrong-ish query. It can't capture that she was the only candidate that day I'd trust not to silently ship something broken.

The reverse happened with a guy who nailed every question cold. Perfect, fast answers. My feedback said "answers are memorized, not owned," and I flagged him no-hire. Every time I pushed past the clean answer with "why that and not X," he had nothing. The transcript reads like a top score. What it doesn't show is that curiosity dies the second you leave the script — and on a real team, that's the person who can't debug anything they didn't build.

**The trait I'd have called "soft" at 25**

Early on I thought interviews scored correctness. Now I know the feedback doc mostly says some version of "did they interrogate the question before answering it." The signal I weight most is what a candidate does when I hand them a deliberately underspecified prompt. The ones who ask "what decision is this number feeding?" before touching a query are the ones I fight to hire. Because across ten years, the expensive mistakes were never wrong models — they were correct answers to the wrong question. I'd have dismissed that as fluff at 25. Now it's the first thing I write down.

**How often the room disagrees with you**

Roughly 1 in 5 debriefs flip from what the candidate walked out assuming. Most of the time the room already agrees before anyone speaks — the clear yes and the clear no read the same to everyone. The flips happen in the middle, and almost always in the same direction: someone got the right answer fast and left grinning, and then a person in the debrief says "yeah, but did anyone actually understand *why* it worked, or did they just watch him type?"

The thing that flips a debrief isn't correctness — it's whether you made the interviewer think *with* you. One candidate got a messy SQL question technically right, and the flip came when our junior analyst said, "I didn't learn anything watching that." That killed it. The rarer reverse flip: someone fumbled the code but narrated their reasoning so clearly that two people said "I'd want to sit next to them," and the write-up quietly turned from lean-no to hire.

**Two things you can fix before your next loop**

First, the "any questions for us?" moment. I've written this note more than once: the candidate asks only about perks — WFH policy, vacation days — and nothing about the work. One guy was technically sharp all interview, then closed by asking whether we'd expense his home setup. That was the whole note I wrote. It reads as someone optimizing for comfort before they've shown they care about the problem. The fix costs nothing: one genuine question about the actual work. "What's the messiest dataset the team is fighting right now?" or "Where does this model actually break in production?" It flips the read from *taker* to *someone who'd be good to work next to*.

Second, the one line I'd show every candidate if I could: "Strong technically, but I still don't know what he'd actually *do* on Monday." Most people I wrote that about were sharp. But when I asked "tell me about a time your analysis was wrong," they gave a polished non-answer, and I left unable to picture them in the seat. The ones who stuck said something like: "I shipped a churn model that looked great offline and tanked in production because I'd leaked a future field into the features — took me a week to catch it." That one honest failure told me more than an hour of correct answers. Because it showed me how they think when things break, which is the actual job.

So before your next loop, stop rehearsing answers. Go find the story of the time you were wrong, and learn to tell it without flinching. That's the line they'll write down.

If you want the exact questions I use to pressure-test judgment — the ones that separate "watched him type" from "I'd sit next to them" — I put them in a free companion worksheet you can grab when you join the list below.

<!-- Medium tags: Data Science, Interviewing, Career Advice, Machine Learning, Job Search -->
<!-- Target keyphrase: data science interview feedback -->
<!-- SEO title: What Data Science Interview Feedback Really Says -->
<!-- SEO description: What interviewers actually write in data science interview feedback after you leave — the real phrases that decide the hire, from someone who ran 40+ loops. -->

<!-- worksheet-cta -->

---

### Want to put this into practice?

[Download the companion worksheet →](https://worksheets-thebreathnetwork.vercel.app/get-worksheet/what-interviewers-actually-write-in-the-feedback-doc-after-y)

_Free PDF. Enter your email and it opens right away._
