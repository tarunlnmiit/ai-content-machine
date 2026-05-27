# Claude Design Prompts — 2026-05-25_data_science_tech_python-for-data-science-tutorial-210

Niche: ds

---

## 1. SLIDE DECK PROMPT

You are an expert presentation designer and visual storyteller creating a precise, technically grounded, quietly urgent slide deck for a data science Python tutorial series.

**PROJECT CONTEXT**
- Topic: Python for Data Science — Tutorial 2: Variables, Data Types & the Structures That Actually Matter
- Tone: Analytical, grounded, quietly urgent
- Audience: Aspiring data scientists who've written their first Python scripts but haven't been burned by a type bug yet; self-taught analysts who've shipped wrong numbers without knowing why; early-career data professionals who copy-paste code between notebooks

**VISUAL DIRECTION**
- Style: Dark mode precision. Every frame feels like a well-lit terminal window — purposeful, controlled, no decoration without function. The aesthetic is Apple/Vercel/Linear applied to technical education: dense with meaning, sparse with noise. Slides feel like a senior engineer's internal deck, not a course preview. Authority without performance.
- Color Palette: Deep midnight navy `#1C1C2E` (backgrounds), Steel blue-grey `#7C9CB0` (supporting text, labels), Electric teal `#00D4AA` (correct outputs, key callouts), Off-white `#E8E0D5` (body text), Neon purple `#7B61FF` (error highlights, string type labels), Amber `#F5A623` (warning states, the wrong answer `"283542"`)
- Typography: Bold geometric sans-serif (Inter or DM Sans) for slide headlines — 48–64pt, white or off-white. Monospace (JetBrains Mono or Fira Code) for all code — 18–22pt. Data labels in steel blue-grey, 14pt. Never more than 3 typographic weights per slide.
- Imagery Direction: No photography. Terminal windows and code panels are the visual anchor. Dark background panels with slight transparency or subtle grid texture. Code sits inside rounded dark rectangles (`#0D0D1A`) as if displayed in a real IDE. Diagram elements (boxes, arrows) use stroke-only style — no fills, just outlines in teal or grey. Silent, functional, expert.
- Animation/Transitions: Slide fade at 200ms. Code blocks appear line-by-line with a 80ms stagger per line. Bullet points reveal on click. No bouncing, no swooping. Transitions feel like a terminal loading output, not a presentation template.

**HERO SLIDE**
- Title: Python for Data Science — Tutorial 2 / 10
- Main Text (ALL CAPS): YOUR ANALYSIS CAN BE WRONG WITHOUT CRASHING
- Sub Text: Types encode intention. Python needs to know what you're holding.
- Hero Visual Direction: Full-bleed dark panel (`#1C1C2E`). Dead center: a Python terminal window showing `sum(ages)` returning `'283542'` in amber `#F5A623` — no error, no red, nothing alarming. Just a confident wrong number. Below it in small steel-grey monospace: `# no error. just wrong.` The terminal window has a subtle glow — not dramatic, just the ambient light of a screen in a dim room. Series indicator top-left: `Tutorial 02 / 10` in teal, 14pt monospace.

**SLIDE STRUCTURE + CONTENT**

SLIDE 1 — The Silent Bug
- Heading: Python Will Give You a Wrong Answer Without Telling You
- Bullets:
  - Summing a string column doesn't error — it concatenates
  - `"28" + "35" + "42"` = `"283542"` in Python
  - Types encode intention. Python needs to know what you mean.
- Visual Direction: Split panel. Left side: a CSV preview — column `age` with values `28`, `35`, `42` styled as if imported. Right side: terminal output showing `sum(ages)` = `'283542'` in amber, no error message in frame. Below the output: a thin amber underline. Caption in steel-grey: `No warning. No crash. Just a wrong number.`

SLIDE 2 — CODE_BLOCK: The 4 Primitive Types
- Heading: The 4 Primitive Types
- Bullets:
  - `int` — whole numbers (`28`, `100`, `-5`)
  - `float` — decimals (`3.14`, `0.5`, `-2.718`)
  - `str` — text (`"data"`, `"42"`, `"True"`) — note: `"42"` is not `42`
  - `bool` — `True` or `False` only
