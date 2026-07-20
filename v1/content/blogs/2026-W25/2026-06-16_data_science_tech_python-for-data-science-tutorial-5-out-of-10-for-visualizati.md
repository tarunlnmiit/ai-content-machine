---
title: "Python for Data Science — Tutorial 5/10: Making Your Data Tell a Story with Matplotlib and Seaborn"
type: blog
niche: data_science_tech
date: 2026-06-16
week: 2026-W25
slug: python-for-data-science-tutorial-5-out-of-10-for-visualizati
tags: [content/blog, niche/data_science_tech, week/2026-W25]
---
# Python for Data Science — Tutorial 5/10: Making Your Data Tell a Story with Matplotlib and Seaborn

---

## HOOK — ~150 words

Nobody tells you this in your first data science job, but your charts will get judged before your model does.

You can build a regression with a 0.94 R², a clean pipeline, six months of feature engineering — and then paste a default matplotlib figure into the slide deck, gray background and all, and watch everyone in the room quietly decide you don't know what you're doing.

I made this mistake. Multiple times. `[PERSONAL_INSERT: I remember sending a client a notebook full of analysis I was genuinely proud of, only to realize later that every chart still looked like the default matplotlib output—gray background, tiny fonts, cluttered axes. The feedback wasn't about the analysis at all. The first comments were about how difficult the charts were to read.]`

Visualization is where your analysis either lands or disappears. It's not cosmetic. It's communication. And in Python, you have two tools that, used together, handle 95% of what you'll ever need: **matplotlib** for control, **seaborn** for speed.

This is tutorial 5 of 10 in this series. By the end, you'll never paste a gray-background plot again.

---

