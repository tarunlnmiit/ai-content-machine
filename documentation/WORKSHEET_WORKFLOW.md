# Worksheet Workflow — IG Lead Magnet + Email Collection

Generate actionable PDF worksheets from blogs. Convert readers into email subscribers via a single self-hosted, email-gated download link (Vercel + Kit/ConvertKit) — no per-blog landing page.

## Quick Start (Existing Blogs)

### For This Week's 3 Blogs

**Data Science (ML-to-SQL):**
```bash
python3 scripts/generate_worksheet_outline.py \
  -i content/blogs/2026-05-12_data_science_tech_ml-model-sql-translation.md

python3 scripts/generate_canva_worksheet_prompt.py \
  -i content/worksheets/2026-05-12_data_science_tech_ml-model-sql-translation_worksheet.json
```

**Life & Self-Dev (Check-in Design):**
```bash
python3 scripts/generate_worksheet_outline.py \
  -i content/blogs/2026-05-13_life_self_dev_why-do-most-daily-check-in-habits-fall-apart-after-a-few-day.md

python3 scripts/generate_canva_worksheet_prompt.py \
  -i content/worksheets/2026-05-13_life_self_dev_why-do-most-daily-check-in-habits-fall-apart-after-a-few-day_worksheet.json
```

**Poetry (Ada Limón):**
— Skips automatically (reflection format, no worksheet)

---

## Full Workflow (Per Blog)

### Step 1: Generate Worksheet Outline
```bash
python3 scripts/generate_worksheet_outline.py -i content/blogs/[BLOG_SLUG].md
```

Outputs:
- `content/worksheets/[BLOG_SLUG]_worksheet.json` — worksheet structure
- Console: JSON preview

**What it checks:**
- Niche detection (data_science, life_self_dev, poetry_quotes)
- Engagement potential (high = suitable for worksheet)
- Auto-skips low-engagement blogs (e.g., poetry commentary)

---

### Step 2: Generate Canva Prompt
```bash
python3 scripts/generate_canva_worksheet_prompt.py \
  -i content/worksheets/[BLOG_SLUG]_worksheet.json
```

Outputs:
- Console: Canva design prompt (ready to copy-paste)

