# Brag Plan: "Free Local AI Stack" (Ollama job-hunt autopilot)

**Chosen hook:** "Cancel your $200/month AI stack tonight. It runs local by morning."
**Formula:** Contrarian + Timeframe tension (the cancel-your-stack provocation fused with a tonight→morning promise).
**Tone preset:** yc-parody
**Angle (one line):** A deadpan Series-A launch film for a thing that is completely free — DIY Ollama on your own laptop, pitched with startup gravitas, proven by a job-hunt bot that scores listings against your resume at 2am while you sleep.

---

## What is this app?
Not a product — a Data Science/Tech essay by a working data scientist who replaced $200/month of AI subscriptions (API credits, Copilot, a cloud notebook) with a free local Ollama setup. The proof is a real tool he built: a job-hunt autopilot that scrapes company career portals on a schedule, scores each listing against his resume via a local model (JSON `score` / `match_reasons` / `red_flags`), and leaves a ranked shortlist waiting when he wakes up. No API call, no charge, nothing leaves the machine.

## The angle
The comedy engine is the **mismatch**: full startup-launch seriousness applied to "you just run Ollama on your laptop." The essay itself is earnest and correct — the video does NOT mock it. Instead it plays the *free DIY setup* as if it were a funded launch: deadpan metric slides, matter-of-fact claims, mission-statement outro. The absurdity is that the "product" costs nothing and runs while you sleep. Specific to this piece: it recreates the actual bot flow (terminal → scoring → ranked shortlist), quotes the real metrics from the essay, and closes on the essay's actual thesis line.

## Hook (first 2-3 seconds)
**"Cancel your $200/month AI stack tonight."** on a flat, still card — heavy sentence-case type, no chaos, no caps-shouting. Delivered matter-of-fact like a founder stating an obvious market truth. Beat, then the timeframe promise resolves under it: **"It runs local by morning."** Held to its read floor so the contrarian claim lands completely before the cut.

## Key moments (the middle)
- **The terminal, live.** A simulated dark terminal: `ollama pull llama3` then a Python job-scorer running — a listing streams in and returns JSON (`"score": 9`, `match_reasons`, `red_flags`). This is the product *doing its thing*, the centerpiece.
- **The ranked shortlist arrives.** 3 job rows drop in one by one at 08:00 — company + role + a fit score (9.2 / 8.7 / 8.1) — the "wake up to a ranked list" payoff.
- **The deadpan metric slide.** Three facts stated flat as launch metrics: **$0/month. 0 API calls out. 100% of your data stays on your machine.** Courier-adjacent figures, no inflation.

## Outro / punchline
The essay's real thesis, delivered as the deadpan mission-statement close:
**"The best argument for local AI isn't the cost savings. It's what you build when cost stops being a constraint."**
Then the "product" name card: **Local AI Stack — Runs while you sleep. Costs nothing.**

## User flow worth showing
YES — this is the centerpiece. The bot's three beats, recreated as working-app scenes:
- **Entry:** `ollama pull llama3` + the scorer script starting in a terminal at 2am (no API key, no account).
- **Key action:** a job listing passed to the local model, returning structured JSON — score, matching skills, red flags — visible in the terminal.
- **Result:** the ranked shortlist waiting at 08:00 — 3 scored rows arriving one by one.
Show the flow, not a diagram of it. The landing-page-style metric slide is used once, as a frame around the flow, not as a substitute.

## Tone
- Preset: yc-parody
- Creative direction: deadpan startup-launch film for a genuinely free DIY setup — Series-A gravitas, garage-project budget
- Interpretation: structured, 5 scenes, each making one claim, played completely straight. Hard cuts, no winking, no chaos. The hook is a provocation but stays flat and matter-of-fact (a stated market truth, not a shout) so hook and tone don't fight. Metrics read like fact. The joke is how seriously "run Ollama locally" is delivered.

## Format: vertical — 1080x1920
## Duration: ~20s

## Visual identity (from the DS/Tech niche + the essay's subject)
- Background: deep near-black terminal charcoal `#0d1117` (GitHub-dark register — fits a data-scientist audience and the terminal centerpiece)
- Surface / card: `#161b22`
- Accent: terminal green `#3fb950` for scores / success / the running cursor; secondary electric blue `#58a6ff` for keys and headings
- Text: off-white `#e6edf3`; muted labels `#8b949e`
- Display font: a heavy grotesque (Inter / Space Grotesk, 700) for claim cards
- Body / data font: a monospace (JetBrains Mono / Courier-adjacent) for the terminal, JSON, and metric figures
- Strongest visual element: the live terminal running the local job-scorer, returning JSON, and the ranked shortlist populating at 08:00. Subtle scanline/glow on the terminal, otherwise clean and restrained.

## Share copy (draft)
I cancelled $200/month of AI subscriptions. A free Ollama bot now scores job listings against my resume at 2am while I sleep — no API call, no charge, nothing leaves my laptop. The best argument for local AI isn't the money.

