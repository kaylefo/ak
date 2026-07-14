"""Deterministic glossary-based translation service."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from tsubo_contracts.enums import TranslationState

ROOT = Path(__file__).resolve().parents[4]
GLOSSARY_PATH = ROOT / "data" / "glossary" / "terms.json"


@lru_cache(maxsize=1)
def _load_glossary() -> list[tuple[str, str]]:
    if not GLOSSARY_PATH.exists():
        return []
    entries = json.loads(GLOSSARY_PATH.read_text(encoding="utf-8"))
    return [(item["ja"], item["en"]) for item in entries if item.get("ja") and item.get("en")]


class GlossaryTranslationService:
    """Apply longest-match glossary substitution; preserve untranslated segments."""

    provider = "glossary_deterministic"
    version = "1.0.0"

    def translate_text(self, text: str | None) -> str | None:
        if not text or not text.strip():
            return None
        result = text
        for ja, en in sorted(_load_glossary(), key=lambda x: len(x[0]), reverse=True):
            result = result.replace(ja, en)
        return result

    def translation_state(self, source: str | None, translated: str | None) -> TranslationState:
        if not source:
            return TranslationState.NOT_REQUIRED
        if not translated or translated == source:
            return TranslationState.PENDING
        return TranslationState.MACHINE_TRANSLATED

    def translate_fields(self, fields: dict[str, str | None]) -> dict[str, str | None]:
        return {key: self.translate_text(value) for key, value in fields.items()}
