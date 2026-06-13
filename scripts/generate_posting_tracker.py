#!/usr/bin/env python3
"""
Generate an annual social media posting tracker spreadsheet.

Usage:
  python3 scripts/generate_posting_tracker.py              # current year
  python3 scripts/generate_posting_tracker.py --year 2026
"""

import argparse
import datetime
import json
import os
import sys
from collections import defaultdict

try:
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
except ImportError:
    print("Error: openpyxl not installed. Run: pip install openpyxl")
    sys.exit(1)


# ── Colors ────────────────────────────────────────────────────────────────────
NICHE_COLORS = {"DS": "DDEEFF", "Life": "DDFFDD", "Poetry": "EED9FF"}
HEADER_BG    = "2D3748"
SUBHDR_BG    = "E2E8F0"

DAYS     = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAY_NUM  = {d: i + 1 for i, d in enumerate(DAYS)}  # 1=Mon … 7=Sun (ISO)
MONTHS   = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

NICHE_MARKERS = {
    "_data_science_tech_": "DS",
    "_life_self_dev_":     "Life",
    "_poetry_quotes_":     "Poetry",
}


# ── Schedule ──────────────────────────────────────────────────────────────────

LONGFORM_PLATFORMS = [
    ("DS",     "Medium",  "Article"),
    ("DS",     "YouTube", "Video"),
    ("Life",   "Medium",  "Article"),
    ("Life",   "YouTube", "Video"),
    ("Poetry", "Medium",  "Article"),
    ("Poetry", "YouTube", "Video"),
]

# (day, time, niche, platform, format)
WEEKLY = [
    # Monday
    ("Mon", "08:00 AM", "DS",     "LinkedIn",     "Post"),
    ("Mon", "12:00 PM", "DS",     "Twitter",      "Post"),
    ("Mon", "04:00 PM", "DS",     "FB/IG",        "Carousel"),
    ("Mon", "06:00 PM", "DS",     "LinkedIn",     "Poll"),
    ("Mon", "07:00 PM", "Life",   "Meta Threads", "Native Text Post"),
    # Tuesday
    ("Tue", "08:00 AM", "Life",   "LinkedIn",     "Post"),
    ("Tue", "12:00 PM", "DS",     "Twitter",      "Poll (manual)"),
    ("Tue", "06:00 PM", "Life",   "LinkedIn",     "Poll"),
    ("Tue", "08:30 PM", "Poetry", "FB/IG",        "Post"),
    ("Tue", "09:00 PM", "DS",     "Twitter",      "Twitter Thread"),
    # Wednesday
    ("Wed", "06:00 AM", "DS",     "LinkedIn",     "Slide Deck"),
    ("Wed", "06:00 AM", "Poetry", "FB/IG",        "Carousel"),
    ("Wed", "08:00 AM", "Poetry", "LinkedIn",     "Post"),
    ("Wed", "12:00 PM", "Life",   "Twitter",      "Post"),
    ("Wed", "06:00 PM", "Poetry", "LinkedIn",     "Poll"),
    ("Wed", "08:00 PM", "DS",     "Meta Threads", "Native Text Post"),
    # Thursday
    ("Thu", "08:00 AM", "Life",   "LinkedIn",     "Slide Deck"),
    ("Thu", "10:00 AM", "Life",   "FB/IG",        "Carousel"),
    ("Thu", "12:00 PM", "Life",   "Twitter",      "Poll (manual)"),
    ("Thu", "07:00 PM", "Poetry", "Meta Threads", "Native Text Post"),
    ("Thu", "09:00 PM", "Life",   "Twitter",      "Twitter Thread"),
    # Friday
    ("Fri", "08:00 AM", "Poetry", "LinkedIn",     "Slide Deck"),
    ("Fri", "10:00 AM", "Life",   "FB/IG",        "Post"),
    ("Fri", "12:00 PM", "Poetry", "Twitter",      "Post"),
    # Saturday
    ("Sat", "02:00 PM", "DS",     "FB/IG",        "Post"),
    ("Sat", "09:00 PM", "Poetry", "Twitter",      "Twitter Thread"),
    ("Sat", "12:00 PM", "Poetry", "Twitter",      "Poll (manual)"),
]

