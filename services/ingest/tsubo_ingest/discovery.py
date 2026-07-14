"""Source discovery for administrative geography."""

from __future__ import annotations

from typing import Any

import structlog
from tsubo_contracts.enums import CoverageState, SourceClass

logger = structlog.get_logger(__name__)


async def discover_sources(
    entity_type: str,
    entity_code: str,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Discover candidate sources for a geography entity."""
    logger.info(
        "discovery_started",
        entity_type=entity_type,
        entity_code=entity_code,
        dry_run=dry_run,
    )

    candidates = [
        {
            "name": f"{entity_code} municipal portal",
            "url": f"https://example.local/{entity_code}",
            "source_class": SourceClass.MUNICIPAL_DIRECT.value,
            "coverage_state": CoverageState.DISCOVERED_UNPARSED.value,
        }
    ]

    result = {
        "entity_type": entity_type,
        "entity_code": entity_code,
        "dry_run": dry_run,
        "candidates_found": len(candidates),
        "candidates": candidates if dry_run else [],
        "registered": 0 if dry_run else len(candidates),
    }
    logger.info("discovery_finished", **{k: v for k, v in result.items() if k != "candidates"})
    return result
