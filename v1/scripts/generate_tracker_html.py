#!/usr/bin/env python3
"""
Parse v1/docs/content-tracker.md and emit a self-contained HTML view with the
auto-detected columns (blog/carousel/worksheet/reel/longform/derivatives) baked
in as filesystem-scan results. No runtime fetch of the .md — the HTML is
static and portable.

Record format, auto-detected column rules, and scanner traps: see
v1/docs/content-tracker.md's header and TRACKER_SPEC.md (frozen spec).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from lib.content_paths import REPO  # v1/

DISPLAY_ROOT = REPO.parent  # content-machine/ — paths render as "v1/..."

DEFAULT_MD = REPO / "docs" / "content-tracker.md"
DEFAULT_HTML = REPO / "docs" / "content-tracker.html"

DASH = "—"  # em dash — the MD's "unknown" sentinel
ORPHAN_PREFIX = "ORPHAN:"  # slug prefix for a piece with no confidently-matched blog file

REQUIRED_FIELDS = (
    "title", "week", "niche", "date",
    "medium.pub", "medium.status", "medium.submitted", "medium.url", "medium.method",
    "linkedin.status", "linkedin.url",
    "carousel.status", "carousel.url",
    "reel.ref", "reel.status", "reel.cta", "reel.ig", "reel.yt",
    "longform.ref", "longform.status", "longform.url",
    "worksheet.status", "worksheet.url",
    "source_draft", "flags",
)

# Editing these would change a record's identity or destroy provenance, so the
# model is never allowed to touch them — only additive `notes` is permitted.
IMMUTABLE = frozenset({"title", "week", "niche", "date"})
EDITABLE = tuple(f for f in REQUIRED_FIELDS if f not in IMMUTABLE)

ENUMS = {
    "medium.status": ["submitted", "accepted", "declined", "published", "withdrawn",
                      "draft", "self-publishing", DASH],
    "linkedin.status": ["posted", "scheduled", "pending", "none", DASH],
    "carousel.status": ["none", "created", "scheduled", "posted", DASH],
    "reel.status": ["script", "rendered", "scheduled", "posted", "none", DASH],
    "longform.status": ["none", "script", "assembled", "scheduled", "published", DASH],
    "worksheet.status": ["none", "generated", "deployed", DASH],
}

# Short names like reel.ig read as "posted to IG?" and tempt the model to write a date
# or a bare "yes" into a link column, so the URL shape is enforced, not just requested.
URL_FIELDS = frozenset({
    "medium.url", "linkedin.url", "carousel.url", "reel.ig", "reel.yt",
    "longform.url", "worksheet.url",
})

DATE_FIELDS = frozenset({"medium.submitted"})

VALUE_COL = 18  # every record in the MD aligns its field values at this column

AUTO_COLUMNS = (
    "blog", "carousel", "carousel_export", "worksheet",
    "reel_script", "reel_video", "longform_video", "derivatives",
)

HEADER_RE = re.compile(r"^##\s+(.+?)\s*$")
FIELD_RE = re.compile(r"^(\S+):[ \t]?(.*)$")


class TrackerParseError(Exception):
    def __init__(self, slug: str, reason: str):
        super().__init__(f"{slug}: {reason}")
        self.slug = slug
        self.reason = reason


def split_blocks(text: str) -> list[tuple[str, list[str]]]:
    blocks: list[tuple[str, list[str]]] = []
    slug: str | None = None
    lines: list[str] = []
    for raw in text.splitlines():
        m = HEADER_RE.match(raw)
        if m:
            if slug is not None:
                blocks.append((slug, lines))
            slug = m.group(1)
            lines = []
        elif slug is not None:
            lines.append(raw)
    if slug is not None:
        blocks.append((slug, lines))
    return blocks


def is_record(lines: list[str]) -> bool:
    """A '##' block is a record iff it carries a 'title:' field line; otherwise it is
    reference prose. Continuation lines inside 'notes: |' are indented, so an
    unindented 'title:' can only be a real field."""
    return any(line.startswith("title:") for line in lines)


def parse_record(slug: str, lines: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    notes_lines: list[str] = []
    notes_seen = False
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if line.strip() in ("", "---"):
            i += 1
            continue
        m = FIELD_RE.match(line)
        if not m:
            raise TrackerParseError(slug, f"unparseable line: {line!r}")
        key, val = m.group(1), m.group(2).strip()
        if key == "notes":
            if val != "|":
                raise TrackerParseError(slug, f"notes: must open a '|' block, got {val!r}")
            notes_seen = True
            i += 1
            indent: int | None = None
            while i < n and not re.match(r"^\S", lines[i]):
                nline = lines[i]
                if nline.strip() == "":
                    notes_lines.append("")
                else:
                    cur_indent = len(nline) - len(nline.lstrip(" "))
                    if indent is None:
                        indent = cur_indent
                    notes_lines.append(nline[indent:] if cur_indent >= indent else nline.lstrip())
                i += 1
            continue
        if key not in REQUIRED_FIELDS:
            raise TrackerParseError(slug, f"unknown field {key!r}")
        if key in values:
            raise TrackerParseError(slug, f"duplicate field {key!r}")
        values[key] = val
        i += 1
    missing = [f for f in REQUIRED_FIELDS if f not in values]
    if missing:
        raise TrackerParseError(slug, f"missing field(s): {', '.join(missing)}")
    if not notes_seen:
        raise TrackerParseError(slug, "missing 'notes: |' block")
    while notes_lines and notes_lines[-1] == "":
        notes_lines.pop()
    values["slug"] = slug
    values["notes"] = "\n".join(notes_lines)
    return values


def parse_md(text: str) -> tuple[list[dict[str, str]], list[str]]:
    records: list[dict[str, str]] = []
    errors: list[str] = []
    seen: set[str] = set()
    for slug, lines in split_blocks(text):
        if not is_record(lines):
            continue
        if not slug:
            errors.append("(blank slug): '##' header has no slug text")
            continue
        if slug in seen:
            errors.append(f"{slug}: duplicate slug — block appears more than once")
            continue
        seen.add(slug)
        try:
            records.append(parse_record(slug, lines))
        except TrackerParseError as e:
            errors.append(str(e))
    return records, errors


# ── filesystem auto-detection (spec §3) ────────────────────────────────────

def rel_str(p: Path) -> str:
    return str(p.relative_to(DISPLAY_ROOT))


def week_folder(week: str) -> str | None:
    if not week or week == DASH:
        return None
    # Folder convention is literally "2026-<week>" per spec §3 rule 4 — the
    # week field alone never carries a year, so this is not re-derived here.
    return f"2026-{week}"


def find_first(candidates: list[Path]) -> str:
    for c in candidates:
        if c.exists():
            return rel_str(c)
    return DASH


def find_glob(base_dir: Path, ref: str, pattern: str) -> str:
    if not ref or ref == DASH:
        return DASH
    matches = sorted(base_dir.rglob(pattern.format(ref=ref))) if base_dir.exists() else []
    if not matches:
        return DASH
    if len(matches) > 1:
        return "?"
    return rel_str(matches[0])


def compute_auto(rec: dict[str, str]) -> dict[str, str]:
    slug = rec["slug"]
    wf = week_folder(rec["week"])

    blog = find_first([REPO / "content" / "blogs" / wf / f"{slug}.md"]) if wf else DASH

    carousel_candidates = []
    if wf:
        carousel_candidates.append(REPO / "assets" / "carousels" / wf / f"{slug}_carousel.html")
    carousel_candidates.append(REPO / "assets" / "carousels" / f"{slug}_carousel.html")
    carousel = find_first(carousel_candidates)

    export_candidates = []
    if wf:
        export_candidates.append(REPO / "assets" / "carousels" / wf / f"{slug}_export.py")
    export_candidates.append(REPO / "assets" / "carousels" / f"{slug}_export.py")
    carousel_export = find_first(export_candidates)

    if wf:
        wdir = REPO / "output" / "worksheets" / wf
        worksheet = find_first([wdir / f"{slug}_worksheet.pdf", wdir / f"{slug}.pdf"])
    else:
        worksheet = DASH

    # reel scripts sit either flat in the week folder or one level deeper under a
    # per-reel subfolder, so this scans recursively rather than by week.
    reel_ref = rec["reel.ref"]
    reel_script = find_glob(REPO / "content" / "reels", reel_ref, "{ref}_ig_reel.md")

    reel_video = find_glob(REPO / "assets" / "reels_video", reel_ref, "{ref}*.mp4")
    longform_video = find_glob(REPO / "assets" / "videos", rec["longform.ref"], "{ref}*.mp4")

    derivatives = DASH
    if wf:
        d = REPO / "content" / "derivatives" / wf / slug
        if d.is_dir():
            derivatives = rel_str(d)

    return {
        "blog": blog,
        "carousel": carousel,
        "carousel_export": carousel_export,
        "worksheet": worksheet,
        "reel_script": reel_script,
        "reel_video": reel_video,
        "longform_video": longform_video,
        "derivatives": derivatives,
    }


def is_flagged(rec: dict[str, str], auto: dict[str, str]) -> bool:
    if rec.get("flags", DASH) not in ("", DASH):
        return True
    if rec.get("worksheet.status") == "deployed" and rec.get("worksheet.url", DASH) in ("", DASH):
        return True
    return any(v == "?" for v in auto.values())


# ── HTML rendering ──────────────────────────────────────────────────────────

COLUMNS = (
    ("slug", "Slug", "Core"), ("title", "Title", "Core"), ("week", "Week", "Core"),
    ("niche", "Niche", "Core"), ("date", "Date", "Core"), ("flags", "Flags", "Core"),
    ("medium.pub", "Medium Pub", "Medium"), ("medium.status", "Medium Status", "Medium"),
    ("medium.submitted", "Medium Submitted", "Medium"), ("medium.url", "Medium URL", "Medium"),
    ("medium.method", "Medium Method", "Medium"),
    ("linkedin.status", "LinkedIn Status", "LinkedIn"), ("linkedin.url", "LinkedIn URL", "LinkedIn"),
    ("carousel.status", "Carousel Status", "Carousel"), ("carousel.url", "Carousel URL", "Carousel"),
    ("reel.ref", "Reel Ref", "Reel"), ("reel.status", "Reel Status", "Reel"),
    ("reel.cta", "Reel CTA", "Reel"), ("reel.ig", "Reel IG", "Reel"), ("reel.yt", "Reel YT", "Reel"),
    ("longform.ref", "Longform Ref", "Longform"), ("longform.status", "Longform Status", "Longform"),
    ("longform.url", "Longform URL", "Longform"),
    ("worksheet.status", "Worksheet Status", "Worksheet"), ("worksheet.url", "Worksheet URL", "Worksheet"),
    ("source_draft", "Source Draft", "Meta"),
    ("blog", "Blog (auto)", "Auto"), ("carousel", "Carousel HTML (auto)", "Auto"),
    ("carousel_export", "Carousel Export (auto)", "Auto"),
    ("worksheet", "Worksheet PDF (auto)", "Auto"), ("reel_script", "Reel Script (auto)", "Auto"),
    ("reel_video", "Reel Video (auto)", "Auto"), ("longform_video", "Longform Video (auto)", "Auto"),
    ("derivatives", "Derivatives (auto)", "Auto"),
    ("notes", "Notes", "Notes"),
)

# Starting state only — the browser stores the user's own hidden set in localStorage.
# 35 columns cannot fit a laptop viewport at any wrap setting, so the default is the
# daily-scan tier: identity + statuses. The hidden ones are long identifier/URL/path
# columns you look up rather than scan — one click in the Columns panel brings any back.
HIDDEN_BY_DEFAULT = frozenset({
    "slug", "medium.method", "medium.url", "medium.submitted",
    "linkedin.url", "carousel.url", "reel.ref", "reel.ig", "reel.yt",
    "longform.ref", "longform.url", "worksheet.url", "source_draft",
    *AUTO_COLUMNS,
})

DEFAULT_SORT_KEY = "date"

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Content Tracker</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono&display=swap" rel="stylesheet">
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:#14121f;color:#EDE8DC;font-family:'Inter','Helvetica Neue',Arial,sans-serif;
       padding:28px;line-height:1.5}
  h1{font-size:24px;font-weight:800;letter-spacing:-0.02em;margin-bottom:4px}
  .sub{font-size:13px;opacity:.6;margin-bottom:16px}
  .toolbar{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:14px;align-items:center}
  .toolbar select,.toolbar input,.toolbar button{background:rgba(255,255,255,.06);
       border:1px solid rgba(255,255,255,.15);
       color:#EDE8DC;border-radius:8px;padding:6px 10px;font-size:13px;font-family:inherit}
  .toolbar input{min-width:220px}
  .toolbar button{cursor:pointer}
  .toolbar button:hover{background:rgba(255,255,255,.12)}
  .summary{font-size:12px;opacity:.6;margin-bottom:10px}
  .sortwrap{display:flex;align-items:center;gap:6px}
  .sortwrap label{font-size:10.5px;text-transform:uppercase;letter-spacing:.1em;opacity:.5}

  .cell-editor{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.15);
       color:#EDE8DC;border-radius:4px;padding:4px 6px;font-size:12px;font-family:inherit}
  .cell-editor select{max-width:200px}
  .cell-editor input{min-width:120px}
  .notebtn{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.15);
       color:#EDE8DC;border-radius:4px;padding:1px 7px;margin-top:5px;font-size:10.5px;
       font-family:inherit;cursor:pointer;opacity:.7;display:block}
  .notebtn:hover{opacity:1;background:rgba(255,255,255,.12)}
  .cell-flash{animation:cellFlash 0.3s ease-out}
  @keyframes cellFlash{0%{background:rgba(127,209,168,.3)}100%{background:transparent}}
  .cell-error{animation:cellError 0.4s ease-out}
  @keyframes cellError{0%{background:rgba(232,116,90,.3)}100%{background:transparent}}

  /* the wrap owns BOTH axes of scrolling — that is what gives sticky th a moving
     scrollport to stick to, and it keeps the page itself from growing. */
  .table-wrap{overflow:auto;max-height:calc(100vh - 260px);
       border:1px solid rgba(255,255,255,.12);border-radius:10px;max-width:100%}
  table{border-collapse:collapse;width:100%;font-size:12.5px}
  th,td{text-align:left;padding:7px 10px;vertical-align:top;
       border-bottom:1px solid rgba(255,255,255,.08);white-space:nowrap}
  th{position:sticky;top:0;z-index:2;background:#1b1830;font-size:10.5px;text-transform:uppercase;
     letter-spacing:.08em;opacity:.65;cursor:pointer;user-select:none;
     border-bottom:none;box-shadow:inset 0 -1px 0 rgba(255,255,255,.15)}
  th:hover{opacity:1}
  th.sorted{opacity:1;color:#EDE8DC}
  td code{font-family:'JetBrains Mono',monospace;font-size:11.5px;opacity:.85}
  tr.flagged td{background:rgba(232,116,90,.08)}
  .flagbadge{display:inline-block;font-size:11px;padding:2px 8px;border-radius:20px;
       border:1px solid #E8745A;color:#E8745A;background:rgba(232,116,90,.12)}
  .orphanbadge{display:inline-block;font-size:9.5px;font-weight:800;letter-spacing:.08em;
       padding:1px 6px;border-radius:4px;margin-right:6px;vertical-align:1px;
       border:1px solid rgba(237,232,220,.3);color:#EDE8DC;background:rgba(255,255,255,.07)}
  .qmark{color:#E8745A;font-weight:800}

  /* nowrap stays the default (dates/statuses must not break); only the prose-y and
     path columns opt into wrapping, or the table runs ~16000px wide. */
  /* min-width matters as much as max: under auto table layout the nowrap columns
     bully the wrapping ones down to a few characters and rows grow 7 lines tall. */
  td[data-key="title"],th[data-key="title"]{white-space:normal;min-width:250px;max-width:320px}
  td[data-key="flags"],th[data-key="flags"]{white-space:normal;min-width:170px;max-width:240px;cursor:pointer}
  td[data-key="notes"],th[data-key="notes"]{white-space:normal;min-width:240px;max-width:380px;cursor:pointer}
  td[data-auto="1"]{white-space:normal;max-width:320px;word-break:break-all}
  td[data-key="reel.ref"],td[data-key="longform.ref"]{white-space:normal;max-width:220px;word-break:break-all}
  td[data-key="medium.url"],td[data-key="linkedin.url"],td[data-key="carousel.url"],
  td[data-key="reel.ig"],td[data-key="reel.yt"],td[data-key="longform.url"],
  td[data-key="worksheet.url"]{white-space:normal;max-width:240px;word-break:break-all}
  td[data-key="medium.pub"]{white-space:normal;max-width:170px}
  .clamp{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
  td.expanded .clamp{-webkit-line-clamp:unset;display:block}
  td[data-key="title"] .clamp{-webkit-line-clamp:3}

  .colwrap{position:relative;display:inline-block}
  .colpanel{display:none;position:absolute;top:calc(100% + 6px);left:0;z-index:10;
       background:#1b1830;border:1px solid rgba(255,255,255,.18);border-radius:10px;
       padding:12px 14px;min-width:520px;max-height:60vh;overflow:auto;
       box-shadow:0 12px 32px rgba(0,0,0,.5);
       columns:2;column-gap:22px}
  .colpanel.open{display:block}
  .colgroup{break-inside:avoid;margin-bottom:12px}
  .colgroup h4{font-size:10px;text-transform:uppercase;letter-spacing:.1em;opacity:.5;
       margin-bottom:5px;font-weight:800}
  .colgroup label{display:block;font-size:12px;padding:2px 0;cursor:pointer;opacity:.9}
  .colgroup label:hover{opacity:1}
  .colgroup input{margin-right:7px;vertical-align:-1px}
  .colgroup .ga{font-size:10px;opacity:.5;cursor:pointer;margin-left:6px;text-decoration:underline}
  .ds-foot{margin-top:20px;padding-top:12px;border-top:1px solid rgba(255,255,255,.12);
       font-size:11px;opacity:.55}
</style>
</head>
<body>
<h1>Content Tracker</h1>
<p class="sub">Generated by v1/scripts/generate_tracker_html.py from v1/docs/content-tracker.md. Data baked in — no live fetch.</p>
<div class="toolbar">
  <select id="fWeek"><option value="">All weeks</option></select>
  <select id="fNiche"><option value="">All niches</option></select>
  <select id="fMediumStatus"><option value="">All medium statuses</option></select>
  <select id="fType">
    <option value="">All types</option>
    <option value="orphan">Orphans only</option>
    <option value="piece">Non-orphans only</option>
  </select>
  <input id="fSearch" type="text" placeholder="Search title / slug / notes...">
  <span class="colwrap">
    <button id="colBtn" type="button">Columns ▾</button>
    <div class="colpanel" id="colPanel"></div>
  </span>
  <span class="sortwrap">
    <label for="fSort">Sort</label>
    <select id="fSort"></select>
    <select id="fSortDir">
      <option value="desc">newest / Z→A</option>
      <option value="asc">oldest / A→Z</option>
    </select>
  </span>
</div>
<p class="summary" id="summary"></p>
<div class="table-wrap">
  <table id="tracker">
    <thead><tr id="headRow"></tr></thead>
    <tbody id="bodyRows"></tbody>
  </table>
</div>
<div class="ds-foot">Regenerate with: python3 v1/scripts/generate_tracker_html.py</div>
<script>
const COLUMNS = __COLUMNS_JSON__;
const ROWS = __ROWS_JSON__;
const HIDDEN_BY_DEFAULT = __HIDDEN_JSON__;
const AUTO_KEYS = new Set(__AUTO_JSON__);
const DEFAULT_SORT_KEY = __DEFAULT_SORT_JSON__;
const PUBS = __PUBS_JSON__;
const LS_KEY = 'content-tracker.hiddenColumns.v1';

const ALL_KEYS = new Set(COLUMNS.map(c => c[0]));
const headRow = document.getElementById('headRow');
let sortKey = DEFAULT_SORT_KEY, sortAsc = false;

// Persist the HIDDEN set, not the visible one: storing "visible" would make any column
// added to COLUMNS later invisible forever for anyone with an existing localStorage entry.
function loadHidden() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (raw) {
      const a = JSON.parse(raw);
      if (Array.isArray(a)) return new Set(a.filter(k => ALL_KEYS.has(k)));
    }
  } catch (e) { /* private mode / disabled storage — fall through to defaults */ }
  return new Set(HIDDEN_BY_DEFAULT);
}
function saveHidden() {
  try { localStorage.setItem(LS_KEY, JSON.stringify([...hidden])); } catch (e) { /* non-fatal */ }
}
let hidden = loadHidden();
const visibleColumns = () => COLUMNS.filter(c => !hidden.has(c[0]));

function esc(s) {
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

const noteBtnHtml = slug =>
  LIVE ? '<button type="button" class="notebtn" data-slug="' + esc(slug) + '">+ note</button>' : '';

function cellHtml(key, val, row) {
  if (key === 'title') {
    const badge = row._orphan ? '<span class="orphanbadge">ORPHAN</span>' : '';
    return '<span class="clamp">' + badge + esc(val) + '</span>';
  }
  if (val === '—') {
    if (key === 'notes') return '<code class="clamp">—</code>' + noteBtnHtml(row.slug);
    return '—';
  }
  if (val === '?') return '<span class="qmark">?</span>';
  if (key === 'flags') return '<span class="flagbadge clamp">' + esc(val) + '</span>';
  if (key === 'notes') {
    return '<code class="clamp">' + esc(val).replace(/\\n/g, '<br>') + '</code>' + noteBtnHtml(row.slug);
  }
  const looksLikePath = /^v1\\//.test(val) || AUTO_KEYS.has(key);
  const cellContent = looksLikePath ? '<code>' + esc(val) + '</code>' : esc(val);
  return cellContent;
}

function uniqueSorted(key) {
  return [...new Set(ROWS.map(r => r[key]).filter(v => v && v !== '—'))].sort();
}

function populateSelect(id, key) {
  const sel = document.getElementById(id);
  for (const v of uniqueSorted(key)) {
    const opt = document.createElement('option');
    opt.value = v; opt.textContent = v;
    sel.appendChild(opt);
  }
}
populateSelect('fWeek', 'week');
populateSelect('fNiche', 'niche');
populateSelect('fMediumStatus', 'medium.status');

function renderHead() {
  headRow.innerHTML = '';
  for (const [key, label] of visibleColumns()) {
    const th = document.createElement('th');
    th.textContent = label + (sortKey === key ? (sortAsc ? ' ▲' : ' ▼') : '');
    th.dataset.key = key;
    if (sortKey === key) th.className = 'sorted';
    th.addEventListener('click', () => {
      if (sortKey === key) sortAsc = !sortAsc; else { sortKey = key; sortAsc = true; }
      syncSortControls();
      render();
    });
    headRow.appendChild(th);
  }
}

// the dropdown and the clickable headers are two views of one sort state
function buildSortSelect() {
  const sel = document.getElementById('fSort');
  sel.innerHTML = '';
  for (const [key, label, group] of COLUMNS) {
    const opt = document.createElement('option');
    opt.value = key;
    opt.textContent = group === 'Core' || group === 'Notes' ? label : group + ' · ' + label;
    sel.appendChild(opt);
  }
  sel.value = sortKey;
  document.getElementById('fSortDir').value = sortAsc ? 'asc' : 'desc';
}

function syncSortControls() {
  document.getElementById('fSort').value = sortKey;
  document.getElementById('fSortDir').value = sortAsc ? 'asc' : 'desc';
}

document.getElementById('fSort').addEventListener('change', e => {
  sortKey = e.target.value;
  render();
});
document.getElementById('fSortDir').addEventListener('change', e => {
  sortAsc = e.target.value === 'asc';
  render();
});

function buildColPanel() {
  const panel = document.getElementById('colPanel');
  panel.innerHTML = '';
  const groups = [];
  for (const [key, label, group] of COLUMNS) {
    let g = groups.find(x => x.name === group);
    if (!g) { g = {name: group, cols: []}; groups.push(g); }
    g.cols.push([key, label]);
  }
  for (const g of groups) {
    const box = document.createElement('div');
    box.className = 'colgroup';
    const h = document.createElement('h4');
    h.textContent = g.name;
    const all = document.createElement('span');
    all.className = 'ga'; all.textContent = 'all';
    all.addEventListener('click', () => setGroup(g, true));
    const none = document.createElement('span');
    none.className = 'ga'; none.textContent = 'none';
    none.addEventListener('click', () => setGroup(g, false));
    h.appendChild(all); h.appendChild(none);
    box.appendChild(h);
    for (const [key, label] of g.cols) {
      const lab = document.createElement('label');
      const cb = document.createElement('input');
      cb.type = 'checkbox'; cb.checked = !hidden.has(key); cb.dataset.key = key;
      cb.addEventListener('change', () => toggleColumn(key, cb.checked));
      lab.appendChild(cb);
      lab.appendChild(document.createTextNode(label));
      box.appendChild(lab);
    }
    panel.appendChild(box);
  }
}

function afterVisibilityChange() {
  // sorting by a column you can no longer see is silently confusing
  if (hidden.has(sortKey)) { sortKey = DEFAULT_SORT_KEY; sortAsc = false; }
  saveHidden();
  buildColPanel();
  render();
}

function toggleColumn(key, show) {
  if (show) hidden.delete(key); else hidden.add(key);
  afterVisibilityChange();
}

function setGroup(g, show) {
  for (const [key] of g.cols) { if (show) hidden.delete(key); else hidden.add(key); }
  afterVisibilityChange();
}

const colBtn = document.getElementById('colBtn');
colBtn.addEventListener('click', e => {
  e.stopPropagation();
  document.getElementById('colPanel').classList.toggle('open');
});
document.addEventListener('click', e => {
  const panel = document.getElementById('colPanel');
  if (!panel.contains(e.target) && e.target !== colBtn) panel.classList.remove('open');
});

function currentFilters() {
  return {
    week: document.getElementById('fWeek').value,
    niche: document.getElementById('fNiche').value,
    mediumStatus: document.getElementById('fMediumStatus').value,
    type: document.getElementById('fType').value,
    search: document.getElementById('fSearch').value.trim().toLowerCase(),
  };
}

// '—'/'?' are "unknown", not values — they must sink regardless of sort direction,
// so they are handled outside the sortAsc flip.
const norm = v => (v == null || v === '—' || v === '' || v === '?') ? null : String(v);
const cmpTitle = (a, b) => String(a.title ?? '').localeCompare(String(b.title ?? ''));

function render() {
  const f = currentFilters();
  let rows = ROWS.filter(r => {
    if (f.week && r.week !== f.week) return false;
    if (f.niche && r.niche !== f.niche) return false;
    if (f.mediumStatus && r['medium.status'] !== f.mediumStatus) return false;
    if (f.type === 'orphan' && !r._orphan) return false;
    if (f.type === 'piece' && r._orphan) return false;
    if (f.search) {
      const hay = (r.slug + ' ' + r.title + ' ' + r.notes).toLowerCase();
      if (!hay.includes(f.search)) return false;
    }
    return true;
  });
  if (sortKey) {
    rows = rows.slice().sort((a, b) => {
      const av = norm(a[sortKey]), bv = norm(b[sortKey]);
      if (av === null && bv === null) return cmpTitle(a, b);
      if (av === null) return 1;
      if (bv === null) return -1;
      const c = av.localeCompare(bv);
      return c ? (sortAsc ? c : -c) : cmpTitle(a, b);
    });
  }
  renderHead();
  const cols = visibleColumns();
  const body = document.getElementById('bodyRows');
  body.innerHTML = '';
  for (const r of rows) {
    const tr = document.createElement('tr');
    if (r._flagged) tr.className = 'flagged';
    for (const [key] of cols) {
      const td = document.createElement('td');
      td.dataset.key = key;
      if (AUTO_KEYS.has(key)) td.dataset.auto = '1';
      const val = r[key] ?? '—';

      // Try to render an editor for editable cells. `flags` is editable in the
      // schema but holds long diagnostic prose — an input truncates it, so it
      // stays a read-only clamped badge.
      if (LIVE && EDITABLE_SET.has(key) && key !== 'flags') {
        const editor = renderEditor(key, val, r);
        if (editor) {
          td.appendChild(editor);
          tr.appendChild(td);
          continue;
        }
      }

      // Fall back to static HTML
      td.innerHTML = cellHtml(key, val, r);
      tr.appendChild(td);
    }
    body.appendChild(tr);
  }
  document.getElementById('summary').textContent =
    rows.length + ' of ' + ROWS.length + ' rows shown · ' +
    ROWS.filter(r => r._flagged).length + ' flagged · ' +
    ROWS.filter(r => r._orphan).length + ' orphans · ' +
    cols.length + ' of ' + COLUMNS.length + ' columns';
}

document.getElementById('bodyRows').addEventListener('click', e => {
  const td = e.target.closest('td[data-key="notes"], td[data-key="flags"], td[data-key="title"]');
  if (td) td.classList.toggle('expanded');
});

for (const id of ['fWeek', 'fNiche', 'fMediumStatus', 'fType']) {
  document.getElementById(id).addEventListener('change', render);
}
document.getElementById('fSearch').addEventListener('input', render);

// ── cell editing ──────────────────────────────────────────────────────────────
const LIVE = location.protocol.startsWith('http');
const EDITABLE_SET = new Set(__EDITABLE_JSON__);
const ENUMS_MAP = __ENUMS_JSON__;
const URL_FIELDS_SET = new Set(__URL_FIELDS_JSON__);
const DATE_FIELDS_SET = new Set(__DATE_FIELDS_JSON__);

// Same objects as ROWS, not copies: render() reads ROWS, so a saved edit written only
// to a copy would silently revert on the next sort/filter.
const ROWS_BY_SLUG = Object.fromEntries(ROWS.map(r => [r.slug, r]));

function updateRowCell(slug, key, newValue) {
  if (ROWS_BY_SLUG[slug]) {
    ROWS_BY_SLUG[slug][key] = newValue;
  }
}

function flashCell(cell, success) {
  cell.classList.add(success ? 'cell-flash' : 'cell-error');
  setTimeout(() => cell.classList.remove(success ? 'cell-flash' : 'cell-error'), 400);
  if (success) cell.removeAttribute('title');
}

// Errors surface on the cell, never in a modal: a dialog blocks every later
// interaction, and a spreadsheet should not stop the world to report a typo.
function cellError(cell, msg) {
  flashCell(cell, false);
  cell.title = msg;
}

function revealNewPubInput(select, slug, niche, previousValue) {
  const cell = select.closest('td');
  const input = document.createElement('input');
  input.type = 'text';
  input.className = 'cell-editor';
  input.dataset.key = 'medium.pub';
  input.dataset.slug = slug;
  input.value = '';
  input.dataset.previousValue = previousValue;

  function revert(showValue) {
    const v = showValue === undefined ? previousValue : showValue;
    cell.innerHTML = '';
    const newSelect = renderEditor('medium.pub', v === '' ? '—' : v, ROWS_BY_SLUG[slug]);
    if (newSelect) cell.appendChild(newSelect);
  }

  // Enter fires the save, and the resulting revert() blurs the input — without this
  // guard the blur handler submits a second time with a now-stale `expected` and the
  // successful save reports a bogus 409.
  let submitted = false;

  function saveNewPub() {
    if (submitted) return;
    const newValue = input.value.trim();
    if (!newValue) {
      revert();
      return;
    }
    submitted = true;
    input.disabled = true;
    fetch('/api/tracker-field', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({slug, field: 'medium.pub', value: newValue, expected: previousValue === '' ? '—' : previousValue}),
    })
    .then(res => res.json().then(data => ({status: res.status, data})))
    .then(({status, data}) => {
      if (status === 200) {
        updateRowCell(slug, 'medium.pub', data.new || '—');
        if (niche in PUBS && !PUBS[niche].includes(newValue)) {
          PUBS[niche].push(newValue);
          PUBS[niche].sort();
        }
        flashCell(cell, true);
        revert();
      } else if (status === 409) {
        const onDisk = data.current || previousValue;
        updateRowCell(slug, 'medium.pub', onDisk);
        cellError(cell, 'changed on disk to "' + onDisk + '" — your edit was not applied');
        revert(onDisk);
      } else {
        cellError(cell, data.error || 'save failed');
        revert();
      }
    })
    .catch(err => {
      cellError(cell, 'network error: ' + err);
      revert();
    });
  }

  cell.innerHTML = '';
  cell.appendChild(input);
  input.focus();

  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      saveNewPub();
    } else if (e.key === 'Escape') {
      submitted = true;   // Escape abandons the edit; blur must not resurrect it
      revert();
    }
  });

  input.addEventListener('blur', () => {
    setTimeout(() => {
      if (!submitted && document.activeElement !== input) {
        saveNewPub();
      }
    }, 50);
  });
}

function renderEditor(key, value, row) {
  if (!LIVE || !EDITABLE_SET.has(key)) return null;

  value = value === '—' ? '' : value;

  if (key === 'medium.pub') {
    const select = document.createElement('select');
    select.className = 'cell-editor';
    select.dataset.key = key;
    select.dataset.slug = row.slug;
    select.dataset.originalValue = value;

    // (unset) option
    const unsetOpt = document.createElement('option');
    unsetOpt.value = '—';
    unsetOpt.textContent = '(unset)';
    if (value === '') unsetOpt.selected = true;
    select.appendChild(unsetOpt);

    // pubs for this niche
    const niche = row.niche;
    const pubList = PUBS[niche] || [];
    for (const pub of pubList) {
      const opt = document.createElement('option');
      opt.value = pub;
      opt.textContent = pub;
      if (pub === value) opt.selected = true;
      select.appendChild(opt);
    }

    // current value if not in list
    if (value && !pubList.includes(value) && value !== '') {
      const opt = document.createElement('option');
      opt.value = value;
      opt.textContent = value;
      opt.selected = true;
      select.appendChild(opt);
    }

    // "+ New publication…" escape hatch
    const newOpt = document.createElement('option');
    newOpt.value = '__NEW_PUB__';
    newOpt.textContent = '+ New publication…';
    select.appendChild(newOpt);

    select.addEventListener('change', e => {
      if (e.target.value === '__NEW_PUB__') {
        revealNewPubInput(select, row.slug, row.niche, value);
      } else {
        saveCell(e.target);
      }
    });

    return select;
  }

  if (key in ENUMS_MAP) {
    const select = document.createElement('select');
    select.className = 'cell-editor';
    select.dataset.key = key;
    select.dataset.slug = row.slug;
    for (const opt of ENUMS_MAP[key]) {
      const option = document.createElement('option');
      option.value = opt;
      option.textContent = opt === '—' ? '(unset)' : opt;
      if (opt === (value === '' ? '—' : value)) option.selected = true;
      select.appendChild(option);
    }
    select.addEventListener('change', e => saveCell(e.target));
    return select;
  }

  const input = document.createElement('input');
  input.type = 'text';
  input.className = 'cell-editor';
  input.dataset.key = key;
  input.dataset.slug = row.slug;
  input.value = value;
  input.addEventListener('blur', () => saveCell(input));
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') saveCell(input);
  });
  return input;
}

function saveCell(editor) {
  const slug = editor.dataset.slug;
  const key = editor.dataset.key;
  const newValue = editor.value;
  const oldValue = ROWS_BY_SLUG[slug] ? ROWS_BY_SLUG[slug][key] : '—';
  const expected = oldValue === '—' ? '—' : oldValue;

  if (newValue === (oldValue === '—' ? '' : oldValue)) {
    return; // no change
  }

  const cell = editor.closest('td');
  editor.disabled = true;

  fetch('/api/tracker-field', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({slug, field: key, value: newValue, expected}),
  })
  .then(res => res.json().then(data => ({status: res.status, data})))
  .then(({status, data}) => {
    if (status === 200) {
      updateRowCell(slug, key, data.new || '—');
      flashCell(cell, true);
      if (editor.tagName === 'INPUT') {
        editor.value = data.new === '—' ? '' : data.new;
      } else {
        const idx = [...editor.options].findIndex(o => o.value === (data.new || '—'));
        if (idx >= 0) editor.selectedIndex = idx;
      }
    } else if (status === 409) {
      flashCell(cell, false);
      const onDisk = data.current || '—';
      updateRowCell(slug, key, onDisk);
      if (editor.tagName === 'INPUT') {
        editor.value = onDisk === '—' ? '' : onDisk;
      } else {
        editor.value = onDisk;
      }
      editor.dataset.originalValue = onDisk;
      cellError(cell, 'changed on disk to "' + onDisk + '" — your edit was not applied');
    } else {
      cellError(cell, data.error || 'save failed');
      // a rejected value must not stay on screen — revert the control either way
      editor.value = editor.tagName === 'INPUT' && oldValue === '—' ? '' : oldValue;
    }
  })
  .catch(err => {
    cellError(cell, 'network error: ' + err);
    editor.value = editor.tagName === 'INPUT' && oldValue === '—' ? '' : oldValue;
  })
  .finally(() => {
    editor.disabled = false;
  });
}

// Note button handler. Capture phase + stopPropagation so adding a note never
// also toggles the cell's clamp/expand.
document.getElementById('bodyRows').addEventListener('click', e => {
  const btn = e.target.closest('.notebtn');
  if (btn) {
    e.stopPropagation();
    const slug = btn.dataset.slug;
    const text = prompt('Add a note:');
    if (text && text.trim()) {
      fetch('/api/tracker-note', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({slug, text}),
      })
      .then(res => res.json().then(data => ({status: res.status, data})))
      .then(({status, data}) => {
        const cell = btn.closest('td');
        if (status === 200) {
          // append in place — reloading would discard sort, filters and column choices
          const row = ROWS_BY_SLUG[slug];
          const appended = data.appended || text.trim();
          row.notes = row.notes && row.notes !== '—' ? row.notes + '\\n' + appended : appended;
          updateRowCell(slug, 'notes', row.notes);
          render();
        } else {
          cellError(cell, data.error || 'note failed');
        }
      })
      .catch(err => cellError(btn.closest('td'), 'network error: ' + err));
    }
  }
}, true);

buildColPanel();
buildSortSelect();
render();
</script>
</body>
</html>
"""


