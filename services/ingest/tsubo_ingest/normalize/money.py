"""Normalize Japanese monetary expressions to yen integers."""

from __future__ import annotations

import re
from dataclasses import dataclass

from tsubo_contracts.enums import PriceKind

_FULLWIDTH_DIGITS = str.maketrans("０１２３４５６７８９", "0123456789")
_CURRENCY_RE = re.compile(
    r"(無償|無料|相談|要相談|応相談|未定|非公開|"
    r"([\d,，．.０-９]+)\s*(万円|億円|円|万)?)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class MoneyValue:
    amount_yen: int | None
    kind: PriceKind
    raw: str


def _to_ascii_digits(text: str) -> str:
    return text.translate(_FULLWIDTH_DIGITS).replace("，", ",").replace("．", ".")


def normalize_money(text: str | None) -> MoneyValue:
    if not text:
        return MoneyValue(amount_yen=None, kind=PriceKind.UNKNOWN, raw="")

    raw = text.strip()
    compact = raw.replace(" ", "").replace("　", "")

    if any(token in compact for token in ("無償", "無料", "0円")):
        return MoneyValue(amount_yen=0, kind=PriceKind.ZERO_PRICE, raw=raw)
    if "要相談" in compact or "応相談" in compact or compact == "相談":
        return MoneyValue(amount_yen=None, kind=PriceKind.NEGOTIABLE, raw=raw)
    if "未定" in compact or "非公開" in compact:
        return MoneyValue(amount_yen=None, kind=PriceKind.UNDISCLOSED, raw=raw)

    match = _CURRENCY_RE.search(compact)
    if not match:
        return MoneyValue(amount_yen=None, kind=PriceKind.UNKNOWN, raw=raw)

    if match.group(1) in {"無償", "無料"}:
        return MoneyValue(amount_yen=0, kind=PriceKind.ZERO_PRICE, raw=raw)
    if match.group(1) in {"相談", "要相談", "応相談", "未定", "非公開"}:
        kind = PriceKind.NEGOTIABLE if "相談" in match.group(1) else PriceKind.UNDISCLOSED
        return MoneyValue(amount_yen=None, kind=kind, raw=raw)

    number_text = _to_ascii_digits(match.group(2)).replace(",", "")
    try:
        value = float(number_text)
    except ValueError:
        return MoneyValue(amount_yen=None, kind=PriceKind.UNKNOWN, raw=raw)

    unit = match.group(3) or "円"
    if unit == "万円" or unit == "万":
        yen = int(value * 10_000)
    elif unit == "億円":
        yen = int(value * 100_000_000)
    else:
        yen = int(value)

    return MoneyValue(amount_yen=yen, kind=PriceKind.FIXED, raw=raw)
