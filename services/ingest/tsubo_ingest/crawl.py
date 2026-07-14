"""Source crawl orchestration."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


async def crawl_source(
    source_id: str,
    *,
    force: bool = False,
) -> dict[str, Any]:
    """Crawl a single registered source and return run metadata."""
    started_at = datetime.now(UTC)
    logger.info("crawl_started", source_id=source_id, force=force)

    # Placeholder crawl result; parsers plug in via sources/ registry.
    listings_seen = 0
    listings_upserted = 0
    errors: list[str] = []

    finished_at = datetime.now(UTC)
    result = {
        "source_id": source_id,
        "force": force,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "listings_seen": listings_seen,
        "listings_upserted": listings_upserted,
        "errors": errors,
        "status": "completed" if not errors else "completed_with_errors",
    }
    logger.info("crawl_finished", **{k: v for k, v in result.items() if k != "errors"})
    return result


async def crawl_sources(source_ids: list[str], *, force: bool = False) -> list[dict[str, Any]]:
    """Crawl multiple sources sequentially."""
    results: list[dict[str, Any]] = []
    for source_id in source_ids:
        results.append(await crawl_source(source_id, force=force))
    return results
