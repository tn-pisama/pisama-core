"""Tests for pisama_core.detection module."""

import pytest
from datetime import datetime, timezone

from pisama_core.detection.result import (
    DetectionResult,
    Evidence,
    FixRecommendation,
    FixType,
)
from pisama_core.detection.base import BaseDetector
from pisama_core.detection.registry import DetectorRegistry
from pisama_core.traces.models import Trace, Span
from pisama_core.traces.enums import Platform, SpanKind


class TestEvidence:
    """Tests for Evidence model."""

    def test_create_evidence(self):
        """Test basic evidence creation."""
        evidence = Evidence(description="Loop detected in tool calls")
        assert evidence.description == "Loop detected in tool calls"
        assert evidence.span_ids == []
        assert evidence.data == {}

    def test_evidence_with_span_ids(self):
        """Test evidence with span IDs."""
        evidence = Evidence(
            description="Test",
            span_ids=["span-1", "span-2", "span-3"],
        )
        assert len(evidence.span_ids) == 3

    def test_evidence_to_dict(self):
        """Test evidence serialization."""
        evidence = Evidence(
            description="Test evidence",
            span_ids=["s1"],
            data={"count": 5},
            start_index=0,
            end_index=10,
        )
        data = evidence.to_dict()
        assert data["description"] == "Test evidence"
        assert data["span_ids"] == ["s1"]
        assert data["data"]["count"] == 5
        assert data["start_index"] == 0


class TestFixRecommendation:
    """Tests for FixRecommendation model."""

    def test_create_recommendation(self):
        """Test basic recommendation creation."""
        rec = FixRecommendation(
            fix_type=FixType.BREAK_LOOP,
            instruction="Stop the current loop and try a different approach",
        )
        assert rec.fix_type == FixType.BREAK_LOOP
        assert rec.priority == 1
        assert rec.requires_approval is True

    def test_recommendation_with_params(self):
        """Test recommendation with parameters."""
        rec = FixRecommendation(
            fix_type=FixType.ADD_DELAY,
            instruction="Add delay between retries",
            parameters={"delay_seconds": 5},
        )
        assert rec.parameters["delay_seconds"] == 5

    def test_recommendation_to_dict(self):
        """Test recommendation serialization."""
        rec = FixRecommendation(
            fix_type=FixType.ESCALATE,
            instruction="Escalate to user",
            priority=2,
            auto_approved=True,
        )
        data = rec.to_dict()
        assert data["fix_type"] == "escalate"
        assert data["priority"] == 2
        assert data["auto_approved"] is True


class TestDetectionResult:
    """Tests for DetectionResult model."""

    def test_create_result_no_issue(self):
        """Test creating a no-issue result."""
        result = DetectionResult.no_issue("test_detector")
        assert result.detected is False
        assert result.severity == 0
        assert result.detector_name == "test_detector"

    def test_create_result_issue_found(self):
        """Test creating an issue-found result."""
        result = DetectionResult.issue_found(
            detector_name="loop_detector",
            severity=65,
            summary="Loop detected: Read repeated 10 times",
        )
        assert result.detected is True
        assert result.severity == 65
        assert "Loop" in result.summary

    def test_result_with_recommendation(self):
        """Test result with fix recommendation."""
        result = DetectionResult.issue_found(
            detector_name="loop_detector",
            severity=70,
            summary="Loop detected",
            fix_type=FixType.BREAK_LOOP,
            fix_instruction="Break the loop and try different approach",
        )
        assert result.has_recommendation is True
        assert result.recommendation.fix_type == FixType.BREAK_LOOP

    def test_result_add_evidence(self):
        """Test adding evidence to result."""
        result = DetectionResult(detector_name="test")
        evidence = result.add_evidence(
            description="Found repeating pattern",
            span_ids=["s1", "s2", "s3"],
            data={"pattern_length": 3},
        )
        assert len(result.evidence) == 1
        assert result.evidence[0].description == "Found repeating pattern"

    def test_result_all_recommendations(self):
        """Test getting all recommendations."""
        result = DetectionResult(
            detector_name="test",
            recommendation=FixRecommendation(
                fix_type=FixType.BREAK_LOOP,
                instruction="Primary fix",
            ),
            alternative_recommendations=[
                FixRecommendation(
                    fix_type=FixType.SWITCH_STRATEGY,
                    instruction="Alternative 1",
                ),
                FixRecommendation(
                    fix_type=FixType.ESCALATE,
                    instruction="Alternative 2",
                ),
            ],
        )
        all_recs = result.all_recommendations
        assert len(all_recs) == 3

    def test_result_severity_clamped(self):
        """Test that severity is clamped to 0-100."""
        result = DetectionResult.issue_found("test", severity=150, summary="test")
        assert result.severity == 100

        result2 = DetectionResult.issue_found("test", severity=-10, summary="test")
        assert result2.severity == 0

    def test_result_to_dict(self):
        """Test result serialization."""
        result = DetectionResult.issue_found(
            detector_name="test",
            severity=50,
            summary="Test issue",
        )
        result.add_evidence("Evidence 1")
        data = result.to_dict()

        assert data["detector_name"] == "test"
        assert data["detected"] is True
        assert data["severity"] == 50
        assert len(data["evidence"]) == 1


