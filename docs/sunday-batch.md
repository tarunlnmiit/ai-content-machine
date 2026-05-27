# Sunday Batch — Optional One-Sitting Playbook

Use this **only when free Sunday available**. If busy, skip — daily guides (mon.md…sat.md) still work. No guilt.

Goal: produce full week's content in **one 3–4 hour sitting**, then forget about content Mon–Sat.

---

## Pre-Flight (Saturday night, 5 min)

Do this *only if* you plan to batch Sunday. Otherwise skip.

- [ ] Phone on charger. Laptop charged.
- [ ] Clean shirt + camera spot ready (lighting check).
- [ ] Run overnight idea fetch — already automated via launchd 6am.
- [ ] (Optional) Trigger ghostwriter pre-drafts:
  ```bash
  python3 scripts/ghostwrite.py --topics 3 --output content/blogs/drafts/
  ```
- [ ] Sleep early.

---

## Sunday Batch — The 4 Hour Sit

### Hour 1 — Pick + Write (60 min)

1. Coffee. Open Notion Contents DB.
2. Filter Status='Idea'. Pick **exactly 3** topics (1 DS + 1 Life + 1 Poetry).
   - Rule: first instinct wins. No deliberation > 90 seconds per pick.
3. Mark all 3 Status='Started' in Notion.
4. Open Claude. Run for each:
   ```bash
   python3 scripts/produce_blog.py --slug <slug> --niche <niche>
   ```
5. Read each draft. Fix voice (banned words check, add personal example). 15 min per blog max.

**Output:** 3 blog drafts in `content/blogs/`.

### Hour 2 — Record All 3 Videos (60 min)

Same lighting, same shirt, same energy. Don't break setup between niches.

1. **DS video** (20 min) — screen record + talking head. Use blog as script outline.
2. **Life video** (20 min) — talking head only. Personal story format.
3. **Poetry video** (20 min) — read poem twice (one calm, one expressive). Robot handle rest.

**Tips:**
- Mess up? Keep rolling. `auto_edit.py` strip silences.
- One take per video. Don't re-record. Trust pipeline.
- Save raw to `assets/video/raw/<slug>.mp4`.

### Hour 3 — Robot Does Editing (you walk away)

Run all 3 in parallel terminals or sequential:

```bash
python3 scripts/auto_edit.py --slug ds-<slug>
python3 scripts/auto_edit.py --slug life-<slug>
python3 scripts/auto_edit.py --slug poetry-<slug>
```

Then shorts:
```bash
python3 scripts/clip_shorts.py --slug ds-<slug>
python3 scripts/clip_shorts.py --slug life-<slug>
python3 scripts/clip_shorts.py --slug poetry-<slug>
```

**While robot work:** eat lunch. Walk. Don't watch progress bar.

Runtime: ~15-30 min total on M-series.

### Hour 4 — Schedule + Repurpose (60 min)

1. Review each edited video — 2 min scrub. If watchable, ship. No perfection.
2. Generate thumbnails:
   ```bash
   python3 scripts/generate_design.py --slug <slug> --type thumbnail
   ```
3. Repurpose blogs to Medium + Substack + LinkedIn:
   ```bash
   python3 scripts/repurpose_blog.py --slug <slug>
   ```
4. Drop everything into `output/scheduled/` with publish dates spread Mon–Sat:
   - Mon: DS blog + video
   - Tue: Life blog
   - Wed: Poetry video
   - Thu: DS short
   - Fri: Life video + short
   - Sat: Poetry blog (or skip if sabbath)
5. Update Notion Status='Ready to publish' for each.
6. Scheduler daemon publish automatically. You done.

---

## Mon–Sat When Batch Done

- **No content work.** Pipeline auto-publish.
- **10 min/day:** reply comments. Single time slot. Not all day.
- **Saturday:** sabbath. Phone away from content apps.
- **Analytics:** weekly digest Sunday morning (no daily checking).

---

## Partial Batch (Got 2 Hours, Not 4)

Pick **one niche only**. Ship 1 video + 1 blog. Better than zero.

Priority order:
1. **DS** (highest CPM, biggest audience) — ship if anything
2. **Life** (emotional reach, easy record)
3. **Poetry** (lowest production cost — can skip-and-stockpile next batch)

---

## When To Skip Batch Entirely

- Tired. Sick. Family stuff. Travel.
- Last batch already filled `output/scheduled/` for next week.
- Inspiration low — bad batch = bad content. Rest instead.

Pipeline have buffer. One missed Sunday = scheduler post backlog. Real risk only if **3 Sundays missed in row**.

---

## Honest Rules

1. **Done > perfect.** Watchable beats unreleased.
2. **First instinct wins.** Deliberation kill batch.
3. **No re-record.** Robot fix mess.
4. **Stop at 4 hours.** Hard cap. Quality drop after.
5. **Sabbath sacred.** Saturday off no matter what.

---

## Quick Command Reference

```bash
# Full batch (run sequentially Sunday)
python3 scripts/sync_ideas_to_notion.py        # pull fresh ideas
python3 scripts/produce_blog.py --slug <s>     # x3 niches
python3 scripts/auto_edit.py --slug <s>        # x3 niches
python3 scripts/clip_shorts.py --slug <s>      # x3 niches
python3 scripts/generate_design.py --slug <s>  # thumbnails
python3 scripts/repurpose_blog.py --slug <s>   # cross-platform
```

Scheduler daemon handle publishing — already running via launchd.
