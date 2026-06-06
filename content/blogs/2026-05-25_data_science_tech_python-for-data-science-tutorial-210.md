The file that's there is Tutorial 1. Tutorial 2 is what you pasted — it's the content to humanize. Applying the pass now.

---

# Python for Data Science: Tutorial 2/10 — Variables, Data Types, and the Structures That Actually Matter

## HOOK

Your analysis will give you a wrong answer someday. Not an error. Not a crash. A perfectly confident wrong number.

Here's how it happens: your CSV comes in with a column labeled `age`. You load it. You sum it. Python reports the sum. You move on. Except the column was stored as strings. Python didn't add 28 + 35 + 42. It concatenated them: `"28"` + `"35"` + `"42"` = `"283542"`. No error. No warning. A number plausible enough to fool you — and anyone reading your report.

Tutorial 2 is about types. The difference between data that *looks* like a number and data Python *treats* like a number. The structures that make data science work before you ever touch a library.

Every silent bug in data analysis traces back to the same root: the programmer didn't understand what kind of thing they were holding.

`![Python code on laptop screen with data types highlighted](/content/blogs/2026-05-25_data_science_tech_python-for-data-science-tutorial-210_images/01_context_python-code-on-laptop-screen-with-data-types-highl.jpg)
*Python code on laptop screen with data types highlighted — Photo by [Nemuel Sereti](https://www.pexels.com/photo/programming-code-on-screen-6424584/) on Pexels*`

## CONTEXT

In Tutorial 1, you built your first script. You used a list of dictionaries, looped through them, calculated an average, and saved the result. You used several data types without naming them: integers (`28`), strings (`"data science"`), floats (the average), and a boolean somewhere in the background.

Python is dynamically typed. That means you don't declare types — you assign values, and Python figures out what each one is. This feels like a feature. And it is, until it isn't.

For beginners, dynamic typing hides bugs. For data scientists, it hides *expensive* bugs — the kind that only surface when someone questions your numbers, or when you run the analysis six months later with slightly different data and the answer shifts in ways you can't explain.

Here's the mental model: what types Python uses, how they behave differently, how to check and convert them, and which structures — lists, dicts, and functions — you'll use in every data pipeline you ever build.

---

## SECTION 1 — The Four Primitives: What Python Actually Holds

**When you assign `x = 42`, Python is making a claim about what that number is for.**

Four types form the foundation of every Python data pipeline:

```python
# Integers — whole numbers
age = 28
year = 2024
print(type(age))   # <class 'int'>

# Floats — decimal numbers
salary = 85000.50
accuracy = 0.94
print(type(salary))  # <class 'float'>

# Strings — text
name = "Alex"
role = "data scientist"
print(type(name))  # <class 'str'>

# Booleans — true or false
is_outlier = False
has_missing = True
print(type(is_outlier))  # <class 'bool'>
```

Here's the silent bug that bites every beginner:

```python
# Adding integers — works as expected
print(28 + 35)      # 63

# Adding floats — also fine
print(28.0 + 35.0)  # 63.0

# Adding strings — this is NOT addition
print("28" + "35")  # "2835"
```

Python didn't add those numbers. It concatenated the text. No error. No warning. Wrong answer.

Check what you're holding with `type()`, then convert explicitly:

```python
raw_age = "28"       # came from a CSV — it's a string
print(type(raw_age)) # <class 'str'>

age = int(raw_age)   # convert to integer
print(age + 10)      # 38 — now it adds correctly

# The four conversion functions
int("42")         # → 42
float("42.5")     # → 42.5
str(42)           # → "42"
bool(0)           # → False  (0, "", [], None → False; everything else → True)
```

Rule: any data from a CSV, API, or user input arrives as a string until you convert it.

---

## SECTION 2 — Lists: The Workhorse of Sequences

A list is an ordered, mutable sequence. Create with square brackets:

```python
scores = [85, 92, 78, 95, 88]

# Indexing — zero-based
print(scores[0])   # 85 (first item)
print(scores[-1])  # 88 (last item)

# Slicing — exclusive end
print(scores[1:3]) # [92, 78] — index 1 and 2, NOT 3
print(scores[:3])  # [85, 92, 78] — first three
print(scores[2:])  # [78, 95, 88] — from index 2 to end
```

The exclusive end trips up everyone the first week. `scores[1:3]` gives you positions 1 and 2, not 3.

```python
# Add an item
scores.append(91)
print(scores)  # [85, 92, 78, 95, 88, 91]

# List comprehension — filter in one line
high_scores = [s for s in scores if s > 85]
print(high_scores)  # [92, 95, 88, 91]

# List comprehension — transform in one line
scores_as_percentages = [s / 100 for s in scores]
print(scores_as_percentages)  # [0.85, 0.92, 0.78, 0.95, 0.88, 0.91]

# Both at once — filter then transform
high_as_pct = [s / 100 for s in scores if s > 85]
print(high_as_pct)  # [0.92, 0.95, 0.88, 0.91]
```

