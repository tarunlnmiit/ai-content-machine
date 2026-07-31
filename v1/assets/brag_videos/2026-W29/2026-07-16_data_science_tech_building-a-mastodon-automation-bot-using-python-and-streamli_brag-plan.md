# Brag Plan: "40 Lines" (Mastodon posting bot, no wrapper library)

**Chosen hook:** "You were about to import 4,000 lines to call `/media` and `/statuses`."
**Formula:** Contrarian + Hyper-specificity (the everyone-reaches-for-the-library provocation fused with the two actual endpoint names — the specificity is what sells the deadpan).
**Tone preset:** yc-parody
**Angle (one line):** A deadpan Series-A launch film for a "product" that is 40 lines of `requests` — the Mastodon posting bot pitched with full startup gravitas, its entire moat being that it calls exactly two HTTP endpoints instead of importing a 4,000-line dependency to reach them.

---

## What is this app?
Not a product — a Data Science/Tech essay by a working data scientist who installed `Mastodon.py`, spent twenty minutes reading its docs to attach one image, then closed the tab and wrote the whole bot with `requests` in 40 lines. The proof is real code: a `post_toot()` function that hits `POST /api/v1/media` (park the image, get a media ID back) then `POST /api/v1/statuses` (fire the toot), both authed by one bearer token — plus a Streamlit wrapper that turns it into a web form with a masked token field and a file uploader, no HTML written. The thesis: most of the time the underlying API is simpler than the library wrapping it, so look before you install.

## The angle
The comedy engine is the **mismatch**: full startup-launch seriousness applied to "it's just two HTTP calls." The essay is earnest and correct — the video does NOT mock it. It plays the *40-line bot* as if it were a funded launch: deadpan spec slides, matter-of-fact metrics, a mission-statement outro. The absurdity is that the entire "product" is a function you could read in one screen, and its competitive advantage is *not* importing 4,000 lines. Specific to this piece: it recreates the real two-endpoint flow (media upload → status post → live toot URL), quotes the essay's actual ratio test ("am I calling three functions from this package, or thirty?"), and closes on the essay's real thesis line.

## Hook (first 2-3 seconds)
**"You were about to import 4,000 lines"** lands on a flat, still card — heavy sentence-case type, no caps-shouting, no chaos. Beat, then the specific resolve drops beneath in the accent/mono: **"…to call `/api/v1/media` and `/api/v1/statuses`."** Delivered matter-of-fact, like a founder stating an obvious market inefficiency. Held to its read floor so the contrarian claim and the two endpoint names both land completely before the cut.

## Key moments (the middle)
- **The two endpoints, stated as the entire surface area.** A flat spec card: `POST /api/v1/media` → *park the image, get an ID* and `POST /api/v1/statuses` → *fire the toot*. Mono, no inflation. This is the "our whole architecture" slide, played straight.
- **The function, live.** A simulated dark terminal: the `post_toot()` call runs — media uploads, returns a media ID (`"109834…"`), the status posts, and the response returns the live public `url` of the toot. This is the product *doing its thing* — the centerpiece, and it's 40 lines.
- **The deadpan ratio metric.** Three facts stated flat as launch metrics: **4,000 lines imported → 0. 40 lines shipped. 2 endpoints called.** Courier-adjacent figures. The essay's own ratio test ("three functions, or thirty?") is the punchline underneath.

## Outro / punchline
The essay's real thesis, delivered as the deadpan mission-statement close:
**"Forty lines you wrote beat four thousand you imported — every time you have to debug them at 2 a.m."**
Then the "product" name card: **`post_toot()` — Two endpoints. No wrapper. Ships tonight.**

## User flow worth showing
YES — the bot's real two-call flow is the centerpiece, recreated as working-app scenes:
- **Entry:** the `post_toot()` function called with text + an image path (no wrapper import, one bearer token).
- **Key action:** `POST /api/v1/media` returns a media ID, then `POST /api/v1/statuses` posts with `media_ids[]` — both visible in the terminal.
- **Result:** the response returns the live public `url` of the toot — proof the round trip worked, not a hardcoded green check.
Show the flow, not a diagram of it. The two-endpoint spec card and the ratio-metric slide are each used once, as frames around the flow, not as substitutes for it.

## Tone
- Preset: yc-parody
- Creative direction: deadpan startup-launch film for a 40-line function — Series-A gravitas, one-screen-of-code budget
- Interpretation: structured, 5 scenes, each making one claim, played completely straight. Hard cuts, no winking, no chaos. The hook is a provocation but stays flat and matter-of-fact (a stated inefficiency, not a shout) so hook and tone don't fight. The two endpoint names and the metrics read like fact. The joke is how seriously "just call two endpoints" is delivered as a launch.

## Format: vertical — 1080x1920
## Duration: ~20s

## Visual identity (from the DS/Tech niche + the essay's subject)
- Background: deep near-black terminal charcoal `#0d1117` (GitHub-dark register — fits a data-scientist audience and the terminal centerpiece)
- Surface / card: `#161b22`
- Accent: terminal green `#3fb950` for the returned media ID / live `url` / success; secondary electric blue `#58a6ff` for endpoint paths, keys, and headings; muted amber `#d29922` reserved for the "4,000 → 0" strike on the ratio slide
- Text: off-white `#e6edf3`; muted labels `#8b949e`
- Display font: a heavy grotesque (Inter / Space Grotesk, 700) for claim cards
- Body / data font: a monospace (JetBrains Mono / Courier-adjacent) for the terminal, endpoint paths, JSON, and metric figures
- Strongest visual element: the live terminal running `post_toot()` — media upload returning an ID, status post returning the public toot `url` — plus the two-endpoint spec card. Subtle scanline/glow on the terminal, otherwise clean and restrained.

