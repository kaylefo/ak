"""Adapter contract tests using offline HTML fixtures."""

from __future__ import annotations

import pytest
from adapters import ALL_ADAPTERS
from adapters.athome_discovery import AtHomeDiscoveryAdapter
from adapters.athome_listings import AtHomeListingsAdapter
from adapters.lifull_discovery import LifullDiscoveryAdapter
from adapters.lifull_listings import LifullListingsAdapter
from adapters.mlit_discovery import MlitDiscoveryAdapter
from adapters.mlit_municipal_links import MlitMunicipalLinksAdapter
from adapters.no_inventory import NoInventoryClassifier
from tsubo_contracts.enums import (
    CoverageState,
    ListingStatus,
    SourceClass,
)
from tsubo_ingest.adapter import SourceAdapter

from tests.conftest import crawl_context, fixture_response, source_config


@pytest.mark.parametrize("adapter", ALL_ADAPTERS, ids=lambda a: a.adapter_id)
def test_adapter_protocol(adapter: SourceAdapter) -> None:
    assert isinstance(adapter, SourceAdapter)
    assert adapter.adapter_id


def test_mlit_discovery_fixture() -> None:
    adapter = MlitDiscoveryAdapter()
    source = source_config(
        source_id="mlit_akiya_bank_root",
        adapter_id="mlit_discovery",
        source_class=SourceClass.NATIONAL_GOVERNMENT,
    )
    ctx = crawl_context(source, url="https://www.mlit.go.jp/akiya-bank/")
    response = fixture_response("mlit_discovery.html", url=ctx.url)
    result = adapter.parse(ctx, response)

    assert len(result.links) == 3
    assert any("hokkaido" in link.url for link in result.links)
    assert result.metadata["adapter"] == "mlit_discovery"


def test_mlit_municipal_links_fixture() -> None:
    adapter = MlitMunicipalLinksAdapter()
    source = source_config(
        source_id="mlit_tokyo_municipal_links",
        adapter_id="mlit_municipal_links",
        metadata={"parent_source": "mlit_akiya_bank_root", "prefecture": "東京都"},
    )
    ctx = crawl_context(source, url="https://www.mlit.go.jp/akiya-bank/prefecture/tokyo/")
    response = fixture_response("mlit_municipal_links.html", url=ctx.url)
    result = adapter.parse(ctx, response)

    assert len(result.links) == 3
    assert result.links[0].entity_name == "青梅市"
    assert "city.ome.tokyo.jp" in result.links[0].url


def test_lifull_discovery_fixture() -> None:
    adapter = LifullDiscoveryAdapter()
    source = source_config(
        source_id="lifull_akiya_bank",
        adapter_id="lifull_discovery",
        source_class=SourceClass.NATIONWIDE_AKIYA_BANK,
    )
    ctx = crawl_context(source, url="https://www.akiya-v.jp/")
    response = fixture_response("lifull_discovery.html", url=ctx.url)
    result = adapter.parse(ctx, response)

    assert len(result.links) == 3
    names = {link.entity_name for link in result.links}
    assert "東京都" in names
    assert "京都府" in names


def test_lifull_listings_index_fixture() -> None:
    adapter = LifullListingsAdapter()
    source = source_config(
        source_id="lifull_tokyo_listings",
        adapter_id="lifull_listings",
        source_class=SourceClass.NATIONWIDE_AKIYA_BANK,
        metadata={"page_kind": "index"},
    )
    ctx = crawl_context(source, url="https://www.akiya-v.jp/akiya/prefecture/13/tokyo/")
    response = fixture_response("lifull_listings_index.html", url=ctx.url)
    result = adapter.parse(ctx, response)

    assert len(result.listings) == 3
    assert len(result.links) == 3
    first = result.listings[0]
    assert first.external_id == "AKIYA-13001"
    assert first.price_yen == 1_200_000
    assert first.area_sqm == 85.5
    assert first.status == ListingStatus.APPLICATION_OPEN

    free = next(item for item in result.listings if item.external_id == "AKIYA-13002")
    assert free.price_yen == 0

    tsubo = next(item for item in result.listings if item.external_id == "AKIYA-13003")
    assert tsubo.area_sqm is not None
    assert tsubo.area_sqm > 300


def test_lifull_listing_detail_fixture() -> None:
    adapter = LifullListingsAdapter()
    source = source_config(
        source_id="lifull_detail",
        adapter_id="lifull_listings",
        source_class=SourceClass.NATIONWIDE_AKIYA_BANK,
        metadata={"page_kind": "detail"},
    )
    url = "https://www.akiya-v.jp/akiya/detail/AKIYA-13001"
    ctx = crawl_context(source, url=url, metadata={"page_kind": "detail"})
    response = fixture_response("lifull_listing_detail.html", url=url)
    result = adapter.parse(ctx, response)

    assert len(result.listings) == 1
    listing = result.listings[0]
    assert listing.external_id == "AKIYA-13001"
    assert listing.layout == "4LDK"
    assert "青梅市" in (listing.address or "")
    assert listing.price_yen == 1_200_000


def test_athome_discovery_fixture() -> None:
    adapter = AtHomeDiscoveryAdapter()
    source = source_config(
        source_id="athome_akiya_root",
        adapter_id="athome_discovery",
        source_class=SourceClass.GENERAL_HOME_SEARCH,
    )
    ctx = crawl_context(source, url="https://www.athome.co.jp/akiya/")
    response = fixture_response("athome_discovery.html", url=ctx.url)
    result = adapter.parse(ctx, response)

    assert len(result.links) == 3
    assert {link.entity_name for link in result.links} == {"千葉県", "長野県", "鹿児島県"}


def test_athome_listings_index_fixture() -> None:
    adapter = AtHomeListingsAdapter()
    source = source_config(
        source_id="athome_chiba_listings",
        adapter_id="athome_listings",
        source_class=SourceClass.GENERAL_HOME_SEARCH,
        metadata={"page_kind": "index"},
    )
    ctx = crawl_context(source, url="https://www.athome.co.jp/akiya/chiba/")
    response = fixture_response("athome_listings_index.html", url=ctx.url)
    result = adapter.parse(ctx, response)

    assert len(result.listings) == 2
    first = result.listings[0]
    assert first.external_id == "6961234567"
    assert first.price_yen == 3_500_000
    assert first.layout == "3DK"
    assert first.area_sqm == 330.0


def test_athome_listing_detail_fixture() -> None:
    adapter = AtHomeListingsAdapter()
    source = source_config(
        source_id="athome_detail",
        adapter_id="athome_listings",
        source_class=SourceClass.GENERAL_HOME_SEARCH,
        metadata={"page_kind": "detail"},
    )
    url = "https://www.athome.co.jp/bukken/detail/6961234567/"
    ctx = crawl_context(source, url=url, metadata={"page_kind": "detail"})
    response = fixture_response("athome_listing_detail.html", url=url)
    result = adapter.parse(ctx, response)

    assert len(result.listings) == 1
    listing = result.listings[0]
    assert listing.external_id == "6961234567"
    assert listing.price_yen == 3_500_000
    assert listing.layout == "3DK"
    assert "大多喜町" in (listing.address or "")


def test_no_inventory_classifier_fixture() -> None:
    classifier = NoInventoryClassifier()
    html = fixture_response("no_inventory.html").text
    assert classifier.classify(html) == CoverageState.DIRECT_ZERO_INVENTORY
    assert classifier.is_no_inventory(html)