Read comprehensions left to right: "for each `s` in `scores`, if `s > 85`, include `s / 100`." Every data scientist uses this pattern constantly — it replaces three-line for loops with a single readable expression.

---

## SECTION 3 — Dictionaries: How Data Science Thinks About Records

A dictionary maps keys to values. Create with curly braces:

```python
person = {
    "name": "Alex",
    "age": 28,
    "role": "analyst",
    "salary": 85000
}

# Access by key
print(person["name"])   # "Alex"
print(person["age"])    # 28

# Safe access with .get() — returns None or a default instead of crashing
print(person.get("email"))              # None
print(person.get("email", "not set"))  # "not set"
```

Never use `person["key"]` on data you don't control — if the key doesn't exist, Python raises a `KeyError` and crashes. Use `.get()`.

```python
# Update a value
person["salary"] = 90000

# Add a new key
person["department"] = "analytics"

print(person)
# {"name": "Alex", "age": 28, "role": "analyst", "salary": 90000, "department": "analytics"}
```

In data science, you're almost never working with a single dictionary. You're working with a **list of dictionaries** — one dict per row:

```python
employees = [
    {"name": "Alex",  "role": "analyst",   "salary": 85000},
    {"name": "Jamie", "role": "engineer",  "salary": 92000},
    {"name": "Casey", "role": "analyst",   "salary": 78000},
    {"name": "Morgan","role": "engineer",  "salary": 95000},
]

# Sum all salaries — generator expression inside sum()
total = sum(e["salary"] for e in employees)
print(total)  # 350000

# Filter to analysts only
analysts = [e for e in employees if e["role"] == "analyst"]
print(analysts)
# [{"name": "Alex", ...}, {"name": "Casey", ...}]

# Average analyst salary
avg = sum(e["salary"] for e in analysts) / len(analysts)
print(avg)  # 81500.0
```

This pattern — list of dicts, filter with comprehension, aggregate with `sum()` or `len()` — is exactly what Pandas does internally, just at much larger scale. Understanding it here means you'll understand Pandas intuitively instead of memorizing methods.

---

## SECTION 4 — Functions: Writing Code You Can Actually Reuse

A function is a named, reusable block of logic. Define once, call anywhere:

```python
def calculate_average(numbers):
    return sum(numbers) / len(numbers)

scores = [85, 92, 78, 95, 88]
avg = calculate_average(scores)
print(avg)  # 87.6

# Reuse on any list — same function, different data
salaries = [85000, 92000, 78000]
print(calculate_average(salaries))  # 85000.0
```

Functions get more powerful with **default arguments** — parameters with fallback values you can override:

```python
def is_outlier(value, mean, threshold=2.0):
    distance = abs(value - mean) / mean  # relative distance from mean
    return distance > threshold / 10     # normalize to a useful scale

# Use the default threshold
print(is_outlier(150, mean=87.6))        # True — 150 is far from mean

# Override with a stricter threshold
print(is_outlier(95, mean=87.6, threshold=0.5))  # False — close enough

# Applied to a dataset
scores = [85, 92, 78, 95, 150, 88]  # 150 is suspicious
mean = calculate_average(scores)
outliers = [s for s in scores if is_outlier(s, mean)]
print(outliers)  # [150]
```

The last three lines do something real: compute a mean, flag outliers, return only the suspicious values — in pure Python, no libraries. This is the kind of code you'll write before you even open Pandas.

`[I remember hitting the same wall while building early analytics scripts for content and engagement tracking. I had copied the same 12-line block across three different notebooks — cleaning values, calculating averages, filtering rows — and every tiny change meant hunting through duplicated code hoping I didn’t miss one version. The moment I turned that block into a function, the entire workflow changed: fewer silent mistakes, faster iteration, and code I could actually trust six weeks later when I reopened the project.]`

---

## TAKEAWAY

Four things most beginners don't understand: types encode intention / lists are sequences, dicts are records / list comprehensions are concise loops / functions make code testable. Tutorial 3 brings NumPy — these structures scale to millions of rows.

## CTA

Rewrite Tutorial 1's average calculation as a function. Add a filter function. Reply with what you built or the first type error you caught.

---

**Post-writing:**
- `[PERSONAL_INSERT]` Section 4: 2–3 sentence story about abstracting a repeated notebook block into a function
- `[IMAGE_INSERT]` × 3: auto-fetched by `fetch_images.py`
- **3 title options:** (1) current title, (2) *The Type Error That Makes Your Analysis Wrong Without Crashing*, (3) *Lists, Dicts, and Functions: The Three Things Python Data Scientists Actually Use Every Day*
- **Derivative:** Twitter thread — "5 type mistakes Python beginners make in data science"