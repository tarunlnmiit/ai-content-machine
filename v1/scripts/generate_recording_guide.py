#!/usr/bin/env python3
"""
Generate per-video recording & editing guide based on blog content + niche.
Creates component-by-component breakdown with timing, recording order, and DaVinci Resolve assembly steps.

Usage:
  python3 scripts/generate_recording_guide.py --input content/blogs/2026-04-30-*.md --niche ds
  python3 scripts/generate_recording_guide.py --input content/blogs/2026-05-03-life-*.md --niche life
  python3 scripts/generate_recording_guide.py --input content/blogs/2026-05-03-poetry-*.md --niche poetry
"""

import argparse
import os
from pathlib import Path
from typing import Optional

GUIDES = {
    "ds": {
        "title": "Data Science Video Recording Guide",
        "components": [
            {
                "name": "INTRO (TALKING HEAD)",
                "duration": "0:15-0:30",
                "instructions": [
                    "Record facing camera, clear background",
                    "Hook viewers: state problem or insight from blog",
                    "Example: 'Today I'm breaking down [main concept] that transformed [what it affects]'",
                    "Natural pace, maintain eye contact"
                ],
                "edit_in_davinci": "Import to Media Pool → trim to :30 max → add text overlay with main topic"
            },
            {
                "name": "SCREEN DEMO/CODE",
                "duration": "2:00-3:30",
                "instructions": [
                    "Screen record with 1080p resolution minimum",
                    "Zoom code/terminal to 200% for visibility",
                    "Type or walk through code slowly (assume viewer new to topic)",
                    "Narrate what you're doing: 'First I import X, then set Y'",
                    "Pause on key lines (2-3 sec) so viewers absorb"
                ],
                "edit_in_davinci": "Import screen recording → Fusion Caption Editor → trim dead space → add background music at -20dB"
            },
            {
                "name": "TALKING HEAD (RECAP)",
                "duration": "0:30-1:00",
                "instructions": [
                    "Back to camera, same framing as intro",
                    "Recap what you just showed, connect to blog",
                    "Example: 'So when you run this, you get X benefit. That's why [blog insight] matters.'",
                    "End with one takeaway or next step"
                ],
                "edit_in_davinci": "Import → trim to 1:00 → add closing text (key takeaway)"
            },
            {
                "name": "OPTIONAL: SECOND DEMO OR EXAMPLE",
                "duration": "1:30-2:00",
                "instructions": [
                    "If blog has two major concepts: repeat screen demo for concept #2",
                    "Same format: narrate, pause on key parts, show output/result"
                ],
                "edit_in_davinci": "Import → Auto Captions → trim → match pacing of first demo"
            }
        ],
        "total_video_length": "4:00-6:00",
        "recording_order": [
            "1. Record INTRO talking head (multiple takes, keep best)",
            "2. Record FIRST DEMO screen recording",
            "3. Record RECAP talking head",
            "4. Record SECOND DEMO if time (optional)"
        ],
        "davinci_final_assembly": [
            "Import all clips in order: Intro → Demo1 → Recap → [Demo2]",
            "Auto Caption all (wait 2-3 min)",
            "Review captions, fix any tech terms",
            "Add B-roll video clips between talking head + screen demo (fade transition, :15-:20 each)",
            "Add background music at :30 volume (lo-fi/subtle tech music)",
            "Text overlays: topic title (intro), key code lines (during demo), takeaway (recap)",
            "Export MP4 → assets/video/edited/{slug}.mp4"
        ]
    },
    "life": {
        "title": "Life & Self-Dev Video Recording Guide",
        "components": [
            {
                "name": "B-ROLL MONTAGE + VOICEOVER",
                "duration": "0:30-0:45",
                "instructions": [
                    "Record or gather 4-5 quick clips (:10 each) of related scenes",
                    "Example for 'daily habits': morning routine, workspace, coffee, moment of reflection, nature",
                    "No talking in clips, just visuals",
                    "Will add voiceover in DaVinci Resolve (you narrate: 'Many people struggle with...') "
                ],
                "edit_in_davinci": "Import clips → arrange in sequence → cut to :45 total → add intro voiceover as narrative layer"
            },
            {
                "name": "TALKING HEAD (MAIN STORY)",
                "duration": "2:00-3:00",
                "instructions": [
                    "Record in a calm setting (bedroom, living room, natural light preferred)",
                    "Tell personal story related to blog topic",
                    "Use 'I' language: 'I struggled with X, then I discovered Y'",
                    "Show emotion/authenticity — this isn't data, it's your journey",
                    "Speak naturally, conversational pace"
                ],
                "edit_in_davinci": "Import → Auto Captions → trim to 3:00 max → add subtle background music (:20 volume)"
            },
            {
                "name": "KEY POINTS WITH VISUALS",
                "duration": "1:00-1:30",
                "instructions": [
                    "Record talking head for 2-3 main insights from blog",
                    "One insight per clip (:20-:30 each)",
                    "Example: 'Point #1: Start small. Point #2: Track progress. Point #3: Share with someone.'",
                    "Pause between points (natural silence okay)"
                ],
                "edit_in_davinci": "Import clips → Auto Captions → insert B-roll or text cards between each point (illustrate concept visually)"
            },
            {
                "name": "CLOSING (TALKING HEAD)",
                "duration": "0:30-0:45",
                "instructions": [
                    "Back to camera, same calm setting",
                    "Call to action or reflection question",
                    "Example: 'What's one habit you want to change this week? Drop it in the comments.'",
                    "Genuine, not salesy"
                ],
                "edit_in_davinci": "Import → trim to :45 → add text overlay with question or link"
            }
        ],
        "total_video_length": "4:00-6:30",
        "recording_order": [
            "1. Record B-ROLL clips (can record during week, keep short :10 each)",
            "2. Record MAIN STORY talking head (multiple takes, choose warmest)",
            "3. Record KEY POINTS (3 quick clips)",
            "4. Record CLOSING (one take)"
        ],
        "davinci_final_assembly": [
            "Arrange: B-roll montage → Main story → Key points w/ visuals → Closing",
            "Auto Caption all talking head segments",
            "Between talking head + key points: insert B-roll clips (fade in/out)",
            "Add text overlays on key points (visually reinforce each insight)",
            "Add ambient background music (lo-fi / inspirational, :20-:30 volume throughout)",
            "Adjust pacing: slow on emotional moments, normal on action points",
            "Export MP4 → assets/video/edited/{slug}.mp4"
        ]
    },
    "poetry": {
        "title": "Poetry & Quotes Video Recording Guide",
        "components": [
            {
                "name": "FULL POEM TEXT (ON SCREEN)",
                "duration": "0:30-1:00",
                "instructions": [
                    "Display full poem/quote on screen (large text, artistic background)",
                    "Build in DaVinci Resolve: text appears line-by-line or all at once",
                    "Include attribution (author, year if relevant)",
                    "Music should be contemplative, slow"
                ],
                "edit_in_davinci": "Create title slide with poem text → match to music tempo → fade in/out each line if desired"
            },
            {
                "name": "YOU READING THE POEM",
                "duration": "1:00-1:30",
                "instructions": [
                    "Record talking head, calm lighting, minimal movement",
                    "Read poem aloud slowly, deliberately",
                    "No need to rush — poetry is about rhythm and pause",
                    "If poem has stanzas, natural pause between each",
                    "Inflection: vary tone to match emotion of poem"
                ],
                "edit_in_davinci": "Import voice → Auto Captions off (keep poetry text clean) → sync with poem text slide behind you or voiceover only"
            },
            {
                "name": "YOUR COMMENTARY",
                "duration": "1:00-1:30",
                "instructions": [
                    "Talking head: discuss what the poem means to you, blog context",
                    "Connect to larger theme (from blog title/description)",
                    "Example: 'This poem reminds me of X because Y. In my blog I explore...'",
                    "Tone: reflective, thoughtful"
                ],
                "edit_in_davinci": "Import → Auto Captions → consider adding poem text as subtitle overlay"
            },
            {
                "name": "VISUAL MONTAGE (OPTIONAL)",
                "duration": "0:45-1:15",
                "instructions": [
                    "Gather artistic B-roll matching poem mood (nature, water, sky, abstract)",
                    "Quick cuts (:05-:10 each) set to poem reading as voiceover",
                    "No talking in this segment — just visuals + voiceover of poem"
                ],
                "edit_in_davinci": "Arrange clips to match poem pacing → slow/fade between cuts → layer poem voiceover on top"
            }
        ],
        "total_video_length": "3:30-5:00",
        "recording_order": [
            "1. Record YOU READING poem (take 2-3, choose most natural)",
            "2. Record YOUR COMMENTARY (multiple takes, pick most authentic)",
            "3. Gather/record B-ROLL clips (can be phone video, natural scenes)"
        ],
        "davinci_final_assembly": [
            "Arrange: Poem text slide → You reading → Poem B-roll montage → Your commentary",
            "For poem text slide: large font, centered, artistic background color or subtle image",
            "For reading segment: consider adding subtle visuals (watercolor, gradient, abstract)",
            "Auto Captions for commentary talking head only (NOT for poem reading)",
            "Music: ambient, contemplative (Ólafur Arnalds, piano, string, lo-fi instrumental)",
            "Pacing: slow throughout — let viewers absorb poem meaning",
            "Final touch: fade to black after closing, hold credits/poem info :03-:05",
            "Export MP4 → assets/video/edited/{slug}.mp4"
        ]
    }
}

