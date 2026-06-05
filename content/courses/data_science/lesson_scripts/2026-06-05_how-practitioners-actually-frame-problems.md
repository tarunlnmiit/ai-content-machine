# COLD OPEN

You walk into a room. Someone hands you a brief. It says: "We need a model to predict which customers will churn."

Most data scientists read that and immediately start thinking about features. XGBoost vs. neural net. Train-test split. ROC curves.

And that's exactly where things go wrong.

Because that sentence — "predict which customers will churn" — is not a modelling question. It's a business anxiety dressed up as a technical request. And if you treat it like a modelling question from the start, you will build something technically impressive that solves the wrong problem.

This lesson is about what actually happens before you open a notebook.

---

# WHY THIS MATTERS

I want to talk to you specifically for a second.

If you're early in your career — maybe you've done some Kaggle, maybe you've built a classifier or two, maybe you've watched fifteen hours of ML tutorials — you probably feel like the job is about models. About algorithms. About making the accuracy number go up.

That feeling makes sense. That's what most courses teach. That's what most YouTube videos show. The dramatic moment where the model trains and the loss curve drops.

But here's what those courses don't show you: the meeting before the meeting. The conversation where you figure out whether you're even building the right thing. The moment where a senior practitioner asks one question that reframes the entire project.

That skill — problem framing — is the difference between a data scientist who gets things done and one who produces beautiful work that sits in a drawer.

And nobody teaches it. So that's what we're doing today.

---

# TEACH

## Key Point 1: The Business Ask Is Not the Modelling Question

Let's go back to that brief. "Predict which customers will churn."

The business ask is: we're losing customers and we don't know who's about to leave.

That's real. That's valid. But it is not the same as a modelling question.

A modelling question has a specific target, a specific prediction window, and a specific action attached to it. "Predict churn" has none of those. It's a symptom described as a solution.

Here's the exercise I want you to run on every brief you receive. Ask: "If this model is perfect — absolutely perfect — what happens next?"

If you can't answer that clearly, you don't have a modelling question yet.

For churn: if the model is perfect and it flags 500 customers as high-risk tomorrow morning — what does the company actually do with that list? Do they call them? Email them? Offer a discount? And who decides which of those 500 gets which intervention?

The moment you ask that question, the problem changes shape. Now you're not building a churn predictor. You're building a system that routes customers to specific retention actions. And that system has completely different requirements than a generic churn model.

This is what I mean when I say the business ask and the modelling question are different things. The business ask points at a pain. Your job is to translate that pain into something precise enough to model.

---

## Key Point 2: Define the Target Before You Touch a Model

Once you know what action your model is feeding, you can define your target variable properly. Not before.

This sounds obvious. It is not obvious in practice.

Here's why. Most data scientists define the target based on what's available in the data. Churn flag exists in the database? Great, that's your target. And then you spend weeks building a model on a label that was never designed for the decision you're trying to support.

The churn flag in most company databases means: this customer cancelled. Full stop. That's a historical fact. But the decision you're actually trying to support is: which customers are *worth* intervening with *now*, using *this* intervention, at *this* cost?

Those are different targets. One is about the past. One is about the future. And more importantly — one is connected to an action, and one is just a description.

Before you pull a single row of data, sit down and write this sentence:

*"I want to predict [target] among [population] in the next [time window] so that [decision-maker] can [specific action]."*

Fill in every blank. If you can't fill in a blank, that's not a data problem. That's a stakeholder conversation you haven't had yet. Go have it.

[PERSONAL_INSERT: short example of a project where you wrote out this sentence and discovered mid-sentence that you didn't know the time window — and what happened when you went back to the stakeholder]

---

## Key Point 3: Frame for the Decision, Not the Metric

This is the subtlest one. And probably the one that separates good data scientists from great ones.

Every model has a metric. Accuracy, precision, recall, AUC — pick your poison. And metrics are useful. They're how you know if your model is getting better or worse.

But a metric is not a decision criterion. And this confusion causes a specific, recurring failure mode in industry.

Here's what it looks like: you optimize your model for AUC because that's what data scientists optimize for. You get to 0.85. You're pleased. You present it. And then someone in finance asks: "What's the false positive cost?"

You hadn't thought about false positives the same way they had. Because to you, false positive rate was a model quality thing. To them, it's a budget thing. Every false positive is a retention offer sent to a customer who wasn't going to leave anyway. That costs money. Real money.

The frame for the decision is: what does it cost when my model is wrong, and in which direction?

That question completely reshapes which metric matters. Sometimes you need high precision because false positives are expensive. Sometimes you need high recall because missing a churner is catastrophic. The answer depends on the business context — and you can't know that from the data alone.

So here's the habit I want you to build: before you train anything, before you even split your data, write down the error cost asymmetry. What does a false positive cost? What does a false negative cost? Are they the same? Are they wildly different?

If they're wildly different — which they almost always are — you now know which metric to optimize for. And you'll be the person in the room who asked the question nobody else thought to ask.

---

# STORY

[PERSONAL_STORY: This is where you tell the churn project story in real detail. The shape of it: you were handed a churn modelling brief, you started the usual way, and somewhere in the process — whether it was a conversation with a stakeholder, a question someone asked in a review, or something you noticed in the data — you realized the real question wasn't "who will churn" but "what's the retention budget and who should get it." Walk through what that realization felt like, what changed when you reframed the problem, and what happened to the project as a result. Be specific — what company, what was the original brief, what question cracked it open. If you can share what the model looked like before and after the reframe, even better.]

The reason I'm telling you this story is not to make you feel like you need ten years of experience before you can think this way. You don't. The skill isn't experience. It's a habit of asking one question before you start: *What decision does this model need to support?*

That's it. That's the whole unlock.

---

# DO THIS NOW

Open the worksheet for this lesson. There's a template called the Problem Frame Canvas. It has five rows:

- Business ask — what they said they wanted
- Decision — what action this model will feed
- Target — what you're actually predicting, defined precisely
- Population — who this applies to
- Error cost asymmetry — what a wrong prediction costs, and in which direction

Take a project you've already built — something from a previous course, a Kaggle dataset, anything — and fill in every row. If you've never thought about it this way, some rows will be hard to fill. That discomfort is useful. It's telling you where the assumptions were buried.

Bring your completed canvas to the community forum. We'll look at real examples together.

---

# CLOSE

The model is the easy part. The question before the model — that's the work.