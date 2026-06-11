from datetime import datetime
from typing import Any


def truncate_datetime_to_seconds(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.replace(microsecond=0)


def coerce_datetime_to_seconds(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return truncate_datetime_to_seconds(value)
    if not isinstance(value, str):
        return None
    try:
        return truncate_datetime_to_seconds(datetime.fromisoformat(value))
    except ValueError:
        return None
