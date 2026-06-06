#!/usr/bin/env python3
"""Generate a SEEDED synthetic dirty dataset + failure-mode answer key for a course.

Companion asset for the Data Science course L2 worksheet
(content/courses/data_science/worksheets/2026-06-05_auditing-messy-real-world-data_worksheet.md).
That worksheet ships verbatim student code that loads `loan_applications.csv` and audits it;
this script produces the file it reads, plus an instructor answer key.

Design — no drift between data and answer key:
  A single `Flaw` registry is the source of truth for WHICH flaws exist and HOW they are
  injected. Every COUNT in the answer key is re-measured from the FINAL written frame using
  the worksheet's own predicates (each Flaw carries a `measure` callable). Injection-time
  counts are never trusted, because flaws overlap (e.g. `age` gets negatives, >100, and NaN —
  a later injector can overwrite a row an earlier one touched).

Binding constraint (pandas 3.x raises TypeError on `object < int`):
  `age`, `annual_income`, `loan_amount` stay NUMERIC so Task 3 runs. The number-stored-as-string
  flaw lives on `monthly_emi` (object). `loan_to_income` is NOT emitted — the worksheet derives it.

Usage (always inside the project conda env):
  conda run -n content_engine_env python scripts/generate_course_dataset.py --niche ds
"""

import argparse
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from _console import console

REPO = Path(__file__).parent.parent
NICHES = {"ds": "data_science"}  # only ds wired; life/poetry assets are static, no generator

# --- domain vocab (fintech loans; relatable to 18-25 Indian students) ---
EMPLOYMENT_CANONICAL = ["Salaried", "Self-Employed", "Student", "Unemployed"]
PURPOSE_CANONICAL = ["Education", "Personal", "Vehicle", "Home Renovation", "Medical", "Business"]
CHANNEL_CANONICAL = ["Mobile App", "Website", "Branch", "DSA Agent", "Call Center"]
TS_BASE = date(2024, 1, 1)          # fixed window — never datetime.now() (determinism)
TS_SPAN_DAYS = 270

# messy variants injected into categoricals (mixed case / whitespace / encoding junk)
EMPLOYMENT_VARIANTS = ["salaried", "SALARIED ", " Self Employed", "self-employed", "Student ", "UNEMPLOYED"]
PURPOSE_VARIANTS = ["education", "PERSONAL", " Vehicle", "Home  Renovation", "Medical ", "buisness"]
EMI_JUNK = ["₹12,000", "N/A", "", "NA", "₹ 8,500", "-"]


# --------------------------------------------------------------------------------------
# Flaw registry — single source of truth
# --------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Flaw:
    column: str
    failure_mode: str
    mechanism: str          # how it was injected (prose for the answer key)
    finding: str            # what a correct audit concludes
    worksheet_ref: str      # which worksheet task surfaces it
    measure: Callable[[pd.DataFrame], int]  # re-counts the flaw on the FINAL frame


def _ratio(df: pd.DataFrame) -> pd.Series:
    # mirrors worksheet line 123 exactly (div-by-zero -> inf, counted as extreme like the lesson)
    return df["loan_amount"] / df["annual_income"]


