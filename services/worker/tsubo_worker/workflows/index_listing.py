from __future__ import annotations

from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from tsubo_worker.activities.indexing import index_listing_batch_activity, reindex_all_activity


@workflow.defn(name="IndexListingWorkflow")
class IndexListingWorkflow:
    """Rebuild or incrementally update the listings search index."""

    @workflow.run
    async def run(
        self,
        listing_ids: list[str] | None = None,
        batch_size: int = 500,
    ) -> dict:
        if listing_ids:
            return await workflow.execute_activity(
                index_listing_batch_activity,
                listing_ids,
                start_to_close_timeout=timedelta(minutes=30),
                retry_policy=workflow.RetryPolicy(maximum_attempts=3),
            )

        return await workflow.execute_activity(
            reindex_all_activity,
            batch_size,
            start_to_close_timeout=timedelta(hours=4),
            heartbeat_timeout=timedelta(minutes=10),
            retry_policy=workflow.RetryPolicy(maximum_attempts=2),
        )
