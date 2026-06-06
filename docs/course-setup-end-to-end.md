# Course Setup — End to End (Zero → Launched)

The single front-door for taking one course from nothing to live and selling. It owns
two things no other doc does: the **linear stage spine** (do these in order) and the
**AI-vs-manual map** (what a script does for you vs. what only you can do). Everything
deeper — exact script flags, recording rig, editing pipeline — lives in the docs linked
per stage. Don't expect this doc to re-teach those; follow the links.

> **Building over weekends?** Use the hour-blocked per-niche checklists instead, they
> sequence the same stages into Saturday/Sunday blocks:
> `docs/course-weekend-ds.md` · `docs/course-weekend-life.md` · `docs/course-weekend-poetry.md`.
> This guide is the *reference* behind them.

---

## The 9 stages

```
0 Platform   →  decided (Graphy). Read once, don't re-litigate.
1 Scope      →  YOU lock curriculum (9/7/6 lessons per niche)
2 Draft      →  AI  draft_lesson_script.py  →  spoken script + [PERSONAL_*] markers
3 Personalise→  YOU fill every [PERSONAL_*] with real detail
4 Assets     →  AI  worksheet / dataset / notebook generators
5 Record     →  YOU on camera (one-take, done > perfect)
6 Edit       →  SEMI  trim + Remotion + minimal overlays
7 Upload     →  YOU build Graphy shell, gate L1 free, ₹1 test
8 Launch     →  YOU pre-sell → validate → full launch → backups
```

Pre-sell gate sits between 7 and 8: **record only Lessons 1–2, sell at 50% off, record
the rest only if 20+ buy.** Don't build all 9 lessons before a single sale.

---

## AI vs Manual — the master map

The crown of this guide. Left column runs without you once you give inputs. Right column
is irreducibly yours — your voice, face, judgement, money rails.

| Stage | AI / scripted (it does it) | Manual (only you) |
|-------|----------------------------|-------------------|
| **Scope** | — | Lock lesson titles + key points in `content/courses/<niche>/curriculum.md` |
| **Draft script** | `draft_lesson_script.py` → 10–15 min spoken script, cold-open→teach→story→close, marks `[PERSONAL_*]` | Feed it the title + ~3 points + 1 story prompt |
| **Personalise** | — | Replace every `[PERSONAL_INSERT]` / `[PERSONAL_STORY]` with your real numbers, names, failures |
| **Worksheet** | `generate_course_worksheet.py` → original exercise (code / journaling / writing prompt by niche) | Review for fit + originality |
| **Dirty dataset** (ds) | `generate_course_dataset.py` → seeded CSVs + failure-mode answer keys | — (fully automated, already built for ds) |
| **Notebook** (ds) | `build_course_notebooks.py` → validated `.ipynb` companions | — (already built for ds) |
| **Record** | — | You on camera reading your script. Indian English fine. One retake max |
| **Edit** | `prepare_remotion_edit.py` + Remotion render + `hyperframes_render.py --intensity minimal` | Trim fumbles; judge where overlays help |
| **Graphy shell** | — | Create course, price, cover, connect UPI, **₹1 test transaction**, gate L1 free |
| **Certificate** | — | Canva template + logo, enable on completion |
| **Launch** | — | Pre-sell post, full announce, WhatsApp group, price-raise after 50 |
| **Config fill-back** | — | Paste `graphy_course_id` + `enrol_url` into `graphy_config.yaml` |

**One-line rule:** AI drafts the *structure and the practice material*; you supply the
*soul (personal detail) and the proof (your face + real money rails)*. Never ship an
unpersonalised script — the `[PERSONAL_*]` markers are non-negotiable manual work.

---

## Stage 0 — Platform (already decided: Graphy)

The whole project assumes **Graphy** — primary host, **Instamojo** as backup
(`data/courses/graphy_config.yaml`). You don't need to re-decide; here's the *why* so it's
defensible.

