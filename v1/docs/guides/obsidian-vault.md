---
title: "Obsidian Vault — auto-indexed content and KB"
type: doc
slug: obsidian-vault
tags: [content/doc]
---
# Obsidian Vault — auto-indexed content and KB

The vault at `vault/` (repo root) is an Obsidian workspace that mirrors your repository. Edit notes in Obsidian and changes write directly back to the repo — no copy, no sync step. The vault is opened by pointing Obsidian to the `vault/` directory.

## Architecture

**Relative symlinks** link Obsidian directories to the repo:
- `Content/` → `../v1/content`
- `KB/` → `../v1/data/kb`
- `Docs/` → `../v1/docs`
- `Prompts/` → `../v1/prompts`

When you edit a note (e.g., `Content/blogs/2026-W29/my-article.md`) in Obsidian, you are editing the actual repo file. The symlinks are created automatically by `build_vault.py --vault-only`.

## How to rebuild

Run the vault builder to regenerate frontmatter on all `.md` files, rebuild indexes, and ensure symlinks + Obsidian config are current:

```bash
python3 v1/scripts/build_vault.py
```

### Flags

| Flag | What it does |
|------|-------------|
| `--dry-run` | Print unified diffs; write nothing |
| `--check` | Exit 1 if any file lacks frontmatter; write nothing |
| `--force-rewrite` | Recompute all derived keys (type, niche, date, week, slug, platform, tags) while preserving title and user-added keys; then rebuild vault |
| `--vault-only` | Build only the vault shell (symlinks, `.obsidian` config, index files); skip frontmatter processing of `.md` files |
| `--self-check` | Run self-test with 3 fixtures and exit |

**When to use:**
- **Fresh vault setup:** `python3 v1/scripts/build_vault.py --vault-only`
- **After adding new content:** `python3 v1/scripts/build_vault.py` (to add frontmatter and regenerate indexes)
- **After changing file structure or niche keywords:** `python3 v1/scripts/build_vault.py --force-rewrite`
- **Debugging:** `python3 v1/scripts/build_vault.py --check` (lists files that need frontmatter)

The script is idempotent: running it twice produces no changes on the second run.

## Frontmatter schema

Every `.md` file in the vault gets a YAML frontmatter block. Keys are emitted in this order, omitting keys that cannot be derived:

