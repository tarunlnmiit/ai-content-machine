# The Interview Project Story — Worksheet

**Objective:** By the end of this worksheet, you will have a single, well-structured project story you can tell confidently in any data science interview.

---

## The Situation

Priya has done three projects — a churn prediction model for a telecom dataset, a Diwali sales EDA for her college fest, and a cricket match outcome classifier she built for fun. Every interview she freezes when asked: *"Tell me about a project you've worked on."*

She has real work. She just hasn't built the story yet.

That's what you're fixing today.

---

## Task 1 — Pick Your One Project (Easy)

You will build a story around **one** project. Not your best-looking repo. The one where you *made decisions* and learned something real.

Answer these in the blanks:

**Project name or description:**
`____________________________________________________`

**What dataset or domain?**
`____________________________________________________`

**Where did you get the data? (Kaggle, scraped, provided, self-collected)**
`____________________________________________________`

**Did you finish it? (Yes / Partial / Abandoned — all are fine)**
`____________________________________________________`

> No project? Pick any dataset you've explored for more than 2 hours and write about that.

---

## Task 2 — Map the Problem (Medium)

Before you can tell a story, you need to know what *problem* the project solved. Most students skip this and jump to model accuracy. Interviewers care about the problem first.

Answer in plain sentences — no bullet points, no jargon:

**What was the actual problem? (Who had it? What went wrong without a solution?)**

```
Write 2–3 sentences here:

______________________________________________________________

______________________________________________________________

______________________________________________________________
```

**What would "solved" look like? (What changes in the real world if your model works?)**

```
______________________________________________________________

______________________________________________________________
```

**Did you reframe the problem during the project? (e.g., started with clustering, switched to regression) If yes, why?**

```
______________________________________________________________

______________________________________________________________
```

---

## Task 3 — Extract Your Actual Decisions (Applied)

This is the part that makes your story different from everyone who trained the same dataset. Interviewers remember candidates who explain *why* they did things, not *what* they did.

Run this code on your project (adapt column names as needed). It forces you to reconstruct your decision log:

```python
# decision_log.py
# Fill in each list with YOUR actual choices

decisions = {
    "data_cleaning": [
        # Example: "Dropped rows where salary was null because < 2% of dataset"
        # Write yours:
        "____",
        "____",
    ],
    "feature_choices": [
        # Example: "Dropped user_id — identifier, not a feature"
        # Example: "Created age_bucket from age — model handled it better as ordinal"
        "____",
        "____",
    ],
    "model_selection": [
        # Example: "Tried logistic regression first — baseline, interpretable"
        # Example: "Switched to random forest — 8% F1 gain, acceptable speed tradeoff"
        "____",
        "____",
    ],
    "what_surprised_me": [
        # Example: "Assumed tenure would be top feature — it ranked 6th"
        "____",
    ],
}

for stage, choices in decisions.items():
    print(f"\n=== {stage.upper()} ===")
    for c in choices:
        print(f"  • {c}")
```

**After running it, circle the ONE decision that was most non-obvious.**

Write it here: `____________________________________________`

> This single decision will become the core of your story. It shows judgment, not just execution.

---

## Task 4 — Write the Story Draft (Applied)

Use this template. Fill every blank. Keep each answer to 1–3 sentences — brevity is a skill.

```
I worked on a project where [PROBLEM IN ONE LINE].

The data was [SOURCE + ROUGH SIZE + ANY MESSINESS].

The first thing I did was [FIRST ACTUAL STEP — not "explore the data", be specific].

The decision that mattered most was [YOUR CIRCLED DECISION FROM TASK 3],
because [WHY IT MATTERED — what would have gone wrong otherwise].

The result was [METRIC OR OUTCOME — even rough is fine: "73% accuracy on held-out set"
or "caught 3 patterns I hadn't expected"].

If I did it again, I would [ONE HONEST THING YOU'D CHANGE].
```

Write your filled version below:

```
______________________________________________________________

______________________________________________________________

______________________________________________________________

______________________________________________________________

______________________________________________________________

______________________________________________________________
```

---

## Task 5 — Stress-Test Your Story (Applied)

Read your draft from Task 4 out loud. Then answer:

**Can you explain your most important decision without using the words "accuracy", "model", or "algorithm"?**

Try it here:
```
______________________________________________________________

______________________________________________________________
```

**If the interviewer asks "why not use [different model]?" — what's your answer?**
```
______________________________________________________________

______________________________________________________________
```

**What is the one thing in this project you genuinely don't know well yet?**
```
______________________________________________________________
```

> You will be asked this. Knowing your gap — and saying so clearly — is stronger than bluffing.

---

## Self-Check

A solid project story has these properties. Mark each honestly:

| Check | Done? |
|---|---|
| The problem is described in terms a non-technical person understands | ☐ |
| At least one decision is explained with a *reason*, not just a result | ☐ |
| There is a concrete outcome (number, finding, or clear failure with learning) | ☐ |
| You can deliver the full story in under 90 seconds | ☐ |
| You know what question the story will likely invite next | ☐ |

**What a correct approach looks like:**

A strong story sounds like: *"I was predicting dropout for an ed-tech dataset. I had 40 features but dropped 18 upfront — most were post-dropout signals that would leak the label. After that I had to rebuild the whole feature set from scratch, which I hadn't planned for. Final model was a gradient boosted tree, 81% recall on the minority class, which mattered more than accuracy here because false negatives were costlier."*

Notice: problem context → honest constraint → real decision with reasoning → metric that fits the problem. No fluff.

If your Task 4 draft follows that shape, you're ready to say it in a room.