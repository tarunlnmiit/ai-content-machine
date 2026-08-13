---
title: "Carousel + Brag-Video Research (2026-07-28)"
type: doc
date: 2026-07-28
week: 2026-W31
slug: carousel-brag-research
tags: [content/doc, week/2026-W31]
---
# Carousel + Brag-Video Research (2026-07-28)

Sources: three parallel research agents (2 Sonnet, 1 Haiku) covering carousel visual design/hooks/structure/algorithm facts, carousel generation tooling, and short launch/brag-video best practices — 2025-2026 web research, IG-only (LinkedIn dropped per Tarun). Full agent reports appended verbatim as appendices.

## Executive Summary

Research covered two active pipelines: the Instagram carousel generator and the HyperFrames brag-video generator. Three headline conclusions: (1) the carousel LLM-regenerates-full-HTML-per-run approach is the documented 2025-2026 industry anti-pattern — the market converged on locked design tokens + content injection, which this pipeline now adopts via a skin/archetype library rather than a full tooling swap; (2) carousel and brag-video hooks/structure follow the same underlying mechanics (5-8 word hook, <30 words/slide or kinetic text ≤1.5s, curiosity/pattern-interrupt over generic openers, specific CTA over generic follow/like asks); (3) IG's 2026 ranking shift rewards saves and DM-sends over likes and rewards raw/authentic over polished-and-AI-flavored content — both pipelines were adjusted toward variety, specificity, and grounding in real artifacts rather than generic template repetition.

## Carousel Findings

### Visual design
Minimalism (white background, black text, huge type, whitespace) still signals authority/expertise. Collage/scrapbook style (torn textures, stickers, cutouts) reads as casual/authentic to Gen Z audiences and is directionally aligned with the current collage system. Canva's 2026 trend report names "Imperfect by Design" — deliberately raw, unpolished visuals — as the dominant shift, because AI made glossy design cheap and ubiquitous; casual/raw content converts up to 400% better than polished studio shots in some categories, and 80% of surveyed creators want to "regain creative control from the algorithm." A direct warning: audiences now visually recognize Canva/template carousels the way they used to recognize stock photos — the same ~20 top templates reposted thousands of times since 2023 read as generic on sight. The antidote is bespoke per-slide composition, varying type hierarchy and layout slide-to-slide, not a single repeating template frame. Net: the collage system is on-trend directionally, but risks becoming its own recognizable template shape unless composition genuinely varies slide-to-slide. (carousel-design-report.md)

### Hook slide
Headline should be 5-8 words, the largest text on the slide, a concrete promise (specific numbers/outcomes beat vague description). Formula: bold hook headline + visual pattern interrupt (high contrast / dramatic graphic / expressive face) + a curiosity trigger (partial reveal, surprising stat, unresolvable question). Text ceiling is under 30 words per slide, one concept per slide, 5-second comprehension test. Visual energy pointing toward the right edge, or partial reveals bleeding into the next slide, is repeatedly cited as a swipe-through driver. (carousel-design-report.md)

### Structure & retention
Slide count consensus is 8-10 for educational/career content (5-8 for quick tips, 8-12 for depth/educational, 12-20 only for deep guides or photo-dump storytelling); engagement reportedly dips after slide 3 and picks back up at slide 8+. Completion targets are 55-65%+ swipe-through; below that the carousel is "too long for its own hook." A cliffhanger/micro-hook technique — a one-line tease at the bottom of each slide ("Next: the tool that saves 2 hours a week") — reduces slide-to-slide drop-off. The CTA/recap slide must mirror the hook slide's visual style; a stylistically jarring CTA slide "reads as an ad and tanks save rate." Effective CTA copy is specific ("DM 'CHECKLIST'...", "save this for the next time you ___"); generic like/comment/tag CTAs are the most-ignored. On follow/save badges on every slide: no source validated that pattern — IG's re-serve mechanic already re-shows slide 2 to non-swipers, and sends are the most rewarded 2026 signal, so CTA emphasis should shift toward send/share language, with badges limited to the first and last slide. (carousel-design-report.md)

