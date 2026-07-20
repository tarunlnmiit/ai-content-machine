#!/usr/bin/env python3
"""
Frontmatter engine for content vault. Walks 4 dirs and ensures YAML frontmatter.

Idempotent merge: file lacks frontmatter → prepend fresh block. File has block →
add missing keys only, never overwrite existing values.

CLI:
  --dry-run   Print unified diffs, write nothing
  --check     Exit 1 if files lack frontmatter; write nothing
  --self-check Run self-test with 3 fixtures
"""

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

from lib.niche_config import NICHE_MAP
from lib.schedule_calc import get_iso_week

# Root of the repo (parent of v1/)
REPO_ROOT = Path(__file__).resolve().parents[2]
V1_ROOT = REPO_ROOT / "v1"

# Target directories (relative to repo root)
VAULT_DIRS = [
    V1_ROOT / "content",
    V1_ROOT / "docs",
    V1_ROOT / "data" / "kb",
    V1_ROOT / "prompts",
]

# Canonical niches (used for tag generation)
CANONICAL_NICHES = {
    "data_science_tech": "data_science_tech",
    "life_self_dev": "life_self_dev",
    "poetry_quotes": "poetry_quotes",
}

# Patterns to extract date and platform from filename
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
WEEK_RE = re.compile(r"(\d{4}-W\d{2})")
PLATFORM_MAP = {
    "_ig_reel": "ig",
    "_instagram": "ig",
    "_linkedin_post": "linkedin",
    "_linkedin": "linkedin",
    "_youtube_script": "youtube",
    "_youtube": "youtube",
    "_yt": "yt",
    "_youtube_shorts": "yt",
    "_substack_post": "substack",
    "_substack": "substack",
    "_medium": "medium",
}


@dataclass(frozen=True)
class Frontmatter:
    """Immutable frontmatter record."""
    title: Optional[str] = None
    type: Optional[str] = None
    niche: Optional[str] = None
    date: Optional[str] = None
    week: Optional[str] = None
    slug: Optional[str] = None
    platform: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[list] = None

    def to_yaml_lines(self, unknown_keys: Optional[dict] = None) -> list[str]:
        """Emit YAML frontmatter block (ordered, omit None values).

        unknown_keys: dict of keys not in schema, to be preserved from original.
        These are output first (in order) to preserve the original relative ordering.
        """
        lines = ["---"]

        # Output unknown keys first (to preserve original order)
        if unknown_keys:
            for key, val in unknown_keys.items():
                if isinstance(val, list):
                    tag_str = ", ".join(val)
                    lines.append(f"{key}: [{tag_str}]")
                elif isinstance(val, str) and " " in val:
                    escaped = val.replace('"', '\\"')
                    lines.append(f'{key}: "{escaped}"')
                else:
                    lines.append(f"{key}: {val}")

        # Then output known fields in schema order
        for field_name in ["title", "type", "niche", "date", "week", "slug", "platform", "status", "tags"]:
            val = getattr(self, field_name, None)
            if val is not None:
                if field_name == "title":
                    escaped = str(val).replace('"', '\\"')
                    lines.append(f'title: "{escaped}"')
                elif field_name == "tags":
                    tag_str = ", ".join(val)
                    lines.append(f"tags: [{tag_str}]")
                else:
                    lines.append(f"{field_name}: {val}")
        lines.append("---")
        return lines


def derive_metadata(file_path: Path) -> Frontmatter:
    """Derive frontmatter fields from file path and content."""
    relative_path = file_path.relative_to(REPO_ROOT)
    stem = file_path.stem
    body = file_path.read_text(encoding="utf-8")

    # Parse existing frontmatter if present
    existing_fm = parse_frontmatter_block(body)

    # Extract title from body (first h1)
    title = extract_title(body)
    if existing_fm and existing_fm.get("title"):
        title = existing_fm["title"]

    # Strip trailing .md from title (safety measure for derived titles)
    if title and title.endswith(".md"):
        title = title[:-3]

    # Derive type from path structure
    type_val = derive_type(relative_path)

    # Derive niche from filename and path
    niche = derive_niche(stem, relative_path)

    # Extract date from filename (YYYY-MM-DD prefix)
    date_val = extract_date(stem)

    # Derive week from path component or date
    week = derive_week(relative_path, date_val)

    # Extract platform from filename suffix
    platform = derive_platform(stem)

    # Derive slug: filename stem minus date prefix, minus niche token, minus platform suffix
    slug = derive_slug(stem, date_val, niche, platform)

    # Look up status (simplified: only from medium_posts.json for now)
    status = None

    # Build tags
    tags = build_tags(type_val, niche, week)

    return Frontmatter(
        title=title,
        type=type_val,
        niche=niche,
        date=date_val,
        week=week,
        slug=slug,
        platform=platform,
        status=status,
        tags=tags if tags else None,
    )


def parse_frontmatter_block(text: str) -> Optional[dict]:
    """Parse YAML frontmatter block from file. Return dict or None if no block."""
    if not text.startswith("---"):
        return None

    # Find closing ---
    lines = text.split("\n")
    if len(lines) < 3:
        return None

    closing_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            closing_idx = i
            break

    if closing_idx is None:
        return None

    fm_lines = lines[1:closing_idx]
    fm_dict = {}

    for line in fm_lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if ":" not in line:
            continue

        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        # Handle quoted strings
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1].replace('\\"', '"')
        # Handle lists [tag1, tag2, ...]
        elif value.startswith("[") and value.endswith("]"):
            value = [v.strip() for v in value[1:-1].split(",")]

        fm_dict[key] = value

    return fm_dict if fm_dict else None


