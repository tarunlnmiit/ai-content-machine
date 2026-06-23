# DS — Manual Overlay Placement (2026-W24)

**Clips:** `output/animations/2026-W24/overlay-scenes/ds_scene-*.mp4`

## How (DaVinci, minimal friction)
1. Talking-head video on track **V1**.
2. Each overlay clip on **V2 above it**, starting at its **Time**. Clips are full-frame with an opaque background → they fully cover V1 for their **Dur** = a clean cutaway. No scaling needed.
3. Want the speaker still visible? Scale the V2 clip to ~35% and park it left/right — the card reads as a side panel.

## ⚠️ Timing rule
Times are measured from your **first spoken word**. If your edited timeline has an intro or lead silence before the first word, **add that offset to every Time**.

> ⚠️ **3 scene(s) have estimated (interpolated) times** — scene-09, scene-13, scene-17. These weren't spoken verbatim (e.g. on-screen code or heavy paraphrase); eyeball and nudge them.

## Placement table

| # | Time | Dur | File (in `overlay-scenes/`) | Exact? | Shows on screen |
|---|------|-----|------------------------------|--------|-----------------|
| 01 | 0:09 | 7s | `ds_scene-01_NumberedTips.mp4` | ✓ | A Real Mess |
| 02 | 0:33 | 6s | `ds_scene-02_CounterReveal.mp4` | ✓ | weeks cleaning before any analysis |
| 03 | 1:20 | 6s | `ds_scene-03_AtmosphericQuote.mp4` | ✓ | Data interrogation should feel like conversation, not combat. |
| 04 | 1:28 | 7s | `ds_scene-04_NumberedTips.mp4` | ✓ | Four Pandas Skills |
| 05 | 1:28 | 7s | `ds_scene-05_DataPipelineFlow.mp4` | ✓ | (visual / animation — no text) |
| 06 | 1:40 | 5s | `ds_scene-06_CounterReveal.mp4` | ✓ | unfamiliar dataset to workable |
| 07 | 1:46 | 6s | `ds_scene-07_ConceptExplainer.mp4` | ✓ | Pandas Builds on NumPy |
| 08 | 2:14 | 7s | `ds_scene-08_CodeAnnotation.mp4` | ✓ | (visual / animation — no text) |
| 09 | 3:39 | 6s | `ds_scene-09_DataVizReveal.mp4` | ~est | df.shape |
| 10 | 5:05 | 5s | `ds_scene-10_CounterReveal.mp4` | ✓ | seconds to spot bad columns |
| 11 | 5:51 | 5s | `ds_scene-11_WordReveal.mp4` | ✓ | (visual / animation — no text) |
| 12 | 7:04 | 5s | `ds_scene-12_CounterReveal.mp4` | ✓ | of real Pandas work is selecting |
| 13 | 7:16 | 7s | `ds_scene-13_CodeAnnotation.mp4` | ~est | (visual / animation — no text) |
| 14 | 7:29 | 7s | `ds_scene-14_ToolComparison.mp4` | ✓ | (visual / animation — no text) |
| 15 | 8:38 | 5s | `ds_scene-15_AtmosphericQuote.mp4` | ✓ | Cleaning is analysis. You can't separate them. |
| 16 | 19:43 | 7s | `ds_scene-16_CodeAnnotation.mp4` | ✓ | (visual / animation — no text) |
| 17 | 23:47 | 7s | `ds_scene-17_CodeAnnotation.mp4` | ~est | (visual / animation — no text) |
| 18 | 27:50 | 7s | `ds_scene-18_ToolComparison.mp4` | ✓ | (visual / animation — no text) |
| 19 | 28:43 | 6s | `ds_scene-19_TransformationArc.mp4` | ✓ | (visual / animation — no text) |
| 20 | 29:36 | 6s | `ds_scene-20_HabitLoop.mp4` | ✓ | The Four-Step Pass |

Filename pattern: `ds_scene-NN_<Component>.mp4`. `Exact? ✓` = anchored to a verbatim spoken phrase; `~est` = interpolated estimate.
