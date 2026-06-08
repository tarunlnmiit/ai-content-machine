#!/usr/bin/env python3
"""
Generate a week-N-publishing-checklist.md from schedule.json files.

Usage:
  python3 scripts/generate_checklist.py --week 2026-06-09
  → docs/week-2026-06-09-publishing-checklist.md
"""

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).parent.parent
IST = timezone(timedelta(hours=5, minutes=30))


def parse_week_start(week_str: str) -> datetime:
    """Parse YYYY-MM-DD as Monday 00:00 IST. If not Monday, error."""
    dt = datetime.fromisoformat(week_str).replace(tzinfo=IST)
    if dt.weekday() != 0:
        raise ValueError(f"{week_str} is not a Monday. Please provide a Monday date.")
    return dt


def get_week_bounds(week_start: datetime) -> tuple[datetime, datetime]:
    """Return (Mon 00:00, Sun 23:59:59) IST for the week."""
    week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return week_start, week_end


def find_slugs_for_week(week_start: datetime, week_end: datetime) -> dict[str, dict]:
    """
    Find all schedule.json files with long_form.publish_at in [week_start, week_end].
    Returns dict mapping slug -> schedule data.
    """
    slugs_found = {}
    deriv_dir = REPO / "content" / "derivatives"
    if not deriv_dir.exists():
        return slugs_found

    for slug_dir in deriv_dir.iterdir():
        if not slug_dir.is_dir():
            continue
        schedule_file = slug_dir / "schedule.json"
        if not schedule_file.exists():
            continue

        try:
            sched_data = json.loads(schedule_file.read_text(encoding="utf-8"))
            lf_publish_str = sched_data.get("long_form", {}).get("publish_at")
            if not lf_publish_str:
                continue
            lf_publish = datetime.fromisoformat(lf_publish_str)
            if week_start <= lf_publish <= week_end:
                slugs_found[slug_dir.name] = sched_data
        except (json.JSONDecodeError, ValueError):
            continue

    return slugs_found


def niche_from_schedule(sched: dict) -> str:
    """Extract niche from schedule.json."""
    return sched.get("niche", "unknown")


def format_iso_to_human(iso_str: str) -> str:
    """Convert 2026-06-12T18:00:00+05:30 to 'Jun 12, 6 PM IST'."""
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%b %d, %-I %p IST").replace("AM", "AM").replace("PM", "PM")
    except ValueError:
        return iso_str


def generate_checklist_content(week_start: datetime, slugs_by_week: dict[str, dict]) -> str:
    """
    Generate checklist markdown. Slugs are already filtered to fall in [week_start, week_start + 7 days).
    """
    week_end = week_start + timedelta(days=6)
    week_str = f"{week_start.strftime('%b %d')}–{week_end.strftime('%b %d, %Y')}".replace(" 0", " ")
    next_week_start = week_start + timedelta(days=7)

    lines = [
        f"# Week {week_start.strftime('%Y-%m-%d')} Publishing Checklist",
        f"**Week: {week_str}**",
        "",
        "---",
        "",
        "## Schedule Reference",
        "",
        "### Long-form, blogs, social",
        "",
        "| Content | Platform | Day | Time IST |",
        "|---------|----------|-----|----------|",
    ]

    # Organize by niche
    by_niche = {}
    for slug, sched in slugs_by_week.items():
        niche = niche_from_schedule(sched)
        if niche not in by_niche:
            by_niche[niche] = []
        by_niche[niche].append((slug, sched))

    # Schedule rows
    niche_order = ["ds", "life", "poetry"]
    for niche in niche_order:
        if niche not in by_niche:
            continue
        for slug, sched in by_niche[niche]:
            lf_publish_str = sched.get("long_form", {}).get("publish_at", "")
            lf_dt = datetime.fromisoformat(lf_publish_str) if lf_publish_str else None
            if not lf_dt:
                continue

            # Long-form row
            lf_channel = sched.get("long_form", {}).get("channel", "")
            day_name = lf_dt.strftime("%a %b %d")
            time_str = lf_dt.strftime("%-I:%M %p").replace("AM", "AM").replace("PM", "PM")
            niche_emoji = {"ds": "🔵", "life": "🟢", "poetry": "🟣"}.get(niche, "")
            lines.append(
                f"| {niche_emoji} {niche.replace('_', ' ').title()} Video (long-form) + Blog + Newsletter | "
                f"YouTube / Substack+Medium / Beehiiv | {day_name} | {time_str} |"
            )

            # LinkedIn
            li_publish_str = sched.get("social", {}).get("linkedin_publish_at", "")
            li_dt = datetime.fromisoformat(li_publish_str) if li_publish_str else None
            if li_dt:
                li_day = li_dt.strftime("%a %b %d")
                li_time = li_dt.strftime("%-I:%M %p").replace("AM", "AM").replace("PM", "PM")
                lines.append(
                    f"| {niche_emoji} {niche.replace('_', ' ').title()} LinkedIn post | LinkedIn | {li_day} | {li_time} |"
                )

            # Twitter
            tw_publish_str = sched.get("social", {}).get("twitter_publish_at", "")
            tw_dt = datetime.fromisoformat(tw_publish_str) if tw_publish_str else None
            if tw_dt:
                tw_day = tw_dt.strftime("%a %b %d")
                tw_time = tw_dt.strftime("%-I:%M %p").replace("AM", "AM").replace("PM", "PM")
                lines.append(
                    f"| {niche_emoji} {niche.replace('_', ' ').title()} Twitter thread | Twitter/X | {tw_day} | {tw_time} |"
                )

    lines += [
        "",
        "---",
        "",
        "## Next steps",
        "",
        "Run from project root: `cd \"/Users/tarungupta/Making It Big/Claude/content-machine\"`",
        "",
        "1. **YouTube uploads:** Upload long-form videos with `--publish-at` matching schedule above.",
        "2. **Blog/Substack/Medium:** Publish blogs at scheduled times.",
        "3. **LinkedIn:** Posts auto-queue via scheduler.py.",
        "4. **Social (week after):** Import Metricool CSVs in the following week.",
        "",
        "---",
        "",
        "## Notes",
        "",
        f"- Social posts (IG, FB, Threads) schedule to the week of {next_week_start.strftime('%b %d–%b %d, %Y').replace(' 0', ' ')} (one week after long-form).",
        "- YouTube shorts use the slot-based schedule from the dashboard.",
        "- Check `content/derivatives/{slug}/schedule.json` for detailed timing.",
    ]

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate week publishing checklist from schedule.json files.")
    parser.add_argument("--week", required=True, help="Week start date (YYYY-MM-DD, must be Monday)")
    args = parser.parse_args()

    try:
        week_start = parse_week_start(args.week)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    week_start_utc, week_end_utc = get_week_bounds(week_start)

    # Find all slugs with schedule.json in this week
    slugs_for_week = find_slugs_for_week(week_start_utc, week_end_utc)

    if not slugs_for_week:
        print(f"No schedule.json files found for week {args.week}.")
        return 1

    print(f"Found {len(slugs_for_week)} content piece(s) for week {args.week}:")
    for slug in slugs_for_week:
        print(f"  - {slug}")

    # Generate checklist
    checklist_content = generate_checklist_content(week_start, slugs_for_week)

    # Write to docs/
    output_path = REPO / "docs" / f"week-{args.week}-publishing-checklist.md"
    output_path.write_text(checklist_content, encoding="utf-8")
    print(f"\nChecklist written to: {output_path.relative_to(REPO)}")

    return 0


if __name__ == "__main__":
    exit(main())
