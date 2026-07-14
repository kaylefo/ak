"""Normalize Japanese area expressions to square meters."""

from __future__ import annotations

import re
from dataclasses import dataclass

_FULLWIDTH_DIGITS = str.maketrans("０１２３４５６７８９", "0123456789")
_TSUBO_TO_SQM = 3.305785124
_AREA_RE = re.compile(
    r"([\d,，．.０-９]+)\s*(㎡|m2|m²|平米|平方メートル|坪|tsubo)?",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class AreaValue:
    sqm: float | None
    raw: str


def _to_ascii_digits(text: str) -> str:
    return text.translate(_FULLWIDTH_DIGITS).replace("，", ",").replace("．", ".")


def normalize_area(text: str | None) -> AreaValue:
    if not text:
        return AreaValue(sqm=None, raw="")

    raw = text.strip()
    compact = raw.replace(" ", "").replace("　", "")

    match = _AREA_RE.search(compact)
    if not match:
        return AreaValue(sqm=None, raw=raw)

    number_text = _to_ascii_digits(match.group(1)).replace(",", "")
    try:
        value = float(number_text)
    except ValueError:
        return AreaValue(sqm=None, raw=raw)

    unit = (match.group(2) or "㎡").lower()
    if unit in {"坪", "tsubo"}:
        sqm = value * _TSUBO_TO_SQM
    else:
        sqm = value

    return AreaValue(sqm=round(sqm, 2), raw=raw)
