import re
from typing import Any

from tsubo_api.errors import ValidationError

_LAYOUT_PATTERN = re.compile(
    r"(?P<rooms>\d+)\s*(?:LDK|DK|K|R|SLDK|SDK)",
    re.IGNORECASE,
)
_ROOM_COUNT_PATTERN = re.compile(r"(?P<count>\d+)\s*(?:部屋|室)")


def parse_layout(value: str) -> dict[str, Any]:
    if not value or not str(value).strip():
        raise ValidationError("Layout value is empty")

    text = str(value).strip().upper()
    result: dict[str, Any] = {"raw": value}

    layout_match = _LAYOUT_PATTERN.search(text)
    if layout_match:
        rooms = int(layout_match.group("rooms"))
        layout_type = layout_match.group(0).replace(str(rooms), "").strip()
        result.update(
            {
                "bedrooms": rooms,
                "layout_type": layout_type,
                "label": layout_match.group(0),
            }
        )

    room_match = _ROOM_COUNT_PATTERN.search(value)
    if room_match:
        result["room_count"] = int(room_match.group("count"))

    if len(result) == 1:
        raise ValidationError(f"Unable to parse layout: {value}")

    return result


def normalize_layout(value: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(value, dict):
        if "raw" in value or "layout_type" in value:
            return value
        raise ValidationError("Invalid layout dictionary")
    return parse_layout(str(value))
