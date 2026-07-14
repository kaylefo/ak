"""Tests for Japanese normalization helpers."""

from datetime import date

from tsubo_contracts.enums import ListingStatus, LocationPrecision, PriceKind
from tsubo_ingest.normalize import (
    normalize_address,
    normalize_area,
    normalize_date,
    normalize_layout,
    normalize_money,
    normalize_status,
)


def test_normalize_money_variants() -> None:
    assert normalize_money("120万円").amount_yen == 1_200_000
    assert normalize_money("無償譲渡").kind == PriceKind.ZERO_PRICE
    assert normalize_money("価格応相談").kind == PriceKind.NEGOTIABLE
    assert normalize_money("３５０万円").amount_yen == 3_500_000


def test_normalize_area_variants() -> None:
    assert normalize_area("85.5㎡").sqm == 85.5
    assert normalize_area("98坪").sqm is not None
    assert normalize_area("98坪").sqm > 300


def test_normalize_layout() -> None:
    value = normalize_layout("4LDK")
    assert value.normalized == "4LDK"
    assert value.rooms == 4
    assert value.layout_type == "LDK"


def test_normalize_address() -> None:
    value = normalize_address("〒198-0001 東京都青梅市成木1-2-3")
    assert value.postcode == "198-0001"
    assert "青梅市" in value.normalized
    assert value.precision == LocationPrecision.STREET_BLOCK


def test_normalize_date() -> None:
    assert normalize_date("令和6年7月14日").value == date(2024, 7, 14)
    assert normalize_date("1970年3月15日").value == date(1970, 3, 15)


def test_normalize_status() -> None:
    assert normalize_status("募集中") == ListingStatus.APPLICATION_OPEN
    assert normalize_status("商談中") == ListingStatus.UNDER_NEGOTIATION
    assert normalize_status("不明") == ListingStatus.STATUS_UNKNOWN
