from __future__ import annotations

from typing import Any

from temporalio import activity
from tsubo_ingest.discovery import discover_sources


@activity.defn(name="discover_sources")
async def discover_sources_activity(
    entity_type: str,
    entity_code: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Discover candidate sources for a geography entity."""
    activity.logger.info(
        "discover_sources_activity_started",
        entity_type=entity_type,
        entity_code=entity_code,
        dry_run=dry_run,
    )
    result = await discover_sources(entity_type, entity_code, dry_run=dry_run)
    activity.logger.info(
        "discover_sources_activity_finished",
        candidates_found=result.get("candidates_found"),
    )
    return result
