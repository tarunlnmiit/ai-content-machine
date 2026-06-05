# COLD OPEN

Here's something nobody tells you early in your career: some of the best data science decisions I've ever seen were made by someone who looked at a problem, thought about it for ten minutes, and said — "We don't need a model for this."

Not because they couldn't build one. Because they saw the whole picture. The maintenance. The explainability meeting. The model that works in October but quietly degrades by March. The stakeholder who never really trusted it. The on-call alert at 2am when it stops making sense.

They saw all of that, and they chose a four-line rule instead.

And it worked. For years. Without touching it.

That's the senior move. Not always building more. Sometimes knowing when to stop.

---

# WHY THIS MATTERS

Let me be direct about why we're doing this lesson here — at Lesson 7, not Lesson 1.

The first few lessons were about how to think like a practitioner: frame the problem right, distrust your data, build intuition before you model. All of that still applies. But I held this one back deliberately, because it only makes sense once you've understood what models can do.

If you came into this course having already built classifiers, you probably think of ML as the default answer. The natural next step after data cleaning. The thing that makes you a "real" data scientist.

I thought the same thing for the first few years of my career.

And I wasted time because of it. Built models that were harder to explain than the rules they replaced. Built models that needed babysitting while their simpler alternatives just... ran. Built models to demonstrate technical sophistication when the actual need was a decision that could be made transparently.

If you're grinding Kaggle competitions right now, you're optimizing for a leaderboard. That's fine — it teaches you a lot. But the leaderboard doesn't have a production environment. It doesn't have a skeptical product manager. It doesn't have drift, or a cold start problem, or a business that changes its rules every quarter.

This lesson is about the real-world version of the job. The version where picking the right tool — not the most impressive one — is the actual skill.

---

# TEACH

## Key Point 1: Rules and Heuristics Win More Often Than Anyone Admits

There's a question I now ask at the start of almost every project: "What would a smart person do here if they didn't have access to any data at all?"

I'm not asking this to be contrarian. I'm asking because the answer reveals the shape of the problem.

If the smart person would draw on a whiteboard and write a clear set of conditions — "if X, then Y; if X and Z, then do something else" — that's a signal. The problem might not need a model. It might need a well-documented rule.

Rules have a bad reputation in data science circles because they feel like a step backward. Like you're admitting defeat. But that framing is wrong. Rules are not inferior to models. They're a different tool. And they're often the better tool.

Here's why. A rule is legible. You can explain it in a sentence. A stakeholder can audit it, challenge it, understand exactly why a decision was made. A model cannot offer that — at least not without a layer of interpretability tooling that adds its own complexity and its own failure modes.

A rule also has zero ongoing cost. Write it once. Test it once. Deploy it once. It doesn't drift. It doesn't need retraining. It doesn't need a monitoring dashboard. If the business logic changes, you change the rule — explicitly, not by retraining on new data and hoping the right thing happens.

The question isn't "is a model more accurate than a rule?" The question is: "Is the model accurate enough to justify everything it costs over a rule that's pretty good?"

More often than you'd expect, the honest answer is no.

`[PERSONAL_INSERT: early project where you defaulted to a model, a colleague surfaced that a rule would be cleaner — what was the problem, what did the rule look like, what did you learn]`

---

## Key Point 2: Every Model Carries a Hidden Cost You Don't See at Build Time

I want to walk you through the full lifetime of a machine learning model. Not the exciting part — training, evaluating, deploying. The part after that. The long, quiet, expensive middle.

A model in production is a commitment. From the moment you deploy it, you own it.

You own the data pipeline feeding it. If that pipeline breaks or shifts format, your model breaks or shifts silently — and you might not know for days. You own the monitoring: is the prediction distribution still what it was last month? Has the feature space drifted? Are there edge cases the training data never saw?

You own the explainability conversations. Every time a stakeholder says "why did it decide that?" — that's on you. Every time there's a bad prediction and someone asks what happened — that's on you.

And here's the thing about drift specifically, because this catches a lot of people off guard. The world changes. Customer behavior changes. The patterns a model learned in 2023 might not hold in 2025. This isn't a failure of the model — it's a property of modeling real systems. But it means every model you build has a slow, inevitable decay curve, and you are responsible for detecting that decay and responding to it.

None of this is a reason to never build models. Most of what I do day-to-day involves models. But it is a reason to build them only when the problem actually warrants the overhead.

