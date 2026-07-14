"""LIFULL prefecture and municipality discovery for homes.co.jp/akiyabank."""

from __future__ import annotations

import re

from adapters.base import absolute_url, make_tree
from tsubo_contracts.enums import SourceClass
from tsubo_ingest.adapter import AdapterResult, DiscoveredLink
from tsubo_ingest.context import CrawlContext, FetchResponse, SourceConfig

_PREF_PATH_RE = re.compile(r"/akiyabank/(?:tohoku|kanto|chubu|kansai|chugoku|shikoku|kyushu)/([^/]+)/?")
_FIXTURE_PREF_RE = re.compile(r"/akiya/prefecture/\d+/([^/]+)/?")


class LifullDiscoveryAdapter:
    adapter_id = "lifull_discovery"

    def matches(self, source: SourceConfig) -> bool:
        return source.adapter_id == self.adapter_id or (
            source.source_class == SourceClass.NATIONWIDE_AKIYA_BANK
            and source.source_id == "lifull_akiya_bank"
        )

    def parse(self, ctx: CrawlContext, response: FetchResponse) -> AdapterResult:
        tree = make_tree(response.text)
        links: list[DiscoveredLink] = []
        seen: set[str] = set()

        # Offline fixture format (akiya-v.jp style municipality list)
        for anchor in tree.css(".municipality-list a[href], .municipality-index a[href]"):
            href = anchor.attributes.get("href")
            if not href:
                continue
            url = absolute_url(ctx.url, href)
            if url in seen:
                continue
            seen.add(url)
            name_node = anchor.css_first(".municipality-name")
            label = name_node.text(strip=True) if name_node else anchor.text(strip=True) or url
            links.append(
                DiscoveredLink(
                    url=url,
                    label=label,
                    entity_name=label,
                    metadata={"page_kind": "index"},
                )
            )

        # Live homes.co.jp regional prefecture links
        for anchor in tree.css("a[href]"):
            href = anchor.attributes.get("href")
            if not href:
                continue
            url = absolute_url(ctx.url, href)
            if not _PREF_PATH_RE.search(url):
                continue
            if url in seen:
                continue
            seen.add(url)
            label = anchor.text(strip=True) or url
            pref_match = _PREF_PATH_RE.search(url)
            pref_slug = pref_match.group(1) if pref_match else None
            links.append(
                DiscoveredLink(
                    url=url,
                    label=label,
                    entity_name=label,
                    metadata={"prefecture_slug": pref_slug, "page_kind": "index"},
                )
            )

        return AdapterResult(
            links=links,
            metadata={"adapter": self.adapter_id, "prefecture_count": len(links)},
        )
