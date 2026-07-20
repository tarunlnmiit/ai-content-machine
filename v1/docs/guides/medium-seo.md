---
title: "Medium SEO — how stories rank on Google"
type: doc
slug: medium-seo
tags: [content/doc]
---
# Medium SEO — how stories rank on Google

*Added 2026-06-26. Source: official Medium video (https://www.youtube.com/watch?v=tClbPH94q44).*

Medium has strong domain authority, so stories surface on Google with little effort — but a
small per-story tweak helps them reach searchers, not just Medium readers.

## The rules

1. **Medium does the heavy lifting.** Google trusts the domain; stories rank even without
   optimization. The steps below are the extra nudge.
2. **Set a separate SEO title + SEO description.** In the Medium editor: ••• (More) →
   **SEO settings**. Defaults are your title + the first ~197 chars of the body — override both.
   These are distinct from the on-Medium title/subtitle.
3. **Two audiences.** Medium readers click on curiosity/expertise (the title + subtitle).
   Google searchers click on **intent** — "best / easiest / how to X". Write the SEO fields
   for the searcher; keep the title/subtitle reader-facing.
4. **Pick one target keyphrase** = the exact phrase the ideal reader Googles (2–5 words).
   Put it in the SEO title, the SEO description, **and the first paragraph** of the body.
5. **Research it.** Google the keyphrase, note the modifiers recurring in the top results
   (e.g. "healthy", "2026", "for beginners"), and fold the **truthful** ones into the SEO
   description. Never keyword-stuff.
6. **Paywall trade-off.** Google searchers are often non-members and will hit the paywall —
   decide whether to paywall a story you're aiming at search traffic.

Lengths: SEO title ≤ ~60 chars; SEO description ≤ ~160 chars (Medium's field caps ~197, but
Google truncates the preview around 155–160).

## How the pipeline implements this

Both generators produce the fields automatically:

- **Interview mode** (`prompts/article_writer.md`) emits `TARGET KEYPHRASE` / `SEO TITLE` /
  `SEO DESCRIPTION` output lines → parsed in `scripts/lib/interview.py` → written as comments.
- **Regular mode** (`prompts/writing_agent.md`) ends the article with the three comments directly.

Saved in the blog `.md` as trailing comments (alongside `<!-- Medium tags: … -->`):

```
<!-- Target keyphrase: data scientist portfolio 2026 -->
<!-- SEO title: Data Scientist Portfolio 2026: What Hiring Managers Want -->
<!-- SEO description: A data scientist portfolio in 2026 needs packaged code, not notebooks — here's what hiring managers look for. -->
```

`scripts/lib/seo.py` parses them (`extract_seo`) and renders the manual checklist
(`seo_manual_steps`). The checklist prints at the end of `produce_blog.py`,
`run_blog_pipeline.py`, and `publish_medium.py`.

## The one manual step (can't be automated)

Medium's public API accepts only title/content/tags/canonicalUrl/status — **not** SEO fields.
So after the draft exists:

1. Open the story → ••• → **SEO settings**.
2. Paste the **SEO title** and **SEO description** printed by the pipeline.
3. Confirm the keyphrase reads naturally in the first paragraph (the generator already weaves it in).
4. Re-upload any images (local `/content/...` paths don't render on Medium).
5. Decide on paywall per rule 6.
