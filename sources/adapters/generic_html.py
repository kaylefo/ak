"""Generic HTML link extraction adapter."""

from __future__ import annotations

from adapters.base import extract_links, make_tree
from tsubo_ingest.adapter import AdapterResult
from tsubo_ingest.context import CrawlContext, FetchResponse, SourceConfig


class GenericHtmlAdapter:
    adapter_id = "generic_html"

    def matches(self, source: SourceConfig) -> bool:
        return source.adapter_id == self.adapter_id

    def parse(self, ctx: CrawlContext, response: FetchResponse) -> AdapterResult:
        tree = make_tree(response.text)
        links = extract_links(tree, ctx.url)
        return AdapterResult(
            links=links,
            metadata={"adapter": self.adapter_id, "link_count": len(links)},
        )
