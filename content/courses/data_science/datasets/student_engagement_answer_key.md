# student_engagement.csv — Instructor Answer Key

Generator `scripts/generate_course_dataset.py` · seed `42` · rows `10000` · generated 2026-06-06. **SYNTHETIC — fabricated, not real customer data.** Same seed → byte-identical CSV.
- **Requires scikit-learn** (`pip install scikit-learn`) to run Tasks 2 & 4.

## Task 1 — label distribution (model answer)
```
dropped
0    8400
1    1600

0    0.840
1    0.160
```
- Always predicting 0 scores **84.00%** for free — that is the floor, not a result.
- Accuracy is misleading on a 84%/16% imbalance.

## Task 2 — dummy baseline
- `most_frequent` always predicts the majority class (0). At `test_size=0.2`, support is
  ~1680 (class 0) / ~320 (class 1).
- **Class-1 recall = 0.00** (the dummy never predicts it); precision 0.00. `stratify=y`
  keeps the 84/16 split in both train and test.

## Task 3 — leakage
- **`completion_pct` is the leak** (|corr| = 0.938 with `dropped`). A student 90%
  through the course almost cannot drop — that reflects the outcome, not signal available at
  prediction time. Every other feature sits well below 0.9.

## Task 4 — metric
- Optimise **recall on class 1**: missing an at-risk student costs more than a false alarm.
- Lower accuracy with higher minority-class recall is the right tradeoff — the model stopped
  exploiting the majority class.
