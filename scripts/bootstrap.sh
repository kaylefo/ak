#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> Bootstrapping Tsubo"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required" >&2
  exit 1
fi

if [ ! -f .env ]; then
  echo "==> Copying .env.example to .env"
  cp .env.example .env
else
  echo "==> .env already exists, skipping copy"
fi

echo "==> Creating Python virtual environment"
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Installing Python dependencies"
pip install --upgrade pip
pip install -r services/api/requirements.txt
pip install -r services/ingest/requirements.txt
pip install -r services/worker/requirements.txt
pip install -r tests/requirements.txt

if command -v pnpm >/dev/null 2>&1; then
  echo "==> Installing Node dependencies"
  pnpm install
else
  echo "==> pnpm not found, skipping Node install"
fi

echo "==> Bootstrap complete"
