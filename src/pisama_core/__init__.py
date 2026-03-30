"""PISAMA Core - Detection, Scoring, and Healing Engine for Agent Forensics.

This package provides the shared core functionality for the PISAMA platform,
supporting multiple agent frameworks including Claude Code, LangGraph, AutoGen,
CrewAI, and n8n.

Example:
    from pisama_core import DetectionOrchestrator, ScoringEngine, Trace

    orchestrator = DetectionOrchestrator()
    scoring = ScoringEngine()

    result = await orchestrator.analyze(trace)
    severity = scoring.calculate_severity([result])
"""

__version__ = "1.0.0"

# Traces
from pisama_core.traces.models import Event, Span, Trace, TraceMetadata
from pisama_core.traces.enums import Platform, SpanKind, SpanStatus

# Detection
from pisama_core.detection.base import BaseDetector
from pisama_core.detection.result import DetectionResult, Evidence, FixRecommendation
from pisama_core.detection.registry import DetectorRegistry, registry
from pisama_core.detection.orchestrator import DetectionOrchestrator

# Scoring
from pisama_core.scoring.engine import ScoringEngine
from pisama_core.scoring.thresholds import Thresholds, SeverityLevel

# Healing
from pisama_core.healing.models import FixContext, FixResult, HealingPlan
from pisama_core.healing.base import BaseFix
from pisama_core.healing.engine import HealingEngine

# Injection
from pisama_core.injection.protocol import FixInjectionProtocol
from pisama_core.injection.enforcement import EnforcementLevel, EnforcementEngine

# Audit
from pisama_core.audit.logger import AuditLogger
from pisama_core.audit.models import AuditEvent, AuditEventType

# Config
from pisama_core.config.models import PisamaConfig, DetectionConfig, HealingConfig
from pisama_core.config.loader import load_config

# Adapters
from pisama_core.adapters.base import PlatformAdapter, InjectionResult

# Tokenization
from pisama_core.tokenization import (
    PIIDetector,
    PIIMatch,
    PIIPattern,
    PIIType,
    TokenGenerator,
    TokenParser,
    TokenVault,
    KeychainManager,
    Tokenizer,
    tokenize_trace_data,
)

__all__ = [
    # Version
    "__version__",
    # Traces
    "Event",
    "Span",
    "Trace",
    "TraceMetadata",
    "Platform",
    "SpanKind",
    "SpanStatus",
    # Detection
    "BaseDetector",
    "DetectionResult",
    "Evidence",
    "FixRecommendation",
    "DetectorRegistry",
    "registry",
    "DetectionOrchestrator",
    # Scoring
    "ScoringEngine",
    "Thresholds",
    "SeverityLevel",
    # Healing
    "FixContext",
    "FixResult",
    "HealingPlan",
    "BaseFix",
    "HealingEngine",
    # Injection
    "FixInjectionProtocol",
    "EnforcementLevel",
    "EnforcementEngine",
    # Audit
    "AuditLogger",
    "AuditEvent",
    "AuditEventType",
    # Config
    "PisamaConfig",
    "DetectionConfig",
    "HealingConfig",
    "load_config",
    # Adapters
    "PlatformAdapter",
    "InjectionResult",
    # Tokenization
    "PIIDetector",
    "PIIMatch",
    "PIIPattern",
    "PIIType",
    "TokenGenerator",
    "TokenParser",
    "TokenVault",
    "KeychainManager",
    "Tokenizer",
    "tokenize_trace_data",
]
