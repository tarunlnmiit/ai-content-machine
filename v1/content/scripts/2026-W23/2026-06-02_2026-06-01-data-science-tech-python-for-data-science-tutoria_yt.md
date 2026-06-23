```
SHOW: Breath of Data Science
EPISODE TITLE (working): NumPy and the Art of Thinking in Arrays — Python for Data Science Tutorial 3/10
TARGET RUNTIME: 6–7 minutes
WORD COUNT: 870
```

---

At some point, your Python loop stops being fast enough. Not theoretically — you'll feel it. You'll run a calculation on 100,000 rows and your laptop fan will spin up and you'll sit there watching a cursor blink for 12 seconds. Waiting for one number. A number you could've had in 0.08 seconds if you'd known one thing sooner.

Python loops are slow. NumPy arrays are not.

[ANIMATION: 5-second title card — "Python for Data Science: Tutorial 3/10 — Thinking in Arrays"]

[SCREEN: blank Python file, import numpy as np]

```python
import numpy as np
```

Tutorial 2 covered lists and dictionaries. That's real Python — genuinely useful stuff. But when data scientists say "Python is fast," they don't mean the Python you've been writing so far. They mean NumPy Python. Vectorized operations running in optimized C code underneath a familiar surface. This tutorial is about that shift. Once it clicks, you won't go back. And when we get to Pandas in Tutorial 5, it'll make sense from first contact — because Pandas is built on exactly what we're covering today.

NumPy was released in 2006 to solve a problem that was killing Python for scientific computing. Python lists are flexible — you can put anything in them, integers, strings, a mix. That flexibility costs performance at every step. NumPy's ndarray makes a different tradeoff: all elements must be the same type. In exchange, you get storage that fits in contiguous memory, operations implemented in compiled C and Fortran, and the ability to apply math to an entire array without a single Python loop. The speed difference isn't marginal. For operations on a million numbers, NumPy is typically 50 to 200 times faster than a Python loop. That's the difference between watching your script run and it being done before you look up.

[ANIMATION: 3-second lower third — "NumPy: 50–200× faster than a Python loop"] Every major data science library — Pandas, scikit-learn, TensorFlow, PyTorch — stores its data in NumPy arrays underneath. This isn't a detour. It's the foundation.

[SCREEN: code editor — creating first NumPy array from a Python list]

```python
import numpy as np

# Convert a Python list to a NumPy array
scores = np.array([88, 92, 79, 95, 84, 73, 91])
print(scores)       # [88 92 79 95 84 73 91]  — no commas
print(scores.dtype) # int64

# Utility constructors
zeros = np.zeros(5)               # [0. 0. 0. 0. 0.]
ones  = np.ones(5)                # [1. 1. 1. 1. 1.]
rng   = np.arange(0, 10, 2)       # [0 2 4 6 8]
pts   = np.linspace(0, 1, 5)      # [0.   0.25 0.5  0.75 1.  ]
```

Let's start with how you actually create arrays. The most common starting point is converting a Python list. You call `np.array` on a list and you've got an ndarray. Print it out and you'll notice something small but important — there are no commas between the numbers in the output. That's a visual tell that you're looking at NumPy, not a plain list. You can also check the `dtype` attribute, which tells you exactly what's held in memory — int64 by default for integers, float64 for decimals. [PAUSE] Beyond converting existing data, there are three utility constructors you'll reach for constantly: `np.zeros`, `np.ones`, and `np.arange`. Zeros and ones create arrays of a given size filled with — you guessed it — zeros or ones. `arange` works like Python's built-in `range` but outputs an array, and it handles floats cleanly. For a fixed number of evenly spaced points, `np.linspace` is cleaner — you give it a start, a stop, and how many points you want, and it handles the spacing. These are how you create axis values for plots and percentile scales before you've even loaded a dataset.

[SCREEN: terminal output — shape, ndim, size printed for a 1D array]

```python
scores = np.array([88, 92, 79, 95, 84, 73, 91])

print(scores.shape) # (7,)
print(scores.ndim)  # 1
print(scores.size)  # 7
```

Now the big conceptual shift. The single most important thing NumPy changes about how you write code: you stop looping, and you start describing operations. Take a simple example — you have an array of test scores and you want to double each one. In plain Python, you'd write a loop, append to a new list, and you'd have your answer eventually. In NumPy, you write `scores * 2`. That's it. NumPy applies the multiplication to every element in optimized C code. Same result, but one runs in a fundamentally different way.

[SCREEN: side-by-side — Python loop vs NumPy vectorized operation]

```python
scores = np.array([88, 92, 79, 95, 84, 73, 91])

# Python loop
doubled = []
for s in scores:
    doubled.append(s * 2)

# NumPy — same result, no loop
doubled = scores * 2

# Boolean indexing — filter scores above 90
mask        = scores > 90          # [False  True False  True False False  True]
high_scores = scores[scores > 90]  # [92 95 91]
```

