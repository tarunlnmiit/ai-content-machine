# Life Carousel Skin — LOCKED TEMPLATE PACK (Kitchen Table Confessional + Quiet Hour)

Base philosophy: **Kitchen Table Confessional** — the fridge door, the bedside notebook, the group
chat at midnight. A real feeling written down before anyone smoothed it into a caption; nothing
staged for the camera. Two archetypes from the sibling philosophy **Quiet Hour** (the hushed,
singular, subtractive register of the last twenty minutes before sleep) are folded in for heavier
essay beats that need stillness rather than scatter.

## Visual language

- **Palette**: warm coral `#E8705A` (primary), `#EF9585` (light), `#B34A38` (dark) — reads like a
  sticky note or highlighter, never a corporate accent. The two blended Quiet Hour archetypes
  desaturate toward dusk: `#B34A38` doing most of the work, photo scrims deepened
  (`rgba(20,14,10,...)`) so the mood reads evening rather than daylight.
- **Fonts**: Lora (serif, italic-leaning) for the confession/line itself; Nunito Sans for the
  plain-spoken aside, eyebrow, and UI chrome.
- **Ground**: photo backgrounds on hook/CTA slides via `.slide-photo-bg` (asset-marker contract
  below) with a scrim only where legibility demands it. Non-photo slides use kraft/cream
  `#EDE8DC`, border `#D6D0C4`.

## How these templates work (read before generating)

1. Every archetype below ships as a complete markup block + the CSS it needs. Use it EXACTLY —
   only fill the `<!-- SLOT: ... -->` comments with real copy. Do not drop the sticker pill, the
   torn edge, the Polaroid frame, the letter, or any other signature element to make a slide
   "simpler."
2. The **shared overlay chrome** (progress row, counter chip, follow-tag, swipe-arrow, save-tag,
   cliffhanger) is defined once below in two ground variants — include it, verbatim, on every
   slide, choosing whichever variant matches that slide's background (photo/dark ground vs.
   plain kraft/cream ground). Which of follow-tag / save-tag / cliffhanger actually renders on a
   given slide still follows the main system prompt's per-slide-role rules (badge always;
   follow-tag CTA-slide only; save-tag hook-slide only; swipe-arrow every slide but the last;
   cliffhanger every slide but the last).
3. Every slide commits fully to ONE register (a photo slide trusts the photo, a text-thread slide
   trusts the plain bubbles) rather than blending three per slide. Never run two Quiet Hour
   archetypes (7-8) back to back, and don't let every slide be a photo.
4. The reused doodle set (star outline, small heart, soft squiggle) is placed inconsistently,
   never mirrored — a real hand doesn't repeat itself. On archetypes 7-8 it thins to a single
   soft squiggle at most, at lower opacity.

## Real-asset placeholders

A photo background is injected by the calling script AFTER generation via a literal marker —
never embed real image bytes yourself. Define it once in `<style>` as
`.slide-photo-bg{background-image:url("__LIFE_BG__");background-size:cover;background-position:center
20%;}`, apply the `slide-photo-bg` class to the slide element, and do not write any other rule
setting the `background` SHORTHAND on that same slide (it resets `background-image` to `none`).
When no photo is available this run, skip every photo-based archetype (1, 4, 7 below use a photo;
substitute a plain dusk/kraft ground instead).

## Shared overlay chrome

**Dark/photo-ground variant** (photo backgrounds, letters on dark paper, Quiet Hour night ground):

