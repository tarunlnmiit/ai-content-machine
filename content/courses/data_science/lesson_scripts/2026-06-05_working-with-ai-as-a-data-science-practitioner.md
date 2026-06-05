## COLD OPEN

Here's something nobody told me when AI tools got good enough to actually use at work: the danger isn't that they'll get things wrong and you'll notice. The danger is that they'll get things wrong and you won't.

---

## WHY THIS MATTERS

If you're learning data science right now, you're doing it at the exact moment the job is changing shape.

Two years ago, companies were hiring for people who could write pandas code fast. Today, everyone has a tool that writes pandas code. So if that's your whole pitch — "I can clean data and build models" — you are competing with a system that doesn't sleep, doesn't ask for a salary, and has read more Stack Overflow than you ever will.

I'm not saying this to scare you. I'm saying it because the flip side is real: if you understand what AI actually can and cannot do, you become the person who makes AI useful. And that person — right now — is genuinely rare.

The companies I talk to aren't struggling to find people who can prompt an LLM. They're struggling to find people who can tell when the LLM produced something that *looks* right but is quietly broken. That gap is your opportunity.

---

## TEACH

### Key Point 1: AI Is a Fast Junior Analyst

Let me give you a mental model that I wish I'd had earlier.

Think about the best junior analyst you could imagine. Fresh out of college, sharp, eager, fast. You give them a task at 9pm and by 9am they've turned it around. Beautiful charts, clean code, clear summary.

But — and this is the thing — they haven't been in the industry long enough to know what questions to *not* answer yet. They haven't built the instinct for "wait, that assumption is shaky." They haven't sat in the room where the business decision got made, so they don't know why this metric matters more than that one. They're doing exactly what you asked. Whether you asked the right thing? That's your job to figure out.

AI tools today are that junior analyst, except faster and more confident. The confidence is what makes them dangerous. A junior analyst who's unsure will say "I think this is right, but can you check?" AI doesn't do that. It gives you a polished answer in the same tone whether it's correct or whether it's made something up entirely.

So when you're using AI on a real project — and you should be, it's genuinely useful — your job is to be the senior person in that relationship. You're reviewing the work. You're asking: does this match what I know about the data? Does this answer the question I actually needed answered? Is there an assumption buried in here I didn't notice?

That's not extra work. That's the core of the job.

### Key Point 2: Framing and Judgment Don't Automate

There's a clean line you can draw between what AI does well and what it doesn't.

AI is excellent at the *how*. Given a clear task — clean this dataset, write a query that does X, explain what this error means, summarize these results — it's fast, it's often right, and it saves you hours.

What it cannot do is the *what* and the *should-we*.

The *what* is: what question are we actually trying to answer? That requires understanding the business context, knowing what decisions depend on this analysis, understanding what data you actually have versus what data you wish you had. AI has none of that context unless you give it. And even then, it can only work with what you've described — it can't notice the thing you forgot to mention.

The *should-we* is even harder. It's the judgment call. Should we build a model to predict this outcome, or is the outcome itself the wrong thing to be optimizing for? Should we report this pattern we found, or is it a statistical artifact? Should we trust this training data, given where it came from?

These questions require experience, domain knowledge, and sometimes the courage to push back on what a stakeholder wants to hear. A language model cannot do that. It will give you an answer, but it will give you the answer that sounds reasonable given what you typed — not the answer that comes from understanding the full situation.

This is why data scientists aren't going away. The framing layer is harder than it looks, and it's entirely human.

### Key Point 3: Supervising AI Is the 2026 Skill

I want to be specific about what "supervising AI well" actually means in practice, because it's easy to nod along to the phrase without knowing what to do with it.

It means three things.

First: you can catch errors the AI doesn't flag. You read the output with a critical eye. You check whether the logic is consistent. You look at the numbers and ask: does this make intuitive sense given what I know about this domain?

Second: you can frame tasks precisely enough that the AI has a real chance of getting it right. This is harder than it sounds. Vague prompts produce vague work. The person who knows how to decompose a messy problem into crisp subtasks — and then sequence those subtasks intelligently — is doing something that requires real understanding of both the problem and the tool.

Third: you know when not to use it. There are tasks where AI will confidently produce something plausible that is wrong in a way you might not catch on a quick read. Knowing which tasks those are — and choosing to do them manually or with extra verification — is a judgment call that only comes with experience.

Put those three things together and you have something that's genuinely hard to automate: the expert who knows how to use the tool without being fooled by it.

---

## STORY

[PERSONAL_STORY: This is where you share the specific incident — the AI analysis that was clean, confident, and answering the wrong question. Walk through what the task was, what you asked AI to do, what it produced, how it looked on the surface, and the moment you realized the underlying question was off. What was the actual cost of that near-miss — to the project, to your credibility, to the decision that almost got made? End with what you now do differently before you hand any AI-generated analysis to a stakeholder.]

The reason I tell that story is because it's the version that happened to me when I was already a senior practitioner. I knew what I was doing. I'd been working with data for years. And I still nearly shipped something that would have been confidently, quietly wrong.

If that can happen to me, it can happen to you. The defense isn't to use AI less. The defense is to build the habit of verifying before trusting.

---

## DO THIS NOW

Open the worksheet for this lesson. There's a simple two-column exercise: on the left, a task description. On the right, two columns — one for what you'd hand to AI, one for what you'd personally verify afterward.

Go through the five tasks listed. For each one, decide: what exactly would I ask AI to do? And what would I check — specifically, not generally — before considering the output trustworthy?

The goal isn't to fill in the boxes perfectly. The goal is to build the habit of thinking about AI outputs as inputs to your judgment, not as final answers.

If you want to go further: pick a real analysis you've done before and redo the framing step. What question were you actually answering? Was it the right question? Would AI have caught if it wasn't?

---

## CLOSE

The people who get left behind by AI aren't the ones who refused to use it. They're the ones who used it without knowing what to look for.