from __future__ import annotations

from typing import Any

from temporalio import activity
from tsubo_api.search import index_listing_batch, reindex_all


@activity.defn(name="reindex_all")
async def reindex_all_activity(batch_size: int = 500) -> dict[str, Any]:
    """Rebuild the full listings search index."""
    activity.logger.info("reindex_all_activity_started", batch_size=batch_size)
    result = await reindex_all(batch_size=batch_size)
    activity.logger.info("reindex_all_activity_finished", indexed=result.get("indexed"))
    return result


@activity.defn(name="index_listing_batch")
async def index_listing_batch_activity(listing_ids: list[str]) -> dict[str, Any]:
    """Index a batch of listings."""
    activity.logger.info("index_listing_batch_activity_started", count=len(listing_ids))
    result = await index_listing_batch(listing_ids)
    activity.logger.info("index_listing_batch_activity_finished", indexed=result.get("indexed"))
    return result
