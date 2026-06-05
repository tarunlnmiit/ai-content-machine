# Scoping a first end-to-end project — Worksheet

**Objective:** By the end of this worksheet, you will have a concrete, scoped plan for a 1-week end-to-end data science project you can actually finish.

---

## Scenario

You just got your first internship at a mid-size e-commerce company in Bengaluru. Your manager drops this message on your first day:

> "We have 3 months of order data sitting in a CSV. Can you do something useful with it by Friday?"

No further instructions. This is real life.

Your job this week: figure out *what* to build before you build anything.

---

## Task 1 — Audit the Data Before Promising Anything
*(Easy — about 15 minutes)*

Here is a small sample of what the CSV looks like. Run this code and answer the questions below.

```python
import pandas as pd

# Simulated sample — replace with your actual CSV when you have it
data = {
    "order_id": [1001, 1002, 1003, 1004, 1005],
    "customer_id": [201, 202, 201, 203, None],
    "order_date": ["2024-01-03", "2024-01-03", "2024-01-05", None, "2024-01-07"],
    "product_category": ["electronics", "clothing", "electronics", "books", "clothing"],
    "order_value": [4999, 799, None, 299, 1200],
    "returned": [0, 0, 1, 0, 1]
}

df = pd.DataFrame(data)

print(df.dtypes)
print("\nMissing values per column:")
print(df.isnull().sum())
print("\nRows:", len(df))
```

**1a.** Which columns have missing values?

```
____
____
```

**1b.** What data type does `order_date` come back as? Why is that a problem if you want to analyze trends over time?

```
____
____
```

**1c.** Write one line of code to convert `order_date` to a proper datetime column.

```python
df["order_date"] = ____
```

**1d.** Before any analysis — name one question you *cannot* answer from this data alone (something the data simply doesn't contain).

```
____
```

---

## Task 2 — Narrow the Problem to One Question
*(Easy → Medium — about 20 minutes)*

Your manager said "do something useful." That is not a problem statement. A real problem statement has a single measurable outcome.

**2a.** Below are five possible directions. Cross out any that are too vague, too large for one week, or require data you don't have (based on Task 1).

- [ ] Predict which customers will churn next month
- [ ] Find which product categories have the highest return rate
- [ ] Build a real-time recommendation engine
- [ ] Identify whether order value differs by day of week
- [ ] Predict future revenue for the next quarter using 3 months of data

**2b.** Of the ones you kept, pick **one**. Write it as a proper problem statement:

> *"Using [what data], I want to find out [specific question], so that the business can [one concrete decision]."*

```
Using __________, I want to find out __________,
so that the business can __________.
```

**2c.** How will you know your answer is correct? Write one metric or check you can use to validate your output (not model accuracy — think: does the result make sense to a human?).

```
____
____
```

---

## Task 3 — Break It Into a 5-Day Plan
*(Medium — about 25 minutes)*

A one-week project fails when the first three days are all spent cleaning data and nothing is left for the actual analysis.

**3a.** Fill in the table. Be specific — "clean data" is not specific enough. "Drop rows where `order_date` is null, convert to datetime" is.

| Day | What you will do | What you will have at end of day |
|-----|------------------|----------------------------------|
| Mon | | |
| Tue | | |
| Wed | | |
| Thu | | |
| Fri | | |

**3b.** Identify the single riskiest day in your plan — the one where, if it takes twice as long, the whole project falls apart.

```
Riskiest day: ____
Why: ____
If this goes wrong, I will cut: ____
```

---

## Task 4 — Write the Skeleton Before Writing the Analysis
*(Applied — about 30 minutes)*

Real practitioners write the structure of their notebook before filling it in. It forces you to think before coding.

**4a.** Below is an empty notebook skeleton. Fill in each `# TODO` comment with one sentence describing *exactly* what that cell will do in your specific project (not generic — use your problem from Task 2b).

```python
# Cell 1 — Load data
import pandas as pd
# TODO: ____

df = pd.read_csv("orders.csv")

# Cell 2 — Understand the shape
# TODO: ____

# Cell 3 — Clean what needs cleaning
# TODO: ____

# Cell 4 — Answer the core question
# TODO: ____

# Cell 5 — Communicate the result
# TODO: ____
# (one print statement, one chart, or one table — pick one)
```

**4b.** Which cell are you least sure how to write right now?

```
Cell ____ because: ____
```

**4c.** Write the name of one Python function or method you will need to look up before you can write that cell.

```
Function/method: ____
```

---

## Task 5 — The Scope Check
*(Applied — 10 minutes)*

Before you start coding for real, run your plan through this filter.

Answer each question with a Y / N and one sentence.

**5a.** Can this project be done with the data you already have?

```
Y / N — ____
```

**5b.** Will your output be something a non-technical manager can read in under 2 minutes?

```
Y / N — ____
```

**5c.** If you lose 1 full day to a bug or a missing value problem, can you still produce *something* by Friday?

```
Y / N — ____
```

**5d.** If you answered N to any of the above — what is the one change to your scope that would flip it to Y?

```
____
____
```

---

## Self-Check

A well-scoped project plan looks like this:

- **Problem statement** names the data source, the specific question, and the decision it informs — not just "analyze data"
- **Day 1–2** are fully committed to understanding and cleaning the data; the analysis only starts Day 3
- **The output** is a single chart, table, or number — not a full report
- **The skeleton** matches the problem statement — every cell has a clear job tied to the actual question
- **The risk is named** — you know which step might blow up and what you will cut if it does

If your plan passes all five checks above, you are ready to open a notebook.

If it fails any one of them, revise that section before moving on.

---

*Worksheet ends here. Keep this with your project folder — reread it on Wednesday to check if scope has drifted.*