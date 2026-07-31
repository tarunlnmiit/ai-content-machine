# Poetry Carousel Skin — LOCKED TEMPLATE PACK (Illuminated Manuscript + Darkroom Elegy)

Base philosophy: **Illuminated Manuscript** — the page as relic, gold leaf and hand-lettered drop
capitals, the reverence of a scriptorium. A poem is not decorated, it is illuminated — lit from
within by the care taken over it. Two archetypes from the sibling philosophy **Darkroom Elegy**
(the negative before the print — grain, vignette, grease-pencil marginalia) are folded in as
occasional dark-mode variants — use them for a poem or stanza whose mood wants shadow instead of
gold.

## Visual language

- **Palette**: aged gold `#B89850` (primary), `#D4BC7A` (light), `#8A6E30` (dark) against warm
  parchment cream `#EDE8DC` and near-black ink `#1E1B2E`. Gold is never flat — always graduated,
  foxed, or leafed. The two blended Darkroom Elegy archetypes invert the ground: near-black as
  the base, `#8A6E30` doing most of the accent work, `#B89850` reserved for a single light-leak
  accent.
- **Fonts**: Playfair Display for the verse (display-scale for drop caps/gold-leaf fragments,
  italic and soft-focused on the two blended dark archetypes); DM Sans, small and quiet, for
  attribution/footnote text.
- **Ground textures** — parchment: wide margins, a faint dot-grain
  `radial-gradient(rgba(138,110,48,.05) 1px,transparent 1px);background-size:5px 5px` over
  `#EDE8DC`. The blended dark archetypes replace parchment with true shadow — a radial vignette
  plus a fine grain overlay `radial-gradient(rgba(255,255,255,.04) 1px,transparent 1.4px);
  background-size:3px 3px`.

## How these templates work (read before generating)

1. Every archetype below ships as a complete markup block + the CSS it needs. Use it EXACTLY —
   only fill the `<!-- SLOT: ... -->` comments with real copy. Do not drop the drop-cap, the
   gold-leaf border, the sprockets, the light-leak, or any other signature element to make a
   slide "simpler."
2. The **shared overlay chrome** (progress row, counter chip, follow-tag, swipe-arrow, save-tag,
   cliffhanger) is defined once below in two ground variants — include it, verbatim, on every
   slide, choosing whichever variant matches that slide's background (parchment/light vs. the
   blended dark archetypes). Which of follow-tag / save-tag / cliffhanger actually renders on a
   given slide still follows the main system prompt's per-slide-role rules (badge always;
   follow-tag CTA-slide only; save-tag hook-slide only; swipe-arrow every slide but the last;
   cliffhanger every slide but the last).
3. Alternate ornament-dense and ornament-bare pages — a dense illuminated stanza, then a page of
   almost nothing but one gold-leafed word, then a full decorative frame holding one line. When a
   blended dark archetype (7-8) appears, don't run two of them back to back, or every gold-leaf
   archetype will read the same as every dark one.
4. The reused doodle set (laurel sprig, fleuron, hand-drawn ampersand) recurs consistently enough
   to read as a signature, varied enough in placement to avoid feeling stamped. On archetypes 7-8
   it thins to a single recurring gesture (a light leak, a dust scratch, a sprocket-edge mark).

## Shared overlay chrome

**Light/parchment-ground variant** (used by archetypes 1-6):

