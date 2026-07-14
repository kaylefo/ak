from datetime import date
from decimal import Decimal

import pytest

from tsubo_api.errors import ValidationError
from tsubo_api.services.normalization.area import normalize_area_sqm, parse_area
from tsubo_api.services.normalization.dates import normalize_datetime, parse_japanese_date
from tsubo_api.services.normalization.layout import normalize_layout, parse_layout
from tsubo_api.services.normalization.money import (
    normalize_money_jpy,
    parse_japanese_price,
    parse_money_amount,
)


def test_parse_japanese_price_man_yen():
    amount, currency = parse_money_amount("350万円")
    assert amount == Decimal("3500000")
    assert currency == "JPY"


def test_parse_japanese_price_with_symbol():
    amount = parse_japanese_price("¥1,200,000")
    assert amount == Decimal("1200000")


def test_normalize_money_jpy_with_fx():
    result = normalize_money_jpy(Decimal("100"), currency="USD", fx_rate_to_jpy=Decimal("150"))
    assert result == Decimal("15000")


def test_normalize_money_jpy_requires_fx_for_foreign_currency():
    with pytest.raises(ValidationError):
        normalize_money_jpy("100 USD", currency="USD")


def test_parse_area_tsubo():
    amount, unit = parse_area("45.5坪")
    assert amount == Decimal("45.5")
    assert unit == "tsubo"


def test_normalize_area_sqm_from_tsubo():
    sqm = normalize_area_sqm("10坪", unit="tsubo")
    assert sqm == Decimal("33.06")


def test_parse_japanese_date_reiwa():
    parsed = parse_japanese_date("令和6年7月14日")
    assert parsed == date(2024, 7, 14)


def test_normalize_datetime_from_date():
    dt = normalize_datetime(date(2024, 7, 14))
    assert dt.year == 2024
    assert dt.month == 7
    assert dt.day == 14


def test_parse_layout_ldk():
    layout = parse_layout("3LDK")
    assert layout["bedrooms"] == 3
    assert layout["layout_type"] == "LDK"


def test_normalize_layout_passthrough():
    payload = {"raw": "2DK", "layout_type": "DK", "bedrooms": 2}
    assert normalize_layout(payload) == payload
