#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BATCH_SIZE="${1:-500}"
TEMPORAL_ADDRESS="${TEMPORAL_ADDRESS:-localhost:7233}"
TEMPORAL_NAMESPACE="${TEMPORAL_NAMESPACE:-default}"
TASK_QUEUE="${TASK_QUEUE:-tsubo-worker}"

if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

export PYTHONPATH="$ROOT/services/worker:$ROOT/services/ingest:$ROOT/services/api:$ROOT/packages/contracts/python"

echo "==> Triggering IndexListingWorkflow (full reindex, batch_size=$BATCH_SIZE)"

python3 - <<PY
import asyncio
import uuid
from datetime import timedelta

from temporalio.client import Client

from tsubo_worker.workflows.index_listing import IndexListingWorkflow

async def main() -> None:
    client = await Client.connect(
        "${TEMPORAL_ADDRESS}",
        namespace="${TEMPORAL_NAMESPACE}",
    )
    handle = await client.start_workflow(
        IndexListingWorkflow.run,
        args=[None, ${BATCH_SIZE}],
        id=f"reindex-{uuid.uuid4().hex[:8]}",
        task_queue="${TASK_QUEUE}",
        execution_timeout=timedelta(hours=6),
    )
    result = await handle.result()
    print(result)

asyncio.run(main())
PY

echo "==> Reindex workflow complete"
