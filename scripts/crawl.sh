#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SOURCE_KEY="${1:-lifull_aomori_listings}"
FORCE="${2:-false}"

export DATABASE_URL_SYNC="${DATABASE_URL_SYNC:-postgresql://tsubo:tsubo@localhost:5432/tsubo}"
export PYTHONPATH="$ROOT/services/api:$ROOT/services/ingest:$ROOT/packages/contracts/python:$ROOT/sources"
export TSUBO_LOCAL_SNAPSHOT_ROOT="$ROOT/data/snapshots"

echo "==> Crawling source_key=$SOURCE_KEY force=$FORCE"
python3 - <<PY
from tsubo_ingest.pipeline import IngestionPipeline

pipeline = IngestionPipeline()
result = pipeline.crawl_source_key("${SOURCE_KEY}", force=False if "${FORCE}" == "false" else True, max_details=10)
print(result)
PY

echo "==> Crawl complete"