def generate_guide(blog_path: str, niche: str) -> str:
    """Generate markdown guide for video recording & editing."""

    if niche not in GUIDES:
        print(f"Error: niche '{niche}' not found. Choose: ds, life, poetry")
        return ""

    blog_stem = Path(blog_path).stem
    guide_data = GUIDES[niche]

    output = f"""# {guide_data['title']}
**Video Slug:** `{blog_stem}`

---

## Overview
- **Total video length:** {guide_data['total_video_length']}
- **Format:** Mix of talking head + screen/B-roll + on-screen text
- **End result:** YouTube long-form video (~4-6 min)

---

## Components (In Editing Order)

"""

    for i, component in enumerate(guide_data['components'], 1):
        output += f"""### {i}. {component['name']}
**Duration:** {component['duration']}

**Recording Instructions:**
"""
        for instruction in component['instructions']:
            output += f"- {instruction}\n"

        output += f"""
**How to edit in DaVinci Resolve:**
{component['edit_in_davinci']}

---

"""

    output += f"""## Recording Checklist

**Step 1: Plan your shots**
Record in this order (may vary by scene):
"""
    for step in guide_data['recording_order']:
        output += f"- [ ] {step}\n"

    output += f"""
**Step 2: Quick review**
- [ ] All audio is clear (no background noise)
- [ ] Lighting is consistent
- [ ] Camera stable (tripod or propped up)
- [ ] Microphone positioned well
- [ ] You're comfortable with pacing

---

## DaVinci Resolve Assembly (Final Steps)

"""
    for i, step in enumerate(guide_data['davinci_final_assembly'], 1):
        output += f"{i}. {step}\n"

    output += f"""
**Export Settings:**
- Format: MP4
- Resolution: 1080p minimum
- Filename: `{blog_stem}.mp4`
- Save to: `assets/video/edited/`

---

## Shortcuts + Pro Tips

### DaVinci Resolve Auto-Captions
- Select clip → Text → Auto Captions → wait 2-3 min
- Fix tech terms or mishearings manually

### B-Roll Timing
- Each B-roll clip should be 15-30 sec max
- Use fade/dissolve transition between talking head → B-roll (0.3s)
- Keep audio continuous (don't mute for B-roll unless adding music)

### Music Selection
- Free: Epidemic Sound trial, YouTube Audio Library, Pexels Music
- Use low volume (:15-:30) so voice is always primary

### Multiple Takes
- Record each component 2-3 times, keep the most natural
- Don't over-think, authenticity > perfection

---

## Final Checklist Before Export

- [ ] Captions are accurate (grammar, tech terms correct)
- [ ] Audio levels consistent (no sudden loud/quiet spots)
- [ ] B-roll clips fade smoothly between segments
- [ ] Text overlays readable (high contrast)
- [ ] Video length matches target ({guide_data['total_video_length']})
- [ ] Intro hooks viewer
- [ ] Closing has call-to-action or reflection
- [ ] No awkward pauses or cuts

---

Generated: {blog_stem}
"""

    return output

def main():
    parser = argparse.ArgumentParser(description="Generate recording & editing guide")
    parser.add_argument("--input", required=True, help="Blog markdown file")
    parser.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: {args.input} not found")
        return

    guide = generate_guide(args.input, args.niche)

    output_path = Path(args.input).parent / f"{Path(args.input).stem}_RECORDING_GUIDE.md"
    with open(output_path, "w") as f:
        f.write(guide)

    print(f"✓ Recording guide saved → {output_path}")

if __name__ == "__main__":
    main()
