# Python for Data Science: Tutorial 4/10 — Pandas for Data Analysis

## HOOK

The first real dataset I ever worked with professionally was a mess.

Not academic-mess — real mess. Column names with trailing spaces. Dates formatted three different ways in the same column. Rows where someone had typed "N/A," "na," "None," and a literal dash as four separate attempts at missing data. Revenue figures mixed with strings like "approx 50k."

I spent two weeks on that dataset before I ran a single analysis. Two weeks of writing Python loops that felt like archaeology — chipping away at the rock, never sure if you'd found the actual data or just another layer of sediment.

Then I learned Pandas properly. Not just `pd.read_csv()` and `df.head()` — the actual mental model: a DataFrame is a structured, labeled, query-able object that makes data interrogation feel like conversation instead of combat.

`![data analyst working at computer with spreadsheet and python code on dual monitors](/content/blogs/2026-W24/2026-06-10_data_science_tech_python-for-data-science-tutorial-4-pandas-for-data-analysis_images/01_hook_data-analyst-working-at-computer-with-spreadsheet.jpg)
*data analyst working at computer with spreadsheet and python code on dual monitors — Photo by [Julio Lopez](https://www.pexels.com/photo/hacker-coding-on-multiple-monitors-at-night-34258667/) on Pexels*`

---

## CONTEXT

Tutorial 3 taught you NumPy: how to think in arrays, how vectorized operations work, why the underlying C code makes Python competitive with compiled languages. Pandas is built directly on top of that foundation — its `Series` and `DataFrame` objects are NumPy arrays with labels, structure, and a library of operations designed for real-world, messy, human-generated data.

The relationship matters. When you understand that a DataFrame column is a NumPy array with a name, operations like `.apply()` and boolean indexing feel inevitable rather than magical. You're not learning new concepts — you're learning a higher-level interface for the same ideas.

Pandas is the most-used library in data science. Not because it's the flashiest — it's not — but because every data science project starts with data that isn't ready. Data that has gaps, inconsistencies, wrong types, and structures that don't match what your analysis needs. Pandas bridges the gap between raw data and something you can reason about.

This tutorial covers four things: loading and exploring, selecting and filtering, cleaning messy data, and aggregating. By the end, you'll be able to take an unfamiliar dataset and turn it into something workable in under an hour.

---

## SECTION 1 — Loading and Exploring: Your First 60 Seconds with Any Dataset

**The first question isn't "what's in this data?" It's "what shape is this data?"**

Before you analyze anything, you need to orient yourself. What are the columns? How many rows? What types are stored where? Are there obvious nulls? Pandas gives you a small set of functions that answer all of this in sequence.

```python
import pandas as pd
import numpy as np

# Load data — CSV is most common, but Pandas reads Excel, JSON, SQL, Parquet, and more
df = pd.read_csv('sales_records.csv')

# Shape: rows, columns
print(df.shape)  # e.g., (15420, 12)

# Column names and data types in one call
print(df.dtypes)

# First five rows — always run this first
print(df.head())

# Statistical summary for numeric columns
print(df.describe())

# Critical: how many nulls per column?
print(df.isnull().sum())
```

Run `df.describe()` and you're looking at count, mean, standard deviation, min, and the 25/50/75 percentiles for every numeric column. In 30 seconds you know: are there negative values in a column that should be positive? Is the max suspiciously high (outlier)? Is the mean far from the median (skew)?

The `isnull().sum()` line is the one most beginners skip. Don't skip it. Missing data in a column you use for filtering will silently break your analysis — rows disappear without warning. Know where your nulls are before you start.

`[PERSONAL_INSERT: story about a time missing data created a silent bug in an analysis — wrong conclusion reached because nulls excluded a specific demographic or time period]`

`![close up of python pandas dataframe displayed in jupyter notebook on laptop screen](/content/blogs/2026-W24/2026-06-10_data_science_tech_python-for-data-science-tutorial-4-pandas-for-data-analysis_images/02_section1_close-up-of-python-pandas-dataframe-displayed-in-j.jpg)
*close up of python pandas dataframe displayed in jupyter notebook on laptop screen — Photo by [Mathews Jumba](https://www.pexels.com/photo/black-screen-of-a-monitor-5242012/) on Pexels*`

