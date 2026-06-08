# Repo Split Plan: content-machine → content-machine + course-machine

**Status:** Planned — not yet executed  
**Decision date:** 2026-06-07  
**Execute when:** Content pipeline stable, week 1 published

---

## Context

Current repo `ai-content-machine` (GitHub: `tarunlnmiit/ai-content-machine`) mixes two distinct workstreams:

- **Content pipeline** — daily/weekly social content: blogs, derivatives, buffer, scheduler, analytics, asset rendering (31 GB `assets/`), Notion/Substack/YouTube/Twitter publishing. The vast majority of scripts (~70) and all of `assets/`.
- **Course production** — three weekend mini-courses (Data Science, Life, Poetry): curricula, worksheets, lesson scripts, notebooks, prompt decks, tracker templates. ~1.7 MB content + 7 course-scoped scripts + 6 docs.

These have **separate cadences** (daily content vs weekend course drops), **separate output channels** (social platforms vs course landing pages), and **separate iteration loops**. Keeping them in one repo means course-only changes pollute content commit history (and vice versa), and the 31 GB `assets/` tree is dead weight for anyone cloning to work on courses.

**Decisions (locked):**
- Keep current repo, rename to `content-machine`. It stays the content workstream.
- New repo `course-machine` for course workstream. Self-contained — no shared code, copy `_console.py` if needed.
- `assets/` (31 GB) stays in content repo.
- Fork-out approach, no history rewrite. Course commits stay visible in content-machine git log (acceptable — small fraction, clearly scoped).

---

## Target Layout

### `course-machine/` (new repo)

```
course-machine/
├── CLAUDE.md                          # course-focused (extract from current)
├── README.md
├── .env.example
├── .gitignore
├── requirements.txt                   # pandas, numpy, nbformat, pyyaml, rich
├── content/
│   └── courses/
│       ├── data_science/
│       ├── life_self_dev/
│       └── poetry/
├── data/
│   └── courses/
│       └── graphy_config.yaml
├── docs/
│   ├── course-companion-assets-plan.md
│   ├── course-production-guide.md
│   ├── course-setup-end-to-end.md
│   ├── course-weekend-ds.md
│   ├── course-weekend-life.md
│   └── course-weekend-poetry.md
└── scripts/
    ├── _console.py
    ├── build_course_notebooks.py
    ├── compile_prompt_deck.py
    ├── draft_lesson_script.py
    ├── generate_canva_worksheet_prompt.py
    ├── generate_course_dataset.py
    ├── generate_course_worksheet.py
    └── generate_worksheet_outline.py
```

### `content-machine/` (rename of `ai-content-machine`)

Everything else stays. After split, delete from content-machine:
- `content/courses/`
- `data/courses/`
- `docs/course-*.md` (6 files)
- 7 course scripts listed above

`_console.py` stays in content-machine (used by other scripts).

---

## Execution Steps

### Step 1 — Create `course-machine` repo (local + GitHub)

```bash
mkdir -p ~/Making\ It\ Big/Claude/course-machine
cd ~/Making\ It\ Big/Claude/course-machine
git init -b main
gh repo create tarunlnmiit/course-machine --private --source=. --remote=origin
```

### Step 2 — Copy course files into new repo

```bash
SRC=~/Making\ It\ Big/Claude/content-machine
DST=~/Making\ It\ Big/Claude/course-machine

cp -R "$SRC/content/courses"       "$DST/content/courses"
cp -R "$SRC/data/courses"          "$DST/data/courses"
mkdir -p "$DST/docs" "$DST/scripts"
cp "$SRC/docs/"course-*.md         "$DST/docs/"
for f in build_course_notebooks compile_prompt_deck draft_lesson_script \
         generate_canva_worksheet_prompt generate_course_dataset \
         generate_course_worksheet generate_worksheet_outline _console; do
  cp "$SRC/scripts/$f.py" "$DST/scripts/"
done
```

### Step 3 — Author new top-level files in `course-machine`

- `CLAUDE.md` — extract course-relevant sections from content-machine CLAUDE.md. Drop content-pipeline rules (Notion Contents DB, social platforms, buffer).
- `README.md` — what it is, how to run each script, link to `docs/course-setup-end-to-end.md`.
- `.env.example` — only `ANTHROPIC_API_KEY_FREE` (verify by grepping each script's env reads).
- `.gitignore` — Python (`__pycache__`, `.env`, `*.pyc`), notebook checkpoints, OS junk.
- `requirements.txt` — `pandas`, `numpy`, `nbformat`, `pyyaml`, `rich` + any other imports found in the 7 scripts.

### Step 4 — Verify course-machine works standalone

```bash
cd ~/Making\ It\ Big/Claude/course-machine
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_course_dataset.py --help
python scripts/build_course_notebooks.py --help
# Run one real generation and diff against content-machine copy
```

If any script imports from a path outside `scripts/`, copy that file in and re-run.

### Step 5 — Initial commit + push `course-machine`

```bash
cd ~/Making\ It\ Big/Claude/course-machine
git add -A
git commit -m "feat: initial fork from content-machine (courses workstream)"
git push -u origin main
```

### Step 6 — Delete course files from `content-machine`

```bash
cd ~/Making\ It\ Big/Claude/content-machine
git rm -r content/courses data/courses
git rm docs/course-*.md
git rm scripts/build_course_notebooks.py scripts/compile_prompt_deck.py \
       scripts/draft_lesson_script.py scripts/generate_canva_worksheet_prompt.py \
       scripts/generate_course_dataset.py scripts/generate_course_worksheet.py \
       scripts/generate_worksheet_outline.py
git commit -m "refactor: extract courses into course-machine repo"
git push
```

### Step 7 — Update `content-machine` docs

Per "UPDATE GUIDES ALWAYS" rule:
- `CLAUDE.md` — remove course-specific sections and course folder from Folder Map
- `docs/README.md` — remove links to `course-*.md`
- `docs/weekly-operating-guide.md`, `saturday.md`, `sunday-batch.md`, `friday.md` — strip course-weekend steps; add pointer to course-machine repo URL
- `docs/video-production-guide.md` — strip course refs if present
- Verify: `grep -rn "course" docs/ CLAUDE.md` — triage each hit

### Step 8 — Rename `ai-content-machine` → `content-machine` on GitHub

```bash
gh repo rename content-machine -R tarunlnmiit/ai-content-machine
git remote set-url origin git@github.com:tarunlnmiit/content-machine.git
```

GitHub auto-redirects old URL.

### Step 9 — Regenerate graphify for both repos

```bash
cd ~/Making\ It\ Big/Claude/content-machine && graphify update .
cd ~/Making\ It\ Big/Claude/course-machine  && graphify init .
```

---

## Verification Checklist

1. **course-machine self-contained:** fresh clone → `pip install -r requirements.txt` → `--help` on all 7 scripts → one real generation matches content-machine output
2. **content-machine still works:** run a non-course script (`generate_buffer.py`, `scheduler.py --dry-run`) → no import errors
3. **No dangling course refs in content-machine:** `grep -rn "content/courses\|data/courses\|course-weekend\|course-production-guide" docs/ CLAUDE.md` → 0 hits (or intentional pointers only)
4. **GitHub:** both repos exist, both have green initial commits, old URL redirects
5. **graphify:** both repos have fresh `graphify-out/GRAPH_REPORT.md`
