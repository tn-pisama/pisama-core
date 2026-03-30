"""Adapter for Karpathy's autoresearch framework.

Converts autoresearch experiment cycles into PISAMA-compatible traces,
enabling convergence detection and all other PISAMA detectors to monitor
autonomous research runs.

Trace structure per experiment:
    Trace: autoresearch_run_{timestamp}
    ├── Span: experiment_{n} (kind=AGENT)
    │   ├── Span: hypothesis (kind=LLM)
    │   ├── Span: code_modification (kind=TOOL)
    │   ├── Span: training_run (kind=CHAIN)
    │   │   └── attributes: {val_bpb, train_loss, ...}
    │   └── Span: evaluation (kind=TOOL)
"""

import sys
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from pisama_core.adapters.base import (
    PlatformAdapter,
    InjectionMethod,
    InjectionResult,
)
from pisama_core.injection.enforcement import EnforcementLevel
from pisama_core.traces.enums import Platform, SpanKind, SpanStatus
from pisama_core.traces.models import Span


class AutoresearchAdapter(PlatformAdapter):
    """Adapter for Karpathy's autoresearch framework.

    Wraps experiment cycles and emits PISAMA-compatible spans for
    convergence detection, loop detection, and other analysis.
    """

    def __init__(self) -> None:
        self._trace_id: str = f"autoresearch_{uuid.uuid4().hex[:12]}"
        self._experiments: List[Dict[str, Any]] = []
        self._metrics_history: List[Dict[str, float]] = []

    @property
    def platform_name(self) -> Platform:
        return Platform.AUTORESEARCH

    @property
    def platform_version(self) -> Optional[str]:
        return "1.0"

    def capture_experiment(
        self,
        experiment_id: str,
        hypothesis: str,
        code_diff: str,
        metrics_before: Dict[str, float],
        metrics_after: Dict[str, float],
        decision: str,
        duration_seconds: float,
        start_time: Optional[datetime] = None,
    ) -> Span:
        """Convert one experiment cycle into a Span with child spans.

        Args:
            experiment_id: Unique experiment identifier.
            hypothesis: Agent's hypothesis text.
            code_diff: Diff applied to train.py.
            metrics_before: Metrics before training run.
            metrics_after: Metrics after training run.
            decision: 'keep' or 'discard'.
            duration_seconds: Total experiment wall-clock time.
            start_time: Optional start time (defaults to now).

        Returns:
            Root Span for the experiment.
        """
        now = start_time or datetime.now(timezone.utc)
        end = now + timedelta(seconds=duration_seconds)

        # Root span for the experiment
        root = Span(
            span_id=experiment_id,
            trace_id=self._trace_id,
            name=f"experiment_{len(self._experiments)}",
            kind=SpanKind.AGENT,
            platform=Platform.AUTORESEARCH,
            start_time=now,
            end_time=end,
            status=SpanStatus.OK,
            attributes={
                "autoresearch.experiment_id": experiment_id,
                "autoresearch.decision": decision,
                "autoresearch.hypothesis": hypothesis[:500],
                **{f"autoresearch.metric.{k}": v for k, v in metrics_after.items()},
            },
            input_data={"hypothesis": hypothesis, "metrics_before": metrics_before},
            output_data={"metrics_after": metrics_after, "decision": decision},
            platform_metadata={
                "code_diff": code_diff[:2000],
                "duration_seconds": duration_seconds,
            },
        )

        # Track experiment and metrics
        self._experiments.append({
            "id": experiment_id,
            "hypothesis": hypothesis,
            "decision": decision,
            "metrics_before": metrics_before,
            "metrics_after": metrics_after,
        })
        self._metrics_history.append(metrics_after)

        return root

    def capture_span(self, raw_data: Any) -> Span:
        """Capture a span from raw experiment data dict.

        Args:
            raw_data: Dict with keys matching capture_experiment params.

        Returns:
            Span representing the experiment.
        """
        if isinstance(raw_data, dict):
            return self.capture_experiment(
                experiment_id=raw_data.get("experiment_id", uuid.uuid4().hex[:12]),
                hypothesis=raw_data.get("hypothesis", ""),
                code_diff=raw_data.get("code_diff", ""),
                metrics_before=raw_data.get("metrics_before", {}),
                metrics_after=raw_data.get("metrics_after", {}),
                decision=raw_data.get("decision", "unknown"),
                duration_seconds=raw_data.get("duration_seconds", 300.0),
            )
        raise ValueError(f"Expected dict, got {type(raw_data)}")

    def inject_fix(
        self,
        directive: str,
        level: EnforcementLevel,
        directive_id: Optional[str] = None,
    ) -> InjectionResult:
        """Emit fix as stderr warning.

        autoresearch has no built-in fix injection mechanism, so we output
        warnings to stderr for the operator to act on.
        """
        prefix = f"[PISAMA:{level.value}]"
        message = f"{prefix} {directive}"
        print(message, file=sys.stderr)
        return InjectionResult(
            success=True,
            method=InjectionMethod.STDERR,
            message=message,
            directive_id=directive_id,
        )

    def get_supported_injection_methods(self) -> list[InjectionMethod]:
        return [InjectionMethod.STDERR]

    def get_state(self) -> dict[str, Any]:
        return {
            "trace_id": self._trace_id,
            "experiment_count": len(self._experiments),
            "last_decision": self._experiments[-1]["decision"] if self._experiments else None,
            "metrics_history_length": len(self._metrics_history),
        }

    def get_session_context(self) -> dict[str, Any]:
        return {
            "experiments": self._experiments[-10:],
            "metrics_history": self._metrics_history[-20:],
        }

    def can_block(self) -> bool:
        return False

    def block_action(self, reason: str) -> bool:
        return False

    def get_metrics_for_convergence(
        self, metric_name: str = "val_bpb",
    ) -> List[Dict[str, Any]]:
        """Extract metric time series for convergence detection.

        Args:
            metric_name: Which metric to extract from metrics_after.

        Returns:
            List of {step, value, label} dicts for ConvergenceDetector.
        """
        metrics = []
        for i, m in enumerate(self._metrics_history):
            if metric_name in m:
                metrics.append({
                    "step": i,
                    "value": m[metric_name],
                    "label": self._experiments[i]["id"] if i < len(self._experiments) else f"exp_{i}",
                })
        return metrics