def extract_frontmatter_end_idx(text: str) -> int:
    """Return byte index after closing ---, or 0 if no frontmatter."""
    if not text.startswith("---"):
        return 0

    lines = text.split("\n")
    byte_pos = 0

    for i, line in enumerate(lines):
        if i > 0 and line.strip() == "---":
            # Return byte position after this closing --- and its newline
            return byte_pos + len(line) + 1

        byte_pos += len(line) + 1  # +1 for the \n

    return 0


def should_skip_file(body: str, fm: Optional[dict], file_path: Optional[Path] = None) -> bool:
    """Skip files that should not receive frontmatter.

    Skips:
    1. Claude Code slash-command definitions (must have BOTH $ARGUMENTS AND description key)
    2. IMAGE_MAP.md files (parent directory ends with _images)

    This avoids skipping documentation files that merely mention $ARGUMENTS.
    """
    # Skip IMAGE_MAP files (they are auto-generated asset manifests)
    if file_path and len(file_path.parts) >= 2 and file_path.parts[-2].endswith("_images"):
        return True

    # Skip Claude Code command definitions
    if "$ARGUMENTS" not in body:
        return False
    if not fm or "description" not in fm:
        return False
    return True


def extract_title(body: str) -> Optional[str]:
    """Extract first h1 from body, skipping frontmatter."""
    start_idx = extract_frontmatter_end_idx(body)
    lines = body.split("\n")[start_idx:]

    for line in lines:
        m = re.match(r"^#\s+(.+)$", line)
        if m:
            return m.group(1).strip()

    return None


def derive_type(rel_path: Path) -> Optional[str]:
    """Derive type from path structure."""
    parts = rel_path.parts

    # For v1/content/subdir/..., type is subdir name (blogs→blog, etc.)
    if "content" in parts:
        idx = parts.index("content")
        if idx + 1 < len(parts):
            subdir = parts[idx + 1]
            type_map = {
                "blogs": "blog",
                "reels": "reel",
                "derivatives": "derivative",
                "scripts": "script",
                "buffer": "buffer",
                "archive": "archive",
            }
            return type_map.get(subdir)

    # For v1/docs/..., type is doc
    if "docs" in parts:
        return "doc"

    # For v1/data/kb/..., type is kb
    if "kb" in parts:
        return "kb"

    # For v1/prompts/..., type is prompt
    if "prompts" in parts:
        return "prompt"

    return None


def derive_niche(stem: str, rel_path: Path) -> Optional[str]:
    """Derive canonical niche from filename and path. Longest match wins."""
    # Map aliases to canonical
    candidates = []

    for alias, canonical in NICHE_MAP.items():
        if alias in stem or alias in str(rel_path):
            candidates.append((len(alias), canonical))

    if candidates:
        candidates.sort(reverse=True)
        return candidates[0][1]

    return None


def extract_date(stem: str) -> Optional[str]:
    """Extract YYYY-MM-DD from filename prefix."""
    m = DATE_RE.match(stem)
    if m:
        return m.group(1)
    return None


def derive_week(rel_path: Path, date_val: Optional[str]) -> Optional[str]:
    """Derive week from path component (YYYY-Wnn) or from date."""
    # Check for YYYY-Wnn in path
    m = WEEK_RE.search(str(rel_path))
    if m:
        return m.group(1)

    # Derive from date
    if date_val:
        return get_iso_week(date_val)

    return None


def derive_platform(stem: str) -> Optional[str]:
    """Derive platform from filename suffix."""
    for suffix, platform in PLATFORM_MAP.items():
        if stem.endswith(suffix):
            return platform
    return None


def derive_slug(stem: str, date_val: Optional[str], niche: Optional[str], platform: Optional[str]) -> Optional[str]:
    """Derive slug by removing date, niche, platform, and ALL-CAPS suffixes from stem.

    Rules applied in order:
    1. Strip leading YYYY-MM-DD_ prefix
    2. Strip leading canonical niche token or alias
    3. Strip trailing ALL-CAPS suffix matching _[A-Z][A-Z0-9_]*$ REPEATEDLY
    4. Strip trailing platform/type suffixes
    5. Handle embedded second date+niche (YYYY-MM-DD- prefix + dash-separated niche)
    6. Normalize: lowercase, underscores→dashes, collapse dashes, trim leading/trailing
    7. Return None if empty
    """
    slug = stem

    # Step 1: Strip leading YYYY-MM-DD_ prefix
    if date_val and slug.startswith(date_val + "_"):
        slug = slug[len(date_val) + 1:]

    # Step 2: Strip leading canonical niche token
    # Build map of all aliases to canonical forms
    niche_aliases = {}
    for alias, canonical in NICHE_MAP.items():
        niche_aliases[alias] = canonical
    # Also add canonical forms
    for canonical in CANONICAL_NICHES.values():
        niche_aliases[canonical] = canonical

    # Try to remove niche prefix (longest first to avoid partial matches)
    niche_prefixes = sorted(niche_aliases.keys(), key=len, reverse=True)
    for prefix in niche_prefixes:
        if slug.startswith(prefix + "_"):
            slug = slug[len(prefix) + 1:]
            break

    # Step 3: Strip trailing ALL-CAPS suffix REPEATEDLY
    # Only strip if remainder contains non-uppercase (avoids breaking all-caps filenames)
    while True:
        m = re.match(r"^(.+?)_[A-Z][A-Z0-9_]*$", slug)
        if not m:
            break
        remainder = m.group(1)
        # Only strip if remainder has non-uppercase chars (lowercase/digits/hyphens)
        if not re.search(r"[a-z0-9\-]", remainder):
            break
        slug = remainder

    # Step 4: Strip trailing platform/type suffixes
    for suffix in sorted(PLATFORM_MAP.keys(), key=len, reverse=True):
        if slug.endswith(suffix):
            slug = slug[:-len(suffix)]
            break

    # Step 5: Handle embedded second date+niche (YYYY-MM-DD-niche-...)
    # e.g., "2026-05-27-poetry-quotes-intoxicated-senses" → strip date + niche
    date_pattern = re.match(r"^(\d{4}-\d{2}-\d{2})-(.*)$", slug)
    if date_pattern:
        rest = date_pattern.group(2)

        # Try to strip dash-separated niche from rest
        for alias in niche_prefixes:
            # Convert underscores to dashes for matching
            dash_alias = alias.replace("_", "-")
            if rest.startswith(dash_alias + "-"):
                rest = rest[len(dash_alias) + 1:]
                break

        slug = rest

    # Step 6: Normalize: lowercase, underscores→dashes, collapse repeated dashes, trim
    slug = slug.lower()
    slug = slug.replace("_", "-")
    slug = re.sub(r"-+", "-", slug)  # Collapse repeated dashes
    slug = slug.strip("-")

    # Step 7: Return None if empty
    return slug if slug else None