# (platform, time, niche, format) — repeated every day Mon–Sun
DAILY = [
    # FB/IG
    ("FB/IG",        "07:00 AM", "Life",   "Clip Short Reel"),
    ("FB/IG",        "09:00 AM", "DS",     "Remotion Reel"),
    ("FB/IG",        "10:00 AM", "Poetry", "Remotion Reel"),
    ("FB/IG",        "09:00 PM", "DS",     "Clip Short Reel"),
    ("FB/IG",        "09:00 PM", "Life",   "Remotion Reel"),
    ("FB/IG",        "10:00 PM", "Poetry", "Clip Short Reel"),
    # LinkedIn
    ("LinkedIn",     "07:00 AM", "Life",   "Clip Short Reel"),
    ("LinkedIn",     "09:00 AM", "Poetry", "Clip Short Reel"),
    ("LinkedIn",     "10:00 AM", "DS",     "Clip Short Reel"),
    ("LinkedIn",     "06:00 PM", "Life",   "Remotion Reel"),
    ("LinkedIn",     "07:00 PM", "Poetry", "Remotion Reel"),
    ("LinkedIn",     "08:00 PM", "DS",     "Remotion Reel"),
    # Twitter
    ("Twitter",      "11:00 AM", "DS",     "Clip Short Reel"),
    ("Twitter",      "01:00 PM", "Life",   "Clip Short Reel"),
    ("Twitter",      "02:00 PM", "Poetry", "Clip Short Reel"),
    ("Twitter",      "07:00 PM", "DS",     "Remotion Reel"),
    ("Twitter",      "08:00 PM", "Life",   "Remotion Reel"),
    ("Twitter",      "09:00 PM", "Poetry", "Remotion Reel"),
]


# ── Title loading ─────────────────────────────────────────────────────────────

def detect_niche(slug):
    for marker, niche in NICHE_MARKERS.items():
        if marker in slug:
            return niche
    return None

def slug_to_title(slug):
    for marker in NICHE_MARKERS:
        if marker in slug:
            idx = slug.index(marker) + len(marker)
            return slug[idx:].replace("-", " ").title()
    return slug.replace("-", " ").title()

def load_titles(year, repo_root):
    """Return {(iso_week, niche): title} from youtube_metadata.json files."""
    titles = {}
    deriv_dir = os.path.join(repo_root, "content", "derivatives")
    if not os.path.isdir(deriv_dir):
        return titles
    for week_dir in os.listdir(deriv_dir):
        if not week_dir.startswith(f"{year}-W"):
            continue
        wk = int(week_dir.split("-W")[1])
        week_path = os.path.join(deriv_dir, week_dir)
        for slug in os.listdir(week_path):
            niche = detect_niche(slug)
            if not niche:
                continue
            meta_path = os.path.join(week_path, slug, "youtube_metadata.json")
            if os.path.exists(meta_path):
                with open(meta_path, encoding="utf-8") as f:
                    data = json.load(f)
                title = data.get("title", "").strip()
            else:
                title = slug_to_title(slug)
            if title:
                titles[(wk, niche)] = title
    return titles


# ── Row generation ────────────────────────────────────────────────────────────

def time_minutes(t):
    dt = datetime.datetime.strptime(t, "%I:%M %p")
    return dt.hour * 60 + dt.minute

def max_iso_week(year):
    return datetime.date(year, 12, 28).isocalendar().week

def week_label(week):
    return f"W{week:02d}"

def make_rows(year, titles):
    """
    Return list of row dicts, one per posting slot, for the entire year.
    Each dict: date, iso_week, day, time, niche, platform, format, title, status
    """
    rows = []
    max_wk = max_iso_week(year)

    for wk in range(21, max_wk + 1):
        wl = week_label(wk)
        mon_date = datetime.date.fromisocalendar(year, wk, 1)

        # Titles for this week — direct mapping (user fills future weeks as content is produced)
        week_titles = {n: titles.get((wk, n), "") for n in ("DS", "Life", "Poetry")}

        # Long-form rows (date = Monday of this week, time = "—")
        for niche, platform, fmt in LONGFORM_PLATFORMS:
            date = mon_date
            if date.year != year:
                continue
            rows.append({
                "date":     date,
                "iso_week": wl,
                "day":      "Mon",
                "time":     "—",
                "niche":    niche,
                "platform": platform,
                "format":   fmt,
                "title":    week_titles[niche],
                "status":   "Idea",
            })

        # Weekly-specific rows
        for day, time_str, niche, platform, fmt in WEEKLY:
            date = datetime.date.fromisocalendar(year, wk, DAY_NUM[day])
            if date.year != year:
                continue
            rows.append({
                "date":     date,
                "iso_week": wl,
                "day":      day,
                "time":     time_str,
                "niche":    niche,
                "platform": platform,
                "format":   fmt,
                "title":    week_titles[niche],
                "status":   "Idea",
            })

        # Daily rows (Mon–Sun)
        for day in DAYS:
            date = datetime.date.fromisocalendar(year, wk, DAY_NUM[day])
            if date.year != year:
                continue
            for platform, time_str, niche, fmt in DAILY:
                rows.append({
                    "date":     date,
                    "iso_week": wl,
                    "day":      day,
                    "time":     time_str,
                    "niche":    niche,
                    "platform": platform,
                    "format":   fmt,
                    "title":    week_titles[niche],
                    "status":   "Idea",
                })

    # Sort by date then time (— sorts before timed rows)
    rows.sort(key=lambda r: (r["date"], r["time"] == "—", r["time"]))
    return rows