## Audio direction
- Role: sparse professional accents over a low, confident synth bed — restrained launch-film energy, not hype-reel density
- Music: a quiet, deadpan-confident electronic bed (minimal pulse, no drop). Enters under the hook, holds flat, small lift as the shortlist arrives, settles under the outro thesis line.
- Music treatment: low volume throughout; no swell on the parody beats (restraint is the joke); let the metric slide and outro sit almost dry so the words land.
- Music cue guidance: track TBD from the bundled DS/tech set — to be detected at composition time. Target 1 strong cue at the shortlist arrival (~scene 3) for the one-by-one row reveals; keep the hook and outro on quiet, un-cued holds. Beat-grid window only for the 3 shortlist rows — snap every other beat so each row holds to its read floor.
- Audio-reactive treatment: subtle — let the terminal cursor / running glow breathe faintly with the bed; no waveform bars.
- SFX posture: sparse, motion-matched, professional restraint — a soft key-tick as the terminal command types, a low confirm tick per JSON return and per shortlist row, one dry card-set on the name card. Nothing loud.
- Audio-coupled moments: the typed `ollama pull` command (key ticks), the JSON return (confirm tick), the 3 shortlist rows (one tick each, spaced), the metric figures settling.
- Restraint rule: no hype-reel whooshes, no risers, no dubstep drop. yc-parody stays quiet and deadpan — the audio must never oversell what is deliberately a low-key free setup.

## Storyboard

### Scene 1 — The cancel (hook) — 4.5s
Flat charcoal card, still. Heavy sentence-case line lands and holds: **"Cancel your $200/month AI stack tonight."** Beat (~1s), then a second line resolves beneath in the accent: **"It runs local by morning."** Delivered matter-of-fact, no caps, no motion clutter. Held longest of the setup scenes so the contrarian claim reads fully.
Sequential/interaction: yes — line two arrives after line one holds.
Audio intent: quiet confidence enters; a founder stating an obvious truth.
Audio-coupled idea: none for the hook (keep it still); optional single soft accent as line two lands.
Music: low deadpan bed enters.
Transition mood: hard cut → Scene 2

### Scene 2 — The terminal (entry + key action) — 5s
Simulated dark terminal fills the frame. `ollama pull llama3` types out (mono, key ticks), then a Python job-scorer starts. A job listing streams in and the model returns JSON: `{ "score": 9, "match_reasons": [...], "red_flags": [...] }` — green score, muted keys. Timestamp `02:00` in the corner. This is the product doing its thing, no API key, no account.
Sequential/interaction: yes — command types, then JSON returns; simulated running.
Audio intent: understated "it's working" — dry key ticks and one low confirm tick on the JSON return.
Audio-coupled idea: typed command key ticks; confirm tick on JSON return.
Music: bed holds flat.
Transition mood: hard cut → Scene 3

### Scene 3 — The shortlist at 08:00 (result) — 4.5s
Same dark surface, now a clean ranked list header: **"Ranked shortlist — 08:00"**. Three job rows drop in one by one: company · role · fit score (**9.2 / 8.7 / 8.1** in green). The "wake up to a ranked list" payoff.
Sequential/interaction: yes — 3 rows arrive one by one, each with a soft tick; hold the full set on screen ~1s after the third lands so all read.
Audio intent: small satisfying lift as the list completes.
Audio-coupled idea: one confirm tick per row, spaced (snap every other beat), then hold.
Music: single strong cue targeted here for the row reveals.
Transition mood: hard cut → Scene 4

### Scene 4 — The metrics (deadpan launch slide) — 3s
Flat card, three facts stated as launch metrics, mono figures, no inflation, arriving together or in a fast trio:
**$0 / month · 0 API calls out · 100% data stays on your machine.**
Sequential/interaction: yes — 3 stats settle quickly; hold the full trio to read.
Audio intent: dry, factual — almost silent under the figures.
Audio-coupled idea: soft settle tick as figures lock; otherwise let it sit near-dry.
Music: near-dry, bed ducked.
Transition mood: hard cut → Scene 5

### Scene 5 — The thesis + name (outro) — 3s
Charcoal canvas. The essay's actual thesis line, held clean as a mission statement:
**"The best argument for local AI isn't the cost savings. It's what you build when cost stops being a constraint."**
Then a small name card: **Local AI Stack — Runs while you sleep. Costs nothing.**
Sequential/interaction: thesis line holds, then name card resolves beneath.
Audio intent: bed settles and fades; the words land last.
Audio-coupled idea: one dry card-set on the name card; no flourish.
Music: settle and fade to near-silence under the thesis.
Transition mood: hold, then fade to charcoal.

**Music mood for this video:** deadpan / parody — quiet, confident, minimal electronic bed. Not upbeat, not a hype reel.
**Audio summary:** A low deadpan bed enters under the hook, holds flat through the terminal, gives one small lift as the ranked shortlist completes, goes near-dry under the metric slide, and fades under the closing thesis so the point lands last.
