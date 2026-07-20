#!/usr/bin/env python3
"""Direct field editing for content-tracker.md records.

Validates and applies field changes with re-validation guards. No Claude involved —
the direct path reuses all validation logic from the previous Claude path.

Usage:
    from lib.tracker_update import set_field, append_note
    set_field("2026-07-17_life_...", "carousel.status", "posted", expected="scheduled")
    append_note("2026-07-17_life_...", "Posted to Instagram. https://...")
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from generate_tracker_html import (  # noqa: E402
    DASH,
    REQUIRED_FIELDS,
    HEADER_RE,
    IMMUTABLE,
    EDITABLE,
    ENUMS,
    URL_FIELDS,
    DATE_FIELDS,
    VALUE_COL,
    parse_md,
)


class StaleValueError(Exception):
    """Raised when expected value does not match current on-disk value.

    Carries `current` so callers can show what the file actually holds without
    parsing it back out of the message.
    """

    def __init__(self, message: str, current: str = ""):
        super().__init__(message)
        self.current = current


def validate_field(key: str, value: str) -> str:
    """Validate a single field assignment.

    Args:
        key: field name
        value: field value (may be empty string to mean "unset")

    Returns:
        cleaned value to store

    Raises:
        ValueError: if validation fails
    """
    if key not in EDITABLE:
        raise ValueError(f"field {key!r} is not editable (immutable or unknown)")

    # Empty string from a cell means "unset" → store DASH
    if not value or value.strip() == "":
        return DASH

    value = value.strip()

    if "\n" in value:
        raise ValueError(f"field {key!r} value must be a single line")

    if key in ENUMS and value not in ENUMS[key]:
        raise ValueError(
            f"field {key!r}={value!r} not in allowed values: {ENUMS[key]}"
        )

    if key in URL_FIELDS and value != DASH and not re.match(r"^https?://\S+$", value):
        raise ValueError(
            f"field {key!r} is a link column but got {value!r} — must be a full http(s):// URL"
        )

    if key in DATE_FIELDS and value != DASH and not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
        raise ValueError(f"field {key!r} must be YYYY-MM-DD, got {value!r}")

    return value


def _block_bounds(lines: list[str], slug: str) -> tuple[int, int]:
    """Find the start and end line indices of a record block."""
    start = None
    for i, line in enumerate(lines):
        m = HEADER_RE.match(line)
        if m:
            if m.group(1) == slug:
                start = i
            elif start is not None:
                return start, i
    if start is None:
        raise KeyError(f"no record with slug {slug!r}")
    return start, len(lines)


def set_field(slug: str, key: str, value: str, expected: str | None = None,
              md_path: Path | None = None) -> dict:
    """Set a single field in a record.

    Args:
        slug: record identifier
        key: field name
        value: new value (empty string means "unset" → stores DASH)
        expected: if provided, only update if current value matches this
        md_path: path to tracker MD file (defaults to v1/docs/content-tracker.md)

    Returns:
        result dict with changed field and updated record

    Raises:
        KeyError: if slug not found
        ValueError: if field validation fails
        StaleValueError: if expected value doesn't match current value
        RuntimeError: if edit would corrupt the tracker
    """
    from generate_tracker_html import DEFAULT_MD

    md_path = md_path or DEFAULT_MD

    original = md_path.read_text(encoding="utf-8")
    before, errors = parse_md(original)
    if errors:
        raise RuntimeError(f"tracker does not parse cleanly, refusing to edit: {errors[:3]}")

    by_slug = {r["slug"]: r for r in before}
    if slug not in by_slug:
        raise KeyError(f"no record with slug {slug!r}")

    if key in IMMUTABLE:
        raise ValueError(f"field {key!r} is immutable")

    # Validate the new value
    new_value = validate_field(key, value)

    # Check if current value matches expected (optimistic concurrency)
    current_value = by_slug[slug].get(key, DASH)
    if expected is not None and current_value != expected:
        raise StaleValueError(
            f"field {key!r} current value {current_value!r} does not match "
            f"expected {expected!r}",
            current=current_value,
        )

    if current_value == new_value:
        # No change needed
        return {
            "slug": slug,
            "changed": False,
            "message": f"field {key!r} already {new_value!r}",
        }

    lines = original.split("\n")
    start, end = _block_bounds(lines, slug)

    # Find and update the field line
    for i in range(start, end):
        m = re.match(r"^(\S+):([ \t]*)(.*)$", lines[i])
        if not m:
            continue
        if m.group(1) == key:
            pad = max(1, VALUE_COL - len(key) - 1)
            lines[i] = f"{key}:{' ' * pad}{new_value}"
            break

    updated = "\n".join(lines)

    # Re-validate the whole file
    after, after_errors = parse_md(updated)
    if after_errors:
        raise RuntimeError(f"edit would corrupt the tracker, aborted: {after_errors[:3]}")
    if len(after) != len(before):
        raise RuntimeError(f"record count changed {len(before)} → {len(after)}, aborted")
    for rec in after:
        if rec["slug"] == slug:
            continue
        if rec != by_slug[rec["slug"]]:
            raise RuntimeError(f"edit touched an unrelated record {rec['slug']!r}, aborted")

    # Write the updated file
    md_path.write_text(updated, encoding="utf-8")

    return {
        "slug": slug,
        "changed": True,
        "field": key,
        "old": current_value,
        "new": new_value,
    }


def append_note(slug: str, text: str, md_path: Path | None = None) -> dict:
    """Append a note to a record's notes block.

    Args:
        slug: record identifier
        text: note text to append (may span multiple lines; will be joined with spaces)
        md_path: path to tracker MD file (defaults to v1/docs/content-tracker.md)

    Returns:
        result dict with appended note text

    Raises:
        KeyError: if slug not found
        RuntimeError: if edit would corrupt the tracker
    """
    from generate_tracker_html import DEFAULT_MD

    md_path = md_path or DEFAULT_MD

    original = md_path.read_text(encoding="utf-8")
    before, errors = parse_md(original)
    if errors:
        raise RuntimeError(f"tracker does not parse cleanly, refusing to edit: {errors[:3]}")

    by_slug = {r["slug"]: r for r in before}
    if slug not in by_slug:
        raise KeyError(f"no record with slug {slug!r}")

    lines = original.split("\n")
    start, end = _block_bounds(lines, slug)

    notes_append = text.strip().replace("\n", " ")

    # Find the notes field and append to it
    for i in range(start, end):
        m = re.match(r"^(\S+):([ \t]*)(.*)$", lines[i])
        if not m:
            continue
        if m.group(1) == "notes":
            j = i + 1
            while j < end and (lines[j].startswith("  ") or not lines[j].strip()):
                j += 1
            while j > i + 1 and not lines[j - 1].strip():
                j -= 1
            body = [x for x in lines[i + 1:j] if x.strip()]
            if len(body) == 1 and body[0].strip() == DASH:
                # a lone em dash is a placeholder, not history worth keeping
                lines[i + 1] = f"  {notes_append}"
            else:
                lines.insert(j, f"  {notes_append}")
                end += 1
            break

    updated = "\n".join(lines)

    # Re-validate the whole file
    after, after_errors = parse_md(updated)
    if after_errors:
        raise RuntimeError(f"edit would corrupt the tracker, aborted: {after_errors[:3]}")
    if len(after) != len(before):
        raise RuntimeError(f"record count changed {len(before)} → {len(after)}, aborted")
    for rec in after:
        if rec["slug"] == slug:
            continue
        if rec != by_slug[rec["slug"]]:
            raise RuntimeError(f"edit touched an unrelated record {rec['slug']!r}, aborted")
    old_notes = by_slug[slug].get("notes", "")
    new_notes = next(r for r in after if r["slug"] == slug).get("notes", "")
    # notes are append-only — the one exception is overwriting a lone '—' placeholder,
    # which carries no history to lose.
    placeholder = old_notes.strip() in ("", DASH)
    if not placeholder and not new_notes.startswith(old_notes):
        raise RuntimeError("notes were modified rather than appended to, aborted")

    # Write the updated file
    md_path.write_text(updated, encoding="utf-8")

    return {
        "slug": slug,
        "appended": notes_append,
    }
