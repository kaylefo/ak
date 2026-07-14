"""Generic HTML table field extraction adapter."""

from __future__ import annotations

from adapters.base import listing_from_fields, make_tree, parse_key_value_table
from tsubo_ingest.adapter import AdapterResult
from tsubo_ingest.context import CrawlContext, FetchResponse, SourceConfig


class GenericTableAdapter:
    adapter_id = "generic_table"

    def matches(self, source: SourceConfig) -> bool:
        return source.adapter_id == self.adapter_id

    def parse(self, ctx: CrawlContext, response: FetchResponse) -> AdapterResult:
        tree = make_tree(response.text)
        fields = parse_key_value_table(tree)
        external_id = ctx.metadata.get("external_id") or ctx.entity_id or "table-row"
        listing = listing_from_fields(
            external_id=str(external_id),
            fields=fields,
            detail_url=ctx.url,
        )
        return AdapterResult(
            listings=[listing] if fields else [],
            metadata={"adapter": self.adapter_id, "field_count": len(fields)},
        )
