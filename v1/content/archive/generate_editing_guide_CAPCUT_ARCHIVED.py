#!/usr/bin/env python3
"""
Generate detailed CapCut editing guide per niche with B-roll clip references.
Step-by-step walkthrough for assembling raw clips into final video.

Usage:
  python3 scripts/generate_editing_guide.py --input content/blogs/2026-04-30-*.md --niche ds
  python3 scripts/generate_editing_guide.py --input content/blogs/2026-05-03-life-*.md --niche life
  python3 scripts/generate_editing_guide.py --input content/blogs/2026-05-03-poetry-*.md --niche poetry
"""

import argparse
import os
import json
from pathlib import Path

EDITING_GUIDES = {
    "ds": {
        "title": "Data Science Video — CapCut Editing Guide",
        "overview": "Assemble: voiceover + screen recording → add captions, B-roll (intro/outro), music",
        "steps": [
            {
                "phase": "PREP",
                "title": "Import Raw Assets into CapCut",
                "steps": [
                    "Open CapCut → New Project → 1080×1920 (portrait, allows flexibility)",
                    "File → Import:",
                    "  - code_demo_screen_recording.mp4 (your screen recording with code)",
                    "  - optional B-roll clips (intro/outro visuals from assets/videos/{slug}/)",
                    "  - voiceover audio file (assets/audio/{slug}_voiceover.wav)",
                    "Files appear in timeline bottom panel"
                ]
            },
            {
                "phase": "ASSEMBLY",
                "title": "Arrange Clips and Audio in Timeline",
                "steps": [
                    "Drag screen recording to main timeline (video track)",
                    "Drag voiceover audio file to audio track below",
                    "Sync audio with video (should align naturally)",
                    "Optional: add B-roll for intro (:10-:15) and outro (:10-:15)",
                    "Trim screen recording to match voiceover (should be tight fit)",
                    "Target total length: 5-8 minutes (check timer top-right)",
                    "Add fade transitions between screen recording and B-roll (0.3s)"
                ]
            },
            {
                "phase": "CAPTIONS",
                "title": "Add Auto-Captions from Voiceover",
                "steps": [
                    "Select voiceover audio track → Text → Auto Captions",
                    "CapCut processes (~2-3 min wait) → captions appear on screen recording",
                    "Review and correct captions:",
                    "  - Fix tech terms (Python, TensorFlow, API, etc.)",
                    "  - Remove filler words (umm, uh, like, so)",
                    "  - Check accuracy of variable names and code references",
                    "Position captions at bottom (don't cover code on screen)",
                    "TIP: tap caption line to edit inline"
                ]
            },
            {
                "phase": "B-ROLL INSERTION",
                "title": "Add Optional B-roll for Intro/Outro",
                "steps": [
                    "Optional: add B-roll clips from assets/videos/{slug}/ for polish",
                    "Intro B-roll: layer before screen recording starts (:10-:15)",
                    "  - Use clip(s) matching first B-ROLL cue from script",
                    "  - Fade from B-roll into screen recording (0.3s transition)",
                    "Outro B-roll: add after screen recording ends (:10-:15)",
                    "  - Use clip(s) matching last B-ROLL cue from script",
                    "  - Fade from screen recording into B-roll (0.3s transition)",
                    "If no B-roll desired, skip — screen recording alone is sufficient"
                ]
            },
            {
                "phase": "AUDIO",
                "title": "Add Background Music (Optional)",
                "steps": [
                    "Optional: add background music for polish",
                    "Audio library → search 'lo-fi' or 'focus' or 'tech'",
                    "Drag music track to separate audio layer (below voiceover)",
                    "Music should start :05 in (after intro hook)",
                    "Adjust volume: tap music → Volume slider → set to :15 (voice is primary, music background only)",
                    "Trim music to match video end time (drag audio clip edge)",
                    "If voiceover is clear without music, skip — not required"
                ]
            },
            {
                "phase": "TEXT OVERLAYS",
                "title": "Add Optional Text Graphics",
                "steps": [
                    "Optional: add text overlays for emphasis",
                    "Opening text (start of screen recording):",
                    "  - Tap Text → add new text box",
                    "  - Type: [MAIN TOPIC / PROBLEM]",
                    "  - Position top-left or center, bold font (40-48pt)",
                    "  - Color: white or neon (good contrast against code)",
                    "Key code text (during critical code section):",
                    "  - Add 1-2 text boxes highlighting key variable or function names",
                    "  - Position bottom corner, smaller font (24-32pt), don't cover code",
                    "Closing text (end of screen recording):",
                    "  - Add text: [KEY TAKEAWAY / NEXT STEP]",
                    "  - Position bottom-center, readable, fades out with B-roll"
                ]
            },
            {
                "phase": "SPEED ADJUSTMENT",
                "title": "Slow Down Code Demo if Needed",
                "steps": [
                    "Code demo feeling rushed? Select code clip → Speed → 0.8x (20% slower)",
                    "Check: still under 4-6 min total?",
                    "If over, trim clip or revert to 1.0x",
                    "Talking head clips: keep at 1.0x (natural pace)"
                ]
            },
            {
                "phase": "EXPORT",
                "title": "Final Export",
                "steps": [
                    "Review timeline one final time:",
                    "  ✓ Screen recording in focus",
                    "  ✓ Voiceover clear and synced",
                    "  ✓ Captions readable and accurate",
                    "  ✓ Total time 5-8 min",
                    "  ✓ Audio levels balanced (voiceover primary, music background)",
                    "  ✓ Text overlays visible (don't obscure code)",
                    "  ✓ B-roll transitions smooth if included",
                    "Export → MP4, 1080p, H.264",
                    "Filename: {slug}.mp4",
                    "Save to: assets/video/edited/{slug}.mp4"
                ]
            }
        ]
    },
    "life": {
        "title": "Life & Self-Dev Video — CapCut Editing Guide",
        "overview": "Assemble: B-roll clips matching script sections + voiceover audio + music + captions",
        "steps": [
            {
                "phase": "PREP",
                "title": "Import Assets into CapCut",
                "steps": [
                    "Open CapCut → New Project → 1080×1920 (portrait)",
                    "File → Import:",
                    "  - All B-roll clips from assets/videos/{slug}/ (organized per section from VIDEO_MAP.json)",
                    "  - Voiceover audio from assets/audio/{slug}_voiceover.wav"
                ]
            },
            {
                "phase": "ASSEMBLY",
                "title": "Build B-roll Timeline to Match Voiceover",
                "steps": [
                    "Reference: content/scripts/{slug}_PRODUCTION_GUIDE.md (maps sections → clips)",
                    "Arrange B-roll clips in video track in script order:",
                    "  1. Section 1: clip_00 (trim to match voiceover section duration)",
                    "  2. Section 2: clip_01 (trim to match)",
                    "  3. Section 3: clip_02 (trim to match)",
                    "  4. Continue for each script section",
                    "Add fade transitions between clips (0.3s)",
                    "Total timeline should match voiceover audio duration (~7-9 min)"
                ]
            },
            {
                "phase": "VOICEOVER SYNC",
                "title": "Add Voiceover Audio and Sync to B-roll",
                "steps": [
                    "Drag voiceover audio file to audio track",
                    "Play timeline: B-roll should visually align with voiceover narration",
                    "Trim individual clips to fit voiceover sections (drag clip edges in timeline)",
                    "Check: no gaps or overlaps, smooth transitions",
                    "Optional: add auto-captions to voiceover if desired (Text → Auto Captions)",
                    "If adding captions, review and fix any misheard words/technical terms"
                ]
            },
            {
                "phase": "TEXT OVERLAYS",
                "title": "Add Section Title Text Overlays",
                "steps": [
                    "At start of each major section, add text overlay with section title:",
                    "  - Extract from script: '**[SECTION TITLE]**'",
                    "  - Position top or center, 40-48pt font, white with shadow",
                    "  - Duration: :03-:05 (time to read)",
                    "Optional: add 1-2 key quote/insight text overlays mid-video (position bottom, smaller font 24-32pt)",
                    "All text should fade in/out smoothly"
                ]
            },
            {
                "phase": "MUSIC",
                "title": "Add Ambient Background Music",
                "steps": [
                    "Audio library → search 'inspirational', 'lo-fi', 'acoustic', or 'ambient'",
                    "Drag music to separate audio layer (below voiceover)",
                    "Set volume to :20-:25 (music subtle, voiceover primary)",
                    "Music should fade in gently after opening section (:15-:20 mark)",
                    "Fade out music in closing section (last :15-:20)",
                    "Trim music to match timeline total length"
                ]
            },
            {
                "phase": "TIMING CHECK",
                "title": "Verify Video Matches Voiceover Duration",
                "steps": [
                    "Play full timeline (watch entire video)",
                    "Check: B-roll clips end exactly when voiceover ends (no trailing silence/black)",
                    "Check: transitions feel natural (no abrupt cuts)",
                    "Adjust clip trim points if timing is off",
                    "Target: 7-9 min (should match production guide estimate)"
                ]
            },
            {
                "phase": "CLOSING HOOK",
                "title": "Add Call-to-Action Text",
                "steps": [
                    "At very end of voiceover, add closing text overlay:",
                    "  - Examples: 'What's your next step?', 'Share your thoughts in comments', 'Follow for more'",
                    "Position bottom-center, readable font (32-40pt), white",
                    "Duration: last :10-:15 of video",
                    "Optional: fade to black after CTA (:02)"
                ]
            },
            {
                "phase": "EXPORT",
                "title": "Final Export",
                "steps": [
                    "Preview full video one final time:",
                    "  ✓ B-roll clips arranged per script sections",
                    "  ✓ Voiceover clear and synced to B-roll",
                    "  ✓ Transitions smooth between clips",
                    "  ✓ Captions (if added) readable and accurate",
                    "  ✓ Text overlays visible and well-timed",
                    "  ✓ Music balanced (not overpowering voiceover)",
                    "  ✓ Total time 7-9 min (matches voiceover duration)",
                    "  ✓ Closing CTA visible",
                    "Export → MP4, 1080p, H.264",
                    "Filename: {slug}.mp4",
                    "Save to: assets/video/edited/{slug}.mp4"
                ]
            }
        ]
    },
    "poetry": {
        "title": "Poetry & Quotes Video — CapCut Editing Guide",
        "overview": "Assemble: B-roll clips + your voiceover narration (poem reading + commentary) + contemplative music",
        "steps": [
            {
                "phase": "PREP",
                "title": "Import Assets into CapCut",
                "steps": [
                    "Open CapCut → New Project → 1080×1920 (portrait)",
                    "File → Import:",
                    "  - All B-roll clips from assets/videos/{slug}/ (artistic, contemplative visuals)",
                    "  - Voiceover audio from assets/audio/{slug}_voiceover.wav (poem reading + your commentary)"
                ]
            },
            {
                "phase": "OPENING SLIDE",
                "title": "Create Poem Title Slide",
                "steps": [
                    "Add blank background (dark, subtle color or image)",
                    "Text → add poem title and full poem text",
                    "Format:",
                    "  - Title: 48pt, white, centered top",
                    "  - Poem body: 36pt, white, centered middle",
                    "  - Attribution: 20pt, light gray, bottom right",
                    "Duration: :30-:45 (viewers read text)",
                    "Add fade in/out transitions"
                ]
            },
            {
                "phase": "B-ROLL ASSEMBLY",
                "title": "Build B-roll Timeline Matching Voiceover",
                "steps": [
                    "Reference: content/scripts/{slug}_PRODUCTION_GUIDE.md (sections → clips)",
                    "Arrange B-roll clips in video track per script sections:",
                    "  1. Section 1: clip_00 (poem reading begins, trim to section duration)",
                    "  2. Section 2: clip_01 (poetry continues, trim to match voiceover)",
                    "  3. Section 3: clip_02 (commentary section, trim to match)",
                    "  4. Continue for each voiceover section",
                    "Add dissolve/fade between clips (0.5s — contemplative pace)",
                    "Total timeline should match voiceover duration (~7-9 min)"
                ]
            },
            {
                "phase": "VOICEOVER SYNC",
                "title": "Add Voiceover Audio and Sync",
                "steps": [
                    "Drag voiceover audio (poem reading + your commentary) to audio track",
                    "Play timeline: B-roll should match voiceover narration progression",
                    "Trim individual B-roll clips to fit voiceover sections (drag clip edges)",
                    "Check: no gaps or overlaps between clips",
                    "Optional: add auto-captions to voiceover if desired (Text → Auto Captions)",
                    "If captions added, position them subtly (smaller font, semi-transparent, don't obscure B-roll)"
                ]
            },
            {
                "phase": "TEXT OVERLAYS",
                "title": "Add Section Title and Key Insight Text",
                "steps": [
                    "At start of poem reading, add opening text overlay:",
                    "  - Type: poem title or opening phrase",
                    "  - Position: top-center, 40-48pt, white, contemplative font",
                    "  - Duration: :03-:05",
                    "Optional: at midpoint, add one key insight or quote text overlay:",
                    "  - Position: center or bottom, 32-36pt, white",
                    "  - Duration: :03-:05",
                    "At very end (your commentary closing), add closing text:",
                    "  - Examples: poem title, author, 'What does this poem mean to you?'",
                    "  - Position: bottom-center, 28-32pt",
                    "  - Duration: last :10-:15"
                ]
            },
            {
                "phase": "MUSIC",
                "title": "Add Contemplative Background Music",
                "steps": [
                    "Audio library → search 'ambient', 'piano', 'string', 'lo-fi instrumental', 'meditation'",
                    "Examples: Ólafur Arnalds, Tycho, Nils Frahm style",
                    "Drag music to separate audio layer (below voiceover)",
                    "Set volume to :15-:20 (very subtle, voice primary)",
                    "Music should fade in gently after opening slide (:20 mark)",
                    "Fade out music in final section (last :15-:20)",
                    "Trim music to match timeline total length"
                ]
            },
            {
                "phase": "TIMING CHECK",
                "title": "Verify Pace and Duration",
                "steps": [
                    "Play full timeline (watch entire video)",
                    "Check: pacing is SLOW — no rushing, allow breathing room",
                    "Check: B-roll clips transition smoothly (dissolves not abrupt cuts)",
                    "Check: voiceover ends exactly when video ends (no trailing silence)",
                    "Adjust clip trim points if needed",
                    "Target: 7-9 min (contemplative pace, should match production guide)"
                ]
            },
            {
                "phase": "CLOSING CREDITS",
                "title": "Add End Credits Slide",
                "steps": [
                    "After voiceover ends, fade to black (:01-:02)",
                    "Add text slide with:",
                    "  - Poem title (32pt, white)",
                    "  - 'By [Author]' (24pt, light gray)",
                    "  - Your blog/channel link (optional, 20pt)",
                    "  - Music attribution (if using copyrighted music, 16pt)",
                    "Hold for :03-:05",
                    "Fade out to black"
                ]
            },
            {
                "phase": "EXPORT",
                "title": "Final Export",
                "steps": [
                    "Preview entire video one final time:",
                    "  ✓ Opening slide readable",
                    "  ✓ B-roll clips arranged per script sections",
                    "  ✓ Voiceover (poem reading + commentary) clear and well-paced",
                    "  ✓ B-roll transitions smooth (contemplative dissolves)",
                    "  ✓ Captions (if added) subtle and readable",
                    "  ✓ Text overlays well-timed and readable",
                    "  ✓ Music balanced (supportive, not overpowering)",
                    "  ✓ Total time 7-9 min (matches voiceover duration)",
                    "  ✓ Closing credits visible",
                    "Export → MP4, 1080p, H.264",
                    "Filename: {slug}.mp4",
                    "Save to: assets/video/edited/{slug}.mp4"
                ]
            }
        ]
    }
}

