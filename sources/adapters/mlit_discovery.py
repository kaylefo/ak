"""MLIT national akiya bank discovery root adapter."""

from __future__ import annotations

from adapters.base import extract_links, make_tree
from tsubo_contracts.enums import AccessMode, SourceClass
from tsubo_ingest.adapter import AdapterResult
from tsubo_ingest.context import CrawlContext, FetchResponse, SourceConfig


class MlitDiscoveryAdapter:
    adapter_id = "mlit_discovery"

    def matches(self, source: SourceConfig) -> bool:
        return (
            source.adapter_id == self.adapter_id
            or (
                source.source_class == SourceClass.NATIONAL_GOVERNMENT
                and "mlit" in source.source_id.lower()
                and source.access_mode == AccessMode.PUBLIC_HTML
            )
        )

    def parse(self, ctx: CrawlContext, response: FetchResponse) -> AdapterResult:
        tree = make_tree(response.text)
        links = extract_links(tree, ctx.url, selector="a[href*='prefecture'], a[href*='municipality']")
        if not links:
            links = extract_links(tree, ctx.url, selector="ul.prefecture-list a, .region-list a")

        for link in links:
            if link.label:
                link.entity_name = link.label

        return AdapterResult(
            links=links,
            metadata={"adapter": self.adapter_id, "link_count": len(links)},
        )
