# Claude Design Prompts — 2026-06-01_data_science_tech_python-for-data-science-tutorial-310

Niche: ds
Code blocks: 9/9 validated

---

## 1. SLIDE DECK PROMPT

You are an expert presentation designer and visual storyteller creating a technically precise, quietly revelatory slide deck for a data science tutorial blog post.

**PROJECT CONTEXT**
- Topic: NumPy and the Art of Thinking in Arrays — Tutorial 3/10, Python for Data Science
- Tone: Analytical, direct, quietly revelatory
- Audience: Early-career data scientists who've written Python lists and loops but haven't touched NumPy; self-taught coders who feel something is missing from their data work; computer science students making the transition into applied data science

**VISUAL DIRECTION**
- Style: Dark mode precision. Every design decision earns its place. The aesthetic is Apple documentation meets Linear.app — immaculate negative space, deliberate hierarchy, no decoration without function. The mood is the quiet satisfaction of seeing a complex thing simplified to its essential form. Not flashy. Authoritative.
- Color Palette: Deep midnight navy `#1C1C2E` (primary background) · Steel blue-grey `#7C9CB0` (secondary text, labels) · Electric teal `#00D4AA` (accent — key terms, highlights, code output values) · Off-white `#E8E0D5` (primary body text) · Neon violet `#7B61FF` (code syntax accent — keywords, brackets) · Dark panel `#13131F` (code block backgrounds, inset panels)
- Typography: Bold geometric sans-serif (Inter or similar) at high weight for slide headings — 48–64pt, off-white. Monospace (JetBrains Mono or Fira Code) for all code. Body bullets at 24–28pt in steel blue-grey. Strong hierarchy — heading weight at least 3x body weight. No decorative type. Every character carries information.
- Imagery Direction: Dark terminal environments with deliberate light sources — a laptop screen glowing in a dim room, the rectangular light of a monitor casting blue-white illumination on a desk surface. Abstract data flow imagery: grids of numbers all illuminating simultaneously in a wave, not sequentially. Code on real screens — not illustrations of code. Workspaces with the quiet intensity of late-night deep work sessions.
- Animation/Transitions: Precision grid reveals — slide content builds left to right, top to bottom. Code lines appear one at a time in sequence. Data outputs fade in after code. No decorative motion. Technical rhythm. 200ms transitions, ease-in-out.

**HERO SLIDE (Slide 1)**
- Title: NumPy: The Art of Thinking in Arrays
- Sub-label: Tutorial 3/10 — Python for Data Science
- Main Text (ALL CAPS, large): STOP LOOPING. START DESCRIBING.
- Sub Text: The mental shift that makes your Python actually fast — and makes Pandas make sense.
- Hero Visual Direction: Full-bleed dark panel `#1C1C2E`. Left side: faint, desaturated Python for-loop code in steel-grey, slightly blurred — the old way, receding. Right side: a single bright NumPy expression `scores * 2` in sharp electric teal on a dark terminal panel — clean, confident, luminous. A thin vertical dividing line between them in `#7C9CB0`. No other decoration.

**SLIDE STRUCTURE + CONTENT**

**Slide 2 — The Performance Problem**
- Heading: Why Python Loops Aren't Enough
- Bullets:
  - Python lists are flexible — integers, strings, booleans, mixed types
  - That flexibility costs performance at every single step
  - 1 million numbers: Python loop = ~12 seconds · NumPy = ~0.08 seconds
  - 50–200× faster — structural, not marginal
- Visual: Two side-by-side dark panels. Left panel labeled "Python Loop" shows a spinning cursor and a timer reading 12.0s in muted red. Right panel labeled "NumPy" shows a clean terminal output and a timer reading 0.08s in electric teal. White horizontal separator between them with the label "Same Result." Typography stark and clinical. No illustrations — pure type and UI.

