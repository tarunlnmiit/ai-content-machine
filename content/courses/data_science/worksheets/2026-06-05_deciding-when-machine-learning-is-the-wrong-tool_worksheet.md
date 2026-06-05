# Deciding When Machine Learning Is the Wrong Tool — Worksheet

**Objective:** By the end of this worksheet, you will decide whether ML is the right approach for 3 real problems — and give reasons a senior data scientist would agree with.

---

## Background: The Trap Nobody Warns You About

Most DS courses start with "here's how to train a model." Nobody teaches you when *not* to train one.

ML adds complexity: data pipelines, retraining schedules, monitoring for drift, debugging non-deterministic outputs. When a simpler tool gives you the same answer with less risk, ML is the wrong choice.

This worksheet is about building that judgment.

---

## Task 1 — Read the Decision Framework (No code needed)

Before writing a single line of model code, ask these four questions:

| # | Question | If YES → |
|---|----------|----------|
| 1 | Can a human write down the exact rules? | Use if-else logic |
| 2 | Is the dataset smaller than ~500 labeled examples? | Reconsider ML |
| 3 | Is the output a direct database lookup or formula? | Use SQL / math |
| 4 | Does a wrong prediction have severe consequences (medical, legal, financial)? | Slow down — explainability matters |

**Your turn:** Add one more question you think belongs in this table. Write it below and explain why.

> My question: ____________________________________________________________________

> Why it matters: _________________________________________________________________

---

## Task 2 — Code Exercise: The Formula That Beats a Model

A college student wants to predict their CGPA after each semester. They have:
- Marks in each subject
- Credit hours per subject

**The formula:**

```
CGPA = Σ(grade_points × credits) / Σ(credits)
```

Run the starter code, then answer the questions below.

```python
def calculate_cgpa(subjects: list[dict]) -> float:
    """
    subjects: list of dicts with keys 'grade_points' (0–10) and 'credits' (int)
    Returns: CGPA rounded to 2 decimal places
    """
    total_weighted = sum(s['grade_points'] * s['credits'] for s in subjects)
    total_credits = sum(s['credits'] for s in subjects)
    
    if total_credits == 0:
        raise ValueError("Total credits cannot be zero")
    
    return round(total_weighted / total_credits, 2)


# Sample: Semester 1 results
semester_1 = [
    {'subject': 'Maths',     'grade_points': 8.5, 'credits': 4},
    {'subject': 'Physics',   'grade_points': 7.0, 'credits': 3},
    {'subject': 'CS Basics', 'grade_points': 9.2, 'credits': 4},
    {'subject': 'English',   'grade_points': 6.5, 'credits': 2},
]

print("CGPA:", calculate_cgpa(semester_1))
```

**2a.** What does this code output? Run it or trace it manually.

> Output: ________________________________________________________________________

**2b.** A classmate suggests: *"We should train an ML model to predict CGPA from marks — it'll be more accurate."* What is wrong with this suggestion? Write 2 specific reasons.

> Reason 1: ______________________________________________________________________

> Reason 2: ______________________________________________________________________

**2c.** Modify the code to add an `early_warning` flag that prints `"At risk"` if CGPA drops below 6.0. No ML needed — write the logic directly.

```python
# Your modification here:




```

---

## Task 3 — Three Scenarios, Three Decisions

For each scenario below, decide: **ML** or **Not ML**. Then write one sentence justifying your decision. There is no trick — some are ML, some are not.

---

**Scenario A:** A Swiggy-like food delivery app wants to estimate delivery time. They have GPS data, restaurant prep time, distance, and historical traffic patterns for 2 million past orders.

> Decision: ☐ ML  ☐ Not ML

> Reason: _______________________________________________________________________

---

**Scenario B:** A school wants to flag students who haven't submitted an assignment. The rule is: if `submissions_this_week == 0`, mark as missing.

> Decision: ☐ ML  ☐ Not ML

> Reason: _______________________________________________________________________

---

**Scenario C:** An e-commerce site wants to detect whether a product review is fake. They have 50,000 labeled reviews (fake / genuine) and reviews contain text, star ratings, and account age.

> Decision: ☐ ML  ☐ Not ML

> Reason: _______________________________________________________________________

---

## Task 4 — Debug the Mistake

A junior analyst built the following to flag "expensive" transactions:

```python
import pandas as pd
from sklearn.ensemble import IsolationForest

df = pd.read_csv('transactions.csv')  # columns: user_id, amount, category

model = IsolationForest(contamination=0.05, random_state=42)
df['is_expensive'] = model.fit_predict(df[['amount']])
df['is_expensive'] = df['is_expensive'].map({1: False, -1: True})

print(df[df['is_expensive']].head())
```

The business rule they were actually given: *"Flag any transaction above ₹10,000."*

**4a.** What is the analyst doing wrong? (Not a Python bug — a decision bug.)

> _______________________________________________________________________________

> _______________________________________________________________________________

**4b.** Rewrite the flagging logic correctly — no ML, just pandas.

```python
# Your fix:




```

**4c.** Name one situation where using Isolation Forest on transaction data *would* be the right call.

> _______________________________________________________________________________

---

## Task 5 — Applied Decision (Open-ended)

Pick one problem from your own life, college, or neighbourhood that someone might naively throw ML at. Describe:

1. The problem in one sentence
2. Why a simpler solution works
3. What that simpler solution looks like (pseudocode or plain English)

> Problem: _______________________________________________________________________

> Why simpler works: ______________________________________________________________

> Simpler solution:

```
# Pseudocode or plain English:




```

---

## Self-Check

Use this after completing all tasks. No peeking before you finish.

| Task | What a correct response looks like |
|------|-------------------------------------|
| 1 | Your question targets a real cost of ML (latency, interpretability, data volume, maintenance, etc.) |
| 2a | CGPA ≈ 7.98 |
| 2b | The relationship is deterministic — there is nothing to learn. A model adds variance without adding accuracy. Also: dataset doesn't exist yet when a student starts college. |
| 2c | An `if cgpa < 6.0: print("At risk")` check after calling `calculate_cgpa` |
| 3A | ML — large labeled dataset, non-linear patterns in traffic |
| 3B | Not ML — exact rule already known, no uncertainty |
| 3C | ML — labeled data exists, task is classification with patterns a rule can't cleanly capture |
| 4a | They used an unsupervised anomaly detector for a rule that was already fully specified |
| 4b | `df['is_expensive'] = df['amount'] > 10000` |
| 4c | Valid answers: detecting truly anomalous patterns with no known threshold, fraud detection across multiple correlated features, situations where the definition of "anomalous" shifts over time |
| 5 | Any answer where a loop, formula, or lookup table is faster, more reliable, and more explainable than a model |

---

**Reflection prompt:** What is one situation in your daily life where you have been using a mental "model" (gut feeling) when a simple rule would serve you better?

> _______________________________________________________________________________

> _______________________________________________________________________________