### Algorithm/format facts
IG carousel max is 20 slides, 1080×1350 (4:5) recommended. 2026 ranking shifted toward active dwell time and swipe-through velocity — every swipe is a distinct engagement event. Saves are the most heavily weighted signal; sends (DM shares) are the top signal for reaching new audiences. Format data (Metricool/HypeAuditor, Socialinsider 2025-2026): Reels win reach for small accounts (median ~134 views vs ~56 for carousels at <1K followers, Reels reach rate ~30.8%, roughly 2-3x carousels) but carousels generate roughly 9x more saves than single images; above ~1M followers the reach picture flips (carousel median reach 217,668 vs Reels 110,500). Engagement by format: ~9-10% carousels vs 6-7% Reels vs 5-6% single images. Music on carousels pushes the carousel into the Reels distribution surface for broader reach while keeping carousel-native engagement depth — a currently unused lever. (carousel-design-report.md)

### Anti-patterns
Template recognition fatigue is the most repeated criticism — evolve away from a fixed repeating frame. A jarring CTA slide reads as an ad and suppresses saves. Generic CTAs are ignored; specificity performs. Accessibility: WCAG 4.5:1 contrast for normal text, 3:1 for large text (18pt+/24px+, bold 14pt+); ~12px absolute floor with 16px recommended body; line-height 1.5-1.8; design for feed-thumbnail scale, not full size. Dark vs light: neither inherently wins, contrast is the driver; pastel-on-light-grey was flagged as failing in real conditions. (carousel-design-report.md)

### Tooling
The current LLM-regenerates-full-HTML-per-run → Playwright screenshot approach is the documented 2025-2026 industry anti-pattern for consistency (Tier 3 in the research's own tiering). The market converged on **locked design layer + content injection**: commercial tools (PostNitro — market leader, 100+ templates, Brand Kit auto-applied, REST API + Embed SDK; Taplio — LinkedIn-only, $65/mo; aiCarousels — free, 2026 benchmarks) all follow the pattern of (1) design system locked first, (2) content slots injected, (3) export at platform dimensions, (4) no CSS regeneration per slide. Open-source analogs: Open Carrusel (GitHub, MIT) — Claude-native HTML-to-PNG generator, closest analog to the current pipeline; Satori + Vercel OG — JSX template → SVG → PNG via Resvg, design tokens as code and version-controlled, content injected per slide. Consistency best practice ranks Tier 1 (design tokens as code + fixed templates, LLM injects content only, visual regression testing flagging >2% pixel drift) above Tier 2 (template library + AI template selection, PostNitro's model) above Tier 3 (LLM regenerates full HTML/CSS every run — no design continuity, no rollback, silent quality decay — the prior state of this pipeline). Export specs: IG 1080×1350 (4:5) minimum, export at 2x (2160×2700) then downscale for crisper text, sRGB not P3, PNG for overlays, ~30px safe margin. Benchmark: carousel posts 6.6% engagement vs 2.18% single image vs 1.11% text (2026). Recommendation C — lock the brand/token/contract layer in versioned files, keep LLM-driven composition but constrain it with a skin + archetype library, a hybrid of Tier 1 consistency and per-slide design variety — was the one adopted, over a full Satori rebuild (A, 2-3 days setup) or outsourcing to the PostNitro API (B, subscription). (carousel-tooling-report.md)

## Brag-Video Findings