**Slide 3 — What NumPy Arrays Actually Are**
- Heading: ndarray: The Different Tradeoff
- Bullets:
  - All elements must be the same type — int64, float64, bool
  - Stored in contiguous memory — no pointer-chasing
  - Operations implemented in compiled C and Fortran
  - Foundation: Pandas, scikit-learn, TensorFlow, PyTorch — all built on this
- Visual: Schematic diagram — two memory layouts side by side. Left: "Python list" — scattered memory blocks connected by arrows (pointer-chasing), each block labeled with a different type. Right: "NumPy ndarray" — tight, evenly-spaced contiguous blocks all labeled int64, no arrows. Electric teal highlights the ndarray blocks. Off-white label: "Same performance gap, every operation." Dark background, minimal grid lines.

**Slide 4 — CODE_BLOCK: Creating Arrays**
- Heading: 3 Ways to Create Arrays
- Code panel (dark `#13131F`, monospace, full-width):
```python
import numpy as np

# From a Python list — most common starting point
scores = np.array([85, 92, 78, 95, 88])
print(scores)         # [85 92 78 95 88]
print(type(scores))   # <class 'numpy.ndarray'>
print(scores.dtype)   # int64 — all elements are 64-bit integers

# From scratch — utility constructors
zeros  = np.zeros(5)           # [0. 0. 0. 0. 0.]
ones   = np.ones(5)            # [1. 1. 1. 1. 1.]
rng    = np.arange(0, 10, 2)   # [0 2 4 6 8]
grid   = np.linspace(0, 1, 6)  # [0.  0.2 0.4 0.6 0.8 1.0]
```
- Syntax colors: `np` in violet `#7B61FF` · string literals in amber `#C9A96E` · comment text in steel-grey `#7C9CB0` · output values in electric teal `#00D4AA`
- Call-out annotation floating beside `.dtype`: "No commas in output = NumPy, not a list"
- Visual: Code panel takes 80% of slide. Right sidebar in dark navy holds one insight line: "dtype tells you exactly what's in memory."

**Slide 5 — CODE_BLOCK: Vectorized Operations**
- Heading: Stop Looping. Start Describing.
- Code panel:
```python
import numpy as np
scores = np.array([85, 92, 78, 95, 88])

# Python loop — don't do this
doubled_slow = []
for s in scores:
    doubled_slow.append(s * 2)   # 5 iterations, Python overhead

# NumPy vectorized — do this instead
doubled_fast = scores * 2
print(doubled_fast)  # [170 184 156 190 176]

# All of these run in compiled C — no Python loop required
print(scores + 5)                  # [90 97 83 100 93]
print(scores - scores.mean())      # deviations from mean
print(scores ** 2)                 # [7225 8464 6084 9025 7744]
print(np.sqrt(scores))             # [9.22 9.59 8.83 9.75 9.38]
```
- The Python loop block is rendered slightly dimmer — desaturated to ~60% opacity. The NumPy block is full brightness with a thin electric teal left border. Visual emphasis makes the better path unmistakable.
- Below code: one line in large type, off-white: "One line. Entire array. Compiled execution."

**Slide 6 — CODE_BLOCK: Boolean Indexing**
- Heading: Filter Without a Loop
- Code panel:
```python
import numpy as np
scores = np.array([85, 92, 78, 95, 88])

above_90 = scores > 90
print(above_90)         # [False  True False  True False]

high_scores = scores[above_90]
print(high_scores)      # [92 95]

# Same thing — one line
print(scores[scores > 90])  # [92 95]
```
- Below code panel: bridge line in electric teal, italic: `df[df["column"] > value]` with label "This is what Pandas filtering looks like. You already know how it works."
- Visual: Clean split — top 70% is code panel, bottom 30% is the Pandas preview on a slightly lighter dark background, connecting the dots forward.

