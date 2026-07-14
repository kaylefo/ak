"""LIFULL municipality discovery adapter."""

from __future__ import annotations

from adapters.base import absolute_url, make_tree
from tsubo_contracts.enums import AccessMode, SourceClass
from tsubo_ingest.adapter import AdapterResult, DiscoveredLink
from tsubo_ingest.context import CrawlContext, FetchResponse, SourceConfig


class LifullDiscoveryAdapter:
    adapter_id = "lifull_discovery"

    def matches(self, source: SourceConfig) -> bool:
        return (
            source.adapter_id == self.adapter_id
            or (
                source.source_class == SourceClass.NATIONWIDE_AKIYA_BANK
                and "lifull" in source.source_id.lower()
                and source.access_mode == AccessMode.PUBLIC_HTML
            )
        )

    def parse(self, ctx: CrawlContext, response: FetchResponse) -> AdapterResult:
        tree = make_tree(response.text)
        links: list[DiscoveredLink] = []
        seen: set[str] = set()

        for item in tree.css(".municipality-list li, .area-list__item"):
            anchor = item.css_first("a[href]")
            if not anchor:
                continue
            href = anchor.attributes.get("href")
            if not href:
                continue
            url = absolute_url(ctx.url, href)
            if url in seen:
                continue
            seen.add(url)
            name_node = item.css_first(".municipality-name, .area-list__name")
            name = name_node.text(strip=True) if name_node else anchor.text(strip=True)
            count_node = item.css_first(".listing-count, .area-list__count")
            count_text = count_node.text(strip=True) if count_node else None
            links.append(
                DiscoveredLink(
                    url=url,
                    label=name,
                    entity_name=name,
                    metadata={"listing_count_text": count_text},
                )
            )

        return AdapterResult(
            links=links,
            metadata={"adapter": self.adapter_id, "municipality_count": len(links)},
        )
