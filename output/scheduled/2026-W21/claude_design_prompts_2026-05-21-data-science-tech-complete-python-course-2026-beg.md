# Claude Design Prompts — 2026-05-21_data_science_tech_complete-python-course-2026-beginner-to-advance-tutorial-110

Niche: ds
Code blocks: 4/4 validated

---

## 1. SLIDE DECK PROMPT

You are an expert presentation designer and visual storyteller creating a dark, precision-driven, intellectually honest slide deck for a Data Science technical tutorial.

PROJECT CONTEXT
Topic: Python for Data Science: Tutorial 1/10 — Why Your Setup Matters More Than Your First Program
Tone: Analytical yet encouraging; honest about struggle; foundational confidence over hype
Audience: Beginners with zero Python experience but strong computer literacy; people who value thinking clearly over memorizing syntax; people frustrated by tutorials that skip "the boring parts" then fail months later

VISUAL DIRECTION
Style: Apple/Vercel minimalism meets technical rigor. Dark mode throughout. Every element serves function. Grid-based layouts with generous negative space. The visual language of a well-designed API docs site or clean terminal interface. Precision over decoration. Code takes center stage; aesthetics support clarity.

Color Palette:
- Deep Midnight Navy: #1C1C2E (backgrounds, text)
- Steel Blue-Grey: #7C9CB0 (secondary text, borders, diagrams)
- Electric Teal: #00D4AA (callouts, highlights, data points)
- Off-White: #E8E0D5 (primary text, clean backgrounds for contrast)
- Neon Purple: #7B61FF (accent moments, code highlights, emphasis)
- Terminal Black: #0D0D14 (code block backgrounds)

Typography:
- Headlines: Geometric sans-serif, ultra-bold weight (Montserrat Bold or similar), all caps or title case. Size hierarchy: hero 72px → section head 48px → slide title 36px.
- Body: Clean sans-serif (Inter, Roboto, SF Pro Display), regular weight, 18-22px. High contrast on dark backgrounds.
- Code: Monospace (Monaco, Courier New, or JetBrains Mono), 14-16px, with syntax hints via color layering.