**Slide 7 — CODE_BLOCK: Aggregations and IQR Outlier Detection**
- Heading: Stats in One Method Call — Then Outlier Detection
- Code panel (split into two labeled sections):
```python
import numpy as np
salaries = np.array([85000, 92000, 78000, 95000, 88000, 110000, 74000])

# Descriptive statistics
print(salaries.mean())          # 88857.14
print(salaries.std())           # 11580.51
print(salaries.min(), salaries.max())  # 74000  110000

# Percentiles — IQR outlier detection
q25 = np.percentile(salaries, 25)   # 83000.0
q75 = np.percentile(salaries, 75)   # 93500.0
iqr = q75 - q25                     # 10500.0
upper_fence = q75 + 1.5 * iqr       # 109250.0
lower_fence = q25 - 1.5 * iqr       # 67250.0

outliers = salaries[(salaries > upper_fence) | (salaries < lower_fence)]
print(outliers)  # [110000]
```
- Electric teal annotation beside `[110000]` output: "Flagged. Automatically."
- Section divider between stats and outlier detection blocks — thin steel-grey horizontal rule with label "→ Now use it"

**Slide 8 — CODE_BLOCK: 2D Arrays and Axis**
- Heading: Rows, Columns, and the Axis Rule
- Code panel:
```python
import numpy as np
data = np.array([
    [85, 92, 78, 95],   # student 1
    [70, 88, 91, 84],   # student 2
    [93, 76, 89, 77]    # student 3
])

print(data.shape)   # (3, 4) — 3 rows, 4 columns
print(data[0, 2])   # 78 — row 0, column 2
print(data[:, 2])   # [78 91 89] — all rows, column 2

column_means = data.mean(axis=0)  # avg per test:    [82.67 85.33 86.   85.33]
row_means    = data.mean(axis=1)  # avg per student: [87.5  83.25 83.75]
```
- Right sidebar: visual mnemonic — two arrows. Arrow pointing down labeled "axis=0 — collapses rows." Arrow pointing right labeled "axis=1 — collapses columns." Both in electric teal against dark panel.
- Bottom of slide, in steel-grey italic: "axis=0 down · axis=1 across. Repeat this until it's automatic."

**Slide 9 — Takeaway**
- Heading: The Mental Shift
- Three statements, large type, stacked with generous spacing:
  - "Lists taught you to sequence."
  - "Dicts taught you to map."
  - "NumPy teaches you to operate on the whole thing at once."
- Below, in smaller steel-grey: "Next: Pandas wraps this in column names and row labels. Everything you learned here carries forward directly."
- Visual: Full-bleed dark panel. No imagery. Pure typography — the three statements descend in a clean vertical stack, each separated by significant whitespace. Off-white text on `#1C1C2E`. Nothing competes with the words.

**DESIGN RULES**
1. Every slide holds one idea. If two ideas compete for a slide, split them.
2. Code panels always use `#13131F` background — never the slide background color. Creates visual depth.
3. Electric teal `#00D4AA` is reserved for: output values, key term highlights, call-out annotations, and accent borders. Violet `#7B61FF` is reserved for: code keywords and operators only.
4. No decorative elements — no gradients, no geometric shapes, no background patterns. If something isn't carrying information, remove it.
5. Minimum 40px padding on all slide edges. Content breathes.
6. All code is syntax-highlighted and complete — no ellipsis, no placeholder comments. Viewers should be able to run every slide's code verbatim.

**OUTPUT REQUIREMENTS**
- 9 slides total (1 hero + 8 content)
- 16:9 widescreen format
- Dark mode throughout — no light mode variants
- Export as individual PNG slides at 1920×1080

---

## 2. INSTAGRAM STORY SEQUENCE PROMPT

Create a cinematic dark-tech Instagram Story sequence for a data science tutorial post titled: "NumPy and the Art of Thinking in Arrays"

**THE EMOTIONAL CORE**
The viewer should feel the specific embarrassment of discovering they've been solving a solved problem — followed by the quiet, almost physical relief of a simpler path appearing. Not triumph. Just: oh. That's it.

