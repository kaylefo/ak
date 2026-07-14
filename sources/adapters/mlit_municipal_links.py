"""MLIT municipal link directory adapter."""

from __future__ import annotations

from adapters.base import absolute_url, make_tree
from tsubo_contracts.enums import AccessMode, SourceClass
from tsubo_ingest.adapter import AdapterResult, DiscoveredLink
from tsubo_ingest.context import CrawlContext, FetchResponse, SourceConfig


class MlitMunicipalLinksAdapter:
    adapter_id = "mlit_municipal_links"

    def matches(self, source: SourceConfig) -> bool:
        return (
            source.adapter_id == self.adapter_id
            or (
                source.source_class == SourceClass.MUNICIPAL_DIRECT
                and "mlit" in source.metadata.get("parent_source", "").lower()
            )
        )

    def parse(self, ctx: CrawlContext, response: FetchResponse) -> AdapterResult:
        tree = make_tree(response.text)
        links: list[DiscoveredLink] = []
        seen: set[str] = set()

        for row in tree.css("table.municipality-links tr, table.links tr"):
            cells = row.css("td")
            if len(cells) < 2:
                continue
            municipality = cells[0].text(strip=True)
            anchor = cells[1].css_first("a[href]")
            if not anchor:
                continue
            href = anchor.attributes.get("href")
            if not href:
                continue
            url = absolute_url(ctx.url, href)
            if url in seen:
                continue
            seen.add(url)
            links.append(
                DiscoveredLink(
                    url=url,
                    label=municipality,
                    entity_name=municipality,
                    metadata={"prefecture": ctx.metadata.get("prefecture")},
                )
            )

        return AdapterResult(
            links=links,
            metadata={"adapter": self.adapter_id, "municipality_count": len(links)},
        )