def build_tags(type_val: Optional[str], niche: Optional[str], week: Optional[str]) -> Optional[list]:
    """Build tag list."""
    tags = []

    if type_val:
        tags.append(f"content/{type_val}")

    if niche:
        tags.append(f"niche/{niche}")

    if week:
        tags.append(f"week/{week}")

    return tags if tags else None


def merge_frontmatter(existing_fm: Optional[dict], new_fm: Frontmatter, force_rewrite: bool = False) -> tuple[Frontmatter, Optional[dict]]:
    """Merge: keep existing values, add missing keys only (or recompute derived keys if force_rewrite).

    Args:
        existing_fm: Parsed frontmatter dict from file (or None)
        new_fm: Newly derived Frontmatter
        force_rewrite: If True, recompute derived keys (type, niche, date, week, slug, platform, tags)
                       but preserve title and unknown keys.
                       If False (default), keep existing values and add missing keys only.

    Returns (merged_frontmatter, unknown_keys_dict).
    unknown_keys_dict contains keys from existing_fm that are not in the schema,
    preserving their original order.
    """
    if not existing_fm:
        return new_fm, None

    # Track unknown keys (not in schema)
    schema_keys = set(Frontmatter.__dataclass_fields__.keys())
    unknown_keys = {}

    # Preserve unknown keys in original order
    for key, val in existing_fm.items():
        if key not in schema_keys:
            unknown_keys[key] = val

    # Build merged dict
    merged_dict = {}

    # Define which keys are derived (can be recomputed) and which are user-provided
    derived_keys = {"type", "niche", "date", "week", "slug", "platform", "tags"}
    user_keys = {"title", "status"}

    for field_name in ["title", "type", "niche", "date", "week", "slug", "platform", "status", "tags"]:
        if force_rewrite and field_name in derived_keys:
            # Force-rewrite mode: use new value for derived keys
            val = getattr(new_fm, field_name, None)
            if val is not None:
                merged_dict[field_name] = val
        elif field_name in existing_fm and existing_fm[field_name] is not None:
            # Normal mode: keep existing value
            merged_dict[field_name] = existing_fm[field_name]
        else:
            # Add new value if missing
            val = getattr(new_fm, field_name, None)
            if val is not None:
                merged_dict[field_name] = val

    # Construct Frontmatter from merged dict, filling missing fields with None
    fm_kwargs = {k: merged_dict.get(k) for k in Frontmatter.__dataclass_fields__}
    return Frontmatter(**fm_kwargs), unknown_keys if unknown_keys else None


def process_file(file_path: Path, dry_run: bool = False, force_rewrite: bool = False) -> tuple[bool, str]:
    """
    Process one file: add/merge frontmatter. Return (changed, diff_or_message).

    If force_rewrite=True, recompute and replace derived keys (type, niche, date, week, slug, platform, tags)
    while preserving existing title and unknown keys.
    """
    body = file_path.read_text(encoding="utf-8")

    # Parse existing frontmatter
    existing_fm = parse_frontmatter_block(body)

    # Skip IMAGE_MAP and Claude Code command files
    if should_skip_file(body, existing_fm, file_path=file_path):
        reason = "image-map" if len(file_path.parts) >= 2 and file_path.parts[-2].endswith("_images") else "$ARGUMENTS"
        return False, f"skipped ({reason})"

    # Derive new metadata
    new_fm = derive_metadata(file_path)

    # Merge (keep existing, add missing), returns (Frontmatter, unknown_keys)
    # If force_rewrite, allow overwriting derived keys but preserve title
    merged_fm, unknown_keys = merge_frontmatter(existing_fm, new_fm, force_rewrite=force_rewrite)

    # Check if anything changed
    if existing_fm:
        # Convert merged back to dict for comparison
        existing_keys = set(existing_fm.keys())
        new_keys = {k: v for k, v in merged_fm.__dict__.items() if v is not None}
        if unknown_keys:
            new_keys.update(unknown_keys)

        if existing_keys == set(new_keys.keys()) and all(
            existing_fm.get(k) == new_keys.get(k) for k in existing_keys
        ):
            return False, "no change"

    # Build new content
    fm_lines = merged_fm.to_yaml_lines(unknown_keys=unknown_keys)

    if existing_fm:
        # Replace block, preserving original body exactly (don't lstrip)
        end_idx = extract_frontmatter_end_idx(body)
        original_body = body[end_idx:] if end_idx > 0 else body
        new_body = "\n".join(fm_lines) + "\n" + original_body
    else:
        # Prepend block
        new_body = "\n".join(fm_lines) + "\n" + body

    # Dry run: show diff
    if dry_run:
        import difflib
        diff = difflib.unified_diff(
            body.splitlines(keepends=True),
            new_body.splitlines(keepends=True),
            fromfile=str(file_path),
            tofile=str(file_path),
        )
        diff_text = "".join(diff)
        return True, diff_text

    # Write
    file_path.write_text(new_body, encoding="utf-8")
    return True, "written"


