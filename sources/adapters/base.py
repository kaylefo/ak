"""Shared adapter utilities."""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urljoin, urlparse

from selectolax.parser import HTMLParser

from tsubo_ingest.adapter import DiscoveredLink, ParsedListing
from tsubo_ingest.context import CrawlContext, FetchResponse
from tsubo_ingest.normalize import (
    normalize_address,
    normalize_area,
    normalize_layout,
    normalize_money,
    normalize_status,
)
from tsubo_contracts.enums import ListingStatus, TransactionType


def make_tree(html: str) -> HTMLParser:
    return HTMLParser(html)


def absolute_url(base: str, href: str) -> str:
    return urljoin(base, href.strip())


def same_host(base_url: str, target_url: str) -> bool:
    base_host = urlparse(base_url).netloc
    target_host = urlparse(target_url).netloc
    return base_host == target_host


def extract_links(
    tree: HTMLParser,
    base_url: str,
    *,
    selector: str = "a[href]",
    label_attr: str | None = None,
) -> list[DiscoveredLink]:
    links: list[DiscoveredLink] = []
    seen: set[str] = set()
    for node in tree.css(selector):
        href = node.attributes.get("href")
        if not href or href.startswith(("#", "javascript:", "mailto:")):
            continue
        url = absolute_url(base_url, href)
        if url in seen:
            continue
        seen.add(url)
        label = node.text(strip=True) or None
        if label_attr and node.attributes.get(label_attr):
            label = node.attributes[label_attr]
        links.append(DiscoveredLink(url=url, label=label))
    return links


def parse_key_value_table(tree: HTMLParser, table_selector: str = "table") -> dict[str, str]:
    fields: dict[str, str] = {}
    for table in tree.css(table_selector):
        for row in table.css("tr"):
            cells = row.css("th, td")
            if len(cells) < 2:
                continue
            key = cells[0].text(strip=True)
            value = cells[1].text(strip=True)
            if key:
                fields[key] = value
    return fields


def parse_dl_fields(tree: HTMLParser, dl_selector: str = "dl") -> dict[str, str]:
    fields: dict[str, str] = {}
    for dl in tree.css(dl_selector):
        dts = dl.css("dt")
        dds = dl.css("dd")
        for dt, dd in zip(dts, dds, strict=False):
            key = dt.text(strip=True)
            value = dd.text(strip=True)
            if key:
                fields[key] = value
    return fields


def listing_from_fields(
    *,
    external_id: str,
    fields: dict[str, Any],
    detail_url: str | None = None,
    title: str | None = None,
) -> ParsedListing:
    price_text = fields.get("価格") or fields.get("価格・賃料") or fields.get("譲渡対価")
    area_text = fields.get("面積") or fields.get("建物面積") or fields.get("延床面積")
    layout_text = fields.get("間取り") or fields.get("間取")
    address_text = fields.get("所在地") or fields.get("住所") or fields.get("物件所在地")
    status_text = fields.get("状態") or fields.get("募集状況") or fields.get("ステータス")

    money = normalize_money(price_text)
    area = normalize_area(area_text)
    layout = normalize_layout(layout_text)
    address = normalize_address(address_text)
    status = normalize_status(status_text)

    transaction = TransactionType.SALE
    if price_text and ("賃料" in price_text or "月額" in price_text):
        transaction = TransactionType.RENT

    return ParsedListing(
        external_id=external_id,
        title=title or fields.get("物件名") or fields.get("名称"),
        status=status if status != ListingStatus.STATUS_UNKNOWN else ListingStatus.AVAILABLE,
        transaction_type=transaction,
        price_yen=money.amount_yen,
        price_text=money.raw or price_text,
        area_sqm=area.sqm,
        area_text=area.raw or area_text,
        layout=layout.normalized or layout_text,
        address=address.normalized or address_text,
        detail_url=detail_url,
        raw_fields=fields,
    )


def load_fixture_text(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def extract_json_ld(tree: HTMLParser) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for node in tree.css('script[type="application/ld+json"]'):
        raw = node.text(strip=True)
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, list):
            documents.extend(item for item in payload if isinstance(item, dict))
        elif isinstance(payload, dict):
            documents.append(payload)
    return documents


_EXTERNAL_ID_RE = re.compile(r"/(?:detail|property|bukken)/(?:[^/]+/)?([A-Za-z0-9_-]+)/?")


def external_id_from_url(url: str, fallback: str = "unknown") -> str:
    match = _EXTERNAL_ID_RE.search(url)
    if match:
        return match.group(1)
    slug = urlparse(url).path.rstrip("/").split("/")[-1]
    return slug or fallback