class SimpleTestDetector(BaseDetector):
    """Simple detector for testing."""

    name = "simple_test"
    description = "A simple test detector"
    platforms = [Platform.CLAUDE_CODE]

    async def detect(self, trace: Trace) -> DetectionResult:
        """Detect if trace has more than 5 spans."""
        if len(trace.spans) > 5:
            return DetectionResult.issue_found(
                detector_name=self.name,
                severity=40,
                summary=f"Trace has {len(trace.spans)} spans (>5)",
            )
        return DetectionResult.no_issue(self.name)


class TestBaseDetector:
    """Tests for BaseDetector."""

    def test_detector_attributes(self):
        """Test detector has required attributes."""
        detector = SimpleTestDetector()
        assert detector.name == "simple_test"
        assert detector.enabled is True
        assert detector.realtime_capable is True

    def test_applies_to_platform(self):
        """Test platform filtering."""
        detector = SimpleTestDetector()
        assert detector.applies_to_platform(Platform.CLAUDE_CODE) is True
        assert detector.applies_to_platform(Platform.LANGGRAPH) is False

    @pytest.mark.asyncio
    async def test_run_detection(self, sample_trace):
        """Test running detection."""
        detector = SimpleTestDetector()
        result = await detector.run(sample_trace)

        assert result.detector_name == "simple_test"
        assert result.execution_time_ms >= 0

    @pytest.mark.asyncio
    async def test_run_detection_disabled(self, sample_trace):
        """Test that disabled detector returns no issue."""
        detector = SimpleTestDetector()
        detector.enabled = False
        result = await detector.run(sample_trace)

        assert result.detected is False


class TestDetectorRegistry:
    """Tests for DetectorRegistry."""

    def test_register_detector(self):
        """Test registering a detector."""
        registry = DetectorRegistry()
        detector = SimpleTestDetector()
        registry.register(detector)

        assert registry.count == 1
        assert registry.get("simple_test") is detector

    def test_register_duplicate_overwrites(self):
        """Test that duplicate registration overwrites."""
        registry = DetectorRegistry()
        detector = SimpleTestDetector()
        registry.register(detector)

        # Registering again should overwrite, not raise
        detector2 = SimpleTestDetector()
        registry.register(detector2)
        assert registry.count == 1
        assert registry.get("simple_test") is detector2

    def test_get_for_platform(self):
        """Test getting detectors for platform."""
        registry = DetectorRegistry()
        detector = SimpleTestDetector()
        registry.register(detector)

        claude_detectors = registry.get_for_platform(Platform.CLAUDE_CODE)
        assert len(claude_detectors) == 1

        langgraph_detectors = registry.get_for_platform(Platform.LANGGRAPH)
        assert len(langgraph_detectors) == 0

    def test_get_all(self):
        """Test getting all detectors."""
        registry = DetectorRegistry()
        detector = SimpleTestDetector()
        registry.register(detector)

        all_detectors = registry.get_all()
        assert len(all_detectors) == 1
