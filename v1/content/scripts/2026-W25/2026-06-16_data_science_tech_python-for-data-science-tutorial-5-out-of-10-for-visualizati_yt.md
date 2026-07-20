---
title: "Style baseline — run this at the top of every notebook"
type: script
niche: data_science_tech
date: 2026-06-16
week: 2026-W25
slug: python-for-data-science-tutorial-5-out-of-10-for-visualizati
platform: yt
tags: [content/script, niche/data_science_tech, week/2026-W25]
---
```
SHOW: Breath of Data Science
EPISODE TITLE (working): Your Charts Are Getting Judged Before Your Model Is
TARGET RUNTIME: 6–7 minutes
WORD COUNT: 920
```

[ANIMATION: 5-second title card — "Python for Data Science #5: Matplotlib + Seaborn"]

[BROLL: 5-second intro — screen recording of a default gray matplotlib chart transforming into a clean, styled dashboard]

Nobody tells you this in your first data science job, but your charts will get judged before your model does.

[SCREEN: default matplotlib figure — gray background, tiny fonts, cluttered axes]

```python
import matplotlib.pyplot as plt, seaborn as sns
df = sns.load_dataset("titanic")
plt.figure()                       # raw matplotlib defaults — gray bg, tiny fonts
plt.hist(df["age"].dropna(), bins=30)
plt.title("age")
plt.show()
```

You can build a regression with a 0.94 R², a clean pipeline, six months of feature engineering — and then paste a default matplotlib figure into the slide deck, gray background and all, and watch everyone in the room quietly decide you don't know what you're doing.

I remember sending a client a notebook I was genuinely proud of — six weeks of analysis, solid methodology, results I stood behind. The feedback I got back wasn't about any of that. The first comment was: these charts are really hard to read. That was it. That was the conversation. The analysis became secondary the moment the charts made people work. I've never sent a default matplotlib figure since.

Visualization is where your analysis either lands or disappears. It's not cosmetic. It's communication. And in Python, you have two tools that handle 95% of everything you'll ever need: matplotlib for control, seaborn for speed. This is tutorial five of ten. By the end, you'll never paste a gray-background plot again.

