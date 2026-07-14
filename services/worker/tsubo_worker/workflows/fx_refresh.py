from __future__ import annotations

from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from tsubo_worker.activities.fx import refresh_fx_rates_activity


@workflow.defn(name="FXRefreshWorkflow")
class FXRefreshWorkflow:
    """Refresh FX rates on a schedule or ad-hoc trigger."""

    @workflow.run
    async def run(self, provider_chain: str | None = None) -> dict:
        return await workflow.execute_activity(
            refresh_fx_rates_activity,
            provider_chain,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=workflow.RetryPolicy(maximum_attempts=3),
        )
