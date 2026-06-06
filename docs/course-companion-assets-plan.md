# Plan — Build Companion Course Assets (moat deliverables)

## Context

All three course **lesson drafts + worksheets** are done (23 lessons, 23 sheets, committed
2026-06-05). The outlines promise **companion "moat" assets** that no competitor ships — but
only the prose worksheets exist so far. This task builds the buildable subset:

- **DS** 🔑 real dirty dataset + failure-mode answer key, and the two `.ipynb` notebooks
  (Data Audit Starter, Notebook→Module Refactor Kit) that pair with it.
- **Life** 📊 "your life as a dataset" tracker kit (reusable fill-in trackers).
- **Poetry** 📝 original prompt deck (one downloadable deck + new starter lines).

Out of scope (Tarun must record): the video moats — Inside-the-Work / teardown / write-along.

Decisions locked: dataset is **synthetic** (fabricated realistic mess, seeded); **build both
notebooks**. Outcome: the differentiators in `graphy_config.yaml` become real downloadable files.

## Binding constraint (do not break)

The L2 worksheet `content/courses/data_science/worksheets/2026-06-05_auditing-messy-real-world-data_worksheet.md`
ships **verbatim student code** that reads `loan_applications.csv` and runs numeric ops:
`(df["age"] < 0).sum()`, `(df["annual_income"] == 0).sum()`, `df["loan_amount"]/df["annual_income"]`.
Under pandas 3.0.3, `object < int` raises `TypeError`. Therefore the synthetic dataset MUST:
- be named exactly `loan_applications.csv`
- include columns `application_id, age, annual_income, loan_amount`
- keep `age`, `annual_income`, `loan_amount` **numeric** — the "wrong dtype" flaw goes on a
  separate column (`monthly_emi`, a number-stored-as-string).

## Dependencies

pandas 3.0.3 ✅ · numpy 2.4.4 ✅ · **nbformat ❌ → `pip install nbformat`** (one prereq).
No `requirements.txt` exists; note nbformat in the docs so the notebook step is reproducible.
jupyter/nbconvert absent → verify notebooks via `nbformat.validate`, not nbconvert.

## House style (new scripts inherit for free)

Run as `python3 scripts/<name>.py` from repo root. `from _console import console` and
`from lib.slug import slugify` resolve (script dir on `sys.path[0]`). `REPO =
Path(__file__).parent.parent`; output under `content/courses/<niche_dir>/...`;
`out_dir.mkdir(parents=True, exist_ok=True)`. Console: `console.rule("[info]…")`,
`[success]✓ Saved:[/success]`, `[warn]`/`[error]`. Reference: `scripts/generate_course_worksheet.py`.

## Build order

### 1. `scripts/generate_course_dataset.py` (new) → `content/courses/data_science/datasets/`
Seeded generator (`rng = np.random.default_rng(seed)`) producing `loan_applications.csv` +
`loan_applications_answer_key.md` (+ optional `loan_applications_clean.csv` with `--clean`).
- argparse mirrors existing generators: `--niche {ds,life,poetry}` (only ds wired), `--rows`
  (default 3000), `--seed` (default 42), `--name` (default `loan_applications`), `--clean`.
- **Single source-of-truth `Flaw` registry** drives BOTH injection and the answer key so they
  cannot drift: a frozen dataclass `Flaw(column, failure_mode, mechanism, worksheet_ref)`; each
  `inject_<mode>()` mutates the frame and records the real `n_affected`; `render_answer_key()`
  emits markdown from the same list.
