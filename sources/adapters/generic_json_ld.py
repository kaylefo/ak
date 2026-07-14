"""Generic JSON-LD structured data adapter."""

from __future__ import annotations

from adapters.base import extract_json_ld, listing_from_fields, make_tree
from tsubo_ingest.adapter import AdapterResult, ParsedListing
from tsubo_ingest.context import CrawlContext, FetchResponse, SourceConfig


class GenericJsonLdAdapter:
    adapter_id = "generic_json_ld"

    def matches(self, source: SourceConfig) -> bool:
        return source.adapter_id == self.adapter_id

    def parse(self, ctx: CrawlContext, response: FetchResponse) -> AdapterResult:
        tree = make_tree(response.text)
        documents = extract_json_ld(tree)
        listings: list[ParsedListing] = []

        for doc in documents:
            if doc.get("@type") not in {"Product", "RealEstateListing", "House", "Residence"}:
                continue
            offers = doc.get("offers") or {}
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            fields = {
                "物件名": doc.get("name", ""),
                "価格": str(offers.get("price", "")),
                "所在地": self._address_text(doc.get("address")),
                "面積": str(doc.get("floorSize", "")),
            }
            external_id = str(doc.get("sku") or doc.get("@id") or doc.get("url") or ctx.url)
            listings.append(
                listing_from_fields(
                    external_id=external_id,
                    fields=fields,
                    detail_url=doc.get("url") or ctx.url,
                    title=doc.get("name"),
                )
            )

        return AdapterResult(
            listings=listings,
            metadata={"adapter": self.adapter_id, "json_ld_count": len(documents)},
        )

    def _address_text(self, address) -> str:
        if isinstance(address, str):
            return address
        if isinstance(address, dict):
            parts = [
                address.get("addressRegion", ""),
                address.get("addressLocality", ""),
                address.get("streetAddress", ""),
            ]
            return "".join(parts)
        return ""
