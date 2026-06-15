# POETRY — Manual Overlay Placement (2026-W24)

**Clips:** `output/animations/2026-W24/overlay-scenes/poetry_scene-*.mp4`

## How (DaVinci, minimal friction)
1. Talking-head video on track **V1**.
2. Each overlay clip on **V2 above it**, starting at its **Time**. Clips are full-frame with an opaque background → they fully cover V1 for their **Dur** = a clean cutaway. No scaling needed.
3. Want the speaker still visible? Scale the V2 clip to ~35% and park it left/right — the card reads as a side panel.

## ⚠️ Timing rule
Times are measured from your **first spoken word**. If your edited timeline has an intro or lead silence before the first word, **add that offset to every Time**.

## Placement table

| # | Time | Dur | File (in `overlay-scenes/`) | Exact? | Shows on screen |
|---|------|-----|------------------------------|--------|-----------------|
| 01 | 0:00 | 7s | `poetry_scene-01_LineReveal.mp4` | ✓ | Data. / Models. / Dashboards. / The clean grammar of proof. |
| 02 | 0:26 | 6s | `poetry_scene-02_AtmosphericQuote.mp4` | ✓ | A poem finds the exact nerve no dataset ever mapped. |
| 03 | 1:13 | 7s | `poetry_scene-03_AtmosphericQuote.mp4` | ✓ | The lyric form admits what human experience refuses to sort. |
| 04 | 2:10 | 6s | `poetry_scene-04_DataVizReveal.mp4` | ✓ | Tools different. Curiosity identical. |
| 05 | 2:22 | 7s | `poetry_scene-05_LineReveal.mp4` | ✓ | The best scientific papers have rhythm. / The best commit messages have grief in them. |
| 06 | 2:29 | 6s | `poetry_scene-06_ImageTextReveal.mp4` | ✓ | Poetry was already in the server room |
| 07 | 2:43 | 4s | `poetry_scene-07_CounterReveal.mp4` | ✓ | times you've scraped the toast over the sink |
| 08 | 3:08 | 7s | `poetry_scene-08_HandwrittenReveal.mp4` | ✓ | The grey of a commute counts. / The brown of bad coffee counts. / The particular blue of a |
| 09 | 4:09 | 6s | `poetry_scene-09_AtmosphericQuote.mp4` | ✓ | Grief insists on specificity. |
| 10 | 4:17 | 7s | `poetry_scene-10_LineReveal.mp4` | ✓ | You don't miss a person. / You miss how they said your name. / The exact pitch of their la |
| 11 | 4:17 | 7s | `poetry_scene-11_VoiceMemoryDissolve.mp4` | ✓ | (visual / animation — no text) |
| 12 | 4:30 | 6s | `poetry_scene-12_DataVizReveal.mp4` | ✓ | What it tells you |
| 13 | 5:08 | 4s | `poetry_scene-13_CounterReveal.mp4` | ✓ | times you've heard the lyric before it landed |
| 14 | 5:19 | 6s | `poetry_scene-14_ImageTextReveal.mp4` | ✓ | It dips its fingers in every colour |
| 15 | 5:36 | 5s | `poetry_scene-15_WordReveal.mp4` | ✓ | (visual / animation — no text) |
| 16 | 5:56 | 6s | `poetry_scene-16_AtmosphericQuote.mp4` | ✓ | It is not a small thing. It is the whole thing. |

Filename pattern: `poetry_scene-NN_<Component>.mp4`. `Exact? ✓` = anchored to a verbatim spoken phrase; `~est` = interpolated estimate.