**STYLE DIRECTION**
Dark terminal cinema. Think: late-night coding session, one monitor, the only light in the room. Every frame is composed like a still from a documentary about someone doing difficult, quiet, important work. Code appears on real screens, not illustrated panels. Text is sparse — sometimes just a phrase, sometimes just a number. The pacing is deliberate: each frame earns its beat before the next arrives. This is not a tutorial summary. It's a mood piece that makes someone want to understand arrays.

**COLOR PALETTE**
Deep midnight navy `#1C1C2E` (frame backgrounds) · Electric teal `#00D4AA` (key text, code highlights) · Off-white `#E8E0D5` (primary copy) · Steel blue-grey `#7C9CB0` (secondary text, timestamps, labels) · Neon violet `#7B61FF` (code accent) · Near-black `#0D0D17` (darkest panels)

**FORMAT**
Vertical 9:16 · 7 frames · Transition: slow cross-dissolve (300ms) · No swipe animations

**STORY FLOW**

FRAME 1:
- Visual: Extreme close-up of a laptop trackpad and lower keyboard edge. In the background, slightly out of focus, a terminal window with a Python for-loop running. A progress indicator — just the blinking cursor — blinks once, twice, three times. Warm tungsten glow from a desk lamp in upper right. The kind of light that means it's late and you've been at this a while. No human visible.
- Text overlay (lower third, off-white, large bold geometric sans): "Your loop is the problem."
- Sub-text (steel-grey, smaller): "You just don't know it yet."

FRAME 2:
- Visual: The same laptop screen, now showing two side-by-side terminal windows. Left: a Python for-loop with an indented body visible. Right: a single line — `scores * 2` — with output already printed below. The right window is brighter, slightly more in focus. The left window has a subtle dim overlay, like it's receding.
- Text overlay (centered, electric teal, ALL CAPS, large): "ONE LINE."
- Sub-text (off-white, below): "Same result. Compiled C underneath."

FRAME 3:
- Visual: Abstract — a grid of small square cells filling the frame, all dark grey. Then, in a single wave moving from left to right, all cells illuminate simultaneously in electric teal. Not one at a time. All at once. The wave takes about half a second in the animation. After illumination, the grid holds — a glowing matrix.
- Text overlay (centered, off-white): "Describe it."
- Sub-text (steel-grey, smaller): "Don't instruct it step by step."

FRAME 4:
- Visual: Full-frame dark panel `#0D0D17`. A single code expression centered vertically and horizontally — maximum clarity, nothing else:
  ```
  scores[scores > 90]
  ```
  Monospace font. `scores` in off-white. `>` and `90` in electric teal. No other elements. No background panel around the code — just the expression floating in near-black.
- Text overlay (below code, steel-grey, small): "Filter without a loop. This is also how Pandas works."

FRAME 5:
- Visual: A data scientist — shot from behind and slightly above — sitting at a desk with two monitors. The monitors show nested loop code. The posture is slightly slumped: shoulders forward, chin resting on one hand. Warm amber desk lamp light. The scene reads as: this person has been trying to make something work for a long time. Shot with shallow depth of field — monitors in focus, surroundings soft.
- Text overlay (upper portion, off-white, italic): "I spent an hour writing code NumPy had already solved in 2006."
- No sub-text. The quote stands alone.

FRAME 6:
- Visual: The same person, same desk — but now upright. Posture open. On one monitor: two lines of clean NumPy code. The other monitor is dark or off. The mood has shifted: not excited, just settled. The kind of stillness that follows a realization. Same warm light, same shallow depth of field.
- Text overlay (bottom third, electric teal, ALL CAPS): "THINK IN ARRAYS."
- Sub-text (off-white, smaller): "Not in steps."

FRAME 7 (final):
- Visual: Back to the terminal aesthetic. Dark full-frame panel. At top: tiny "Tutorial 3/10" label in steel-grey. Centered: the three progression lines stacked with generous spacing, appearing one at a time —
  - "Lists: sequence."
  - "Dicts: map."
  - "NumPy: operate on everything at once."
