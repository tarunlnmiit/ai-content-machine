#!/bin/bash
# Launch Content Machine dashboard.
# Usage: bash dashboard/run.sh [PORT]

REPO="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${1:-8501}"

# Try conda env first, fall back to system python3
PY="/Users/tarungupta/miniconda3/envs/content_engine_env/bin/python3.14"
[ -x "$PY" ] || PY="python3"

cd "$REPO" || exit 1

exec "$PY" -m streamlit run "$REPO/dashboard/app.py" \
  --server.port "$PORT" \
  --server.headless true \
  --browser.gatherUsageStats false
