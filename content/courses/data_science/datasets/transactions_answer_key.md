# transactions.csv — Instructor Answer Key

Generator `scripts/generate_course_dataset.py` · seed `42` · rows `3000` · generated 2026-06-06. **SYNTHETIC — fabricated, not real customer data.** Same seed → byte-identical CSV.

## What the data holds
- 3000 transactions · columns `user_id, amount, category`.
- **129** rows are above ₹10,000 (what the business rule flags).
- 30 negative amounts (refunds) — realistic noise.

## Task 4 — the decision bug (model answer)
- **4a:** The analyst used an unsupervised anomaly detector (`IsolationForest`) for a rule
  that was already fully specified (`amount > 10000`). ML adds non-determinism, false
  positives, and a model to maintain — for zero gain over one comparison.
- **4b (correct fix):** `df['is_expensive'] = df['amount'] > 10000`
  → flags exactly **129** rows, deterministically, every run.
- IsolationForest with `contamination=0.05` would instead flag ~5% (~150) rows — many of them *not* above ₹10,000, and it would miss the
  point entirely: the threshold is a business decision, not a statistical outlier.
- **4c:** Isolation Forest *is* right when there is no known threshold and 'anomalous' must
  be learned across correlated features (e.g. fraud), or when the definition drifts over time.
