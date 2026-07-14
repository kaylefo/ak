"""LIFULL listing index and detail adapter for homes.co.jp/akiyabank."""

from __future__ import annotations

import re

from adapters.base import (
    absolute_url,
    is_bot_challenge_page,
    listing_from_fields,
    make_tree,
    parse_dl_fields,
    parse_key_value_table,
)
from tsubo_contracts.enums import SourceClass
from tsubo_ingest.adapter import AdapterResult, DiscoveredLink, ParsedListing
from tsubo_ingest.context import CrawlContext, FetchResponse, SourceConfig
from tsubo_ingest.normalize.area import normalize_area
from tsubo_ingest.normalize.money import normalize_money

_SPEC_RE = re.compile(
    r"・所在地(?P<addr>.*?)・価格(?P<price>.*?)・(?P<area_label>土地面積|建物面積)(?P<area>.*?)詳細をみる"
)
_B_ID_RE = re.compile(r"/b-(\d+)/?", re.IGNORECASE)


class LifullListingsAdapter:
    adapter_id = "lifull_listings"

    def matches(self, source: SourceConfig) -> bool:
        return (
            source.adapter_id == self.adapter_id
            or (
                source.source_class == SourceClass.NATIONWIDE_AKIYA_BANK
                and "lifull" in source.source_id.lower()
            )
        )

    def parse(self, ctx: CrawlContext, response: FetchResponse) -> AdapterResult:
        if is_bot_challenge_page(response.text, status_code=response.status_code):
            return AdapterResult(
                metadata={
                    "adapter": self.adapter_id,
                    "blocked": True,
                    "reason": "bot_challenge",
                },
            )

        tree = make_tree(response.text)
        page_kind = ctx.metadata.get("page_kind") or self._detect_page_kind(tree, response.url)

        if page_kind == "detail":
            listing = self._parse_detail(tree, response.url)
            return AdapterResult(
                listings=[listing] if listing else [],
                metadata={"adapter": self.adapter_id, "page_kind": "detail"},
            )

        links, listings = self._parse_index(tree, response.url)
        return AdapterResult(
            links=links,
            listings=listings,
            metadata={"adapter": self.adapter_id, "page_kind": "index", "count": len(listings)},
        )

    def _detect_page_kind(self, tree, url: str) -> str:
        if _B_ID_RE.search(url) or tree.css_first(".mod-bukkenSubTitle, .mod-contactTitle, .property-detail"):
            return "detail"
        if tree.css_first(".mod-result-bukkenBox, .property-card"):
            return "index"
        return "index"

    def _external_id(self, url: str) -> str:
        match = _B_ID_RE.search(url)
        if match:
            return f"b-{match.group(1)}"
        slug = url.rstrip("/").split("/")[-1]
        return slug or "unknown"

    def _parse_index(self, tree, base_url: str) -> tuple[list[DiscoveredLink], list[ParsedListing]]:
        if tree.css_first(".property-card"):
            return self._parse_fixture_index(tree, base_url)
        return self._parse_live_index(tree, base_url)

    def _parse_fixture_index(self, tree, base_url: str) -> tuple[list[DiscoveredLink], list[ParsedListing]]:
        links: list[DiscoveredLink] = []
        listings: list[ParsedListing] = []
        for card in tree.css(".property-card"):
            anchor = card.css_first("a[href]")
            if not anchor:
                continue
            href = anchor.attributes.get("href")
            if not href:
                continue
            detail_url = absolute_url(base_url, href)
            title_node = card.css_first(".property-title")
            title = title_node.text(strip=True) if title_node else None
            price_node = card.css_first(".price")
            area_node = card.css_first(".area")
            status_node = card.css_first(".status")
            fields: dict[str, str] = {}
            if price_node:
                fields["価格"] = price_node.text(strip=True)
            if area_node:
                fields["面積"] = area_node.text(strip=True)
            if status_node:
                fields["募集状況"] = status_node.text(strip=True)
            external_id = detail_url.rstrip("/").split("/")[-1]
            listing = listing_from_fields(
                external_id=external_id,
                fields=fields,
                detail_url=detail_url,
                title=title,
            )
            listings.append(listing)
            links.append(DiscoveredLink(url=detail_url, label=title, metadata={"external_id": external_id}))
        return links, listings

    def _parse_live_index(self, tree, base_url: str) -> tuple[list[DiscoveredLink], list[ParsedListing]]:
        links: list[DiscoveredLink] = []
        listings: list[ParsedListing] = []
        seen: set[str] = set()

        for box in tree.css(".mod-result-bukkenBox"):
            anchor = box.css_first("a[href*='/b-']")
            if not anchor:
                continue
            href = anchor.attributes.get("href")
            if not href:
                continue
            detail_url = absolute_url(base_url, href)
            if detail_url in seen:
                continue
            seen.add(detail_url)

            title_node = box.css_first(".bukkenTitle")
            title = title_node.text(strip=True) if title_node else None
            spec_node = box.css_first(".specText")
            spec_text = spec_node.text(strip=True) if spec_node else ""
            address_node = box.css_first(".address")
            address = address_node.text(strip=True) if address_node else None

            fields: dict[str, str] = {}
            if spec_text:
                match = _SPEC_RE.search(spec_text.replace(" ", ""))
                if match:
                    fields["所在地"] = match.group("addr")
                    fields["価格"] = match.group("price")
                    fields[match.group("area_label")] = match.group("area")
                else:
                    fields["概要"] = spec_text
            if address:
                fields["所在地"] = address
            if title:
                fields["物件名"] = title

            external_id = self._external_id(detail_url)
            listing = listing_from_fields(
                external_id=external_id,
                fields=fields,
                detail_url=detail_url,
                title=title,
            )
            money = normalize_money(fields.get("価格"))
            if money.amount_yen is not None:
                listing.price_yen = money.amount_yen
            land = normalize_area(fields.get("土地面積"))
            building = normalize_area(fields.get("建物面積"))
            if land.sqm:
                listing.raw_fields["land_sqm"] = land.sqm
            if building.sqm:
                listing.area_sqm = building.sqm
            elif land.sqm and listing.area_sqm is None:
                listing.area_sqm = land.sqm

            listings.append(listing)
            links.append(DiscoveredLink(url=detail_url, label=title, metadata={"external_id": external_id}))

        return links, listings

    def _parse_detail(self, tree, url: str) -> ParsedListing | None:
        if tree.css_first(".property-detail__list, dl.property-detail__list"):
            return self._parse_fixture_detail(tree, url)

        fields = parse_key_value_table(tree, "table.table-style-a, table.mod-bukkenSpecTable, table")

        price_node = tree.css_first(".price-value")
        if price_node:
            fields["価格"] = price_node.text(strip=True)

        area_node = tree.css_first(".area-text")
        if area_node:
            fields["所在地"] = area_node.text(strip=True)

        title_node = tree.css_first("h1, .mod-bukkenTitle, title")
        title = None
        if title_node:
            title = title_node.text(strip=True)
            title = title.split("の物件詳細")[0].split(" の物件詳細")[0]
            if title.startswith("売買居住用"):
                title = title[len("売買居住用") :]

        og = tree.css_first('meta[property="og:description"]')
        if og and og.attributes.get("content"):
            fields["ポイント"] = og.attributes["content"]

        address_node = tree.css_first(".address")
        if address_node:
            fields["所在地"] = address_node.text(strip=True)

        external_id = self._external_id(url)
        if not fields and not title:
            return None
        if title and title.lower() == "javascript is disabled":
            return None

        listing = listing_from_fields(
            external_id=external_id,
            fields=fields,
            detail_url=url,
            title=title,
        )

        money = normalize_money(fields.get("価格") or listing.price_text)
        if money.amount_yen is not None:
            listing.price_yen = money.amount_yen
        land = normalize_area(fields.get("土地面積") or fields.get("土地面積(土地面積計測方式)"))
        building = normalize_area(fields.get("建物面積") or fields.get("建物面積(建物面積計測方式)"))
        if land.sqm:
            listing.raw_fields["land_sqm"] = land.sqm
        if building.sqm:
            listing.area_sqm = building.sqm
        layout_key = next((k for k in fields if k.startswith("間取り")), None)
        if layout_key:
            listing.layout = fields[layout_key]

        return listing

    def _parse_fixture_detail(self, tree, url: str) -> ParsedListing | None:
        fields = parse_dl_fields(tree, "dl.property-detail__list, dl")
        title_node = tree.css_first("h1.property-title, h1")
        title = title_node.text(strip=True) if title_node else None
        external_id = fields.get("物件番号") or self._external_id(url)
        return listing_from_fields(
            external_id=external_id,
            fields=fields,
            detail_url=url,
            title=title,
        )
