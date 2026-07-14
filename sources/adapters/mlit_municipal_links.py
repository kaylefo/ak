"""MLIT nationwide municipal akiya link directory adapter."""

from __future__ import annotations

from urllib.parse import urlparse

from adapters.base import absolute_url, make_tree
from tsubo_contracts.enums import SourceClass
from tsubo_ingest.adapter import AdapterResult, DiscoveredLink
from tsubo_ingest.context import CrawlContext, FetchResponse, SourceConfig


def _is_akiya_url(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    if "mlit.go.jp" in host:
        return False
    if host.endswith(".jpg") or host.endswith(".png"):
        return False
    return url.startswith("http")


class MlitMunicipalLinksAdapter:
    adapter_id = "mlit_municipal_links"

    def matches(self, source: SourceConfig) -> bool:
        return (
            source.adapter_id == self.adapter_id
            or source.source_id == "mlit_akiya_municipal_links"
        )

    def parse(self, ctx: CrawlContext, response: FetchResponse) -> AdapterResult:
        tree = make_tree(response.text)
        links: list[DiscoveredLink] = []
        seen: set[str] = set()

        # Simple 2-column fixture / simplified table layout
        for row in tree.css("table.municipality-links tr, table tr"):
            cells = row.css("td")
            if len(cells) == 2:
                municipality = cells[0].text(strip=True).replace("\xa0", " ").strip()
                anchor = cells[1].css_first("a[href]")
                if not anchor or not municipality:
                    continue
                href = anchor.attributes.get("href")
                if not href:
                    continue
                url = absolute_url(ctx.url, href)
                if not _is_akiya_url(url) or url in seen:
                    continue
                seen.add(url)
                links.append(
                    DiscoveredLink(
                        url=url,
                        label=anchor.text(strip=True),
                        entity_name=municipality,
                        metadata={
                            "municipality": municipality,
                            "source_class": "MUNICIPAL_DIRECT",
                        },
                    )
                )
                continue

            # Live MLIT 3-column layout with prefecture anchors
            if len(cells) < 3:
                continue

        current_prefecture = ""
        for row in tree.css("tr"):
            cells = row.css("td")
            if len(cells) < 3:
                continue

            pref_anchor = cells[0].css_first("a[name]")
            if pref_anchor and pref_anchor.attributes.get("name", "").startswith("q"):
                current_prefecture = pref_anchor.text(strip=True)

            municipality = cells[1].text(strip=True).replace("\xa0", " ").strip()
            anchor = cells[2].css_first("a[href]")
            if not anchor or not municipality:
                continue
            href = anchor.attributes.get("href")
            if not href:
                continue
            url = absolute_url(ctx.url, href)
            if not _is_akiya_url(url) or url in seen:
                continue
            seen.add(url)
            links.append(
                DiscoveredLink(
                    url=url,
                    label=anchor.text(strip=True),
                    entity_name=municipality,
                    metadata={
                        "prefecture": current_prefecture,
                        "municipality": municipality,
                        "source_class": "MUNICIPAL_DIRECT",
                    },
                )
            )

        return AdapterResult(
            links=links,
            metadata={"adapter": self.adapter_id, "municipality_count": len(links)},
        )
