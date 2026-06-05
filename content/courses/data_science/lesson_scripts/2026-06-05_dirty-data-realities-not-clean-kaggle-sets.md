# Dirty Data Realities (Not Clean Kaggle Sets)
**Course: Data Science from the Inside: A Practitioner's Mindset — Lesson 2**

---

## COLD OPEN

The dataset looked fine.

That's the most dangerous sentence in data science. Four words that have buried careers, invalidated studies, and shipped models that made things worse than doing nothing.

"The dataset looked fine" — until row 400,000. Until the third week. Until a stakeholder said, "wait, that number doesn't match what we see on the ground."

And by then, you've already built a model on top of it.

---

## WHY THIS MATTERS

Let me tell you what most data science education gets wrong about data.

Every course — Kaggle, Coursera, whatever — starts with a dataset that already exists, is already clean, and fits neatly into a pandas DataFrame. You load it in two lines. You run `.describe()`. Everything looks reasonable. And then you get to the interesting part: the modelling.

So your brain starts to build a map of what data science feels like. And in that map, data is the boring setup. The model is the main event.

Now imagine you're six months into your first real job. Someone drops a CSV on you. Or an API connection. Or a database dump. And you load it up, run `.describe()`, and some columns are 40% null. One date column has three different formats in the same file. A column called `revenue` has negative values nobody can explain. And your manager says, "yeah, that's just how it comes — just clean it up."

You freeze. Because nobody taught you this part.

I want to fix that today. Not by handing you a checklist of cleaning steps — you can find those anywhere. But by changing *how you think about data* before you touch it.

Because the practitioner's mindset isn't "clean data, then model." It's: "data is guilty until proven innocent, and the burden of proof never fully lifts."

---

## TEACH

### Key Point 1: Real Data Is Missing, Wrong, and Late — Assume Nothing

Here's the first thing to internalize: every dataset you receive in a real job was produced by a system that was not built for you.

Think about it. When an e-commerce platform records a transaction, it's not thinking about your downstream model. When a hospital records a patient event, the system is built for billing, not for your readmission prediction. When a logistics company logs a delivery, it's for their ops dashboard, not for your churn analysis.

This means the data carries the fingerprints of whatever it was actually designed for. It has gaps where the original system didn't care to record something. It has errors where a human typed in a field that should have been a dropdown. It has inconsistencies where the same underlying reality got recorded five different ways across five different data entry clerks.

And then there's lateness. This one catches people off guard. Real pipelines have lag. A record that says "event at 10pm" might not land in your table until 2am. Sometimes it doesn't land for three days. Sometimes it gets corrected or updated after you already pulled it. Your training data might be a snapshot. Your production data is a river. These are not the same thing.

So when you open a new dataset, the professional posture is not curiosity — it's suspicion. Friendly suspicion. You're not trying to find problems to complain about. You're trying to understand what you're actually working with before you commit to it.

The question isn't "does this look okay?" The question is: "where would this dataset lie to me, and what's the cost of believing it?"

---

### Key Point 2: Cleaning Is Not Pre-Work — It Is Most of the Work

There's a phrase that floats around — "data scientists spend 80% of their time cleaning data." You've probably heard it. And your immediate reaction, if you're honest, is probably: that sounds terrible. Like wasting four-fifths of your day on janitorial work.

I used to think that too. I was wrong.

Cleaning is not what happens before the real work. Cleaning *is* the real work. And here's why that reframe matters.

When you're cleaning data, you are not just fixing formatting issues. You're building your understanding of what the data actually *measures*. Every null you investigate tells you something about the process that generated the data. Every outlier you examine forces you to ask: is this noise, or is this signal? Every inconsistency you trace back reveals an assumption someone made upstream that may or may not hold.

[B-ROLL: notebook with exploratory code running, terminal output visible]

The practitioner who rushes through cleaning misses all of that. They impute the nulls with a median, clip the outliers, standardize the formats, and move on to the model. And then they're surprised six weeks later when their model behaves strangely on a slice of data they didn't think to examine.

The practitioner who takes cleaning seriously ends up understanding the domain better than the stakeholders who handed them the data. Not because they're smarter — because they were forced to ask hard questions.