## Share copy (draft)
I installed a 4,000-line library to post one toot with an image. Then I read the API — it's two HTTP endpoints. The whole bot is 40 lines of `requests`. Open the docs before you `pip install`. Forty lines you wrote beat four thousand you imported.

## Audio direction
- Role: sparse professional accents over a low, confident synth bed — restrained launch-film energy, not hype-reel density
- Music: a quiet, deadpan-confident electronic bed (minimal pulse, no drop). Enters under the hook, holds flat, small lift as the live `url` returns, settles under the outro thesis line.
- Music treatment: low volume throughout; no swell on the parody beats (restraint is the joke); let the ratio-metric slide and outro sit almost dry so the words land.
- Music cue guidance: track TBD from the bundled DS/tech set — to be detected at composition time. Target 1 strong cue at the live-`url` return (~scene 3) — the "it actually posted" payoff beat. Keep the hook and outro on quiet, un-cued holds. Beat-grid window only for the 3 ratio-metric figures on the metric slide — snap every other beat so each figure holds to its read floor.
- Audio-reactive treatment: subtle — let the terminal cursor / running glow breathe faintly with the bed; no waveform bars.
- SFX posture: sparse, motion-matched, professional restraint — a soft key-tick as the terminal command types, a low confirm tick per HTTP call returning, one dry card-set on the name card. Nothing loud.
- Audio-coupled moments: the typed `post_toot(...)` call (key ticks), the media ID return (confirm tick), the status post return (confirm tick), the live `url` appearing (the one small lift), the ratio figures settling.
- Restraint rule: no hype-reel whooshes, no risers, no dubstep drop. yc-parody stays quiet and deadpan — the audio must never oversell what is deliberately a 40-line function.

## Storyboard

### Scene 1 — About to import 4,000 lines (hook) — 4.5s
Flat charcoal card, still. Heavy sentence-case line lands and holds: **"You were about to import 4,000 lines"**. Beat (~1s), then the specific resolve drops beneath in mono/accent: **"…to call `/api/v1/media` and `/api/v1/statuses`."** Delivered matter-of-fact, no caps, no motion clutter. Held longest of the setup scenes so the claim and both endpoint names read fully.
Sequential/interaction: yes — line two arrives after line one holds.
Audio intent: quiet confidence enters; a founder stating an obvious inefficiency.
Audio-coupled idea: none for the hook (keep it still); optional single soft accent as line two lands.
Music: low deadpan bed enters.
Transition mood: hard cut → Scene 2

### Scene 2 — The two endpoints (the whole architecture) — 4.5s
Flat spec card, played as a launch "architecture" slide. Two rows, mono, arriving one by one:
`POST /api/v1/media` → *park the image, get an ID*
`POST /api/v1/statuses` → *fire the toot*
Both authed by one bearer token (a small muted footnote). Stated as the entire surface area of the product.
Sequential/interaction: yes — 2 endpoint rows drop in one by one; hold the pair on screen ~0.8s after the second lands so both read.
Audio intent: dry, factual — a low tick as each row locks.
Audio-coupled idea: one confirm tick per endpoint row, spaced.
Music: bed holds flat.
Transition mood: hard cut → Scene 3

### Scene 3 — The function runs (entry + key action + result) — 5.5s
Simulated dark terminal fills the frame. The `post_toot(...)` call types out (mono, key ticks). Then it runs: `POST /api/v1/media` returns a media ID (`"id": "109834…"`, green), `POST /api/v1/statuses` posts with `media_ids[]`, and the response returns the live public toot **`url`** in green — the round-trip proof. This is the product doing its thing, and it's one function.
Sequential/interaction: yes — command types, media ID returns, then the live `url` returns; simulated running.
Audio intent: understated "it's working" — dry key ticks, a low confirm tick per call, one small lift as the live `url` appears.
Audio-coupled idea: typed call key ticks; confirm tick on media ID; the one lift on the `url` return.
Music: single strong cue targeted here at the `url` return.
Transition mood: hard cut → Scene 4

### Scene 4 — The ratio (deadpan launch metric) — 3s
Flat card, three facts stated as launch metrics, mono figures, no inflation, arriving in a fast trio:
**4,000 lines imported → 0 · 40 lines shipped · 2 endpoints called.**
The essay's ratio test sits underneath as a small muted line: *"Three functions from this package, or thirty?"* The amber strike on "4,000 → 0" is the only color flourish.
Sequential/interaction: yes — 3 figures settle quickly; hold the full trio to read.
Audio intent: dry, factual — almost silent under the figures.
Audio-coupled idea: soft settle tick as figures lock; otherwise near-dry.
Music: near-dry, bed ducked.
Transition mood: hard cut → Scene 5

### Scene 5 — The thesis + name (outro) — 3s
Charcoal canvas. The essay's actual thesis line, held clean as a mission statement:
**"Forty lines you wrote beat four thousand you imported — every time you have to debug them at 2 a.m."**
Then a small name card: **`post_toot()` — Two endpoints. No wrapper. Ships tonight.**
Sequential/interaction: thesis line holds, then name card resolves beneath.
Audio intent: bed settles and fades; the words land last.
Audio-coupled idea: one dry card-set on the name card; no flourish.
Music: settle and fade to near-silence under the thesis.
Transition mood: hold, then fade to charcoal.

**Music mood for this video:** deadpan / parody — quiet, confident, minimal electronic bed. Not upbeat, not a hype reel.
**Audio summary:** A low deadpan bed enters under the hook, holds flat through the two-endpoint slide, gives one small lift as the live toot `url` returns, goes near-dry under the ratio metric, and fades under the closing thesis so the point lands last.
