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

`int`, `float`, `str`, `bool` — all four with code examples showing type(), the `"42" + "42" = "4242"` silent bug, and the conversion functions `int()`, `float()`, `str()`, `bool()`.

---

## SECTION 2 — Lists: The Workhorse of Sequences

Indexing, slicing (exclusive end), `append()`, and list comprehensions: `[s for s in scores if s > 85]`. Code shows filtering and transformation in one line.

---

## SECTION 3 — Dictionaries: How Data Science Thinks About Records

`.get()` for safe access, updating/adding keys, then the full list-of-dicts pattern with `sum(e["salary"] for e in employees)` and list comprehension filtering.

---

## SECTION 4 — Functions: Writing Code You Can Actually Reuse

`calculate_average()` as a named reusable function, then `is_outlier()` with a default `threshold=2.0` argument — real statistical logic in pure Python, no libraries.

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