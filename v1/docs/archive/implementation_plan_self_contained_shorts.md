---
title: "Implementation: Self-Contained Short-Form Repurposing"
type: doc
slug: implementation-plan-self-contained-shorts
tags: [content/doc]
---
# Implementation: Self-Contained Short-Form Repurposing

**For the executing agent (Haiku):** Follow these steps exactly. Make ONLY the
edits below. Do not refactor anything else. If any `old_string` does not match
the file exactly (line numbers may have drifted), STOP and re-read the file
around the quoted text, then adapt the match — keep the `new_string` intent
identical. **Before you conclude the task, call the `advisor` tool (Opus) to
review your diffs.** If the advisor flags a problem, fix it before finishing.

## Goal

Every short-form video piece chopped from a long-form source — and its
caption/title/description — must be COMPLETE ON ITS OWN. A viewer landing cold
on one short gets the full hook→payoff with zero outside context. Ban all
references to other parts of the source or sibling shorts.

Scope: **video shorts only** (4 files below). Do NOT touch
`prompts/repurposing_agent.md` or any text-derivative code.

## The shared clause (use this wording, adapt parenthetical per file)

> SELF-CONTAINED — COMPLETE ON ITS OWN: This short stands alone. A viewer seeing
> ONLY this clip, cold, must get the full hook→payoff with zero outside context.
> Ban every reference to other parts of the source or other shorts: no "as I
> mentioned", "earlier", "like I said", "part 2 / next / previous", "continued",
> "in this series", "watch the full video to understand", "stick around for". If
> a moment only makes sense after setup shown elsewhere, include that setup
> inside this short or pick a different moment.

---

## Edit 1 — `scripts/generate_scene_plans.py` (motion shorts)

In `SHORT_INSTRUCTIONS`, the "Rules for EACH short" block. Find:

```
- 6–12 scenes, played sequentially, self-contained (own hook + payoff).
```

Replace with:

```
- 6–12 scenes, played sequentially, self-contained (own hook + payoff).
- COMPLETE ON ITS OWN: this short must make full sense to a viewer who sees ONLY
  this short, cold, having watched nothing else. Its scenes must not depend on
  setup shown in another short or in an un-included part of the source script.
  Ban every reference to other parts/shorts: no "as I mentioned", "earlier",
  "like I said", "part 2 / next / previous", "continued", "in this series",
  "watch the full video". Each verbatim "script" excerpt and the short's angle
  must carry their own context.
```

---

## Edit 2 — `scripts/clip_shorts.py` (clip selection)

In `pick_clips_with_claude`, the prompt's "Each segment must" list. Find:

```
- Be self-contained (no "as I mentioned earlier", no missing setup)
```

Replace with:

```
- Be COMPLETE ON ITS OWN: a viewer seeing only this clip, cold, gets the full
  hook→payoff with zero outside context. Reject any segment whose hook or payoff
  depends on setup that lives outside the cut. Ban references to other parts of
  the video: no "as I mentioned", "earlier", "like I said", "part 2 / next /
  previous", "continued", "watch the full video". Prefer segments that already
  contain their own setup.
```

---

## Edit 3 — `scripts/lib/shorts_captions.py` (per-shot captions)

In `_build_prompt`, after the `Banned words:` line and before
`This is shot #{shot_index + 1}.`. Find:

```
Creator context: {voice}
Banned words: {BANNED_WORDS}

This is shot #{shot_index + 1}. The clip's hook / opening line:
```

Replace with:

```
Creator context: {voice}
Banned words: {BANNED_WORDS}

SELF-CONTAINED: This caption, title, and description must read standalone. The
viewer may never have seen the long-form or any sibling short. Never write "part
N", "continued", "in the previous short", or "watch the full video to
understand". Sell THIS clip as a complete piece. (A CTA pointing to the full
video for MORE is fine; requiring it to UNDERSTAND is not.)

This is shot #{shot_index + 1}. The clip's hook / opening line:
```

---

## Edit 4 — `scripts/generate_shorts_meta.py` (YouTube Shorts title/desc)

In `claude_metadata`, the prompt's `Rules:` block. Find:

```
- tags: 5-8 strings, mix broad + specific. No "#" prefix in tags array.
```

Replace with:

```
- tags: 5-8 strings, mix broad + specific. No "#" prefix in tags array.
- SELF-CONTAINED: title and description must stand alone. No part numbers, no
  "watch the previous short", no implying the long-form is required to
  understand this clip. (A CTA to the full video for MORE is fine.)
```

---

## Docs (per CLAUDE.md "UPDATE GUIDES ALWAYS")

Open `docs/video-production-guide.md` and any day guide that describes the shorts
generation step (search for "shorts" / "clip_shorts" / "scene plan"). Add one
line where shorts generation is described: "Shorts are generated self-contained —
each stands alone with no references to other clips or the source long-form."
Only edit guides that already cover the shorts step. Do not create new docs.

## Verification (run after edits)

1. `python3 scripts/generate_scene_plans.py --niche ds --week 2026-W25 --mode short --shorts 2 --force`
   → open a `remotion/public/scene-plans/2026-W25/*_s01.json`; confirm no scene
   `script`/`angle` references "earlier", "part", "as I mentioned".
2. `python3 scripts/clip_shorts.py --slug <a finished long-form slug> --count 2`
   → confirm chosen `hook_line`/`why` are self-contained segments.
3. Run captions end-to-end (via `clip_shorts.py`) → open the produced
   `shorts_captions.md`; confirm no "part N"/"continued"/"in this video".
4. `python3 scripts/generate_shorts_meta.py --slug <slug> --force`
   → open `content/derivatives/<slug>/youtube_shorts_metadata.json`; confirm each
   title/description stands alone.
5. Cold-viewer spot check: read one output per pipeline. Full sense with zero
   outside context? If yes → call `advisor` (Opus) for final review, then finish.

## Conclusion gate

Before declaring done: (a) all 4 code edits applied, (b) docs note added where
relevant, (c) at least one verification run inspected, (d) **`advisor` tool
called and any flagged issues resolved.**