```css
.progress-row{position:absolute;top:0;left:0;right:0;display:flex;gap:4px;padding:8px 12px 0;z-index:20;}
.progress-seg{flex:1;height:3px;border-radius:2px;background:rgba(255,255,255,.28);overflow:hidden;}
.progress-seg .fill{height:100%;border-radius:2px;background:rgba(255,255,255,.85);}
.counter-chip{position:absolute;top:18px;left:18px;background:rgba(255,255,255,.92);color:#1E1B2E;font-size:11px;font-weight:600;padding:5px 10px;border-radius:20px;letter-spacing:.03em;z-index:20;font-family:'Space Grotesk',sans-serif;}
.follow-tag{position:absolute;top:18px;right:18px;font-size:10.5px;font-weight:600;color:#EDE8DC;background:rgba(255,255,255,.14);padding:5px 10px;border-radius:20px;letter-spacing:.02em;z-index:20;font-family:'Space Grotesk',sans-serif;}
.swipe-arrow{position:absolute;top:50%;right:18px;transform:translateY(-50%);width:38px;height:38px;border-radius:50%;background:#EDE8DC;color:#1E1B2E;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;box-shadow:0 8px 18px rgba(0,0,0,.3);z-index:20;}
.save-tag{position:absolute;bottom:18px;right:18px;font-size:10px;font-weight:600;color:#EDE8DC;background:rgba(255,255,255,.14);padding:5px 9px;border-radius:6px;letter-spacing:.03em;z-index:20;font-family:'Space Grotesk',sans-serif;}
.cliffhanger{position:absolute;bottom:17px;left:0;right:0;text-align:center;font-size:9.5px;letter-spacing:.05em;text-transform:uppercase;z-index:20;font-family:'Space Grotesk',sans-serif;color:#EDE8DC;opacity:.85;}
```

**Light-ground variant** (kraft/cream backgrounds — sticky notes, thread, torn strips, scrapbook):

```css
.progress-row{position:absolute;top:0;left:0;right:0;display:flex;gap:4px;padding:8px 12px 0;z-index:20;}
.progress-seg{flex:1;height:3px;border-radius:2px;background:rgba(0,0,0,.12);overflow:hidden;}
.progress-seg .fill{height:100%;border-radius:2px;background:rgba(0,0,0,.42);}
.counter-chip{position:absolute;top:18px;left:18px;background:rgba(30,27,46,.88);color:#EDE8DC;font-size:11px;font-weight:600;padding:5px 10px;border-radius:20px;letter-spacing:.03em;z-index:20;font-family:'Space Grotesk',sans-serif;}
.follow-tag{position:absolute;top:18px;right:18px;font-size:10.5px;font-weight:600;color:#B34A38;background:rgba(255,255,255,.75);padding:5px 10px;border-radius:20px;letter-spacing:.02em;z-index:20;font-family:'Space Grotesk',sans-serif;}
.swipe-arrow{position:absolute;top:50%;right:18px;transform:translateY(-50%);width:38px;height:38px;border-radius:50%;background:#B34A38;color:#fff;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;box-shadow:0 8px 18px rgba(0,0,0,.3);z-index:20;}
.save-tag{position:absolute;bottom:18px;right:18px;font-size:10px;font-weight:600;color:#B34A38;background:rgba(255,255,255,.75);padding:5px 9px;border-radius:6px;letter-spacing:.03em;z-index:20;font-family:'Space Grotesk',sans-serif;}
.cliffhanger{position:absolute;bottom:17px;left:0;right:0;text-align:center;font-size:9.5px;letter-spacing:.05em;text-transform:uppercase;z-index:20;font-family:'Space Grotesk',sans-serif;color:#B34A38;opacity:.85;}
```

```html
<div class="progress-row"><!-- one .progress-seg per slide in the deck, repeated identically on every slide --></div>
<div class="counter-chip"><!-- SLOT: e.g. "2 / 8" --></div>
<div class="follow-tag">Tap to follow &rarr;</div> <!-- CTA slide only -->
<div class="swipe-arrow">&rarr;</div> <!-- every slide except the last -->
<div class="save-tag">Save this &darr;</div> <!-- hook slide only -->
<div class="cliffhanger"><!-- SLOT: teaser micro-line --></div> <!-- every slide except the last -->
```

## HOOK TEMPLATE (mandatory) — Full-Bleed Confession

One full-bleed photo, minimal scrim, a single short handwritten-feel Lora line set large and low
on the frame. No card. Uses the dark/photo-ground overlay chrome.

```html
<div class="scrim"></div>
<div class="eyebrow"><!-- SLOT: short uppercase eyebrow --></div>
<div class="line"><!-- SLOT: 5-8 word headline, italic Lora --></div>
```

