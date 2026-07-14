"""Crawl context and source configuration types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from tsubo_contracts.enums import AccessMode, CoverageState, EntityType, SourceClass


@dataclass(frozen=True)
class SourceConfig:
    """Static configuration for a registered source."""

    source_id: str
    name: str
    adapter_id: str
    base_url: str
    source_class: SourceClass
    access_mode: AccessMode
    entity_type: EntityType = EntityType.MUNICIPALITY
    coverage_state: CoverageState = CoverageState.DIRECT_ACTIVE
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CrawlContext:
    """Mutable crawl state passed through adapter pipelines."""

    source: SourceConfig
    url: str
    depth: int = 0
    parent_url: str | None = None
    entity_id: str | None = None
    entity_name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FetchResponse:
    """Normalized HTTP fetch result with encoding and conditional metadata."""

    url: str
    status_code: int
    content: bytes
    content_type: str | None
    encoding: str
    etag: str | None = None
    last_modified: datetime | None = None
    fetched_at: datetime = field(default_factory=datetime.utcnow)
    from_cache: bool = False
    not_modified: bool = False

    @property
    def text(self) -> str:
        return self.content.decode(self.encoding, errors="replace")
