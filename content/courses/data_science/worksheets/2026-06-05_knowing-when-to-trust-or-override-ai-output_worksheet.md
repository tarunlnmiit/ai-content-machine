# Knowing When to Trust or Override AI Output — Worksheet

**Objective:** By the end of this worksheet, you will be able to decide when AI output is safe to use as-is, when it needs adjustment, and when it must be overridden entirely — and you'll be able to explain why.

---

## Scenario

You're a junior data analyst at a fintech startup. Your team uses an AI assistant (a fine-tuned LLM) to help with EDA, feature engineering, and writing SQL queries. Your manager has made it clear: *AI mistakes that reach production are your mistakes, not the AI's.*

Today you have three AI outputs in your queue. Your job is to evaluate each one.

---

## Task 1 — Read the Output, Find the Crack (Easy)

The AI wrote this code to calculate the churn rate for last month:

```python
import pandas as pd

df = pd.read_csv("users.csv")

# AI-generated
churned = df[df["status"] == "churned"]
churn_rate = len(churned) / len(df)
print(f"Churn rate: {churn_rate:.2%}")
```

You know from the data dictionary that `users.csv` includes **all users ever**, not just last month's active users.

**Q1a.** What is the specific flaw in the AI's logic?

```
________________________________________________________________________

________________________________________________________________________
```

**Q1b.** Fix the code so it computes churn rate only over users who were *active last month* (assume a column `last_active_month` exists with values like `"2026-05"`).

```python
# Your fix here




```

**Q1c.** Would you trust this AI output if you hadn't read the data dictionary? Circle one and explain:

`YES / NO`

```
Because: ______________________________________________________________

________________________________________________________________________
```

---

## Task 2 — Override or Accept? (Medium)

Your AI assistant generated this SQL to find the top 5 customers by transaction volume this quarter:

```sql
SELECT customer_id, SUM(amount) AS total
FROM transactions
WHERE transaction_date >= '2026-04-01'
GROUP BY customer_id
ORDER BY total DESC
LIMIT 5;
```

You run it. Results look clean. No errors. Numbers seem reasonable.

But then you notice: your company's fiscal Q2 starts on **April 1** — and today is **June 5**. The quarter isn't over yet.

**Q2a.** Is this query logically correct for "this quarter's" data given today's date?

```
________________________________________________________________________
```

**Q2b.** Should you accept, adjust, or fully override this output? Justify in one sentence.

```
Decision: _____________________________________________________________

Why: __________________________________________________________________
```

**Q2c.** Write the corrected WHERE clause that ensures the query only pulls data through today's date dynamically (use Python's `datetime` to construct the query string, not a hardcoded date).

```python
from datetime import date

today = date.today()
query = f"""
SELECT customer_id, SUM(amount) AS total
FROM transactions
WHERE transaction_date >= '2026-04-01'
  AND _______________________________________________
GROUP BY customer_id
ORDER BY total DESC
LIMIT 5;
"""
print(query)
```

---

## Task 3 — Domain Beats Model (Applied)

A teammate used an AI to build a feature for a credit risk model. The AI suggested this:

```python
# AI suggested feature: days since last login as a proxy for engagement
df["days_since_login"] = (pd.Timestamp.today() - pd.to_datetime(df["last_login"])).dt.days
```

You're working with a dataset of rural microfinance customers. Many of them use the mobile app once every 2–3 months — not because they're disengaged, but because they have intermittent internet access.

**Q3a.** What assumption is the AI making about "days since login" that doesn't hold for this customer segment?

```
________________________________________________________________________

________________________________________________________________________
```

**Q3b.** If this feature is fed into a credit scoring model unchanged, what real-world harm could it cause for these customers?

```
________________________________________________________________________

________________________________________________________________________
```

**Q3c.** Propose one alternative feature that better captures engagement *for this specific context*. Write it as a Python expression or describe the logic clearly.

```python
# Your feature idea:




```

---

## Task 4 — Build a Trust Decision Framework (Applied + Reflective)

You've now seen three cases. Let's make this systematic.

**Q4a.** Fill in this decision table based on what you've learned today:

| Signal you observe | Trust / Adjust / Override |
|---|---|
| AI output matches your domain knowledge exactly | ______________________ |
| AI output is logically correct but uses wrong date range | ______________________ |
| AI output has no bugs but ignores real-world context of the users | ______________________ |
| AI output produces a number that "feels off" but you can't explain why | ______________________ |
| AI output passes all your unit tests and aligns with business logic | ______________________ |

**Q4b.** Write your own one-sentence rule for when you *must* override AI output, regardless of how confident the AI seems:

```
My rule: ______________________________________________________________

________________________________________________________________________
```

---

## Task 5 — The Hard Case (Challenge)

An AI model predicts that a loan applicant has a 78% probability of default. The model's historical accuracy on your validation set is 82%. But the applicant is a 24-year-old first-generation entrepreneur with no credit history — a profile almost absent from your training data.

**Q5a.** Should you trust the 78% figure? What's the core risk of doing so?

```
________________________________________________________________________

________________________________________________________________________
```

**Q5b.** What additional information would you need before making a final decision?

```
1. ____________________________________________________________________

2. ____________________________________________________________________

3. ____________________________________________________________________
```

**Q5c.** This is a judgment call, not a code fix. In 2–3 sentences, explain how you would communicate your override decision to your manager with evidence, not just instinct.

```
________________________________________________________________________

________________________________________________________________________

________________________________________________________________________
```

---

## Self-Check

Go through each item. If you can answer it clearly without looking back at the tasks, you've got this lesson.

**Can you:**

- [ ] Identify a logical error in AI-generated code even when it runs without exceptions?
- [ ] Distinguish between a bug (wrong logic) and a domain mismatch (correct logic, wrong context)?
- [ ] Explain *why* a number might be technically correct but analytically wrong?
- [ ] Propose a fix or alternative without discarding the AI's work entirely?
- [ ] Make and defend an override decision using evidence, not gut feel?

---

**What a strong answer looks like:**

- **Task 1:** The fix filters `last_active_month == "2026-05"` before computing the denominator. Trusting the AI without checking the data dictionary would have given a meaninglessly low churn rate across all-time users.
- **Task 2:** Adjust, not override — the query structure is right, but the date boundary needs to be dynamic. `AND transaction_date <= '{today}'` closes the quarter correctly.
- **Task 3:** Days-since-login penalizes low-connectivity users unfairly. A better proxy might be transaction frequency or average transaction value in the past 6 months.
- **Task 4:** "Must override" situations are those where the AI's context assumptions fundamentally don't match your data population — especially when real people bear the cost of errors.
- **Task 5:** A model trained on credit-history-rich profiles cannot reliably score someone with almost no representation in training. The 78% carries wide uncertainty. Override with caution and document the basis.