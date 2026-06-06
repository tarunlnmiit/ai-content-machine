# users.csv — Instructor Answer Key

Generator `scripts/generate_course_dataset.py` · seed `42` · rows `4000` · generated 2026-06-06. **SYNTHETIC — fabricated, not real customer data.** Same seed → byte-identical CSV.

## Task 1 — the crack in the AI's logic (model answer)
- The AI computed churn as `churned / all users ever` = **9.88%**. The denominator
  includes every user who ever signed up, so the rate is meaninglessly deflated.
- Correct: churn among users *active last month* (2026-05, 402 users) =
  **27.36%** — over 2.8× the naive figure.
- **Fix:** `recent = df[df['last_active_month'] == '2026-05']; churn = (recent['status']=='churned').mean()`.
- Without reading the data dictionary you'd ship the deflated number — a wrong denominator
  is a logic bug that runs cleanly and produces a plausible-looking result.