def parse_publications(text: str, records: list[dict]) -> dict[str, list[str]]:
    ruled = set()
    sec = re.search(r"^## Publications ruled out.*?$(.*?)^(?:>|## )", text, re.S | re.M)
    if sec:
        ruled = {m.group(1).strip() for m in re.finditer(r"^- \*\*(.+?)\*\*", sec.group(1), re.M)}

    labels = {"DS/Tech": "ds", "Life": "life", "Poetry": "poetry"}
    pubs: dict[str, list[str]] = {"ds": [], "life": [], "poetry": []}
    sec = re.search(r"^## Homes secured per niche.*?$(.*?)^## ", text, re.S | re.M)
    if sec:
        for line in sec.group(1).split("\n"):
            m = re.match(r"^- \*\*(.+?):\*\*\s*(.*)$", line)
            if not m or m.group(1) not in labels:
                continue
            niche = labels[m.group(1)]
            body = m.group(2)
            # italic notes must go FIRST — one of them contains an em dash
            # ("AI in Plain English ✓ *(…PUBLISHED 06-30 — network home…)*"), and splitting
            # on " — " before stripping them truncates the list mid-entry.
            body = re.sub(r"\*\([^)]*\)\*", "", body)
            body = body.split(" — ")[0]
            for name in re.split(r"[,·]", body):
                name = name.replace("✓", "").replace("*", "").strip().rstrip(".")
                if name and name not in ruled:
                    pubs[niche].append(name)

    # a pub already used on a record is valid for that record's niche — this is what makes
    # a newly-typed publication appear in the dropdown on the next regen, with no extra list
    for r in records:
        p, n = r["medium.pub"], r["niche"]
        if p != DASH and n in pubs and p not in pubs[n]:
            pubs[n].append(p)

    return {k: sorted(v) for k, v in pubs.items()}


