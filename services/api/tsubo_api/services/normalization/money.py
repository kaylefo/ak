import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from tsubo_api.errors import ValidationError

MONEY_QUANTIZE = Decimal("1")
TSUBO_TO_SQM = Decimal("3.305785")

_CURRENCY_SYMBOLS = {
    "¥": "JPY",
    "￥": "JPY",
    "円": "JPY",
    "$": "USD",
    "US$": "USD",
    "€": "EUR",
    "£": "GBP",
}

_CURRENCY_CODES = re.compile(r"\b([A-Z]{3})\b")
_AMOUNT_PATTERN = re.compile(
    r"(?P<amount>[\d,]+(?:\.\d+)?)\s*(?P<suffix>万円|億円|円|万|億)?",
    re.IGNORECASE,
)


def parse_money_amount(value: str) -> tuple[Decimal, str | None]:
    if not value or not str(value).strip():
        raise ValidationError("Money value is empty")

    text = str(value).strip()
    currency: str | None = None

    for symbol, code in _CURRENCY_SYMBOLS.items():
        if symbol in text:
            currency = code
            text = text.replace(symbol, "")
            break

    code_match = _CURRENCY_CODES.search(text.upper())
    if code_match:
        currency = code_match.group(1)
        text = text.replace(code_match.group(0), "")

    text = text.replace(",", "").strip()
    match = _AMOUNT_PATTERN.search(text)
    if not match:
        raise ValidationError(f"Unable to parse money amount: {value}")

    amount = Decimal(match.group("amount"))
    suffix = (match.group("suffix") or "").strip()

    if suffix in {"万円", "万"}:
        amount *= Decimal("10000")
    elif suffix in {"億円", "億"}:
        amount *= Decimal("100000000")
    elif suffix == "円":
        pass

    return amount.quantize(MONEY_QUANTIZE, rounding=ROUND_HALF_UP), currency


def parse_japanese_price(value: str) -> Decimal:
    amount, currency = parse_money_amount(value)
    if currency is not None and currency != "JPY":
        raise ValidationError("Japanese price parser expects JPY-denominated input")
    return amount


def normalize_money_jpy(
    value: str | Decimal | int | float,
    *,
    currency: str | None = None,
    fx_rate_to_jpy: Decimal | None = None,
) -> Decimal:
    if isinstance(value, Decimal):
        amount = value.quantize(MONEY_QUANTIZE, rounding=ROUND_HALF_UP)
    elif isinstance(value, (int, float)):
        amount = Decimal(str(value)).quantize(MONEY_QUANTIZE, rounding=ROUND_HALF_UP)
    else:
        amount, detected_currency = parse_money_amount(str(value))
        currency = currency or detected_currency

    resolved_currency = (currency or "JPY").upper()
    if resolved_currency == "JPY":
        return amount

    if fx_rate_to_jpy is None:
        raise ValidationError(f"FX rate required to convert {resolved_currency} to JPY")

    try:
        rate = Decimal(str(fx_rate_to_jpy))
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError("Invalid FX rate") from exc

    return (amount * rate).quantize(MONEY_QUANTIZE, rounding=ROUND_HALF_UP)
