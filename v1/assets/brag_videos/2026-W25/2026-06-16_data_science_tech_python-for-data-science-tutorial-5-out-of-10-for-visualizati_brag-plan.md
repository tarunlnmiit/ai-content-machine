# Brag Plan: "Your Charts Get Judged First" (Python Tutorial 5/10 — Matplotlib & Seaborn)

**Chosen hook:** "Your model isn't what's getting judged first. Your charts are."
**Formula:** Authority reversal + Negativity bias
**Tone preset:** default
**Angle (one line):** A before/after reveal — the same analysis rendered as a gray default-matplotlib plot (that quietly loses the room) versus a clean seaborn chart that makes people trust you — ending on the 2×2 "story panel" that changes the conversation.

---

## What is this app?
Not an app — tutorial 5 of a 10-part Python-for-data-science series, arguing that visualization is communication, not cosmetics: your charts get judged before your model does, and a few setup fixes (seaborn theme, dropped spines, 300 DPI, zero-baseline, consistent colors) are the difference between a chart that lands and one that disappears.

## The angle
The essay's own thesis is an authority reversal: you assume your model is what's on trial, but the gray default figure in your slide deck is what actually decides whether the room trusts you. The video makes that literal — it shows the villain (a real default gray matplotlib chart) and kills it with one edit into a clean seaborn chart, then escalates to the 2×2 dashboard "story panel." Specific to THIS piece: it recreates the essay's actual charts (Titanic — steelblue/salmon survival, coolwarm heatmap, the four-panel EDA grid), not stock photos or generic motion.

## Hook (first 2-3 seconds)
Full-screen on the DS dark canvas: **"Your model isn't what's getting judged first."** lands, then the second line snaps under it: **"Your charts are."** Held ~3s so both sentences read. This is the reversal — the assumption, then the correction.

## Key moments (the middle)
- **The before/after reveal (centerpiece):** a real default gray-background matplotlib chart sits on screen (tiny fonts, gray box, top/right spines) — then in one snap-cut it becomes the clean seaborn version (white `whitegrid`, dropped spines, steelblue). The essay's actual personal-insert moment, made visual.
- **The five plot types, fast:** a quick sequence of the real seaborn charts — histogram (steelblue), scatter colored by survival (steelblue/salmon), survival-by-class barplot, coolwarm correlation heatmap — as evidence the toolkit is small.
- **The story panel:** the 2×2 EDA dashboard where the four panels arrive one-by-one, landing the line "one figure, two insights that interact."

