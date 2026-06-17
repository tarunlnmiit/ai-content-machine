# Saturday — Rest Day

Saturday is your rest day. No scheduled content work.

Everything that needed doing this week was handled by Thursday (render + upload + Notion sync) and Friday (social scheduling + buffer check).

---

## If something slipped

If a step from Thursday or Friday was missed, handle it now — otherwise close the laptop.

**Missed upload:**
```bash
python3 scripts/list_week_content.py {week}
# Check for any ✗ next to video/blog items
```

**Notion status not updated:**
```bash
python3 scripts/update_notion_status.py \
  --title "{title}" --status Uploaded \
  --url "https://youtube.com/watch?v=..."
```

**Buffer below 4 weeks:**
```bash
for niche in data_science_tech life_self_dev poetry_quotes; do
  count=$(ls content/buffer/week-*/${niche}/*_meta.md 2>/dev/null | wc -l | tr -d ' ')
  echo "$niche: ${count}/4"
done
# If any < 4, run generate_buffer.py (see friday.md Step 6)
```

---

## Evergreen teasers (optional, ~10 min)

Free time? Mine your back catalogue. Turn an already-published YouTube video or Medium blog into
short teasers + a backlink, then post them by hand. No render, no scheduler.

```bash
# Preview first (no files written)
python3 scripts/teaser_from_published.py --url <youtube-or-medium-url> --dry-run

# Write teaser files for one piece (niche auto-detected; --niche to force)
python3 scripts/teaser_from_published.py --url <url> --niche ds

# Batch a backlog list — one URL per line: `url[, niche][, project]`  ('#' comments ok)
python3 scripts/teaser_from_published.py --urls urls.txt
```

Output → `content/derivatives/{week}/{slug}/`: `*_teaser.txt` per platform + `teasers.md`
(all-in-one bundle to copy from). Each post ends with a UTM backlink to the original.

**Already have derivatives for a piece?** Just append the backlink instead (idempotent):
```bash
python3 scripts/teaser_from_published.py --inject-link content/derivatives/{week}/{slug} --url <url>
```

Then paste into each platform manually. Full reference: `docs/medium-repurposing-guide.md`.

---

**Otherwise: rest.**