| Need | Graphy | YouTube (free/membership) | Why it matters |
|------|--------|---------------------------|----------------|
| One-time ₹ via UPI | ✅ native | ❌ (membership = recurring only) | Indian students pay UPI, not cards |
| Gate worksheets/datasets | ✅ | ❌ | The companion assets *are* the moat |
| Certificate on completion | ✅ | ❌ | Students want the credential |
| **You own student emails** | ✅ export monthly | ❌ YouTube keeps them | Own the audience or rent it |
| Platform cut | ~none | ~30% | Keeps the ₹299 yours |

YouTube is the **funnel** (free teasers + free Lesson 1 → Graphy), not the host. YouTube
Membership is a *separate recurring* product (members-only "Inside the Work" sessions),
added later once the channel hits 1k subs + 4k watch-hours. YouTube paid "Courses" is
US-first and winding down — treat as unavailable in India.

Full distribution-model breakdown: `docs/course-production-guide.md` → "Distribution channels".

---

## Stage 1 — Scope (manual)

Open `content/courses/<niche>/curriculum.md`. Confirm or rewrite the lesson titles + key
points. **You own this list** — the AI drafts *from* it, never invents it. Lesson counts:
DS 9, Life 7, Poetry 6.

---

## Stage 2 — Draft with AI

One command per lesson. Pull the `--title` / `--point` / `--story` text straight from the
curriculum row:

```bash
python3 scripts/draft_lesson_script.py \
  --niche ds \
  --title "How practitioners actually frame problems" \
  --point "Business ask is not the modelling question" \
  --point "Define the target before the model" \
  --point "Frame for the decision, not the metric" \
  --story "The project where the real question was budget, not accuracy"
# → content/courses/<niche>/lesson_scripts/YYYY-MM-DD_<slug>.md
```

Drafts with Sonnet 4.6, loads `data/kb/master_brief.md` + `prompts/writing_agent.md` so it
carries your voice and respects the banned-words list. Repeat `--point` ~3×.

---

## Stage 3 — Personalise (manual, mandatory)

```bash
grep -n 'PERSONAL' content/courses/<niche>/lesson_scripts/<file>.md
```

Replace every marker with real detail — the project you actually shipped, the number you
actually saw, the mistake you actually made. This is what makes it un-fakeable. Skipping
this = shipping a generic AI script.

---

## Stage 4 — Companion assets (AI / scripted)

Each lesson ships practice material. Generators do the work:

```bash
# Worksheet (all niches) — original, ingests no published content
python3 scripts/generate_course_worksheet.py --niche ds \
  --topic "Framing a problem before touching a model" \
  --objective "translate a vague business ask into a testable target variable"

# DS dirty datasets + failure-mode answer keys (conda env — already built, regenerate if needed)
conda run -n content_engine_env python scripts/generate_course_dataset.py --niche ds --all

# DS companion notebooks (needs nbformat — already built)
conda run -n content_engine_env python scripts/build_course_notebooks.py --niche ds --which both
```

DS assets are already built and committed — the dataset/notebook commands are for
regeneration, not first build. Life/Poetry use worksheets only (templates + prompt deck
are separate phases). Student prereqs for DS: `pip install scikit-learn` (baselines + L7),
`pip install nbformat` (notebooks). Detail: `docs/course-production-guide.md` → "The two scripts".

---

## Stage 5 — Record (manual)

You on camera. **Pre-sell discipline: record only Lessons 1–2 first.** Targets: DS 10–15
min, Life 8–12, Poetry 6–10. DS = screen-share body + talking-head intro/outro; Life/Poetry
= talking head, look at camera.

Physical rig + teleprompter + per-take mechanics: **`docs/recording-guide.md`** (iPhone on
tripod, Lark mic, clap at `[PAUSE]`, keep talking through `[BROLL:]`). Save masters to
`assets/raw/` **and** Google Drive — never one copy.

