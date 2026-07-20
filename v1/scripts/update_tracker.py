#!/usr/bin/env python3
"""Direct field editing for content-tracker.md records, then regenerate the HTML.

    python3 scripts/update_tracker.py <slug> --set field=value [--set field=value ...]
    python3 scripts/update_tracker.py <slug> --append-note "note text"
    python3 scripts/update_tracker.py --list

No Claude involved — direct validation and write.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_tracker_html import DEFAULT_MD, parse_md  # noqa: E402
from lib.tracker_update import set_field, append_note, StaleValueError  # noqa: E402


def resolve_row(query: str) -> str:
    """Resolve a slug or title fragment to an exact slug."""
    records, errors = parse_md(DEFAULT_MD.read_text(encoding="utf-8"))
    if errors:
        raise SystemExit(f"tracker does not parse: {errors[0]}")
    if any(r["slug"] == query for r in records):
        return query
    q = query.lower()
    hits = [r for r in records if q in r["slug"].lower() or q in r["title"].lower()]
    if not hits:
        raise SystemExit(f"no record matches {query!r} — try --list")
    if len(hits) > 1:
        lines = "\n".join(f"  {r['slug']}\n      {r['title']}" for r in hits[:10])
        raise SystemExit(f"{len(hits)} records match {query!r}; be more specific:\n{lines}")
    return hits[0]["slug"]


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("row", nargs="?", help="slug, or a unique fragment of the slug/title")
    ap.add_argument("--set", action="append", dest="sets", metavar="FIELD=VALUE",
                    help="set a field (repeatable)")
    ap.add_argument("--append-note", metavar="TEXT",
                    help="append a note")
    ap.add_argument("--list", action="store_true", help="list every row and exit")
    args = ap.parse_args()

    if args.list:
        records, _ = parse_md(DEFAULT_MD.read_text(encoding="utf-8"))
        for r in sorted(records, key=lambda r: r["date"], reverse=True):
            print(f"{r['date']}  {r['slug']}\n            {r['title'][:70]}")
        return 0

    if not args.row:
        ap.error("need a row (or --list)")

    if not (args.sets or args.append_note):
        ap.error("need at least one --set or --append-note")

    slug = resolve_row(args.row)
    any_changed = False

    # Process --set directives
    if args.sets:
        for assignment in args.sets:
            if "=" not in assignment:
                print(f"error: --set requires FIELD=VALUE format, got {assignment!r}")
                return 1

            field, value = assignment.split("=", 1)
            field = field.strip()
            value = value.strip()

            try:
                result = set_field(slug, field, value)
                if result["changed"]:
                    print(f"{slug}")
                    print(f"  {field}: {result['old']} → {result['new']}")
                    any_changed = True
                else:
                    print(f"{slug}")
                    print(f"  ({result['message']})")
            except ValueError as e:
                print(f"error: {e}")
                return 1
            except StaleValueError as e:
                print(f"error: {e}")
                return 1
            except KeyError as e:
                print(f"error: {e}")
                return 1
            except RuntimeError as e:
                print(f"error: {e}")
                return 1

    # Process --append-note
    if args.append_note:
        try:
            result = append_note(slug, args.append_note)
            print(f"{slug}")
            print(f"  notes += {result['appended']}")
            any_changed = True
        except KeyError as e:
            print(f"error: {e}")
            return 1
        except RuntimeError as e:
            print(f"error: {e}")
            return 1

    # Regenerate HTML if anything changed
    if any_changed:
        subprocess.run([sys.executable, str(Path(__file__).parent / "generate_tracker_html.py")],
                       check=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
