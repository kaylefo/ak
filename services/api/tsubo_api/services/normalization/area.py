import re
from decimal import Decimal, ROUND_HALF_UP

from tsubo_api.errors import ValidationError

SQM_QUANTIZE = Decimal("0.01")
TSUBO_TO_SQM = Decimal("3.305785")

_AREA_PATTERN = re.compile(
    r"(?P<amount>[\d,]+(?:\.\d+)?)\s*(?P<unit>㎡|m2|m²|平米|坪|tsubo|sqm)?",
    re.IGNORECASE,
)


def parse_area(value: str) -> tuple[Decimal, str | None]:
    if not value or not str(value).strip():
        raise ValidationError("Area value is empty")

    text = str(value).strip().replace(",", "")
    match = _AREA_PATTERN.search(text)
    if not match:
        raise ValidationError(f"Unable to parse area: {value}")

    amount = Decimal(match.group("amount"))
    unit = (match.group("unit") or "").lower()

    if unit in {"坪", "tsubo"}:
        return amount, "tsubo"
    if unit in {"㎡", "m2", "m²", "平米", "sqm"}:
        return amount, "sqm"
    return amount, None


def normalize_area_sqm(value: str | Decimal | int | float, *, unit: str | None = None) -> Decimal:
    if isinstance(value, Decimal):
        amount = value
        resolved_unit = unit
    elif isinstance(value, (int, float)):
        amount = Decimal(str(value))
        resolved_unit = unit
    else:
        amount, resolved_unit = parse_area(str(value))

    if resolved_unit == "tsubo":
        sqm = amount * TSUBO_TO_SQM
    elif resolved_unit in {None, "sqm"}:
        sqm = amount
    else:
        raise ValidationError(f"Unsupported area unit: {resolved_unit}")

    return sqm.quantize(SQM_QUANTIZE, rounding=ROUND_HALF_UP)