---

## SECTION 2 — Selecting, Filtering, and Slicing: Asking Questions of Your Data

**A DataFrame is a database. `.loc` and `.iloc` are your query language.**

Selecting the right rows and columns is 60% of what you do in Pandas. There are three mechanisms, and knowing when to use each one saves constant confusion.

```python
# Select a single column — returns a Series
revenue = df['revenue']

# Select multiple columns — returns a DataFrame
subset = df[['customer_id', 'revenue', 'region']]

# .loc: label-based — use column names and row index labels
# Select rows where revenue > 10000, keep only two columns
high_value = df.loc[df['revenue'] > 10000, ['customer_id', 'revenue']]

# .iloc: position-based — use integer positions
# First 100 rows, first 4 columns
sample = df.iloc[:100, :4]

# Boolean filtering with multiple conditions
# Note: use & (not 'and'), | (not 'or'), wrap each condition in parentheses
filtered = df[(df['region'] == 'North') & (df['revenue'] > 5000)]

# .query() — cleaner syntax for complex filters
filtered_v2 = df.query("region == 'North' and revenue > 5000")
```

The common mistake is using Python's `and`/`or` keywords inside boolean filters — they don't work on arrays. Use `&` and `|` with parentheses around each condition. This trips up everyone once; now it won't trip you up at all.

`.query()` is underused. For multi-condition filters, it's dramatically more readable than stacked boolean expressions. When your filter has three or more conditions, switch to `.query()`.

One more: `.isin()` for membership tests. Instead of `(df['status'] == 'active') | (df['status'] == 'trial')`, write `df[df['status'].isin(['active', 'trial'])]`. Cleaner, scales to any list length.

---

## SECTION 3 — Cleaning Messy Data: The Work Nobody Talks About

**Data cleaning is not preparation for analysis. It *is* analysis. You can't separate the two.**

Real datasets have at least three of these problems: wrong types, inconsistent strings, unexpected nulls, duplicates, and values that are technically present but semantically wrong (a birthdate of 1900-01-01, a negative product ID). Pandas has direct tools for all of them.

```python
# Fix types — the most common silent problem
df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')

# Standardize string columns — strip whitespace, normalize case
df['region'] = df['region'].str.strip().str.title()

# Handle nulls — three strategies depending on context
df_dropped = df.dropna(subset=['customer_id'])           # Drop rows where key column is null
df_filled = df.fillna({'revenue': 0, 'notes': 'none'})   # Fill with sensible defaults
df['age'] = df['age'].fillna(df['age'].median())          # Fill with statistical estimate

# Remove duplicates — by key columns
df_deduped = df.drop_duplicates(subset=['order_id'], keep='first')

# Rename columns — especially when source has spaces or inconsistent casing
df = df.rename(columns={
    'Customer ID ': 'customer_id',
    'Rev (USD)': 'revenue_usd'
})
```

The `errors='coerce'` argument does critical work: instead of crashing when a value can't be converted, it silently turns it into `NaN`. This preserves row structure while flagging the bad values, which you can then handle intentionally.

After cleaning, always run `df.isnull().sum()` and `df.dtypes` again. A cleaning step that created new nulls instead of removing them is still a bug.

`[PERSONAL_INSERT: example of a string column that looked numeric — pd.to_numeric revealed it had commas as thousands separators, causing the entire column to silently become nulls]`

---

## SECTION 4 — GroupBy and Aggregation: Where Insights Actually Live

**The raw data doesn't tell you anything. Summaries do.**

No Pandas operation produces more insight per line of code than `.groupby()`. The pattern: split the data into groups based on one or more columns, apply an aggregation function to each group, combine the results into a new DataFrame.

