# DS Carousel Skin — LOCKED TEMPLATE PACK (Fieldwork Ledger + Terminal Marginalia)

Base philosophy: **Fieldwork Ledger** — the page as a lived-in research notebook: torn exhibits,
pinned index cards, exhibit stamps, a giant verdict underlined in blue. Not a poster about the
work — a page pulled from the notebook of someone who actually did it. Three archetypes from the
sibling philosophy **Terminal Marginalia** (a diff-view/terminal-annotation register) are folded
in for posts that genuinely have a before/after, a prompt, or a code-comment-worthy line.

## Visual language

- **Palette**: `#6B8FA8` (primary), `#96BAD0` (light), `#3D5F75` (dark/verdict blue) against warm
  kraft/cream `#EDE8DC` and near-black ink `#1E1B2E`, border `#D6D0C4`. Blue is reserved for
  verdicts and diffs, never decoration. No red/green, ever.
- **Fonts**: Space Grotesk (ledger voice — headlines, verdicts, margin notes); JetBrains Mono
  (terminal/diff-flavored archetypes — prompts, diffs, code-comment quotes).
- **Ground textures** — ruled kraft: `repeating-linear-gradient(0deg,transparent 0 27px,#D6D0C4
  27px 28px)` over `#EDE8DC`. Grid paper (terminal-flavored archetypes):
  `linear-gradient(rgba(61,95,117,.09) 1px,transparent 1px),linear-gradient(90deg,rgba(61,95,117,.09)
  1px,transparent 1px);background-size:26px 26px` over `#EDE8DC`.

## How these templates work (read before generating)

1. Every archetype below ships as a complete markup block + the CSS it needs. Use it EXACTLY —
   only fill the `<!-- SLOT: ... -->` comments with real copy. Do not drop the stamp, the tape,
   the redaction bar, the pin, or any other signature element to make a slide "simpler."
2. The **shared overlay chrome** (progress row, counter chip, follow-tag, swipe-arrow, save-tag,
   cliffhanger) is defined once below in two ground variants — include it, verbatim, on every
   slide, choosing whichever variant matches that slide's background. Which of follow-tag /
   save-tag / cliffhanger actually renders on a given slide still follows the main system
   prompt's per-slide-role rules (badge always; follow-tag CTA-slide only; save-tag hook-slide
   only; swipe-arrow every slide but the last; cliffhanger every slide but the last).
3. Never use the same archetype on two adjacent slides. Never run two Terminal-Marginalia-flavored
   archetypes (Diff Stack, Prompt Statement, Comment-Line Quote) back to back either — alternate
   registers the way a real notebook alternates page-types.
4. The reused doodle set (hand-drawn star outline, curved arrow, 3-dot cluster, stroke `#3D5F75`
   at low opacity) may appear on any archetype, max 2 per slide, as marginalia — never as
   center-stage decoration.

## Shared overlay chrome

**Light-ground variant** (kraft/cream/grid-paper backgrounds):

```css
.progress-row{position:absolute;top:0;left:0;right:0;display:flex;gap:4px;padding:8px 12px 0;z-index:20;}
.progress-seg{flex:1;height:3px;border-radius:2px;background:rgba(0,0,0,.12);overflow:hidden;}
.progress-seg .fill{height:100%;border-radius:2px;background:rgba(0,0,0,.42);}
.counter-chip{position:absolute;top:18px;left:18px;background:rgba(30,27,46,.88);color:#EDE8DC;font-size:11px;font-weight:600;padding:5px 10px;border-radius:20px;letter-spacing:.03em;z-index:20;font-family:'Space Grotesk',sans-serif;}
.follow-tag{position:absolute;top:18px;right:18px;font-size:10.5px;font-weight:600;color:#3D5F75;background:rgba(255,255,255,.75);padding:5px 10px;border-radius:20px;letter-spacing:.02em;z-index:20;font-family:'Space Grotesk',sans-serif;}
.swipe-arrow{position:absolute;top:50%;right:18px;transform:translateY(-50%);width:38px;height:38px;border-radius:50%;background:#3D5F75;color:#fff;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;box-shadow:0 8px 18px rgba(0,0,0,.3);z-index:20;}
.save-tag{position:absolute;bottom:18px;right:18px;font-size:10px;font-weight:600;color:#3D5F75;background:rgba(255,255,255,.75);padding:5px 9px;border-radius:6px;letter-spacing:.03em;z-index:20;font-family:'Space Grotesk',sans-serif;}
.cliffhanger{position:absolute;bottom:17px;left:0;right:0;text-align:center;font-size:9.5px;letter-spacing:.05em;text-transform:uppercase;z-index:20;font-family:'Space Grotesk',sans-serif;color:#3D5F75;opacity:.85;}
```

