#!/usr/bin/env python3
"""
archive_week.py — Move weekly content from content-machine to /Volumes/Archive.

Discovers every 2026-Wnn/ subfolder across the repo automatically — no need
to specify individual source folders.

Usage:
    python3 archive_week.py --repo ~/path/to/content-machine
    python3 archive_week.py --repo ~/path/to/content-machine --week 2026-W24
    python3 archive_week.py --repo ~/path/to/content-machine --types mp4 mov jpg
    python3 archive_week.py --repo ~/path/to/content-machine --dry-run
    python3 archive_week.py --repo ~/path/to/content-machine --copy   # preserve source

Options:
    --repo      Required. Root of the content-machine repository.
    --week      ISO week string e.g. 2026-W24. Defaults to current ISO week.
    --types     Space-separated file extensions to move. Defaults to all files.
    --dry-run   Preview what would be moved without writing anything.
    --copy      Copy instead of move (source files are preserved).
"""

import argparse
import datetime
import logging
import shutil
import sys
from pathlib import Path

ARCHIVE_ROOT = Path("/Volumes/Archive/content-archive")

log = logging.getLogger("archive_week")


def setup_logging(log_path: Path | None, dry_run: bool) -> None:
    level = logging.DEBUG
    fmt = "%(asctime)s  %(levelname)-7s  %(message)s"
    datefmt = "%Y-%m-%dT%H:%M:%S"

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if log_path and not dry_run:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path, encoding="utf-8"))

    logging.basicConfig(level=level, format=fmt, datefmt=datefmt, handlers=handlers)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Move weekly content to /Volumes/Archive."
    )
    parser.add_argument("--repo", required=True, help="Content-machine repo root path")
    parser.add_argument(
        "--week",
        default=None,
        help="ISO week e.g. 2026-W24. Defaults to current week.",
    )
    parser.add_argument(
        "--types",
        nargs="*",
        default=None,
        help="File extensions to move (without dot). Omit to move all.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be moved without moving anything.",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy instead of move (source files are preserved).",
    )
    return parser.parse_args()


def current_iso_week() -> str:
    today = datetime.date.today()
    iso = today.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def parse_week(week_str: str) -> tuple[int, int]:
    try:
        parts = week_str.split("-W")
        if len(parts) != 2:
            raise ValueError
        return int(parts[0]), int(parts[1])
    except (ValueError, IndexError):
        print(f"ERROR: Invalid week format '{week_str}'. Expected YYYY-Wnn (e.g. 2026-W24).")
        sys.exit(1)


