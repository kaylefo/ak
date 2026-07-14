from __future__ import annotations

from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from tsubo_worker.activities.crawl import crawl_source_activity


@workflow.defn(name="CrawlSourceWorkflow")
class CrawlSourceWorkflow:
    """Crawl a single registered source."""

    @workflow.run
    async def run(self, source_id: str, force: bool = False) -> dict:
        return await workflow.execute_activity(
            crawl_source_activity,
            args=[source_id, force],
            start_to_close_timeout=timedelta(hours=2),
            heartbeat_timeout=timedelta(minutes=5),
            retry_policy=workflow.RetryPolicy(maximum_attempts=2),
        )
