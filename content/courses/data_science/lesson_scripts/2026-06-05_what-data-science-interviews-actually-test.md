# COLD OPEN

The person who got the offer wasn't the one who knew the most.

I've sat on both sides of a data science interview table. I've watched candidates with clean resumes and textbook answers walk out without a job. And I've watched someone stumble through the math, get the formula slightly wrong, and still get the call back.

The difference wasn't knowledge. It was something most people never think to prepare.

---

# WHY THIS MATTERS

You're probably preparing for interviews the way most people do — grinding LeetCode, memorising the difference between L1 and L2 regularisation, rehearsing what a p-value "really means." And some of that matters. I'm not going to pretend technical knowledge is irrelevant.

But here's what nobody tells you when you're 21, applying for your first DS role, trying to figure out what these companies actually want: the technical questions are partially a trap.

Not because the companies are trying to trick you. But because what they're evaluating with those questions is not what you think they're evaluating.

Interviews in data science — real ones, at companies building real products — are not memory tests. They're judgment tests. And if you prepare for one while they're running the other, you will lose to people who are technically weaker than you.

This lesson is about how to stop doing that.

---

# TEACH

## Key Point 1: Reasoning Beats Recall — They're Watching How You Think Out Loud

Here's a question a real interviewer might ask: "How would you decide whether to use a decision tree or logistic regression for this problem?"

The wrong answer is a clean, rehearsed comparison of both algorithms. Interpretability here, non-linearity there, feature scaling for one, not the other. Technically correct. Completely useless.

The right answer starts with a question back: "What matters more for this use case — being able to explain individual predictions, or maximising overall accuracy? And do we have any sense of whether the relationship between features and outcome is roughly linear?"

See what happened there? You didn't demonstrate that you memorised something. You demonstrated that you think before you model.

Interviewers — good ones — are not running a knowledge quiz. They're watching your reasoning process. They're listening for: do you ask clarifying questions before jumping in? Do you acknowledge tradeoffs instead of pretending one answer is always right? Do you know when you don't know something?

The single most useful thing you can do in a DS interview is slow down before you answer. Take five seconds. Say what you're considering. Show the work of your thinking, not just the conclusion.

`[PERSONAL_INSERT: moment where you or someone you observed answered too fast — wrong direction, had to backtrack — what that looked like from both sides of the table]`

The candidates who do this feel vulnerable doing it. They think: "I'm not giving a clean answer, this looks bad." But what the interviewer is actually thinking is: "This person reasons like a practitioner, not a student."

---

## Key Point 2: Communicating Tradeoffs Is the Real Signal

There's a follow-up to every technical question that most candidates never get asked — because they never get past the first version of their answer.

The follow-up is: *What's the cost of being wrong here?*

If you're building a model to flag potential fraud transactions, what's worse — a false positive (flagging a legitimate transaction) or a false negative (missing actual fraud)? They have very different costs. One annoys a customer. One costs the company money and possibly legal exposure.

A candidate who answers "we'd use precision-recall tradeoff, tune the threshold" is giving a technically correct response. A candidate who says "it depends on what the business can absorb — let me think through both failure modes and what they actually mean for the product" is giving a practitioner response.

This is the tradeoff muscle. And it's something you can practice.

[B-ROLL: notebook open with two columns — "Cost if we're wrong this way" / "Cost if we're wrong that way"]

Every technical decision in data science has a tradeoff. Complexity vs. interpretability. Precision vs. recall. Speed vs. accuracy. Build vs. buy. More data vs. faster iteration.

In an interview, every time you name a tradeoff explicitly — without being asked — you signal that you've done this before. Because people who've only studied data science don't naturally think in tradeoffs. People who've shipped things do.

When you're preparing, take any technical topic you know well and ask yourself: what does a bad choice here actually cost? Not theoretically — concretely. In terms of time, money, customer experience, or trust. That's the frame interviewers are looking for.

`[PERSONAL_INSERT: question where you named a tradeoff the interviewer hadn't raised — what they said or how they responded]`

---

## Key Point 3: One Project Told Well Gets You Hired

This is the part most people completely underestimate.

Almost every DS interview has some version of: "Tell me about a project you've worked on."

And almost every candidate gives the same answer: what the project was, what data they used, what model they tried, what accuracy they got. Chronological. Thorough. Completely forgettable.

Here's what the interviewer actually wants to know: how did you handle the point where things got hard?

Because things always get hard. The data was messier than expected. The metric you were optimising turned out to be the wrong one. The stakeholder changed the requirement halfway through. The model was good but nobody used it.

Those moments — the messy middle — are where your actual skill lives. And if your project story skips over them, you're hiding the most interesting part.

The structure that works is not chronological. It's: what was the real problem → what did I try first → where did it break → what did I actually learn. You don't need a perfect outcome. You need an honest account of thinking under uncertainty.

`[PERSONAL_INSERT: one specific element from your strongest project — the moment it got complicated, what you did, what it taught you — rough form, not polished]`

One project, told this way, is worth more than a GitHub full of repositories with no story attached. Interviews select for judgment and self-awareness, not volume. Know your one project better than you know anything else.

---

# STORY

`[PERSONAL_STORY: The candidate who knew less but reasoned through the messy middle and got the offer. Tell the full version — who they were, what the question was, what they got technically wrong, how they caught themselves and walked through their uncertainty out loud, named what they didn't know and how they'd figure it out. The specific contrast: what other candidates were doing versus what this person did. The moment you or someone in the room realised they were the one. What made the difference in concrete terms.]`

---

# DO THIS NOW

Open the worksheet for this lesson. One exercise: your interview project story, written in the structure we just covered — real problem, first attempt, where it broke, what you actually learned.

Do not write the polished version. Write the honest version. The messy one. That's the one that works in a room.

If you haven't shipped a real project yet, that's your other action: start one. Not a Kaggle competition. A question you actually care about, a dataset you found yourself, and an answer you'd be willing to defend out loud.

---

# CLOSE

The best data scientists I know aren't the ones who know the most. They're the ones you'd trust to think out loud in a hard room.

---

## Marker Notes (Post-Writing)

**`[PERSONAL_INSERT` — Key Point 1]** Need a moment of answering too fast (yours or someone you interviewed). Ideal: gave a model recommendation without asking about the use case, interviewer paused with "interesting — why?" and it unravelled. Brief, a little self-deprecating.

**`[PERSONAL_INSERT` — Key Point 2]** A moment where you named a failure mode the interviewer hadn't raised. Their response — surprise, a follow-up question, being fast-tracked. Small signal works fine.

**`[PERSONAL_INSERT` — Key Point 3]** Your strongest project story in rough form — the version with the failure or pivot in it. Not the LinkedIn version.

**`[PERSONAL_STORY]`** Core story of the lesson. If real person: protect identity, keep specific behavioral detail. The contrast between them and other candidates is what makes it land.

---

**Suggested titles:**
1. *What Data Science Interviews Are Actually Testing (Hint: Not What You Think)*
2. *The Interview Skill Nobody Prepares For*
3. *Why the Candidate Who Knew Less Got the Job*

**Derivative angle:** Twitter thread — "3 things I learned from watching 50+ DS interviews" — pull one concrete example from each key point.