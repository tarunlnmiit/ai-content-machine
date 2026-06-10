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

**Otherwise: rest.**