- CODE_BLOCK (dark terminal panel, full width, monospace JetBrains Mono):
```python
age = 28          # int
salary = 95000.50 # float
name = "Tarun"    # str
is_active = True  # bool

# The silent bug
ages_as_strings = ["28", "35", "42"]
print(sum(ages_as_strings))   # TypeError — but not always
print("28" + "35" + "42")     # "283542" — no error, wrong answer

# Correct
ages_as_ints = [28, 35, 42]
print(sum(ages_as_ints))      # 105
```
- Syntax coloring: keywords in purple `#7B61FF`, strings in teal `#00D4AA`, comments in steel-grey `#7C9CB0`, numbers in off-white. Wrong output `"283542"` highlighted with amber background.

SLIDE 3 — CODE_BLOCK: Check and Convert Types
- Heading: Check and Convert Types
- Bullets:
  - `type(x)` tells you what Python thinks it's holding
  - `int()`, `float()`, `str()` convert between types
  - Always check before calculating — especially on loaded CSVs
- CODE_BLOCK:
```python
x = "42"
print(type(x))        # <class 'str'>

x_int = int(x)
print(type(x_int))    # <class 'int'>
print(x_int + 1)      # 43

# Diagnose before you calculate
ages = ["28", "35", "42"]
print(type(ages[0]))  # <class 'str'>

ages_clean = [int(a) for a in ages]
print(sum(ages_clean)) # 105
```
- Visual accent: `type(x)` output line highlighted in teal. A callout annotation in steel-grey: `First diagnostic habit to build.`

SLIDE 4 — CODE_BLOCK: Lists — Ordered Sequences
- Heading: Lists: Ordered Sequences
- Bullets:
  - Index from `0`, slice with `[start:end]` — end is exclusive
  - `append()` adds to the end
  - List comprehensions: `[s for s in scores if s > 85]`
- CODE_BLOCK:
```python
scores = [72, 88, 91, 64, 95, 83]

# Indexing
print(scores[0])      # 72
print(scores[-1])     # 83

# Slicing (end index excluded)
print(scores[1:4])    # [88, 91, 64]

# append
scores.append(79)

# List comprehension: filter + transform in one line
high_scores = [s for s in scores if s > 85]
print(high_scores)    # [88, 91, 95]

# Equivalent for loop (more verbose)
high_scores = []
for s in scores:
    if s > 85:
        high_scores.append(s)
```
- Visual accent: The comprehension line highlighted in teal. A split-view annotation: loop version on left, comprehension on right, arrow between them labeled `same result`.

SLIDE 5 — CODE_BLOCK: Dictionaries — Named Records
- Heading: Dictionaries: Named Records
- Bullets:
  - Key-value pairs — one record per dict
  - `.get()` for safe access (no `KeyError` on missing keys)
  - List of dicts = the natural shape of a dataset row by row
- CODE_BLOCK:
```python
employee = {"name": "Tarun", "age": 28, "salary": 95000}

# Safe access
dept = employee.get("department", "Unknown")  # no KeyError

# Add / update
employee["department"] = "Data Science"

# List of dicts — natural dataset shape
employees = [
    {"name": "Tarun",  "salary": 95000},
    {"name": "Priya",  "salary": 87000},
    {"name": "Carlos", "salary": 102000},
]

total = sum(e["salary"] for e in employees)
print(total)  # 284000

senior = [e for e in employees if e["salary"] > 90000]
```
- Visual accent: A minimal diagram below the code — three rows labeled `Row 0`, `Row 1`, `Row 2` each pointing to a dict structure. Caption: `This is how CSVs map to Python.`

SLIDE 6 — CODE_BLOCK: Functions — Write Once, Trust Forever
- Heading: Functions: Write Once, Trust Forever
- Bullets:
  - `def calculate_average(values):` — reusable, testable
  - Default arguments: `is_outlier(value, threshold=2.0)`
  - One function replaces 3 copies of the same notebook block
- CODE_BLOCK:
```python
def calculate_average(values):
    if not values:
        return 0
    return sum(values) / len(values)

scores = [72, 88, 91, 64, 95]
print(calculate_average(scores))  # 82.0

# Default arguments
import statistics

def is_outlier(value, data, threshold=2.0):
    mean = calculate_average(data)
    std  = statistics.stdev(data)
    return abs(value - mean) > threshold * std

print(is_outlier(150, scores))          # True
print(is_outlier(88,  scores))          # False
print(is_outlier(88,  scores, threshold=0.5))  # True
```
- Visual accent: A before/after annotation — three ghosted identical code blocks on the left (duplicate notebook cells) collapsing into a single `def calculate_average():` on the right with a teal arrow. Caption in steel-grey: `One function. Three fixed.`