FLAWS: list[Flaw] = [
    Flaw("application_id", "Duplicate application IDs",
         "A slice of rows had their ID overwritten with an ID already used by an earlier row.",
         "The primary key is not unique; joining or de-duping on it would silently merge applicants.",
         "Task 3c", lambda df: int(df["application_id"].duplicated().sum())),
    Flaw("age", "Negative ages",
         "A small set of ages was flipped to a negative number (sign-flip / bad form input).",
         "Impossible values present; range checks are mandatory before modelling.",
         "Task 3 (Q3a)", lambda df: int((df["age"] < 0).sum())),
    Flaw("age", "Ages above 100",
         "Some ages were set to 1xx (likely a year keyed into an age field).",
         "Upper-bound impossible values; the field needs a sane [18,100] gate.",
         "Task 3 (Q3a)", lambda df: int((df["age"] > 100).sum())),
    Flaw("age", "Missing ages",
         "Some ages were nulled to NaN.",
         "Age is missing for part of the book; imputing it for a credit decision is risky.",
         "Task 2", lambda df: int(df["age"].isna().sum())),
    Flaw("annual_income", "Negative income",
         "A few incomes were sign-flipped negative.",
         "Negative income is impossible; it poisons any ratio that uses income as a denominator.",
         "Task 3 (Q3a)", lambda df: int((df["annual_income"] < 0).sum())),
    Flaw("annual_income", "Zero income",
         "Some incomes were set to exactly 0 (blank coerced to zero on export).",
         "Zero income breaks loan-to-income (division yields inf); these rows must be quarantined.",
         "Task 3 (Q3a)", lambda df: int((df["annual_income"] == 0).sum())),
    Flaw("loan_amount", "Extreme loan-to-income",
         "Loan amounts on some rows were inflated to many multiples of income.",
         "Loan-to-income > 50 flags data error or fraud; not modellable as-is.",
         "Task 3 (Q3a)", lambda df: int((_ratio(df) > 50).sum())),
    Flaw("monthly_emi", "Number stored as string",
         "The whole column was exported as text; some cells carry currency symbols, commas, 'N/A', or blanks.",
         "dtype is text (shows as str/object), so numeric ops fail until parsed; the classic dtype-surprise trap.",
         "Task 1 (Q1c)", lambda df: int(pd.to_numeric(df["monthly_emi"], errors="coerce").isna().sum())),
    Flaw("cibil_score", "Non-random missing credit score",
         "Nulls were clustered into self-employed applicants (the bureau pull failed for that segment).",
         "Missingness is NOT random — dropping rows would systematically remove the self-employed.",
         "Task 2 (Q2c)", lambda df: int(df["cibil_score"].isna().sum())),
    Flaw("employment_type", "Inconsistent categoricals",
         "Canonical labels were replaced with case/whitespace/spelling variants on some rows.",
         "The same category appears under several spellings; value_counts fragments without cleaning.",
         "Task 4", lambda df: int((~df["employment_type"].isin(EMPLOYMENT_CANONICAL)).sum())),
    Flaw("loan_purpose", "Inconsistent categoricals + encoding junk",
         "Variants plus double spaces, trailing spaces, and a typo ('buisness') were injected.",
         "Stray whitespace and typos create phantom categories that value_counts splits apart.",
         "Task 4", lambda df: int((~df["loan_purpose"].isin(PURPOSE_CANONICAL)).sum())),
    Flaw("event_timestamp", "Three timezones stitched together",
         "Rows were rewritten in mixed string formats representing IST, UTC, and a US-format source.",
         "One column silently holds three realities; naive parsing shifts events by hours.",
         "Task 1 / Task 4", lambda df: int((~df["event_timestamp"].str.match(r"^\d{4}-\d{2}-\d{2} ")).sum())),
    Flaw("applied_channel", "Plain missing values",
         "A modest fraction of the channel field was nulled.",
         "A lower-rate gap that still ranks in the top-3 missing columns; affects attribution.",
         "Task 2 (Q2a)", lambda df: int(df["applied_channel"].isna().sum())),
]


# --------------------------------------------------------------------------------------
# clean frame + injectors  (every random draw comes from the one passed-in rng)
# --------------------------------------------------------------------------------------
def build_clean_frame(rng: np.random.Generator, rows: int) -> pd.DataFrame:
    ids = [f"LA2024{i:06d}" for i in range(rows)]
    loan_amount = rng.integers(50_000, 1_500_000, rows).astype(float)
    base_dt = datetime(TS_BASE.year, TS_BASE.month, TS_BASE.day)
    offsets = rng.integers(0, TS_SPAN_DAYS * 86_400, rows)
    timestamps = [(base_dt + timedelta(seconds=int(s))).strftime("%Y-%m-%d %H:%M:%S") for s in offsets]
    return pd.DataFrame({
        "application_id": ids,
        "age": rng.integers(18, 61, rows).astype(float),
        "annual_income": rng.integers(150_000, 1_800_000, rows).astype(float),
        "loan_amount": loan_amount,
        "monthly_emi": (loan_amount * 0.021).round().astype(int),  # stringified last
        "cibil_score": rng.integers(300, 901, rows).astype(float),
        "employment_type": rng.choice(EMPLOYMENT_CANONICAL, rows),
        "loan_purpose": rng.choice(PURPOSE_CANONICAL, rows),
        "event_timestamp": timestamps,
        "applied_channel": rng.choice(CHANNEL_CANONICAL, rows),
    })


def _pick(rng: np.random.Generator, n: int, frac: float) -> np.ndarray:
    return rng.choice(n, size=max(1, int(n * frac)), replace=False)