```html
<div class="progress-row"><!-- one .progress-seg per slide in the deck, repeated identically on every slide --></div>
<div class="counter-chip"><!-- SLOT: e.g. "3 / 8" --></div>
<div class="follow-tag">Tap to follow &rarr;</div> <!-- CTA slide only -->
<div class="swipe-arrow">&rarr;</div> <!-- every slide except the last -->
<div class="save-tag">Save this &darr;</div> <!-- hook slide only -->
<div class="cliffhanger"><!-- SLOT: teaser micro-line --></div> <!-- every slide except the last -->
```

This is the only overlay chrome DS uses — every archetype below is built on a light ground, so
no dark-ground overlay variant is needed for this niche.

## HOOK TEMPLATE (mandatory) — Verdict Page

No card at all: the verdict sits directly on the ruled-kraft ground.

```html
<div class="stamp"><!-- SLOT: credibility label, uppercase, e.g. "40+ HIRING LOOPS" --></div>
<div class="verdict"><!-- SLOT: 5-8 word headline; wrap the operative phrase in <span class="u">...</span> --></div>
<div class="margin-note"><!-- SLOT: one whisper-scale margin line --></div>
```

```css
body{background-color:#EDE8DC;background-image:repeating-linear-gradient(0deg,transparent 0 27px,#D6D0C4 27px 28px);}
.stamp{position:absolute;top:64px;left:18px;right:18px;font-family:'Space Grotesk',sans-serif;font-size:10.5px;font-weight:700;letter-spacing:.12em;color:#3D5F75;border:1.5px solid #3D5F75;display:inline-block;padding:4px 10px;border-radius:3px;transform:rotate(-1.5deg);width:fit-content;}
.verdict{position:absolute;top:150px;left:18px;right:18px;font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:38px;line-height:1.14;color:#1E1B2E;}
.verdict .u{border-bottom:5px solid #6B8FA8;padding-bottom:2px;}
.margin-note{position:absolute;top:372px;left:18px;right:70px;font-family:'Space Grotesk',sans-serif;font-size:12px;line-height:1.5;color:#3D5F75;font-weight:500;}
```

Do not omit the stamp or the underline — a verdict with no stamp and no underline is a plain
paragraph, not this archetype.

## CTA TEMPLATE (derived from hook — same archetype, same visual register)

```html
<div class="stamp"><!-- SLOT: credibility label, may repeat the hook's or vary --></div>
<div class="verdict"><!-- SLOT: CTA line; wrap the keyword in <span class="u">...</span>, e.g. Comment <span class="u">TELL</span> for the checklist --></div>
<div class="cta-btn"><!-- SLOT: button copy, e.g. "Comment TELL &rarr; I'll DM it" --></div>
```

```css
.cta-btn{position:absolute;bottom:70px;left:18px;right:18px;background:#3D5F75;color:#EDE8DC;font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:15px;text-align:center;padding:14px;border-radius:6px;letter-spacing:.02em;}
```

## Archetype library (9 — use a mix, never all from one register in a row)

### 1. Exhibit Page

One full-bleed torn/taped photo or screenshot "exhibit," rotated, filling nearly the whole frame;
a stamped caption strip is the only text. Only use when a proof-image marker is available this
run (see asset instructions below) — otherwise skip this archetype entirely.

```html
<div class="exhibit-wrap"><img class="exhibit-img" src="<!-- SLOT: proof marker, e.g. __DS_PROOF_1__ -->"><div class="exhibit-tape"></div></div>
<div class="exhibit-stamp"><!-- SLOT: caption strip, 3-6 words uppercase --></div>
```

