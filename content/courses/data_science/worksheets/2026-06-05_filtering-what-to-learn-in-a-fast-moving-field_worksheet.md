# Filtering what to learn in a fast-moving field — Worksheet

**Objective:** Build your own personal filter — a clear list of what to learn next and what to deliberately skip — based on your actual situation, not hype.

---

## The Scenario

You open Twitter on a Monday morning. Three new frameworks dropped last week. A YouTube video says "LangChain is dead." Someone else says "every DS must know Rust." Your college friend just started a "Kafka for beginners" course. You have 45 minutes free each evening.

This is the real environment. The skill is not knowing everything — it is knowing *what to learn when*, and being able to defend that choice.

---

## Task 1 — Understand Your Baseline (Easy)

Before filtering anything, you need to know where you stand.

Fill in the table below honestly. No aspirational answers — write what is *actually true today*.

| Dimension | Your Answer |
|---|---|
| Current role / goal (student, fresher, switching from X, etc.) | `____` |
| One project you want to finish in the next 3 months | `____` |
| Time available for learning per week (hours, realistic) | `____` |
| One tool or concept you already know reasonably well | `____` |
| One thing you started learning but dropped — and why | `____` |

**Why this matters:** Every filter you build later will use *your* context as the input, not a generic beginner profile.

---

## Task 2 — Score a Topic (Code Task)

Below is a simple scoring function. It takes a topic and three attributes, and returns a priority score.

```python
def topic_priority(topic_name, job_demand, project_fit, learning_curve):
    """
    job_demand   : 1–5 (1 = niche/rare in JDs, 5 = appears in most)
    project_fit  : 1–5 (1 = useless for your 3-month project, 5 = core to it)
    learning_curve: 1–5 (1 = takes months to get useful output, 5 = useful within days)
    """
    score = (job_demand * 0.4) + (project_fit * 0.4) + (learning_curve * 0.2)
    return round(score, 2)

# Example
print(topic_priority("Pandas", job_demand=5, project_fit=5, learning_curve=4))
```

**2a.** Run this function for the following topics. Use your *honest judgment* for the ratings — not what sounds impressive.

| Topic | job_demand (1–5) | project_fit (1–5) | learning_curve (1–5) | Score |
|---|---|---|---|---|
| Pandas | | | | |
| Apache Spark | | | | |
| Prompt engineering | | | | |
| Statistics (hypothesis testing) | | | | |

Write your scores here after running the code:

```
Pandas score:              ____
Apache Spark score:        ____
Prompt engineering score:  ____
Statistics score:          ____
```

**2b.** Which topic scored lowest? Write one sentence explaining whether that score *feels right* to you — or whether you disagree with it and why.

```
____________________________________________________________________
____________________________________________________________________
```

---

## Task 3 — Add a Hype Penalty (Code Task — Medium)

The function above ignores one important thing: whether something is being pushed by the internet right now versus actually needed. Hot topics get overcrowded fast and the hype often disappears before you finish learning them.

Modify the function to include a `hype_level` parameter (1 = barely mentioned, 5 = every newsletter has a tutorial). Higher hype should *reduce* the final score slightly.

```python
def topic_priority_v2(topic_name, job_demand, project_fit, learning_curve, hype_level):
    # YOUR CODE HERE
    # Suggestion: subtract a fraction of hype_level from the final score
    # Make sure the score still stays between 0 and 5
    pass

# Test it
print(topic_priority_v2("LLM Fine-tuning", job_demand=3, project_fit=2, learning_curve=1, hype_level=5))
print(topic_priority_v2("SQL window functions", job_demand=5, project_fit=4, learning_curve=3, hype_level=1))
```

Write your implementation below, then copy it to your editor and run it:

```python
def topic_priority_v2(topic_name, job_demand, project_fit, learning_curve, hype_level):
    _______________________________________________
    _______________________________________________
    _______________________________________________
```

**What did you choose as the hype penalty weight? Why?**

```
____________________________________________________________________
```

---

## Task 4 — Build Your Personal Filter List (Applied)

Take 5 topics you are genuinely curious about right now — things you have bookmarked, half-started, or seen recommended. Run them through your `topic_priority_v2` function.

List them here first:

1. `____`
2. `____`
3. `____`
4. `____`
5. `____`

Now fill in this table after running your code:

| Topic | Score | Decision |
|---|---|---|
| | | Learn / Delay / Skip |
| | | Learn / Delay / Skip |
| | | Learn / Delay / Skip |
| | | Learn / Delay / Skip |
| | | Learn / Delay / Skip |

**"Delay" means:** you can see yourself needing this in 6+ months. Not ignoring it permanently — parking it consciously.

---

## Task 5 — Write Your Filter Rules (Applied)

The scoring function captures numbers. But you also carry qualitative rules in your head — things like "I never start a course longer than 6 hours" or "I only learn things I can practice on real data the same week."

Write 3 personal filter rules that you will actually follow. Be specific. Vague rules get ignored.

**Rule 1:**
```
If _________________________ then I will not start learning this yet because _________________________.
```

**Rule 2:**
```
If _________________________ then I will prioritize this even if the score is moderate, because _________________________.
```

**Rule 3:**
```
If a topic has been on my list for more than _______ weeks without me touching it, I will _________________________.
```

---

## Self-Check

Review your work against these markers. Be honest — this is not graded by anyone else.

| Check | Yes / Needs work |
|---|---|
| My Task 1 answers reflect my *current* situation, not what I wish were true | |
| My scores in Task 2 differ from topic to topic — not all 4s and 5s | |
| My `topic_priority_v2` actually penalizes high hype (tested with two examples) | |
| My Task 4 list contains at least one "Skip" or "Delay" — not everything is "Learn" | |
| My Task 5 rules are specific enough that a stranger could follow them | |

**What a good filter looks like:**
- It produces different decisions for different topics. If everything scores "Learn," the filter is not working.
- It reflects *time constraints*, not just interest. High interest + zero time = still a delay.
- It is revisited every 4–6 weeks as your project and role context changes.

**One thing you will stop learning (or delay starting) based on this worksheet:**

```
____________________________________________________________________
```

**One thing you will start or continue, with a clear reason:**

```
____________________________________________________________________
```