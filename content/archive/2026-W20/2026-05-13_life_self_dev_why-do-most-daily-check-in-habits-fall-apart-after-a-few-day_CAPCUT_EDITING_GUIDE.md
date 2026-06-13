# Life & Self-Dev Video — CapCut Editing Guide
**Video:** `2026-05-13_life_self_dev_why-do-most-daily-check-in-habits-fall-apart-after-a-few-day`

**Overview:** Assemble: B-roll montage + voiceover → main story → key points w/ B-roll → closing + music + captions

---

## PREP: Import Raw Clips into CapCut

1. Open CapCut → New Project → 1080×1920 (portrait)
2. File → Import all clips:
  - broll_clip_1.mp4, broll_clip_2.mp4, ... (4-5 clips)
  - main_story_talking_head.mp4
  - key_point_1.mp4, key_point_2.mp4, key_point_3.mp4
  - closing_talking_head.mp4

## ASSEMBLY: Build Timeline Structure

1. Arrange in timeline:
  1. B-ROLL MONTAGE (arrange 4-5 B-roll clips, trim to :45 total)
  2. MAIN STORY talking head (trim to 3:00)
  3. KEY POINTS (3 clips, :20 each = 1:00 total)
  4. CLOSING talking head (trim to :45)
6. Total target: 4:30-5:30
7. Gaps auto-fill black (will hide with B-roll + music)

## B-ROLL LAYERING: Add Stock B-roll Between Segments

1. Import stock clips from assets/videos/{slug}/VIDEO_MAP.json
2. Insert between talking head segments:
  - Between intro voiceover + main story: one :20 clip
  - Between main story + key points: one :20 clip
  - Between key points + closing: one :15 clip
6. Trim to fit transitions smoothly
7. Add fade transition (0.3s) between each segment

## VOICEOVER + CAPTIONS: Add Voiceover to B-roll Montage

1. B-ROLL MONTAGE at start needs voiceover narration:
  - Create voiceover track (Audio → Record Voiceover)
  - Read intro hook over B-roll (:45 duration)
  - Example: 'Many people struggle with daily habits. Here's how I changed mine.'
5. Auto Captions for talking head clips:
  - Select main story → Text → Auto Captions (wait 2-3 min)
  - Select key points → Auto Captions (repeat)
  - Select closing → Auto Captions
9. Review all captions, fix as needed

## TEXT OVERLAYS: Highlight Key Insights

1. For each KEY POINT clip, add text overlay:
  - Point 1: 'Start Small'
  - Point 2: 'Track Progress'
  - Point 3: 'Share the Journey'
5. Position at bottom/center, :18pt+ font, white with shadow
6. Fade in at start of clip, fade out at end

## MUSIC: Add Ambient Background Music

1. Audio library → search 'inspirational' or 'lo-fi'
2. Drag music to audio layer
3. Set volume to :25 (music is background, voices primary)
4. Music should fade in after B-roll intro (:30 mark)
5. Fade out music at closing talking head (last :15)
6. Trim music to match timeline length

## PACING: Adjust Speed for Emotion

1. Main story clip: keep at 1.0x (natural, intimate pace)
2. Key points clips: can speed to 1.1x if punchy/energetic
3. B-roll between segments: check total time still 4:30-5:30
4. Voiceover montage: natural pace (:45 for ~100 words)

## CLOSING HOOK: Add Call-to-Action Text

1. During closing talking head, add text overlay:
  - 'What habit will YOU change this week?'
  - OR 'Drop your answer in the comments'
4. Position bottom, readable, stays for last :20

## EXPORT: Final Export

1. Preview full video (play button, watch through):
  ✓ Voiceover clear over B-roll
  ✓ Transitions smooth (no jarring cuts)
  ✓ Music balanced (not overpowering)
  ✓ Captions readable on all talking head clips
  ✓ Text overlays visible (white on video background)
  ✓ Total time 4:30-5:30
  ✓ Closing has CTA
9. Export → MP4, 1080p
10. Filename: {slug}.mp4
11. Save to: assets/video/edited/{slug}.mp4

---

## Keyboard Shortcuts (CapCut)

- **Space** — Play/pause
- **T** — Add text
- **M** — Add music
- **Ctrl+Z** — Undo
- **Ctrl+S** — Auto-save

---

## Troubleshooting

**Audio sync is off?**
- Select clip → Audio → Sync Audio → reselect video file

**Captions wrong/messed up?**
- Delete caption → re-import clip → re-run Auto Captions

**Video takes forever to export?**
- Lower resolution to 720p if testing
- Final export should be 1080p (check before saving)

**Music too loud/soft?**
- Select music clip → Volume slider (top-left)
- Adjust to :15-:30 range (voice always primary)

**Text overlays hard to read?**
- Add drop shadow (Text → Shadow)
- Increase font size
- Choose white or bright color for dark backgrounds

---

Generated: 2026-05-13_life_self_dev_why-do-most-daily-check-in-habits-fall-apart-after-a-few-day
