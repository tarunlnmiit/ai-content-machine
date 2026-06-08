#!/usr/bin/env python3
"""
Migrate all content/assets/output directories to ISO-week subfolder structure.

Usage:
    python3 scripts/migrate_to_weekly.py --dry-run  # Default: show what would happen
    python3 scripts/migrate_to_weekly.py --live     # Perform actual migration
"""

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

# Add project root to path
REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO))

from scripts.lib.schedule_calc import get_iso_week, DATE_RE

# Regex to check if a folder is already migrated (ISO week pattern)
WEEK_PATTERN = re.compile(r"^\d{4}-W\d{2}$")


def extract_date_simple(name: str) -> str | None:
	"""Extract date from filename/dirname starting with YYYY-MM-DD."""
	match = DATE_RE.match(name)
	return match.group(1) if match else None


def extract_hyperframe_date(name: str) -> str | None:
	"""
	Extract content date from hyperframe filename.
	Files have inconsistent patterns; find the LATER date (content date, not render date).
	Examples:
	  2026-05-29_ds-2026-05-22_2026-05-21-data-science...
	  2026-05-30_2026-05-25_data_science_tech_python-for...
	  2026-05-25_2026-05-25-data-science-tech-python...
	Strategy: find all YYYY-MM-DD patterns, take the last one (typically content date).
	"""
	dates = DATE_RE.findall(name)
	if dates:
		# Return the last date found (usually the content date)
		return dates[-1]
	return None


def should_migrate(name: str) -> bool:
	"""Check if entry needs migration (not already in a YYYY-Wnn folder)."""
	return not WEEK_PATTERN.match(name)


def git_mv(src: Path, dest: Path, dry_run: bool = True) -> bool:
	"""Move file using git mv (LFS-safe). Returns True on success."""
	try:
		if dry_run:
			print(f"[DRY-RUN] git mv {src.relative_to(REPO)} → {dest.relative_to(REPO)}")
			return True
		else:
			subprocess.run(
				["git", "mv", str(src), str(dest)],
				cwd=REPO,
				check=True,
				capture_output=True,
			)
			print(f"[MIGRATED] {src.relative_to(REPO)} → {dest.relative_to(REPO)}")
			return True
	except subprocess.CalledProcessError as e:
		print(f"[ERROR] git mv failed: {e.stderr.decode()}", file=sys.stderr)
		return False


def migrate_directory(
	target_dir: Path,
	extract_date_fn=extract_date_simple,
	dry_run: bool = True,
	skip_dirs: bool = False,
) -> tuple[int, int]:
	"""
	Migrate all dated entries in target_dir into ISO-week subfolders.

	Args:
		target_dir: Directory to migrate
		extract_date_fn: Function to extract date from entry name
		dry_run: If True, print moves instead of executing
		skip_dirs: If True, only migrate files, not directories

	Returns:
		(migrated_count, skipped_count)
	"""
	if not target_dir.exists():
		print(f"[SKIP] {target_dir} does not exist", file=sys.stderr)
		return 0, 0

	migrated = 0
	skipped = 0

	for entry in sorted(target_dir.iterdir()):
		# Skip if already migrated (in a YYYY-Wnn folder)
		if not should_migrate(entry.name):
			continue

		# Skip if it's a directory and we're told to skip dirs
		if skip_dirs and entry.is_dir():
			continue

		date_str = extract_date_fn(entry.name)
		if not date_str:
			print(f"[SKIP] {entry.relative_to(REPO)} — no date found", file=sys.stderr)
			skipped += 1
			continue

		week_folder = target_dir / get_iso_week(date_str)
		week_folder.mkdir(exist_ok=True, parents=True)
		dest = week_folder / entry.name

		if git_mv(entry, dest, dry_run):
			migrated += 1
		else:
			skipped += 1

	return migrated, skipped


