"""JSON utilities."""

import json
from datetime import datetime
from typing import Any


def _default_serializer(obj: Any) -> Any:
    """Default JSON serializer for complex types."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def safe_json_dumps(obj: Any, **kwargs: Any) -> str:
    """Safely serialize object to JSON string."""
    kwargs.setdefault("default", _default_serializer)
    return json.dumps(obj, **kwargs)


def safe_json_loads(s: str) -> Any:
    """Safely deserialize JSON string."""
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return None
