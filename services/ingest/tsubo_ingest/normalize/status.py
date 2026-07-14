"""Normalize Japanese listing status expressions."""

from __future__ import annotations

import re

from tsubo_contracts.enums import ListingStatus

_STATUS_PATTERNS: list[tuple[re.Pattern[str], ListingStatus]] = [
    (re.compile(r"募集中|受付中|申込受付中"), ListingStatus.APPLICATION_OPEN),
    (re.compile(r"新着|新規"), ListingStatus.NEW),
    (re.compile(r"商談中|交渉中"), ListingStatus.UNDER_NEGOTIATION),
    (re.compile(r"申込みあり|申込あり|申込済"), ListingStatus.APPLICATION_PENDING),
    (re.compile(r"予約|仮押"), ListingStatus.RESERVED),
    (re.compile(r"成約|売却済|売却完了|譲渡済"), ListingStatus.SOLD),
    (re.compile(r"賃貸中|入居済"), ListingStatus.RENTED),
    (re.compile(r"終了|受付終了|募集終了"), ListingStatus.APPLICATION_CLOSED),
    (re.compile(r"取下|取り下げ|非公開"), ListingStatus.WITHDRAWN),
    (re.compile(r"期限切れ|掲載終了"), ListingStatus.EXPIRED),
    (re.compile(r"空き|公開中|掲載中|利用可能"), ListingStatus.AVAILABLE),
    (re.compile(r"在庫なし|物件なし|該当なし|0件"), ListingStatus.REMOVED_FROM_SOURCE),
]


def normalize_status(text: str | None) -> ListingStatus:
    if not text:
        return ListingStatus.STATUS_UNKNOWN

    compact = text.strip().replace(" ", "").replace("　", "")
    for pattern, status in _STATUS_PATTERNS:
        if pattern.search(compact):
            return status

    return ListingStatus.STATUS_UNKNOWN