```css
body{background:#1E1B2E url("__LIFE_BG__") center/cover no-repeat;}
.scrim{position:absolute;inset:0;background:linear-gradient(180deg,rgba(20,14,10,.05) 0%,rgba(20,14,10,.15) 45%,rgba(20,14,10,.82) 100%);}
.eyebrow{position:absolute;top:64px;left:18px;right:60px;font-family:'Nunito Sans',sans-serif;font-size:11px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:#EF9585;}
.line{position:absolute;bottom:64px;left:18px;right:18px;font-family:'Lora',serif;font-style:italic;font-weight:600;font-size:27px;line-height:1.3;color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.35);}
```

Do not flatten this to plain text on a solid background — the photo + scrim + eyebrow + large
italic line is the whole point of this archetype.

## CTA TEMPLATE (derived from hook — photo + scrim REPLACES the brand gradient for this niche)

```html
<div class="scrim"></div>
<div class="eyebrow"><!-- SLOT: short uppercase eyebrow --></div>
<div class="line"><!-- SLOT: CTA line, reposition higher (top:270px) to leave room for the button --></div>
<div class="cta-btn"><!-- SLOT: comment-keyword button copy --></div>
```

```css
.line{position:absolute;top:270px;left:18px;right:18px;font-family:'Lora',serif;font-style:italic;font-weight:600;font-size:24px;line-height:1.3;color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.35);}
.cta-btn{position:absolute;bottom:64px;left:18px;right:18px;background:rgba(255,255,255,.14);border:1.5px solid #EDE8DC;color:#EDE8DC;font-family:'Nunito Sans',sans-serif;font-weight:800;font-size:14px;text-align:center;padding:13px;border-radius:24px;letter-spacing:.02em;}
```

## Archetype library (8 — vary register slide to slide, never the same twice in a row)

### 1. Full-Bleed Confession

See HOOK TEMPLATE above — this archetype IS the hook template; reuse it unchanged whenever a
body slide also wants one full-bleed photo moment.

### 2. Fridge-Note Stack

2-3 sticky-note fragments of the hook, each independently rotated and slightly overlapping,
scattered rather than stacked cleanly, on plain kraft/cream ground.

```html
<div class="sticky st1"><!-- SLOT: hook fragment 1 --></div>
<div class="sticky st2"><!-- SLOT: hook fragment 2 --></div>
<div class="sticky st3"><!-- SLOT: hook fragment 3 (optional) --></div>
```

```css
body{background:#EDE8DC;}
.sticky{position:absolute;padding:14px 16px;border-radius:8px;box-shadow:0 8px 18px rgba(0,0,0,.18);font-family:'Lora',serif;font-style:italic;font-weight:600;font-size:16px;line-height:1.35;color:#1E1B2E;}
.st1{top:110px;left:24px;right:80px;background:#E8705A;color:#fff;transform:rotate(-3deg);}
.st2{top:230px;left:60px;right:36px;background:#EF9585;transform:rotate(2deg);}
.st3{top:350px;left:20px;right:100px;background:#fff;border:1px solid #D6D0C4;transform:rotate(-1.5deg);}
```

### 3. Text-Thread Confession

The story beat as an iMessage-style bubble exchange (2-3 bubbles), plain background, no photo,
no card — pure dialogue.

```html
<div class="hdr"><!-- SLOT: short uppercase header --></div>
<div class="thread">
  <div class="bubble recv">&ldquo;<!-- SLOT: received line 1 --></div>
  <div class="bubble sent"><!-- SLOT: sent line 1 --></div>
  <div class="bubble recv"><!-- SLOT: received line 2 (optional) --></div>
  <div class="bubble sent"><!-- SLOT: sent line 2 (optional) --></div>
</div>
```

