# Buffer Decision Guide

## Push current production to buffer?

```bash
python3 scripts/push_to_buffer.py --auto --dry-run   # preview
python3 scripts/push_to_buffer.py --auto              # auto-decide all niches
```

**Logic:** buffer < 4 weeks → content copied to next empty slot. Buffer full → stays as live content this week.

## File naming conventions

| Type | Pattern |
|------|---------|
| Blog | `content/blogs/YYYY-MM-DD_{niche}_{slug}.md` |
| YouTube script | `content/scripts/YYYY-MM-DD_{niche-dashes}-{slug}_yt.md` |
| Derivatives dir | `content/derivatives/YYYY-MM-DD_{niche}_{slug}/` |
| Video (edited) | `assets/video/edited/YYYY-MM-DD_{niche}_{slug}.mp4` |
| Shorts | `assets/video/edited/shorts/YYYY-MM-DD_{niche}_{slug}_short_NN.mp4` |
| Buffer | `content/buffer/week-N/{niche}/YYYY-MM-DD_{niche}_{slug}_*.md` |

Niche tokens: `data_science_tech` · `life_self_dev` · `poetry_quotes`
Script niche-dashes: `data-science-tech` · `life-self-dev` · `poetry-quotes`

See full table: [weekly-operating-guide.md § File Naming Conventions](weekly-operating-guide.md#file-naming-conventions)

## After consuming a week from buffer — rotate immediately

```bash
bash scripts/shift_buffer.sh
# Verifies week-4 exists before touching week-1
# Rotates: week-2→1, week-3→2, week-4→3
# Updates week numbers in data/buffer/topics.yaml
```

Then fill week-4 and regenerate:
```bash
# Edit data/buffer/topics.yaml — add week-4 topics (check Notion first for 90-day angles)
conda run -n content_engine_env python3 scripts/generate_buffer.py --week 4
```
