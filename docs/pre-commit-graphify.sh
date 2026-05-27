#!/bin/bash
# Pre-commit hook template: keeps graphify knowledge graph in sync.
#
# Install:
#   cp docs/pre-commit-graphify.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# Skip on any commit: git commit --no-verify
# Uninstall:         rm .git/hooks/pre-commit

REPO="$(git rev-parse --show-toplevel)"
cd "$REPO" || exit 0

if git diff --cached --name-only | grep -qE '\.(py|md|js|ts)$'; then
  if command -v graphify >/dev/null 2>&1; then
    echo "[pre-commit] graphify update (AST-only, no API)"
    graphify update . >/dev/null 2>&1 || echo "[pre-commit] graphify warned (continuing)"
    [ -d graphify-out ] && git add graphify-out/ 2>/dev/null
  fi
fi

exit 0