| Key | Derived how | Always present? |
|-----|-------------|-----------------|
| `title` | First `# H1` from body, OR existing frontmatter, OR (rarely) inferred from filename | Usually |
| `type` | Directory structure: `content/blogs` → `blog`, `content/reels` → `reel`, `docs/` → `doc`, `data/kb/` → `kb`, `prompts/` → `prompt`. **Special:** parent dir ends in `_images` → `image-map` | Yes |
| `niche` | Matched from filename/path against `NICHE_MAP` (longest match wins). Canonical: `data_science_tech`, `life_self_dev`, `poetry_quotes` | Only if derivable |
| `date` | Filename must start with `YYYY-MM-DD` prefix | Only if derivable |
| `week` | ISO week found in path (e.g., `2026-W29`), or derived from `date` via `get_iso_week()` | Only if derivable |
| `slug` | Filename stem with date, niche, and platform suffixes removed; normalized to lowercase dashes | Only if derivable |
| `platform` | Matched from filename suffix against `PLATFORM_MAP` (e.g., `_ig_reel` → `ig`, `_linkedin` → `linkedin`) | Only if derivable |
| `status` | **Omitted from frontmatter intentionally** — see [Why status is NOT in frontmatter](#why-status-is-not-in-frontmatter) | Never |
| `tags` | Generated from type + niche + week, e.g., `[content/blog, niche/life_self_dev, week/2026-W29]` | Only if derivable |

If a file has existing frontmatter with unknown keys (not in the schema), those keys are preserved.

### Example

File: `v1/content/blogs/2026-W29/2026-07-17_life_self_dev_clarity-paradox.md`

Generated frontmatter:
```yaml
---
title: "Finding Clarity in Paradox"
type: blog
niche: life_self_dev
date: 2026-07-17
week: 2026-W29
slug: clarity-paradox
tags: [content/blog, niche/life_self_dev, week/2026-W29]
---
```

## Why status is NOT in frontmatter

`status` (Published / Scheduled / Draft) is deliberately omitted from the vault's frontmatter. Instead, it lives in the Medium tracker (`v1/docs/medium-submissions-tracker.md`) as the single source of truth. 

**Reason:** The repo rule is [TRACKER FIRST](../../CLAUDE.md). Article slugs sometimes drift from titles, making a frontmatter status field unreliable. The tracker keys on full article titles and stays canonical.

## Body is never touched

The script modifies **only the frontmatter block**, never the body text. Inline bold metadata like `**Niche:** life_self_dev` in buffer or derivative prose is left untouched. The body is read-only from the script's perspective; frontmatter is the query layer.

## Files skipped

Only **true Claude Code slash-command definitions** are skipped. A file is skipped if it has BOTH:
1. `$ARGUMENTS` in the body, AND
2. `description:` key in the frontmatter

This avoids skipping documentation files that happen to mention `$ARGUMENTS`. For example, a guide explaining a command is not skipped; a command definition file is.

## Obsidian configuration

The vault uses a `.obsidian/app.json` file (gitignored) to configure Obsidian. Key setting:

| Setting | Value | Why |
|---------|-------|-----|
| `userIgnoreFilters` | Hide `.json`, `.txt`, `.html`, `.mov`, `.mp4`, video, audio, code, PDFs, notebooks under `Content/` | Keep the view focused on note content; images are shown (so blog embeds render) |
| `attachmentFolderPath` | `./` | Default location for Obsidian-inserted attachments |
| `alwaysUpdateLinks` | `true` | Automatically update links when files are renamed |

The config is merged (not overwritten) on every run — user customizations are preserved.

## Generated indexes

After frontmatter processing, the script rebuilds four auto-generated index files in `vault/Index/`:

| Index | What it contains |
|-------|-----------------|
| `Blogs.md` | All `type: blog` entries, grouped by ISO week (newest first), sorted by title within each week |
| `Reels.md` | All `type: reel` entries, grouped by ISO week (newest first) |
| `By-Niche.md` | Entries by canonical niche (data_science_tech, life_self_dev, poetry_quotes), sorted by week descending then title ascending |
| `By-Week.md` | Entries by ISO week (newest first), sorted by title within each week |
| `Trackers.md` | Hardcoded link to pipeline-2026.md + auto-discovered tracker docs |

**Image-map manifests** (`type: image-map`, which live in `*_images/` directories) are excluded from all indexes — they are asset metadata, not content.

`Home.md` (at vault root) is a dashboard showing quick stats: total Blogs, Reels, and counts by niche. The counts auto-update based on the indexes.

**Do not edit generated indexes.** They are marked with a comment header and overwritten on every build.

## After adding new content

Once you create a new blog, reel, or document, run the builder so:
1. Frontmatter is added to the new file
2. Indexes pick up the new entry
3. `Home.md` stats update

```bash
python3 v1/scripts/build_vault.py
```

This is safe to run weekly as part of your publishing workflow — it's idempotent and skips files that are already current.

## Troubleshooting

**Missing frontmatter?** Run `--check` to see which files lack it:
```bash
python3 v1/scripts/build_vault.py --check
```

**Wiki links not working in Obsidian?** Ensure symlinks are created:
```bash
python3 v1/scripts/build_vault.py --vault-only
```

**Slugs look wrong after a rename?** Use `--force-rewrite` to recompute derived fields:
```bash
python3 v1/scripts/build_vault.py --force-rewrite
```

**Obsidian showing too many files?** The `.obsidian/app.json` config filters out media and code under `Content/`. If Obsidian is still cluttered, check `userIgnoreFilters` in that file and add more patterns as needed.
