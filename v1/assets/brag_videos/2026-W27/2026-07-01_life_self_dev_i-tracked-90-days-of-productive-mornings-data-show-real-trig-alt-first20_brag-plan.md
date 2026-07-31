# Brag Plan: "FIRST20" — yc-parody for the 90-day mornings essay

## What is this?
Not an app — a personal essay published in the Medium publication **Know Thyself Heal Thyself**:
"I Woke at 6AM Every Day for 90 Days. The Data Said Wake Time Was Never the Point."
The essay tracks 90 mornings of data and finds that wake time never predicted a good day —
first-task latency (how long before you touch real work, phone-first vs not) did. The brag is
real writing, really published. **No recorded live URL** — the proof card shows the real headline
+ the "Know Thyself Heal Thyself" wordmark only, no domain text anywhere.

## The angle
The video is a mock product launch deck for a fake product, **FIRST20**. The essay's real finding —
that the first 20 minutes of your morning are the only variable that matters — is presented as a
polished product spec. Deadpan-straight corporate confidence. The joke is that "FIRST20" is not a
product at all: no app, no alarm gimmick, just the instruction. The medium (a launch deck) becomes
the message.

## Tone
- Preset: yc-parody — mock-corporate confidence, deadpan-straight, the real finding sold as a spec.
- Hard cuts (NOT crossfades). Minimal motion — quick entrance tweens inside each scene, but the
  cut between scenes is a hard slam. Flatter, more graphic than the photographic siblings.
- Typographic flip: **Inter 900 uppercase is the DOMINANT typeface** — it carries the FIRST20
  wordmark and every spec-card headline. Playfair Display is demoted to exactly ONE line — the S4
  manifesto — so that single editorial moment cuts through the mock-corporate deck.

## Color contract
- Background warm `#1a1208`, card bg `#231a0e`, text `#fdf8f0`, muted `#a0856a`.
- Amber `#f59e0b` is the "fake brand color" for the FIRST20 wordmark.
- Warm-red `#ef4444` is LOAD-BEARING: the "34% productive" stat stamp (S3) and the underlined
  phrase "checked out" in the manifesto (S4). Nowhere else.
- Sage `#86efac` is reserved EXCLUSIVELY for the final proof beat — the "Know Thyself Heal
  Thyself" wordmark in S5.

## Storyboard (hard cuts, ~19s total, vertical 1080x1920, all scenes on track 1, back-to-back)
- **S1 hook (0 – 3.0):** hard cut in. Near-black background, static. Centered wordmark, Inter 900
  uppercase amber: "FIRST20." Tagline below, Inter 400: "Stop optimizing your wake-up time.
  Optimize your first 20 minutes."
- **S2 (3.0 – 6.5):** spec card on `#231a0e`. "90 mornings tested." → "1 variable that mattered:
  first-task latency."
- **S3 (6.5 – 10.5):** photo (notebook + laptop) framed as a feature-spec card. Two stat stamps:
  "71% productive" (amber) vs "34% productive" (warm-red). Beneath: "No-phone-first-hour vs
  phone-first."
- **S4 (10.5 – 15.5):** the one Playfair italic moment — a manifesto: "You can't gym your way out
  of a mind that already checked out before it stood up." ("checked out" underlined warm-red).
  Longest hold (5.0s) — 17 words must clear their reading floor before the cut.
- **S5 outro (15.5 – 19.0):** "FIRST20. No app. No alarm gimmick. Just the first 20 minutes." →
  proof tag: "As seen in" + "Know Thyself Heal Thyself" wordmark (sage) + the real unchanged
  headline. NO URL bar / domain anywhere.

## Duration: 19.0s
Five scenes, hard cuts. Reading floors respected — S4 (the 17-word manifesto) gets the longest
hold at 5.0s so it clears its floor before the cut.

## Real data (verbatim, not re-rounded)
- No-phone-first-hour mornings → 71% "productive" self-rating.
- Phone-first mornings → 34% "productive".

## Audio direction
- Role: warm acoustic bed, slightly more produced feel but tasteful — visuals/copy carry the
  parody, not the music. Kept low; nothing swells.
- Source: `v1/assets/audio/bgm/life/itYCLFXGQMc_[No Copyright Music] I Just Want Quiet - Slow Acou.mp3`.
  The brief specified a ~245s offset, but the source is only 214s long — used a fresh 180s offset
  instead (still distinct from the sibling builds, which used ~30s).
- Treatment: trim to 19.0s, `volume=0.20, afade in 1.0s, afade out st=17.5 d=1.5` (slightly faster
  fades matching the hard cuts). Root-level `<audio class="clip">`.

## Share copy (draft)
We built FIRST20 to fix your mornings. It has no app, no alarm gimmick, and no six-step routine —
it is the first 20 minutes of your day, phone untouched. We tested it across 90 mornings: 71%
productive with it, 34% without. Know Thyself Heal Thyself published the data.