Before you build a model, ask yourself three things. One: how do I know when this model has gone wrong, and how fast will I find out? Two: who in the organization owns the conversation when it makes a bad call? Three: what does retraining look like — is there a process, a schedule, a person?

If you can't answer those questions before you build, you're not ready to build. And often, when you sit with those questions honestly, a simpler approach starts to look a lot more attractive.

---

## Key Point 3: The Boring Solution That Ships Beats the Clever One That Rots

Let me tell you about a pattern I've seen more times than I can count.

Someone builds a model. Genuinely good work — well-structured code, solid validation, real thought in the feature engineering. They're proud of it. Rightfully so.

And then it sits. Deployment takes longer than expected. The monitoring infrastructure isn't ready. The stakeholder who sponsored it changes teams. The business problem shifts slightly, and suddenly the model is answering a question nobody is asking anymore.

The model rots. Not because it was bad work. Because the surrounding system wasn't ready for it, and nobody maintained the connection between the model and the live need it was supposed to serve.

Meanwhile — in a different part of the same company — someone wrote a branching rule in a script. Not elegant. Basically a sequence of if-statements with thresholds a domain expert guessed at. But it's been running for eighteen months. It's in production. It's making decisions. Stakeholders trust it because they can read it. It gets updated when business rules change — explicitly, intentionally, with version control.

Which one of those is actually doing data science?

The second one is closer to what the job is about. Not because rules are better than models in the abstract. Because the job is to create real, working solutions to real, working problems — not impressive solutions to problems slightly adjacent to reality.

The complexity tax is real. Every increment of sophistication you add is a future maintenance burden, a future source of breakage, a future explainability conversation. That doesn't mean you never add it. It means you add it because the problem demands it — not because you want to demonstrate that you could.

Ship the boring thing that works. Complexity is debt. Pay it only when you have to.

---

# STORY

`[PERSONAL_STORY: The 4-line if-rule story. Set the scene: what was the project, what was the original model, when did you or your team realize the model wasn't the right tool? Walk through what the rule looked like — the actual logic, simplified if needed. What was the reaction when you proposed replacing a model with four lines of conditional logic? Skepticism? How did you make the case? Fast-forward: how long did it run? Did it ever need changing? What did the people maintaining it say years later, compared to what maintaining the model would have looked like? Be honest — including any part where you personally resisted simplifying.]`

I tell this story not because rules are always the answer. They're not. But because the instinct to reach for a model — to signal sophistication, to use the full capability you've built — is real, and it overrides good judgment more often than we admit.

The story stuck with me because it was the first time I saw simplicity chosen deliberately, by someone senior, as an act of professional judgment rather than laziness.

That's the shift I want you to internalize: simplicity isn't a fallback. It's a decision.

---

# DO THIS NOW

Open the worksheet for this lesson. It's called the ML-or-Not Decision Filter.

Five questions. Work through them for three different problems — from your own work, from the dirty dataset in this course, or from case studies you've encountered.

The five questions:

**One:** Can a smart domain expert write down most of the decision logic right now, without data? If yes, start with a rule.

**Two:** Does this decision need to be explained to a non-technical person who can push back? If yes, your model needs to be at least as explainable as a rule.

**Three:** What's the cost of the model being quietly wrong for two weeks before anyone notices? If that's catastrophic, simplicity buys you safety.

**Four:** Is there a clear owner for monitoring, retraining, and defending this model in production? If not, you're building an orphan.

**Five:** Is the performance gap between the simple solution and the model large enough to justify everything in questions one through four?

For each problem: write your ML-or-not call and one sentence of reasoning. Practice making the argument out loud. Because at some point in your career, someone is going to ask why you didn't use ML. "It wasn't worth it" is not an answer. "The performance delta didn't justify the maintenance overhead given our monitoring capacity" is.

---

# CLOSE

The senior move is often deleting the model. A rule you can explain, maintain, and defend will outlast a model you can't — every time.

---

**Post-writing notes:**

- `[PERSONAL_INSERT]` — needs: early project where default-to-model instinct was wrong; ideal if a senior colleague caught it; show the before/after of rule vs. model
- `[PERSONAL_STORY]` — needs: the specific 4-line if-rule story with real business context, the decision to replace the model, the years-long production run
- Titles (3 options):
  1. *The Senior Move Nobody Teaches: When Not to Build a Model*
  2. *Rules Beat Models More Often Than You Think*
  3. *Delete the Model: What Real Practitioners Know*
- Derivative angle: X thread — "Juniors add models. Seniors delete them. The 5 questions I run before building anything ↓" (post the Decision Filter as a thread)