def inject_duplicate_ids(df: pd.DataFrame, rng: np.random.Generator) -> None:
    n = len(df)
    targets = _pick(rng, n, 0.015)
    sources = rng.choice(np.setdiff1d(np.arange(n), targets), size=len(targets), replace=False)
    df.loc[df.index[targets], "application_id"] = df["application_id"].to_numpy()[sources]


def inject_cibil_missing(df: pd.DataFrame, rng: np.random.Generator) -> None:
    # clustered in self-employed rows -> non-random missingness (run before employment is messed)
    self_emp = np.flatnonzero(df["employment_type"].to_numpy() == "Self-Employed")
    take = rng.choice(self_emp, size=int(len(self_emp) * 0.62), replace=False)
    df.loc[df.index[take], "cibil_score"] = np.nan


def inject_age_flaws(df: pd.DataFrame, rng: np.random.Generator) -> None:
    n = len(df)
    df.loc[df.index[_pick(rng, n, 0.012)], "age"] = rng.integers(-40, -1)
    df.loc[df.index[_pick(rng, n, 0.010)], "age"] = rng.integers(101, 180)
    df.loc[df.index[_pick(rng, n, 0.030)], "age"] = np.nan


def inject_income_flaws(df: pd.DataFrame, rng: np.random.Generator) -> None:
    n = len(df)
    df.loc[df.index[_pick(rng, n, 0.008)], "annual_income"] = -rng.integers(50_000, 900_000)
    df.loc[df.index[_pick(rng, n, 0.012)], "annual_income"] = 0.0
    df.loc[df.index[_pick(rng, n, 0.030)], "annual_income"] = np.nan


def inject_loan_extremes(df: pd.DataFrame, rng: np.random.Generator) -> None:
    n = len(df)
    df.loc[df.index[_pick(rng, n, 0.010)], "loan_amount"] = rng.integers(80_000_000, 250_000_000)
    df.loc[df.index[_pick(rng, n, 0.025)], "loan_amount"] = np.nan


def inject_employment_mess(df: pd.DataFrame, rng: np.random.Generator) -> None:
    idx = _pick(rng, len(df), 0.14)
    df.loc[df.index[idx], "employment_type"] = rng.choice(EMPLOYMENT_VARIANTS, len(idx))


def inject_loan_purpose_junk(df: pd.DataFrame, rng: np.random.Generator) -> None:
    idx = _pick(rng, len(df), 0.12)
    df.loc[df.index[idx], "loan_purpose"] = rng.choice(PURPOSE_VARIANTS, len(idx))


def inject_timestamp_tz(df: pd.DataFrame, rng: np.random.Generator) -> None:
    n = len(df)
    utc = _pick(rng, n, 0.18)   # ISO 8601 Z (UTC source)
    us = _pick(rng, n, 0.14)    # US mm/dd/yyyy (third system)
    df.loc[df.index[utc], "event_timestamp"] = (
        df["event_timestamp"].iloc[utc].str.replace(" ", "T") + "Z"
    )
    df.loc[df.index[us], "event_timestamp"] = pd.to_datetime(
        df["event_timestamp"].iloc[us].str.replace("Z", "").str.replace("T", " ")
    ).dt.strftime("%m/%d/%Y %H:%M")


def inject_channel_missing(df: pd.DataFrame, rng: np.random.Generator) -> None:
    df.loc[df.index[_pick(rng, len(df), 0.08)], "applied_channel"] = np.nan


def inject_emi_string(df: pd.DataFrame, rng: np.random.Generator) -> None:
    # column-wide: stringify, then scatter currency/blank/NA junk so dtype stays object on read
    df["monthly_emi"] = df["monthly_emi"].astype(int).astype(str)
    idx = _pick(rng, len(df), 0.13)
    df.loc[df.index[idx], "monthly_emi"] = rng.choice(EMI_JUNK, len(idx))


# fixed order: cibil before employment-mess (cluster needs clean labels); emi-string LAST
INJECTORS = [
    inject_duplicate_ids, inject_cibil_missing, inject_age_flaws, inject_income_flaws,
    inject_loan_extremes, inject_employment_mess, inject_loan_purpose_junk,
    inject_timestamp_tz, inject_channel_missing, inject_emi_string,
]


def build_dirty(rng: np.random.Generator, rows: int) -> pd.DataFrame:
    df = build_clean_frame(rng, rows)
    for inject in INJECTORS:
        inject(df, rng)
    return df


