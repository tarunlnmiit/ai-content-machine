#!/bin/bash
# Daily idea-fetch pipeline. Runs all free sources → rescore → weekly_ideas.md
# Triggered by launchd (com.contentmachine.dailyideas) at 06:00 every day.
# Manual: bash scripts/daily_ideas.sh

set -uo pipefail

REPO="/Users/tarungupta/Making It Big/Claude/content-machine"
cd "$REPO" || exit 1

PY="/Users/tarungupta/miniconda3/envs/content_engine_env/bin/python3.14"
[ -x "$PY" ] || PY="python3"

LOG_DIR="$REPO/data/analytics"
mkdir -p "$LOG_DIR"
TS=$(date '+%Y-%m-%d %H:%M:%S')
echo "=== daily_ideas $TS ==="

# Retention: keep last 14 days of fetched JSONs
echo "--- retention prune ---"
find "$REPO/data/ideas" -maxdepth 1 -name "reddit_*.json"   -mtime +14 -delete -print 2>/dev/null | wc -l | xargs echo "  reddit removed:"
find "$REPO/data/ideas" -maxdepth 1 -name "youtube_*.json"  -mtime +14 -delete -print 2>/dev/null | wc -l | xargs echo "  youtube removed:"
find "$REPO/data/ideas" -maxdepth 1 -name "external_*.json" -mtime +14 -delete -print 2>/dev/null | wc -l | xargs echo "  external removed:"
find "$REPO/data/ideas" -maxdepth 1 -name "suggest_*.json"  -mtime +14 -delete -print 2>/dev/null | wc -l | xargs echo "  suggest removed:"

# Log rotation: cap files at last 2000 lines
echo "--- log rotation ---"
for log in /tmp/daily_ideas.log /tmp/daily_ideas.error.log "$LOG_DIR/scheduler.log" "$LOG_DIR/scheduler.error.log"; do
  if [ -f "$log" ] && [ "$(wc -l < "$log" 2>/dev/null)" -gt 2000 ]; then
    tail -2000 "$log" > "${log}.tmp" && mv "${log}.tmp" "$log"
    echo "  rotated: $log"
  fi
done

run() {
  local label="$1"; shift
  echo "--- $label ---"
  if "$@"; then
    echo "  ✓ $label ok"
  else
    echo "  ✗ $label failed (continuing)"
  fi
}

run "reddit"          "$PY" scripts/rss_scraper.py
run "youtube"         "$PY" scripts/youtube_scraper.py
run "external_feeds"  "$PY" scripts/fetch_external_feeds.py
run "google_suggest"  "$PY" scripts/fetch_google_suggest.py --quick
run "idea_scorer"     "$PY" scripts/idea_scorer.py

echo "=== done $(date '+%Y-%m-%d %H:%M:%S') ==="
