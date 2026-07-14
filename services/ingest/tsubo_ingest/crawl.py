"""Source crawl orchestration — delegates to ingestion pipeline."""

from __future__ import annotations

from typing import Any

from tsubo_ingest.pipeline import IngestionPipeline, crawl_source as _crawl_source_async


async def crawl_source(source_id: str, *, force: bool = False) -> dict[str, Any]:
    pipeline = IngestionPipeline()
    return pipeline.crawl_source_key(source_id, force=force)


async def crawl_sources(source_ids: list[str], *, force: bool = False) -> list[dict[str, Any]]:
    pipeline = IngestionPipeline()
    results: list[dict[str, Any]] = []
    for source_id in source_ids:
        results.append(pipeline.crawl_source_key(source_id, force=force))
    return results
