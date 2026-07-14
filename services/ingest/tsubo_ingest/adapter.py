"""Source adapter protocol and shared result types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from tsubo_contracts.enums import CoverageState, ListingStatus, PropertyType, TransactionType

from tsubo_ingest.context import CrawlContext, FetchResponse, SourceConfig


@dataclass
class DiscoveredLink:
    """A URL discovered during crawl for follow-up fetching."""

    url: str
    label: str | None = None
    entity_id: str | None = None
    entity_name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedListing:
    """Normalized listing extracted from a source page."""

    external_id: str
    title: str | None = None
    status: ListingStatus = ListingStatus.STATUS_UNKNOWN
    transaction_type: TransactionType = TransactionType.UNKNOWN
    property_type: PropertyType = PropertyType.UNKNOWN
    price_yen: int | None = None
    price_text: str | None = None
    area_sqm: float | None = None
    area_text: str | None = None
    layout: str | None = None
    address: str | None = None
    detail_url: str | None = None
    raw_fields: dict[str, Any] = field(default_factory=dict)


@dataclass
class AdapterResult:
    """Output of a source adapter parse step."""

    links: list[DiscoveredLink] = field(default_factory=list)
    listings: list[ParsedListing] = field(default_factory=list)
    coverage_state: CoverageState | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class SourceAdapter(Protocol):
    """Protocol implemented by all source adapters."""

    adapter_id: str

    def matches(self, source: SourceConfig) -> bool:
        """Return True when this adapter should handle the given source."""
        ...

    def parse(self, ctx: CrawlContext, response: FetchResponse) -> AdapterResult:
        """Parse fetched content into links and/or listings."""
        ...
