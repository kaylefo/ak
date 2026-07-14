"""At Home listing index and detail adapter."""

from __future__ import annotations

from adapters.base import (
    absolute_url,
    external_id_from_url,
    listing_from_fields,
    make_tree,
    parse_dl_fields,
    parse_key_value_table,
)
from tsubo_contracts.enums import AccessMode, SourceClass
from tsubo_ingest.adapter import AdapterResult, DiscoveredLink, ParsedListing
from tsubo_ingest.context import CrawlContext, FetchResponse, SourceConfig


class AtHomeListingsAdapter:
    adapter_id = "athome_listings"

    _INDEX_SELECTORS = (
        ".cassetteitem",
        ".property-item",
        ".mod-bukkenList__item",
    )

    def matches(self, source: SourceConfig) -> bool:
        return (
            source.adapter_id == self.adapter_id
            or (
                source.source_class == SourceClass.GENERAL_HOME_SEARCH
                and "athome" in source.source_id.lower()
                and source.metadata.get("page_kind") in {"index", "detail", None}
            )
        )

    def parse(self, ctx: CrawlContext, response: FetchResponse) -> AdapterResult:
        tree = make_tree(response.text)
        page_kind = ctx.metadata.get("page_kind") or self._detect_page_kind(tree, response.url)

        if page_kind == "detail":
            listing = self._parse_detail(tree, response.url)
            return AdapterResult(
                listings=[listing] if listing else [],
                metadata={"adapter": self.adapter_id, "page_kind": "detail"},
            )

        links, listings = self._parse_index(tree, ctx.url)
        return AdapterResult(
            links=links,
            listings=listings,
            metadata={"adapter": self.adapter_id, "page_kind": "index", "count": len(listings)},
        )

    def _detect_page_kind(self, tree, url: str) -> str:
        if "/bukken/detail/" in url or tree.css_first(".bukkenDetail, .mod-bukkenDetail"):
            return "detail"
        return "index"

    def _parse_index(self, tree, base_url: str) -> tuple[list[DiscoveredLink], list[ParsedListing]]:
        links: list[DiscoveredLink] = []
        listings: list[ParsedListing] = []
        seen: set[str] = set()

        for selector in self._INDEX_SELECTORS:
            for card in tree.css(selector):
                anchor = card.css_first("a[href]")
                if not anchor:
                    continue
                href = anchor.attributes.get("href")
                if not href:
                    continue
                detail_url = absolute_url(base_url, href)
                if detail_url in seen:
                    continue
                seen.add(detail_url)

                title_node = card.css_first(".cassetteitem_detail-title, .property-item__title, h3")
                title = title_node.text(strip=True) if title_node else None
                price_node = card.css_first(".cassetteitem_price, .property-item__price")
                area_node = card.css_first(".cassetteitem_detail-area, .property-item__area")
                layout_node = card.css_first(".cassetteitem_madori, .property-item__layout")

                external_id = external_id_from_url(detail_url)
                fields = {
                    "物件名": title or "",
                    "価格": price_node.text(strip=True) if price_node else "",
                    "面積": area_node.text(strip=True) if area_node else "",
                    "間取り": layout_node.text(strip=True) if layout_node else "",
                }
                listings.append(
                    listing_from_fields(
                        external_id=external_id,
                        fields=fields,
                        detail_url=detail_url,
                        title=title,
                    )
                )
                links.append(DiscoveredLink(url=detail_url, label=title, metadata={"external_id": external_id}))

            if listings:
                break

        return links, listings

    def _parse_detail(self, tree, url: str) -> ParsedListing | None:
        fields = parse_dl_fields(tree, "dl.bukkenDetail-spec, dl.mod-bukkenDetail__spec")
        if not fields:
            fields = parse_key_value_table(tree, "table.bukkenDetail-table, table.detail-spec")

        title_node = tree.css_first("h1.bukkenDetail-title, h1.mod-bukkenDetail__title")
        title = title_node.text(strip=True) if title_node else None
        external_id = external_id_from_url(url)

        if not fields and not title:
            return None

        return listing_from_fields(
            external_id=external_id,
            fields=fields,
            detail_url=url,
            title=title,
        )
