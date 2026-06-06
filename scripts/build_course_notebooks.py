#!/usr/bin/env python3
"""Build the DS course companion Jupyter notebooks (Phase 3 of the companion-assets plan).

Two notebooks under content/courses/data_science/notebooks/:
  - data_audit_starter.ipynb        — pairs with the L2 auditing worksheet; loads the real
    ../datasets/loan_applications.csv and walks the audit, leaving TODO cells for the student.
  - notebook_to_module_refactor_kit.ipynb — mirrors the L8 "notebooks → team code" worksheet's
    clean_sales_data scenario, but SELF-CONTAINED (writes its own tiny sample CSV, no external file).

Notebooks are built with nbformat.v4 and `nbformat.validate`d before writing, so an invalid
notebook never lands on disk. No Claude call — pure structure.

Usage (always in the project conda env; needs nbformat):
  conda run -n content_engine_env python scripts/build_course_notebooks.py --niche ds --which both
"""

import argparse
import sys
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

from _console import console

REPO = Path(__file__).parent.parent
NICHES = {"ds": "data_science"}


def md(text: str) -> nbformat.NotebookNode:
    return new_markdown_cell(text.strip())


def code(text: str) -> nbformat.NotebookNode:
    return new_code_cell(text.strip())


# ======================================================================================
# data_audit_starter.ipynb  — pairs with the L2 auditing worksheet
# ======================================================================================
def build_audit_notebook() -> nbformat.NotebookNode:
    cells = [
        md("""
# Data Audit Starter — `loan_applications.csv`

Companion notebook for the lesson **Auditing Messy Real-World Data**. Work top to bottom; the
`# TODO` cells are yours to fill in. Check your numbers against `loan_applications_answer_key.md`.

> **Run this from the `notebooks/` folder** — the load path is relative (`../datasets/…`).
"""),
        code("""
import pandas as pd

df = pd.read_csv("../datasets/loan_applications.csv")
print("shape:", df.shape)
print(df.dtypes)
df.head(10)
"""),
        md("""
## Task 1 — first contact
**TODO:** one column is a number stored as text (its dtype is `str`, not a number). Which one?
Write it down — you will parse it later.
"""),
        code("""
# Task 2 — missing-value map
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
missing_report = pd.DataFrame(
    {"missing_count": missing, "missing_pct": missing_pct}
).sort_values("missing_pct", ascending=False)
print(missing_report[missing_report["missing_count"] > 0])
"""),
        code("""
# TODO (Task 2c) — is the missingness random, or does it cluster?
# Hint: cibil_score may be missing far more often for one employment type.
#   df.groupby("employment_type")["cibil_score"].apply(lambda s: s.isna().mean())
"""),
        code("""
# TODO — the dtype trap: monthly_emi looks numeric but is text.
#   print(df["monthly_emi"].dtype)
#   pd.to_numeric(df["monthly_emi"], errors="coerce")  # which values refuse to parse?
"""),
        code("""
# Task 3 — value sanity checks (runs as-is because the amount columns are numeric)
print("Age range:", df["age"].min(), "to", df["age"].max())
print("Negative ages:", (df["age"] < 0).sum())
print("Ages above 100:", (df["age"] > 100).sum())
print("Income negatives:", (df["annual_income"] < 0).sum())
print("Income zeros:", (df["annual_income"] == 0).sum())
df["loan_to_income"] = df["loan_amount"] / df["annual_income"]
print("Loan-to-income > 50:", (df["loan_to_income"] > 50).sum())
"""),
        code("""
# TODO (Task 3c) — duplicates
#   df["application_id"].duplicated().sum()   # repeated IDs
#   df.duplicated().sum()                      # fully repeated rows
"""),
        md("""
## The timestamp trap
`event_timestamp` was stitched together from three systems (IST, UTC, and a US `mm/dd/yyyy`
source). One column, three realities. The cell below shows how many values a naive parse drops.
"""),
        code("""
parsed = pd.to_datetime(df["event_timestamp"], errors="coerce")
print("rows a naive parse turns into NaT:", parsed.isna().sum())
print(df["event_timestamp"].head(8).tolist())
"""),
        code("""
# Task 4 — categorical mess
for col in df.select_dtypes(include="object").columns:
    print(f"\\n--- {col} ---")
    print(df[col].value_counts(dropna=False).head(10))
"""),
        code("""
# TODO (Task 4b) — write clean_column() to standardise employment_type:
#   .str.strip().str.lower() + a replacement map for the variants, then reapply to the column.
"""),
        md("""
## Close it out
Write the **Data Quality Report** (worksheet Task 5): total rows, the 3 most critical issues
(name the column, the size, the risk to a loan model), and a usable / not-usable verdict. Then
open `loan_applications_answer_key.md` and compare.
"""),
    ]
    nb = new_notebook(cells=cells)
    nb.metadata.update({"language_info": {"name": "python"},
                        "kernelspec": {"name": "python3", "display_name": "Python 3"}})
    return nb


