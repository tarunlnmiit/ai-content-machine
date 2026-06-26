#!/usr/bin/env node
// Copies output/worksheets/**/*.pdf → public/worksheets/{slug}.pdf
// Works on Node.js 18+.

import { readdirSync, copyFileSync, mkdirSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, basename } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO = join(__dirname, "..");

const NICHE_SEGMENTS = ["data_science_tech", "life_self_dev", "poetry_quotes"];
const PDF_RE = new RegExp(
  `^(\\d{4}-\\d{2}-\\d{2})_(${NICHE_SEGMENTS.join("|")})_(.+?)(_worksheet)?\\.pdf$`,
);

function walkPdfs(dir, results = []) {
  let entries;
  try { entries = readdirSync(dir); } catch { return results; }
  for (const entry of entries) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) {
      walkPdfs(full, results);
    } else if (entry.endsWith(".pdf")) {
      results.push(full);
    }
  }
  return results;
}

const destDir = join(REPO, "public", "worksheets");
mkdirSync(destDir, { recursive: true });

const pdfs = walkPdfs(join(REPO, "output", "worksheets"));
let count = 0;

for (const fullPath of pdfs) {
  const file = basename(fullPath);
  const m = file.match(PDF_RE);
  if (!m) { console.warn(`[copy-pdfs] skip (unparseable): ${file}`); continue; }
  const [, , , slug] = m;
  const dest = join(destDir, `${slug}.pdf`);
  copyFileSync(fullPath, dest);
  console.log(`[copy-pdfs] ${file} → public/worksheets/${slug}.pdf`);
  count++;
}

console.log(`[copy-pdfs] done — ${count} PDF(s) copied.`);
