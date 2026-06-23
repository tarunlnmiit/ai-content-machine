# LinkedIn Post — DS Tutorial 2/10
# Status: DRAFT — do not publish until employer clearance

---

I built an analytics report that was completely wrong.

Python never said a word.

The column was labeled "age." I summed it. Python returned a number. I moved on.

Except the values were stored as strings. Python didn't add 28 + 35 + 42. It concatenated them: "283542".

No error. No crash. Just a confident, plausible-looking wrong answer waiting to embarrass me in front of a stakeholder.

This is the silent bug that traps every beginner data scientist — and more intermediate ones than anyone admits.

The fix is two lines:
- `print(type(your_column))` — check what you're actually holding
- Cast explicitly: `int(value)`, `float(value)` — convert before you compute

Rule: anything from a CSV, API, or user input arrives as a string until you explicitly convert it. Always.

The deeper principle: types encode intention. Python doesn't add "28" + "35" — it concatenates text. That's not a bug. That's Python doing exactly what you told it to do with the type you gave it.

Senior data scientists type-check at ingestion. Not after the analysis is done. Not when a stakeholder questions the number. In line 5.

Tutorial 2 of my Python for Data Science series covers this in full — plus lists, dicts, and the functions that make up 90% of what data scientists actually write before they open Pandas. Link in bio.

What's the worst silent bug you've ever shipped? I'll start: this exact one, in a client-facing engagement report. The number looked right. It wasn't.

#Python #DataScience #DataAnalysis #PythonTutorial #SoftwareEngineering
