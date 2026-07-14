from __future__ import annotations

from typing import Any

from temporalio import activity
from tsubo_ingest.crawl import crawl_source


@activity.defn(name="crawl_source")
async def crawl_source_activity(source_id: str, force: bool = False) -> dict[str, Any]:
    """Crawl a single source via the ingest module."""
    activity.logger.info("crawl_source_activity_started", source_id=source_id, force=force)
    result = await crawl_source(source_id, force=force)
    activity.logger.info(
        "crawl_source_activity_finished",
        source_id=source_id,
        listings_upserted=result.get("listings_upserted"),
    )
    return result
