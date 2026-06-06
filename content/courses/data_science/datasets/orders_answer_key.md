# orders.csv — Instructor Answer Key

Generator `scripts/generate_course_dataset.py` · seed `42` · rows `3000` · generated 2026-06-06. **SYNTHETIC — fabricated, not real customer data.** Same seed → byte-identical CSV.

## Task 1 — audit (model answer)
- **Columns with missing values:** `customer_id` (150), `order_date` (180), `order_value` (120).
- **`order_date` reads back as a string** (object/str), not datetime — trend analysis over
  time needs `df['order_date'] = pd.to_datetime(df['order_date'])` first (Task 1c).
- Cannot answer from this data alone: anything about *why* customers returned, customer
  demographics, or profit (no cost column).

## A defensible scoped question (Task 2)
*Using 3 months of orders, find which product categories have the highest return rate, so
the business can prioritise quality checks.* Return rate by category:

| Category | Return rate |
|---|---|
| electronics | 28.2% |
| clothing | 24.2% |
| toys | 12.7% |
| home | 9.1% |
| books | 7.3% |
| grocery | 3.1% |

Validation that needs no model: the ranking should match human intuition
(electronics/clothing return more than books/grocery).