```css
.exhibit-wrap{position:absolute;top:56px;left:18px;right:18px;bottom:56px;transform:rotate(-2.5deg);box-shadow:0 20px 40px rgba(30,27,46,.22);border-radius:2px;overflow:hidden;}
.exhibit-img{width:100%;height:100%;object-fit:cover;display:block;}
.exhibit-tape{position:absolute;top:-10px;left:38px;width:64px;height:22px;background:rgba(150,186,208,.6);transform:rotate(-5deg);box-shadow:0 2px 6px rgba(0,0,0,.1);}
.exhibit-stamp{position:absolute;bottom:14px;left:14px;right:14px;font-family:'Space Grotesk',sans-serif;font-size:10.5px;font-weight:700;letter-spacing:.1em;color:#EDE8DC;background:rgba(30,27,46,.82);padding:6px 10px;border-radius:2px;text-transform:uppercase;width:fit-content;}
```

### 2. Verdict Page

See HOOK TEMPLATE above — this archetype IS the hook template; reuse it unchanged whenever a
body slide also wants a giant standalone verdict.

### 3. Corkboard Stack

2-3 pinned index cards of varying width/rotation, slightly overlapping — the "evidence board"
read for a multi-beat insight.

```html
<div class="cork-card c1"><div class="pin"></div><!-- SLOT: line 1 --></div>
<div class="cork-card c2"><div class="pin"></div><!-- SLOT: line 2 --></div>
<div class="cork-card c3"><div class="pin"></div><!-- SLOT: line 3 (optional, drop if only 2 lines) --></div>
```

```css
body{background-color:#EDE8DC;background-image:repeating-linear-gradient(0deg,transparent 0 27px,#D6D0C4 27px 28px);}
.cork-card{position:absolute;background:#F6F1E4;border:1px solid #D6D0C4;box-shadow:0 10px 22px rgba(30,27,46,.16);border-radius:2px;padding:16px 18px;font-family:'Space Grotesk',sans-serif;font-size:14.5px;line-height:1.4;color:#1E1B2E;}
.pin{position:absolute;top:-7px;left:50%;transform:translateX(-50%);width:12px;height:12px;border-radius:50%;background:#3D5F75;box-shadow:0 2px 4px rgba(0,0,0,.3);}
.c1{top:96px;left:24px;right:96px;transform:rotate(-3deg);}
.c2{top:210px;left:56px;right:40px;transform:rotate(2deg);}
.c3{top:322px;left:24px;right:110px;transform:rotate(-1.5deg);}
```

### 4. Case File Quote

A typewriter-styled transcript excerpt in a rotated, taped white card, a redaction bar striking
the unimportant half of a sentence, a divider, then a second before/after line using `.hl` for
the phrase that mattered.

```html
<div class="card">
  <div class="tape"></div>
  <div class="label"><!-- SLOT: label 1, e.g. "THE LINE THAT SANK HIM" --></div>
  <div class="quote">&ldquo;<!-- SLOT: quoted phrase --><span class="redact"><!-- SLOT: redaction filler, e.g. xxxxxxxxxxxx --></span></div>
  <div class="sub"><!-- SLOT: one-line gloss --></div>
  <div class="divider"></div>
  <div class="label"><!-- SLOT: label 2, e.g. "THE LINE THAT SAVED HER" --></div>
  <div class="quote">&ldquo;<!-- SLOT: quoted phrase, wrap the key words in <span class="hl">...</span> --></div>
  <div class="sub"><!-- SLOT: one-line gloss --></div>
</div>
```

