#!/usr/bin/env python3
import os
import shutil
import re
from pathlib import Path
from collections import defaultdict

HYPERFRAMES_DIR = Path("assets/hyperframes")

def extract_true_slug(filename):
    """
    Extract TRUE content slug by normalizing render metadata.

    Pattern: [RENDER_DATE_]?[NICHE_PREFIX-]?CONTENT_DATE-CONTENT_TITLE[_NICHE]?[-|_aug][TYPE_SUFFIX].mp4

    Examples:
    - 2026-06-04_2026-06-01-poetry-quotes-looking-at-the-world-through-a-reflective-lens-short-00.mp4
      → 2026-06-01-poetry-quotes-looking-at-the-world-through-a-reflective-lens

    - 2026-06-03_ds-2026-06-01_data_science_tech_python-for-data-science-tutorial-310-aug.mp4
      → 2026-06-01-data-science-tech-python-for-data-science-tutorial-310

    - 2026-06-04_poetry-2026-06-01_poetry_quotes_looking-at-the-world-through-a-reflective-lens-aug.mp4
      → 2026-06-01-poetry-quotes-looking-at-the-world-through-a-reflective-lens
    """

    # Remove render-date prefix: "2026-XX-XX_"
    fname = re.sub(r'^20\d{2}-\d{2}-\d{2}_', '', filename)

    # Remove niche prefix: "[niche-|niche_]"
    fname = re.sub(r'^(ds|life|poetry)[-_]', '', fname, flags=re.IGNORECASE)

    # Extract YYYY-MM-DD[-or_]SLUG pattern. For files with multiple dates,
    # find the LAST date pattern (closest to the type marker).
    # Stop BEFORE sequence numbers (e.g., -short-00, -short-01)

    # Find what comes before each type marker to know where to cut
    short_match = re.search(r'-short-\d+', fname)
    aug_match = re.search(r'[-_]aug(?:\.mp4)?', fname)
    yt_match = re.search(r'[-_]yt(?:-short-\d+|\.mp4)?', fname)

    # Determine cutoff position (earliest type marker)
    cutoff_candidates = [m.start() for m in [short_match, aug_match, yt_match] if m]
    if not cutoff_candidates:
        cutoff = fname.rfind('.mp4')
    else:
        cutoff = min(cutoff_candidates)

    # Find all YYYY-MM-DD patterns up to cutoff
    dates_before_cutoff = list(re.finditer(r'20\d{2}-\d{2}-\d{2}', fname[:cutoff]))

    if dates_before_cutoff:
        # Use the LAST date found
        last_date = dates_before_cutoff[-1]
        start_pos = last_date.start()
        # Extract from this date to cutoff (before sequence numbers)
        slug = fname[start_pos:cutoff]
        # Remove trailing -short, -yt, etc if they snuck in
        slug = re.sub(r'(-short|-yt)$', '', slug)
        # Normalize: underscores → hyphens
        slug = re.sub(r'_', '-', slug)
        return slug

    # Fallback: if no YYYY-MM-DD pattern, archive it
    return None

def categorize_file(filename):
    """Return 'shorts', 'long-form', or 'archive'."""
    if '-short-' in filename or '-short_' in filename:
        return 'shorts'
    elif '_aug.mp4' in filename or '-aug.mp4' in filename:
        return 'long-form'
    else:
        if re.search(r'20\d{2}-\d{2}-\d{2}', filename):
            return 'long-form'
        else:
            return 'archive'

def main():
    if not HYPERFRAMES_DIR.exists():
        print(f"✗ {HYPERFRAMES_DIR} not found")
        return

    # First, flatten all existing slug dirs back to top level
    print("Flattening existing structure...")
    for item in HYPERFRAMES_DIR.iterdir():
        if item.is_dir() and item.name != 'archive':
            # Move all files up from slug/* subdirs
            for subdir in item.iterdir():
                if subdir.is_dir():
                    for f in subdir.iterdir():
                        if f.is_file():
                            dest = HYPERFRAMES_DIR / f.name
                            shutil.move(str(f), str(dest))
            # Remove empty slug dir
            try:
                item.rmdir()
            except:
                pass

    # Handle archive separately
    archive_dir = HYPERFRAMES_DIR / 'archive'
    if archive_dir.exists():
        for f in archive_dir.iterdir():
            if f.is_file():
                dest = HYPERFRAMES_DIR / f.name
                shutil.move(str(f), str(dest))
        archive_dir.rmdir()

    print("Reorganizing by true slug...")
    files = sorted([f for f in HYPERFRAMES_DIR.iterdir() if f.is_file()])

    if not files:
        print("✗ No files in hyperframes/")
        return

    # Group by TRUE slug
    by_slug = defaultdict(list)
    archive_files = []

    for fpath in files:
        fname = fpath.name
        slug = extract_true_slug(fname)
        cat = categorize_file(fname)

        if slug is None or cat == 'archive':
            archive_files.append(fpath)
        else:
            by_slug[slug].append((cat, fpath))

    # Create dirs + move files
    created = 0
    moved = 0

    for slug in sorted(by_slug.keys()):
        files_list = by_slug[slug]
        slug_dir = HYPERFRAMES_DIR / slug
        slug_dir.mkdir(exist_ok=True)
        created += 1

        for cat, fpath in files_list:
            subdir = slug_dir / cat
            subdir.mkdir(exist_ok=True)

            new_path = subdir / fpath.name
            if new_path != fpath:
                shutil.move(str(fpath), str(new_path))
                moved += 1
                print(f"  {fpath.name} → {slug}/{cat}/")

    # Move archive files
    if archive_files:
        ARCHIVE_DIR = HYPERFRAMES_DIR / 'archive'
        ARCHIVE_DIR.mkdir(exist_ok=True)
        for fpath in archive_files:
            new_path = ARCHIVE_DIR / fpath.name
            if new_path != fpath:
                shutil.move(str(fpath), str(new_path))
                moved += 1
                print(f"  {fpath.name} → archive/")

    print(f"\n✓ Consolidated to {created} true slugs, {len(archive_files)} archived, {moved} files moved")

if __name__ == '__main__':
    main()
