"""Detection engine for PISAMA.

Provides 20+ detectors for identifying agent failure patterns.
"""

from pisama_core.detection.base import BaseDetector
from pisama_core.detection.result import DetectionResult, Evidence, FixRecommendation
from pisama_core.detection.registry import DetectorRegistry, registry
from pisama_core.detection.orchestrator import DetectionOrchestrator

__all__ = [
    "BaseDetector",
    "DetectionResult",
    "Evidence",
    "FixRecommendation",
    "DetectorRegistry",
    "registry",
    "DetectionOrchestrator",
]
