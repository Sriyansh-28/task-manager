#!/usr/bin/env bash
# Run the backend tests. Usage: scripts/test.sh [--install] [pytest args...]
set -euo pipefail

cd "$(dirname "$0")/../backend"

PYTHON="${PYTHON:-python}"
command -v "$PYTHON" >/dev/null 2>&1 || PYTHON=python3

if [[ "${1:-}" == "--install" ]]; then
  shift
  "$PYTHON" -m pip install -r requirements-dev.txt
fi

exec "$PYTHON" -m pytest -v "$@"