```css
body{background-color:#EDE8DC;background-image:repeating-linear-gradient(0deg,transparent 0 27px,#D6D0C4 27px 28px);}
.card{position:absolute;top:96px;left:18px;right:70px;background:#F6F1E4;border:1px solid #D6D0C4;box-shadow:0 14px 30px rgba(30,27,46,.16);transform:rotate(-1.1deg);padding:22px 20px;border-radius:2px;}
.tape{position:absolute;top:-12px;left:32px;width:60px;height:22px;background:rgba(150,186,208,.55);transform:rotate(-6deg);box-shadow:0 2px 6px rgba(0,0,0,.08);}
.label{font-family:'Space Grotesk',sans-serif;font-size:10px;font-weight:700;letter-spacing:.1em;color:#3D5F75;margin-bottom:8px;}
.quote{font-family:'JetBrains Mono',monospace;font-size:15px;line-height:1.5;color:#1E1B2E;position:relative;margin-bottom:6px;}
.redact{background:#3D5F75;color:#3D5F75;border-radius:2px;padding:0 3px;}
.sub{font-family:'Space Grotesk',sans-serif;font-size:11.5px;line-height:1.5;color:#5b5648;margin-bottom:18px;}
.divider{height:1px;background:#D6D0C4;margin:14px 0;}
.hl{background:#96BAD0;padding:0 4px;border-radius:2px;}
```

### 5. Field Notes Checklist

A numbered stack of torn notebook strips, each pinned at a slightly different angle, for
sequential/how-to beats.

```html
<div class="strip s1"><span class="num">01</span><!-- SLOT: step 1 --></div>
<div class="strip s2"><span class="num">02</span><!-- SLOT: step 2 --></div>
<div class="strip s3"><span class="num">03</span><!-- SLOT: step 3 --></div>
```

```css
body{background-color:#EDE8DC;background-image:repeating-linear-gradient(0deg,transparent 0 27px,#D6D0C4 27px 28px);}
.strip{position:absolute;left:18px;right:18px;background:#F6F1E4;border:1px solid #D6D0C4;box-shadow:0 8px 18px rgba(30,27,46,.14);padding:12px 16px;font-family:'Space Grotesk',sans-serif;font-size:14px;color:#1E1B2E;display:flex;gap:12px;align-items:baseline;clip-path:polygon(0 0,100% 2%,99% 100%,1% 98%);}
.num{font-family:'JetBrains Mono',monospace;font-weight:700;color:#3D5F75;font-size:13px;}
.s1{top:100px;transform:rotate(-1.5deg);}
.s2{top:210px;transform:rotate(1deg);}
.s3{top:320px;transform:rotate(-0.8deg);}
```

### 6. Ledger Recap

A small corkboard grid of 3-4 miniature pinned notes, each one word or number, summarizing the
whole deck at a glance — the "flip back through the notebook" close.

```html
<div class="mini-cork m1"><!-- SLOT: word/number 1 --></div>
<div class="mini-cork m2"><!-- SLOT: word/number 2 --></div>
<div class="mini-cork m3"><!-- SLOT: word/number 3 --></div>
<div class="mini-cork m4"><!-- SLOT: word/number 4 (optional) --></div>
```

```css
body{background-color:#EDE8DC;background-image:repeating-linear-gradient(0deg,transparent 0 27px,#D6D0C4 27px 28px);}
.mini-cork{position:absolute;width:88px;background:#F6F1E4;border:1px solid #D6D0C4;box-shadow:0 8px 16px rgba(30,27,46,.16);border-radius:2px;padding:12px 10px;font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:15px;color:#3D5F75;text-align:center;}
.m1{top:120px;left:24px;transform:rotate(-4deg);}
.m2{top:110px;right:30px;transform:rotate(3deg);}
.m3{top:250px;left:60px;transform:rotate(2deg);}
.m4{top:260px;right:50px;transform:rotate(-3deg);}
```

### 7. Diff Stack *(blended from Terminal Marginalia)*

Two stacked cards on the grid-paper ground: darker-blue "before," lighter-blue "after," connected
by a thin down-arrow. Restrained to brand blues only — never red/green.

```html
<div class="diffcard d1"><div class="tag"><!-- SLOT: e.g. "&minus; SANK IT" --></div><div class="qt">&ldquo;<!-- SLOT: before quote --></div></div>
<div class="arrowdown">&darr;</div>
<div class="diffcard d2"><div class="tag"><!-- SLOT: e.g. "+ SAVED IT" --></div><div class="qt">&ldquo;<!-- SLOT: after quote --></div></div>
```

