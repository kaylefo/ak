#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

export DATABASE_URL_SYNC="${DATABASE_URL_SYNC:-postgresql://tsubo:tsubo@localhost:5432/tsubo}"
export PYTHONPATH="$ROOT/services/api:$ROOT/packages/contracts/python"

echo "==> Seeding geography, sources, coverage, and fixture listings"
python3 "$ROOT/services/api/scripts/seed.py"
echo "==> Seed complete"
