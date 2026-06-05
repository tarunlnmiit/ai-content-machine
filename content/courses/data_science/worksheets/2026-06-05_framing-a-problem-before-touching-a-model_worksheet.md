# Framing a Problem Before Touching a Model — Worksheet

**Objective:** Take a vague business request and convert it into a precise, measurable target variable you can actually train a model on.

---

## The Scenario

You've just joined a D2C startup that sells affordable skincare products online. The founder calls you into a Zoom and says:

> *"We're losing customers. Can you use AI to fix our retention problem?"*

That's it. No data dictionary. No KPI. No definition of "losing."

Your job — before opening a single notebook — is to turn this into something a model can learn from.

---

## Task 1 — Decompose the Vague Ask (Easy)

The founder's statement contains **three hidden assumptions**. List them below.

**Example of what a hidden assumption looks like:**  
*"Losing customers" assumes we know what counts as 'lost' — but does that mean no purchase in 30 days? 90 days? Forever?*

Your three assumptions:

1. ____________________________________________________________________

   ____________________________________________________________________

2. ____________________________________________________________________

   ____________________________________________________________________

3. ____________________________________________________________________

   ____________________________________________________________________

---

## Task 2 — Define the Target Variable (Medium)

A target variable must be:
- **Binary or numeric** (something a model can predict)
- **Tied to a specific time window**
- **Calculable from data you actually have**

Below is a sample from the company's order table:

```python
import pandas as pd

orders = pd.DataFrame({
    "customer_id": [101, 101, 102, 103, 103, 104],
    "order_date":  ["2024-01-05", "2024-03-10",
                    "2024-01-20",
                    "2024-02-01", "2024-02-28",
                    "2024-01-15"],
    "order_value": [450, 620, 310, 290, 480, 700]
})

orders["order_date"] = pd.to_datetime(orders["order_date"])
```

**2a.** Write a function that labels a customer as **churned (1)** if they have made **no purchase in the 60 days after their last order**, evaluated as of `2024-04-30`. Non-churned customers get label **0**.

```python
EVALUATION_DATE = pd.Timestamp("2024-04-30")
CHURN_WINDOW_DAYS = 60

def label_churn(orders_df, eval_date, window_days):
    # Step 1: Find each customer's last order date
    last_orders = ___________________________________

    # Step 2: Calculate days since last order (from eval_date)
    last_orders["days_since"] = ___________________________________

    # Step 3: Assign churn label
    last_orders["churned"] = (last_orders["days_since"] > window_days).astype(int)

    return last_orders[["customer_id", "days_since", "churned"]]

result = label_churn(orders, EVALUATION_DATE, CHURN_WINDOW_DAYS)
print(result)
```

**Expected output shape:** One row per customer. `churned` column is 0 or 1.

**2b.** After running this, customer 102 gets `churned = 1`. Customer 103 gets `churned = 0`. Does that match your intuition? Why?

____________________________________________________________________

____________________________________________________________________

---

## Task 3 — Stress-Test Your Definition (Medium)

Every target variable definition has edge cases that can silently corrupt your training data.

For each scenario below, write whether your 60-day churn definition **handles it correctly**, and if not, how you'd fix it.

| Scenario | Correct? (Y/N) | Fix if needed |
|---|---|---|
| A customer placed an order on April 28 (two days before eval date) | | |
| A customer returned their only order and got a refund | | |
| A new customer joined on April 20 (10 days before eval) | | |

---

## Task 4 — Write the Problem Statement (Applied)

You now have a definition. Write a **one-paragraph ML problem statement** that includes all of the following:

- What you're predicting (the target variable, precisely defined)
- The time window
- Why it matters to the business (in plain terms, not "AI will help")
- One thing this definition *cannot* tell you

Write it here:

____________________________________________________________________

____________________________________________________________________

____________________________________________________________________

____________________________________________________________________

____________________________________________________________________

____________________________________________________________________

---

## Task 5 — Spot the Trap (Applied)

A colleague on your team proposes a different target variable:

> *"Let's predict order_value for each customer's next purchase. Higher predicted value = more loyal customer."*

List **two specific problems** with using this as a retention metric. Be concrete — name the exact failure mode.

**Problem 1:**

____________________________________________________________________

____________________________________________________________________

**Problem 2:**

____________________________________________________________________

____________________________________________________________________

---

## Self-Check

Compare your work against these markers. Be honest — partial credit counts.

**Task 1 — Decompose**  
Strong answers name at least: (a) what "lost" means numerically, (b) what time window counts, (c) whether the goal is prediction or diagnosis. If you named all three, you're set.

**Task 2 — Code**  
Your `label_churn` should use `groupby("customer_id")["order_date"].max()` to get last order dates. Days since = `(eval_date - last_order_date).dt.days`. The `.astype(int)` on a boolean gives clean 0/1 labels. Customer 102's last order was Jan 20 — that's 100 days before April 30, so churn = 1. Customer 103's last order was Feb 28 — that's 61 days, just over the window, churn = 1 also (double-check your own output).

**Task 3 — Stress-test**  
The April 28 customer is a false positive risk — only 2 days of data, no fair chance to reorder. Fix: exclude customers whose first or last order falls within the churn window of the eval date. Refunded orders should be excluded from order history. New customers (joined < 60 days ago) should be excluded from training data entirely.

**Task 4 — Problem statement**  
A clean statement sounds like: *"We want to predict, for each customer active in the last 6 months, whether they will place no order in the 60 days following their most recent purchase (as of April 30, 2024). A label of 1 means churned. This lets the business identify at-risk customers before the window closes so retention offers can be targeted. This definition cannot distinguish customers who churned by choice from those who had no trigger to return — both look identical in the data."*

**Task 5 — Spot the trap**  
Two strong answers: (1) Order value is not a loyalty signal — a high-value one-time buyer looks "loyal" but never returns. (2) You need future data to compute the target, which creates a data leakage problem the moment you join it with features from the same period.

---

*If Tasks 1–3 feel solid but Task 4 was hard to write in one paragraph — that's the real skill gap. Precision in definition is harder than writing code. Go back and rewrite Task 4 until it would make sense to the founder on that Zoom call.*