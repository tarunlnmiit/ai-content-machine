# Tuesday — Life Blog + Repurpose DS (~35 min)

## Step 0 — Check buffer first (1 min)

```bash
ls content/buffer/week-1/life_self_dev/*_meta.md 2>/dev/null
```

**Buffer has content?** → Skip Steps 1–3. Use buffer files directly:
- Blog: `content/buffer/week-1/life_self_dev/*_substack_post.md`
- Social: `content/buffer/week-1/life_self_dev/*_social_copy.md`

Jump straight to Step 4 (Repurpose DS). After consuming: log in Notion as `Script`.

**No buffer?** → Proceed with Steps 1–3 below. Alert: buffer should never be empty — check Sunday Step 7.

---

## Step 1 — Produce Life blog

Option A — topic only:
```bash
python3 scripts/produce_blog.py --topic 'YOUR LIFE TOPIC' --niche life --humanize
```

Optional listicle mode (Top-N format, e.g. "Top 3 habits that backfire"):
```bash
python3 scripts/produce_blog.py --topic 'YOUR LIFE TOPIC' --niche life --listicle 3 --humanize
```
- `--listicle N` (N ≥ 2) — forces Top-N structure with N numbered H2 item sections. Skip for default narrative.

Option B — have notes/transcript:
```bash
python3 scripts/ghostwrite.py --source notes.txt --niche life --voice conversational
```

## Step 2 — Fill personal sections
```bash
grep -rn 'PERSONAL_INSERT' content/blogs/
```

## Step 3 — Add images to Life blog
```bash
python3 scripts/fetch_images.py --input content/blogs/[tuesday_life_blog].md --dry-run
python3 scripts/fetch_images.py --input content/blogs/[tuesday_life_blog].md
```

## Step 4 — Repurpose Monday's DS blog (with design prompts)
```bash
python3 scripts/repurpose_blog.py --input content/blogs/[monday_ds_blog].md --design
# Saves 10 files to content/derivatives/{slug}/
# Includes claude_design_brief.json
# Calls generate_design_prompts.py automatically
# → output/scheduled/claude_design_prompts_{slug}.md (4 sections)
# For DS tutorial blogs: extracts + validates code blocks before generating slide deck prompt
```

## Step 5 — DS thumbnail brief
```bash
python3 scripts/thumbnail_brief.py --input content/blogs/[monday_ds_blog].md
# → content/derivatives/{slug}/thumbnail_brief.json
```

---

## After production — buffer or keep live?

```bash
python3 scripts/push_to_buffer.py --auto --dry-run   # preview
python3 scripts/push_to_buffer.py --auto              # run
```
→ Decision logic + file naming: [_buffer_decision.md](_buffer_decision.md)