Imagery Direction (as if briefing a photographer):
Slide 1 (Chaos): Overhead shot of cluttered developer desk — multiple browser windows open, notebooks scattered, code on screen looking confusing. Dark overhead lighting. Foreground shows laptop keyboard, slightly out of focus.
Slide 2 (Cost of Failure): Split screen: left shows tangled red error lines in terminal, right shows a calendar marked with large red X's. Moody dark blue-grey background. Feeling: consequences, time wasted.
Slide 3 (Environment Setup): Close-up of hands typing terminal command into clean shell interface. Single command visible: `python3 -m venv env`. Teal highlight on the text. Clean desk background, minimal.
Slide 4 (Computational Thinking): Geometric animation or diagram: one large problem box exploding into four smaller pieces with labels (decompose, pattern, abstract, algorithm). Teal connectors showing relationships. Dark navy background.
Slide 5 (First Program): Code editor fullscreen, dark theme, showing the actual first_script.py. Teal syntax highlights on key lines. Terminal output below showing results. Clean, no clutter.
Slide 6 (CODE_BLOCK 1 — Actual Code): Dark terminal panel (nearly black background, #0D0D14). Code in monospace with subtle syntax coloring: keywords in teal, strings in steel grey, comments muted. Show the complete first_script.py from the blog, exactly as written. Output visible below showing `Average age: 35.0` and file save confirmation.
Slide 7 (Error Messages): Red terminal output showing `KeyError: 'ages'` with annotation lines pointing to error type and explanation. Dark background. Show the before/after: broken line highlighted, then fixed line below it. Clean layout, educational.
Slide 8 (Foundation Built): Graphic showing a building foundation with four supporting columns labeled (Isolated Environment, Mental Model, Working Program, Error Handling). Checkmarks above each. Confident, complete. Warm teal accent lighting on the structure.

Animation / Transitions:
- Slide-to-slide: Fade in 0.3s, no motion distraction
- Code lines: Subtle line-by-line appearance (100ms per line) when showing code blocks
- Diagrams: Build on logic flow, not gratuitously (e.g., problem decomposition builds top-to-bottom)
- Error messages: Flash in red, stay static
- Keep motion minimal and purposeful. No spinning objects, no excessive zoom. The content is the focus.

HERO SLIDE (Slide 1)
Title: PYTHON FOR DATA SCIENCE
Main Text (ALL CAPS): YOU'LL WRITE CODE THAT FAILS. SUCCESS IS LEARNING WHY.
Sub Text: Setup, thinking, and debugging matter more than syntax.
Hero Visual Direction: Overhead shot of developer at desk with laptop showing terminal window. Warm task lighting overhead. Multiple screens visible. Organized but busy workspace. Teal highlight on laptop glow. Feeling: ready to build something real.

SLIDE STRUCTURE + CONTENT

Slide 1: HERO SLIDE
[As described above]

Slide 2: THE TWO WAYS TO LEARN
Visual: Split-screen diagram. Left side: arrows pointing down accumulating boxes (Variables, Loops, Functions, Classes) with overwhelmed face at bottom. Right side: single upward arrow labeled "Computational Thinking" leading to organized structure below. Teal connectors showing the structural path.
Content:
- Additive: Collect syntax rules until drowning in details
- Structural: Learn thinking first, code second
- Data science demands structural approach from day one

Slide 3: WHY SETUP FAILS (AND WHAT IT COSTS)
Visual: Two-column timeline. Left column (red tones fading to grey): Day 1 "code works" → Month 3 "library updated" → Month 6 "nothing runs". Right column (teal upward trajectory): Day 1 "environment isolated" → Month 3 "everything still works" → Month 6 "reproduces exactly".
Content:
- Bad setup = unreproducible results that fail months later
- Version conflicts and silent failures multiply
- Global installs create cascade problems
- Most 'failures' aren't Python—they're environment issues

Slide 4: VIRTUAL ENVIRONMENTS: YOUR FOUNDATION
Visual: Terminal window showing the setup commands in dark panel. Teal highlight on `source env/bin/activate`. Below: Venn diagram showing "Your Project Dependencies" isolated in one circle, "System Python" in another, no overlap. Teal border around isolated circle.
Content:
- Isolate each project's dependencies completely
- Never install globally again
- One command: source env/bin/activate (dark terminal font)
- Reproducibility becomes automatic, not aspirational

Slide 5: COMPUTATIONAL THINKING: FOUR PARTS
Visual: Four geometric shapes (circle, square, triangle, diamond) arranged in sequence with labels and teal connector lines. Each shape represents one concept. Flowing left-to-right showing progression: decomposition → pattern → abstraction → algorithm.
Content:
- Decomposition: break big problems into smaller pieces
- Pattern Recognition: notice what steps repeat
- Abstraction: write it once, reuse everywhere
- Algorithm Design: sequence the logic clearly

Slide 6: YOUR FIRST PROGRAM: DATA, NOT HELLO WORLD
Visual: Code editor split-view. Top half shows clean Python code with teal syntax highlights. Bottom half shows terminal output and results.json file created. Clean, side-by-side layout emphasizing input → processing → output flow.
Content:
- Read structured data (list of dictionaries)
- Process with loops (the pattern you'll repeat forever)
- Save results reproducibly (JSON, not terminal output)
- This is already a real program, not a toy

Slide 7: CODE_BLOCK — First Program [FULL CODE]
Visual: Dark terminal panel (#0D0D14 background). Display the complete tested code block exactly as provided:

```python
import json

# Define some data
people = [
    {"name": "Alice", "age": 28, "field": "data science"},
    {"name": "Bob", "age": 35, "field": "software engineering"},
    {"name": "Carol", "age": 42, "field": "product management"},
]

# Calculate average age
total_age = 0
for person in people:
    total_age += person["age"]

average_age = total_age / len(people)

# Output
print(f"Average age: {average_age:.1f}")
print(f"Total people: {len(people)}")

# Save results
results = {
    "average_age": average_age,
    "total_count": len(people)
}

with open("results.json", "w") as f:
    json.dump(results, f)

print("\nResults saved to results.json")
```

Syntax coloring: Keywords (import, for, with) in teal, strings in steel grey, comments in muted grey, numbers in neon purple. Monospace font 14px. Line numbers on left in steel grey.

Below the code, show the terminal output:
```
Average age: 35.0
Total people: 3

Results saved to results.json
```

Slide 8: ERROR MESSAGES ARE YOUR TEACHER
Visual: Left side shows broken code line highlighted in red: `total_age += person["ages"]`. Right side shows red terminal error: `KeyError: 'ages'`. Center arrows with annotations: "Error Type" pointing to KeyError, "Specific Issue" pointing to 'ages'. Teal correction arrow below showing fixed line: `total_age += person["age"]`. Teaching moment: reading errors = learning.
Content:
- Read the error type: KeyError, ValueError, IndexError
- Identify exactly what went wrong
- Fix it and run again immediately
- That cycle is 80% of all programming

Slide 9: YOUR FOUNDATION IS READY
Visual: Building foundation graphic. Four stone blocks at base, each labeled with icon + text: ✓ Isolated Environment | ✓ Mental Model | ✓ Working Program | ✓ Error Handling. Structure glows with teal accent lighting. Feeling: complete, solid, ready for next steps.
Content:
- ✓ Isolated environment with no version conflicts
- ✓ Mental model for decomposing any problem
- ✓ Your first working program saving real output
- ✓ A way to debug and learn from error messages
- Everything after scales on this foundation

DESIGN RULES
1. Dark mode throughout. Primary background #1C1C2E, never pure white or light grey. Code blocks always dark terminal aesthetic (#0D0D14).
2. Teal (#00D4AA) is the only highlight color. Use sparingly: on active code, on key callouts, on structural connectors. Never overuse.
3. Typography hierarchy strict: Hero text 72px bold, section heads 36px bold, body 18px regular. Never smaller than 16px body text. Every word earns its space.
4. Code blocks are full-featured: show complete, runnable code. Include monospace font, syntax hints via color, line numbers. Never show pseudo-code or abbreviated snippets.
5. No decorative illustrations. Every image serves explanation: teaching a concept, showing workflow, or capturing a mood. Diagrams are functional geometry, not embellished art.
6. Negative space is generous. Slides are never full. Content floats in calm dark space. Breathing room between sections.

OUTPUT REQUIREMENTS
- Total of 9 slides (plus optional cover/title sequence)
- Google Slides or Canva Presentation format
- Every slide title pulled directly from blog content where possible
- Code block slides display complete, tested code exactly as written in blog
- Color palette locked: only use the six specified hex codes
- All transitions fade only; no motion on content
- Font lock: geometric sans-serif for headlines, clean sans for body, monospace for code
- Export-ready for direct paste into Claude Design

---

## 2. INSTAGRAM STORY SEQUENCE PROMPT

Create a cinematic dark-mode Instagram Story sequence for a Data Science tutorial post titled: Python for Data Science — Why Your Setup Matters More Than Your First Program

THE EMOTIONAL CORE
Frustration melts into confidence when you realize: foundation comes before flashiness. The moment you understand that environment setup, clear thinking, and error-reading are the actual skills — that's when programming stops feeling scary and starts feeling like communication.

STYLE DIRECTION
Dark, minimalist, technically honest. Every frame is either a real screenshot or a carefully composed workspace shot. No stock photos. No motivational poster energy. Pacing is slow: let each frame breathe for 2-3 seconds. The vibe is late-night focused work, quiet competence, the satisfaction of something working when you set it up right. Cool color temperature. Teal accents only on key moments. Monospace fonts matter. Show code, show terminals, show real output. This isn't about aesthetics—it's about clarity.

COLOR PALETTE
#1C1C2E · #7C9CB0 · #00D4AA · #E8E0D5 · #7B61FF

FORMAT
Vertical 9:16. 7 frames. Fade transitions (0.3s between frames). Text appears 0.5s into frame, fades at 2.5s mark.

STORY FLOW

FRAME 1: THE HOOK — Overwhelm
Visual: Overhead shot of laptop screen showing chaotic terminal with multiple error messages scrolling, red text, confusing stack traces. Mouse cursor visible. Desk is cluttered. Cool blue-grey lighting. Desaturated colors, moody.
Text: "Your first Python program breaks"
[Visual dominates, text minimal, centered bottom]

FRAME 2: THE PROBLEM
Visual: Close-up of same screen. Red KeyError visible. Developer's hands visible at keyboard, pressing keys to fix it. One hand on mouse.
Text: "You panic. Is Python too hard?"
[Text centered, white on dark overlay]

FRAME 3: THE REFRAME
Visual: Split screen: left shows messy environment, right shows clean terminal window with single command `python3 -m venv env` glowing in teal. Before/after comparison.
Text: "No. Your environment is broken"
[Text left-aligned, teal accent on keyword]

FRAME 4: THE SHIFT
Visual: New terminal window, clean, dark. Text flowing: `source env/bin/activate` in teal. Cursor blinking. Minimal background.
Text: "One command. Everything isolates."
[Minimal, let the code speak]

FRAME 5: THE FOUNDATION
Visual: Geometric diagram: large problem box breaking into 4 smaller pieces (decompose, pattern, abstract, algorithm) with teal connectors. Dark navy background. Animated reveal: pieces separate and re-arrange cleanly.
Text: "Think in pieces before code"
[Centered, white text, teal accent on "pieces"]

FRAME 6: THE PROOF
Visual: Code editor showing first_script.py with output below showing successful results. Terminal shows: "Average age: 35.0" and "Results saved to results.json". Clean, working, real.
Text: "Your first program works"
[Right-aligned, smaller font, matter-of-fact tone]

FRAME 7: THE PAYOFF — Calm Confidence
Visual: Developer leaning back from desk, satisfied expression (or just hands relaxed on keyboard). Workspace is organized. Code visible on screen in background, glowing teal highlights. Soft lighting. Clean desk.
Text: "Because you built it right"
[Centered, white, warmth rather than urgency]

ANIMATION STYLE
Fade only. No zoom, no pan, no parallax. Each frame appears at normal opacity over 0.3s. Text fades in 0.5s after visual. Hold 2.5s. Fade out 0.3s. Total ~3-4s per frame. Pacing is meditative, not rushed.

TYPOGRAPHY
Font: Clean sans-serif (SF Pro Display or equivalent). White #E8E0D5 on dark background. Size: 32px for main text, 18px for supporting. All caps for emphasis only (e.g., "ONE COMMAND"). Let whitespace surround words. No shadow, no outline—just clean contrast.

GOAL
Viewer should finish the story feeling: "Oh. Setup isn't overhead. It's the thing that makes everything else work. And I can do this." Relief + confidence + clarity.

---

## 3. REEL COVER / THUMBNAIL PROMPT

Create a cinematic vertical reel cover (9:16) for Python for Data Science — Foundation First.

VISUAL DIRECTION
Dark terminal window filling the entire frame. Clean, centered. Show actual Python code on dark background: the first_script.py with teal syntax highlights. Code is sharp, readable, the hero of the frame. Monospace font dominant. Below the code, show one line of output in green terminal text: "Results saved to results.json". Soft glow effect around the code panel (subtle, barely noticeable). Bottom third darker than top, creating visual weight that draws eye to text overlay. Feeling: "this code works, this is real."

TEXT OVERLAY
Main Text: SETUP MATTERS MORE THAN CODE
(All caps, geometric sans-serif bold, 48px, centered, positioned at bottom 1/3 of frame)

Sub Text: Python for Data Science — Tutorial 1
(Title case, clean sans, 24px, positioned above main text, steel grey color #7C9CB0, optional)

COLOR TREATMENT
Dark navy background (#1C1C2E) with code panel in terminal black (#0D0D14). Teal accents (#00D4AA) on syntax highlights and possibly a thin glowing border around the code panel. Main text in off-white (#E8E0D5). No gradient, no blur effect — just clean contrast. Minimal color, maximum clarity.

TYPOGRAPHY
Main text: Montserrat Bold or geometric sans, all caps, 48px, tight line-height, white (#E8E0D5), no shadow.
Sub text: Inter or clean sans, 24px, grey (#7C9CB0), positioned 12px above main text.
Code: Monaco or JetBrains Mono, 12px, with subtle syntax coloring (teal for keywords, grey for strings, purple for numbers).

MOOD
Quiet competence. The satisfaction of something working when you do the setup right. Late-night focus. Technical precision mixed with accomplishment. Not hyped, not dramatic — just: this works because we built it correctly.

OPTIMIZATION NOTE
Stop-scroll factor: The contrast between dark background and bright code + bold text is high enough to catch the eye in a fast-scrolling feed. The "tutorial" label in sub-text signals educational value. "Setup matters more than code" is counter-intuitive enough to make people pause: "Wait, that's backwards from what I've heard." That pause = engagement.

---

## 4. SOCIAL POST SET PROMPT (Instagram · LinkedIn · Twitter/X · Threads)

Create a social graphic set for Python for Data Science — Foundation First — 4 platform variants from the same visual system.

VISUAL SYSTEM
Unified dark-mode aesthetic across all variants. Color palette locked: navy backgrounds, teal accents, off-white text, steel grey supporting text. Every variant shows real code or a clean workspace—no illustrations, no stock photos. The visual language: technical precision mixed with human warmth. Every frame earns its place. The mood is quiet confidence: "this foundation is solid."

VARIANT 1 — INSTAGRAM (1080×1080 square)
Headline/Quote: "Your environment is the difference between 'I learned Python' and 'I can use Python to think clearly.'"
(Exactly 82 characters, pulled from blog)

Supporting Text: Build your foundation first. Code second.
(Optional sub-line, 28 characters, teal color #00D4AA)

Layout: Portrait-friendly. Hero visual: dark terminal window with code (top 60% of frame). Bold headline floats over bottom 40%, centered, white text on dark semi-transparent overlay. Supporting text below in teal. Handle @mistakenlyhuman positioned bottom-right in 12px sans, steel grey, barely visible.

Typography: Headline in geometric sans-serif bold, 44px, line-height 1.2. Supporting text 18px regular. Clean sans throughout.

VARIANT 2 — LINKEDIN (1200×628 landscape)
Headline: Setup Isn't Overhead — It's Everything
(Changed framing for professional authority, 46 characters)

Sub-line: The skill that compounds: isolated environments, reproducible results, confidence.
(48 characters, authority-forward)

Layout: Wider canvas. Left 60%: text hierarchy dominates. Right 40%: dark terminal code panel as background. Headline bold, 52px. Sub-line 22px regular, steel grey. Handle @tarun-gupta-in bottom-right, 10px, barely visible. Professional but not corporate.

Typography: Same sans-serif system. High contrast. Generous margins.

VARIANT 3 — TWITTER/X (1200×675 landscape)
Headline: Environment > Code
(Punchy. 17 characters. Scroll-stopping contrast to conventional wisdom.)

Sub-line: Isolation. Reproducibility. Error-reading. Foundation-first thinking.
(58 characters, bullets, quick-scan friendly)

Layout: Bold typography dominates. Headline in neon purple #7B61FF (eye-catching on X feed), 64px, bold, positioned top-left with room to breathe. Sub-line in white, 20px, positioned below in bullet format. Background: dark terminal window (subtle, supporting texture, not competing). Handle @mistakenlyhuman bottom-right, minimal.

Typography: Geometric sans, punchy, high contrast. Speed-reading optimized.

VARIANT 4 — THREADS (1080×1080 square)
Same as Instagram variant but slightly more personal, less polished. Can optionally drop sub-line if headline is strong. Threads rewards authenticity over production value. Use the same code-and-text layout but with a tiny bit more "handmade" feel: maybe show a real screenshot rather than a clean render, maybe add a cursor visible in the terminal, maybe show a small handwritten note in corner. The precision stays—the polish loosens slightly.

Typography: Same system, same typeface, but slightly looser tracking (letter-spacing +2). Feeling: still technical, but more "person at their desk" than "studio production."

TYPOGRAPHY (SHARED SYSTEM)
Geometric sans-serif (Montserrat, Poppins, or Inter-based variant) for all headlines. Clean sans (Inter, Roboto, SF Pro) for body/sub-text. Monospace (Monaco, JetBrains Mono) for any code visible in background. White (#E8E0D5) for primary text. Steel grey (#7C9CB0) for secondary. Teal (#00D4AA) for emphasis/accents only. No shadows. No outlines. Contrast is all.

BRAND ELEMENT
Handle placement per variant:
- Instagram & Threads: @mistakenlyhuman, bottom-right, 12px, steel grey, semi-transparent
- LinkedIn: @tarun-gupta-in, bottom-right, 10px, barely visible
- Twitter/X: @mistakenlyhuman, bottom-right, 10px, minimal presence

Never prominent. Handle is a detail, not a focal point.

MOOD
Quiet authority. You've figured something out that most people overlook. There's satisfaction in that clarity. The mood is "late-night realization" or "morning coffee reflecting on what actually works." Technical precision. Human warmth. No hype. No urgency. Just: this matters and you should know why.