SLIDE 7 — What's Next: Tutorial 3 — NumPy
- Heading: What's Next: Tutorial 3 — NumPy
- Bullets:
  - These structures scale to millions of rows with NumPy
  - Arrays replace lists for numerical work
  - Everything from Tutorial 2 underpins everything in Tutorial 3
- Visual Direction: A minimal pipeline diagram — five labeled boxes connected by teal arrows: `Raw CSV` → `Type Check` → `Transform` → `Aggregate` → `Output`. Stroke-only rectangles, no fills, clean geometric sans labels. Below: teal callout box — `Tutorial 3: NumPy arrays. Same logic, ten thousand times faster.` Series progress indicator bottom-right: dots 1–10, dot 2 filled in teal, rest in grey.

**DESIGN RULES**
1. Every slide has exactly one code panel OR one diagram — never both at full scale on the same slide
2. Maximum 3 bullet points per slide — no exceptions
3. Code comments in steel-grey `#7C9CB0` — they carry the explanation, not the headline
4. The wrong answer `"283542"` appears in amber `#F5A623` wherever referenced — never in teal or white
5. Correct outputs appear in teal `#00D4AA` — visually resolving the tension amber created
6. Slide numbers appear bottom-right in monospace, 12pt, steel-grey — always visible

**OUTPUT REQUIREMENTS**
- 7 slides total
- Export as 16:9 widescreen
- All code panels use rounded corners (8px radius) on a `#0D0D1A` background
- Consistent 48px margin on all sides
- No slide title or number in slide 1 (hero) — series label only

---

## 2. INSTAGRAM STORY SEQUENCE PROMPT

Create a cinematic dark-mode technical Instagram Story sequence for a data science tutorial post titled: "Python for Data Science — Tutorial 2: Variables, Data Types & the Structures That Actually Matter"

**THE EMOTIONAL CORE**
The quiet dread of realizing your analysis was confidently wrong — and the specific, grounded relief of understanding exactly why. This sequence moves from exposure to comprehension: the viewer should finish feeling like they've been handed a diagnostic tool they didn't have before.

**STYLE DIRECTION**
Dark mode precision throughout. Every frame is a terminal window, a code panel, or a minimal diagram — rendered as if captured from a real development environment in low ambient light. No photography, no lifestyle imagery. The visual language is the IDE itself: monospace type, dark panels, deliberate color-coded syntax. Pacing is measured — each frame holds for 3–4 seconds before transitioning. The tone is that of a senior engineer showing you something quietly important, not a course selling itself.

**COLOR PALETTE**
- Background: Deep midnight navy `#1C1C2E`
- Body text: Off-white `#E8E0D5`
- Code / monospace labels: Steel blue-grey `#7C9CB0`
- Correct outputs / key insight highlights: Electric teal `#00D4AA`
- Wrong answer / warning state: Amber `#F5A623`
- String type indicators: Neon purple `#7B61FF`

**FORMAT**
Vertical 9:16. 7 frames. Transition: 200ms crossfade — no swipes, no bounces. Each frame designed for maximum legibility at phone-screen scale.

**STORY FLOW**

FRAME 1 — The Hook
- Visual: Full-bleed dark panel. Dead center: a Python terminal output. Single line in amber monospace — `283542`. No context. No error. Just the number. Below it, in small steel-grey: `# no error.` Top-left corner: a small teal label — `Tutorial 02 / 10`
- Text: NO ERROR. WRONG ANSWER.

FRAME 2 — The Cause
- Visual: Dark terminal panel showing the exact silent bug. Three lines of monospace code: `ages = ["28", "35", "42"]` then `print(sum(ages))` — TypeError on screen; then below: `print("28" + "35" + "42")` outputting `"283542"` in amber. The strings are purple `#7B61FF`. The wrong output is amber. Nothing else on the frame.
- Text: `"42"` is not `42`. Python knows the difference.

FRAME 3 — The Fix
- Visual: Two-line code panel. `x = "42"` on line 1, then `x = int(x)` on line 2. An arrow between them in teal. Output: `type(x)` returning `<class 'int'>` in teal. Minimal. Clean. The conversion is the entire story.
- Text: `type()` first. Always.