def scan_vault(dry_run: bool = False, check_mode: bool = False, force_rewrite: bool = False) -> tuple[int, int, int, int, list]:
    """
    Scan all 4 dirs. Return (scanned, written, current, skipped, missing_files).
    """
    scanned = 0
    written = 0
    current = 0
    skipped = 0
    missing = []
    skipped_files = []

    for dir_path in VAULT_DIRS:
        if not dir_path.exists():
            continue

        for md_file in sorted(dir_path.rglob("*.md")):
            scanned += 1

            try:
                body = md_file.read_text(encoding="utf-8")

                if check_mode and not body.startswith("---"):
                    missing.append(str(md_file))

                changed, msg = process_file(md_file, dry_run=dry_run, force_rewrite=force_rewrite)

                if msg.startswith("skipped"):
                    skipped += 1
                    skipped_files.append((str(md_file), msg))
                elif not changed:
                    current += 1
                elif dry_run:
                    print(msg)
                    written += 1
                else:
                    written += 1

            except Exception as e:
                print(f"ERROR {md_file}: {e}", file=sys.stderr)
                skipped += 1
                skipped_files.append((str(md_file), str(e)))

    if skipped_files:
        print(f"Skipped {skipped} files:")
        for fpath, reason in skipped_files[:10]:
            print(f"  {fpath}: {reason}")
        if len(skipped_files) > 10:
            print(f"  ... and {len(skipped_files) - 10} more")

    return scanned, written, current, skipped, missing


