#!/usr/bin/env python3
import os
import shutil
import re
from pathlib import Path
from collections import defaultdict

HYPERFRAMES_DIR = Path("assets/hyperframes")
ARCHIVE_DIR = HYPERFRAMES_DIR / "archive"

def extract_slug(filename):
    """Extract content slug from hyperframes filename."""
    # Pattern: 2026-XX-XX_[prefix-]2026-XX-XX-SLUG[-short-##|-_aug|-other].mp4
    # Examples:
    # 2026-06-04_2026-06-01-poetry-quotes-looking-at-the-world-through-a-reflective-lens-short-00.mp4
    # 2026-06-04_poetry-2026-06-01_poetry_quotes_looking-at-the-world-through-a-reflective-lens-aug.mp4

    # Try to match YYYY-MM-DD-SLUG pattern (normalize underscores to hyphens)
    match = re.search(r'(20\d{2}-\d{2}-\d{2}[^.]*?)(?:-short-\d+|-_aug|_aug|\.mp4)', filename)
    if match:
        slug = match.group(1)
        # Normalize: replace underscores in slug with hyphens (except where they're part of date separation)
        slug = re.sub(r'_(?!\.)', '-', slug)
        return slug

    return None

def categorize_file(filename):
    """Return ('shorts', filename) or ('long-form', filename) or ('archive', filename)."""
    if '-short-' in filename or '-short_' in filename:
        return 'shorts'
    elif '_aug.mp4' in filename or '-aug.mp4' in filename:
        return 'long-form'
    else:
        # Check if it has YYYY-MM-DD pattern (keep in long-form if dated, else archive)
        if re.search(r'20\d{2}-\d{2}-\d{2}', filename):
            return 'long-form'
        else:
            return 'archive'

def main():
    if not HYPERFRAMES_DIR.exists():
        print(f"✗ {HYPERFRAMES_DIR} not found")
        return

    files = sorted([f for f in HYPERFRAMES_DIR.iterdir() if f.is_file()])

    if not files:
        print("✗ No files in hyperframes/")
        return

    # Group by slug
    by_slug = defaultdict(list)
    archive_files = []

    for fpath in files:
        fname = fpath.name
        slug = extract_slug(fname)
        cat = categorize_file(fname)

        if cat == 'archive' or slug is None:
            archive_files.append(fpath)
        else:
            by_slug[slug].append((cat, fpath))

    # Create dirs + move files
    created = 0
    moved = 0

    for slug, files_list in sorted(by_slug.items()):
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
        ARCHIVE_DIR.mkdir(exist_ok=True)
        for fpath in archive_files:
            new_path = ARCHIVE_DIR / fpath.name
            if new_path != fpath:
                shutil.move(str(fpath), str(new_path))
                moved += 1
                print(f"  {fpath.name} → archive/")

    print(f"\n✓ Organized {len(by_slug)} slugs, {len(archive_files)} archived, {moved} files moved")

if __name__ == '__main__':
    main()
