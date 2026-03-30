"""Platform adapters for PISAMA.

Adapters provide the interface between pisama-core and specific
agent platforms (Claude Code, LangGraph, etc.).
"""

from pisama_core.adapters.base import (
    PlatformAdapter,
    InjectionResult,
    InjectionMethod,
)
from pisama_core.adapters.autoresearch import AutoresearchAdapter

__all__ = [
    "PlatformAdapter",
    "InjectionResult",
    "InjectionMethod",
    "AutoresearchAdapter",
]