FRAME 4 — Lists
- Visual: A dark panel showing a single list comprehension: `[s for s in scores if s > 85]` — output on the next line in teal: `[88, 91, 95]`. Below: a ghosted 4-line for loop struck through with a single teal line. Label in steel-grey: `same result`.
- Text: One line. Same result.

FRAME 5 — Dicts
- Visual: Three minimal row cards stacked vertically — each a rounded dark rectangle containing `{"name": "...", "salary": ...}`. An annotation in teal connecting all three: `list of dicts = your dataset`. Clean, no decoration.
- Text: Lists are rows. Dicts are records.

FRAME 6 — Functions
- Visual: Left side — three ghosted identical code blocks, each labeled with a small `notebook_1.py`, `notebook_2.py`, `notebook_3.py` badge. Right side — a single clean `def calculate_average(values):` function block in teal. A converging arrow from all three pointing into the one. Nothing else.
- Text: One function. Three fixed.

FRAME 7 — Resolution
- Visual: Terminal output showing `sum(ages_clean)` = `105` in teal. Quiet. Still. No annotation needed. A one-line caption below in steel-grey monospace: `# that's what trust looks like.` Bottom: teal label — `Tutorial 03 → NumPy`
- Text: 105. That's the right answer.

**ANIMATION STYLE**
Code text types in character-by-character on frames 2, 3, 4 — 30ms per character delay. All other frames fade in at 200ms. No motion on frame 7 — it just appears.

**TYPOGRAPHY**
- All explanatory text: Bold geometric sans-serif (Inter or DM Sans), 28–34pt, centered, off-white
- All code: JetBrains Mono or Fira Code, 18–22pt
- Series label: 14pt monospace in teal, top-left
- No more than 6 words of display text per frame

**GOAL**
After the last frame, the viewer should feel specific, practical calm — like they now have one diagnostic move they didn't have before. Not inspired. Not impressed. Just quietly more capable.

---

## 3. REEL COVER / THUMBNAIL PROMPT

Create a cinematic vertical reel cover (9:16) for a Python data science tutorial about types, data structures, and the silent bugs that make analysis confidently wrong.

**VISUAL DIRECTION**
Full-bleed dark panel — deep midnight navy `#1C1C2E`. Dead center of the frame: a terminal window rendered realistically — rounded corners, subtle inner shadow, a faint glow as if actively lit. The terminal displays three lines of monospace code at 24pt:

```
ages = ["28", "35", "42"]
sum(ages)
→  '283542'
```

The strings `"28"`, `"35"`, `"42"` are rendered in neon purple `#7B61FF`. The output `'283542'` is in amber `#F5A623` — warm, confident, wrong. No error icon. No red. Nothing alarming. Just a number that looks plausible. The terminal window sits on a very slightly lighter background panel (`#0D0D1A`) with 8px rounded corners. Above the terminal, in small teal monospace 14pt: `Tutorial 02 / 10`. The overall composition is vertically centered with generous negative space above and below — the terminal occupies roughly 40% of vertical height.

**TEXT OVERLAY**
- Main text: YOUR ANALYSIS CAN LIE TO YOU
  - Font: Bold geometric sans-serif (Inter Black or DM Sans Bold)
  - Size: 38pt
  - Color: Off-white `#E8E0D5`
  - Position: Upper third of frame, centered, above the terminal window
  - Letter-spacing: +0.02em
- Sub text: Python types — what they are and why they matter
  - Font: Regular weight geometric sans-serif, 18pt
  - Color: Steel blue-grey `#7C9CB0`
  - Position: Below the terminal window, centered

**COLOR TREATMENT**
Background: `#1C1C2E` solid, no gradient. A single very subtle radial glow behind the terminal — teal `#00D4AA` at 4% opacity, 300px radius — gives the impression of a screen lit in a dark room. No vignette, no additional overlays.

**TYPOGRAPHY**
Two weights only: Black/Bold for the headline, Regular for the sub text. Monospace for all code. Strong size hierarchy: headline at 38pt, sub at 18pt, code at 24pt, series label at 14pt.

**MOOD**
The calm before someone realizes they've been working with the wrong numbers — technical authority, zero alarm.

**OPTIMIZATION NOTE**
The amber output `'283542'` is the scroll-stopper — anyone who has written data analysis code will feel it immediately. The cover rewards recognition before they read a single word of text. Frame it so the wrong answer is the first thing the eye lands on.

---

