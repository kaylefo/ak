"""Normalize Japanese date expressions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime

_ERA_OFFSETS = {
    "令和": 2018,
    "平成": 1988,
    "昭和": 1925,
}
_FULLWIDTH_DIGITS = str.maketrans("０１２３４５６７８９", "0123456789")
_WESTERN_RE = re.compile(r"(\d{4})[年/.-](\d{1,2})[月/.-](\d{1,2})")
_ERA_RE = re.compile(r"(令和|平成|昭和)\s*(\d{1,2})年\s*(\d{1,2})月\s*(\d{1,2})日?")


@dataclass(frozen=True)
class DateValue:
    value: date | None
    raw: str


def _to_ascii_digits(text: str) -> str:
    return text.translate(_FULLWIDTH_DIGITS)


def normalize_date(text: str | None) -> DateValue:
    if not text:
        return DateValue(value=None, raw="")

    raw = text.strip()
    normalized = _to_ascii_digits(raw)

    era_match = _ERA_RE.search(normalized)
    if era_match:
        era, year_s, month_s, day_s = era_match.groups()
        year = _ERA_OFFSETS[era] + int(year_s)
        try:
            return DateValue(value=date(year, int(month_s), int(day_s)), raw=raw)
        except ValueError:
            return DateValue(value=None, raw=raw)

    western_match = _WESTERN_RE.search(normalized)
    if western_match:
        year_s, month_s, day_s = western_match.groups()
        try:
            return DateValue(value=date(int(year_s), int(month_s), int(day_s)), raw=raw)
        except ValueError:
            return DateValue(value=None, raw=raw)

    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return DateValue(value=datetime.strptime(normalized, fmt).date(), raw=raw)
        except ValueError:
            continue

    return DateValue(value=None, raw=raw)
