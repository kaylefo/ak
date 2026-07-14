import re
from datetime import date, datetime, timezone

from tsubo_api.errors import ValidationError

_REIWA_PATTERN = re.compile(
    r"令和(?P<year>\d{1,2})年(?P<month>\d{1,2})月(?P<day>\d{1,2})日"
)
_HEISEI_PATTERN = re.compile(
    r"平成(?P<year>\d{1,2})年(?P<month>\d{1,2})月(?P<day>\d{1,2})日"
)
_WESTERN_PATTERN = re.compile(
    r"(?P<year>\d{4})[/-](?P<month>\d{1,2})[/-](?P<day>\d{1,2})"
)
_JP_WESTERN_PATTERN = re.compile(
    r"(?P<year>\d{4})年(?P<month>\d{1,2})月(?P<day>\d{1,2})日"
)


def _era_to_western(era_year: int, era_offset: int) -> int:
    return era_offset + era_year


def parse_japanese_date(value: str) -> date:
    if not value or not str(value).strip():
        raise ValidationError("Date value is empty")

    text = str(value).strip()

    for pattern, offset in (( _REIWA_PATTERN, 2018), (_HEISEI_PATTERN, 1988)):
        match = pattern.search(text)
        if match:
            year = _era_to_western(int(match.group("year")), offset)
            return date(year, int(match.group("month")), int(match.group("day")))

    for pattern in (_WESTERN_PATTERN, _JP_WESTERN_PATTERN):
        match = pattern.search(text)
        if match:
            return date(
                int(match.group("year")),
                int(match.group("month")),
                int(match.group("day")),
            )

    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError as exc:
        raise ValidationError(f"Unable to parse date: {value}") from exc


def normalize_datetime(value: str | date | datetime) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    parsed = parse_japanese_date(str(value))
    return datetime(parsed.year, parsed.month, parsed.day, tzinfo=timezone.utc)