def human_size(num_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"


def free_space(path: Path) -> int:
    return shutil.disk_usage(path).free


def collect_files_for_week(
    repo_root: Path, week_str: str, extensions: list[str] | None
) -> list[tuple[Path, Path]]:
    """
    Find every file inside any directory named week_str under repo_root.
    Returns list of (src_file, relative_path_from_repo_root) pairs.
    """
    exts = {e.lower().lstrip(".") for e in extensions} if extensions else None
    results = []

    for week_dir in sorted(repo_root.rglob(week_str)):
        if not week_dir.is_dir():
            continue
        for p in sorted(week_dir.rglob("*")):
            if not p.is_file():
                continue
            if exts is not None and p.suffix.lower().lstrip(".") not in exts:
                continue
            results.append((p, p.relative_to(repo_root)))

    return results


def main():
    args = parse_args()

    repo_root = Path(args.repo).expanduser().resolve()
    if not repo_root.exists() or not repo_root.is_dir():
        # Logging not set up yet — plain print for fatal pre-init errors.
        print(f"ERROR: Repo root not found: {repo_root}")
        sys.exit(1)

    archive_mount = Path("/Volumes/Archive")
    if not archive_mount.exists() or not archive_mount.is_mount():
        print("ERROR: Archive drive not mounted at /Volumes/Archive. Connect drive and retry.")
        sys.exit(1)

    week_str = args.week or current_iso_week()
    year, week_num = parse_week(week_str)

    dest_root = ARCHIVE_ROOT / str(year) / f"W{week_num:02d}"
    manifest_path = dest_root / "manifest.txt"
    log_path = dest_root / "archive.log"
    action = "copy" if args.copy else "move"

    setup_logging(log_path, args.dry_run)

    log.info("Repo     : %s", repo_root)
    log.info("Week     : %s", week_str)
    log.info("Dest     : %s", dest_root)
    log.info("Types    : %s", ", ".join(args.types) if args.types else "all")
    log.info("Action   : %s", action)
    if args.dry_run:
        log.info("Mode     : DRY RUN — nothing will be written")

    file_pairs = collect_files_for_week(repo_root, week_str, args.types)

    if not file_pairs:
        log.warning("No matching files found for %s in %s. Nothing to do.", week_str, repo_root)
        sys.exit(0)

    log.info("Discovered %d files to %s.", len(file_pairs), action)

    moved_files: list[tuple[Path, Path, int]] = []
    cleaned_files: list[Path] = []   # already archived on prior run, src deleted this run
    error_files: list[tuple[Path, str]] = []

    for src_file, rel_path in file_pairs:
        dst_file = dest_root / rel_path

        if dst_file.exists():
            # File already in archive — delete source so it only lives on the drive.
            if args.dry_run:
                log.debug("CLEAN %s (archived, src would be deleted)", rel_path)
                cleaned_files.append(src_file)
            else:
                try:
                    src_file.unlink()
                    log.debug("CLEAN %s (deleted from source)", rel_path)
                    cleaned_files.append(src_file)
                except OSError as e:
                    log.error("FAIL  %s — could not delete source: %s", rel_path, e)
                    error_files.append((src_file, f"could not delete source: {e}"))
            continue

        size = src_file.stat().st_size

        if args.dry_run:
            log.debug("DRY   %s (%s)", rel_path, human_size(size))
            moved_files.append((src_file, dst_file, size))
            continue

        try:
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            if args.copy:
                shutil.copy2(src_file, dst_file)
            else:
                shutil.move(str(src_file), dst_file)
            log.debug("OK    %s (%s)", rel_path, human_size(size))
            moved_files.append((src_file, dst_file, size))
        except PermissionError as e:
            log.error("FAIL  %s — permission denied: %s", rel_path, e)
            error_files.append((src_file, f"permission denied: {e}"))
        except OSError as e:
            log.error("FAIL  %s — %s", rel_path, e)
            error_files.append((src_file, str(e)))

    # Remove empty week dirs left behind in source.
    pruned_dirs: list[Path] = []
    if not args.dry_run:
        pruned_dirs = _prune_empty_week_dirs(repo_root, week_str)
    elif cleaned_files or moved_files:
        # Dry-run: show which dirs would be pruned.
        pruned_dirs = _collect_pruneable_week_dirs(repo_root, week_str)
        for d in pruned_dirs:
            log.debug("PRUNE %s (would remove empty dir)", d.relative_to(repo_root))

    total_moved_size = sum(s for _, _, s in moved_files)

    if not args.dry_run and (moved_files or cleaned_files):
        _write_manifest(
            manifest_path=manifest_path,
            repo_root=repo_root,
            week_str=week_str,
            extensions=args.types,
            action=action,
            moved=moved_files,
            cleaned=cleaned_files,
            pruned=pruned_dirs,
            errors=error_files,
        )

    if not args.dry_run:
        _verify(dest_root, moved_files)

    verb = (
        "Would move" if (args.dry_run and not args.copy)
        else ("Would copy" if args.dry_run
        else ("Copied" if args.copy else "Moved"))
    )

    log.info("── Summary ──────────────────────────────────────────")
    log.info("  %-12s: %d files (%s)", verb, len(moved_files), human_size(total_moved_size))
    log.info("  %-12s: %d files (already archived, src %s)", "Cleaned",
             len(cleaned_files), "would be deleted" if args.dry_run else "deleted")
    log.info("  %-12s: %d dirs (empty week dirs %s)", "Pruned",
             len(pruned_dirs), "would be removed" if args.dry_run else "removed")
    if error_files:
        log.warning("  %-12s: %d files", "Errors", len(error_files))
    log.info("  %-12s: %s", "Destination", dest_root)
    log.info("  %-12s: %s remaining on source SSD", "SSD free", human_size(free_space(repo_root)))
    log.info("  %-12s: %s remaining on /Volumes/Archive", "Archive free", human_size(free_space(archive_mount)))
    if not args.dry_run:
        log.info("  %-12s: %s", "Log", log_path)

    if error_files:
        log.error("Errors detail:")
        for f, reason in error_files:
            log.error("  %s: %s", f, reason)
        sys.exit(1)


def _is_dir_empty(d: Path) -> bool:
    return not any(d.rglob("*"))


def _collect_pruneable_week_dirs(repo_root: Path, week_str: str) -> list[Path]:
    """Return week dirs that are already empty (safe to delete)."""
    return [
        d for d in sorted(repo_root.rglob(week_str))
        if d.is_dir() and _is_dir_empty(d)
    ]


def _prune_empty_week_dirs(repo_root: Path, week_str: str) -> list[Path]:
    """Delete empty week dirs in source. Returns list of dirs removed."""
    pruned = []
    for week_dir in sorted(repo_root.rglob(week_str), reverse=True):
        if not week_dir.is_dir():
            continue
        if _is_dir_empty(week_dir):
            try:
                week_dir.rmdir()
                log.debug("PRUNED %s", week_dir.relative_to(repo_root))
                pruned.append(week_dir)
            except OSError as e:
                log.warning("Could not remove dir %s: %s", week_dir, e)
    return pruned


def _write_manifest(
    manifest_path: Path,
    repo_root: Path,
    week_str: str,
    extensions: list[str] | None,
    action: str,
    moved: list[tuple[Path, Path, int]],
    cleaned: list[Path],
    pruned: list[Path],
    errors: list[tuple[Path, str]],
):
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    total_size = sum(s for _, _, s in moved)

    lines = [
        "CONTENT ARCHIVE MANIFEST",
        "=" * 60,
        f"Timestamp   : {timestamp}",
        f"Repo root   : {repo_root}",
        f"ISO Week    : {week_str}",
        f"Action      : {action}",
        f"File types  : {', '.join(extensions) if extensions else 'all'}",
        f"Files {action}d : {len(moved)}",
        f"Total size  : {human_size(total_size)}",
        "",
        f"── {action.title()}d Files " + "─" * 44,
    ]

    current_parent = None
    for src, dst, size in moved:
        parent = dst.relative_to(manifest_path.parent).parts[0] if len(dst.relative_to(manifest_path.parent).parts) > 1 else ""
        if parent != current_parent:
            current_parent = parent
            lines.append(f"\n  [{parent}/]")
        lines.append(f"    {human_size(size):>10}  {dst.name}")

    if cleaned:
        lines += ["", "── Cleaned (already archived, source deleted) " + "─" * 15]
        for src in cleaned:
            lines.append(f"  {src}")

    if pruned:
        lines += ["", "── Pruned Empty Dirs " + "─" * 39]
        for d in pruned:
            lines.append(f"  {d}")

    if errors:
        lines += ["", "── Errors " + "─" * 50]
        for src, reason in errors:
            lines.append(f"  {src}: {reason}")

    manifest_path.write_text("\n".join(lines) + "\n")
    log.info("Manifest written: %s", manifest_path)


def _verify(dest_root: Path, moved: list[tuple[Path, Path, int]]):
    if not moved:
        return

    expected_count = len(moved)
    expected_size = sum(s for _, _, s in moved)

    actual_count = sum(1 for _, dst, _ in moved if dst.exists())
    actual_size = sum(dst.stat().st_size for _, dst, _ in moved if dst.exists())

    ok = True
    if actual_count != expected_count:
        log.warning("Verify FAIL: expected %d files at dest, found %d.", expected_count, actual_count)
        ok = False
    if actual_size != expected_size:
        log.warning(
            "Verify FAIL: expected %s at dest, found %s.",
            human_size(expected_size), human_size(actual_size),
        )
        ok = False
    if ok:
        log.info("Verify OK — %d files, %s.", actual_count, human_size(actual_size))


if __name__ == "__main__":
    main()