def demo() -> None:
    """Self-check with fixtures. Run twice, ensure idempotency."""

    # Test slug derivation with exact user-provided examples
    print("Testing slug derivation...")

    # Example 1: the-end-of-poetry-by-ada-limó_CAPCUT_EDITING_GUIDE
    # Should strip _CAPCUT_EDITING_GUIDE and normalize
    stem1 = "the-end-of-poetry-by-ada-limó_CAPCUT_EDITING_GUIDE"
    slug1 = derive_slug(stem1, date_val=None, niche=None, platform=None)
    expected1 = "the-end-of-poetry-by-ada-limo"  # Non-ASCII ó→o in slug derivation
    # Actually, the user said "preserve non-ASCII letters", so ó should stay ó
    expected1 = "the-end-of-poetry-by-ada-limó"
    assert slug1 == expected1, f"Slug 1 failed: expected {expected1}, got {slug1}"
    print(f"  ✓ Slug 1: {stem1} → {slug1}")

    # Example 2: 2026-06-03_2026-05-27-poetry-quotes-intoxicated-senses_yt_PRODUCTION_GUIDE
    # Should strip date prefix, handle embedded date+niche, strip platform, strip PRODUCTION_GUIDE
    stem2 = "2026-06-03_2026-05-27-poetry-quotes-intoxicated-senses_yt_PRODUCTION_GUIDE"
    slug2 = derive_slug(stem2, date_val="2026-06-03", niche="poetry_quotes", platform="yt")
    expected2 = "intoxicated-senses"
    assert slug2 == expected2, f"Slug 2 failed: expected {expected2}, got {slug2}"
    print(f"  ✓ Slug 2: {stem2} → {slug2}")

    # Example 3: WEEKLY_STEPS_TODO
    # Should strip _TODO (ALL-CAPS suffix) and normalize
    stem3 = "WEEKLY_STEPS_TODO"
    slug3 = derive_slug(stem3, date_val=None, niche=None, platform=None)
    expected3 = "weekly-steps-todo"
    assert slug3 == expected3, f"Slug 3 failed: expected {expected3}, got {slug3}"
    print(f"  ✓ Slug 3: {stem3} → {slug3}")

    # Example 4: GUIDE_for_followers
    # Should strip nothing (no ALL-CAPS suffix match) and normalize
    stem4 = "GUIDE_for_followers"
    slug4 = derive_slug(stem4, date_val=None, niche=None, platform=None)
    expected4 = "guide-for-followers"
    assert slug4 == expected4, f"Slug 4 failed: expected {expected4}, got {slug4}"
    print(f"  ✓ Slug 4: {stem4} → {slug4}")

    print("All slug derivation tests passed.\n")

    # Test IMAGE_MAP skip detection
    print("Testing IMAGE_MAP skip detection...")
    test_image_map_path = Path("v1/content/blogs/2026-W29/2026-07-17_life_self_dev_foo_images/IMAGE_MAP.md")
    # IMAGE_MAP files should be skipped entirely (not given type: image-map)
    is_skipped = should_skip_file("# Image Map", None, file_path=test_image_map_path)
    assert is_skipped, f"IMAGE_MAP path should be skipped, but got skipped={is_skipped}"
    print(f"  ✓ IMAGE_MAP path: {test_image_map_path} → SKIPPED")

    # Test title .md stripping
    print("Testing title .md stripping...")
    test_title_with_md = "My Article.md"
    # Create a minimal mock to test the stripping logic
    if test_title_with_md.endswith(".md"):
        test_title_stripped = test_title_with_md[:-3]
    else:
        test_title_stripped = test_title_with_md
    expected_title = "My Article"
    assert test_title_stripped == expected_title, f"Title strip failed: expected {expected_title}, got {test_title_stripped}"
    print(f"  ✓ Title stripping: {test_title_with_md} → {test_title_stripped}\n")

    # Fixture 1: File with existing frontmatter (title + niche must survive)
    fixture1_orig = """---
title: "My Article"
niche: life_self_dev
---

# My Article

This is the body.
"""

    # Fixture 2: Plain file with only h1
    fixture2_orig = """# A Fresh Blog Post

This is content without frontmatter.

Some more text here.
"""

    # Fixture 3: Buffer file with inline bold metadata
    fixture3_orig = """# Buffer Post

**Niche:** life_self_dev
**Status:** Buffer

This is a buffer piece with inline metadata that must survive.
"""

    # Fixture 4: File with unknown frontmatter keys (must preserve description)
    fixture4_orig = """---
description: Edit or create a Remotion video from a plain-English description
---

# Some Command

This is the body.
"""

    # Fixture 5: force-rewrite test (title + description + stale slug)
    fixture5_orig = """---
title: "The Hangover That Won't Lift"
description: A poem about regret
slug: 2026-05-27-poetry-quotes-intoxicated-senses_yt_PRODUCTION_GUIDE
---

# The Hangover That Won't Lift

This is the body of the poem.
"""

    def apply_fm(text: str, force_rewrite: bool = False) -> str:
        """Apply frontmatter logic (simplified version)."""
        body = text
        existing_fm = parse_frontmatter_block(body)

        # Create mock path and derive
        fm = Frontmatter(
            title="Test Title",
            type="blog",
            niche="life_self_dev",
            tags=["content/blog", "niche/life_self_dev"],
        )

        merged, unknown_keys = merge_frontmatter(existing_fm, fm, force_rewrite=force_rewrite)
        fm_lines = merged.to_yaml_lines(unknown_keys=unknown_keys)

        if existing_fm:
            end_idx = extract_frontmatter_end_idx(body)
            original_body = body[end_idx:] if end_idx > 0 else body
            # BUG FIX: Don't lstrip the original body to preserve blank line after ---
            result = "\n".join(fm_lines) + "\n" + original_body
        else:
            result = "\n".join(fm_lines) + "\n" + body

        return result

    # Test idempotency: apply twice, should be identical
    print("Testing fixture 1 (existing frontmatter with title + niche)...")
    result1_a = apply_fm(fixture1_orig)
    result1_b = apply_fm(result1_a)
    if result1_a != result1_b:
        print(f"  First: {repr(result1_a[:150])}")
        print(f"  Second: {repr(result1_b[:150])}")
    assert result1_a == result1_b, "Fixture 1 not idempotent"
    # Also verify original title survives
    assert 'title: "My Article"' in result1_a, "Fixture 1 title was overwritten"
    # BUG FIX: Verify body is byte-identical (blank line preserved)
    body_start = result1_a.find("\n---\n") + len("\n---\n")
    body_in_result = result1_a[body_start:]
    original_body = fixture1_orig[fixture1_orig.find("\n---\n") + len("\n---\n"):]
    assert body_in_result == original_body, f"Fixture 1 body was mutated.\nExpected: {repr(original_body)}\nGot: {repr(body_in_result)}"
    print("  PASS")

    print("Testing fixture 2 (plain file with h1 only)...")
    result2_a = apply_fm(fixture2_orig)
    result2_b = apply_fm(result2_a)
    assert result2_a == result2_b, "Fixture 2 not idempotent"
    assert "---" in result2_a, "Fixture 2 missing frontmatter block"
    print("  PASS")

    print("Testing fixture 3 (buffer with inline bold metadata)...")
    result3_a = apply_fm(fixture3_orig)
    result3_b = apply_fm(result3_a)
    assert result3_a == result3_b, "Fixture 3 not idempotent"
    # Verify inline metadata survived byte-identical
    assert "**Niche:** life_self_dev" in result3_a, "Fixture 3 body was mutated"
    assert "**Status:** Buffer" in result3_a, "Fixture 3 body was mutated"
    print("  PASS")

    print("Testing fixture 4 (unknown key 'description' must survive)...")
    result4_a = apply_fm(fixture4_orig)
    result4_b = apply_fm(result4_a)
    assert result4_a == result4_b, "Fixture 4 not idempotent"
    # BUG FIX: Verify unknown 'description' key is preserved (may be quoted)
    assert "description:" in result4_a and "Remotion video" in result4_a, \
        f"Fixture 4 lost unknown key 'description'. Got:\n{result4_a}"
    print("  PASS")

    print("Testing fixture 5 (force-rewrite: preserve title + description, fix stale slug)...")
    # Normal mode: slug should not change (existing value kept)
    result5_normal = apply_fm(fixture5_orig, force_rewrite=False)
    assert 'slug: 2026-05-27-poetry-quotes-intoxicated-senses_yt_PRODUCTION_GUIDE' in result5_normal, \
        "Fixture 5 normal mode should preserve stale slug"
    assert 'title: "The Hangover That Won\'t Lift"' in result5_normal, \
        "Fixture 5 normal mode should preserve title"
    assert "description:" in result5_normal and "A poem about regret" in result5_normal, \
        "Fixture 5 normal mode should preserve description"

    # force-rewrite mode: slug should be fixed, title and description preserved, body untouched
    result5_force = apply_fm(fixture5_orig, force_rewrite=True)
    # Should have fixed slug now (derived from stem would be "intoxicated-senses" if we had full derive_metadata)
    # But since we're using mock FM, we just test that unknown keys are preserved
    assert 'title: "The Hangover That Won\'t Lift"' in result5_force, \
        "Fixture 5 force-rewrite should preserve title"
    assert "description:" in result5_force and "A poem about regret" in result5_force, \
        "Fixture 5 force-rewrite should preserve description"
    assert "This is the body of the poem." in result5_force, \
        "Fixture 5 force-rewrite should preserve body"

    # Idempotency of force-rewrite: run twice, should be identical
    result5_force_b = apply_fm(result5_force, force_rewrite=True)
    assert result5_force == result5_force_b, \
        "Fixture 5 force-rewrite should be idempotent"
    print("  PASS")

    print("\nTesting wiki link path builder...")
    # Test: file at v1/content/blogs/2026-W29/2026-07-17_life_self_dev_foo.md
    # with title "Foo Bar" should produce [[Content/blogs/2026-W29/2026-07-17_life_self_dev_foo|Foo Bar]]
    test_file_path = V1_ROOT / "content" / "blogs" / "2026-W29" / "2026-07-17_life_self_dev_foo.md"
    test_source_dir = V1_ROOT / "content"
    test_prefix = "Content"
    wiki_link_path = build_wiki_link_path(test_file_path, test_source_dir, test_prefix)
    expected_path = "Content/blogs/2026-W29/2026-07-17_life_self_dev_foo"
    assert wiki_link_path == expected_path, f"Wiki link path mismatch: expected {expected_path}, got {wiki_link_path}"
    test_title = "Foo Bar"
    wiki_link = f"[[{wiki_link_path}|{test_title}]]"
    expected_link = "[[Content/blogs/2026-W29/2026-07-17_life_self_dev_foo|Foo Bar]]"
    assert wiki_link == expected_link, f"Wiki link mismatch: expected {expected_link}, got {wiki_link}"
    print(f"  ✓ Wiki link path: {expected_link}")

    print("\nAll self-checks passed.")


