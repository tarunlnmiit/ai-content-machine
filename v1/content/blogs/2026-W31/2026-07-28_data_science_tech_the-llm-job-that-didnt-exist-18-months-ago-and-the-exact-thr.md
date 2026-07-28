# A Junior Beat a 10-Year ML Veteran for This Job — Because of One Question He Asked

*The title didn't exist 18 months ago. The three skills that fill it aren't the ones you're studying.*

Eighteen months ago, my friend in Bangalore was a "Senior Data Scientist" building churn models in scikit-learn. Late in 2024, her own team opened a req for an **LLM Application Engineer** — and the job description didn't mention a single thing her old title was built on. No supervised learning framing, no AUC to argue about in a review. The hard part had quietly moved from *building the model* to *building everything around a model you rent by the token.*

If you're a working data scientist, analyst, or ML engineer, that shift is the most important thing happening to your job right now, and the roles are filling before most people notice the title. Her old work was framing a business question, cleaning data, and shipping a model. The new req asked for three things the old one never had: designing evals and guardrails for outputs you can't score with a single accuracy number, wiring retrieval and tools around a model you don't train, and writing the orchestration — prompts, context windows, fallbacks — as actual production code, not notebooks.

![The hard part moved from building the model to building everything around one you rent by the token.](/content/blogs/2026-W31/2026-07-28_data_science_tech_the-llm-job-that-didnt-exist-18-months-ago-and-the-exact-thr_images/01_context_data-scientist-reviewing-code-on-laptop.jpg)
*The hard part moved from building the model to building everything around one you rent by the token. — Photo by [Jakub Zerdzicki](https://www.pexels.com/photo/close-up-of-programmer-typing-code-on-laptop-36496927/) on Pexels*

Here are the three skills that get people hired — and, for each, the specific artifact that makes a hiring manager stop scrolling.

**1. Eval harness design.** The proof isn't a claim, it's a repo. Show a golden dataset you built by hand — say 200 labeled cases, with the disagreements between you and a second annotator resolved and documented — plus the offline/online gap it caught before a release. That artifact proves you understand that a model's "vibes-good" and "actually-good" are different things. Anyone can eyeball a few outputs and call it a day. Almost nobody bothers to prove it works, and that gap is exactly where you become the obvious hire.

**2. Retrieval architecture.** The answer that stops a hiring manager is a number with an ablation behind it: "chunking by semantic boundary beat fixed-token chunking by 14 points on my eval set, and here's the ablation." Not "I used Pinecone." Anyone can `pip install` a vector DB; few can tell you *why* their recall moved.

**3. Agent orchestration under cost and latency budgets.** The proof is a diagram of an agent you actually shipped, with the failure modes annotated — where it retries, where it falls back to a cheaper model, what the p95 latency and per-run token cost are. Because in production the interesting question was never "can the agent do it." It was "can it do it for 4 cents in under 3 seconds without looping forever."

The through-line across all three: bring receipts, not vocabulary. The candidate who says "I built a RAG system" and the one who says "I ran the ablation, here's the number" are applying for different jobs.

**Now the skill to drop: fine-tuning.** People treat it as the deep-end skill that separates real engineers from prompt jockeys, so they burn weeks on LoRA configs and learning-rate schedules for a problem a clean prompt and good retrieval would have solved in an afternoon. I lost most of a month early on trying to fine-tune a model to classify support tickets into our internal taxonomy — collecting data, curating labels, running eval sweeps — before I tried putting the taxonomy and six examples in the context window. Better accuracy, same day. The thing that matters isn't teaching the model new weights; it's teaching *yourself* to shape the problem. Fine-tuning is the last 5% you reach for only after you've proven clean context and tight retrieval aren't enough — which, for most business problems, they are.

I watched this decide a hire. We were filling an "LLM systems" role, down to two candidates. On paper the senior one won easily — a decade of ML, papers, all of it. I asked both to fix a RAG pipeline hallucinating on edge cases. He reached straight for fine-tuning and a bigger model. The junior guy asked to see the eval set first, found we didn't have one, and built fifteen adversarial test cases before touching a single prompt. That was it. He could measure whether a change helped, he wrote prompts like he was debugging a system instead of wishing at it, and he knew when the answer was "this isn't a model problem, it's a retrieval problem." The senior candidate knew transformers cold and still couldn't tell me if his fix worked. In this job, if you can't prove the thing got better, you don't have a fix — you have a vibe.

Here's the number that makes all of this concrete. Our RAG support-bot's retrieval hit-rate sat at 61% — nearly 4 in 10 answers built on chunks that didn't contain the answer, and the model confidently filled the gap anyway. Everyone assumed we needed a better embedding model. The real culprit was chunk size. We'd split on a fixed 512 tokens, which cut tables and multi-step instructions in half, so the relevant sentence and its context landed in two different chunks — and neither alone scored high enough to get retrieved. Structure-aware splitting (keep a table, a numbered list, a full section intact) plus a rerank pass over the top 20 pushed hit-rate to 89%, and hallucination on the eval set dropped from 22% to 7% without touching the prompt. The number I fought hardest for was the rerank latency budget: it added 340ms per query, and I had to show the product team the before/after evals to win the argument that 340ms of correctness beats an instant wrong answer.

If you have a free weekend, build the one project that shows all three at once. Pick a real task from your job — "read our messiest support tickets and route them, with a reason for each call" — wrap it in an eval harness that scores itself against 50 examples you labeled by hand, and ship it as a running thing with a README, not a notebook that only runs on your laptop.

"Done" looks like a public repo where someone clones it, runs one command, and watches it score itself:

```python
# route.py — the whole point is the last two lines
import json

def route_ticket(ticket: str) -> str:
    """Ask the LLM to classify + explain. Swap in your client of choice."""
    prompt = f"Route this ticket to one of [billing, bug, feature, other].\n" \
             f"Return JSON: {{'label': ..., 'reason': ...}}.\n\nTicket: {ticket}"
    return call_llm(prompt)  # your Anthropic/OpenAI/local call here

def evaluate(gold_path: str = "gold.jsonl") -> None:
    cases = [json.loads(line) for line in open(gold_path)]
    hits = 0
    for c in cases:
        pred = json.loads(route_ticket(c["ticket"]))
        hits += pred["label"] == c["label"]
    acc = hits / len(cases)
    print(f"routed {len(cases)} tickets, {acc:.0%} match to hand labels")

if __name__ == "__main__":
    evaluate()  # the line a hiring manager actually reads
```

That final print line — "routes 50 tickets, 86% match to my hand labels, here's the confusion on the 14% it missed" — is the whole interview. A candidate who reports their own error rate has already proven they think like the job needs, before I've written a single question. The counterintuitive part is that the eval set is worth more than the agent. Anyone can prompt an LLM this weekend. Almost nobody proves it works.

Want the companion worksheet — the golden-dataset template and the eval checklist I use to build these repos? Grab it free when you join my data science list, and I'll send the next teardown straight to your inbox.

<!-- Medium tags: Machine Learning, Data Science, Artificial Intelligence, Careers, LLM -->
<!-- Target keyphrase: LLM Application Engineer -->
<!-- SEO title: LLM Application Engineer: 3 Skills to Get Hired -->
<!-- SEO description: The 3 skills that get you hired as an LLM Application Engineer in 2026 — eval harnesses, RAG retrieval, agent orchestration — plus a weekend project to prove them. -->