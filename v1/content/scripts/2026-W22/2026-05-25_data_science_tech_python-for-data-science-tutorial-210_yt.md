Reading transcript now and drafting script.

---

# Why Python Lies to You (And How to Stop It): Data Types, Lists, and Dictionaries

**Hook:** Your analysis will give you a wrong answer someday — and the worst part is it won't crash. Python will just hand you a number so plausible you'll believe it, ship it, and find out six months later.

---

## The Silent Bug That Bites Every Data Scientist

Here's how it happens.

Your CSV comes in with a column called `H`. You load it. You sum the values. Python reports a total, and you move on.

Except that column was stored as text — as strings, not numbers. So when Python "added" them, it didn't calculate 28 + 35 + 42. It smashed the strings together: `"283542"`.

[BROLL: terminal showing string concatenation vs numeric addition side by side]

No error message. No warning. Just a wrong answer sitting in your spreadsheet, looking completely legitimate.

This is what this tutorial is about — the difference between data that *looks* like a number and data Python *actually treats* as a number. And the structures that let you build analysis that doesn't lie to you by accident.

---

## Why Python's Flexibility Is Also Its Trap

In the first tutorial, you built your first script: lists, dictionaries, looping, calculating an average. You handled multiple data types without ever naming them — integers, strings, floats, maybe a Boolean.

Python is dynamically typed. That means you don't declare what type something is — you just assign a value and Python figures it out. This feels like a feature.

And it is. Right up until the moment it lets you concatenate numbers like they're words and call the result a sum.

[BROLL: code snippet showing `"28" + "35"` returning `"2835"`]

For beginners, this causes confusion. For data scientists, it causes *expensive* confusion — the kind where your analysis runs fine, your numbers look reasonable, and then six months later someone asks: *wait, how did you get that?* And you can't trace it back, because the bug was never in your logic. It was in your data types all along.

---

## What We're Covering Today

Four things:

1. **The four primitive types** Python uses — integers, floats, strings, Booleans
2. **Lists** — ordered sequences
3. **Dictionaries** — how data scientists think about records
4. **Functions** — turning code you copy-paste into code you actually reuse

By the end, you'll know what type every piece of your data is, why that matters, and how to catch type mistakes before they become silent bugs.

---

## The Four Primitives

Let's start with assignment. Python has a built-in function called `type()` that tells you exactly what you're holding.

```python
print(type(28))      # <class 'int'>
print(type("28"))    # <class 'str'>
```

[BROLL: running the above in terminal, output shown]

Same-looking value. Completely different type. That's the trap.

Here are the four primitives:

- **Integer** — whole numbers. `age = 28`
- **Float** — decimals. `accuracy = 0.94`
- **String** — text in quotes. `role = "analyst"`
- **Boolean** — `True` or `False`. `has_missing = False`

Python treats them completely differently, even when they look the same. `1`, `1.0`, and `"1"` are three distinct things.

```python
age = 28          # int
year = 2024       # int
accuracy = 0.94   # float
rate = 1.5        # float
role = "analyst"  # str
has_missing = False  # bool
```

[BROLL: `type()` printed for each variable, output scrolling in terminal]

---

## The Silent Bug, Demonstrated

Here it is, live:

```python
print(28 + 35)      # 63   ✓
print(28.0 + 35.0)  # 63.0 ✓
print("28" + "35")  # 2835 ✗
```

[BROLL: running this — first two lines correct, third line shows "2835"]

Python did not add those numbers. It concatenated the text. No error, no warning — just a plain wrong answer.

---

## How to Check What You're Holding

Use `type()`. Get in the habit of calling it on anything that came from outside your code — especially CSVs, APIs, and user input.

```python
h = "28"          # came from CSV — it's a string
print(type(h))    # <class 'str'>

h_int = int(h)    # explicit conversion
print(h_int + 10) # 38 ✓
```

[BROLL: terminal output showing type str → conversion → int arithmetic working correctly]

The four conversion functions you'll use constantly:

```python
int("42")      # → 42
float("42.5")  # → 42.5
str(42)        # → "42"
bool(0)        # → False
```

**Rule of thumb:** any data from a CSV, API, or user input arrives as a string until you convert it. This is where silent bugs are born. You load your CSV, sum a column, get a result that looks plausible — and never realize it was concatenation instead of addition.

---

## Lists — Ordered Collections

A list is a sequence: an ordered collection of items, created with square brackets.

```python
scores = [85, 92, 78, 95]
```

Access items by position. Python indexes from zero:

```python
scores[0]  # 85
scores[1]  # 92
```

[BROLL: list index diagram — position 0, 1, 2, 3 labeled]

You can slice — pull a range of items:

```python
scores[1:3]  # [92, 78]
```

Python slicing is *exclusive on the end* — `1:3` gives you index 1 and 2, not 3. This trips up everyone in their first week.

Add an item with `.append()`:

```python
scores.append(90)
print(scores)  # [85, 92, 78, 95, 90]
```

---

## Filtering Lists — Two Ways

Say you want every score above 85.

**Way 1: for loop**

```python
for score in scores:
    if score > 85:
        print(score)
# 92, 95, 90
```

**Way 2: list comprehension**

```python
high_scores = [score for score in scores if score > 85]
print(high_scores)  # [92, 95, 90]
```

[BROLL: both outputs side by side in terminal — same result]

List comprehension is concise, readable, and every data scientist uses this pattern constantly. Get comfortable with it early — you'll see it everywhere in pandas, NumPy, and real production code.

---

**Close:** Data science bugs don't always crash. The dangerous ones run quietly and hand you a wrong answer with a straight face. Understanding what type your data actually is — not just what it looks like — is the first layer of defense. In the next part, we go deeper: dictionaries, functions, and how these pieces connect into real analysis workflows. If this helped, subscribe — one tutorial a week, no fluff.