### Video quality/style
Faceless motion graphics are not algorithmically disadvantaged — IG 2026 ranking optimizes completion rate, pacing, and originality, not faces. There is real tension on shares specifically: "low production beats high production for shares in 2026 — the more polished the Reel, the less shareable; raw reads as personal and gets sent to friends." Polished motion graphics may rank fine on watch-time but underperform DM-sends, the #2 ranking signal. Screen-Studio-style polish does outperform in demo/landing-page contexts (85% of buyers persuaded by demo video, up to 86% higher conversion) but that's not organic Reels reach. Top SaaS launches (Figma Config, Stripe Sessions) use fast screen-recording cuts to music with no voiceover, validating the no-VO approach, though at 60-90s. Meta's Dec 31, 2025 memo (Mosseri) states IG will prioritize "raw, real human content" over AI-generated material through 2026 — a headwind for fully-synthetic pipelines, arguing for grounding videos in real screenshots/footage/photos. (brag-video-report.md)

### Hooks
50% of viewers drop off within the first 3 seconds; IG weighs the first two seconds harder than TikTok, with the stay/scroll decision made in 1.7-2s. 3-second retention above 70% triggers wider non-follower distribution. By hook type (3-sec retention): Pattern Interrupt 72-84%, Curiosity Gap 65-78%, Direct Question 58-72%, Bold Claim 55-70%, Problem 50-65%, Social Proof 45-60%. Text hooks should be 5-8 words max, phrased as a question or bold claim, with each text element held at least 2 seconds. Kinetic hook text in the first 1.5 seconds doubles thumb-stop rate versus static text. Audio audible within the first 3 seconds produces roughly 41% higher retention than late-starting audio. (brag-video-report.md)

### Length & looping
7-15s reels get the highest completion and shareability (60-80% retention) and are the most rewatched; 45-60s reels get the highest raw engagement (Socialinsider 2026, ~140k business Reels sampled). The non-follower distribution trigger is 70-80%+ completion past 5 seconds. A 15-25s target is reasonably positioned, but 25s should be treated as a ceiling, not a default — default to 15-18s. Seamless looping (final frame matches the opening frame) drives multiple rewatches per session, and each rewatch counts as a watch-time/completion signal, one of the two strongest 2026 ranking signals — near-zero implementation cost for the payoff. (brag-video-report.md)

### Audio
Watch time is the #1 ranking signal (Mosseri, Jan 2026); sends-per-reach is #2, weighted 3-5x likes. Original/licensed BGM is safe and standard for brand content — it forfeits trending-audio discovery but carries no penalty. Captions are an explicit Reels ranking factor: captioned Reels get roughly 38% longer retention and roughly 65% vs 37% completion. Kinetic (animated) captions hold viewers 39% longer than static captions (Meta internal 2025 research). With no voiceover, on-screen kinetic typography effectively carries the narrative — a ranking lever, not just a style choice. SFX (whoosh/riser/pop/shutter) should be matched precisely to visual beat cuts; a small trusted library beats variety for this purpose. (brag-video-report.md)

### Share performance
DM sends are the most important lever after watch time (3-5x likes weight for non-follower reach); "send this to a friend" CTAs target that signal directly. Keyword-comment CTAs ("Comment LAUNCH") convert 5-15% versus 1-3% for "link in bio," and keyword-rich captions get roughly 30% more reach (caption SEO). (brag-video-report.md)

### Thumbnail/cover
IG's grid switched to a 3:4 crop in early 2025 — design covers at the full 1080×1920 frame but keep faces/text/logo inside the central 1080×1080 safe zone. Treat the cover as a separate design from frame 0: a distinct, high-contrast, bold-text frame built specifically to stop the scroll. (brag-video-report.md)

### Benchmarks
Platform-wide IG engagement is roughly 0.48% (Socialinsider Q1 2026, down 24% year-over-year); Reels roughly 0.50%, carousels 0.55%. Nano creators see roughly 4-4.5% median engagement. No launch-video-specific benchmark exists (acknowledged data gap); the closest proxy is that 15s micro-teasers show 60% higher completion among C-suite viewers. (brag-video-report.md)

## What We're Implementing vs. Recommended-Only