```css
.progress-row{position:absolute;top:0;left:0;right:0;display:flex;gap:4px;padding:8px 12px 0;z-index:20;}
.progress-seg{flex:1;height:3px;border-radius:2px;background:rgba(0,0,0,.12);overflow:hidden;}
.progress-seg .fill{height:100%;border-radius:2px;background:rgba(0,0,0,.42);}
.counter-chip{position:absolute;top:18px;left:18px;background:rgba(30,27,46,.88);color:#EDE8DC;font-size:11px;font-weight:600;padding:5px 10px;border-radius:20px;letter-spacing:.03em;z-index:20;font-family:'Space Grotesk',sans-serif;}
.follow-tag{position:absolute;top:18px;right:18px;font-size:10.5px;font-weight:600;color:#8A6E30;background:rgba(255,255,255,.75);padding:5px 10px;border-radius:20px;letter-spacing:.02em;z-index:20;font-family:'Space Grotesk',sans-serif;}
.swipe-arrow{position:absolute;top:50%;right:18px;transform:translateY(-50%);width:38px;height:38px;border-radius:50%;background:#8A6E30;color:#fff;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;box-shadow:0 8px 18px rgba(0,0,0,.3);z-index:20;}
.save-tag{position:absolute;bottom:18px;right:18px;font-size:10px;font-weight:600;color:#8A6E30;background:rgba(255,255,255,.75);padding:5px 9px;border-radius:6px;letter-spacing:.03em;z-index:20;font-family:'Space Grotesk',sans-serif;}
.cliffhanger{position:absolute;bottom:17px;left:0;right:0;text-align:center;font-size:9.5px;letter-spacing:.05em;text-transform:uppercase;z-index:20;font-family:'Space Grotesk',sans-serif;color:#8A6E30;opacity:.85;}
```

**Dark-ground variant** (used by the blended Darkroom Elegy archetypes 7-8):

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

```html
<div class="progress-row"><!-- one .progress-seg per slide in the deck, repeated identically on every slide --></div>
<div class="counter-chip"><!-- SLOT: e.g. "1 / 8" --></div>
<div class="follow-tag">Tap to follow &rarr;</div> <!-- CTA slide only -->
<div class="swipe-arrow">&rarr;</div> <!-- every slide except the last -->
<div class="save-tag">Save this &darr;</div> <!-- hook slide only -->
<div class="cliffhanger"><!-- SLOT: teaser micro-line --></div> <!-- every slide except the last -->
```

## HOOK TEMPLATE (mandatory) — Illuminated Drop Cap

One oversized ornamented gold drop-cap letter beginning the stanza, the rest of the verse set
small and quiet beside/beneath it in a narrow parchment column; wide margins. Uses the
light/parchment-ground overlay chrome.

```html
<div class="title"><!-- SLOT: poem title, small uppercase --></div>
<div class="dropcap"><!-- SLOT: first letter of the opening line --></div>
<div class="stanza"><!-- SLOT: rest of the stanza, use <br> between lines --></div>
<div class="flourish">&#10087;</div>
```

```css
body{background:#EDE8DC;background-image:radial-gradient(rgba(138,110,48,.05) 1px,transparent 1px);background-size:5px 5px;}
.title{position:absolute;top:60px;left:18px;right:18px;font-family:'DM Sans',sans-serif;font-size:10.5px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:#8A6E30;}
.dropcap{position:absolute;top:108px;left:18px;font-family:'Playfair Display',serif;font-weight:700;font-size:108px;line-height:.82;color:#B89850;text-shadow:1px 1px 0 #8A6E30,2px 2px 6px rgba(138,110,48,.25);}
.stanza{position:absolute;top:150px;left:112px;right:24px;font-family:'Playfair Display',serif;font-style:italic;font-size:16px;line-height:1.65;color:#1E1B2E;}
.flourish{position:absolute;top:296px;left:18px;font-family:'Playfair Display',serif;font-size:20px;color:#B89850;}
```

Do not shrink the drop cap or drop the title/flourish — the oversized leafed letter anchoring a
narrow verse column IS this archetype.

## CTA TEMPLATE (derived from hook — same illuminated register)

```html
<div class="title"><!-- SLOT: e.g. "THE FULL POEM" --></div>
<div class="dropcap"><!-- SLOT: first letter of the closing/CTA line --></div>
<div class="stanza"><!-- SLOT: closing line, e.g. "&hellip;the rest, saved below." --></div>
<div class="cta-btn"><!-- SLOT: comment-keyword button copy --></div>
```

```css
.cta-btn{position:absolute;bottom:70px;left:18px;right:18px;background:#8A6E30;color:#EDE8DC;font-family:'DM Sans',sans-serif;font-weight:700;font-size:14px;text-align:center;padding:13px;border-radius:4px;letter-spacing:.04em;}
```

## Archetype library (8 — alternate ornament-dense/bare, never repeat register twice running)

### 1. Illuminated Drop Cap