Arithmetic is fully vectorized — addition, subtraction, powers, square roots, all applied element-wise with no loop in sight. The one that matters most for real data work is comparison. Write `scores > 90` and you get back a boolean array — True where the condition holds, False where it doesn't. Then use that boolean array as an index to filter your original data. `scores[scores > 90]` gives you only the values above 90. [PAUSE] This is the exact pattern Pandas uses for filtering DataFrames. You'll write `df[df["column"] > value]` hundreds of times. Understanding it now means it won't feel like magic later.

[SCREEN: aggregation methods — mean, std, percentile on a salary array]

```python
salaries = np.array([42000, 58000, 75000, 95000, 110000, 48000, 61000, 250000])

print(salaries.mean())                   # 92375.0
print(salaries.std())                    # 64895.4
print(salaries.min(), salaries.max())    # 42000  250000

# IQR-based outlier detection
q1, q3  = np.percentile(salaries, [25, 75])
iqr     = q3 - q1
low     = q1 - 1.5 * iqr
high    = q3 + 1.5 * iqr
clean   = salaries[(salaries >= low) & (salaries <= high)]
print(clean)  # [42000 58000 75000 95000 110000 48000 61000]
```

For actual data analysis, you'll be computing the same stats over and over: mean, standard deviation, min, max, percentiles. NumPy has all of them as one-method calls. Where it gets genuinely useful is percentile-based outlier detection. Compute the 25th and 75th percentiles, find the interquartile range, set a fence at 1.5 times the IQR above and below, then use boolean indexing to pull out what falls outside it. That's a proper statistical outlier check in six lines of code. No loop. No library beyond NumPy.

[SCREEN: 2D array creation — student scores matrix with shape (3, 4)]

```python
# 3 students, 4 tests
grades = np.array([
    [85, 92, 78, 90],   # student 0
    [79, 88, 95, 82],   # student 1
    [91, 76, 84, 88],   # student 2
])

print(grades.shape)      # (3, 4)
print(grades[1, 2])      # 95  — student 1, test 2
print(grades[:, 2])      # [78 95 84]  — all rows, column 2
```

Everything so far has been one-dimensional. Real datasets have rows and columns, so let's look at 2D arrays. You create them by passing a list of lists to `np.array`. Shape comes back as `(3, 4)` — three rows, four columns. To access a single element you use two indices separated by a comma: row first, then column. To get an entire column, you use a colon for the row dimension — "all rows, column 2." The colon means "all of this dimension." You'll write that syntax constantly.

[SCREEN: axis=0 vs axis=1 aggregation — column means vs row means]

```python
# axis=0 → collapse rows → one value per column (avg score per test)
avg_per_test    = grades.mean(axis=0)   # [85.  85.33 85.67 86.67]

# axis=1 → collapse columns → one value per row (avg score per student)
avg_per_student = grades.mean(axis=1)   # [86.25 86.   84.75]
```

When you aggregate a 2D array, you have to specify an axis. Axis zero collapses down across rows — you get one result per column. Axis one collapses across columns — one result per row. Average score per student is axis one. Average score per test is axis zero. If that's not sticking yet, the mnemonic I use: axis zero goes down, axis one goes across. [PAUSE]

[ANIMATION: 3-second lower third — "axis=0 → down (per column) · axis=1 → across (per row)"]

[PERSONAL_INSERT: Early in my data science journey, I had a script that used multiple nested loops to calculate metrics across a dataset. I remember feeling oddly proud that I'd finally gotten it working—until I learned the same operation could be expressed in a couple of NumPy statements. The embarrassing part wasn't the performance difference; it was realizing I'd spent an hour writing code that NumPy had already solved years ago. That was the moment I started thinking in arrays instead of loops.]

[SCREEN: final output — row means and column means printed]

```python
print("Avg score per test (axis=0):")
print(avg_per_test)
# [85.   85.33 85.67 86.67]

print("Avg score per student (axis=1):")
print(avg_per_student)
# [86.25 86.   84.75]
```

Here's what NumPy actually gave you. A grammar. When you write `scores[scores > 90]`, you're describing a relationship — not issuing step-by-step instructions. Lists taught you to sequence. Dicts taught you to map. NumPy teaches you to operate on the whole thing at once. That shift is what people mean when they say Python is expressive for data work.

Next up is Pandas. It wraps NumPy arrays in a structure with column names, row labels, and a query language. Every pattern you learned here — boolean indexing, axis-based aggregation, vectorized math — carries forward directly. You're not starting over. You're adding a layer.

[ANIMATION: 5-second outro card — "Tutorial 4 coming next: data cleaning with Pandas"]

Before that though — take the outlier detection code from this tutorial and run it on any list of numbers you have. Make up a salary dataset. Use your own exam scores. The only way this clicks is through repetition with real numbers. And if you know someone who keeps asking why Python feels slow, send them this one. It's probably the tutorial they actually need.