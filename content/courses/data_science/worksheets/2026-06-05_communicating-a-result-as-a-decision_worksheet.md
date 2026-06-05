# Communicating a Result as a Decision — Worksheet

**Objective:** Take a raw model output and write a crisp 3-sentence decision brief that a non-technical stakeholder can act on.

---

## Scenario

You work as a data analyst at a mid-sized edtech startup in Pune. The product team asked you to predict which free-trial users are likely to convert to a paid plan within 7 days.

You trained a logistic regression model. Here's what came back:

```
Model: Logistic Regression (7-day conversion prediction)
Accuracy:        81%
Precision:       74%
Recall:          68%
AUC-ROC:         0.83

Top features by coefficient weight:
  1. lessons_completed_last_7d   (+2.1)
  2. opened_pricing_page         (+1.8)
  3. days_since_signup           (-0.9)
  4. support_tickets_raised      (-0.6)

On the holdout set (n=1,200 users):
  Predicted converters:    340
  Actual converters:       312
  Users correctly flagged: 228
```

The product manager has 10 minutes before a call with the CEO. She's not technical.

---

## Task 1 — Strip the noise (Easy)

From the model output above, circle or list the **three numbers** that matter most for a business decision. Ignore the rest.

Write them here:

1. ____________________________________________________________________
2. ____________________________________________________________________
3. ____________________________________________________________________

**Why did you pick those three?** (1–2 sentences)

________________________________________________________________________

________________________________________________________________________

---

## Task 2 — Translate a metric (Medium)

Recall = 68% sounds bad if you don't know what it means. But for this use case, what does it actually mean in plain language?

Complete this sentence without using the word "recall":

> "Out of every 100 users who would have converted anyway, our model correctly identifies about ______ of them — and misses ______."

Now answer: **Is that acceptable here, or is it a problem?** Explain in one sentence using the business context (hint: what's the cost of a false negative vs. a false positive in a conversion campaign?).

________________________________________________________________________

________________________________________________________________________

---

## Task 3 — Build the decision brief (Core task)

Write a **3-sentence decision brief** for the product manager. Each sentence has one job:

- **Sentence 1 — What the model found:** State the key result in numbers. No model names, no jargon.
- **Sentence 2 — What it means:** Translate it into a business implication. What can the team do differently now?
- **Sentence 3 — What you recommend:** One concrete, specific action with a measurable scope.

Draft it here:

**Sentence 1:**

________________________________________________________________________

________________________________________________________________________

**Sentence 2:**

________________________________________________________________________

________________________________________________________________________

**Sentence 3:**

________________________________________________________________________

________________________________________________________________________

---

## Task 4 — Write the code that supports your brief (Applied)

Your brief claims the model identifies ~340 likely converters. Write the Python snippet that produces that number from a trained model and a user DataFrame.

```python
import pandas as pd
# Assume: model is already trained, X_holdout is the feature matrix

# Your code here:




# Expected output: an integer count of predicted converters
```

Now add one line that also prints the **top 5 user IDs** most likely to convert (highest predicted probability):

```python
# Your code here:


```

---

## Task 5 — Stress-test your brief (Applied)

Your PM reads your brief and asks two follow-up questions. Answer each in **one sentence**, using only what the model output can support. If the model output can't answer it, say so — and say what data you'd need.

**Q1: "Can we trust this model next month if our user base grows from 5,000 to 50,000?"**

________________________________________________________________________

________________________________________________________________________

**Q2: "Which users should we NOT target with a discount offer — because they'll convert anyway?"**

________________________________________________________________________

________________________________________________________________________

---

## Self-Check

Review your Task 3 brief against this checklist before moving on:

| Check | Yes / No |
|---|---|
| Sentence 1 contains at least one specific number | |
| No technical term appears without a plain-language equivalent | |
| Sentence 3 names a specific action (not "we should investigate") | |
| The brief could be read aloud in under 20 seconds | |
| You haven't used any banned words from the course style guide | |

**What a strong brief looks like for this scenario:**

> *"Our model correctly flags about 228 of the 312 users who actually converted — roughly 7 in 10. Users who completed lessons in the past week and visited the pricing page are the clearest signals of intent. Recommend sending a targeted nudge (one email + one in-app prompt) to the 340 flagged users this week, starting with the top 50 by predicted probability."*

Notice: no mention of AUC, logistic regression, or coefficients. The number comes first. The action is specific enough to hand off without a follow-up meeting.

---

**Reflection (optional, but worth it):**

Think of one real situation — in college, an internship, or a personal project — where you had data but struggled to say what to *do* with it. What was missing? Write 2–3 sentences.

________________________________________________________________________

________________________________________________________________________

________________________________________________________________________