**How to use:**
1. Copy entire prompt
2. Go to [Canva.com](https://www.canva.com)
3. New Design → Custom Size → A4 (or custom)
4. Paste prompt into **Canva AI Design** (or manually design following the structure)
5. Export as **PDF**
6. Save to `output/worksheets/[BLOG_SLUG]_worksheet.pdf`

---

### Step 3: Commit the PDF — that's the whole "setup"

No per-blog ConvertKit landing page anymore. Drop the PDF in `output/worksheets/{week}/` (the generator already names it `{date}_{niche}_{slug}[_worksheet].pdf`), commit, push. Vercel redeploys, regenerates the manifest, and the link goes live:

```
https://worksheets-thebreathnetwork.vercel.app/get-worksheet?slug=<slug>
```

The `<slug>` is the human part of the filename (date + niche prefix stripped, `_worksheet` suffix dropped). No config edit, no landing page, no upload.

---

### Step 4: Get the shareable link

```bash
node scripts/build-worksheets-manifest.mjs      # refresh slug → PDF map
python3 scripts/worksheet_links.py --week 2026-W21   # print links for a week
python3 scripts/worksheet_links.py              # all worksheets
```

`worksheet_links.py` prints three ready-to-paste forms per worksheet: the raw **URL**, a **blog** markdown line (`📋 Free worksheet: [Download … →](url)`), and a **YouTube description** block.

Auto-insertion (no copy step):
- **Blogs** via `produce_blog.py` → CTA appended to the markdown.
- **YouTube scripts** via `ghostwrite.py --format yt` (DS/Life) → a spoken "free worksheet, linked in the description" line is appended **only if a worksheet exists for that slug**, and the description snippet is printed for you to paste into the video description.

---

### Step 5: Share

The link behaves like a mini landing page: visitor enters email → tagged in Kit (new vs returning) → PDF opens immediately. Same URL works in stories link stickers, bio, blog body, and comment replies.

---

## Integration with Blog Creation Workflow

When writing new blogs, **immediately** decide: worksheet or not?

**Decision tree:**

```
Is this blog actionable? (How-to, personal practice, framework)
  ├─ YES: Data Science/Tech
  │   └─ → Generate DS worksheet (SQL, code, technical checklist)
  ├─ YES: Life & Self-Dev
  │   └─ → Generate Life worksheet (design template, reflection prompts)
  ├─ NO: Poetry/Commentary/Reflection
  │   └─ → Skip worksheet
  └─ MAYBE: Ambiguous
      └─ → Run script, it auto-detects and skips if unsuitable
```

---

## Delivery system (Vercel + Kit)

The link is served by a small Vercel app at the repo root (`api/`, `vercel.json`):

```
GET  /get-worksheet?slug=<slug>   → email-capture page (title from manifest)
POST /api/subscribe {email,slug}  → Kit v4: classify new/returning, tag, sign URL
GET  /api/worksheet?slug=&t=<tok>  → verify HMAC token → stream the PDF
```

Stateless, no database. `worksheets-manifest.json` (built at deploy) maps slug → PDF. Token is HMAC-SHA256 with ~10-min expiry so the PDF path can't be shared around the email gate.

### One-time Kit setup (done once, never per blog)

1. Two tags: `first_time_worksheet`, `worksheet_repeat_visitor` (the app auto-creates them on first hit if missing).
2. **Automation A** — trigger tag `first_time_worksheet` → welcome email.
3. **Automation B** — trigger tag `worksheet_repeat_visitor` → returning-visitor email.
4. Generate a v4 API key → set `CONVERTKIT_API_KEY` in `.env` and the Vercel dashboard.

**New vs returning = does the email already exist in Kit.** Existing Substack/newsletter subscribers therefore get Automation B on their first worksheet; only brand-new emails get Automation A.

### Env vars

`CONVERTKIT_API_KEY`, `WORKSHEET_TOKEN_SECRET` (`openssl rand -hex 32`), `WORKSHEET_BASE_URL`.

---

## Email Collection Flow

1. **Reader clicks the worksheet link** (blog, IG bio/story, social).
2. **Email-capture page** → enters email.
3. **`/api/subscribe`** → Kit upsert + tag (new vs returning) → fires the matching automation.
4. **Redirect to a signed `/api/worksheet` URL** → PDF opens immediately.
5. **Welcome / returning email** sent by the Kit automation.

---

## Measurement

Track in ConvertKit:
- **Form views** (click-through from IG)
- **Form conversions** (emails collected)
- **Download rate** (PDF opened)
- **Reply rate** (email responses)

Update `data/analytics/worksheet_performance.csv` weekly:
```
date,blog_slug,worksheet_type,form_views,conversions,conversion_rate,pdf_downloads
2026-05-17,2026-05-12_ml_sql,conversion_guide,143,28,19.6%,26
2026-05-17,2026-05-13_checkin,design_template,267,54,20.2%,52
```

---

## Key Files

| File | Purpose |
|------|---------|
| `scripts/generate_worksheet_outline.py` | Blog → worksheet JSON |
| `scripts/generate_canva_worksheet_prompt.py` | Worksheet JSON → Canva prompt |
| `prompts/worksheet_canva_prompts.md` | Design templates per niche |
| `config/worksheet_config.json` | Optional titles + IG CTAs (worksheet titles override the slug-derived default) |
| `content/worksheets/` | Generated worksheet JSONs |
| `output/worksheets/` | Final PDFs — committing one here makes its link live |
| `scripts/build-worksheets-manifest.mjs` | Globs PDFs → `worksheets-manifest.json` (slug → PDF) |
| `scripts/worksheet_links.py` | Print shareable links (`--week`, `--niche`, `--json`) |
| `scripts/lib/worksheet_cta.py` | CTA block + URL helper (used by `produce_blog.py`) |
| `api/` + `vercel.json` | Vercel delivery app (capture page, subscribe, PDF stream) |

---

## Tips

- **Worksheet-first mindset:** When writing, ask: "Will readers want to *do* something with this?" If yes → worksheet-eligible.
- **Time investment:** Prompt generation (free), Canva design (15-20 min), ConvertKit setup (5 min).
- **Reusable designs:** Once you design a DS worksheet template in Canva, duplicate it for future DS blogs (just swap sections).
- **Poetry workaround:** If you want worksheets for reflection, manually create them outside this script (it auto-skips poetry).