Here's a concrete habit: when you're cleaning, keep a living document. Every decision you make — "I dropped rows where X was null because those represent cancelled orders" — write it down. Because six months later, someone will ask you why your dataset has 90,000 rows when the source system shows 140,000. And if you didn't document it, you're digging through old notebooks trying to remember why.

Cleaning that's documented is analysis. Cleaning that isn't documented is technical debt.

---

### Key Point 3: Trust Nothing Until You Have Checked It Yourself

I don't mean this cynically. I mean it operationally.

When someone hands you data and says "it's all been cleaned" — great. Verify it anyway. Not because they're lying. Because cleaning is a subjective process. What they cleaned for their purpose may not be what your model needs. Their definition of an outlier may be different from yours. Their handling of nulls may introduce systematic bias you haven't accounted for.

When someone says "this column is the revenue per customer" — verify that too. Pull five rows. Open the source system if you can. Check whether the number you're seeing actually means what the label says. Aggregation logic in enterprise data warehouses is famously opaque. Columns get renamed. Metrics get redefined. The column called `revenue` might actually be `gross revenue before refunds and discounts` — or it might not. You should know which.

And when you run your own cleaning scripts — verify those too. Run `.value_counts()` after you think you've standardized a categorical column. Check that nulls dropped the way you expected. Confirm that your join didn't silently create duplicate rows.

This isn't paranoia. This is the scientific method applied to your own work. You form a hypothesis — "I think this data is now clean for my purpose" — and then you design small tests to try to falsify it.

[PERSONAL_INSERT: specific moment where trusting someone else's "clean" data burned you — what the column was, what they said it was, what it actually turned out to be]

The practitioners I've seen make the fewest errors are not the ones who are most careful. They're the ones who've been burned enough times that they've built verification into their muscle memory. It's automatic. Every assumption gets a check. Every check gets a note.

---

## STORY

[PERSONAL_STORY: The timestamp column that was three timezones stitched together.

Sketch of what to cover: You had a column labeled `event_timestamp`. It looked like a normal datetime column. You did your exploratory work, didn't notice anything unusual, and built a session-based feature on top of it — something like "time between events" or "events per hour."

The model trained fine. But when you looked at your feature distribution more carefully, there was this weird trimodal pattern. Sessions that should have been, say, 10 minutes apart were sometimes showing as 9 hours apart or 10 hours apart. 

You dug in. Turns out the timestamp column had been assembled from three different regional systems — one logging in IST, one in UTC, one in some other zone — and nobody had normalized it during the merge. The column was technically populated, no nulls, valid datetime format. It just silently represented three different realities stitched into one field.

Expand with the specific dataset, the specific feature, what you actually found, how long it took to catch, what you had to redo.]

---

## DO THIS NOW

Open the worksheet for this lesson.

You'll find a messy dataset — I've put real failure modes in there: missing values with a pattern, a column that claims to be one thing but isn't, a timestamp that behaves strangely, and at least one column you'll need to make a judgment call on.

Your job is not to clean it. Your job is to *document it*. Fill out the failure mode audit in the worksheet. For each problem you find, write: what you found, where you found it, what you think caused it, and what assumption you'd make if you were forced to proceed.

That last part — "what assumption you'd make if you were forced to proceed" — that's the practitioner's lens. You're not waiting for perfect data. You're making explicit, traceable decisions under imperfect conditions.

When you're done, you should have a document that another data scientist could read and immediately understand what they're working with. That's the standard.

---

## CLOSE

The dataset that "looks fine" is the one that will cost you the most.

---

**Post-writing flags:**

- `[PERSONAL_INSERT]` at Key Point 3 — needs a concrete story of trusting someone else's cleaned data and getting burned. A specific column name, a specific wrong assumption, the moment of discovery.
- `[PERSONAL_STORY]` — the three-timezone timestamp story. Expand with: actual dataset context (internal product? external source?), what feature was being built on top of it, how long it ran before the issue surfaced, what had to be redone.

**Suggested titles (3):**
1. *The Dataset That "Looked Fine"*
2. *Real Data Doesn't Come Clean: What Kaggle Never Taught You*
3. *Dirty Data Is the Job*

**Derivative angle:** Thread — "5 things I've found hiding in 'clean' datasets" — each tweet is one failure mode from the lesson.