def load_video_map(blog_stem: str) -> dict:
    """Load VIDEO_MAP.json if it exists."""
    video_map_path = Path(f"assets/videos/{blog_stem}/VIDEO_MAP.json")
    if video_map_path.exists():
        with open(video_map_path, "r") as f:
            return json.load(f)
    return {}

def generate_broll_reference(video_map: dict, niche: str) -> str:
    """Generate B-roll clip references for insertion."""
    if not video_map:
        return ""

    clips = list(video_map.items())
    if niche == "ds":
        if len(clips) < 2:
            return f"""**Available B-roll clips:** {len(clips)} found (need at least 2)
Clips available:
{chr(10).join(f"  - {fn}: {md['duration']}s ({md['source']}) — {md['search_term']}" for fn, md in clips)}

**Note:** Not enough clips for suggested placement. Use as available.
"""
        return f"""**Available B-roll clips:**
- {clips[0][0]} ({clips[0][1]['duration']}s) — {clips[0][1]['search_term']}
- {clips[1][0]} ({clips[1][1]['duration']}s) — {clips[1][1]['search_term']}
{f"- {clips[2][0]} ({clips[2][1]['duration']}s) — {clips[2][1]['search_term']}" if len(clips) > 2 else ""}

**Suggested placement:** Use clip_00 between screen intro & demo (fade 0.3s), clip_01 between demo & recap
"""
    elif niche == "life":
        clip_list = chr(10).join(f"  - {fn}: {md['duration']}s ({md['source']}) — {md['search_term']}" for fn, md in clips[:min(5, len(clips))])
        return f"""**Available B-roll clips:** {len(clips)} total
{f"- First 3 search terms: {clips[0][1]['search_term']}, {clips[1][1]['search_term']}, {clips[2][1]['search_term']}" if len(clips) >= 3 else ""}
- Suggested: Layer throughout voiceover, changing clips every :20-:30s for visual variety

**Clip details:**
{clip_list}
"""
    elif niche == "poetry":
        clip_list = chr(10).join(f"  - {fn}: {md['duration']}s ({md['source']}) — {md['search_term']}" for fn, md in clips[:min(6, len(clips))])
        return f"""**Available artistic B-roll clips:** {len(clips)} total
- Suggested sequence: clips_00 → clips_01 → clips_02 → clips_03 (each :10-:15)
- Layer over poem reading voiceover for contemplative visual flow

**Clip details:**
{clip_list}
"""
    return ""

