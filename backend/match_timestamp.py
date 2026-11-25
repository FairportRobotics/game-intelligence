"""Parse normalized Match timestamps into timezone-aware UTC values."""

from datetime import datetime, timezone


def parse_match_timestamp(value: object) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("must be an ISO-8601 timestamp with a timezone")
    timestamp = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(timestamp)
    except ValueError as error:
        raise ValueError("must be an ISO-8601 timestamp with a timezone") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("must include a timezone offset")
    return parsed.astimezone(timezone.utc)