- Bottom: `@mistakenlyhuman` in steel-grey, small. Below that in teal: "Next: Pandas" — as a quiet forward hook.
- No photography. Pure text on dark. Maximum stillness to close.

**ANIMATION STYLE**
Long gentle cross-dissolves between frames. Frame 3 (grid illumination) is the only kinetic moment — all others are static compositions. Text fades in 200ms after frame fully loads. Final frame text appears line by line with 400ms pauses between each line.

**TYPOGRAPHY**
Bold geometric sans-serif for emotional statements — Inter Black or equivalent. Monospace (JetBrains Mono) for all code. All body text in off-white `#E8E0D5`. Accent copy in electric teal. Attribution in steel-grey, 14–16pt.

**GOAL**
After the last frame, the viewer should feel the specific quiet satisfaction of: "I need to understand this properly." Not motivated — oriented. They know exactly what they're missing and where to find it.

---

## 3. REEL COVER / THUMBNAIL PROMPT

Create a cinematic vertical reel cover (9:16) for a data science tutorial about NumPy — specifically about replacing Python loops with vectorized array operations.

**VISUAL DIRECTION**
A developer's desk at night — shot from a 45-degree overhead angle, tight crop on the laptop screen and the hands on the keyboard. The laptop screen shows a terminal with two expressions side by side: a Python for-loop (left, slightly dim, desaturated) and a single NumPy line `scores * 2` (right, bright, sharp). The NumPy side has a thin electric teal `#00D4AA` glow emanating from the screen edge — not a lens flare, just the ambient light of a screen doing real work efficiently. Desk surface is dark matte wood. Keyboard is dark mechanical. A coffee cup visible in far upper-left corner, slightly out of focus. Shallow depth of field — the screen is the sharpest thing in frame. Tungsten ambient light from the lower right counterbalances the cool blue screen glow.

**TEXT OVERLAY**
- Main text: YOUR LOOP IS TOO SLOW
  - Placement: upper 35% of frame, flush left with 48px left margin
  - Font: Bold geometric sans-serif, ~80pt, off-white `#E8E0D5`
  - Letter spacing: slightly tight — dense, authoritative
- Sub text: NumPy: Think in arrays, not steps.
  - Placement: directly below main text, 40pt, steel blue-grey `#7C9CB0`
- Bottom label: Tutorial 3 · Python for Data Science
  - Placement: lower 8% of frame, centered, 20pt, electric teal `#00D4AA`
  - Monospace font to match code aesthetic

**COLOR TREATMENT**
No gradient overlay — the scene's natural dark tones do the work. Slight vignette at frame edges (~15% opacity black) to contain focus on screen center. Electric teal `#00D4AA` appears only in the screen glow and the bottom label — used sparingly so it reads as signal, not decoration.

**TYPOGRAPHY**
Main text: Inter Black or Neue Haas Grotesk Display Bold · Left-aligned · Off-white · No shadow, no outline — the dark scene provides sufficient contrast. Monospace for the tutorial label line.

**MOOD**
The quiet intensity of someone who just discovered they've been doing something the hard way — not frustrated, just recalibrated. The cover promises a revelation, not a lesson.

