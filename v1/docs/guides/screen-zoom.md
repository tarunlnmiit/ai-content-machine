# Screen-recording auto-zoom (`lib/screen_zoom.py`)

Makes screen recordings more legible on a phone. A raw capture cropped to 9:16
still shows tiny UI text; this detects the dense-content region and zooms into it
so the text that matters is larger. Created 2026-07-01.

## How it works

1. Samples frames, builds an edge-density map (Pillow `FIND_EDGES`).
2. **Trims low-energy margins** (empty black / whitespace) via a percentile on the
   per-column and per-row energy → a content bounding box.
3. Locks the box to the target aspect and **clamps the zoom** (`MAX_ZOOM = 1.9`).
4. Crops to the box, scales to target dims (`1080×1920` default), adds a subtle punch-in.

Falls back to a centered cover-crop if Pillow is missing or detection fails.

## Usage

```bash
python3 -m lib.screen_zoom --in screen.mp4 --out screen_zoomed.mp4          # 9:16
python3 -m lib.screen_zoom --in screen.mp4 --out wide.mp4 --width 1920 --height 1080
```

```python
from lib.screen_zoom import zoom_to_content
zoom_to_content(src, dst, target_w=1080, target_h=1920)
```

## Honest limits

- The zoom is **conservative on purpose**: it won't crop aggressively enough to lose
  content that scrolls through the clip, so on a heavily bottom-weighted screen (lots of
  black + a text block) the gain is modest (~1.3×), not dramatic.
- Best gains: captures with large empty margins. Minimal (safe) change: a full-bleed
  editor that already fills the frame.
- Validated on the reel's ChatGPT segment (1080×1920): detected box `832×1479`, text
  enlarged ~30%, dead right margin trimmed. `py_compile` clean.

## Wiring

**Opt-in.** Apply it to a screen-recording segment before the plain `crop_vertical`
column crop in `clip_shorts.py` or the voiceover screen mode (`--base-video`). It's not
auto-wired into the crop path to avoid surprising over-crops — turn it on where you know
the source is a screen capture with wasted margins.