## 4. SOCIAL POST SET PROMPT (Instagram · LinkedIn · Twitter/X · Threads)

Create a social graphic set for "Python for Data Science — Tutorial 2: Variables, Data Types & the Structures That Actually Matter" — 4 platform variants from the same visual system.

**VISUAL SYSTEM**
All 4 variants share: deep midnight navy `#1C1C2E` backgrounds, a terminal or code panel as the primary visual anchor, the amber wrong-answer `'283542'` as the emotional hook, teal `#00D4AA` for corrected output or key callouts, off-white `#E8E0D5` for headline text, steel blue-grey `#7C9CB0` for supporting labels. Style is dark-mode technical editorial — the aesthetic of a thoughtful engineering blog post, not a course ad. No photography. Code is the image.

---

**VARIANT 1 — Instagram (1080×1080 square)**
- Headline: "Python didn't add 28 + 35 + 42. It concatenated them: '283542'. No error. No warning. Just a wrong number."
- Supporting text: Tutorial 2 / 10 — Variables, Data Types & the Structures That Actually Matter
- Layout: Vertical stack. Top 55%: dark terminal panel (`#0D0D1A`, rounded 12px) showing the silent bug — `sum(["28","35","42"])` → `'283542'` in amber, 3 lines, monospace 22pt. Bottom 45%: Headline text centered, Inter Bold 28pt, off-white. Below headline: Supporting text in steel-grey 16pt. Generous 48px padding all sides.
- Handle: @mistakenlyhuman — bottom-right, 13pt, steel-grey, monospace

**VARIANT 2 — LinkedIn (1200×628 landscape)**
- Headline: "Python will give you a wrong answer without telling you. Here's the type system that prevents it."
- Sub-line: Variables, data types, and structures every data scientist needs before touching a library.
- Layout: Left 48% — the terminal panel showing `sum(["28","35","42"])` → `'283542'` in amber, full-height left panel with slight inner glow. Right 52% — text zone, left-aligned: headline in Inter Bold 30pt off-white, sub-line in steel-grey 18pt below, a thin teal `#00D4AA` horizontal rule (1px, 64px wide) separating headline from sub-line. `Tutorial 02 / 10` in small teal monospace top-right of text zone.
- Handle: @tarun-gupta-in — bottom-right of text zone, 12pt steel-grey

**VARIANT 3 — Twitter/X (1200×675 landscape)**
- Headline: "No error. No crash. Just a wrong number. Python types, explained."
- Sub-line: Tutorial 2 — Variables & Data Types
- Layout: Full-bleed dark panel. Large centered terminal window (60% of frame width) showing the minimal 2-line bug: `"28" + "35" + "42"` = `"283542"` in amber. Headline above the terminal in Inter Black 34pt, off-white, centered, tight letter-spacing. Sub-line below in steel-grey 16pt. Strong vertical hierarchy — headline → terminal → sub-line.
- Handle: @mistakenlyhuman — bottom-right, 12pt, steel-grey

**VARIANT 4 — Threads (1080×1080 square)**
- Headline: "I once shipped an analysis where ages were being concatenated, not summed. '283542'. Nobody caught it. This is why types matter."
- No sub-line — the headline carries it.
- Layout: Same terminal panel as Instagram variant, same vertical stack structure. Headline text: Inter Regular (not Bold) — slightly less polished, more first-person. 26pt, off-white, more generous line-height (1.5). The authenticity comes from the weight choice and the first-person copy, not a different layout.
- Handle: @mistakenlyhuman — bottom-right, 13pt, steel-grey

---

**TYPOGRAPHY — Shared System**
- Headline: Inter Bold or Black — off-white `#E8E0D5`
- Sub-line / supporting: Inter Regular — steel blue-grey `#7C9CB0`
- All code: JetBrains Mono or Fira Code — syntax-colored as described
- Series label: Monospace 12–14pt — teal `#00D4AA`
- Handle: Monospace 12–13pt — steel-grey `#7C9CB0`
- Hierarchy enforced by size and weight only — no decorative type

**BRAND ELEMENT**
Handle placement: bottom-right on all 4 variants. Spacing: 20px from edge. Size: 12–13pt. Never overlapping the terminal panel or headline. Color: steel-grey `#7C9CB0` — present but never competing.

**MOOD**
The specific recognition of a mistake you've made or could have made — not fear, not lecture, just the quiet exposure of something that was hiding in plain sight.