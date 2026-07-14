#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/data/seed/municipalities_raw.csv"
URL="https://raw.githubusercontent.com/geolonia/japanese-addresses/develop/api/ja/address.csv"

mkdir -p "$(dirname "$DEST")"

if [ -f "$DEST" ]; then
  echo "==> Municipality CSV already exists at $DEST"
  exit 0
fi

echo "==> Downloading official-derived municipality address CSV"
curl -fsSL "$URL" -o "$DEST"
echo "==> Saved $(wc -l < "$DEST") lines to $DEST"