[SCREEN: seaborn docs homepage alongside matplotlib docs — showing they're separate packages]

> Links to show on screen: seaborn — https://seaborn.pydata.org/ · matplotlib — https://matplotlib.org/stable/

Here's what most tutorials skip about matplotlib and seaborn: they're not competing libraries. They're layers. Seaborn is built on top of matplotlib — it gives you high-level plot types that look good with almost no configuration. Matplotlib gives you low-level control when seaborn's defaults aren't enough.

The mental model is: seaborn for the 80%, matplotlib for the last 20%.

Most of your plots — distributions, correlations, category comparisons — can be written in three to five lines of seaborn. The cleanup — titles, font sizes, saving to file — that's matplotlib. We'll use the Titanic dataset throughout. It's built into seaborn, no download needed.

[SCREEN: terminal — pip install matplotlib seaborn pandas running]

Before you plot a single point, establish your visual defaults. This block goes at the top of every notebook.

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

[SCREEN: Titanic dataset loaded — 891 rows, columns: survived, pclass, age, fare, sex, embarked]

Three things this does that matter. `sns.set_theme(style="whitegrid")` kills the gray background — replaces it with a clean white area and light horizontal gridlines. `font_scale=1.2` bumps all text up 20%. Default matplotlib fonts were designed for small monitors. They're too small for slides, too small for anything you'll share. And removing the top and right spines — those box lines around your chart — is a design decision backed by Edward Tufte's data-ink ratio principle: every non-data element should justify its existence. The borders add no information. Remove them, your chart looks cleaner immediately.

I actually learned the spine thing from a code review, not a tutorial. Someone looked at one of my charts and asked: what are those border lines doing there? And I didn't have an answer. They're just... there, by default. I removed them. Looked at the before and after. The chart immediately felt less boxed in. That was three or four years ago. It's been in my baseline since.

Set this once per session. Every plot in the notebook inherits it.

[PAUSE]

Now, five plot types. Learn these cold and you'll cover 90% of exploratory analysis.

[SCREEN: histplot output — age distribution with KDE curve, fare distribution heavily right-skewed]

[ANIMATION: 3-second lower third — "5 Plot Types: hist · scatter · bar · heatmap · box"]

Distribution first, always. `sns.histplot` with `kde=True` gives you the shape and density together.

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

[SCREEN: two-panel output — age roughly normal, fare skewed right with a long tail past £500]

Age is roughly normal. Fare is heavily skewed right — most passengers paid under £50, but some paid over £500. That asymmetry matters the moment you consider fare as a model feature. For relationships between two numeric variables, `sns.scatterplot` with a `hue` parameter encodes a third variable with color — in this case survival. High-fare passengers cluster with more survivors. For categorical comparisons, `sns.barplot` gives you confidence intervals automatically — first class survival roughly 63%, third class drops below 25%. A correlation heatmap with `sns.heatmap` and `annot=True` gives you the full feature correlation matrix in under ten lines. And `sns.boxplot` shows distributions across groups — age by passenger class, median and outliers both visible.

[SCREEN: 2x2 grid of all five chart types side by side]

```python
fig, ax = plt.subplots(2, 3, figsize=(16, 9))
sns.histplot(df["age"].dropna(), kde=True, ax=ax[0,0], color="steelblue"); ax[0,0].set_title("histplot")
sns.scatterplot(data=df, x="age", y="fare", hue="survived", ax=ax[0,1]); ax[0,1].set_title("scatterplot")
sns.barplot(data=df, x="pclass", y="survived", palette="Blues_d", ax=ax[0,2]); ax[0,2].set_title("barplot")
sns.heatmap(df[["survived","pclass","age","fare"]].corr(), annot=True, cmap="coolwarm", ax=ax[1,0]); ax[1,0].set_title("heatmap")
sns.boxplot(data=df, x="pclass", y="age", palette="pastel", ax=ax[1,1]); ax[1,1].set_title("boxplot")
ax[1,2].axis("off")
plt.tight_layout(); plt.show()
```

Here's where people get stuck: they want to combine these into one figure, and it breaks. The key insight is that every seaborn call returns a matplotlib object. Once you know that, the two libraries become one tool.

```python
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Titanic EDA Dashboard", fontsize=16, fontweight="bold", y=1.01)

sns.barplot(data=df, x="pclass", y="survived", palette="Blues_d", ax=axes[0, 0])
axes[0, 0].set_title("Survival Rate by Class")
axes[0, 0].set_ylabel("Rate")

sns.histplot(df["age"].dropna(), kde=True, ax=axes[0, 1], color="steelblue")
axes[0, 1].set_title("Age Distribution")

sns.boxplot(data=df, x="pclass", y="fare", palette="pastel", ax=axes[1, 0])
axes[1, 0].set_title("Fare by Passenger Class")
axes[1, 0].set_ylabel("Fare (£)")

sns.barplot(data=df, x="sex", y="survived", palette="Set2", ax=axes[1, 1])
axes[1, 1].set_title("Survival Rate by Sex")

plt.tight_layout()
plt.show()
```

[SCREEN: 2×2 dashboard output — all four charts with consistent styling and shared suptitle]

Four charts. Consistent styling. A shared title. Under 25 lines. And when you look at this together, your eye sees what you'd miss chart by chart — survival drops hard from class one to three, and the male/female survival gap is enormous. One figure. Two insights that interact.

First time I put something like this together for a stakeholder meeting, it changed the whole dynamic. Before that I was going slide by slide, chart by chart, and I was doing all the connecting out loud. With the dashboard up, someone in the room pointed at the class breakdown and the sex breakdown at the same time and said — these two are related, aren't they? They made the connection themselves. I didn't have to lead them there. That's the difference between a chart and a dashboard.

[PAUSE]

Last thing: save it right. Default matplotlib saves at 72 DPI. Most presentation software renders at 150 to 300. Your chart gets stretched and fuzzy on a projector. Fix this at save time.

```python
fig.savefig(
    "titanic_eda_dashboard.png",
    dpi=300,
    bbox_inches="tight",
    facecolor="white",
)
```

`bbox_inches="tight"` prevents cropping. `facecolor="white"` locks the background even in dark-mode notebooks. For publication or printing, save as SVG — resolution independent, scales to any size.

Three chart details that separate good from bad: every numeric axis needs units — "Fare (£)", not "Fare". Color assignment must stay consistent — if survived is steelblue in chart one, it's steelblue everywhere, use a palette dict to enforce it. And bar charts always start at zero. Always. Matplotlib won't enforce this for you. Add `plt.ylim(0, 1)` explicitly.

These aren't design skills. They're intentions. And they're the difference between a chart that communicates and a chart that misleads.

[SCREEN: before/after comparison — default matplotlib vs styled dashboard]

```python
fig, (l, r) = plt.subplots(1, 2, figsize=(14, 5))
sns.reset_defaults()                                  # left = ugly default
l.hist(df["age"].dropna(), bins=30); l.set_title("Before — default")
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.2)
sns.histplot(df["age"].dropna(), kde=True, ax=r, color="steelblue"); r.set_title("After — styled")
plt.tight_layout(); plt.show()
```

Start with one notebook. Load a dataset you care about. Build all five chart types. Save at 300 DPI. Then ask: does someone who's never seen this data understand the key pattern within five seconds of looking? If not — the chart needs work, not the data.

Tutorial six is statistical testing with scipy and statsmodels. We'll take these patterns and start asking whether what we see is actually real.

If this series is useful, share it with one person who's learning Python right now — not bookmarking it, sharing it. That's what keeps this going. Follow along for tutorial six next week.

[ANIMATION: 5-second outro card — "Next: Statistical Testing with Scipy & Statsmodels (#6/10)"]