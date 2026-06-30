#!/usr/bin/env node
// Builds worksheets-manifest.json by globbing output/worksheets/**/*.pdf.
// Public slug is derived from the filename (strip date + niche prefix and
// optional _worksheet suffix). Title resolves in priority order:
//   1. config/worksheet_config.json override (full stem key)
//   2. the worksheet content JSON `title` (content/worksheets/**/<stem>_worksheet.json)
//   3. the existing committed manifest's title (survives Vercel builds, where
//      content/ is .vercelignore'd and step 2's JSONs are absent)
//   4. Title-Cased slug (last-resort fallback)
//
// Runs at Vercel build (buildCommand) AND locally. No npm deps.

import { readdirSync, statSync, readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, relative, basename } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO = join(__dirname, "..");

const NICHE_SEGMENTS = ["data_science_tech", "life_self_dev", "poetry_quotes"];
const PDF_RE = new RegExp(
  `^(\\d{4}-\\d{2}-\\d{2})_(${NICHE_SEGMENTS.join("|")})_(.+?)(_worksheet)?\\.pdf$`,
);

function titleCase(slug) {
  return slug
    .split("-")
    .filter(Boolean)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

function loadConfigTitles() {
  const path = join(REPO, "config", "worksheet_config.json");
  try {
    const cfg = JSON.parse(readFileSync(path, "utf8"));
    return cfg.worksheets ?? {};
  } catch {
    return {};
  }
}

// Map slug -> title from the existing committed manifest. This is the
// build-sandbox-safe title source: content/ is excluded by .vercelignore, so
// the worksheet JSONs are NOT present during a Vercel build — but the committed
// manifest (correct, generated locally) IS uploaded. Preserving its titles
// stops the build from clobbering good titles back to Title-Cased slugs.
function loadExistingTitles() {
  const path = join(REPO, "worksheets-manifest.json");
  try {
    const m = JSON.parse(readFileSync(path, "utf8"));
    const out = {};
    for (const [slug, e] of Object.entries(m.worksheets ?? {})) {
      if (e?.title) out[slug] = e.title;
    }
    return out;
  } catch {
    return {};
  }
}

// Map worksheet stem -> human title from the generated content JSON
// (content/worksheets/**/<stem>_worksheet.json). Source of truth for the
// display title locally; absent in the Vercel build sandbox (content/ ignored).
function loadJsonTitles() {
  const titles = {};
  const root = join(REPO, "content", "worksheets");
  const walk = (dir) => {
    let entries;
    try { entries = readdirSync(dir); } catch { return; }
    for (const entry of entries) {
      const full = join(dir, entry);
      if (statSync(full).isDirectory()) {
        walk(full);
      } else if (entry.endsWith("_worksheet.json")) {
        const stem = entry.slice(0, -"_worksheet.json".length);
        try {
          const t = JSON.parse(readFileSync(full, "utf8")).title;
          if (t) titles[stem] = t;
        } catch { /* ignore unreadable json */ }
      }
    }
  };
  walk(root);
  return titles;
}

function walkPdfs(dir, root, results = []) {
  let entries;
  try { entries = readdirSync(dir); } catch { return results; }
  for (const entry of entries) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) {
      walkPdfs(full, root, results);
    } else if (entry.endsWith(".pdf")) {
      results.push(relative(root, full));
    }
  }
  return results;
}

function main() {
  const configWorksheets = loadConfigTitles();
  const jsonTitles = loadJsonTitles();
  const existingTitles = loadExistingTitles();
  const pdfs = walkPdfs(join(REPO, "output", "worksheets"), REPO);

  const bySlug = new Map(); // slug -> { date, niche, pdfPath, title }
  const warnings = [];

  for (const rel of pdfs.sort()) {
    const file = basename(rel);
    const m = file.match(PDF_RE);
    if (!m) {
      warnings.push(`skip (unparseable name): ${rel}`);
      continue;
    }
    const [, date, niche, slug] = m;
    const stem = `${date}_${niche}_${slug}`;
    const cfg = configWorksheets[stem];
    const title =
      cfg?.title ?? jsonTitles[stem] ?? existingTitles[slug] ?? titleCase(slug);
    const entry = { date, niche, slug, pdfPath: rel, title };

    const existing = bySlug.get(slug);
    if (existing) {
      // Newest date wins on collision.
      if (date >= existing.date) {
        warnings.push(
          `slug collision "${slug}": ${existing.pdfPath} -> superseded by ${rel}`,
        );
        bySlug.set(slug, entry);
      } else {
        warnings.push(`slug collision "${slug}": kept ${existing.pdfPath}, ignored ${rel}`);
      }
    } else {
      bySlug.set(slug, entry);
    }
  }

  const manifest = {
    generatedAt: new Date().toISOString(),
    count: bySlug.size,
    worksheets: Object.fromEntries(
      [...bySlug.entries()].map(([slug, e]) => [
        slug,
        { title: e.title, niche: e.niche, date: e.date, pdfPath: e.pdfPath },
      ]),
    ),
  };

  const outPath = join(REPO, "worksheets-manifest.json");
  writeFileSync(outPath, JSON.stringify(manifest, null, 2) + "\n", "utf8");

  console.log(`[manifest] wrote ${relative(REPO, outPath)} (${manifest.count} worksheets)`);
  for (const w of warnings) console.warn(`[manifest] WARN ${w}`);
}

main();