# ── Spreadsheet writer ────────────────────────────────────────────────────────

def niche_fill(niche):
    return PatternFill("solid", fgColor=NICHE_COLORS.get(niche, "FFFFFF"))

def solid_fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def bold_white(size=10):
    return Font(bold=True, color="FFFFFF", size=size)

def bold_dark(size=10):
    return Font(bold=True, color="1A202C", size=size)

HEADERS = ["ISO Week", "Day", "Date", "Time", "Niche", "Platform", "Format",
           "Content Title", "Status", "✓"]
COL_WIDTHS = [9, 6, 13, 11, 8, 15, 22, 48, 14, 4]

STATUS_OPTIONS = "Idea,In Progress,Editing,Published"


def write_sheet(ws, month_rows, year, month_idx):
    ws.freeze_panes = "A2"

    # Header
    for col, (h, w) in enumerate(zip(HEADERS, COL_WIDTHS), 1):
        c = ws.cell(row=1, column=col, value=h)
        c.font  = bold_white()
        c.fill  = solid_fill(HEADER_BG)
        c.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[get_column_letter(col)].width = w
    ws.row_dimensions[1].height = 18

    # Data rows
    for r_idx, row in enumerate(month_rows, start=2):
        fill = niche_fill(row["niche"])
        vals = [
            row["iso_week"],
            row["day"],
            row["date"].strftime("%-d %b %Y"),
            row["time"],
            row["niche"],
            row["platform"],
            row["format"],
            row["title"],
            row["status"],
            "",
        ]
        for col, val in enumerate(vals, 1):
            c = ws.cell(row=r_idx, column=col, value=val)
            c.fill = fill

    last_row = len(month_rows) + 1

    # AutoFilter
    ws.auto_filter.ref = f"A1:J{last_row}"

    # Status dropdown (col I = 9)
    dv = DataValidation(
        type="list",
        formula1=f'"{STATUS_OPTIONS}"',
        allow_blank=True,
        showDropDown=False,  # False = show the dropdown arrow
    )
    ws.add_data_validation(dv)
    dv.sqref = f"I2:I{last_row}"


def write_annual_tracker(year, repo_root):
    titles = load_titles(year, repo_root)
    all_rows = make_rows(year, titles)

    # Group by month
    by_month = defaultdict(list)
    for row in all_rows:
        by_month[row["date"].month].append(row)

    wb = Workbook()
    wb.remove(wb.active)  # remove default sheet

    for m in range(1, 13):
        month_rows = by_month.get(m, [])
        if not month_rows:
            continue
        ws = wb.create_sheet(title=MONTHS[m - 1])
        write_sheet(ws, month_rows, year, m)

    out_dir  = os.path.join(repo_root, "output", "trackers")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"annual-tracker-{year}.xlsx")
    wb.save(out_path)
    print(f"Saved → {out_path}")
    print(f"  Rows: {len(all_rows)} across 12 monthly sheets")
    print(f"  Content titles loaded: {len(titles)}")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Generate annual posting tracker")
    parser.add_argument("--year", type=int, default=datetime.date.today().year)
    args = parser.parse_args()

    repo_root = os.path.join(os.path.dirname(__file__), "..")
    write_annual_tracker(args.year, os.path.abspath(repo_root))


if __name__ == "__main__":
    main()
