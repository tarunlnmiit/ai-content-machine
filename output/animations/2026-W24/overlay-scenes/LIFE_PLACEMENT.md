# LIFE — Manual Overlay Placement (2026-W24)

**Clips:** `output/animations/2026-W24/overlay-scenes/life_scene-*.mp4`

## How (DaVinci, minimal friction)
1. Talking-head video on track **V1**.
2. Each overlay clip on **V2 above it**, starting at its **Time**. Clips are full-frame with an opaque background → they fully cover V1 for their **Dur** = a clean cutaway. No scaling needed.
3. Want the speaker still visible? Scale the V2 clip to ~35% and park it left/right — the card reads as a side panel.

## ⚠️ Timing rule
Times are measured from your **first spoken word**. If your edited timeline has an intro or lead silence before the first word, **add that offset to every Time**.

> ⚠️ **2 scene(s) have estimated (interpolated) times** — scene-09, scene-10. These weren't spoken verbatim (e.g. on-screen code or heavy paraphrase); eyeball and nudge them.

## Placement table

| # | Time | Dur | File (in `overlay-scenes/`) | Exact? | Shows on screen |
|---|------|-----|------------------------------|--------|-----------------|
| 01 | 0:00 | 6s | `life_scene-01_AtmosphericQuote.mp4` | ✓ | The most productive people don't have complicated systems. They have a handful of small ha |
| 02 | 0:19 | 6s | `life_scene-02_TransformationArc.mp4` | ✓ | (visual / animation — no text) |
| 03 | 0:40 | 6s | `life_scene-03_CounterReveal.mp4` | ✓ | Simple habits, zero apps |
| 04 | 1:06 | 8s | `life_scene-04_NumberedTips.mp4` | ✓ | The Shutdown Ritual |
| 05 | 1:29 | 5s | `life_scene-05_CounterReveal.mp4` | ✓ | Minutes to close the day |
| 06 | 1:55 | 6s | `life_scene-06_ImageTextReveal.mp4` | ✓ | Physically at the table. Mentally still inside my laptop. |
| 07 | 2:24 | 6s | `life_scene-07_ConceptExplainer.mp4` | ✓ | The Zeigarnik Effect |
| 08 | 2:55 | 5s | `life_scene-08_CounterReveal.mp4` | ✓ | Minutes to empty your head |
| 09 | 3:06 | 5s | `life_scene-09_CounterReveal.mp4` | ~est | Tabs open in your head |
| 10 | 3:17 | 6s | `life_scene-10_BrowserTabOverload.mp4` | ~est | (visual / animation — no text) |
| 11 | 3:28 | 6s | `life_scene-11_ConceptExplainer.mp4` | ✓ | Offloading |
| 12 | 4:29 | 5s | `life_scene-12_WordReveal.mp4` | ✓ | (visual / animation — no text) |
| 13 | 4:36 | 7s | `life_scene-13_ToolComparison.mp4` | ✓ | (visual / animation — no text) |
| 14 | 5:26 | 6s | `life_scene-14_ToolComparison.mp4` | ✓ | (visual / animation — no text) |
| 15 | 5:58 | 7s | `life_scene-15_DataVizReveal.mp4` | ✓ | Focus block length vs. real output |
| 16 | 6:07 | 5s | `life_scene-16_CounterReveal.mp4` | ✓ | Minutes lost per context switch |
| 17 | 7:05 | 7s | `life_scene-17_NumberedTips.mp4` | ✓ | Plan tomorrow tonight |
| 18 | 8:30 | 5s | `life_scene-18_AtmosphericQuote.mp4` | ✓ | What gets measured gets noticed. And noticing, it turns out, is most of the work. |
| 19 | 9:37 | 7s | `life_scene-19_HandwrittenReveal.mp4` | ✓ | You don't need all seven. / Start with one. / The one that stings a little — / that's the  |

Filename pattern: `life_scene-NN_<Component>.mp4`. `Exact? ✓` = anchored to a verbatim spoken phrase; `~est` = interpolated estimate.
