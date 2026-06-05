# Moving from notebooks to real team code — Worksheet

**Objective:** Take one notebook cell and turn it into reusable, tracked, team-ready code.

---

## Scenario

You've been working on a data cleaning task in Jupyter. Your manager asks you to share it with the team so anyone can run it on new data. You open the notebook and see this:

```python
import pandas as pd

df = pd.read_csv('/Users/rahul/Downloads/sales_data_final_v3.csv')
df = df.dropna(subset=['revenue'])
df['revenue'] = df['revenue'].astype(float)
df = df[df['revenue'] > 0]
df['month'] = pd.to_datetime(df['date']).dt.month
print(df.shape)
```

Right now, this only works on your laptop, for that one file, once.

---

## Task 1 — Spot the Problems (Easy)

Read the cell above. List **three specific things** that would break if a teammate tried to run this on their machine or on a different dataset.

1. ____________________________________________________________________

2. ____________________________________________________________________

3. ____________________________________________________________________

---

## Task 2 — Wrap It in a Function (Core)

Rewrite the cell as a function called `clean_sales_data`. It should:
- Accept the file path as a parameter (not hardcode it)
- Accept the minimum revenue threshold as a parameter with a default of `0`
- Return the cleaned DataFrame
- Not print anything — return data, let the caller decide what to do with it

Write your function below:

```python
def clean_sales_data(______, ______=0):
    """
    ______________________________________________________
    ______________________________________________________
    """
    
    
    
    
    return ______
```

**Check:** Call your function with a fake path to make sure Python accepts the syntax before moving on.

---

## Task 3 — Move It to a Module (Applied)

Imagine your project folder looks like this:

```
my_project/
├── notebooks/
│   └── exploration.ipynb
├── src/
│   └── data_utils.py
└── main.py
```

**3a.** Where should your `clean_sales_data` function live? Write the file path:

`______________________________________________________`

**3b.** Write the import statement you'd use inside `main.py` to call your function:

```python
______________________________________________________
```

**3c.** Why is putting the function in `src/data_utils.py` better than keeping it inside the notebook? (One sentence, in your own words.)

____________________________________________________________________

____________________________________________________________________

---

## Task 4 — Add a Docstring and Type Hints (Applied)

Go back to your function from Task 2. Add:
- A proper docstring (what it does, what parameters it takes, what it returns)
- Type hints on the parameters and return value

Rewrite the function signature and docstring only:

```python
def clean_sales_data(______: ______, ______: ______ = 0) -> ______:
    """
    ______________________________________________________
    
    Args:
        ______: ____________________________________________
        ______: ____________________________________________
    
    Returns:
        ____________________________________________
    """
```

**Why this matters:** A teammate reading your code at midnight should understand what your function expects without running it.

---

## Task 5 — Version It with Git (Applied)

You've moved the function to `src/data_utils.py`. Now track it.

**5a.** Write the three git commands (in order) to stage only this file and commit it:

```bash
# 1. Check what changed
______________________________________________________

# 2. Stage only the data utils file
______________________________________________________

# 3. Commit with a message that says what you did and why
______________________________________________________
```

**5b.** Your commit message should answer two questions: *what* changed and *why*. Write one below (50 words or less):

`______________________________________________________`

---

## Self-Check

Before you mark this done, verify each item:

| What a correct approach looks like | Done? |
|---|---|
| Function takes inputs as parameters — no hardcoded paths or values | ☐ |
| Function returns data; it does not print or save as a side effect | ☐ |
| Function lives in `src/`, not inside the notebook | ☐ |
| Docstring explains params and return value in plain language | ☐ |
| Commit message describes the change, not just "updated file" | ☐ |

---

## Reflection (Write 2–3 sentences)

Think about a notebook you've built before — a project, a college assignment, a personal experiment. What would it take to turn *that* code into something a teammate could run without asking you a single question?

____________________________________________________________________

____________________________________________________________________

____________________________________________________________________