```css
body{background-color:#EDE8DC;background-image:linear-gradient(rgba(61,95,117,.09) 1px,transparent 1px),linear-gradient(90deg,rgba(61,95,117,.09) 1px,transparent 1px);background-size:26px 26px;}
.diffcard{position:absolute;left:18px;right:18px;border-radius:6px;padding:16px 18px;font-family:'JetBrains Mono',monospace;}
.d1{top:112px;background:#3D5F75;color:#EDE8DC;}
.d2{top:262px;right:70px;background:#96BAD0;color:#1E1B2E;}
.tag{font-size:10px;font-weight:700;letter-spacing:.08em;margin-bottom:8px;opacity:.85;}
.qt{font-size:14.5px;line-height:1.5;}
.arrowdown{position:absolute;top:214px;left:38px;font-size:20px;color:#3D5F75;font-weight:700;}
```

### 8. Prompt Statement *(blended)*

Full-bleed grid-paper ground, one giant monospace headline set like a terminal prompt, a
blinking-cursor glyph at the end. No card.

```html
<div class="label"><!-- SLOT: small monospace label, e.g. "// 40+ debriefs, interviewer side" --></div>
<div class="prompt"><span class="sym">$</span> <!-- SLOT: prompt name, e.g. the_tell --><span class="out">&gt; <!-- SLOT: output line --><span class="cursor"></span></span></div>
```

```css
body{background-color:#EDE8DC;background-image:linear-gradient(rgba(61,95,117,.09) 1px,transparent 1px),linear-gradient(90deg,rgba(61,95,117,.09) 1px,transparent 1px);background-size:26px 26px;}
.prompt{position:absolute;top:172px;left:18px;right:18px;font-family:'JetBrains Mono',monospace;font-weight:700;font-size:27px;line-height:1.35;color:#1E1B2E;}
.prompt .sym{color:#6B8FA8;}
.prompt .out{color:#3D5F75;font-weight:500;font-size:22px;display:block;margin-top:8px;}
.cursor{display:inline-block;width:11px;height:22px;background:#6B8FA8;margin-left:4px;vertical-align:-4px;}
.label{position:absolute;top:70px;left:18px;font-family:'JetBrains Mono',monospace;font-size:10.5px;color:#3D5F75;letter-spacing:.05em;}
```

### 9. Comment-Line Quote *(blended)*

A quote set as a code comment, JetBrains Mono, tilted against the grid-paper ground, with a small
bracket annotation pointing at the key phrase.

```html
<div class="comment-line"><span class="slash">// </span>&ldquo;<!-- SLOT: quoted phrase, one line --></div>
<div class="bracket">&#9492;&#9472; <!-- SLOT: short annotation, e.g. "the tell" --></div>
```

```css
body{background-color:#EDE8DC;background-image:linear-gradient(rgba(61,95,117,.09) 1px,transparent 1px),linear-gradient(90deg,rgba(61,95,117,.09) 1px,transparent 1px);background-size:26px 26px;}
.comment-line{position:absolute;top:220px;left:18px;right:18px;font-family:'JetBrains Mono',monospace;font-size:19px;line-height:1.5;color:#1E1B2E;transform:rotate(-1.5deg);}
.comment-line .slash{color:#6B8FA8;font-weight:700;}
.bracket{position:absolute;top:280px;left:34px;font-family:'JetBrains Mono',monospace;font-size:12px;color:#3D5F75;transform:rotate(-1.5deg);}
```

## Rhythm

Alternate page-types — never the same archetype twice in a row (a torn exhibit, then a dense
annotated card, then a wide-open verdict page). Don't run two terminal-flavored archetypes
(7-9) back to back either.

## Inherited unchanged

`.hl` highlight-block typography; the reused doodle set (star, curved arrow, dot cluster) at low
opacity; brand tokens (`#6B8FA8`/`#96BAD0`/`#3D5F75`, Space Grotesk + JetBrains Mono, kraft
ruled-line and grid-paper textures); fixed overlay anchors (counter top-left, follow-tag
top-right, swipe arrow center-right, save-tag bottom-right, cliffhanger bottom-center, 18px
insets).
