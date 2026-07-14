#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

export PYTHONPATH="$ROOT/services/api:$ROOT/services/ingest:$ROOT/services/worker:$ROOT/packages/contracts/python:$ROOT/sources"

echo "==> API tests"
pytest services/api/tests/ -v --tb=short

echo "==> Ingest tests"
pytest services/ingest/tests/ -v --tb=short

echo "==> Integration tests"
pytest tests/integration/ -v --tb=short

if command -v pnpm >/dev/null 2>&1; then
  echo "==> Web unit tests"
  pnpm --filter @tsubo/web test
fi

echo "==> All verification checks passed"
