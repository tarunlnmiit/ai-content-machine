#!/usr/bin/env bash
# Rotate content buffer after consuming week-1.
# Safety: verifies week-4 exists before touching anything.
# Usage: bash scripts/shift_buffer.sh [--dry-run]

set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
BUFFER="$REPO/content/buffer"
TOPICS="$REPO/data/buffer/topics.yaml"
DRY_RUN=false

[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

die() { echo "ERROR: $*" >&2; exit 1; }
say() { echo "[shift_buffer] $*"; }

# --- Safety checks ---
[[ -d "$BUFFER/week-1" ]] || die "week-1 not found — nothing to rotate"
[[ -d "$BUFFER/week-4" ]] || die "week-4 does not exist — fill buffer before rotating"

# Confirm week-4 has actual content (at least 1 _meta.md per niche)
for niche in data_science_tech life_self_dev poetry_quotes; do
    count=$(ls "$BUFFER/week-4/$niche/"*_meta.md 2>/dev/null | wc -l | tr -d ' ')
    [[ "$count" -gt 0 ]] || die "week-4/$niche is empty — fill before rotating"
done

say "Pre-rotation state:"
for w in 1 2 3 4; do
    count=$(ls "$BUFFER/week-$w/"*/*_meta.md 2>/dev/null | wc -l | tr -d ' ')
    say "  week-$w: $count items"
done

if $DRY_RUN; then
    say "DRY RUN — no changes made"
    say "Would: rm -rf week-1 | week-2→1 | week-3→2 | week-4→3"
    exit 0
fi

# --- Rotate ---
say "Removing week-1..."
rm -rf "$BUFFER/week-1"

say "Rotating week-2 → week-1..."
mv "$BUFFER/week-2" "$BUFFER/week-1"

say "Rotating week-3 → week-2..."
mv "$BUFFER/week-3" "$BUFFER/week-2"

say "Rotating week-4 → week-3..."
mv "$BUFFER/week-4" "$BUFFER/week-3"

# --- Update topics.yaml week numbers ---
if [[ -f "$TOPICS" ]]; then
    say "Updating $TOPICS week numbers..."
    # Shift week-4→3, week-3→2, week-2→1 in-place (reverse order to avoid collisions)
    sed -i '' \
        -e 's/^week-4:/week-3:/g' \
        -e 's/^  week-4:/  week-3:/g' \
        "$TOPICS" 2>/dev/null || true
    sed -i '' \
        -e 's/^week-3:/week-2:/g' \
        -e 's/^  week-3:/  week-2:/g' \
        "$TOPICS" 2>/dev/null || true
    sed -i '' \
        -e 's/^week-2:/week-1:/g' \
        -e 's/^  week-2:/  week-1:/g' \
        "$TOPICS" 2>/dev/null || true
fi

say "Done. week-3 is now the latest filled week."
say "Next: add week-4 topics to $TOPICS, then:"
say "  conda run -n content_engine_env python3 scripts/generate_buffer.py --week 4"