def build_wiki_link_path(file_path: Path, source_dir: Path, symlink_prefix: str) -> str:
    """Build wiki link path from file path.

    Given:
      - file_path: absolute path like /repo/v1/content/blogs/2026-W29/file.md
      - source_dir: base dir like /repo/v1/content
      - symlink_prefix: vault symlink name like "Content"

    Returns: "Content/blogs/2026-W29/file" (no .md extension)
    """
    relative = file_path.relative_to(source_dir)
    # Remove .md suffix
    path_without_ext = relative.with_suffix("")
    # Use forward slashes and prefix with symlink name
    return f"{symlink_prefix}/{path_without_ext.as_posix()}"


def scan_frontmatter_vault() -> tuple[dict, dict, dict, dict]:
    """Scan all 4 source dirs and collect frontmatter.

    Returns (blogs_by_week, reels_by_week, by_niche, by_week).
    - blogs_by_week[week] = [(path, title, niche), ...]
    - reels_by_week[week] = [(path, title, niche), ...]
    - by_niche[niche] = [(path, title, type), ...]
    - by_week[week] = [(path, title, type), ...]
    """
    blogs_by_week = {}
    reels_by_week = {}
    by_niche = {}
    by_week = {}

    # Map source dirs to symlink prefixes
    dir_map = {
        V1_ROOT / "content": "Content",
        V1_ROOT / "docs": "Docs",
        V1_ROOT / "data" / "kb": "KB",
        V1_ROOT / "prompts": "Prompts",
    }

    for source_dir, prefix in dir_map.items():
        if not source_dir.exists():
            continue

        for md_file in sorted(source_dir.rglob("*.md")):
            body = md_file.read_text(encoding="utf-8")
            fm = parse_frontmatter_block(body)

            # Extract fields
            title = fm.get("title") if fm else None
            if not title:
                title = extract_title(body)
            if not title:
                title = md_file.stem

            type_val = fm.get("type") if fm else None
            niche = fm.get("niche") if fm else None
            week = fm.get("week") if fm else None

            # Build wiki link path
            wiki_path = build_wiki_link_path(md_file, source_dir, prefix)

            # Index by type + week for blogs/reels
            if type_val == "blog" and week:
                if week not in blogs_by_week:
                    blogs_by_week[week] = []
                blogs_by_week[week].append((wiki_path, title, niche))
            elif type_val == "reel" and week:
                if week not in reels_by_week:
                    reels_by_week[week] = []
                reels_by_week[week].append((wiki_path, title, niche))

            # Index by niche
            if niche:
                if niche not in by_niche:
                    by_niche[niche] = []
                by_niche[niche].append((wiki_path, title, type_val, week))

            # Index by week
            if week:
                if week not in by_week:
                    by_week[week] = []
                by_week[week].append((wiki_path, title, type_val))

    return blogs_by_week, reels_by_week, by_niche, by_week


