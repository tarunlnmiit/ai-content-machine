## COLD OPEN

The day I joined my first real data team, I opened the repo and felt stupid.

Not because the code was advanced. Because I couldn't tell what anything *did*. Files named `final_v3_USE_THIS.py`. Functions with no docstrings, no tests, three global variables at the top. A model training script that imported a module that didn't exist anymore.

And somewhere in that mess was the thing the whole business ran on.

That was the moment I realized: school taught me to build things alone, from scratch, in a clean environment. Real work is the opposite of that.

---

## WHY THIS MATTERS

Here's something nobody tells you when you're learning data science online.

You will spend maybe 20% of your time doing what YouTube tutorials show you — loading data, building models, trying things. The other 80%? Reading code someone else wrote. Submitting your work for review and getting comments back. Debugging something that worked on your machine but fails in production. Waiting for a deployment. Writing a pull request description.

If you've only trained for the 20%, the 80% is going to feel like you're failing. You're not failing. You were just never taught this part.

And for anyone here who wants to work at a serious company — Indian or international — this is the difference between the candidate who gets hired and the one who gets told "strong skills, but not a fit for the team."

---

## TEACH

### Key Point 1: The notebook is for thinking. Production is for shipping.

Jupyter notebooks are one of the best thinking tools ever made for data work. You can try something, see the result, try something else, draw a chart, go back three cells, change your mind. That exploratory loop is genuinely powerful.

But a notebook is a conversation with yourself. It has hidden state — cells run out of order, variables that got reassigned four steps ago, a dataframe that only exists because you loaded it manually before running anything else. None of that survives a handoff.

When your exploration becomes something real — a feature pipeline, a model inference function, a data validation check — you have to translate it. Pull the logic into a proper Python function. Write a docstring. Give it inputs and outputs that are explicit. Make it something another person can run without asking you three questions first.

The skill isn't choosing notebooks *or* clean code. It's knowing when to switch. Explore in the notebook. Ship the function.

`[PERSONAL_INSERT: moment when you first had to translate a messy notebook into something the team could use — what was the hardest part of that translation]`

---

### Key Point 2: Git, reviews, and reading code ARE the job

Let me be direct: if you are not comfortable with Git beyond `add`, `commit`, `push`, you have a gap that will cost you in your first month at any serious company.

Git is not just version control. In a team, it's communication. A commit message tells your colleague *why* something changed, not just what. A pull request is a proposal, not just a delivery. The review comments on that PR are free mentorship from someone who knows the codebase better than you.

Here's what actually happens on a data team day-to-day. Someone makes a change to the feature pipeline. Someone else reviews it — checks the logic, checks for edge cases, maybe runs it. Comments go back. The author responds. The PR gets merged or revised.

If you treat code review as a bureaucratic hoop, you'll miss what it actually is: the fastest way to absorb how experienced people think about the problem.

And reading other people's code — which you will do constantly — is a skill that only improves by doing it. Start with one function. Understand what it takes as input, what it returns, what could go wrong. Don't just skim. Read it the way you'd read a short story: with attention.

`[PERSONAL_INSERT: a specific code review you received early in your career — a comment that stung at first but turned out to be exactly right]`

---

### Key Point 3: The team's code outlives your cleverness

There is a specific kind of trap that catches technically strong people early in their careers. It goes like this.

You see a problem. You know a clever solution — maybe it uses a decorator, a generator expression, some elegant pattern you learned recently. You implement it. It works beautifully. You're proud of it.

Six months later, a colleague needs to modify that function. They spend four hours trying to understand what it does. They eventually rewrite it in something simpler. Your clever version is gone.

Code in a team context has one job: be understood by the next person. That person might be your manager. It might be a new hire who joined last week. It might be you, eight months from now, at 11pm trying to fix a production issue.

Clarity is not a compromise. It's the point.

The data scientists who become senior fast are not usually the ones who write the most sophisticated code. They're the ones whose code *other people can work with*. That's the actual moat.

---

## STORY

`[PERSONAL_STORY: Tell the story of the brilliant notebook vs the modest function. A specific project where you built something technically impressive in a notebook — the right setup, the analysis, the model — and then either couldn't reproduce it yourself a month later, or handed it to someone and it completely fell apart. Contrast it with a simple, almost boring function you wrote for the same team that still gets used. What made the simple one survive? What does that tell you about what "good work" actually means in a professional context?]`

The punchline I want to land here is this: **nobody is using the impressive thing. Everyone is using the boring thing.**

Not because the team didn't appreciate good work. Because the boring thing was *for* the team. The impressive thing was for me.

---

## DO THIS NOW

Open the worksheet for this lesson. There are two exercises.

First: take any analysis you've built in a notebook recently — doesn't matter what it does — and pull one logical chunk of it into a standalone Python function. Give it a proper name. Write three lines explaining what it does, what it takes, what it returns. Then ask yourself: could someone who has never seen your notebook run this function without asking you anything? If no, fix it until yes.

Second: if you don't already have a GitHub account with at least one public repo, create one today and push that function. It doesn't need to be impressive. It needs to exist. Your professional reputation starts somewhere, and "I have a GitHub" is better than "I have some notebooks on my laptop."

---

## CLOSE

The code you write alone, in a notebook, with nobody watching — that's practice.

The code you write knowing someone else has to read it, run it, and build on it — that's the job.

---

Script saved at `content/courses/data_science/lesson_scripts/2026-06-05_working-in-a-real-codebase-and-team.md`. Three `[PERSONAL_INSERT]` spots + one `[PERSONAL_STORY]` block need your real detail. No regen needed unless you want structural changes.