```css
body{background:#EDE8DC;}
.hdr{position:absolute;top:64px;left:18px;right:18px;font-family:'Nunito Sans',sans-serif;font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#B34A38;}
.thread{position:absolute;top:104px;left:18px;right:70px;display:flex;flex-direction:column;gap:10px;}
.bubble{max-width:82%;padding:11px 15px;border-radius:16px;font-family:'Nunito Sans',sans-serif;font-size:14px;line-height:1.4;}
.recv{align-self:flex-start;background:#fff;border:1px solid #D6D0C4;color:#1E1B2E;border-bottom-left-radius:4px;}
.sent{align-self:flex-end;background:#E8705A;color:#fff;border-bottom-right-radius:4px;}
```

### 4. Polaroid Proof

A single Polaroid-framed photo (white border, tiny handwritten caption inside the frame),
rotated, on cream ground — the "moment that happened" beat. Only use when a photo asset is
available this run; otherwise substitute a solid coral `<div>` fill in place of the `<img>`.

```html
<div class="polaroid">
  <img src="<!-- SLOT: photo marker -->">
  <div class="cap"><!-- SLOT: tiny handwritten caption --></div>
</div>
```

```css
body{background:#EDE8DC;}
.polaroid{position:absolute;top:80px;left:56px;right:56px;background:#fff;padding:14px 14px 34px;box-shadow:0 20px 40px rgba(0,0,0,.22);transform:rotate(-2.5deg);}
.polaroid img{width:100%;height:320px;object-fit:cover;display:block;}
.cap{position:absolute;bottom:10px;left:14px;right:14px;font-family:'Lora',serif;font-style:italic;font-size:13px;color:#5b5648;text-align:center;}
```

### 5. Torn-List Practice

A numbered list rendered as a torn notebook strip, pinned at a candid angle, for the
how-to/practice beat.

```html
<div class="tstrip t1"><span class="tnum">1</span><!-- SLOT: practice step 1 --></div>
<div class="tstrip t2"><span class="tnum">2</span><!-- SLOT: practice step 2 --></div>
<div class="tstrip t3"><span class="tnum">3</span><!-- SLOT: practice step 3 --></div>
```

```css
body{background:#EDE8DC;}
.tstrip{position:absolute;left:18px;right:18px;background:#fff;border:1px solid #D6D0C4;box-shadow:0 8px 16px rgba(0,0,0,.12);padding:12px 16px;font-family:'Nunito Sans',sans-serif;font-size:14.5px;color:#1E1B2E;display:flex;gap:12px;align-items:baseline;clip-path:polygon(0 0,100% 3%,98% 100%,2% 97%);}
.tnum{font-family:'Lora',serif;font-style:italic;font-weight:700;color:#B34A38;font-size:15px;}
.t1{top:100px;transform:rotate(-1.5deg);}
.t2{top:210px;transform:rotate(1.2deg);}
.t3{top:320px;transform:rotate(-0.8deg);}
```

### 6. Scrapbook Recap

A loose collage recap: 2 small photo corners + 1 sticky note, arranged like a scrapbook page
corner rather than a clean grid. Photos are optional; if none is available this run, drop the
`<img>` tags and keep the two corner boxes as plain coral/cream fills.

```html
<div class="corner-photo cp1"><img src="<!-- SLOT: optional photo marker --></div>
<div class="corner-photo cp2"><img src="<!-- SLOT: optional photo marker --></div>
<div class="mini-sticky"><!-- SLOT: one-line recap phrase --></div>
```

```css
body{background:#EDE8DC;}
.corner-photo{position:absolute;width:120px;height:120px;box-shadow:0 10px 20px rgba(0,0,0,.2);}
.corner-photo img{width:100%;height:100%;object-fit:cover;}
.cp1{top:70px;left:20px;transform:rotate(-4deg);}
.cp2{bottom:120px;right:24px;transform:rotate(3deg);}
.mini-sticky{position:absolute;top:220px;left:50px;right:50px;background:#E8705A;color:#fff;padding:16px 18px;border-radius:8px;box-shadow:0 10px 20px rgba(0,0,0,.18);transform:rotate(-1.5deg);font-family:'Lora',serif;font-style:italic;font-weight:600;font-size:17px;text-align:center;}
```

### 7. The Letter *(blended from Quiet Hour)*