**OPTIMIZATION NOTE**
The overhead angle and split-screen terminal create an immediately legible visual hierarchy even at thumbnail size — left side: "old way" (dim), right side: "better way" (bright). This binary works in a vertical scroll feed where viewers have 0.3 seconds to decide. The phrase "YOUR LOOP IS TOO SLOW" speaks directly to the exact audience (Python coders who've felt this) and excludes no one worth reaching.

---

## 4. SOCIAL POST SET PROMPT (Instagram · LinkedIn · Twitter/X · Threads)

Create a social graphic set for "NumPy and the Art of Thinking in Arrays" — 4 platform variants from the same visual system.

**VISUAL SYSTEM**
Dark terminal aesthetic across all 4 variants. Background: deep midnight navy `#1C1C2E`. A centered or left-anchored dark panel `#13131F` holds a single code expression — `scores[scores > 90]` — rendered in monospace with syntax highlighting: `scores` in off-white `#E8E0D5`, `>` and `90` in electric teal `#00D4AA`. Above the code panel: the headline. Below: optional sub-line. The code isn't decoration — it's the point. All 4 variants are unified by this: the code panel is always present, always readable, always the visual anchor.

Across all 4: no gradients, no stock photography, no illustrated characters. Pure typography and code on dark. If imagery appears, it is a real terminal screenshot — never clip art.

---

**VARIANT 1 — Instagram (1080×1080 square)**
- Headline: "You don't write loops. You write operations. NumPy applies them to everything."
- Supporting text: Tutorial 3/10 — Python for Data Science
- Layout: Headline in large bold geometric sans-serif in the upper 40% of frame, off-white, left-aligned with 60px margin. Code panel centered in mid-frame, full-width minus margins, dark `#13131F` background, monospace code. Supporting text below code in steel-grey `#7C9CB0`, small. Generous whitespace above and below code panel — the breathing room signals confidence.
- Handle: @mistakenlyhuman · lower-right · 18pt · steel-grey · small

**VARIANT 2 — LinkedIn (1200×628 landscape)**
- Headline: "Python loops are slow. NumPy arrays are not. Here's the 50–200× difference explained."
- Sub-line: Tutorial 3/10 · NumPy basics every data scientist needs
- Layout: Left third — headline and sub-line stacked vertically, text left-aligned, top-anchored. Right two-thirds — the code panel, full height of the canvas minus margins. A thin vertical electric teal `#00D4AA` line (2px) separates the text column from the code panel. This layout signals: authority on the left, proof on the right.
- Handle: @tarun-gupta-in · lower-right of code panel · 16pt · steel-grey

**VARIANT 3 — Twitter/X (1200×675 landscape)**
- Headline: "Your Python loop is 200× slower than it needs to be."
- Sub-line: NumPy fixes it in one line. →
- Layout: Bold headline dominates the left 60% of canvas — large weight, off-white, 68pt minimum. Code panel on right 40%, slightly shorter than full height, centered vertically. The headline and the code panel feel like a before/after even without labels. The arrow `→` at the end of the sub-line points toward the code — compositional micro-direction.
- Handle: @mistakenlyhuman · lower-left below sub-line · 16pt · steel-grey

**VARIANT 4 — Threads (1080×1080 square)**
- Headline: "I spent an hour writing nested loops. NumPy did it in two lines. The embarrassing part wasn't the time — it was realizing this was solved in 2006."
- Sub-line: (omit — headline is the full thought; adding a sub-line would dilute it)
- Layout: Headline fills the upper 55% in a slightly smaller weight than Instagram — more personal, more like a post than a campaign. Off-white text. Code panel below, same treatment as Instagram variant. The headline is longer than the other variants intentionally: Threads readers scroll slower and reward honesty over compression.
- Handle: @mistakenlyhuman · lower-right · 16pt · steel-grey

**TYPOGRAPHY**
Shared system: Inter Black (headlines) · Inter Regular (sub-lines, labels) · JetBrains Mono (all code). Headline size scales per canvas: Instagram/Threads 52–60pt, LinkedIn 44–50pt, Twitter 60–68pt. Steel-grey `#7C9CB0` for all sub-lines and handles. Off-white `#E8E0D5` for all headlines. Code always in monospace with syntax colors: keywords in violet `#7B61FF`, values/outputs in teal `#00D4AA`, comments in steel-grey.

**BRAND ELEMENT**
Handle placement specified per variant above. Consistent: small, lower placement, steel-grey — visible but never competing with the headline or code.

**MOOD**
The specific feeling of a long-held inefficiency being named. Not "learn something new" energy — "oh, I've been doing this wrong, and now I see it" energy. The graphic doesn't try to impress. It recognizes.