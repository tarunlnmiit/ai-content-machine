# Data Science Video — CapCut Editing Guide
**Video:** `2026-05-12_data_science_tech_ml-model-sql-translation`

**Overview:** Assemble: talking head intro → screen demo → talking head recap + add captions, B-roll, music

---

## B-ROLL ASSETS

**Available B-roll clips:**
- 2026-05-12_data_science_tech_ml-model-sql-translation_clip_00.mp4 (26s) — programming code editor
- 2026-05-12_data_science_tech_ml-model-sql-translation_clip_01.mp4 (55s) — programming code editor
- 2026-05-12_data_science_tech_ml-model-sql-translation_clip_02.mp4 (9s) — data pipeline workflow

**Suggested placement:** Use clip_00 between intro & demo (fade 0.3s), clip_01 between demo & recap


---

## PREP: Import Raw Clips into CapCut

1. Open CapCut → New Project → 1080×1920 (portrait, allows flexibility)
2. File → Import → select all 3 raw video files:
  - intro_talking_head.mp4
  - code_demo_screen_recording.mp4
  - recap_talking_head.mp4
6. Clips appear in timeline bottom panel

## ASSEMBLY: Arrange Clips in Timeline

1. Drag clips to main timeline in order:
  1. intro_talking_head (preview right side)
  2. code_demo_screen_recording
  3. recap_talking_head
5. Trim each clip if needed (double-tap clip → trim handle)
6. Target total length: 4-6 minutes (check timer top-right)
7. Gaps between clips auto-fill with black (okay for now)

## CAPTIONS: Add Auto-Captions

1. Select FIRST talking head clip → Text menu → Auto Captions
2. CapCut processes (~2-3 min wait) → captions appear
3. Review captions:
  - Fix tech terms (if 'Python' → 'python', correct)
  - Check speaker name (should be blank or your name)
  - Remove filler (umm, uh, like)
7. Repeat for SECOND talking head clip (code demo likely has no audio, skip)
8. Repeat for RECAP talking head clip
9. TIP: tap caption line to edit inline

## B-ROLL INSERTION: Insert Stock Video Clips (if using)

1. Import B-roll clips from assets/videos/{slug}/
2. Drag one :20-:30 clip between talking head → code demo
3. Drag another between code demo → recap
4. Position in timeline at natural transition points
5. Trim to fit (drag edge)
6. Add fade transition (tap transition icon, select Fade, 0.3s)

## AUDIO: Add Background Music

1. Audio library → search 'lo-fi' or 'focus' or 'tech'
2. Drag music track to audio layer (below video)
3. Music should start :05 in (after intro hook)
4. Adjust volume: tap music → Volume slider → set to :20 (so voice loud, music background)
5. If music too loud/distracting: lower to :15
6. Trim music to match video end time (drag audio clip edge)

## TEXT OVERLAYS: Add Text Graphics

1. Opening text (during intro talking head):
  - Tap Text → add new text box
  - Type: [MAIN TOPIC]
  - Position top/center, large bold font (50pt+)
  - Color: white or neon (contrast to background)
6. Key code text (during demo):
  - Add 2-3 text boxes highlighting key lines from code
  - Position corner, smaller font (28-36pt)
9. Closing text (during recap):
  - Add text: [KEY TAKEAWAY]
  - Position bottom-center, readable

## SPEED ADJUSTMENT: Slow Down Code Demo if Needed

1. Code demo feeling rushed? Select code clip → Speed → 0.8x (20% slower)
2. Check: still under 4-6 min total?
3. If over, trim clip or revert to 1.0x
4. Talking head clips: keep at 1.0x (natural pace)

## EXPORT: Final Export

1. Check timeline one more time:
  ✓ All clips in order
  ✓ Captions readable and accurate
  ✓ Total time 4-6 min
  ✓ Audio levels balanced (voice > music)
  ✓ Text overlays don't cover faces
7. Export → MP4, 1080p
8. Filename: {slug}.mp4
9. Save to: assets/video/edited/{slug}.mp4

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

Generated: 2026-05-12_data_science_tech_ml-model-sql-translation