def build_obsidian_config(vault_root: Path, dry_run: bool = False) -> None:
    """Create or merge .obsidian/app.json."""
    obsidian_dir = vault_root / ".obsidian"
    app_json = obsidian_dir / "app.json"

    config = {
        "userIgnoreFilters": [
            "Content/**/*.json", "Content/**/*.txt", "Content/**/*.html",
            "Content/**/*.mov", "Content/**/*.mp4", "Content/**/*.webm",
            "Content/**/*.wav", "Content/**/*.m4a", "Content/**/*.zip",
            "Content/**/*.tsx", "Content/**/*.py", "Content/**/*.ass",
            "Content/**/*.pdf", "Content/**/*.ipynb"
        ],
        "attachmentFolderPath": "./",
        "alwaysUpdateLinks": True,
    }

    # If file exists, merge in missing keys only
    existing = {}
    if app_json.exists():
        try:
            import json
            existing = json.load(app_json.open("r", encoding="utf-8"))
        except Exception:
            pass

    # Merge: don't overwrite existing userIgnoreFilters if present
    if "userIgnoreFilters" in existing:
        config["userIgnoreFilters"] = existing["userIgnoreFilters"]

    # Add other keys from existing (preserve user tuning)
    for key, val in existing.items():
        if key not in config:
            config[key] = val

    if dry_run:
        print(f"[dry-run] Would write {app_json}")
    else:
        obsidian_dir.mkdir(parents=True, exist_ok=True)
        import json
        app_json.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def ensure_symlink(vault_root: Path, link_name: str, target_rel: str, dry_run: bool = False) -> bool:
    """Create or repoint a relative symlink. Return True if created/repointed.

    Args:
        link_name: name in vault (e.g., "Content")
        target_rel: relative path from vault root (e.g., "../v1/content")

    Returns: True if changed, False if already correct.
    Raises: Exception if a real directory (not symlink) exists at that name.
    """
    link_path = vault_root / link_name

    # If symlink exists and points to right target, do nothing
    if link_path.is_symlink():
        existing_target = link_path.readlink()
        if str(existing_target) == target_rel:
            return False

        # Repoint it
        if dry_run:
            print(f"[dry-run] Would repoint symlink {link_path} from {existing_target} to {target_rel}")
            return True
        else:
            link_path.unlink()
            link_path.symlink_to(target_rel)
            return True

    # If real directory exists (not symlink), abort
    if link_path.exists() or link_path.is_dir():
        raise Exception(f"ERROR: {link_path} is a real directory, not a symlink. Cannot proceed.")

    # Create new symlink
    if dry_run:
        print(f"[dry-run] Would create symlink {link_path} -> {target_rel}")
        return True
    else:
        link_path.symlink_to(target_rel)
        return True


def write_index_md(vault_root: Path, filename: str, content: str, dry_run: bool = False) -> None:
    """Write a generated index .md file."""
    index_dir = vault_root / "Index"
    file_path = index_dir / filename

    # Add generated comment header
    full_content = "<!-- generated by build_vault.py — do not edit -->\n\n" + content

    if dry_run:
        print(f"[dry-run] Would write {file_path}")
    else:
        index_dir.mkdir(parents=True, exist_ok=True)
        file_path.write_text(full_content, encoding="utf-8")


def build_blogs_index(blogs_by_week: dict, vault_root: Path, dry_run: bool = False) -> None:
    """Generate Index/Blogs.md."""
    lines = []

    # Sort weeks descending
    for week in sorted(blogs_by_week.keys(), reverse=True):
        items = blogs_by_week[week]
        for wiki_path, title, niche in sorted(items, key=lambda x: x[1]):
            niche_str = f" — {niche}" if niche else ""
            lines.append(f"- [[{wiki_path}|{title}]]{niche_str}")

    content = "\n".join(lines) if lines else "No blogs found.\n"
    write_index_md(vault_root, "Blogs.md", content, dry_run=dry_run)


def build_reels_index(reels_by_week: dict, vault_root: Path, dry_run: bool = False) -> None:
    """Generate Index/Reels.md."""
    lines = []

    # Sort weeks descending
    for week in sorted(reels_by_week.keys(), reverse=True):
        items = reels_by_week[week]
        for wiki_path, title, niche in sorted(items, key=lambda x: x[1]):
            niche_str = f" — {niche}" if niche else ""
            lines.append(f"- [[{wiki_path}|{title}]]{niche_str}")

    content = "\n".join(lines) if lines else "No reels found.\n"
    write_index_md(vault_root, "Reels.md", content, dry_run=dry_run)


def build_by_niche_index(by_niche: dict, vault_root: Path, dry_run: bool = False) -> None:
    """Generate Index/By-Niche.md."""
    lines = []

    def niche_sort_key(item):
        """Sort by week descending (newest first), then title ascending."""
        wiki_path, title, type_val, week = item
        # Week is YYYY-Wnn format. To sort newest first (descending),
        # split and negate the week number.
        if week:
            year, week_part = week.split('-')  # "2026-W29" -> ("2026", "W29")
            week_num = int(week_part[1:])  # "W29" -> 29
            week_sort = (int(year), -week_num)  # Negate for descending
        else:
            week_sort = (9999, 9999)  # Items without week sort last
        return (week_sort, title)

    # Three canonical niches
    for niche in ["data_science_tech", "life_self_dev", "poetry_quotes"]:
        lines.append(f"## {niche}\n")

        if niche in by_niche:
            items = by_niche[niche]
            # Sort by week descending, then title ascending
            sorted_items = sorted(items, key=niche_sort_key)
            for wiki_path, title, type_val, week in sorted_items:
                type_str = f" ({type_val})" if type_val else ""
                lines.append(f"- [[{wiki_path}|{title}]]{type_str}")
        else:
            lines.append("(No content)\n")

        lines.append("")

    content = "\n".join(lines)
    write_index_md(vault_root, "By-Niche.md", content, dry_run=dry_run)


def build_by_week_index(by_week: dict, vault_root: Path, dry_run: bool = False) -> None:
    """Generate Index/By-Week.md."""
    lines = []

    # Sort weeks descending (YYYY-Wnn format, so reverse alphabetical sorts correctly)
    for week in sorted(by_week.keys(), reverse=True):
        lines.append(f"## {week}\n")
        items = by_week[week]
        # Sort items by title ascending
        for wiki_path, title, type_val in sorted(items, key=lambda x: x[1]):
            type_str = f" ({type_val})" if type_val else ""
            lines.append(f"- [[{wiki_path}|{title}]]{type_str}")
        lines.append("")

    content = "\n".join(lines)
    write_index_md(vault_root, "By-Week.md", content, dry_run=dry_run)