def migrate_buffer_directory(target_dir: Path, dry_run: bool = True) -> tuple[int, int]:
	"""
	Migrate content/buffer/ — flatten week-N/ structure.
	Files inside week-1/niche/*_*.md move to content/buffer/YYYY-Wnn/
	based on date extracted from the filename.
	"""
	if not target_dir.exists():
		print(f"[SKIP] {target_dir} does not exist", file=sys.stderr)
		return 0, 0

	migrated = 0
	skipped = 0

	# Recurse into week-1/, week-2/, week-3/
	for week_dir in target_dir.iterdir():
		if not week_dir.is_dir() or not week_dir.name.startswith("week-"):
			continue

		print(f"[BUFFER] Processing {week_dir.name}/", file=sys.stderr)

		# Recurse into niche subdirs
		for niche_dir in week_dir.iterdir():
			if not niche_dir.is_dir():
				continue

			# Iterate files inside niche_dir
			for entry in sorted(niche_dir.iterdir()):
				date_str = extract_date_simple(entry.name)
				if not date_str:
					print(
						f"[SKIP] {entry.relative_to(REPO)} — no date found",
						file=sys.stderr,
					)
					skipped += 1
					continue

				# Move to target_dir / YYYY-Wnn / entry.name
				iso_week = get_iso_week(date_str)
				iso_week_dir = target_dir / iso_week
				iso_week_dir.mkdir(exist_ok=True, parents=True)
				dest = iso_week_dir / entry.name

				if git_mv(entry, dest, dry_run):
					migrated += 1
				else:
					skipped += 1

		# After processing week_dir, try to remove it (should be empty now)
		if not dry_run:
			try:
				week_dir.rmdir()
				print(f"[REMOVED] {week_dir.relative_to(REPO)} (now empty)")
			except OSError:
				print(f"[KEPT] {week_dir.relative_to(REPO)} (not empty)", file=sys.stderr)

	return migrated, skipped


def main():
	parser = argparse.ArgumentParser(description="Migrate content to ISO-week structure.")
	parser.add_argument(
		"--dry-run",
		action="store_true",
		default=True,
		help="Show what would be migrated (default: True)",
	)
	parser.add_argument(
		"--live",
		action="store_true",
		help="Perform actual migration with git mv",
	)
	args = parser.parse_args()

	# --live overrides --dry-run
	dry_run = not args.live

	print(f"\n{'='*70}")
	print(f"Migrating to ISO-week structure ({'DRY-RUN' if dry_run else 'LIVE'})")
	print(f"{'='*70}\n")

	# Define all directories to migrate with their extraction functions
	migrations = [
		(REPO / "content" / "blogs", extract_date_simple, "content/blogs/"),
		(REPO / "content" / "derivatives", extract_date_simple, "content/derivatives/"),
		(REPO / "assets" / "raw", extract_date_simple, "assets/raw/"),
		(REPO / "assets" / "hyperframes", extract_hyperframe_date, "assets/hyperframes/"),
		(REPO / "assets" / "social_posts", extract_date_simple, "assets/social_posts/"),
		(REPO / "assets" / "slides", extract_date_simple, "assets/slides/"),
		(REPO / "assets" / "carousels", extract_date_simple, "assets/carousels/"),
		(REPO / "assets" / "reels_video", extract_date_simple, "assets/reels_video/"),
		(REPO / "output" / "animations", extract_date_simple, "output/animations/"),
		(REPO / "output" / "visuals", extract_date_simple, "output/visuals/"),
		(REPO / "output" / "worksheets", extract_date_simple, "output/worksheets/"),
		(REPO / "output" / "scheduled", extract_date_simple, "output/scheduled/"),
		(REPO / "remotion" / "public" / "broll", extract_date_simple, "remotion/public/broll/"),
		(REPO / "remotion" / "public" / "videos", extract_date_simple, "remotion/public/videos/"),
		(REPO / "remotion" / "public" / "captions", extract_date_simple, "remotion/public/captions/"),
		(REPO / "remotion" / "public" / "edit-plans", extract_date_simple, "remotion/public/edit-plans/"),
	]

	total_migrated = 0
	total_skipped = 0

	# Regular directory migrations
	for target_dir, extract_fn, label in migrations:
		if not target_dir.exists():
			print(f"[SKIP] {label} does not exist")
			continue

		print(f"Migrating {label}...")
		m, s = migrate_directory(target_dir, extract_fn, dry_run=dry_run)
		total_migrated += m
		total_skipped += s
		print(f"  → {m} migrated, {s} skipped\n")

	# Special: content/buffer/ — SKIPPED
	# Buffer files don't have date prefixes (they're slug-based: slug_meta.md, slug_social_copy.md, etc.)
	# and are pre-scheduling. Keep week-N structure as-is; it provides temporal context.
	print("Skipping content/buffer/ (no date prefixes, used for pre-scheduling staging)\n")

	print(f"{'='*70}")
	print(f"Total: {total_migrated} migrated, {total_skipped} skipped")
	if dry_run:
		print(f"(DRY-RUN: to execute, run with --live flag)")
	print(f"{'='*70}\n")


if __name__ == "__main__":
	main()
