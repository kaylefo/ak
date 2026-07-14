"""Classifier for pages with no inventory."""

from __future__ import annotations

import re

from tsubo_contracts.enums import CoverageState

_NO_INVENTORY_PATTERNS = [
    re.compile(r"現在、物件はありません"),
    re.compile(r"掲載物件はございません"),
    re.compile(r"該当する物件がありません"),
    re.compile(r"物件情報は0件です"),
    re.compile(r"空き家情報はありません"),
    re.compile(r"現在募集している物件はありません"),
    re.compile(r"0件"),
]


class NoInventoryClassifier:
    """Detect zero-inventory municipal pages."""

    def classify(self, html: str) -> CoverageState | None:
        text = html.replace(" ", "").replace("　", "")
        hits = sum(1 for pattern in _NO_INVENTORY_PATTERNS if pattern.search(text))
        if hits >= 1 and ("0件" in text or "ありません" in text):
            return CoverageState.DIRECT_ZERO_INVENTORY
        return None

    def is_no_inventory(self, html: str) -> bool:
        return self.classify(html) == CoverageState.DIRECT_ZERO_INVENTORY
