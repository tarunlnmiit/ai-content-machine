---
title: "The Type Error That Makes Your Analysis Wrong Without Crashing"
type: script
niche: data_science_tech
date: 2026-05-25
week: 2026-W22
slug: python-for-data-science-tutorial-210
platform: yt
tags: [content/script, niche/data_science_tech, week/2026-W22]
---

```
SHOW: Breath of Data Science
EPISODE TITLE (working): The Type Error That Makes Your Analysis Wrong Without Crashing
TARGET RUNTIME: 6–7 minutes
WORD COUNT: 930
```

[ANIMATION: 5-second title card — "Python for Data Science #2: Types, Lists, Dicts, Functions"]

[BROLL: 5-second intro — terminal typing `print("28" + "35")`, output `2835` appearing on screen]

Your analysis will give you a wrong answer someday. Not an error. Not a crash. A perfectly confident wrong number.

[SCREEN: CSV file open in a text editor — an `age` column, values `28`, `35`, `42`]

Here's how it happens. Your CSV comes in with a column labeled `age`. You load it, you sum it, Python reports the sum, you move on.

```python
print("28" + "35")   # "2835"
```

Except the column was stored as strings. Python didn't add 28 and 35. It concatenated them. No error, no warning — a number plausible enough to fool you, and anyone reading your report.

This is tutorial two. It's about types — the difference between data that looks like a number and data Python treats like a number. The structures that make data science work before you ever open a library.

[SCREEN: four variable assignments — `age = 28`, `salary = 85000.50`, `name = "Alex"`, `is_outlier = False`]

Four types carry every Python data pipeline: integers, floats, strings, booleans.

```python
age = 28
print(type(age))          # <class 'int'>

salary = 85000.50
print(type(salary))       # <class 'float'>

name = "Alex"
print(type(name))         # <class 'str'>

is_outlier = False
print(type(is_outlier))   # <class 'bool'>
```

`type()` tells you what you're actually holding. And the fix for the concatenation bug is one function call away.

```python
raw_age = "28"           # came from a CSV — it's a string
age = int(raw_age)
print(age + 10)          # 38 — now it adds correctly
```

`int()`, `float()`, `str()`, `bool()` — those four conversions cover almost everything. Rule to keep for life: any data from a CSV, an API, or user input arrives as a string until you convert it.

[PAUSE]

[SCREEN: `scores = [85, 92, 78, 95, 88]` with index arrows drawn under each value]

Next structure — lists. Ordered, mutable, zero-indexed.

```python
scores = [85, 92, 78, 95, 88]
print(scores[0])    # 85
print(scores[-1])   # 88
print(scores[1:3])  # [92, 78] — index 1 and 2, NOT 3
```

That slice trips up everyone the first week. `scores[1:3]` stops before index 3 — the end is exclusive. Once that clicks, comprehensions get easy.

```python
high_scores = [s for s in scores if s > 85]
scores_as_percentages = [s / 100 for s in scores]
```

[SCREEN: comprehension breaking down left to right — "for each s in scores, if s > 85, include s / 100"]

Read it left to right: for each `s` in `scores`, if `s` is greater than 85, include it. Every data scientist writes this pattern constantly — it replaces a three-line loop with one readable expression.

[PAUSE]

Lists give you sequences. Dictionaries give you rows.

```python
person = {"name": "Alex", "age": 28, "role": "analyst"}
print(person["name"])              # "Alex"
print(person.get("email", "not set"))  # "not set"
```

Never index a dict you don't control with square brackets — a missing key crashes the whole script. `.get()` returns a default instead.

[SCREEN: a list of four dicts scrolling — `employees = [{"name": "Alex", ...}, {"name": "Jamie", ...}, ...]`]

In real work you're almost never holding one dictionary. You're holding a list of dictionaries — one dict per row.

```python
employees = [
    {"name": "Alex",  "role": "analyst",  "salary": 85000},
    {"name": "Jamie", "role": "engineer", "salary": 92000},
]

analysts = [e for e in employees if e["role"] == "analyst"]
avg = sum(e["salary"] for e in analysts) / len(analysts)
```

List of dicts, filter with a comprehension, aggregate with `sum()` and `len()` — that's exactly what Pandas does internally, at a much larger scale. Learn it here and Pandas stops being a wall of methods to memorize.

[PAUSE]

Last piece — functions. A named, reusable block of logic.

```python
def calculate_average(numbers):
    return sum(numbers) / len(numbers)

print(calculate_average(scores))    # 87.6
print(calculate_average([85000, 92000, 78000]))  # 85000.0
```

Same function, any list. And default arguments let you set a fallback you can override on demand.

```python
def is_outlier(value, mean, threshold=2.0):
    distance = abs(value - mean) / mean
    return distance > threshold / 10

outliers = [s for s in scores if is_outlier(s, mean=87.6)]
```

I hit this wall early on, building analytics scripts for content tracking. I had the same twelve-line block — clean values, calculate an average, filter rows — copy-pasted across three notebooks. Every small change meant hunting through duplicated code, hoping I hadn't missed a copy. The moment I turned that block into a function, the whole workflow changed. Fewer silent mistakes, faster iteration, code I still trusted six weeks later when I reopened the project.

[SCREEN: three-line summary card — "types encode intention · lists are sequences, dicts are records · functions make code testable"]

Four things most beginners miss: types encode intention. Lists are sequences, dicts are records. List comprehensions are concise loops. Functions make code testable. Not the libraries — these. Every pipeline you'll ever build rests on them.

Tutorial three brings NumPy — these same structures, scaled to millions of rows.

Rewrite tutorial one's average as a function. Add a filter function next to it. Reply with what you built, or the first type error you caught — and if this is useful, send it to one person still learning Python.

[ANIMATION: 5-second outro card — "Next: NumPy for Data Science (#3/10)"]