See HOOK TEMPLATE above — this archetype IS the hook template; reuse it unchanged whenever a
body slide also wants the drop-cap treatment.

### 2. Bordered Psalter Page

A full decorative gold-leaf border frame (double border, laurel/fleuron corner glyphs) enclosing
a single short line centered in the middle, nothing else on the page.

```html
<div class="frame"><div class="frame-inner"></div></div>
<div class="corner c1">&#10087;</div><div class="corner c2">&#10087;</div>
<div class="corner c3">&#10087;</div><div class="corner c4">&#10087;</div>
<div class="line"><!-- SLOT: single short line, use <br> to break across 2-3 lines --></div>
```

```css
body{background:#EDE8DC;}
.frame{position:absolute;top:52px;left:26px;right:26px;bottom:60px;border:2px solid #B89850;padding:16px;}
.frame-inner{position:absolute;top:8px;left:8px;right:8px;bottom:8px;border:1px solid #D4BC7A;}
.corner{position:absolute;font-family:'Playfair Display',serif;font-size:22px;color:#B89850;}
.c1{top:52px;left:26px;}
.c2{top:52px;right:26px;transform:scaleX(-1);}
.c3{bottom:60px;left:26px;transform:scaleY(-1);}
.c4{bottom:60px;right:26px;transform:scale(-1,-1);}
.line{position:absolute;top:0;bottom:0;left:56px;right:56px;display:flex;align-items:center;justify-content:center;text-align:center;font-family:'Playfair Display',serif;font-style:italic;font-weight:600;font-size:19px;line-height:1.7;color:#1E1B2E;}
```

### 3. Marginal Gloss

The verse set as the main column with a single hand-lettered gold annotation or translation note
in the margin beside it, echoing a scribe's commentary.

```html
<div class="verse-col"><!-- SLOT: main verse, 2-4 lines, use <br> --></div>
<div class="gloss"><!-- SLOT: short margin annotation, italic --></div>
```

```css
body{background:#EDE8DC;}
.verse-col{position:absolute;top:110px;left:18px;right:150px;font-family:'Playfair Display',serif;font-style:italic;font-size:19px;line-height:1.7;color:#1E1B2E;}
.gloss{position:absolute;top:130px;right:18px;width:120px;font-family:'DM Sans',sans-serif;font-size:11px;line-height:1.5;color:#8A6E30;border-left:1px solid #D4BC7A;padding-left:10px;}
```

### 4. Gold Leaf Fragment

One word or short phrase rendered enormous in gradient/leafed gold, filling most of the frame —
the "relic" read.

```html
<div class="fragment"><!-- SLOT: one word or very short phrase --></div>
```

```css
body{background:#EDE8DC;}
.fragment{position:absolute;top:170px;left:18px;right:18px;font-family:'Playfair Display',serif;font-weight:700;font-size:64px;line-height:1.05;background:linear-gradient(135deg,#D4BC7A 0%,#B89850 45%,#8A6E30 100%);-webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:1px 1px 0 rgba(138,110,48,.3);}
```

### 5. Ribbon Colophon

A scroll/ribbon-shaped banner holding the attribution or closing line, gold-bordered, centered
low on a plain parchment ground — the manuscript's closing mark.

```html
<div class="ribbon"><!-- SLOT: attribution or closing line --></div>
```

```css
body{background:#EDE8DC;}
.ribbon{position:absolute;bottom:150px;left:40px;right:40px;background:#F6F1E4;border:1.5px solid #B89850;border-radius:2px;padding:18px 24px;text-align:center;font-family:'Playfair Display',serif;font-style:italic;font-size:16px;color:#1E1B2E;}
.ribbon:before,.ribbon:after{content:'';position:absolute;top:0;bottom:0;width:14px;background:#B89850;}
.ribbon:before{left:-14px;clip-path:polygon(100% 0,0 50%,100% 100%);}
.ribbon:after{right:-14px;clip-path:polygon(0 0,100% 50%,0 100%);}
```

### 6. Facing-Leaves Recap

Two narrow parchment "pages" side by side, each holding a short fragment of the poem, divided by
a thin gold gutter rule — the "open book" close.

