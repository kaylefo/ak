#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export DATABASE_URL_SYNC="${DATABASE_URL_SYNC:-postgresql://tsubo:tsubo@localhost:5432/tsubo}"
export PYTHONPATH="$ROOT/services/api:$ROOT/packages/contracts/python"

echo "==> Downloading municipality CSV if needed"
bash "$ROOT/scripts/download_municipalities.sh"

echo "==> Importing municipalities from official-derived address CSV"
python3 "$ROOT/services/api/scripts/import_municipalities.py"

echo "==> Seeding source registry"
python3 "$ROOT/services/api/scripts/seed.py"

echo "==> Seed complete"