---

## Stage 6 — Edit (semi-automated)

Same muscle as your YouTube videos: record one take, trim, let pre-lined b-roll drop in,
light overlay pass. **Don't hand-edit.**

```bash
# Talking-head (Life/Poetry, or DS intro/outro): trim + b-roll + captions → Remotion plan
python3 scripts/prepare_remotion_edit.py --raw "assets/raw/<lesson>.MOV" \
  --script "<lesson-script>.md" --niche life --slug <slug>
cd remotion && npx remotion render CourseLesson ../assets/video/edited/<slug>.mp4 \
  --props="{\"editPlanFile\":\"edit-plans/<slug>.json\"}" && cd ..
# Optional restrained overlays — courses want a calm human editor, not an effects reel
python3 scripts/hyperframes_render.py assets/video/edited/<slug>.mp4 --slug <slug> --intensity minimal
```

**Always `--intensity minimal`** for courses (≈ one overlay/minute). DS screen-share body:
just trim, optional minimal overlays. Full editing notes: `docs/course-production-guide.md` → "Editing".

---

## Stage 7 — Upload to Graphy (manual — the "how to upload it")

Do this once Lessons 1–2 are edited. This is the authoritative upload sequence.

1. **Create the course shell.** Title, description, cover image, price — pull all from
   `data/courses/graphy_config.yaml` (DS ₹299 / Life ₹149 / Poetry ₹99, first 50 seats).
2. **Connect payments.** Razorpay / direct UPI. **Test a ₹1 transaction before launch** —
   non-negotiable; a broken checkout kills launch day silently.
3. **Upload lessons.** Set **Lesson 1 = free preview** with email capture — that's your
   lead magnet and the funnel from YouTube.
4. **Certificate.** Canva template + your logo + course/student name merge fields; enable
   "issue on completion."
5. **Community.** Add the WhatsApp/Telegram group link; students join on first sale.
6. **Cross-link.** Put the course URL in the matching YouTube channel "About" + video
   descriptions (@breathofdatascience / @breathoflife_ / @breathofpoetry).
7. **Fill back the config.** Paste `graphy_course_id` + `enrol_url` into
   `data/courses/graphy_config.yaml`. This closes the loop — the repo now knows the live URL.

---

## Stage 8 — Launch + maintain (manual)

**Pre-sell (after Stage 7, lessons 1–2 only).** Announce to the funnel channel + Twitter +
Substack: *"Course drops in 2 weeks. First 30 get 50% off. Lesson 1 free."* Pin the link.
**Gate: 20+ pre-sales → record the rest. 0 → rethink positioning, don't record more.**

**Full launch** once all lessons are up: announce price auto-raises after first 50 seats,
post the YouTube video + community + Twitter + Substack.

**Maintain (don't skip):**
- Keep video masters on Google Drive / own storage — **never Graphy-only**.
- Export the student email list from Graphy **monthly** — own your audience.
- Raise price after 100+ students/reviews (launch → `price_later_inr` in config).
- Refund policy: 7-day refund if ≤ 2 lessons watched.

**Launch order (staggered, not simultaneous):** DS ₹299 → Life ₹149 → Poetry ₹99 →
Bundle ₹449. All can be live at once; announce one at a time.

---

## Where each thing is owned (so docs don't drift)

| Topic | Authoritative doc |
|-------|-------------------|
| Stage spine + AI/manual map + upload walkthrough | **this doc** |
| Script flags, distribution model, editing detail | `docs/course-production-guide.md` |
| Hour-blocked weekend schedule | `docs/course-weekend-<niche>.md` |
| Recording rig + per-take mechanics | `docs/recording-guide.md` |
| Pricing, IDs, enrol URLs, distribution config | `data/courses/graphy_config.yaml` |
| Per-lesson video + companion + repurpose layers | `content/courses/<niche>/outline.md` |
