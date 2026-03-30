"""Built-in detectors for PISAMA.

This module auto-registers all built-in detectors with the global registry.
"""

from pisama_core.detection.registry import registry

# Import detectors to trigger registration
from pisama_core.detection.detectors.loop import LoopDetector
from pisama_core.detection.detectors.repetition import RepetitionDetector
from pisama_core.detection.detectors.coordination import CoordinationDetector
from pisama_core.detection.detectors.hallucination import HallucinationDetector
from pisama_core.detection.detectors.cost import CostDetector

# Register all built-in detectors
_BUILTIN_DETECTORS = [
    LoopDetector(),
    RepetitionDetector(),
    CoordinationDetector(),
    HallucinationDetector(),
    CostDetector(),
]

for detector in _BUILTIN_DETECTORS:
    registry.register(detector)

__all__ = [
    "LoopDetector",
    "RepetitionDetector",
    "CoordinationDetector",
    "HallucinationDetector",
    "CostDetector",
]
