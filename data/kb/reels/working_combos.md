# Working Tool Combos — Idea Cards + Shoot Scripts

Real, verified-as-of-June-2026 "tool + tool" / "Claude + skill" combos you can actually set up, demo, and shoot. Every combo here exists and works today (sources at the end). Each card flags **demo type** (dev / no-code / local), the **honest impact**, and **why it hooks** — built so you only ever claim what you can show on screen (`04_honesty_guardrail.md`).

Part A = idea cards (pick from these). Part B = full 5-beat shoot scripts for the six strongest.

---

# PART A — Idea cards

## Developer / automation

### 1. Claude + ScrapeGraphAI — "describe it, get the data"
- **Connect:** ScrapeGraphAI (open-source, MIT, Python) — paste a URL, describe what you want in plain English, get structured data. Works with OpenAI/Gemini/Groq or local Ollama models.
- **Impact:** replaces paid scrapers (Apify/Bright Data) for many jobs; no proxies, no selectors. Repo was updated today, ~MIT licensed — fully legit to point people to.
- **Why it hooks:** "free open-source tool killed my paid scraper" is *already proven* in your swipe file (thevibefounder, 24.4K likes). Equation + secret hook.
- **Demo:** dev. **Honesty:** show it scraping one real site live; don't claim it beats every paid tool — say "for most jobs."

### 2. Claude + GitHub MCP — "Claude reviews my PRs"
- **Connect:** official GitHub MCP. Claude analyzes PR diffs, suggests review fixes, opens issues from bug reports, watches Actions.
- **Impact:** a code-review pass before any human looks. Real time saved on every PR.
- **Why it hooks:** "I let Claude review my code and it caught what I missed" — build-in-public credibility. One-AI-replaces-team hook.
- **Demo:** dev. **Honesty:** show a real diff + a real comment it generated.

### 3. Claude + Playwright MCP — "Claude clicks through my app and finds the bug"
- **Connect:** Playwright MCP for browser automation/testing.
- **Impact:** Claude drives a real browser, reproduces a bug, reports the failing step.
- **Why it hooks:** watching an AI operate a UI is inherently watchable. "I stopped writing test scripts."
- **Demo:** dev. **Honesty:** show the browser actually moving.

### 4. Claude Code, 100% local on a Mac — "$0/month, fully offline"
- **Connect:** LM Studio + LiteLLM, or `claude-code-local` / `vllm-mlx` (MLX-native, Anthropic Messages API) running a model like Qwen/Llama on Apple Silicon.
- **Impact:** no API fees, private/airgap-ready, MLX is fast on unified memory (a 128GB Mac loads an 80B model).
- **Why it hooks:** contrarian "I cancelled my AI subscription" + local-privacy angle.
- **Demo:** local. **⚠️ Honesty (important):** the local model is **Qwen/Llama, not Claude** — say "Claude Code *the tool*, running a local open model." The reel in your swipe file that blurred this (hasantoxr) got roasted in the comments. Be precise and you win the trust the roasted one lost.

### 5. Claude skill: code-reviewer / git-commit-writer — "the skills that run my dev day"
- **Connect:** install a couple of the most-used Claude Code skills (code-reviewer, git-commit-writer, readme-generator).
- **Impact:** consistent commit messages, READMEs, review notes with zero prompting.
- **Why it hooks:** listicle hook ("the 3 Claude skills I install on every repo"). High save intent.
- **Demo:** dev.

## Content / creator workflow

### 6. Claude + Metricool MCP — "schedule + analyze all my socials from chat"
- **Connect:** Metricool MCP at `https://ai.metricool.com/mcp` (Customize → Connectors, OAuth2). Schedule posts, read analytics, find best posting time, check competitors — across all connected networks, in plain language.
- **Impact:** replaces hopping between 4 tools; "upload a video → schedule to IG/TikTok/LinkedIn at best time" in one message.
- **Why it hooks:** top-performing pattern in your data (mavgpt Metricool reel, 5.3K + 1.6K comments). Equation hook: Claude + Metricool = autopilot socials.
- **Demo:** no-code.

### 7. Claude + Metricool Carousel Agent skill — "idea → scheduled carousel, no design tool"
- **Connect:** the Metricool Carousel Agent (a Claude skills package) — turns Claude into a carousel generator wired to your Metricool account.
- **Impact:** go from a topic to a scheduled carousel without opening Canva. Carousels are your top save/share format.
- **Why it hooks:** "I make a week of carousels in one prompt." Number/result hook.
- **Demo:** no-code / light dev.

