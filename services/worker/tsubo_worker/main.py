"""Temporal worker entry point."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from temporalio.client import Client
from temporalio.worker import Worker

from tsubo_worker.activities import (
    crawl_source_activity,
    discover_sources_activity,
    index_listing_batch_activity,
    refresh_fx_rates_activity,
    reindex_all_activity,
)
from tsubo_worker.config import settings
from tsubo_worker.workflows import (
    CrawlSourceWorkflow,
    FXRefreshWorkflow,
    IndexListingWorkflow,
    SourceDiscoveryWorkflow,
)

# Ensure api package is importable alongside ingest and worker.
_ROOT = Path(__file__).resolve().parents[3]
_API_PATH = _ROOT / "services" / "api"
if str(_API_PATH) not in sys.path:
    sys.path.insert(0, str(_API_PATH))


async def run_worker() -> None:
    client = await Client.connect(
        settings.temporal_address,
        namespace=settings.temporal_namespace,
    )

    worker = Worker(
        client,
        task_queue=settings.task_queue,
        workflows=[
            FXRefreshWorkflow,
            CrawlSourceWorkflow,
            SourceDiscoveryWorkflow,
            IndexListingWorkflow,
        ],
        activities=[
            refresh_fx_rates_activity,
            crawl_source_activity,
            discover_sources_activity,
            reindex_all_activity,
            index_listing_batch_activity,
        ],
    )

    print(
        f"tsubo worker listening on {settings.temporal_address} "
        f"queue={settings.task_queue} namespace={settings.temporal_namespace}"
    )
    await worker.run()


def main() -> None:
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