## Outro / punchline
The reversal pays off: **"Fix the chart, not the data."** (adapted from the takeaway's "the chart needs work, not the data") over the clean dashboard, then the series tag: **Python for Data Science · 5/10**.

## User flow worth showing
none — no app or flow. Centerpiece is recreating the essay's real charts: the gray→clean before/after and the 2×2 story panel. These are the strongest visual material (Step-2 "choosing what to show" rank 1: recreate a real working-notebook moment), far stronger than the essay's stock Pexels photos.

## Tone
- Preset: default
- Creative direction: clean, confident, postable data-viz flex — the charts do the bragging
- Interpretation: 5 comfortable scenes, snappy entrances (0.3–0.5s) with settled holds; playful and direct, not solemn. The hook and the before/after get the room to read; everything else moves fast. Crossfade / clean slide, one hard snap-cut for the before→after transformation.

## Format: vertical — 1080x1920
## Duration: ~20s

## Visual identity (from the essay's real charts + DS niche look bible `v1/data/kb/design/ds_design.md`)
- Background: `#0a0e1a` (DS dark canvas) for title/outro cards; chart area is `whitegrid` white (the seaborn "after" look) — the white-vs-gray contrast IS the story
- Accent: `#3b82f6` (accent blue) for the hook emphasis + series tag; chart series use the essay's real colors — **steelblue** + **salmon** (survival), **coolwarm** heatmap
- Text: `#f0f4ff` (primary), muted labels `#64748b`
- Display font: Inter 800 (hook/outro), Inter 900 for any number/KPI
- Body font: Inter 500/600; code snippets JetBrains Mono 400 if any `sns.set_theme(...)` line is shown
- Strongest visual element: the gray default matplotlib figure transforming into the clean seaborn chart; the 2×2 Titanic dashboard with four real panels

## Share copy (draft)
Your model isn't what's getting judged first — your charts are. Same analysis, two charts: the gray default one loses the room, the clean one wins it. Tutorial 5/10 on making your data actually tell a story.

## Audio direction
- Role: warm, confident bed — light modern electronic/lo-fi, postable energy (not cinematic, not parody)
- Music: upbeat-but-clean instrumental bed; enter under the hook, hold through the chart sequence, small lift as the dashboard panels complete, soft fade under the outro line
- Music treatment: steady groove, no dramatic swell; let the beat carry the five-chart sequence and the four-panel arrivals
- Music cue guidance: track to be selected at composition time. Target 1 strong cue at the before→after snap-cut (Scene 3) and 1 at the moment the 2×2 dashboard completes (Scene 4). Beat-grid window: the four dashboard panels should arrive on a beat sub-grid but each hold to its read floor (~0.8s visible), not snapped every half-beat.
- Audio-reactive treatment: subtle — a soft presence lift on the clean chart when it snaps in; no waveform bars
- SFX posture: sparse, motion-matched — one clean "snap/whoosh" on the gray→clean transformation, light tick per dashboard panel arrival, tiny confirm on the outro tag
- Audio-coupled moments: the before→after snap-cut; the four dashboard panels arriving one-by-one
- Restraint rule: no heavy risers, no meme SFX; audio stays clean and professional so the charts read as credible

## Storyboard

### Scene 1 — The reversal (hook) — 3.5s
DS dark canvas `#0a0e1a`. Line one lands in Inter 800: **"Your model isn't what's getting judged first."** Then **"Your charts are."** snaps under it, "charts" emphasized in accent blue `#3b82f6`. Held so both sentences read fully.
Sequential/interaction: yes — two lines, second snaps in after the first settles (hold the full pair ~1.5s after both present).
Audio intent: confident open, set the groove.
Audio-coupled idea: subtle key-in on the second line.
Music: upbeat clean bed enters.
Transition mood: clean slide → Scene 2

### Scene 2 — The villain — 3s
Recreate a real DEFAULT matplotlib chart: gray background, tiny fonts, top+right spines, cramped axes — the Titanic age histogram rendered the ugly default way. Muted label: *"default matplotlib."* It should feel slightly wrong / cheap on purpose.
Sequential/interaction: none.
Audio intent: slight tension, a beat of "oof."
Audio-coupled idea: none (hold for the snap next scene).
Music: hold groove.
Transition mood: hard snap-cut → Scene 3

### Scene 3 — The fix (before → after, centerpiece) — 4s
Same chart SNAPS into the clean seaborn version: white `whitegrid`, dropped top/right spines, larger fonts, steelblue bars + KDE. The transformation is the payoff. Optional tiny JetBrains Mono line: `sns.set_theme(style="whitegrid")`. Muted label flips to *"one line at the top of every notebook."*
Sequential/interaction: yes — simulate the transformation (gray → clean) as a single decisive snap.
Audio intent: the satisfying "there it is" moment.
Audio-coupled idea: clean snap/whoosh SFX exactly on the transform + subtle presence lift on the clean chart (strong cue here).
Music: small accent hit on the snap.
Transition mood: clean slide → Scene 4

### Scene 4 — The story panel — 5s
The 2×2 Titanic EDA dashboard builds: four real panels arrive one-by-one — survival-by-class barplot (Blues), age histogram (steelblue), fare-by-class boxplot, survival-by-sex barplot — under a shared title *"Titanic EDA."* Line lands after the grid completes: **"One figure. Two insights that interact."**
Sequential/interaction: yes — 4 panels arrive one by one, each with a light tick; each panel holds ~0.8s visible; the full grid holds ~1.5s with the caption after completion.
Audio intent: building, satisfying accumulation.
Audio-coupled idea: tick per panel arrival; soft completion swell when the 4th lands (strong cue).
Music: small lift as the grid completes.
Transition mood: crossfade → Scene 5

### Scene 5 — Punchline + tag (outro) — 4s
Back to DS dark canvas, the clean dashboard dimmed behind. Punchline in Inter 800: **"Fix the chart, not the data."** Then the series tag in accent blue: **Python for Data Science · 5 / 10**. Hold clean, fade.
Sequential/interaction: yes — punchline lands, then the tag snaps under it.
Audio intent: confident button, resolve the groove.
Audio-coupled idea: tiny confirm tick on the series tag.
Music: soft fade after the tag.
Transition mood: fade to end.

**Music mood for this video:** upbeat-clean (confident, postable) — not cinematic, not parody.
**Audio summary:** A clean upbeat bed carries the whole piece — enters on the hook, holds a steady groove through the villain and the before→after snap (one accent hit), lifts gently as the four dashboard panels complete, then fades under the "fix the chart, not the data" button.
