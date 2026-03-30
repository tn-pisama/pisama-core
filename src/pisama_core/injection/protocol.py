"""Fix Injection Protocol (FIP) for structured fix directives."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from pisama_core.healing.base import BaseFix
from pisama_core.healing.models import FixContext
from pisama_core.injection.enforcement import EnforcementLevel


@dataclass
class Directive:
    """A fix directive to be injected."""

    directive_id: str
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    action: str
    instruction: str
    reason: str
    created_at: datetime
    expires_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "directive_id": self.directive_id,
            "priority": self.priority,
            "action": self.action,
            "instruction": self.instruction,
            "reason": self.reason,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


class FixInjectionProtocol:
    """Protocol for formatting and parsing fix directives.

    The FIP provides a structured format that agents can recognize
    and follow, with clear delimiters and required fields.
    """

    VERSION = "1.0"

    # Format template for directives
    DIRECTIVE_TEMPLATE = """
╔══════════════════════════════════════════════════════════════╗
║ [PISAMA:FIX v{version}]                                      ║
║ directive_id: {directive_id}                                 ║
║ priority: {priority}                                         ║
║ action: {action}                                             ║
║ instruction: |                                               ║
║   {instruction}                                              ║
║ reason: {reason}                                             ║
║ [/PISAMA:FIX]                                                ║
╚══════════════════════════════════════════════════════════════╝
""".strip()

    def __init__(self) -> None:
        self._directives: dict[str, Directive] = {}

    def create_directive(
        self,
        fix: BaseFix,
        context: FixContext,
        reason: str,
        level: EnforcementLevel,
    ) -> Directive:
        """Create a new directive from a fix.

        Args:
            fix: The fix to create directive for
            context: Fix context
            reason: Why this fix is needed
            level: Enforcement level

        Returns:
            A new Directive
        """
        directive_id = f"fix-{uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)

        # Map enforcement level to priority
        priority_map = {
            EnforcementLevel.SUGGEST: "MEDIUM",
            EnforcementLevel.DIRECT: "HIGH",
            EnforcementLevel.BLOCK: "CRITICAL",
            EnforcementLevel.TERMINATE: "CRITICAL",
        }

        directive = Directive(
            directive_id=directive_id,
            priority=priority_map.get(level, "MEDIUM"),
            action=fix.name,
            instruction=fix.get_instruction(context),
            reason=reason,
            created_at=now,
        )

        self._directives[directive_id] = directive
        return directive

    def format_directive(self, directive: Directive) -> str:
        """Format a directive as a string for injection.

        Args:
            directive: The directive to format

        Returns:
            Formatted directive string
        """
        # Indent multi-line instructions
        instruction = directive.instruction.replace("\n", "\n║   ")

        return self.DIRECTIVE_TEMPLATE.format(
            version=self.VERSION,
            directive_id=directive.directive_id,
            priority=directive.priority,
            action=directive.action,
            instruction=instruction,
            reason=directive.reason,
        )

    def format_simple(
        self,
        action: str,
        instruction: str,
        reason: str,
        priority: str = "HIGH",
    ) -> str:
        """Format a simple directive without creating a full Directive object.

        Args:
            action: Fix action name
            instruction: What to do
            reason: Why
            priority: Priority level

        Returns:
            Formatted directive string
        """
        directive_id = f"fix-{uuid4().hex[:8]}"
        instruction = instruction.replace("\n", "\n║   ")

        return self.DIRECTIVE_TEMPLATE.format(
            version=self.VERSION,
            directive_id=directive_id,
            priority=priority,
            action=action,
            instruction=instruction,
            reason=reason,
        )

    def parse_compliance_response(self, response: str) -> dict[str, Any]:
        """Parse an agent's response to check for compliance.

        Args:
            response: Agent's response text

        Returns:
            Dictionary with compliance information
        """
        # Look for compliance indicators
        compliance_phrases = [
            "i'll change my approach",
            "let me try a different",
            "stopping the loop",
            "asking for guidance",
            "following the directive",
        ]

        response_lower = response.lower()
        complied = any(phrase in response_lower for phrase in compliance_phrases)

        return {
            "complied": complied,
            "confidence": 0.8 if complied else 0.5,
        }

    def get_directive(self, directive_id: str) -> Optional[Directive]:
        """Get a directive by ID."""
        return self._directives.get(directive_id)

    def clear_directive(self, directive_id: str) -> bool:
        """Clear a directive after compliance."""
        if directive_id in self._directives:
            del self._directives[directive_id]
            return True
        return False
