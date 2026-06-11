```
SHOW: Breath of Data Science
EPISODE TITLE (working): Pandas in 4 Essential Skills: Load, Filter, Clean, Aggregate
TARGET RUNTIME: 7 minutes
WORD COUNT: 940
```

---

[ANIMATION: 5-second title card — "Python for Data Science Tutorial 4: Pandas for Data Analysis"]

[BROLL: 5-second intro — screen recording fade-in, terminal blinking cursor on dark IDE background]

The first real dataset I ever worked with professionally was a mess. Not academic-mess — real mess. Column names with trailing spaces. Dates formatted three different ways in the same column. Rows where someone had typed "N/A," "na," "None," and a literal dash as four separate attempts at missing data. Revenue figures mixed with strings like "approx 50k."

I spent two weeks on that dataset before I ran a single analysis. Two weeks of Python loops that felt like archaeology — chipping away, never sure if you'd found the actual data or just another layer of sediment.

Then I learned Pandas properly. Not just `pd.read_csv()` and `df.head()` — the actual mental model: a DataFrame is a structured, labeled, query-able object that makes data interrogation feel like conversation instead of combat.

[SCREEN: empty Jupyter notebook, imports typed out]

Today I'm covering four things: loading and exploring, selecting and filtering, cleaning messy data, and aggregating. By the end, you'll be able to take an unfamiliar dataset and make it workable in under an hour.

Before we start — if you caught Tutorial 3 on NumPy, this is the natural next step. Pandas builds directly on NumPy. A DataFrame column is a NumPy array with a name. Once you see that, operations like `.apply()` and boolean indexing stop feeling magical. You're not learning new concepts, you're using a higher-level interface for the same ideas.

[SCREEN: sales_records.csv open in file explorer, then switching to notebook]

The first question with any dataset isn't "what's in this data?" It's "what *shape* is this data?" Before you analyze anything, you orient yourself. What are the columns? How many rows? What types are stored where?

```python
import pandas as pd
import numpy as np

df = pd.read_csv('sales_records.csv')

print(df.shape)       # e.g., (15420, 12)
print(df.dtypes)
print(df.head())
print(df.describe())
print(df.isnull().sum())
```

Run `df.describe()` and in thirty seconds you know whether there are negative values in a column that should be positive, whether the max is suspiciously high, whether the mean is far from the median. That's your first signal before you've written a single line of actual analysis.

The `isnull().sum()` line is the one most beginners skip. Don't skip it. [PAUSE] Missing data in a column you use for filtering will silently break your analysis — rows just disappear without warning. [PERSONAL_INSERT: story about a time missing data created a silent bug in an analysis — wrong conclusion reached because nulls excluded a specific demographic or time period]

[SCREEN: terminal output showing isnull().sum() with highlighted non-zero columns]

Now, selecting the right rows and columns. This is sixty percent of what you actually do in Pandas.

```python
revenue = df['revenue']
subset = df[['customer_id', 'revenue', 'region']]

high_value = df.loc[df['revenue'] > 10000, ['customer_id', 'revenue']]
sample = df.iloc[:100, :4]

filtered = df[(df['region'] == 'North') & (df['revenue'] > 5000)]
filtered_v2 = df.query("region == 'North' and revenue > 5000")

df[df['status'].isin(['active', 'trial'])]
```

[ANIMATION: 3-second lower third — "Use .query() for 3+ conditions"]

Two things here. First: use `&` and `|` for boolean filters, not Python's `and` and `or` — those don't work on arrays. Wrap each condition in parentheses. This trips up everyone once; now it won't trip you up.

Second: `.query()` is underused. For multi-condition filters it's dramatically more readable than stacked boolean expressions. And `.isin()` — instead of three `==` conditions joined with `|`, just pass a list. Cleaner and scales to any list length.

[SCREEN: filtered DataFrame output showing fewer rows]

Data cleaning is where most tutorials lose the thread, because it feels like janitor work. It's not. Cleaning *is* analysis. You can't separate them.

```python
df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')

df['region'] = df['region'].str.strip().str.title()

df_dropped = df.dropna(subset=['customer_id'])
df_filled = df.fillna({'revenue': 0, 'notes': 'none'})
df['age'] = df['age'].fillna(df['age'].median())

df_deduped = df.drop_duplicates(subset=['order_id'], keep='first')

df = df.rename(columns={
    'Customer ID ': 'customer_id',
    'Rev (USD)': 'revenue_usd'
})
```

The `errors='coerce'` argument is doing critical work here. Instead of crashing when a value can't be converted, it turns it into `NaN` and keeps moving. This preserves your row structure while flagging the bad values — you handle them intentionally instead of getting a runtime error at 2am. [PAUSE]

[PERSONAL_INSERT: example of a string column that looked numeric — pd.to_numeric revealed it had commas as thousands separators, causing the entire column to silently become nulls]

After cleaning: run `df.isnull().sum()` and `df.dtypes` again. A cleaning step that created new nulls instead of removing them is still a bug.

[SCREEN: before/after df.dtypes output, clean column names visible]

Now the part where actual insights live: groupby and aggregation.

```python
revenue_by_region = df.groupby('region')['revenue'].sum()

region_summary = df.groupby('region').agg(
    total_revenue=('revenue', 'sum'),
    avg_order_value=('revenue', 'mean'),
    order_count=('order_id', 'count'),
    top_customer_revenue=('revenue', 'max')
).reset_index()

monthly_by_region = df.groupby(['region', 'month'])['revenue'].sum().reset_index()

pivot = df.pivot_table(
    values='revenue',
    index='region',
    columns='month',
    aggfunc='sum',
    fill_value=0
)
```

The `.agg()` pattern with named aggregations — `total_revenue=('revenue', 'sum')` — commit that to memory. Clean output column names, multiple metrics in one pass, no postprocessing. Always call `.reset_index()` after groupby — a MultiIndex grouped result is harder to work with than a flat DataFrame.

And pivot tables: grouped DataFrames are for computation, pivot tables are for communication. When someone asks "show me revenue by region and by month," `.pivot_table()` produces the exact grid they're already picturing.

[PERSONAL_INSERT: example of a groupby finding an unexpected pattern — a region or segment generating disproportionate revenue that was invisible in the raw data]

[SCREEN: pivot table output with regions as rows, months as columns, revenue values]

Pandas doesn't replace thinking. It removes the mechanical friction that gets between you and thinking. Before I understood it properly, I spent enormous energy on logistics — how to get to row 400, how to rename a column without losing the rest. Those aren't data science problems. They're plumbing problems. And plumbing problems eat the time that should go toward the actual question.

Tutorial 5 picks up from here. Once your data is clean and aggregated, the next job is making it visible — matplotlib and seaborn. But the plots are only as honest as the data feeding them. Get Pandas right first, and visualization becomes translation.

The cleanest next step: open a dataset you've been avoiding. Run through these four sections in order. Explore it, select what matters, clean what's broken, aggregate into a summary that tells you something. Links to the full series are in the description.

[ANIMATION: 5-second outro card — "Next: Tutorial 5 — Data Visualization with Matplotlib & Seaborn"]