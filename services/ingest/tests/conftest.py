"""Shared test helpers."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from tsubo_contracts.enums import AccessMode, EntityType, SourceClass
from tsubo_ingest.context import CrawlContext, FetchResponse, SourceConfig

FIXTURES_DIR = Path(__file__).resolve().parents[3] / "sources" / "fixtures"


def load_fixture(name: str) -> bytes:
    return (FIXTURES_DIR / name).read_bytes()


def fixture_response(
    name: str,
    *,
    url: str = "https://example.test/page",
    status_code: int = 200,
) -> FetchResponse:
    content = load_fixture(name)
    return FetchResponse(
        url=url,
        status_code=status_code,
        content=content,
        content_type="text/html; charset=utf-8",
        encoding="utf-8",
        fetched_at=datetime(2026, 7, 14, 12, 0, 0),
    )


def source_config(
    *,
    source_id: str,
    adapter_id: str,
    source_class: SourceClass = SourceClass.MUNICIPAL_DIRECT,
    access_mode: AccessMode = AccessMode.PUBLIC_HTML,
    metadata: dict | None = None,
) -> SourceConfig:
    return SourceConfig(
        source_id=source_id,
        name=source_id,
        adapter_id=adapter_id,
        base_url="https://example.test/",
        source_class=source_class,
        access_mode=access_mode,
        entity_type=EntityType.MUNICIPALITY,
        metadata=metadata or {},
    )


def crawl_context(
    source: SourceConfig,
    *,
    url: str = "https://example.test/page",
    metadata: dict | None = None,
) -> CrawlContext:
    return CrawlContext(
        source=source,
        url=url,
        metadata=metadata or {},
    )
