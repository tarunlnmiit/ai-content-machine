# Twitter Thread — DS Tutorial 2/10
# Post manually — cannot be scheduled

---

**Tweet 1 (HOOK)**
Python just gave me a wrong answer.

No error.
No crash.
Just a confident lie.

Here's the silent bug that fools every beginner's data analysis: 🧵

---

**Tweet 2 (BUG DEMO)**
You load a CSV with an "age" column.
You sum it.
Python reports a number.
You move on.

Except the column was stored as strings.

Python didn't add 28 + 35 + 42.
It concatenated them: "283542"

No error. Wrong answer.

---

**Tweet 3 (DEMONSTRATION)**
```
>>> print("28" + "35")
"2835"
```

Not 63.

Python treats string "28" completely differently from integer 28.

This is type behavior — and it trips up every data scientist.

---

**Tweet 4 (FIX)**
Two lines that fix this forever:

```
print(type(raw_value))  → <class 'str'>
age = int(raw_value)    → now it adds correctly
```

Rule: anything from a CSV, API, or user input arrives as a string until you explicitly convert it.

---

**Tweet 5 (THE FOUR CONVERSIONS)**
The four conversion functions you'll use constantly:

```
int("42")     → 42
float("42.5") → 42.5
str(42)       → "42"
bool(0)       → False
```

0, "", and [] all evaluate False. Everything else is True.

---

**Tweet 6 (INSIGHT)**
Senior data scientists type-check at ingestion, not after analysis.

Finding a type bug after the report is in front of stakeholders is very different from catching it in line 5.

Build the habit early.

---

**Tweet 7 (BROADER RULE)**
Every silent bug in data analysis traces back to the same root:

The programmer didn't know what kind of thing they were holding.

Types encode intention. Once you see this, you can't unsee it.

---

**Tweet 8 (CTA)**
This is covered in full — plus lists, dicts, and functions — in Tutorial 2 of my Python for Data Science series.

10 tutorials. Real analysis code. No fluff.

Tutorial 2 → [Medium link]
Tutorial 1 → [Medium link]
