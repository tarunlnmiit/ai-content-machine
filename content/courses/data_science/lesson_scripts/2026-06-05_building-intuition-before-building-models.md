# COLD OPEN

Most people build a model first and look at the data after.

That's backwards. And I've seen it cost teams months.

---

# WHY THIS MATTERS

Here's something that took me longer to learn than it should have.

There's a version of data science where you spend two weeks engineering features, tuning hyperparameters, stacking models — and then someone asks: "But what does the data actually look like?" And you realize you never properly answered that question. You were so eager to get to the model that you skipped the part where you understand what you're modelling.

This isn't a beginner mistake, by the way. It happens to people with years of experience, because the culture of data science rewards the model. The model is the deliverable. The model is what goes into the presentation. The exploratory work, the baseline, the sanity checks — those feel like warming up. Like they don't count.

They count. They count more than almost anything else you'll do.

If you're early in your career and you're trying to move fast, to prove you can ship something technical — this lesson is asking you to slow down one step earlier than you're used to. Not permanently. Just long enough to actually understand what you're working with.

That's the discipline. And it will separate you from the majority of people who learn the same algorithms you do.

---

# TEACH

## Key Point 1: Look Before You Fit — Plot It, Eyeball It, Question It

Before you split a dataset. Before you encode a categorical. Before you touch `model.fit()` — look at your data.

Not look as in `df.head()`. Look as in: understand the shape of what you're dealing with.

What does the distribution of your target variable look like? If you're predicting a continuous value, is it symmetric? Heavily skewed? Are there gaps? If you're doing classification, how imbalanced are your classes — and not in a rough sense, in an actual number sense. Ten percent positive class is very different from one percent positive class, and both require completely different approaches.

What are the relationships between your features and your target? Not correlations — those come later. Just eyeballing. If you plot your target variable against each feature, do obvious patterns appear? Do some features seem to have no relationship at all? Are there features that have a near-perfect relationship — which should make you suspicious, not excited?

What does the data look like at the extremes? The outliers aren't always errors. Sometimes they're the most important observations in the dataset. Sometimes they're test accounts that slipped into your training data. You can't know which until you look.

Here's a concrete habit: before any model work, write a single page of observations about the dataset. Not code. Not stats. Observations in plain language.

*"The target variable is heavily right-skewed. Most values cluster below 50, but there are some extreme values above 500 that are probably genuine — they correspond to the enterprise customer segment."*

That kind of observation, written before you model, will save you hours of post-hoc debugging later. Because when your model behaves strangely in production, you'll have a reference point. You'll know what the data looked like before you touched it.

`[PERSONAL_INSERT: a specific time when plotting the data first caught something — a cluster you'd have missed, a target variable distribution that changed how you built the whole pipeline — describe what you saw and what it changed]`

---

## Key Point 2: Baselines First — The Model Must Beat Something

Every model needs to beat a baseline. Not philosophically — practically.

A baseline is the dumbest possible prediction you could make. If you're predicting house prices: what if you just predicted the mean price for every house? If you're classifying customer churn: what if you just predicted "no churn" for every customer? If you're forecasting daily sales: what if you predicted last week's same-day number?

These sound like jokes. They are not jokes. These are the thing your model has to beat before it earns the right to be called useful.

And you'd be surprised how often a real, carefully tuned model barely beats the baseline. Or doesn't beat it at all. And when that happens, you need to know — because deploying a sophisticated model that performs the same as "guess the mean" is not a neutral decision. It's worse: it's expensive, hard to maintain, and opaque.

The baseline does several things for you.

First, it calibrates your expectations. If your baseline gets 65% accuracy and your best model gets 67%, something is probably wrong — either with the data, the problem framing, or your approach. That two-point gap should make you stop and think, not ship.

Second, it gives stakeholders a reference point. When you present results and say "the model achieves 78% precision," that number means nothing without context. When you say "the baseline was 52% and the model reaches 78%," now there's a story. The model is doing real work.

Third — and this one is subtle — calculating the baseline forces you to understand the problem structure. To compute "predict the majority class" you have to know your class distribution. To compute "predict the historical mean" you have to understand what the data looked like before any modelling. You have to engage with the problem, not just the algorithm.

The baseline is not a throwaway step. It's your ground truth for whether the model is earning its keep.

---

## Key Point 3: Know What Good Looks Like Before You Start

This is the one that most people skip, and it's the one that creates the most waste.

What does "good" mean for this problem?

