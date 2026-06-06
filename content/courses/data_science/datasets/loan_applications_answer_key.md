# loan_applications.csv — Instructor Answer Key (failure-mode reference)

## Provenance
- Generator: `scripts/generate_course_dataset.py` · seed `42` · rows `3000`
- Generated: 2026-06-06
- **SYNTHETIC — fabricated realistic mess, not real anonymised customer data.**
- Reproducible: same seed + row count yields a byte-identical CSV.

## Summary — every injected flaw

| Column | Failure mode | Rows affected | Worksheet task |
|---|---|---|---|
| `application_id` | Duplicate application IDs | 45 | Task 3c |
| `age` | Negative ages | 35 | Task 3 (Q3a) |
| `age` | Ages above 100 | 29 | Task 3 (Q3a) |
| `age` | Missing ages | 90 | Task 2 |
| `annual_income` | Negative income | 23 | Task 3 (Q3a) |
| `annual_income` | Zero income | 36 | Task 3 (Q3a) |
| `loan_amount` | Extreme loan-to-income | 62 | Task 3 (Q3a) |
| `monthly_emi` | Number stored as string | 390 | Task 1 (Q1c) |
| `cibil_score` | Non-random missing credit score | 461 | Task 2 (Q2c) |
| `employment_type` | Inconsistent categoricals | 420 | Task 4 |
| `loan_purpose` | Inconsistent categoricals + encoding junk | 360 | Task 4 |
| `event_timestamp` | Three timezones stitched together | 889 | Task 1 / Task 4 |
| `applied_channel` | Plain missing values | 240 | Task 2 (Q2a) |

## Top-3 columns by missing % (Task 2 answer)

| Rank | Column | Missing count | Missing % |
|---|---|---|---|
| 1 | `cibil_score` | 461 | 15.37% |
| 2 | `applied_channel` | 240 | 8.00% |
| 3 | `monthly_emi` | 176 | 5.87% |

## Flaw detail

### `application_id` — Duplicate application IDs
- **Rows affected (measured):** 45
- **How it was injected:** A slice of rows had their ID overwritten with an ID already used by an earlier row.
- **What a correct audit finds:** The primary key is not unique; joining or de-duping on it would silently merge applicants.
- **Surfaced by:** Task 3c

### `age` — Negative ages
- **Rows affected (measured):** 35
- **How it was injected:** A small set of ages was flipped to a negative number (sign-flip / bad form input).
- **What a correct audit finds:** Impossible values present; range checks are mandatory before modelling.
- **Surfaced by:** Task 3 (Q3a)

### `age` — Ages above 100
- **Rows affected (measured):** 29
- **How it was injected:** Some ages were set to 1xx (likely a year keyed into an age field).
- **What a correct audit finds:** Upper-bound impossible values; the field needs a sane [18,100] gate.
- **Surfaced by:** Task 3 (Q3a)

### `age` — Missing ages
- **Rows affected (measured):** 90
- **How it was injected:** Some ages were nulled to NaN.
- **What a correct audit finds:** Age is missing for part of the book; imputing it for a credit decision is risky.
- **Surfaced by:** Task 2

### `annual_income` — Negative income
- **Rows affected (measured):** 23
- **How it was injected:** A few incomes were sign-flipped negative.
- **What a correct audit finds:** Negative income is impossible; it poisons any ratio that uses income as a denominator.
- **Surfaced by:** Task 3 (Q3a)

### `annual_income` — Zero income
- **Rows affected (measured):** 36
- **How it was injected:** Some incomes were set to exactly 0 (blank coerced to zero on export).
- **What a correct audit finds:** Zero income breaks loan-to-income (division yields inf); these rows must be quarantined.
- **Surfaced by:** Task 3 (Q3a)

### `loan_amount` — Extreme loan-to-income
- **Rows affected (measured):** 62
- **How it was injected:** Loan amounts on some rows were inflated to many multiples of income.
- **What a correct audit finds:** Loan-to-income > 50 flags data error or fraud; not modellable as-is.
- **Surfaced by:** Task 3 (Q3a)

### `monthly_emi` — Number stored as string
- **Rows affected (measured):** 390
- **How it was injected:** The whole column was exported as text; some cells carry currency symbols, commas, 'N/A', or blanks.
- **What a correct audit finds:** dtype is text (shows as str/object), so numeric ops fail until parsed; the classic dtype-surprise trap.
- **Surfaced by:** Task 1 (Q1c)

### `cibil_score` — Non-random missing credit score
- **Rows affected (measured):** 461
- **How it was injected:** Nulls were clustered into self-employed applicants (the bureau pull failed for that segment).
- **What a correct audit finds:** Missingness is NOT random — dropping rows would systematically remove the self-employed.
- **Surfaced by:** Task 2 (Q2c)

### `employment_type` — Inconsistent categoricals
- **Rows affected (measured):** 420
- **How it was injected:** Canonical labels were replaced with case/whitespace/spelling variants on some rows.
- **What a correct audit finds:** The same category appears under several spellings; value_counts fragments without cleaning.
- **Surfaced by:** Task 4

### `loan_purpose` — Inconsistent categoricals + encoding junk
- **Rows affected (measured):** 360
- **How it was injected:** Variants plus double spaces, trailing spaces, and a typo ('buisness') were injected.
- **What a correct audit finds:** Stray whitespace and typos create phantom categories that value_counts splits apart.
- **Surfaced by:** Task 4

### `event_timestamp` — Three timezones stitched together
- **Rows affected (measured):** 889
- **How it was injected:** Rows were rewritten in mixed string formats representing IST, UTC, and a US-format source.
- **What a correct audit finds:** One column silently holds three realities; naive parsing shifts events by hours.
- **Surfaced by:** Task 1 / Task 4

### `applied_channel` — Plain missing values
- **Rows affected (measured):** 240
- **How it was injected:** A modest fraction of the channel field was nulled.
- **What a correct audit finds:** A lower-rate gap that still ranks in the top-3 missing columns; affects attribution.
- **Surfaced by:** Task 2 (Q2a)

## Expected Data Quality Report (Task 5 model answer)

```
DATA QUALITY REPORT
Dataset: loan_applications.csv
Total rows: 3000   Total columns: 10

Critical Issue 1: event_timestamp — Three timezones stitched together (889 rows). One column silently holds three realities; naive parsing shifts events by hours.

Critical Issue 2: cibil_score — Non-random missing credit score (461 rows). Missingness is NOT random — dropping rows would systematically remove the self-employed.

Critical Issue 3: employment_type — Inconsistent categoricals (420 rows). The same category appears under several spellings; value_counts fragments without cleaning.

Recommendation: NOT usable as-is. Quarantine impossible values, parse monthly_emi,
reconcile the three timestamp formats, and treat cibil_score missingness as informative
(do not drop self-employed rows) before any modelling.
```