- Schema → injected flaw (fintech loan domain, relatable to 18–25 Indian students):
  - `application_id` (object) → duplicate rows / dupe IDs (~1.5%)
  - `age`, `annual_income`, `loan_amount` (**numeric**) → impossible outliers (negatives, zeros,
    extremes) + some NaN — Task 3 code still runs
  - `monthly_emi` (**object/mixed**) → number-as-string (`"₹12,000"`, `"N/A"`, `""`) — the
    dtype-surprise flaw, kept OFF the Task-3 numeric columns
  - `cibil_score` (numeric) → non-random missingness (cluster nulls in self-employed rows)
  - `employment_type`, `loan_purpose` (object) → inconsistent categoricals + whitespace/encoding junk
  - `event_timestamp` (object) → **three-timezone-stitched** timestamps in mixed string formats
    (the lesson's signature flaw), no nulls — silently three realities
  - `applied_channel` (object) → plain missing values (lower %, so "top-3 by missing %" ranks)
  - do NOT add `loan_to_income` — the worksheet derives it.
- Answer key: provenance block (script · seed · rows · "SYNTHETIC, not real anonymised"),
  summary table, one section per flaw (column · mode · how injected · real rows-affected · what a
  correct audit finds · worksheet task), and an expected Data-Quality-Report mirroring Task 5.

### 2. `pip install nbformat` (prereq for step 3)

### 3. `scripts/build_course_notebooks.py` (new) → `content/courses/data_science/notebooks/`
Build via `nbformat.v4` (`new_notebook/new_markdown_cell/new_code_cell`); helper
`write_nb()` calls `nbformat.validate()` before writing so an invalid notebook never lands.
argparse: `--which {audit,refactor,both}` (default both), `--niche` (house signature).
- **`data_audit_starter.ipynb`** — loads `../datasets/loan_applications.csv` (document the
  notebooks/-as-cwd assumption in cell 1). Cells walk: shape/dtypes (Task 1), null-map (Task 2)
  with a TODO on non-random missingness, the dtype-trap TODO on `monthly_emi`, range/sanity
  (Task 3, verbatim — runs because numeric), duplicate TODO, timezone-trap cell, categorical
  `value_counts` + `clean_column()` TODO, closing pointer to the worksheet Task 5 + answer key.
- **`notebook_to_module_refactor_kit.ipynb`** — reuses the L8 worksheet's `clean_sales_data`
  scenario but **self-contained**: builds a tiny inline DataFrame so it runs with no external
  file. BEFORE (messy cell) → AFTER (`def clean_sales_data(...) -> pd.DataFrame` with docstring +
  type hints) → inline assert-based test (no pytest) → git-ready `src/` tree + import + 3 git
  commands → "do this now."

### 4. Life tracker kit (hand-authored static files) → `content/courses/life_self_dev/templates/` (new dir)
Fixed artifacts, so no generator (YAGNI). Four Sheets-importable CSV templates (header row +
a couple of example/blank rows) + one markdown guide:
- `energy_audit_tracker.csv` (L1) · `keystone_habit_designer.csv` (L2) ·
  `weekly_review_template.csv` (L5) · `deep_block_planner.csv` (L6)
- `systems_kit_guide.md` — how to import to Google Sheets/Notion and use each tracker, tying
  each to its lesson. Keep masters in repo; Tarun links the live Sheet in Graphy.

### 5. Poetry prompt deck → `content/courses/poetry/prompts/`
- **Reuse the existing generator** for new creative content (no new prose code):
  `python3 scripts/generate_course_worksheet.py --niche poetry --topic "Starter lines deck —
  opening lines to beat the blank page" --objective "give a writer 40+ original starter lines
  to pull from whenever the page is blank"` → new starter-lines sheet in `prompts/`.
- **`scripts/compile_prompt_deck.py`** (new, small) — reads all `prompts/2026-06-05_*.md` + the
  starter-lines sheet, assembles one `prompts/prompt_deck.md` with a title page, TOC, and each
  prompt sheet as a section. Reproducible; re-run after adding sheets.

### 6. Docs sync (CLAUDE.md mandate — never leave guides stale)
- `content/courses/data_science/outline.md`, `life_self_dev/outline.md`, `poetry/outline.md`:
  update the "Companion material — production notes" tables to point at the real new paths
  (`datasets/`, `notebooks/`, `templates/`, `prompt_deck.md`).
- `docs/course-production-guide.md`: add a short "Building companion assets" section with the
  three new commands + the `pip install nbformat` prereq.
- `data/courses/graphy_config.yaml`: note the produced asset files under each course's
  differentiators (paths now exist).

### 7. Verify, then commit granularly (one logical commit per asset group)

## Verification

1. `python3 scripts/generate_course_dataset.py --niche ds` → CSV + answer key appear.
2. Regression guard (the dtype constraint):
   `python3 -c "import pandas as pd; df=pd.read_csv('content/courses/data_science/datasets/loan_applications.csv'); print(df.shape); (df['age']<0).sum(); (df['annual_income']==0).sum(); (df['loan_amount']/df['annual_income'])"`
   — must run with no `TypeError`; confirm `monthly_emi` is object, the three amount cols numeric.
3. Determinism: run the generator twice with `--seed 42`; CSVs byte-identical (`md5`).
4. `pip install nbformat && python3 scripts/build_course_notebooks.py --niche ds`.
5. Validate notebooks:
   `python3 -c "import nbformat; [nbformat.validate(nbformat.read(p,as_version=4)) for p in ['content/courses/data_science/notebooks/data_audit_starter.ipynb','content/courses/data_science/notebooks/notebook_to_module_refactor_kit.ipynb']]; print('valid')"`
6. Exec the non-TODO code cells of each notebook (audit run from `notebooks/` so `../datasets/…`
   resolves; refactor is self-contained) — no exceptions.
7. Life: open each CSV in a sheet / `python3 -c "import csv,glob;[list(csv.reader(open(f))) for f in glob.glob('content/courses/life_self_dev/templates/*.csv')]"` — parse clean.
8. Poetry: `python3 scripts/compile_prompt_deck.py` → `prompt_deck.md` exists, contains all
   sheets + starter lines; spot-read for voice + no banned words.

## Risks

- **Dtype crash (highest)** — pinned numeric amount cols + Verification step 2 regression guard.
- **nbformat not installed** — explicit prereq step; documented.
- **Synthetic ≠ real** — answer key states it's fabricated; flaws still mirror the lesson, so
  pedagogy holds.
- **Answer-key/data drift** — eliminated by the single `Flaw` registry under a fixed seed.