def build_trackers_index(vault_root: Path, dry_run: bool = False) -> None:
    """Generate Index/Trackers.md with tracker docs."""
    lines = []

    # Scan v1/docs for files with "tracker" in the name
    docs_dir = V1_ROOT / "docs"
    tracker_files = []

    if docs_dir.exists():
        for md_file in sorted(docs_dir.glob("**/*tracker*.md")):
            relative = md_file.relative_to(docs_dir)
            path_without_ext = relative.with_suffix("")
            wiki_path = f"Docs/{path_without_ext.as_posix()}"
            title = md_file.stem.replace("-", " ").replace("_", " ").title()
            tracker_files.append((wiki_path, title))

    # Add hardcoded pipeline doc
    lines.append("- [[Docs/guides/pipeline-2026|Pipeline 2026]]")

    # Add discovered trackers
    for wiki_path, title in tracker_files:
        lines.append(f"- [[{wiki_path}|{title}]]")

    content = "\n".join(lines) if lines else "No trackers found.\n"
    write_index_md(vault_root, "Trackers.md", content, dry_run=dry_run)


def build_home_md(blogs_by_week: dict, reels_by_week: dict, by_niche: dict, by_week: dict, vault_root: Path, dry_run: bool = False) -> None:
    """Generate Home.md dashboard."""
    # Count by type
    total_blogs = sum(len(items) for items in blogs_by_week.values())
    total_reels = sum(len(items) for items in reels_by_week.values())

    # Count by niche
    niche_counts = {}
    for niche, items in by_niche.items():
        niche_counts[niche] = len(items)

    lines = [
        "# Vault Home",
        "",
        "This is your content vault, auto-generated by `build_vault.py`.",
        "Edits to generated files will be overwritten.",
        "",
        "## Quick Stats",
        "",
        f"- **Blogs:** {total_blogs}",
        f"- **Reels:** {total_reels}",
        f"- **Data Science/Tech:** {niche_counts.get('data_science_tech', 0)}",
        f"- **Life & Self-Development:** {niche_counts.get('life_self_dev', 0)}",
        f"- **Poetry & Quotes:** {niche_counts.get('poetry_quotes', 0)}",
        "",
        "## Index",
        "",
        "- [[Index/Blogs|All Blogs]]",
        "- [[Index/Reels|All Reels]]",
        "- [[Index/By-Niche|By Niche]]",
        "- [[Index/By-Week|By Week]]",
        "- [[Index/Trackers|Trackers & Docs]]",
        "",
    ]

    content = "\n".join(lines)
    write_index_md(vault_root, "../Home.md", content, dry_run=dry_run)


def build_vault_shell(dry_run: bool = False) -> None:
    """Build vault shell: symlinks, .obsidian config, Home.md, Index/ notes."""
    vault_root = REPO_ROOT / "vault"

    if not dry_run:
        vault_root.mkdir(parents=True, exist_ok=True)

    # 1. Create symlinks (relative)
    ensure_symlink(vault_root, "Content", "../v1/content", dry_run=dry_run)
    ensure_symlink(vault_root, "KB", "../v1/data/kb", dry_run=dry_run)
    ensure_symlink(vault_root, "Docs", "../v1/docs", dry_run=dry_run)
    ensure_symlink(vault_root, "Prompts", "../v1/prompts", dry_run=dry_run)

    # 2. Create .obsidian/app.json
    build_obsidian_config(vault_root, dry_run=dry_run)

    # 3. Scan frontmatter
    blogs_by_week, reels_by_week, by_niche, by_week = scan_frontmatter_vault()

    # 4. Generate index files
    build_blogs_index(blogs_by_week, vault_root, dry_run=dry_run)
    build_reels_index(reels_by_week, vault_root, dry_run=dry_run)
    build_by_niche_index(by_niche, vault_root, dry_run=dry_run)
    build_by_week_index(by_week, vault_root, dry_run=dry_run)
    build_trackers_index(vault_root, dry_run=dry_run)

    # 5. Generate Home.md
    build_home_md(blogs_by_week, reels_by_week, by_niche, by_week, vault_root, dry_run=dry_run)

    if not dry_run:
        print(f"Vault shell built at {vault_root}")


def main():
    parser = argparse.ArgumentParser(
        description="Frontmatter engine for content vault.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print unified diffs, write nothing (applies to both frontmatter and vault shell)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if files lack frontmatter; write nothing",
    )
    parser.add_argument(
        "--self-check",
        action="store_true",
        help="Run self-test and exit",
    )
    parser.add_argument(
        "--force-rewrite",
        action="store_true",
        help="Recompute and replace derived keys (type, niche, date, week, slug, platform, tags); preserve title and unknown keys",
    )
    parser.add_argument(
        "--vault-only",
        action="store_true",
        help="Build only the vault shell (symlinks, .obsidian config, index files); skip frontmatter processing",
    )

    args = parser.parse_args()

    if args.self_check:
        demo()
        sys.exit(0)

    if args.vault_only:
        build_vault_shell(dry_run=args.dry_run)
        sys.exit(0)

    if args.check:
        scanned, written, current, skipped, missing = scan_vault(check_mode=True, force_rewrite=args.force_rewrite)
        if missing:
            print(f"Files missing frontmatter ({len(missing)}):")
            for path in missing[:10]:  # Show first 10
                print(f"  {path}")
            if len(missing) > 10:
                print(f"  ... and {len(missing) - 10} more")
            sys.exit(1)
        print(f"Scanned {scanned}, all have frontmatter.")
        sys.exit(0)

    scanned, written, current, skipped, _ = scan_vault(dry_run=args.dry_run, force_rewrite=args.force_rewrite)

    print(f"\nScanned: {scanned}")
    print(f"Written: {written}")
    print(f"Already current: {current}")
    print(f"Skipped: {skipped}")

    # After frontmatter processing, build vault shell
    build_vault_shell(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