```python
# Basic groupby — total revenue per region
revenue_by_region = df.groupby('region')['revenue'].sum()

# Multiple aggregations at once using .agg()
region_summary = df.groupby('region').agg(
    total_revenue=('revenue', 'sum'),
    avg_order_value=('revenue', 'mean'),
    order_count=('order_id', 'count'),
    top_customer_revenue=('revenue', 'max')
).reset_index()

# Group by multiple columns
monthly_by_region = df.groupby(['region', 'month'])['revenue'].sum().reset_index()

# Pivot table — same idea, spreadsheet-style output
pivot = df.pivot_table(
    values='revenue',
    index='region',
    columns='month',
    aggfunc='sum',
    fill_value=0
)
```

The `.agg()` syntax with named aggregations — `total_revenue=('revenue', 'sum')` — is the pattern to commit to memory. Clean column names, readable code, multiple metrics in one pass.

`reset_index()` converts the grouped result back into a regular flat DataFrame. A grouped DataFrame with a MultiIndex is harder to work with than a flat one — always reset.

The pivot table is your bridge to the stakeholder conversation. Grouped DataFrames are for computation; pivot tables are for communication. When someone asks "show me revenue by region and by month," `.pivot_table()` produces exactly the grid they're picturing.

`[PERSONAL_INSERT: example of a groupby finding an unexpected pattern — a region or segment generating disproportionate revenue that was invisible in the raw data]`

`![python data analysis results showing grouped bar chart with regional sales data](/content/blogs/2026-W24/2026-06-10_data_science_tech_python-for-data-science-tutorial-4-pandas-for-data-analysis_images/03_section4_python-data-analysis-results-showing-grouped-bar-c.jpg)
*python data analysis results showing grouped bar chart with regional sales data — Photo by [RDNE Stock project](https://www.pexels.com/photo/white-blue-and-black-paper-7947849/) on Pexels*`

---

## TAKEAWAY

Pandas doesn't replace thinking. It removes the mechanical friction that gets between you and thinking.

Before I understood it properly, I spent enormous energy on the logistics of data — how to get to row 400, how to rename a column without losing the rest. Those aren't data science problems. They're plumbing problems. And plumbing problems eat time that should go toward the actual question: what's happening in this data, and why?

The four skills in this tutorial — exploring, selecting, cleaning, aggregating — are the foundation of every analysis you'll ever do. Not the whole foundation. But the part you touch first and return to constantly.

Tutorial 5 picks up from here: once your data is clean and aggregated, the next job is making it visible. But the plots are only as honest as the data feeding them. Get Pandas right first, and visualization becomes translation — turning what you've already understood into something others can see.

---

## CTA

The cleanest next step: open a dataset you've been avoiding and run through the four sections in order. Explore it, select what matters, clean what's broken, aggregate into a summary that tells you something.

Then share what you find — or share this tutorial with someone stuck on a messy CSV. The Python for Data Science series runs ten tutorials end-to-end; Tutorial 5 (visualization) is the natural next read.

Follow me on Medium or subscribe to [Breath of Data Science](https://breathofdatascience.substack.com) for weekly tutorials grounded in real data work, not textbook examples.

---

## Post-Writing Notes

**`[PERSONAL_INSERT]` guidance:**
1. *Section 1* — Nulls creating a silent analysis bug. E.g.: "retention looked 78% but was actually 61% because nulls in `signup_date` excluded mobile users entirely."
2. *Section 3* — Revenue column with comma-formatted thousands (`1,200`) causing `pd.to_numeric(errors='coerce')` to turn the whole column into NaN. Common real-world trap.
3. *Section 4* — A groupby revealing a hidden outlier region/segment — one geography driving 40% of revenue while averaging looked uniform.

**Suggested titles:**
1. Python for Data Science Tutorial 4: Pandas for Data Analysis (the Complete Practical Guide)
2. Pandas in 4 Essential Skills: Load, Filter, Clean, Aggregate
3. The Pandas Mental Model That Changed How I Work with Data

**Derivative angle:**
Thread: "6 Pandas operations every data scientist actually uses daily" — pull `.agg()`, `.query()`, `isnull().sum()`, `pd.to_numeric(errors='coerce')`, `.drop_duplicates()`, `.pivot_table()` with one-sentence explanations each.