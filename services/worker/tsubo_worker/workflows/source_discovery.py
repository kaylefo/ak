from __future__ import annotations

from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from tsubo_worker.activities.discovery import discover_sources_activity


@workflow.defn(name="SourceDiscoveryWorkflow")
class SourceDiscoveryWorkflow:
    """Discover candidate sources for a geography entity."""

    @workflow.run
    async def run(self, entity_type: str, entity_code: str, dry_run: bool = False) -> dict:
        return await workflow.execute_activity(
            discover_sources_activity,
            args=[entity_type, entity_code, dry_run],
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=workflow.RetryPolicy(maximum_attempts=3),
        )