### 8. Claude + Higgsfield MCP — "50 UGC ads from one product photo"
- **Connect:** Higgsfield MCP — AI image + video from 30+ models through one interface.
- **Impact:** generate carousels, product shots, UGC-style ads inside Claude.
- **Why it hooks:** proven (mavgpt Higgsfield reel, 18.8K). "This killed my need for an ad agency" — land it honestly (it assists, doesn't replace strategy).
- **Demo:** no-code.

### 9. Claude + Meta Ads MCP — "run my ad reporting from the terminal"
- **Connect:** Meta's official MCP for Facebook/Instagram ads — create campaigns, pull performance breakdowns, manage audiences, A/B analysis.
- **Impact:** ad performance Q&A in chat instead of Ads Manager spelunking.
- **Why it hooks:** "I asked Claude why my ad flopped and it pulled the numbers." Demo: no-code. **Honesty:** don't auto-spend; show reporting, not money-moving.

## Productivity / knowledge

### 10. Claude in Excel — "a financial model / dashboard in minutes"
- **Connect:** Claude for Excel add-in (spreadsheet agent, now on Opus 4.6); MCP connectors pull live data into the sheet.
- **Impact:** build and explain models in-place, no copy-paste; pull live data via connectors.
- **Why it hooks:** "I built a live dashboard in 4 minutes" — number/result hook; broad appeal.
- **Demo:** no-code.

### 11. Claude across Excel + PowerPoint + Word (shared context) — "spreadsheet → deck, no copy-paste"
- **Connect:** the Office add-ins now share full conversation context across apps.
- **Impact:** turn a model into a slide deck without re-explaining or re-pasting.
- **Why it hooks:** "watch a spreadsheet become a presentation by itself." Secret/curiosity hook.
- **Demo:** no-code.

### 12. Claude + Notion MCP — "my notes file themselves as tasks"
- **Connect:** Notion MCP.
- **Impact:** turn a brain-dump into structured pages/tasks; query your workspace in chat.
- **Why it hooks:** "I never organize Notion again." Accessibility hook.
- **Demo:** no-code.

## Data / job-hunt / career (your proven niche)

### 13. Job-hunt Agent v2 — "Claude + ScrapeGraphAI scans boards + scores against my resume"
- **Connect:** ScrapeGraphAI to pull fresh postings + Claude to score 0–100 vs your resume; notify on Telegram (your original mechanic).
- **Impact:** the honest sequel to the reel that already worked for you — now open-sourced and tool-combined.
- **Why it hooks:** it's your winner, leveled up. Build-in-public + free/open/local trifecta.
- **Demo:** dev. **Honesty:** "scores and surfaces, doesn't auto-apply."

### 14. Claude in Excel — "an application tracker that scores itself"
- **Connect:** Claude in Excel over a job-application sheet; pull JD text, score fit, draft tailored bullet points per row.
- **Impact:** a self-scoring job tracker, no-code version of #13 for non-developers.
- **Why it hooks:** accessibility hook ("no code, just a spreadsheet"). Pairs with a downloadable template (lead magnet).
- **Demo:** no-code.

---

# PART B — Full shoot scripts (the six strongest)

Format: **Hook (0–3s) → Problem → Reveal+proof → Payoff → CTA.** On-screen text in **bold**, B-roll in *italics*. All ≤45s, captions burned in, hard cut at 0–3s, one keyword CTA.

## Script 1 — ScrapeGraphAI (Combo #1) · dev
- **Hook:** *Face to camera, big text:* **"This free tool replaced my $300/month scraper."**
- **Problem:** "I was paying for Apify just to pull data off a few sites. Overkill." *Cut to the pricing page.*
- **Reveal+proof:** "This is ScrapeGraphAI — open source, MIT. I paste a URL, describe what I want in plain English…" *Screen-record: type a prompt, run it, structured JSON appears.* "…and it hands me clean structured data. No selectors, no proxies."
- **Payoff:** *Back to face:* "Free. Open source. Runs with a local model if you want zero API cost." **For most scraping jobs, this is all you need.**
- **CTA:** **"Comment 'SCRAPE' and I'll DM you the repo + my exact prompt."**
- *Honesty check:* shows one real run; claim is "for most jobs," not "beats everything."

## Script 2 — Claude + Metricool MCP (Combo #6) · no-code
- **Hook:** *Big text over screen:* **"Claude now runs my entire social calendar."**
- **Problem:** "I had four tabs open just to schedule one post and check what's working."
- **Reveal+proof:** "I connected Claude to Metricool with one link." *Screen-record: Customize → Connectors → paste `ai.metricool.com/mcp` → OAuth.* "Now I just say: 'schedule this to Instagram, TikTok and LinkedIn at my best time.'" *Show it scheduling + pulling an analytics number.*
- **Payoff:** "Scheduling, analytics, best-time, competitor check — all in one chat. No more tool-hopping."
- **CTA:** **"Comment 'CONTENT' for the 30-second setup guide."**

## Script 3 — Local Claude Code on a Mac (Combo #4) · local
- **Hook:** *Face, big text:* **"I run Claude Code on my Mac for $0/month."**
- **Problem:** "API bills add up, and some of my work can't leave my machine."
- **Reveal+proof:** "Here's the honest version: it's Claude Code — *the tool* — pointed at a local open model on Apple Silicon with MLX." *Screen-record terminal: a task running fully offline, wifi symbol off.* "Qwen running natively. No cloud, no data leaving the laptop."
- **Payoff:** "Private, offline, airgap-ready. Zero per-token cost. Great for NDA work."
- **CTA:** **"Comment 'LOCAL' for the setup (LM Studio + LiteLLM)."**
- *Honesty check:* explicitly states the model is a local open model, not Claude's cloud model — this is the line that earns trust.

## Script 4 — Claude in Excel (Combo #10) · no-code
- **Hook:** *Screen, big text:* **"I built this live dashboard in 4 minutes."**
- **Problem:** "Building a model used to mean an afternoon of formulas."
- **Reveal+proof:** *Screen-record the Claude for Excel add-in:* "I describe the model, Claude builds it in the sheet — formulas, not pasted values." *Show a connector pulling live data into a cell.*
- **Payoff:** "It explains every formula and pulls live data through connectors. Running on Opus 4.6."
- **CTA:** **"Comment 'EXCEL' and I'll send the prompt + the template."**

## Script 5 — Claude + GitHub MCP (Combo #2) · dev
- **Hook:** *Face, big text:* **"I let Claude review my pull request. It caught what I missed."**
- **Problem:** "Self-reviewing your own PR at midnight never goes well."
- **Reveal+proof:** "Claude's connected to my repo through the GitHub MCP." *Screen-record: point at a PR, Claude reads the diff, posts review comments, opens an issue from a bug.*
- **Payoff:** "A real review pass before any human looks — every single PR."
- **CTA:** **"Comment 'REVIEW' for the MCP setup."**

## Script 6 — Job-hunt Agent v2 (Combo #13) · dev · your niche
- **Hook:** *Face, big text:* **"My job-hunt bot got an upgrade."**
- **Problem:** "Last time it scanned career pages. The slow part was still finding the postings."
- **Reveal+proof:** "Now Claude + ScrapeGraphAI pulls fresh postings, scores each 0–100 against my resume, and texts me the top matches." *Screen-record: scores ticking, a Telegram message arriving.*
- **Payoff:** "Free, open source, runs on my machine. It surfaces and scores — it does **not** auto-apply."
- **CTA:** **"Comment 'JOBS2' for the repo."**
- *Honesty check:* the explicit "does not auto-apply" is the trust line; it's the upgrade to the reel that already worked.

---

## Sources (all verified June 2026)
- Best MCP servers for Claude (GitHub, Playwright, Sequential Thinking, Notion, Slack, Filesystem, Meta Ads, Higgsfield): [codersera](https://codersera.com/blog/best-mcp-servers-claude-code-cursor-2026/), [truefoundry](https://www.truefoundry.com/blog/best-mcp-servers-for-claude-code), [mcpcat](https://mcpcat.io/guides/best-mcp-servers-for-claude-code/)
- Claude skills (code-reviewer, git-commit-writer, etc.): [Composio](https://composio.dev/content/top-claude-skills), [Agensi](https://www.agensi.io/learn/best-claude-code-skills-2026), [Awesome Claude Skills](https://awesomeclaude.ai/awesome-claude-skills)
- Local Claude Code on Apple Silicon (MLX / LM Studio + LiteLLM / vllm-mlx): [claude-code-local](https://github.com/nicedreamzapp/claude-code-local), [claude-code-mlx-proxy](https://github.com/chand1012/claude-code-mlx-proxy), [todatabeyond](https://todatabeyond.substack.com/p/run-claude-code-locally-on-apple)
- Metricool MCP + Carousel Agent: [Metricool MCP](https://metricool.com/metricool-mcp-claude/), [Carousel generator](https://metricool.com/claude-ai-carousel-generator-metricool-mcp/)
- ScrapeGraphAI (MIT, updated June 15 2026): [GitHub org](https://github.com/ScrapeGraphAI)
- Claude in Excel / PowerPoint / Word (shared context, Opus 4.6, MCP data connectors): [WinBuzzer](https://winbuzzer.com/2026/03/12/claude-links-excel-and-powerpoint-with-shared-context-reusab-xcxwbn/), [TechRepublic](https://www.techrepublic.com/article/news-claude-excel-powerpoint-integration-anthropic-ai-workflows/), [AI Tool Analysis](https://aitoolanalysis.com/claude-in-excel-review/)
