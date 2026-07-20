---
title: "I Stopped Googling Travel Guides. I Interrogated an AI Instead - Here's the Exact Prompt That Worked"
type: blog
niche: data_science_tech
date: 2026-06-16
week: 2026-W25
slug: ai-prompt-anatomy-travel
tags: [content/blog, niche/data_science_tech, week/2026-W25]
---
# I Stopped Googling Travel Guides. I Interrogated an AI Instead - Here's the Exact Prompt That Worked

Most people ask ChatGPT questions. I gave it a job. Here's the 5-part prompt anatomy that turned AI into my personal Parisian historian.

I had Paris on my bucket list for six years.
First, COVID. Then work. Then life doing what life does - filling every gap with something urgent and leaving the beautiful things for "later."

When later finally arrived in 2025, I made a decision: no more hours lost in travel blogs with 47 tabs open, no more Reddit rabbit holes, no more contradicting TripAdvisor reviews written by people who think the Eiffel Tower is "underrated."

I'm an AI Engineer. I work with large language models every day. So I did what felt natural - I didn't ask ChatGPT for help. I interrogated it.

And it whispered Paris's secrets back to me like a historian who actually lives there.

Here's the exact prompt anatomy I used, broken into five surgical steps.

---

## The Problem With How Most People Prompt AI

Most people type something like: "Best things to do in Paris?"

And they get the Eiffel Tower. The Louvre. Sacré-Cœur. The same ten things that appear on every listicle written since 2009.

The model isn't failing you. The prompt is.

LLMs are prediction engines - they give you the most statistically likely answer to your input. If your input is vague, you get the average. You get the median tourist experience. You get a postcard.

If you want the city behind the postcard, you have to engineer your prompt. Here's how.

---

## Step 1: Assign a Role (Give the AI a Personality)

An LLM without a role is a generalist. A generalist gives you Wikipedia. You want an expert.

```
You are an expert architectural historian and Paris travel guide with 
decades of experience uncovering overlooked historical sites. You know 
the hidden streets, palaces, chapels, and mansions that most tourists 
ignore. Provide context about each site's architectural significance, 
era, and historical anecdotes. Think like a local historian who also 
loves storytelling.
```

Why it works: Role-setting shifts the model's response distribution. It stops predicting "average travel answer" and starts predicting "what would an obsessive Parisian historian say." The persona acts as a filter on every word that follows.

---

## Step 2: Define the Task With Surgical Precision

Vague tasks produce vague outputs. Be explicit - almost uncomfortably so.

```
Identify and recommend three lesser-known historical sites in Paris. 
Include palaces, mansions, small chapels, or minor museums that rarely 
appear in mainstream travel guides. For each site, provide its official 
name, location (district/arrondissement), architectural style, era of 
construction, and one unique feature that makes it worth visiting. 
Include links to official sources, Wikipedia, or heritage databases 
for verification.
```

Why it works: Every line is a constraint that narrows the output space. "Lesser-known," "minor museums," "arrondissement," "era of construction" - these aren't decorative. They're guardrails that prevent the model from defaulting to the obvious.

---

## Step 3: Explicitly Exclude What You Don't Want

This is the step most people skip - and it's often the most powerful one.

```
Do not include extremely popular landmarks such as Notre-Dame, 
the Eiffel Tower, Sacré-Cœur, the Louvre, or Musée d'Orsay. 
Exclude sites that appear in the top 10 tourist lists or are 
heavily photographed on social media. Focus on hidden gems with 
historical, architectural, or cultural significance that tourists 
regularly miss. Prioritize publicly accessible and verifiable sites.
```

Why it works: LLMs, like humans, have defaults. Excluding by name forces the model to explore lower-probability, higher-quality territory. Think of it as telling a sommelier: "No Bordeaux. Surprise me."

---

## Step 4: Dictate the Output Format

If you don't specify format, you get a wall of prose that's exhausting to parse. Make the model do the organizational work for you.

```
Return all results in a Markdown table with columns: 
Name (linked to source) | Location (arrondissement and street) 
| Style/Era | Key Feature | Historical Anecdote | Why it's unique. 
Include concise explanations for each column. Limit text to 
practical, informative summaries while keeping it engaging.
```

Why it works: Structured output isn't just about aesthetics - it forces the model to populate specific fields, which reduces hallucination and increases information density. You're essentially giving the AI a form to fill out, not a blank page to wander across.

---

## Step 5: Demand Verification

This is the step that separates casual prompting from professional prompting.

```
Verify each recommended site against at least two reliable sources 
such as Wikipedia, official heritage websites, or local historical 
records. Provide links. If sources conflict, note discrepancies 
and mention the most widely accepted details. Avoid unverified 
or speculative entries.
```

Why it works: AI models can confabulate with total confidence. By explicitly requesting citations and instructing the model to flag conflicts, you activate a more careful, source-anchored generation mode. It won't eliminate hallucinations entirely - but it dramatically reduces them, and makes the ones that slip through much easier to spot.

---

## The Mental Model Behind All of This

Think of prompting as hiring a contractor, not asking a friend for advice.

When you hire a contractor, you give them: a role (architect), a deliverable (three-bedroom layout), constraints (no open plan, must have a study), a format (blueprints, not sketches), and quality standards (must pass code inspection).

You wouldn't hire a contractor and just say "build me something nice."

Your prompt is your contract. The more precise it is, the better the build.

---

## The Four Prompting Principles I Live By

1. **Role first, always.** It sets the entire tone of the response.
2. **Structure the output.** Tables and lists outperform prose for dense information.
3. **Exclude explicitly.** Telling the model what not to do is just as important as what to do.
4. **Iterate without ego.** If the output misses the mark, refine the prompt - not your expectations.