# --------------------------------------------------------------------------------------
# answer key (counts re-measured from the FINAL frame)
# --------------------------------------------------------------------------------------
def render_answer_key(df: pd.DataFrame, seed: int, rows: int, name: str) -> str:
    counts = [(f, f.measure(df)) for f in FLAWS]
    missing = df.isnull().sum()
    top3 = missing[missing > 0].sort_values(ascending=False).head(3)

    lines = [
        f"# {name}.csv — Instructor Answer Key (failure-mode reference)",
        "",
        "## Provenance",
        f"- Generator: `scripts/generate_course_dataset.py` · seed `{seed}` · rows `{rows}`",
        f"- Generated: {date.today().isoformat()}",
        "- **SYNTHETIC — fabricated realistic mess, not real anonymised customer data.**",
        "- Reproducible: same seed + row count yields a byte-identical CSV.",
        "",
        "## Summary — every injected flaw",
        "",
        "| Column | Failure mode | Rows affected | Worksheet task |",
        "|---|---|---|---|",
    ]
    lines += [f"| `{f.column}` | {f.failure_mode} | {n} | {f.worksheet_ref} |" for f, n in counts]
    lines += [
        "",
        "## Top-3 columns by missing % (Task 2 answer)",
        "",
        "| Rank | Column | Missing count | Missing % |",
        "|---|---|---|---|",
    ]
    lines += [
        f"| {i} | `{col}` | {int(cnt)} | {cnt / rows * 100:.2f}% |"
        for i, (col, cnt) in enumerate(top3.items(), 1)
    ]
    lines += ["", "## Flaw detail", ""]
    for f, n in counts:
        lines += [
            f"### `{f.column}` — {f.failure_mode}",
            f"- **Rows affected (measured):** {n}",
            f"- **How it was injected:** {f.mechanism}",
            f"- **What a correct audit finds:** {f.finding}",
            f"- **Surfaced by:** {f.worksheet_ref}",
            "",
        ]

    rows_audited = len(df)
    crit = sorted(((f, n) for f, n in counts if isinstance(n, int)), key=lambda x: -x[1])[:3]
    lines += [
        "## Expected Data Quality Report (Task 5 model answer)",
        "",
        "```",
        "DATA QUALITY REPORT",
        f"Dataset: {name}.csv",
        f"Total rows: {rows_audited}   Total columns: {df.shape[1]}",
        "",
    ]
    for i, (f, n) in enumerate(crit, 1):
        lines += [f"Critical Issue {i}: {f.column} — {f.failure_mode} ({n} rows). {f.finding}", ""]
    lines += [
        "Recommendation: NOT usable as-is. Quarantine impossible values, parse monthly_emi,",
        "reconcile the three timestamp formats, and treat cibil_score missingness as informative",
        "(do not drop self-employed rows) before any modelling.",
        "```",
        "",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------------------
# loan_applications verify (round-trip): folds the binding constraint into code
# --------------------------------------------------------------------------------------
def verify_loan(df: pd.DataFrame) -> list[str]:
    checks = {
        "age numeric": pd.api.types.is_numeric_dtype(df["age"]),
        "annual_income numeric": pd.api.types.is_numeric_dtype(df["annual_income"]),
        "loan_amount numeric": pd.api.types.is_numeric_dtype(df["loan_amount"]),
        # pandas 3.x infers text as StringDtype('str'), not object — the trap is "not numeric"
        "monthly_emi non-numeric": not pd.api.types.is_numeric_dtype(df["monthly_emi"]),
        "no loan_to_income column": "loan_to_income" not in df.columns,
        "negative ages found": (df["age"] < 0).sum() > 0,
        "ages>100 found": (df["age"] > 100).sum() > 0,
        "income zeros found": (df["annual_income"] == 0).sum() > 0,
        "extreme ratio found": (df["loan_amount"] / df["annual_income"] > 50).sum() > 0,
        "duplicate ids found": df["application_id"].duplicated().sum() > 0,
    }
    return [name for name, ok in checks.items() if not ok]


# ======================================================================================
# transactions.csv  — L7 "Deciding when ML is the wrong tool"
#   Pedagogy: the rule `amount > 10000` is correct; IsolationForest is overkill.
# ======================================================================================
RULE_THRESHOLD = 10_000
TXN_CATEGORIES = ["groceries", "dining", "fuel", "electronics", "recharge", "apparel", "travel"]


def build_transactions(rng: np.random.Generator, rows: int) -> pd.DataFrame:
    amount = rng.lognormal(7.0, 0.8, rows).round(2)            # median ~₹1,100, light tail
    df = pd.DataFrame({
        "user_id": rng.integers(10_000, 99_999, rows),
        "amount": amount,
        "category": rng.choice(TXN_CATEGORIES, rows),
    })
    big = _pick(rng, rows, 0.04)                                # deliberate >₹10k big-ticket tail
    df.loc[df.index[big], "amount"] = rng.uniform(10_000, 80_000, len(big)).round(2)
    refunds = _pick(rng, rows, 0.01)                            # a few negative refunds (realism)
    df.loc[df.index[refunds], "amount"] = -rng.uniform(200, 5_000, len(refunds)).round(2)
    return df


def verify_transactions(df: pd.DataFrame) -> list[str]:
    checks = {
        "amount numeric": pd.api.types.is_numeric_dtype(df["amount"]),
        "amount has no NaN (IsolationForest would raise)": int(df["amount"].isna().sum()) == 0,
        "rule amount>10000 finds rows": (df["amount"] > RULE_THRESHOLD).sum() > 0,
        "category non-numeric": not pd.api.types.is_numeric_dtype(df["category"]),
    }
    return [name for name, ok in checks.items() if not ok]


def key_transactions(df: pd.DataFrame, meta: dict) -> str:
    n_flag = int((df["amount"] > RULE_THRESHOLD).sum())
    n_refund = int((df["amount"] < 0).sum())
    return "\n".join([
        f"# transactions.csv — Instructor Answer Key", "",
        _provenance(meta), "",
        "## What the data holds",
        f"- {len(df)} transactions · columns `user_id, amount, category`.",
        f"- **{n_flag}** rows are above ₹{RULE_THRESHOLD:,} (what the business rule flags).",
        f"- {n_refund} negative amounts (refunds) — realistic noise.", "",
        "## Task 4 — the decision bug (model answer)",
        "- **4a:** The analyst used an unsupervised anomaly detector (`IsolationForest`) for a rule",
        "  that was already fully specified (`amount > 10000`). ML adds non-determinism, false",
        "  positives, and a model to maintain — for zero gain over one comparison.",
        "- **4b (correct fix):** `df['is_expensive'] = df['amount'] > 10000`",
        f"  → flags exactly **{n_flag}** rows, deterministically, every run.",
        "- IsolationForest with `contamination=0.05` would instead flag ~5% (~"
        f"{round(len(df) * 0.05)}) rows — many of them *not* above ₹10,000, and it would miss the",
        "  point entirely: the threshold is a business decision, not a statistical outlier.",
        "- **4c:** Isolation Forest *is* right when there is no known threshold and 'anomalous' must",
        "  be learned across correlated features (e.g. fraud), or when the definition drifts over time.",
        "",
    ])


# ======================================================================================
# student_engagement.csv  — "Baselines and sanity checks"
#   Constraints: dropped exactly 16% (matches the sheet's 8400/1600); completion_pct is the
#   UNIQUE leakage feature (|corr|>0.9); every other feature |corr|<0.85.
# ======================================================================================
DROP_RATE = 0.16


def build_student_engagement(rng: np.random.Generator, rows: int) -> pd.DataFrame:
    n_drop = round(DROP_RATE * rows)
    dropped = np.zeros(rows, dtype=int)
    dropped[rng.permutation(rows)[:n_drop]] = 1                 # exactly n_drop ones, shuffled
    d = dropped.astype(bool)

    def split(rng, low_mean, low_sd, high_mean, high_sd):
        out = np.where(d, rng.normal(low_mean, low_sd, rows), rng.normal(high_mean, high_sd, rows))
        return out

    completion = np.clip(split(rng, 12, 5, 80, 10), 0, 100).round(1)   # leakage: |corr|>0.9
    last_login = np.clip(split(rng, 35, 18, 6, 8), 0, None).round(0)   # droppers idle longer
    videos = np.clip(split(rng, 8, 7, 45, 22), 0, None).round(0)
    quiz = np.clip(split(rng, 48, 18, 74, 15), 0, 100).round(1)
    enrolled = rng.integers(10, 200, rows)                            # independent of dropped
    return pd.DataFrame({
        "last_login_days_ago": last_login,
        "videos_watched": videos,
        "completion_pct": completion,
        "quiz_avg_score": quiz,
        "enrolled_days": enrolled.astype(float),
        "dropped": dropped,
    })


_SE_FEATURES = ["last_login_days_ago", "videos_watched", "completion_pct", "quiz_avg_score", "enrolled_days"]


def verify_student_engagement(df: pd.DataFrame) -> list[str]:
    n_drop = round(DROP_RATE * len(df))
    corr = {c: abs(df[c].corr(df["dropped"])) for c in _SE_FEATURES}
    others = [c for c in _SE_FEATURES if c != "completion_pct"]
    checks = {
        f"dropped == {n_drop} (exact {int(DROP_RATE*100)}%)": int((df["dropped"] == 1).sum()) == n_drop,
        "both classes present": df["dropped"].nunique() == 2,
        "all 6 cols numeric & no NaN": all(
            pd.api.types.is_numeric_dtype(df[c]) and df[c].isna().sum() == 0
            for c in _SE_FEATURES + ["dropped"]),
        "completion_pct |corr|>0.9 (the leakage)": corr["completion_pct"] > 0.9,
        "every other feature |corr|<0.85": all(corr[c] < 0.85 for c in others),
    }
    return [name for name, ok in checks.items() if not ok]


def key_student_engagement(df: pd.DataFrame, meta: dict) -> str:
    vc = df["dropped"].value_counts().sort_index()
    n0, n1 = int(vc.get(0, 0)), int(vc.get(1, 0))
    base_acc = n0 / len(df)
    leak_corr = abs(df["completion_pct"].corr(df["dropped"]))
    return "\n".join([
        f"# student_engagement.csv — Instructor Answer Key", "",
        _provenance(meta),
        "- **Requires scikit-learn** (`pip install scikit-learn`) to run Tasks 2 & 4.", "",
        "## Task 1 — label distribution (model answer)",
        "```",
        "dropped", f"0    {n0}", f"1    {n1}", "",
        f"0    {n0/len(df):.3f}", f"1    {n1/len(df):.3f}", "```",
        f"- Always predicting 0 scores **{base_acc:.2%}** for free — that is the floor, not a result.",
        "- Accuracy is misleading on a "
        f"{n0/len(df):.0%}/{n1/len(df):.0%} imbalance.", "",
        "## Task 2 — dummy baseline",
        "- `most_frequent` always predicts the majority class (0). At `test_size=0.2`, support is",
        f"  ~{round(n0*0.2)} (class 0) / ~{round(n1*0.2)} (class 1).",
        "- **Class-1 recall = 0.00** (the dummy never predicts it); precision 0.00. `stratify=y`",
        "  keeps the 84/16 split in both train and test.", "",
        "## Task 3 — leakage",
        f"- **`completion_pct` is the leak** (|corr| = {leak_corr:.3f} with `dropped`). A student 90%",
        "  through the course almost cannot drop — that reflects the outcome, not signal available at",
        "  prediction time. Every other feature sits well below 0.9.", "",
        "## Task 4 — metric",
        "- Optimise **recall on class 1**: missing an at-risk student costs more than a false alarm.",
        "- Lower accuracy with higher minority-class recall is the right tradeoff — the model stopped",
        "  exploiting the majority class.", "",
    ])


# ======================================================================================
# orders.csv  — "Scoping a first end-to-end project"
#   Schema from the worksheet's Task-1 inline sample. order_date stays string (Task 1b dtype point).
# ======================================================================================
ORDER_CATEGORIES = ["electronics", "clothing", "books", "home", "toys", "grocery"]
RETURN_RATE_BY_CAT = {"electronics": 0.28, "clothing": 0.22, "books": 0.06,
                      "home": 0.12, "toys": 0.15, "grocery": 0.03}


def build_orders(rng: np.random.Generator, rows: int) -> pd.DataFrame:
    start = datetime(2024, 1, 1)
    dates = [(start + timedelta(days=int(x))).strftime("%Y-%m-%d")
             for x in rng.integers(0, 90, rows)]              # ~3 months
    cat = rng.choice(ORDER_CATEGORIES, rows)
    returned = (rng.random(rows) < np.array([RETURN_RATE_BY_CAT[c] for c in cat])).astype(int)
    df = pd.DataFrame({
        "order_id": np.arange(1000, 1000 + rows),
        "customer_id": rng.integers(200, 1200, rows).astype(float),
        "order_date": dates,
        "product_category": cat,
        "order_value": rng.integers(199, 9999, rows).astype(float),
        "returned": returned,
    })
    df.loc[df.index[_pick(rng, rows, 0.05)], "customer_id"] = np.nan
    df.loc[df.index[_pick(rng, rows, 0.06)], "order_date"] = None
    df.loc[df.index[_pick(rng, rows, 0.04)], "order_value"] = np.nan
    return df


def verify_orders(df: pd.DataFrame) -> list[str]:
    checks = {
        "order_date is unparsed string (Task 1b)": not pd.api.types.is_numeric_dtype(df["order_date"])
            and not pd.api.types.is_datetime64_any_dtype(df["order_date"]),
        "customer_id has missing": df["customer_id"].isna().sum() > 0,
        "order_date has missing": df["order_date"].isna().sum() > 0,
        "order_value has missing": df["order_value"].isna().sum() > 0,
        "order_value numeric": pd.api.types.is_numeric_dtype(df["order_value"]),
        "returned is 0/1": set(df["returned"].dropna().unique()) <= {0, 1},
    }
    return [name for name, ok in checks.items() if not ok]


def key_orders(df: pd.DataFrame, meta: dict) -> str:
    miss = df.isnull().sum()
    miss = miss[miss > 0]
    rates = (df.groupby("product_category")["returned"].mean() * 100).round(1).sort_values(ascending=False)
    lines = [
        f"# orders.csv — Instructor Answer Key", "",
        _provenance(meta), "",
        "## Task 1 — audit (model answer)",
        "- **Columns with missing values:** " + ", ".join(f"`{c}` ({int(n)})" for c, n in miss.items()) + ".",
        "- **`order_date` reads back as a string** (object/str), not datetime — trend analysis over",
        "  time needs `df['order_date'] = pd.to_datetime(df['order_date'])` first (Task 1c).",
        "- Cannot answer from this data alone: anything about *why* customers returned, customer",
        "  demographics, or profit (no cost column).", "",
        "## A defensible scoped question (Task 2)",
        "*Using 3 months of orders, find which product categories have the highest return rate, so",
        "the business can prioritise quality checks.* Return rate by category:", "",
        "| Category | Return rate |", "|---|---|",
    ]
    lines += [f"| {c} | {r}% |" for c, r in rates.items()]
    lines += ["", "Validation that needs no model: the ranking should match human intuition",
              "(electronics/clothing return more than books/grocery).", ""]
    return "\n".join(lines)


# ======================================================================================
# users.csv  — "Knowing when to trust AI output"
#   The trap: naive churn (churned / all-time users) is deflated by the oversized denominator;
#   churn among users active last month is meaningfully higher.
# ======================================================================================
ACTIVE_MONTH = "2026-05"
USER_STATUSES = ["active", "churned"]


def build_users(rng: np.random.Generator, rows: int) -> pd.DataFrame:
    months = pd.period_range("2023-01", ACTIVE_MONTH, freq="M").strftime("%Y-%m").to_numpy()
    signup = rng.choice(months, rows)
    # last_active >= signup; weight toward older months so the all-time denominator is large
    last_active = np.array([
        rng.choice(months[np.searchsorted(months, s):]) for s in signup
    ])
    is_recent = last_active == ACTIVE_MONTH
    # recent-active users churn at ~25%; everyone else at ~8% → naive << active-month rate
    p_churn = np.where(is_recent, 0.25, 0.08)
    status = np.where(rng.random(rows) < p_churn, "churned", "active")
    return pd.DataFrame({
        "user_id": np.arange(50_000, 50_000 + rows),
        "signup_month": signup,
        "last_active_month": last_active,
        "status": status,
    })


def _churn_rates(df: pd.DataFrame) -> tuple[float, float]:
    naive = (df["status"] == "churned").mean()
    recent = df[df["last_active_month"] == ACTIVE_MONTH]
    active = (recent["status"] == "churned").mean() if len(recent) else 0.0
    return float(naive), float(active)


def verify_users(df: pd.DataFrame) -> list[str]:
    naive, active = _churn_rates(df)
    checks = {
        "status has churned + other": {"churned"} <= set(df["status"].unique()) and df["status"].nunique() >= 2,
        f"last_active has {ACTIVE_MONTH} + others": (df["last_active_month"] == ACTIVE_MONTH).any()
            and df["last_active_month"].nunique() >= 2,
        "trap is real & directional (naive < active-month by >0.05)": naive < active - 0.05,
    }
    return [name for name, ok in checks.items() if not ok]


def key_users(df: pd.DataFrame, meta: dict) -> str:
    naive, active = _churn_rates(df)
    n_recent = int((df["last_active_month"] == ACTIVE_MONTH).sum())
    return "\n".join([
        f"# users.csv — Instructor Answer Key", "",
        _provenance(meta), "",
        "## Task 1 — the crack in the AI's logic (model answer)",
        f"- The AI computed churn as `churned / all users ever` = **{naive:.2%}**. The denominator",
        "  includes every user who ever signed up, so the rate is meaninglessly deflated.",
        f"- Correct: churn among users *active last month* ({ACTIVE_MONTH}, {n_recent} users) =",
        f"  **{active:.2%}** — over {active/naive:.1f}× the naive figure.",
        "- **Fix:** `recent = df[df['last_active_month'] == '2026-05']; "
        "churn = (recent['status']=='churned').mean()`.",
        "- Without reading the data dictionary you'd ship the deflated number — a wrong denominator",
        "  is a logic bug that runs cleanly and produces a plausible-looking result.", "",
    ])


def _provenance(meta: dict) -> str:
    return (f"Generator `scripts/generate_course_dataset.py` · seed `{meta['seed']}` · "
            f"rows `{meta['rows']}` · generated {date.today().isoformat()}. "
            "**SYNTHETIC — fabricated, not real customer data.** Same seed → byte-identical CSV.")


# --------------------------------------------------------------------------------------
# registry + CLI
# --------------------------------------------------------------------------------------
@dataclass(frozen=True)
class DatasetSpec:
    default_rows: int
    build: Callable[[np.random.Generator, int], pd.DataFrame]
    render_key: Callable[[pd.DataFrame, dict], str]   # measures from the RE-READ frame
    verify: Callable[[pd.DataFrame], list[str]]       # binding constraints; [] == pass


DATASETS: dict[str, DatasetSpec] = {
    "loan_applications": DatasetSpec(
        3000, build_dirty,
        lambda df, m: render_answer_key(df, m["seed"], m["rows"], m["name"]), verify_loan),
    "transactions": DatasetSpec(3000, build_transactions, key_transactions, verify_transactions),
    "student_engagement": DatasetSpec(
        10000, build_student_engagement, key_student_engagement, verify_student_engagement),
    "orders": DatasetSpec(3000, build_orders, key_orders, verify_orders),
    "users": DatasetSpec(4000, build_users, key_users, verify_users),
}


def generate_one(name: str, seed: int, rows: int | None, out_dir: Path, make_clean: bool) -> None:
    spec = DATASETS[name]
    n = rows or spec.default_rows
    df = spec.build(np.random.default_rng(seed), n)

    csv_path = out_dir / f"{name}.csv"
    df.to_csv(csv_path, index=False)
    # Render the key from the RE-READ frame — that is what the student's pandas sees (text cols
    # become StringDtype, "N/A"/"" -> NaN). Measuring the in-memory frame would drift from it.
    written = pd.read_csv(csv_path)
    meta = {"seed": seed, "rows": n, "name": name}
    (out_dir / f"{name}_answer_key.md").write_text(spec.render_key(written, meta), encoding="utf-8")

    if make_clean and name == "loan_applications":
        build_clean_frame(np.random.default_rng(seed), n).to_csv(
            out_dir / f"{name}_clean.csv", index=False)
    elif make_clean:
        console.print(f"[warn]--clean ignored for {name} (only loan_applications has a clean variant)[/warn]")

    failures = spec.verify(written)
    if failures:
        sys.exit(f"[self-verify FAILED · {name}] {', '.join(failures)}")
    console.print(f"[success]✓ {name}[/success]  ({df.shape[0]}×{df.shape[1]})  → key + verify ok")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate seeded synthetic dirty course datasets.")
    parser.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    parser.add_argument("--name", default="loan_applications", choices=list(DATASETS))
    parser.add_argument("--all", action="store_true", help="generate every ds dataset")
    parser.add_argument("--rows", type=int, default=None, help="override the dataset's default")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--clean", action="store_true", help="also emit a pristine *_clean.csv (loan only)")
    args = parser.parse_args()

    if args.niche != "ds":
        sys.exit(f"--niche {args.niche} not yet supported (only 'ds' is wired).")

    names = list(DATASETS) if args.all else [args.name]
    console.rule("[info]Course Dataset Generator[/info]")
    console.print(f"Niche: [niche]{args.niche}[/niche]  datasets: {', '.join(names)}  seed: {args.seed}")

    out_dir = REPO / "content" / "courses" / NICHES[args.niche] / "datasets"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in names:
        generate_one(name, args.seed, args.rows, out_dir, args.clean)

    console.print(f"\n[success]✓ Done[/success] → {out_dir.relative_to(REPO)}")


if __name__ == "__main__":
    main()
