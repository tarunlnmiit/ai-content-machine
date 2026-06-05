# Baselines and Sanity Checks Before Modelling — Worksheet

**Objective:** Before you train any model, lock in a baseline score and verify your data pipeline is doing what you think it is.

---

## Scenario

You're a junior data scientist at an edtech startup. The product team wants to predict which students will drop a course before completing it. Someone hands you a CSV with 10,000 rows and says: "Train something by Friday."

Before touching any algorithm, your job is to make sure you're not solving a broken problem with a broken setup.

---

## Task 1 — Read the Label Distribution (Easy)

You load the dataset and peek at the target column `dropped` (1 = dropped, 0 = completed).

```python
import pandas as pd

df = pd.read_csv("student_engagement.csv")
print(df['dropped'].value_counts())
print(df['dropped'].value_counts(normalize=True).round(3))
```

**1a.** Run this code (or imagine the output below). What does the distribution tell you before you build anything?

```
dropped
0    8400
1    1600
dtype: int64

dropped
0    0.84
1    0.16
dtype: float64
```

Write your interpretation here:

____
____
____

**1b.** If a model always predicts `0` (never dropped) for every student, what accuracy would it get on this dataset? Calculate it.

____

**1c.** Is that accuracy impressive? Why or why not?

____
____

---

## Task 2 — Implement a Dummy Baseline (Easy → Medium)

A dummy baseline is your floor. Any model you build must beat it — if it doesn't, you haven't learned anything useful yet.

```python
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

X = df.drop(columns=['dropped'])
y = df['dropped']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

dummy = DummyClassifier(strategy="most_frequent")
dummy.fit(X_train, y_train)
y_pred = dummy.predict(X_test)

print(classification_report(y_test, y_pred))
```

**2a.** What does `strategy="most_frequent"` do? Describe in plain words.

____
____

**2b.** Look at the classification report output below. Fill in the blanks with what you'd expect for each class, given the 84/16 split.

```
              precision    recall  f1-score   support

           0       ____      ____      ____      1680
           1       ____      ____      ____       320
```

*Hint: Think about what happens to class 1 when the classifier always predicts class 0.*

**2c.** Why is `stratify=y` important in the train/test split for this dataset?

____
____

---

## Task 3 — Sanity Check Your Features (Medium)

A sanity check catches silent data leakage or preprocessing bugs before they corrupt your results.

You have these features:

| Column | Description |
|--------|-------------|
| `last_login_days_ago` | Days since last platform login |
| `videos_watched` | Total videos watched |
| `completion_pct` | % of course completed at time of prediction |
| `quiz_avg_score` | Average quiz score |
| `enrolled_days` | Days since enrollment |

**3a.** One of these features is almost certainly data leakage for predicting dropout. Which one, and why?

Suspicious feature: ____

Reason:
____
____

**3b.** Write a quick sanity check — a few lines of code — that would surface whether any features are suspiciously correlated with the target (above 0.9 absolute correlation). Use pandas.

```python
# Your code here




```

**3c.** You also want to check for target leakage from the future. Describe in one sentence what "leakage from the future" means in this context, using the enrollment scenario.

____
____

---

## Task 4 — Set Your Evaluation Metric Before Training (Applied)

Accuracy is the wrong metric here. You need to choose the right one before you start, not after you see your results.

**4a.** The product team says: *"We'd rather flag 50 at-risk students who weren't actually going to drop than miss 10 who genuinely were."* Which metric should you optimise for — precision or recall on class 1? Circle one and justify.

**Precision / Recall** (circle one)

Justification:
____
____

**4b.** Write the code to compute this metric on your dummy classifier's predictions. Use scikit-learn.

```python
from sklearn.metrics import ____

score = ____(y_test, y_pred)
print(f"Baseline score: {score:.3f}")
```

**4c.** You train a logistic regression and get the following results:

| Model | Accuracy | Recall (class 1) | Precision (class 1) |
|-------|----------|-----------------|---------------------|
| Dummy | 0.84 | 0.00 | 0.00 |
| Logistic Regression | 0.81 | 0.55 | 0.43 |

The logistic regression has *lower accuracy* than the dummy. Should you reject it? Explain.

____
____
____

---

## Task 5 — Write Your Pre-Modelling Checklist (Applied)

You've just joined a new project: predicting loan default for a small fintech. You have no domain knowledge yet.

**5a.** Write a 5-point personal checklist you'd run through *before* training any model. Make it concrete enough that a teammate could follow it independently.

1. ____
2. ____
3. ____
4. ____
5. ____

**5b.** Which single check from your list would you do first, and why?

____
____

---

## Self-Check

Read these against your answers. No peeking before you've written something.

**Task 1:** The 84/16 split means always predicting "not dropped" gives 84% accuracy for free. That's your floor — not a result to be proud of. Imbalanced datasets make accuracy misleading by design.

**Task 2:** `most_frequent` always predicts the majority class. Class 1 recall should be 0.00 — the dummy never predicts it. `stratify=y` ensures both train and test sets preserve the 84/16 split, so you're not accidentally testing on a balanced subset.

**Task 3:** `completion_pct` is the leakage risk — if a student is 90% through the course, they almost certainly won't drop. That information reflects outcome, not signal available at prediction time. Leakage from the future means using data that wouldn't exist at the point you'd actually make the prediction in production.

**Task 4:** Recall on class 1 — because missing an at-risk student costs more than a false alarm. Lower accuracy with higher recall on the minority class is a genuine improvement. Accuracy went down because the model stopped exploiting the majority class; that's the right tradeoff here.

**Task 5:** No single right answer — but your checklist should mention: checking label distribution, picking a metric before training, checking for leakage, setting a dummy baseline, and verifying train/test split logic. First step is almost always the label distribution: if you don't know your target's shape, nothing else is grounded.

---

*Keep this sheet. Before your next modelling session, run through Tasks 1–3 first. It takes 10 minutes and will save you hours of chasing fake results.*