| Status | Carousel | Brag-video |
|---|---|---|
| **IMPLEMENTED (this session)** | Skin/archetype variety system in `v1/design-system/`; hook 5-8 words + <30 words/slide caps; content-driven slide count (5-12 guidance band); cliffhanger micro-lines; badges limited to hook + CTA slides only; CTA slide matches hook style with keyword-comment CTA; 2x supersampled export; dead `*_export.py` artifact removed; new `--outline`/`--export-only` flags; `/carousel` interactive skill | 55-track music library deployment fix; CLAUDE.md quality rules — seamless loop, pattern-interrupt kinetic hook ≤1.5s, beat in first 2-3s, 15-18s default, send/keyword CTA, 1080x1080 cover safe zone, kinetic text in all presets, real grounding artifact, essay-subject adaptation |
| **RECOMMENDED-ONLY (not implemented)** | Music on carousels (would require a scheduler/publish change); Satori/PostNitro pipeline replacement (rejected in favor of the hybrid skin/archetype approach); visual regression testing for slides (possible future work) | Music on carousels item n/a here; anything LinkedIn (explicitly dropped per Tarun — IG only) |

Note: "anything LinkedIn" and "music on carousels" apply to the carousel pipeline (LinkedIn scope explicitly out, per Tarun's direction to the research agents; music-on-carousels requires publish-path changes not made this session). They're listed once here to avoid duplicating the row across both columns.

---

## Appendix A — Carousel Design Report (verbatim)

```
# Carousel research report (IG focus, 2025-2026) — Sonnet research agent, 2026-07-28

(10 web searches across visual design, hooks, structure, algorithm/format facts, and anti-patterns. LinkedIn sections omitted per Tarun's direction.)

## 1. VISUAL DESIGN

- **Minimalism** still dominates for authority/expertise signaling — white background, black text, huge type, generous whitespace. Reads as premium/credible.
- **Collage/scrapbook** (torn textures, stickers, cutout photos, expressive fonts) is popular with Gen Z audiences because it feels casual and authentic vs. polished — directionally similar to the current collage system.
- **Bigger 2026 story: "Imperfect by Design."** Canva's own 2026 trend report names this the dominant shift — deliberately raw, unpolished visuals (phone-shot photos, lo-fi collage, "Notes app" screenshots) outperforming glossy design specifically *because* AI made glossy cheap and ubiquitous. One stat: casual/raw content converts up to 400% better than polished studio shots in some categories. 80% of surveyed creators want to "regain creative control from the algorithm."
- **Direct warning:** audiences now visually recognize Canva/template carousels "the way they used to recognize stock photos" — the same ~20 top templates reposted thousands of times since 2023 read as generic/AI-flavored on sight. Antidote: bespoke per-slide composition (varying type hierarchy and layout slide-to-slide) rather than one repeating template frame.
- Net: the collage system is on-trend directionally, but the risk is rotated-card-on-kraft becoming itself a recognizable template shape. The 2026 differentiator is whether each slide's composition genuinely varies.

## 2. HOOK SLIDE

- Headline: **5-8 words**, largest text on the slide, concrete promise (specific numbers/outcomes beat generic description).
- Formula: **Bold hook headline + visual pattern interrupt (high contrast / dramatic graphic / expressive face) + curiosity trigger** (partial reveal, surprising stat, unresolvable question).
- Text ceiling: **under 30 words per slide**, one concept per slide, 5-second comprehension test.
- "Visual energy pointing toward the right edge / partial reveals bleeding into the next slide" repeatedly cited as a swipe-through driver.

## 3. STRUCTURE & RETENTION

- **Slide count consensus: 8-10 sweet spot** for educational/career content. Ranges: 5-8 quick tips, 8-12 depth/educational, 12-20 only for deep guides or photo-dump storytelling. Engagement reportedly dips after slide 3 and picks back up at slide 8+.
- **Completion targets: 55-65%+ swipe-through**; below that the carousel is "too long for its own hook."
- **Cliffhanger/micro-hook technique**: a one-line tease at the bottom of each slide ("Next: the tool that saves 2 hours a week") reduces slide-to-slide drop-off.
- **CTA/recap slide**: must mirror the hook slide's visual style — a stylistically jarring CTA slide "reads as an ad and tanks save rate." Effective CTA copy is specific ("DM 'CHECKLIST'...", "save this for the next time you ___"); generic like/comment/tag CTAs are the most-ignored.
- **Follow/save badge on every slide**: no source validated the pattern. IG's re-serve mechanic already re-shows slide 2 to non-swipers; "sends" are the most rewarded signal in 2026 — arguing CTA emphasis should shift to send/share language, and per-slide badges are redundant. Recommend limiting badges to first + last slide.

## 4. ALGORITHM / FORMAT FACTS

- IG carousel max **20 slides**, 1080×1350 (4:5) recommended.
- 2026 ranking shifted toward **active dwell time and swipe-through velocity** — every swipe is a distinct engagement event.
- **Saves are the most heavily weighted signal**; "sends" (DM shares) are the top signal for reaching new audiences.
- Format data (Metricool/HypeAuditor, Socialinsider 2025-2026): Reels win reach for small accounts (median ~134 views vs ~56 for carousels at <1K followers); Reels average reach rate ~30.8%, roughly 2-3x carousels — BUT carousels generate roughly **9x more saves than single images**; above ~1M followers the reach picture flips (carousel median reach 217,668 vs Reels 110,500). Engagement by format: ~9-10% carousels vs 6-7% Reels vs 5-6% single images.
- **Music on carousels** pushes the carousel into the Reels distribution surface for broader reach while keeping carousel-native engagement depth — low-effort unused lever.

## 5. ANTI-PATTERNS

- Template recognition fatigue (most repeated criticism) — evolve away from a fixed repeating frame.
- Jarring CTA slide reads as an ad; suppresses saves.
- Generic CTAs are ignored; specificity performs.
- Accessibility: WCAG 4.5:1 contrast normal text, 3:1 large text (18pt+/24px+, bold 14pt+); ~12px absolute floor with 16px recommended body; line-height 1.5-1.8. Design for feed-thumbnail scale, not full size.
- Dark vs light: neither inherently wins; contrast is the driver. Pastel-on-light-grey flagged as failing in real conditions.

## TOP 10 ACTIONABLE CHANGES (ranked by expected impact)

1. Break template recognizability — vary slide composition/layout meaningfully slide-to-slide within the collage system.
2. Add a cliffhanger micro-line to the bottom of each slide.
3. Slide count in the 8-10 educational band (content-driven; 12+ only for deep guides).
4. CTA slide: specific, platform-native copy; visual style matches the hook slide.
5. Limit follow/save badges to first + last slide.
6. Hard caps: 5-8 word hook headlines, <30 words per slide body.
7. Add music to some carousels for Reels-surface distribution.
8. (LinkedIn item dropped per Tarun.)
9. Push saves/DM-send CTAs over follow CTAs.
10. Audit contrast (4.5:1 / 3:1) and bias toward 16px-equivalent minimum body text.

Sources: postnitro.ai, carouselli.com, trymypost.com, socialpilot.co, contentdrips.com, canva.com/newsroom, metricool.com, oktopost.com, meet-lea.com and other 2025-2026 dated guides via WebSearch. Caveat: numeric claims are directionally reliable but not independently verified against primary study PDFs.
```

## Appendix B — Carousel Tooling Report (verbatim)

```
# Carousel generation tooling research (2025-2026) — Haiku research agent, 2026-07-28

## Executive summary
The current approach (LLM → full HTML/CSS regenerated every run → Playwright screenshot) is the industry anti-pattern for consistency. The 2025-2026 market converged on **locked design layer + content injection**.

## 1. Commercial tools
- **PostNitro** (market leader): 100+ templates → LLM injects content → PNG/PDF export; Brand Kit (colors, fonts, logos, layouts) applied automatically; REST API + Embed SDK. Locked design eliminates drift.
- **Taplio**: paste URL/idea → AI writes + designs slides → PDF; Brand Kit; LinkedIn-only, $65/mo.
- **aiCarousels**: free AI carousel generator, used in 2026 benchmarks.
- Common pattern: (1) design system locked first, (2) content slots injected, (3) export at platform dimensions, (4) no CSS regeneration per slide.

## 2. Open-source / programmatic
- **Open Carrusel** (GitHub, MIT): Claude-native HTML-to-PNG carousel generator — Claude generates real HTML/CSS slides, Playwright screenshots at 1080×1350. Closest analog to the current pipeline.
- **Satori + Vercel OG**: JSX template → SVG → PNG via Resvg (faster than Playwright); design tokens are code, version-controlled; content injected per slide.

## 3. Consistency best practice
- Tier 1 (recommended): design tokens as code + fixed templates, LLM injects content only, visual regression testing (Playwright/Percy; flag >2% pixel drift).
- Tier 2: template library + AI template selection + copy injection (PostNitro model).
- Tier 3 (anti-pattern): LLM regenerates full HTML/CSS every run — no design continuity, no rollback, silent quality decay. (= current pipeline.)

## 4. Export specs
- IG: 1080×1350 (4:5) minimum; export at 2× (2160×2700) then downscale for crisper text; sRGB (not P3); PNG for overlays; ~30px safe margin.
- Benchmark: carousel posts 6.6% engagement vs 2.18% single image vs 1.11% text (2026).

## Recommendations
- A: Satori + design tokens (2-3 days setup, 10s/carousel).
- B: PostNitro API (1 day, outsourced, subscription).
- C (adopted, adapted): lock the brand/token/contract layer in versioned files, keep LLM-driven composition but constrained by a skin + archetype library — hybrid of Tier 1 consistency and per-slide design variety.

Sources: postnitro.ai, taplio.com, connectsafely.ai, github.com/Hainrixz/open-carrusel, vercel.com/docs/og-image-generation, trigger.dev, blog.brandghost.ai, postiv.ai.
```

## Appendix C — Brag-Video Report (verbatim)

```
# Short launch/brag video research (2025-2026) — Sonnet research agent, 2026-07-28

Context: auto-generated 15-25s vertical (1080×1920) motion-graphics brag videos (HyperFrames), no voiceover, music+SFX, 7 tone presets, published as IG Reels. (LinkedIn findings dropped per Tarun.)

## 1. Video quality/style
- Faceless motion graphics are NOT algorithmically disadvantaged — IG 2026 ranking optimizes completion rate, pacing, originality, not faces (syncstudio.ai, invideo.io).
- Real tension for SHARES: "low production beats high production for shares in 2026 — the more polished the Reel, the less shareable; raw reads as personal and gets sent to friends" (Aurelius Media, truefuturemedia.com). Polished motion graphics may rank fine on watch-time but underperform DM-sends (#2 ranking signal).
- Screen-Studio-style polish outperforms in demo/landing-page contexts (85% of buyers persuaded by demo video; up to 86% higher conversion) — but that's not organic Reels reach.
- Top SaaS launches (Figma Config, Stripe Sessions) use fast screen-recording cuts to music with NO voiceover — validates the no-VO approach (though at 60-90s).
- Meta's Dec 31, 2025 memo (Mosseri): IG will prioritize "raw, real human content" over AI-generated material through 2026 — headwind for fully-synthetic pipelines; ground videos in real screenshots/footage/photos.

## 2. Hooks
- 50% drop off within first 3 seconds; IG weighs the first TWO seconds harder than TikTok; decision in 1.7-2s.
- 3-sec retention >70% triggers wider non-follower distribution. By hook type (3-sec retention): Pattern Interrupt 72-84%, Curiosity Gap 65-78%, Direct Question 58-72%, Bold Claim 55-70%, Problem 50-65%, Social Proof 45-60%.
- Text hook: 5-8 words max, question or bold claim, each text element held ≥2s. Kinetic hook text in the first 1.5s doubles thumb-stop rate vs static.
- Audio audible within first 3s → ~41% higher retention than late-starting audio.

## 3. Length & looping
- 7-15s reels: highest completion + shareability (60-80% retention), most rewatched. 45-60s: highest raw engagement (Socialinsider 2026, ~140k business Reels). Non-follower distribution trigger: 70-80%+ completion past 5s.
- 15-25s target is reasonably positioned; treat ~25s as ceiling, not default — default 15-18s.
- Seamless looping (final frame matches opening frame) → multiple rewatches per session; each rewatch counts as watch-time/completion signal — one of the two strongest 2026 signals. Near-zero implementation cost.

## 4. Audio
- Watch time #1 signal (Mosseri, Jan 2026); sends-per-reach #2, weighted 3-5x likes.
- Original/licensed BGM is safe and standard for brand content; forfeits trending-audio discovery but no penalty.
- Captions are an explicit Reels ranking factor (Mosseri). Captioned Reels: ~38% longer retention, ~65% vs ~37% completion. Kinetic (animated) captions hold viewers 39% longer than static (Meta internal 2025 research). With no VO, on-screen kinetic typography carries the narrative — a ranking lever, not just style.
- SFX: whoosh/riser/pop/shutter matched precisely to visual beat cuts; small trusted library, precision over variety.

## 5. Share performance
- DM sends: most important lever after watch time (3-5x likes for non-follower reach). "Send this to a friend" CTAs target it directly.
- Keyword-comment CTAs ("Comment LAUNCH") convert 5-15% vs 1-3% for "link in bio". Keyword-rich captions get ~30% more reach (caption SEO).

## 6. Thumbnail/cover
- IG grid switched to 3:4 crop (early 2025): design covers 1080×1920 but keep faces/text/logo inside the central 1080×1080 safe zone.
- Treat the cover as a separate design from frame 0 — a distinct high-contrast bold-text frame that stops the scroll.

## 7. Benchmarks
- Platform-wide IG engagement ~0.48% (Socialinsider Q1 2026, −24% YoY); Reels ~0.50%, carousels 0.55%. Nano creators ~4-4.5% median. No launch-video-specific benchmark exists (data gap); closest proxy: 15s micro-teasers show 60% higher completion among C-suite viewers.

## Top actionable changes (ranked, IG-only)
1. Seamless loop (punchline final frame = hook opening frame).
2. Pattern-interrupt/bold-claim hook, 5-8 words, kinetic entrance within 1.5s; bias chaotic/yc-parody presets toward literal pattern-interrupt mechanics.
3. First music beat inside first 2-3s, no fade-in.
4. Default 15-18s; 20-25s only when the punchline earns it.
5. "Send to a friend" / keyword-comment CTA in punchline card + caption.
6. Dedicated cover frame, critical content in central 1080×1080.
7. Kinetic typography on every key text element in ALL tone presets (esp. polished/default).
8. Ground each video in one real artifact (screenshot/photo) — hedge against Meta's 2026 "raw, real" bias.

Sources: syncstudio.ai, aureliusmedia.co, makerstack.co, advids.co, truefuturemedia.com, newswirejet.com, smmnut.com, digitalzoomstudio.net, socialbu.com, retensis.com, influencers-time.com, dataslayer.ai, manchesterdigital.com, esecut.com, socialync.io, postfa.st, oktopost.com, apaya.com, creatorflow.so. Caveat: secondary marketing-blog sources synthesizing Meta statements; treat exact percentages as directional.
```