def render_html(rows: list[dict[str, str]], pubs: dict[str, list[str]]) -> str:
    def blob(value: object) -> str:
        # bound the injected JSON to its <script> block — no unescaped "</script>"
        return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")

    page = PAGE_TEMPLATE
    for placeholder, value in (
        ("__COLUMNS_JSON__", COLUMNS),
        ("__ROWS_JSON__", rows),
        ("__HIDDEN_JSON__", sorted(HIDDEN_BY_DEFAULT)),
        ("__AUTO_JSON__", list(AUTO_COLUMNS)),
        ("__DEFAULT_SORT_JSON__", DEFAULT_SORT_KEY),
        ("__EDITABLE_JSON__", list(EDITABLE)),
        ("__ENUMS_JSON__", ENUMS),
        ("__URL_FIELDS_JSON__", list(URL_FIELDS)),
        ("__DATE_FIELDS_JSON__", list(DATE_FIELDS)),
        ("__PUBS_JSON__", pubs),
    ):
        page = page.replace(placeholder, blob(value))
    return page


# ── self-check ──────────────────────────────────────────────────────────────

def demo() -> None:
    good_md = """## 2026-07-17_life_self_dev_understanding-who-truly-cares-a-guide-to-valuing-real-connec
title:            The Person You're Begging To Notice You Isn't The Problem
week:             W29
niche:            life
date:             2026-07-17
medium.pub:       —
medium.status:    —
medium.submitted: —
medium.url:       https://medium.com/@tarun-gupta/9777e99b83ff
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         2026-07-17_life_self_dev_the-person-youre-begging-to-notice
reel.status:      script
reel.cta:         SYSTEM
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: none
worksheet.url:    —
source_draft:     34
flags:            —
notes: |
  line one
  line two

## ORPHAN:safe-and-alive
title:            Safe and Alive
week:             W20
niche:            life
date:             —
medium.pub:       Some Pub
medium.status:    published
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: none
worksheet.url:    —
source_draft:     —
flags:            ? pre-pipeline piece
notes: |
  verbatim
"""
    records, errors = parse_md(good_md)
    assert not errors, errors
    assert len(records) == 2
    assert records[0]["slug"] == "2026-07-17_life_self_dev_understanding-who-truly-cares-a-guide-to-valuing-real-connec"
    assert records[0]["notes"] == "line one\nline two"
    assert records[0]["medium.url"] == "https://medium.com/@tarun-gupta/9777e99b83ff"
    assert records[1]["slug"] == "ORPHAN:safe-and-alive"
    assert records[1]["flags"].startswith("?")

    bad_md = good_md + "\n## broken-block\ntitle: only one field\n"
    _, bad_errors = parse_md(bad_md)
    assert bad_errors, "expected a parse error for the broken block"
    assert any("broken-block" in e for e in bad_errors)

    # a title-less '##' block is reference prose: skipped, never an error...
    prose_md = good_md + """
---

## Publications ruled out (do not retry)
- **Better Humans** — not accepting new writers as of 2026-06-26.
- **HackerNoon** — off Medium.

## Homes secured per niche
- **DS/Tech:** DataDrivenInvestor, AI in Plain English ✓
- **Life:** Mind Cafe ✓, ILLUMINATION ✓
- **Poetry:** CRY Magazine, Other Doors

## Daily routine
Each day we produce blogs → I surface **3 new pubs**.
"""
    prose_records, prose_errors = parse_md(prose_md)
    assert not prose_errors, prose_errors
    assert len(prose_records) == 2, f"prose blocks must not become records: {len(prose_records)}"

    # ...but a title-bearing block still hard-errors even amid prose.
    _, mixed_errors = parse_md(prose_md + "\n## still-broken\ntitle: has a title but nothing else\n")
    assert any("still-broken" in e for e in mixed_errors), mixed_errors

    keys = {c[0] for c in COLUMNS}
    unknown = HIDDEN_BY_DEFAULT - keys
    assert not unknown, f"HIDDEN_BY_DEFAULT names columns that do not exist: {unknown}"
    assert DEFAULT_SORT_KEY in keys, f"DEFAULT_SORT_KEY {DEFAULT_SORT_KEY!r} is not a column"
    assert all(len(c) == 3 and c[2] for c in COLUMNS), "every COLUMNS entry needs a non-empty group"
    assert set(AUTO_COLUMNS) <= keys, "AUTO_COLUMNS must all be real columns"

    # test parse_publications
    pubs = parse_publications(prose_md, records)
    assert all(len(pubs[n]) > 0 for n in ["ds", "life", "poetry"]), "every niche must have >= 1 pub"
    ruled_set = {"Better Humans", "The Ascent", "Poets Unlimited", "The Junction", "Scribe",
                 "Data Science Collective", "HackerNoon", "Curious", "Be Yourself", "AI Advances",
                 "zipBoard", "The Personal Growth Project", "Practice in Public"}
    for niche, pubs_list in pubs.items():
        for pub in pubs_list:
            assert pub not in ruled_set, f"ruled-out pub {pub!r} leaked into {niche} list"

    page = render_html([{**records[0], "_flagged": False, "_orphan": False}], pubs)
    for placeholder in ("__COLUMNS_JSON__", "__ROWS_JSON__", "__HIDDEN_JSON__",
                        "__AUTO_JSON__", "__DEFAULT_SORT_JSON__",
                        "__EDITABLE_JSON__", "__ENUMS_JSON__", "__URL_FIELDS_JSON__", "__DATE_FIELDS_JSON__",
                        "__PUBS_JSON__"):
        assert placeholder not in page, f"unsubstituted placeholder {placeholder}"


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--md", type=Path, default=DEFAULT_MD, help="source content-tracker.md")
    ap.add_argument("--out", type=Path, default=DEFAULT_HTML, help="output HTML path")
    ap.add_argument("--selfcheck", action="store_true", help="run the assert-based self-check and exit")
    args = ap.parse_args(argv)

    if args.selfcheck:
        demo()
        print("self-check OK")
        return 0

    if not args.md.exists():
        print(f"error: MD source not found: {args.md}", file=sys.stderr)
        return 1

    text = args.md.read_text(encoding="utf-8")
    records, errors = parse_md(text)
    if errors:
        for e in errors:
            print(f"PARSE ERROR: {e}", file=sys.stderr)
        return 1

    rows: list[dict[str, str]] = []
    n_missing = 0
    n_flags = 0
    for rec in records:
        auto = compute_auto(rec)
        n_missing += sum(1 for v in auto.values() if v == DASH)
        row = {**rec, **auto}
        row["_flagged"] = is_flagged(rec, auto)
        row["_orphan"] = rec["slug"].startswith(ORPHAN_PREFIX)
        if row["_flagged"]:
            n_flags += 1
        rows.append(row)

    pubs = parse_publications(text, records)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render_html(rows, pubs), encoding="utf-8")

    print(f"records parsed: {len(records)}")
    print(f"rows emitted: {len(rows)}")
    print(f"missing artifacts: {n_missing}")
    print(f"flagged rows: {n_flags}")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
