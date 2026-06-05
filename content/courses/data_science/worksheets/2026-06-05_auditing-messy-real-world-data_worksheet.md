# Auditing Messy Real-World Data — Worksheet

**Objective:** Audit a messy dataset end-to-end and produce a written failure-mode report you could hand to a teammate.

---

## Scenario

You've just joined a fintech startup as a junior data analyst. Your first task: a CSV file called `loan_applications.csv` landed in your inbox with a note — *"Use this to build the approval model. Should be clean, we exported it from our CRM."*

It is not clean. Your job is to find out exactly how broken it is before anyone touches it for modelling.

---

## Task 1 — First Contact (Easy)

Load the dataset and get a feel for its shape. Run the code below, then answer the questions in your own words.

```python
import pandas as pd

df = pd.read_csv("loan_applications.csv")

print(df.shape)
print(df.dtypes)
print(df.head(10))
```

**Q1a.** How many rows and columns does the dataset have?

```
Rows: ________    Columns: ________
```

**Q1b.** Without any cleaning, what is your first gut reaction to the data? Write 2–3 sentences describing what looks off just from `.head()`.

```
____________________________________________________________

____________________________________________________________

____________________________________________________________
```

**Q1c.** List any columns whose dtype surprises you (e.g., a number stored as `object`):

```
Column name             Expected dtype         Actual dtype
__________________      __________________     __________________
__________________      __________________     __________________
__________________      __________________     __________________
```

---

## Task 2 — Missing Value Map (Easy → Medium)

Run this audit block:

```python
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)

missing_report = pd.DataFrame({
    "missing_count": missing,
    "missing_pct": missing_pct
}).sort_values("missing_pct", ascending=False)

print(missing_report[missing_report["missing_count"] > 0])
```

**Q2a.** List the top 3 columns by missing percentage:

```
1. ________________________  →  _______ %
2. ________________________  →  _______ %
3. ________________________  →  _______ %
```

**Q2b.** For each of those 3 columns, write one sentence explaining *why* that missing data is dangerous for a loan approval model specifically (not just "it reduces data quality"):

```
Column 1: ___________________________________________________

Column 2: ___________________________________________________

Column 3: ___________________________________________________
```

**Q2c.** Is the missingness random or does it cluster in certain rows? Write the code you'd use to check this, then describe what you found:

```python
# Your code here




```

Findings:
```
____________________________________________________________
____________________________________________________________
```

---

## Task 3 — Value Sanity Checks (Medium)

Real dirty data hides problems inside valid-looking cells. Check these:

```python
# Age column
print("Age range:", df["age"].min(), "to", df["age"].max())
print("Negative ages:", (df["age"] < 0).sum())
print("Ages above 100:", (df["age"] > 100).sum())

# Income column
print("\nIncome negatives:", (df["annual_income"] < 0).sum())
print("Income zeros:", (df["annual_income"] == 0).sum())

# Loan amount vs income ratio
df["loan_to_income"] = df["loan_amount"] / df["annual_income"]
print("\nLoan-to-income > 50:", (df["loan_to_income"] > 50).sum())
```

**Q3a.** Fill in what you found:

```
Impossible age values found:        ________
Negative or zero income rows:       ________
Extreme loan-to-income ratios:      ________
```

**Q3b.** Pick one impossible or extreme value you found. Write a 2-sentence explanation of how it could have gotten into the data (think: data entry, system migration, form validation failure):

```
____________________________________________________________

____________________________________________________________
```

**Q3c.** Now write code to find any duplicate application IDs (if an `application_id` column exists) or duplicate rows:

```python
# Your code here




```

Duplicates found: ________

---

## Task 4 — Categorical Mess (Medium → Applied)

Categorical columns in messy data are rarely consistent. Run this:

```python
for col in df.select_dtypes(include="object").columns:
    print(f"\n--- {col} ---")
    print(df[col].value_counts(dropna=False).head(15))
```

**Q4a.** Pick any 2 categorical columns that show inconsistencies (different spellings, mixed case, rogue spaces, unknown codes). List the messy values you see:

```
Column 1: ________________________
  Problem values:
  - ____________________________
  - ____________________________
  - ____________________________

Column 2: ________________________
  Problem values:
  - ____________________________
  - ____________________________
  - ____________________________
```

**Q4b.** Write a cleaning function for ONE of those columns that standardises it. Use `.str.strip()`, `.str.lower()`, and a replacement map:

```python
def clean_column(series):
    # Step 1: strip whitespace and lowercase
    

    # Step 2: map known variants to canonical values
    replacements = {
        
    }
    
    return series.map(replacements).fillna(series)

df["your_column"] = clean_column(df["your_column"])
```

---

## Task 5 — Failure Mode Report (Applied)

You've done the audit. Now document it like a professional.

Write a short **Data Quality Report** (plain text, no code) covering:

- Total rows audited
- 3 most critical issues found (be specific: column name, size of problem, risk to the model)
- Your recommendation: is this dataset usable as-is, or does it need fixes before modelling begins?

```
DATA QUALITY REPORT
Dataset: loan_applications.csv
Audited by: ____________________   Date: ____________

Total rows: ________   Total columns: ________

Critical Issue 1:
________________________________________________________________
________________________________________________________________

Critical Issue 2:
________________________________________________________________
________________________________________________________________

Critical Issue 3:
________________________________________________________________
________________________________________________________________

Recommendation:
________________________________________________________________
________________________________________________________________
________________________________________________________________
```

---

## Self-Check

Review your work against these markers before submitting:

| Check | What a correct approach looks like |
|---|---|
| Task 1 | dtypes inspected, surprises listed with specific column names |
| Task 2 | Missing pct computed per column; explanation tied to loan approval risk, not generic |
| Task 3 | At least one impossible value found *and* a plausible origin story written |
| Task 4 | Cleaning function handles both whitespace AND value variants; not just lowercasing |
| Task 5 | Report names specific columns, not vague categories; recommendation is a clear yes/no/conditional |

**Reflection — one sentence each:**

What surprised you most about the dataset?
```
____________________________________________________________
```

What would you do differently if you had to audit a 10-million-row version of this file?
```
____________________________________________________________

____________________________________________________________
```