A handwritten-style note on aged/textured paper, addressed, holding one paragraph and a signature
line. Centered on a plain dusk-toned ground — no photo, no sticker. Reserve for a heavier essay
line the confessional register's stickers can't hold. Uses the dark/photo-ground overlay chrome.

```html
<div class="letter">
  <div class="dateline"><!-- SLOT: dateline, e.g. "Dear self," --></div>
  <div class="body-txt"><!-- SLOT: one paragraph --></div>
  <div class="sign"><!-- SLOT: signature line, e.g. "&mdash; a note to carry in" --></div>
</div>
```

```css
body{background:#2b1c17;}
.letter{position:absolute;top:88px;left:34px;right:34px;background:#f3e9d2;box-shadow:0 24px 50px rgba(0,0,0,.45);padding:30px 26px 24px;transform:rotate(-0.8deg);clip-path:polygon(0 0,100% 0,100% 97%,96% 100%,4% 100%,0 96%);}
.dateline{font-family:'Lora',serif;font-style:italic;font-size:12px;color:#8a6a4f;margin-bottom:16px;}
.body-txt{font-family:'Lora',serif;font-size:15px;line-height:1.7;color:#3a2b1c;}
.sign{margin-top:20px;font-family:'Lora',serif;font-style:italic;font-size:13px;color:#8a6a4f;}
```

### 8. Underlined Excerpt *(blended from Quiet Hour)*

A single sentence set as a journal excerpt in Lora, generous negative space, with a hand-drawn
double-underline beneath the operative phrase, on a muted photo (deepened scrim) or plain dusk
ground. Quieter and smaller-scale than the confessional register's sticker treatment. Uses the
dark/photo-ground overlay chrome.

```html
<div class="scrim"></div>
<div class="torn"></div>
<div class="eyebrow"><!-- SLOT: short uppercase eyebrow --></div>
<div class="line"><!-- SLOT: single sentence, wrap the operative phrase in <span class="u2">...</span> --></div>
```

```css
body{background:#1E1B2E url("__LIFE_BG__") center/cover no-repeat;}
.scrim{position:absolute;inset:0;background:radial-gradient(120% 90% at 50% 50%,rgba(20,16,26,.45) 0%,rgba(15,12,20,.86) 100%);}
.torn{position:absolute;bottom:0;left:0;width:120px;height:46px;background:#EDE8DC;clip-path:polygon(0 40%,10% 55%,20% 38%,32% 58%,45% 36%,58% 60%,70% 40%,82% 56%,100% 42%,100% 100%,0 100%);opacity:.92;}
.eyebrow{position:absolute;top:190px;left:0;right:0;text-align:center;font-family:'Nunito Sans',sans-serif;font-size:10px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#EF9585;opacity:.8;}
.line{position:absolute;top:224px;left:60px;right:60px;text-align:center;font-family:'Lora',serif;font-style:italic;font-weight:500;font-size:20px;line-height:1.5;color:#f2ece2;letter-spacing:.01em;}
.u2{border-bottom:2px solid #B34A38;padding-bottom:2px;box-shadow:0 4px 0 -2px #B34A38;}
```

If no photo asset is available this run, drop the `body` image rule and use `body{background:#2b1c17;}`
instead, keeping the scrim, torn edge, eyebrow, and line unchanged.

## Rhythm

Every slide commits fully to ONE register. Vary which register appears slide to slide — don't
run two Quiet Hour archetypes (7-8) back to back, and don't let every slide be a photo.

## Inherited unchanged

Sticker-pill phrase-level highlight technique (2-3 short phrase chunks, each its own rotated pill,
`background:#E8705A` or `#EF9585`, `border-radius:8px`, `box-shadow:0 8px 18px rgba(0,0,0,.18)`,
rotate -3° to 2°); the reused doodle set (star, heart, squiggle); brand tokens
(`#E8705A`/`#EF9585`/`#B34A38`, Lora/Nunito Sans, cream/kraft ground); the photo-background +
scrim treatment on hook and CTA slides; fixed overlay anchors (counter top-left, follow-tag
top-right, swipe arrow center-right, save-tag bottom-right, cliffhanger bottom-center, 18px
insets).
