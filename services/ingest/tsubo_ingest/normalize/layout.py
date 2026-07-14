"""Normalize Japanese room layout (間取り) expressions."""

from __future__ import annotations

import re
from dataclasses import dataclass

_LAYOUT_RE = re.compile(
    r"([0-9０-９]+)\s*(LDK|DK|K|R|SLDK|SDK|SK|LK|LD|DK|K)",
    re.IGNORECASE,
)
_FULLWIDTH_DIGITS = str.maketrans("０１２３４５６７８９", "0123456789")


@dataclass(frozen=True)
class LayoutValue:
    rooms: int | None
    layout_type: str | None
    normalized: str | None
    raw: str


def normalize_layout(text: str | None) -> LayoutValue:
    if not text:
        return LayoutValue(rooms=None, layout_type=None, normalized=None, raw="")

    raw = text.strip()
    compact = raw.replace(" ", "").replace("　", "")
    match = _LAYOUT_RE.search(compact.translate(_FULLWIDTH_DIGITS))
    if not match:
        return LayoutValue(rooms=None, layout_type=None, normalized=None, raw=raw)

    rooms = int(match.group(1))
    layout_type = match.group(2).upper()
    normalized = f"{rooms}{layout_type}"
    return LayoutValue(rooms=rooms, layout_type=layout_type, normalized=normalized, raw=raw)
