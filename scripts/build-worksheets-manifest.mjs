#!/usr/bin/env node
// Builds worksheets-manifest.json by globbing output/worksheets/**/*.pdf.
// Public slug is derived from the filename (strip date + niche prefix and
// optional _worksheet suffix). Title comes from config/worksheet_config.json
// when the full stem is present, else Title-Cases the slug.
//
// Runs at Vercel build (buildCommand) AND locally. No npm deps.

import { globSync } from "node:fs";
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, relative } from "node:path";

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

function main() {
  const configWorksheets = loadConfigTitles();
  const pdfs = globSync("output/worksheets/**/*.pdf", { cwd: REPO });

  const bySlug = new Map(); // slug -> { date, niche, pdfPath, title }
  const warnings = [];

  for (const rel of pdfs.sort()) {
    const file = rel.split("/").pop();
    const m = file.match(PDF_RE);
    if (!m) {
      warnings.push(`skip (unparseable name): ${rel}`);
      continue;
    }
    const [, date, niche, slug] = m;
    const stem = `${date}_${niche}_${slug}`;
    const cfg = configWorksheets[stem];
    const title = cfg?.title ?? titleCase(slug);
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
