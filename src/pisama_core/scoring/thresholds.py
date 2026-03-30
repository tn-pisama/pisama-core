"""Severity thresholds and levels."""

from enum import Enum
from typing import Tuple


class SeverityLevel(str, Enum):
    """Severity level categories."""

    HEALTHY = "healthy"
    WARNING = "warning"
    PROBLEMATIC = "problematic"
    CRITICAL = "critical"
    SEVERE = "severe"

    def __str__(self) -> str:
        return self.value


class Thresholds:
    """Threshold definitions for severity scoring."""

    # Severity ranges
    HEALTHY: Tuple[int, int] = (0, 19)
    WARNING: Tuple[int, int] = (20, 39)
    PROBLEMATIC: Tuple[int, int] = (40, 59)
    CRITICAL: Tuple[int, int] = (60, 79)
    SEVERE: Tuple[int, int] = (80, 100)

    # Default thresholds for actions
    DEFAULT_ALERT_THRESHOLD = 40
    DEFAULT_BLOCK_THRESHOLD = 60
    DEFAULT_TERMINATE_THRESHOLD = 90

    @classmethod
    def get_level(cls, severity: int) -> SeverityLevel:
        """Get severity level for a score."""
        if severity <= cls.HEALTHY[1]:
            return SeverityLevel.HEALTHY
        elif severity <= cls.WARNING[1]:
            return SeverityLevel.WARNING
        elif severity <= cls.PROBLEMATIC[1]:
            return SeverityLevel.PROBLEMATIC
        elif severity <= cls.CRITICAL[1]:
            return SeverityLevel.CRITICAL
        else:
            return SeverityLevel.SEVERE

    @classmethod
    def should_alert(cls, severity: int, threshold: int = DEFAULT_ALERT_THRESHOLD) -> bool:
        """Whether severity should trigger an alert."""
        return severity >= threshold

    @classmethod
    def should_block(cls, severity: int, threshold: int = DEFAULT_BLOCK_THRESHOLD) -> bool:
        """Whether severity should trigger blocking."""
        return severity >= threshold

    @classmethod
    def should_terminate(cls, severity: int, threshold: int = DEFAULT_TERMINATE_THRESHOLD) -> bool:
        """Whether severity should trigger termination."""
        return severity >= threshold