def generate_guide(blog_path: str, niche: str) -> str:
    """Generate detailed CapCut editing guide with B-roll references."""

    if niche not in EDITING_GUIDES:
        print(f"Error: niche '{niche}' not found. Choose: ds, life, poetry")
        return ""

    blog_stem = Path(blog_path).stem
    guide_data = EDITING_GUIDES[niche]
    video_map = load_video_map(blog_stem)
    broll_ref = generate_broll_reference(video_map, niche)

    output = f"""# {guide_data['title']}
**Video:** `{blog_stem}`

**Overview:** {guide_data['overview']}

---

"""
    if broll_ref:
        output += f"""## B-ROLL ASSETS

{broll_ref}

---

"""

    for phase_section in guide_data['steps']:
        output += f"""## {phase_section['phase']}: {phase_section['title']}

"""
        for i, step in enumerate(phase_section['steps'], 1):
            if step.startswith("  "):
                output += f"{step}\n"
            else:
                output += f"{i}. {step}\n"

        output += "\n"

    output += f"""---

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

Generated: {blog_stem}
"""

    return output

def main():
    parser = argparse.ArgumentParser(description="Generate CapCut editing guide")
    parser.add_argument("--input", required=True, help="Blog markdown file")
    parser.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: {args.input} not found")
        return

    guide = generate_guide(args.input, args.niche)

    output_path = Path(args.input).parent / f"{Path(args.input).stem}_CAPCUT_EDITING_GUIDE.md"
    with open(output_path, "w") as f:
        f.write(guide)

    print(f"✓ Editing guide saved → {output_path}")

if __name__ == "__main__":
    main()
