"""Normalize Japanese addresses."""

from __future__ import annotations

import re
from dataclasses import dataclass

from tsubo_contracts.enums import LocationPrecision

_POSTCODE_RE = re.compile(r"〒?\s*(\d{3})[-‐－]?\s*(\d{4})")
_WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class AddressValue:
    normalized: str
    postcode: str | None
    precision: LocationPrecision
    raw: str


def normalize_address(text: str | None) -> AddressValue:
    if not text:
        return AddressValue(normalized="", postcode=None, precision=LocationPrecision.UNKNOWN, raw="")

    raw = text.strip()
    compact = _WHITESPACE_RE.sub(" ", raw.replace("　", " "))

    postcode = None
    postcode_match = _POSTCODE_RE.search(compact)
    if postcode_match:
        postcode = f"{postcode_match.group(1)}-{postcode_match.group(2)}"
        compact = _POSTCODE_RE.sub("", compact).strip()

    precision = LocationPrecision.UNKNOWN
    if "丁目" in compact or "番地" in compact or re.search(r"\d+号", compact) or re.search(r"\d+-\d+", compact):
        precision = LocationPrecision.STREET_BLOCK
    elif "町" in compact or "字" in compact:
        precision = LocationPrecision.TOWN_AZA
    elif re.search(r"[市区町村]", compact):
        precision = LocationPrecision.MUNICIPALITY
    elif re.search(r"[都道府県]", compact):
        precision = LocationPrecision.PREFECTURE

    return AddressValue(
        normalized=compact,
        postcode=postcode,
        precision=precision,
        raw=raw,
    )
