"""Time utilities."""

from datetime import datetime, timezone


def now_utc() -> datetime:
    """Get current UTC timestamp."""
    return datetime.now(timezone.utc)


def parse_iso_datetime(s: str) -> datetime:
    """Parse ISO format datetime string."""
    return datetime.fromisoformat(s)