```html
<div class="leaf l1"><!-- SLOT: fragment 1 --></div>
<div class="gutter"></div>
<div class="leaf l2"><!-- SLOT: fragment 2 --></div>
```

```css
body{background:#EDE8DC;}
.leaf{position:absolute;top:90px;bottom:90px;width:172px;font-family:'Playfair Display',serif;font-style:italic;font-size:15px;line-height:1.6;color:#1E1B2E;}
.l1{left:24px;}
.l2{right:24px;}
.gutter{position:absolute;top:80px;bottom:80px;left:50%;width:1px;background:#B89850;transform:translateX(-50%);}
```

### 7. Light Leak Fragment *(blended from Darkroom Elegy)*

Near-total darkness with a single warm gold light-leak radial glow bleeding in from one corner, a
fine grain overlay across the whole frame, and one short phrase lit by the leak — nothing else on
the page. Uses the dark-ground overlay chrome.

```html
<div class="leak"></div>
<div class="grain"></div>
<div class="phrase"><!-- SLOT: one short phrase, use <br> to break across 1-2 lines --></div>
```

```css
body{background:#0b090e;}
.leak{position:absolute;top:-80px;right:-80px;width:340px;height:340px;border-radius:50%;background:radial-gradient(circle,rgba(184,152,80,.85) 0%,rgba(184,152,80,.28) 40%,rgba(184,152,80,0) 70%);}
.grain{position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.04) 1px,transparent 1.4px);background-size:3px 3px;}
.phrase{position:absolute;top:290px;left:34px;right:60px;font-family:'Playfair Display',serif;font-style:italic;font-weight:600;font-size:21px;line-height:1.55;color:#f4e9d2;text-shadow:0 0 14px rgba(184,152,80,.4);}
```

### 8. Contact Print *(blended from Darkroom Elegy)*

A dark, grainy radial-vignette field, a sprocket-hole column down one edge, a small uppercase
frame-label near the top, and one short handwritten-style verse line in pale grease-pencil white
low in the frame. No card, no gold border — the photographic negative read. Uses the dark-ground
overlay chrome.

```html
<div class="grain"></div>
<div class="sprockets">
  <div class="sprocket"></div><div class="sprocket"></div><div class="sprocket"></div>
  <div class="sprocket"></div><div class="sprocket"></div><div class="sprocket"></div>
</div>
<div class="title"><!-- SLOT: frame label, e.g. "frame 07 &middot; the poem title" --></div>
<div class="grease"><!-- SLOT: short verse line, use <br> for a 2-line break --></div>
```

```css
body{background:radial-gradient(120% 90% at 35% 30%,#2a2318 0%,#161219 55%,#0c0a10 100%);}
.grain{position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.05) 1px,transparent 1.4px);background-size:3px 3px;opacity:.5;}
.sprockets{position:absolute;top:70px;bottom:70px;left:14px;width:8px;display:flex;flex-direction:column;justify-content:space-between;}
.sprocket{width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,.18);}
.title{position:absolute;top:80px;left:40px;right:32px;font-family:'DM Sans',sans-serif;font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;color:rgba(212,188,122,.55);}
.grease{position:absolute;bottom:70px;left:40px;right:32px;font-family:'Playfair Display',serif;font-style:italic;font-weight:500;font-size:20px;line-height:1.5;color:#efe9dc;text-shadow:0 0 8px rgba(0,0,0,.5);}
```

## Rhythm

Alternate ornament-dense and ornament-bare pages — a dense illuminated stanza, then a page of
almost nothing but one gold-leafed word, then a full decorative frame holding one line. When a
blended dark archetype (7-8) appears, treat it as its own bare extreme and don't run two of them
back to back.

## Inherited unchanged

Brand tokens (`#B89850`/`#D4BC7A`/`#8A6E30`, Playfair Display/DM Sans, cream parchment ground,
dark ink `#1E1B2E`); the `.hl` highlight-block technique reinterpreted as gold-leaf phrase
emphasis on the light archetypes and as the single light-leak accent on the two blended dark
ones; fixed overlay anchors (counter top-left, follow-tag top-right, swipe arrow center-right,
save-tag bottom-right, cliffhanger bottom-center, 18px insets).