# ======================================================================================
# notebook_to_module_refactor_kit.ipynb  — mirrors the L8 worksheet, self-contained
# ======================================================================================
def build_refactor_notebook() -> nbformat.NotebookNode:
    cells = [
        md("""
# Notebook → Module Refactor Kit

Companion for **Moving from notebooks to real team code**. Self-contained — it writes its own tiny
sample file, so it runs anywhere with no setup. Goal: turn one throwaway notebook cell into
reusable, tracked, team-ready code.
"""),
        md("""
## BEFORE — the cell your manager just saw

```python
import pandas as pd

df = pd.read_csv('/Users/rahul/Downloads/sales_data_final_v3.csv')
df = df.dropna(subset=['revenue'])
df['revenue'] = df['revenue'].astype(float)
df = df[df['revenue'] > 0]
df['month'] = pd.to_datetime(df['date']).dt.month
print(df.shape)
```

**Three things that break for a teammate (Task 1):** hardcoded laptop-only path · no function, so
nobody can reuse it · prints a side effect instead of returning data · the `> 0` threshold is
baked in. (Not run here — that path only exists on Rahul's machine.)
"""),
        code("""
# Setup — write a tiny messy sample so the refactored function has something to read.
import pandas as pd
from pathlib import Path

Path("sample_sales.csv").write_text(
    "date,revenue,region\\n"
    "2024-01-05,1200,North\\n"
    "2024-01-06,,South\\n"      # missing revenue
    "2024-01-07,-50,East\\n"    # invalid revenue
    "2024-01-08,900,West\\n"
    "2024-02-01,1500,North\\n",
    encoding="utf-8",
)
print("wrote sample_sales.csv")
"""),
        code('''
# AFTER — Tasks 2 + 4: a parameterised function with a docstring and type hints.
def clean_sales_data(path: str, min_revenue: float = 0) -> pd.DataFrame:
    """Load raw sales data and return a cleaned frame.

    Args:
        path: path to the sales CSV.
        min_revenue: drop rows at or below this revenue (default 0).

    Returns:
        A cleaned DataFrame with a numeric `revenue` and an added `month` column.
    """
    df = pd.read_csv(path)
    df = df.dropna(subset=["revenue"])
    df["revenue"] = df["revenue"].astype(float)
    df = df[df["revenue"] > min_revenue]
    df["month"] = pd.to_datetime(df["date"]).dt.month
    return df


clean_sales_data("sample_sales.csv")
'''),
        code('''
# A tiny test — no pytest needed. Run it; if nothing prints an error, you are good.
out = clean_sales_data("sample_sales.csv")
assert "month" in out.columns
assert (out["revenue"] > 0).all()           # no zero / negative revenue survived
assert out["revenue"].dtype == float
print("All checks passed:", len(out), "clean rows")
'''),
        md("""
## Task 3 + 5 — move it to a module, then track it

```
my_project/
├── notebooks/
│   └── exploration.ipynb
├── src/
│   └── data_utils.py      ← clean_sales_data lives HERE, not in the notebook
└── main.py
```

Import it from `main.py`:

```python
from src.data_utils import clean_sales_data
```

Version it (three commands, in order):

```bash
git status
git add src/data_utils.py
git commit -m "Add clean_sales_data: reusable sales cleaning for the team"
```

**Do this now:** paste your function into `src/data_utils.py`, import it once, and make that commit.
A teammate should be able to run it on a new file without asking you a single question.
"""),
    ]
    nb = new_notebook(cells=cells)
    nb.metadata.update({"language_info": {"name": "python"},
                        "kernelspec": {"name": "python3", "display_name": "Python 3"}})
    return nb


BUILDERS = {"audit": ("data_audit_starter", build_audit_notebook),
            "refactor": ("notebook_to_module_refactor_kit", build_refactor_notebook)}


def write_nb(nb: nbformat.NotebookNode, path: Path) -> None:
    nbformat.validate(nb)  # fail before writing — never land an invalid notebook
    nbformat.write(nb, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build DS course companion notebooks.")
    parser.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    parser.add_argument("--which", choices=["audit", "refactor", "both"], default="both")
    args = parser.parse_args()

    if args.niche != "ds":
        sys.exit(f"--niche {args.niche} not yet supported (only 'ds' has notebooks).")

    console.rule("[info]Course Notebook Builder[/info]")
    out_dir = REPO / "content" / "courses" / NICHES[args.niche] / "notebooks"
    out_dir.mkdir(parents=True, exist_ok=True)

    names = list(BUILDERS) if args.which == "both" else [args.which]
    for key in names:
        fname, builder = BUILDERS[key]
        path = out_dir / f"{fname}.ipynb"
        write_nb(builder(), path)
        console.print(f"[success]✓ {fname}.ipynb[/success]  → validated + written")

    console.print(f"\n[success]✓ Done[/success] → {out_dir.relative_to(REPO)}")


if __name__ == "__main__":
    main()