![data scientist laptop screen showing colorful data charts graphs python](/content/blogs/2026-W25/2026-06-16_data_science_tech_python-for-data-science-tutorial-5-out-of-10-for-visualizati_images/01_hook_data-scientist-laptop-screen-showing-colorful-data.jpg)
*data scientist laptop screen showing colorful data charts graphs python — Photo by [RDNE Stock project](https://www.pexels.com/photo/person-using-black-and-gray-laptop-7947999/) on Pexels*

---

## CONTEXT — ~200 words

If you've been following this series, you now know how to load data (tutorial 1), clean it (tutorials 2–3), and wrangle it with pandas (tutorial 4). You have good data. The next problem is showing it to someone.

Here's what most tutorials skip about visualization: matplotlib and seaborn are not competing libraries. They're layers. Seaborn is built *on top of* matplotlib — it gives you high-level plot types that look good with almost no configuration. Matplotlib gives you low-level control to customize every pixel when seaborn's defaults aren't enough.

The mental model: **seaborn for the 80%, matplotlib for the last 20%.**

Most of your plots — distributions, correlations, category comparisons, time trends — can be written in 3–5 lines of seaborn. The cleanup (titles, font sizes, axis labels, saving to file) is matplotlib.

In this tutorial, we'll cover:
- Setting up a clean style baseline
- The five plot types you'll use constantly
- Combining seaborn and matplotlib in the same figure
- Saving publication-quality output

We'll use a real dataset throughout: the classic Titanic dataset, available everywhere.

---

## SECTION 1 — ~400 words

### The Setup: Importing Libraries and Getting Your Style Baseline Right

Before you plot a single point, establish your visual defaults. This one block at the top of every notebook will save you from wrestling with aesthetics on every chart.

```bash
pip install matplotlib seaborn pandas
```

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Style baseline — run this at the top of every notebook
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.2)
plt.rcParams.update({
    "figure.dpi": 150,
    "figure.figsize": (10, 6),
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# Load the dataset
df = sns.load_dataset("titanic")
df.head()
```

Run this and you'll see the Titanic dataset load cleanly — 891 rows, columns including `survived`, `pclass`, `age`, `fare`, `sex`, `embarked`.

Three things this setup does that matter:

**`sns.set_theme(style="whitegrid")`** removes the gray background matplotlib defaults to and replaces it with a clean white plot area and light horizontal gridlines. Every chart immediately looks more professional.

**`font_scale=1.2`** bumps all text up by 20%. Default matplotlib font sizes are designed for an era when monitors were small. They're too small for slides, too small for Medium images, too small for anything you'll share.

**Removing top and right spines** (the box lines around your chart) is a visual design decision backed by data-ink ratio theory — Edward Tufte's principle that every non-data element in a chart should justify its existence. The top and right borders add no information. Remove them and your chart looks cleaner immediately.

`[PERSONAL_INSERT: One of my favorite visualization lessons came from a two-line change. I removed the top and right borders from a chart, put the before-and-after versions side by side, and realized how much visual clutter I'd been accepting as normal.]`

One important detail: **set this once per session, not per chart.** Seaborn's `set_theme` sets a global matplotlib state. Every plot in the notebook inherits it. If you're opening a new notebook or script, this block goes at the top.

---

![matplotlib seaborn python visualization comparison clean vs default chart](/content/blogs/2026-W25/2026-06-16_data_science_tech_python-for-data-science-tutorial-5-out-of-10-for-visualizati_images/02_section1_matplotlib-seaborn-python-visualization-comparison.jpg)
*matplotlib seaborn python visualization comparison clean vs default chart — Photo by [RDNE Stock project](https://www.pexels.com/photo/black-flat-screen-computer-monitor-7948062/) on Pexels*

---

## SECTION 2 — ~400 words

### The Five Plot Types You'll Use in 90% of Your Work

Five charts handle almost everything in exploratory data analysis. Learn these cold and you'll be fast.

**1. Distribution — `sns.histplot`**

When you first see a new numeric column, you want its shape. Skewed? Bimodal? Bounded at zero?

```python
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

sns.histplot(df["age"].dropna(), kde=True, ax=axes[0], color="steelblue")
axes[0].set_title("Age Distribution")
axes[0].set_xlabel("Age")

sns.histplot(df["fare"], kde=True, ax=axes[1], color="salmon")
axes[1].set_title("Fare Distribution")
axes[1].set_xlabel("Fare (£)")

plt.tight_layout()
plt.show()
```

Look at the output: age is roughly normal with a slight right skew, while fare is heavily skewed right — most passengers paid under £50, but some paid over £500. That asymmetry matters the moment you consider using fare as a model feature.

**2. Relationship — `sns.scatterplot`**

Two numeric variables, any interaction.

```python
sns.scatterplot(
    data=df,
    x="age",
    y="fare",
    hue="survived",
    palette={0: "salmon", 1: "steelblue"},
    alpha=0.6,
    s=60,
)
plt.title("Age vs Fare, colored by Survival")
plt.xlabel("Age")
plt.ylabel("Fare (£)")
plt.legend(title="Survived", labels=["No", "Yes"])
plt.show()
```

The `hue` parameter encodes a third variable with color — in this case survival. You can see high-fare passengers cluster at the top with more blues (survived) than reds.

**3. Categorical comparison — `sns.barplot`**

```python
sns.barplot(
    data=df,
    x="pclass",
    y="survived",
    palette="Blues_d",
    errorbar="ci",
)
plt.title("Survival Rate by Passenger Class")
plt.xlabel("Passenger Class")
plt.ylabel("Survival Rate")
plt.ylim(0, 1)
plt.show()
```

The confidence interval bars (default in seaborn) are automatic — you get uncertainty for free. First class survival rate is roughly 63%; third class drops below 25%.

**4. Correlation heatmap — `sns.heatmap`**

```python
numeric_cols = df.select_dtypes(include="number")
corr_matrix = numeric_cols.corr()

sns.heatmap(
    corr_matrix,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0,
    square=True,
    linewidths=0.5,
)
plt.title("Feature Correlation Matrix")
plt.tight_layout()
plt.show()
```

**5. Distribution across categories — `sns.boxplot`**

```python
sns.boxplot(data=df, x="pclass", y="age", palette="pastel")
plt.title("Age Distribution by Passenger Class")
plt.xlabel("Passenger Class")
plt.ylabel("Age")
plt.show()
```

These five handle distributions, relationships, categorical comparisons, correlations, and grouped distributions. Most EDA starts and ends here.

---

## SECTION 3 — ~400 words

### What Most People Miss: Combining Seaborn and Matplotlib in One Figure

Here's where beginners get stuck. They find a seaborn chart they like, then want to add a title, annotation, or custom axis — and it breaks because they're mixing seaborn and matplotlib calls without understanding the object structure.

The key insight: **every seaborn call returns a matplotlib object.** Once you understand this, the two libraries become one tool.

Seaborn has two API levels:
- **Figure-level functions** (e.g., `sns.relplot`, `sns.displot`, `sns.catplot`) — these create their own figure and return a `FacetGrid` object
- **Axes-level functions** (e.g., `sns.scatterplot`, `sns.histplot`, `sns.barplot`) — these draw on a matplotlib axes object

For control, use axes-level functions with explicit `ax=` targets:

```python
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Titanic EDA Dashboard", fontsize=16, fontweight="bold", y=1.01)

# Top-left: survival by class
sns.barplot(data=df, x="pclass", y="survived", palette="Blues_d", ax=axes[0, 0])
axes[0, 0].set_title("Survival Rate by Class")
axes[0, 0].set_ylabel("Rate")
axes[0, 0].set_xlabel("Class")

# Top-right: age distribution
sns.histplot(df["age"].dropna(), kde=True, ax=axes[0, 1], color="steelblue")
axes[0, 1].set_title("Age Distribution")
axes[0, 1].set_xlabel("Age")

# Bottom-left: fare by class
sns.boxplot(data=df, x="pclass", y="fare", palette="pastel", ax=axes[1, 0])
axes[1, 0].set_title("Fare by Passenger Class")
axes[1, 0].set_ylabel("Fare (£)")

# Bottom-right: survival by sex
sns.barplot(data=df, x="sex", y="survived", palette="Set2", ax=axes[1, 1])
axes[1, 1].set_title("Survival Rate by Sex")
axes[1, 1].set_ylabel("Rate")
axes[1, 1].set_xlabel("")

plt.tight_layout()
plt.show()
```

You'll get a 2×2 dashboard with four charts, a shared title, consistent styling — all in under 25 lines.

The thing to notice in the output: your eye moves across all four charts together. You see patterns you'd miss looking at them one by one — survival drops hard from class 1 to 3, while the male/female gap is enormous. One figure. Two insights that interact.

`[PERSONAL_INSERT: The first time I built a dashboard-style figure instead of presenting charts one at a time, the conversation changed completely. People stopped focusing on individual charts and started discussing the story emerging across all of them. That's when I realized good visualization isn't decoration—it's narrative.]`

This is the pattern professional data scientists use in notebooks they hand to stakeholders. Not one chart. A story panel.

---

![professional python data visualization dashboard multiple charts grid analysis](/content/blogs/2026-W25/2026-06-16_data_science_tech_python-for-data-science-tutorial-5-out-of-10-for-visualizati_images/03_section3_professional-python-data-visualization-dashboard-m.jpg)
*professional python data visualization dashboard multiple charts grid analysis — Photo by [Lukas Blazek](https://www.pexels.com/photo/close-up-photo-of-gray-laptop-577210/) on Pexels*

---

## SECTION 4 — ~400 words

### Saving Your Output and the Details That Separate Good Charts from Bad Ones

Everything we've done looks fine on screen. But if you're saving to a PNG and pasting it into a slide, you're probably making it blurry.

Default matplotlib saves at 72 DPI. Most presentation software and monitors render at 150–300 DPI. Your chart gets stretched and interpolated. It looks fine at small size. Zoom in on a projector and the text is fuzzy.

Fix this at save time:

```python
# After your final plt.show() call, save high-quality output
fig.savefig(
    "titanic_eda_dashboard.png",
    dpi=300,
    bbox_inches="tight",
    facecolor="white",
)
```

`bbox_inches="tight"` prevents cropping at the edges — especially important when your suptitle sits above the figure. `facecolor="white"` ensures a white background even if your notebook theme is dark.

For vector output (best for publication or scaling):

```python
fig.savefig("titanic_eda_dashboard.pdf", bbox_inches="tight")
fig.savefig("titanic_eda_dashboard.svg", bbox_inches="tight")
```

SVG and PDF are resolution-independent. Use these for blog images, publications, or anything that might be printed.

**Three chart details that make the biggest difference:**

**Titles with units.** "Fare" is a bad axis label. "Fare (£)" is better. "Fare in GBP (1912 prices)" is best. Every numeric axis should have a unit.

**Consistent color assignment.** If "survived" is steelblue in your first chart, it must be steelblue in every chart. Assign colors explicitly using a palette dict: `palette={0: "salmon", 1: "steelblue"}`. Never let seaborn cycle randomly across plots that share a variable.

**Zero-baseline for bar charts.** Always start your y-axis at zero for bar charts. A chart showing survival rates from 0.2 to 0.7 is honest. The same chart with y-axis starting at 0.19 makes a 10% difference look enormous. Matplotlib doesn't enforce this automatically — you do: `plt.ylim(0, 1)`.

These three fixes don't require design skill. They require intention. And they're the difference between a chart that communicates and a chart that misleads.

---

## TAKEAWAY — ~200 words

Matplotlib and seaborn aren't tools you learn once and master. They're tools you get comfortable with over a hundred notebooks, and then suddenly one day you realize you're not thinking about the API at all — you're thinking about the story you're trying to tell.

That's the shift. From "how do I make this chart" to "what does this chart need to say."

The five plot types in Section 2 handle almost everything you'll encounter for the next year. The setup block in Section 1 takes 10 seconds to copy. The multi-panel approach in Section 3 will change how your stakeholder meetings go.

Start there. One notebook. Load a dataset you care about. Build all five charts. Save them at 300 DPI. Then ask: does someone who has never seen this data understand the key pattern within 5 seconds of looking at each chart?

If not — the chart needs work, not the data.

That's the standard. It's achievable. And it makes everything downstream — presentations, reports, model explainability — easier.

Tutorial 6 covers statistical testing with scipy and statsmodels. We'll take these patterns and start asking whether what we see is real.

---

## CTA — ~100 words

If this series is helping you build real Python skills for data science, the best thing you can do is share it with one person who's currently learning — not bookmarking it. That's how good content survives.

Follow me on Medium if you want the rest of this series in your feed. Tutorial 6 drops next week: statistical testing, when to use which test, and how to report results in plain English.

And if you've built something with matplotlib or seaborn recently — screenshot it and reply. I'd genuinely like to see what you're working on.

---

## Post-Writing Notes

**`[PERSONAL_INSERT]` spots:**
1. *Hook* — A specific memory of presenting a default gray-background matplotlib chart at a job or to a client. The silence or polite feedback that followed. Keep it short and specific — one sentence of setup, one of consequence.
2. *Section 1* — The "spine trick" discovery moment. A before/after visual would work here, but a line like "I spent two years not knowing about `axes.spines`" is enough.
3. *Section 3* — First time building a multi-panel figure for a stakeholder meeting vs. showing charts sequentially. The difference in engagement and the speed of the conversation.

**`[IMAGE_INSERT]` spots:** All three are auto-fetched by `fetch_images.py`. No action needed.

---

**3 Potential Titles:**

1. **Python for Data Science #5: Matplotlib and Seaborn Are Not Competing Libraries**
2. **Your Charts Are Getting Judged Before Your Model Is — Here's How to Fix That**
3. **The 5 Plot Types Every Data Scientist Actually Uses (Python Tutorial 5/10)**

---

**1 Derivative Angle:**

Twitter/X thread: "5 matplotlib mistakes I made in my first year as a data scientist (and the 1-line fixes)" — pull the setup block, spine tip, DPI save, zero-baseline rule, and consistent color assignment as 5 numbered tweets. Ends with link to full tutorial.

<!-- worksheet-cta -->

---

### Want to put this into practice?

[Download the companion worksheet →](https://worksheets-thebreathnetwork.vercel.app/get-worksheet?slug=python-for-data-science-tutorial-5-out-of-10-for-visualizati)

_Free PDF. Enter your email and it opens right away._