Not in the abstract. Not "as accurate as possible." Concretely: what metric, what threshold, what level of performance would make this model actually useful in production?

This has to be decided before you start. Not after you see what you can achieve, not after you've tried three architectures and you're anchoring on the best result. Before.

Because if you decide what good looks like after you see the results, you'll always find a way to convince yourself that what you built is good enough. Humans are very good at this. We adjust our definition of success to match our outcomes. It's a natural, unconscious thing — and in data science, it produces models that look fine on paper and fail in deployment.

The way to set this threshold properly is to connect it to the decision the model is feeding. We did this in Lesson 1 — if you know what action your model supports, you can work backwards to what performance level makes that action sensible.

Let's say you're building a model that flags customers for a manual review process. You have enough capacity to review 100 customers per week. Your model generates a ranked list, and the team works through the top 100.

What precision do you need? You can calculate it. If your team reviews 100 cases and at least 30 need to be actual positive cases for the intervention to be worth the cost — you need at least 30% precision in the top 100. That's your threshold. That's what "good" looks like.

Now you have something to aim at. And you have something to test against before you call the model done.

`[PERSONAL_INSERT: a specific project where you either set this threshold upfront and it protected you — or didn't set it and paid the price when someone asked "but is this actually good enough?" in a review or demo. The second version is more instructive if you have it]`

---

# STORY

`[PERSONAL_STORY: This is the groupby-and-mean story. Tell it like this: you were working on a forecasting or prediction problem — some project where the expectation was that you'd build something sophisticated. You built it. You had a gradient-boosted model, properly tuned, cross-validated. And then at some point in the process — maybe before presenting, maybe after a stakeholder pushed back — you calculated what happened if you just did a groupby and took the mean. And it was within spitting distance of your model. Maybe it was actually better. Tell us what that felt like. What did it tell you about the data? About the problem? Did you end up shipping the simple version? What did that conversation with the stakeholder or team look like? If there was a reason the simpler model was better — class imbalance, too much noise in the data, a structural reason — explain that too. The point of the story isn't "simple is always better." The point is: you only knew the model was unnecessary because you had the baseline to compare against. If you'd never calculated the groupby-mean, you'd have shipped the gradient-boosted model and felt good about it.]`

The lesson here isn't that complex models are bad. They're not. But complexity has to earn its place. And the only way to know if it's earning its place is to know what you're comparing it to.

That comparison — baseline to model — is the work. Everything else is optimisation.

---

# DO THIS NOW

Open the worksheet for this lesson. You'll find three exercises.

The first: pick any dataset you've worked with before — Kaggle, a personal project, anything — and spend fifteen minutes only looking at it. No modelling. Write ten observations in plain language about what you see. What's the target distribution? What relationships are obvious before you even compute anything? What's weird or unexpected?

The second: calculate the simplest possible baseline for that dataset. Mean prediction, majority class, last known value — whatever fits. Write down the number.

The third: if this were a real production problem, what performance level would make the model worth deploying? Work backwards from a hypothetical use case. What decision would the model feed? What threshold makes that decision sensible?

Bring all three to the forum. The baselines especially — I want to see what people find when they actually calculate them.

---

# CLOSE

The model you didn't need to build is always the most expensive one.

---

**Post-writing notes:**

**`[PERSONAL_INSERT]` guidance:**
1. Key Point 1 insert — needs a story where plotting first revealed something structural: a bimodal distribution, a data leak, a cluster that changed the whole approach. The more specific the "what you saw" the better.
2. Key Point 3 insert — the "didn't set the threshold and paid for it" version is stronger here. A stakeholder or manager asking "but is this good enough?" with no pre-agreed answer in the room is the exact pain point this audience will recognise.

**`[PERSONAL_STORY]` guidance:**
- The groupby-mean story is the anchor of this lesson. The key beat is: you built the complex thing, then checked the simple thing, and the gap was embarrassing. The story should name the real project context (even loosely), show the emotional beat of seeing that comparison, and land on "I only knew because I checked."

**Suggested titles:**
1. *Before the Model: The Habit That Separates Good Data Scientists from Great Ones*
2. *Why I Always Start With a Dumb Prediction*
3. *The Baseline Problem: What Nobody Teaches You About Building Models*

**Derivative angle:**
Thread: "3 things to do before you train any model" — tweet 1 anchors on the cold open line, tweets 2–4 are one-sentence versions of each key point, final tweet is the groupby-mean story as a 2-sentence anecdote. Strong engagement hook for the DS audience.