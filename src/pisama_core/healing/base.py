"""Base fix class."""

from abc import ABC, abstractmethod
from typing import Optional

from pisama_core.healing.models import FixContext, FixResult, RollbackResult
from pisama_core.traces.enums import Platform


class BaseFix(ABC):
    """Abstract base class for fix implementations.

    To create a new fix:
    1. Subclass BaseFix
    2. Set name, description, and platforms
    3. Implement can_apply(), apply(), and optionally rollback()

    Example:
        class MyFix(BaseFix):
            name = "my_fix"
            description = "Applies my specific fix"

            async def can_apply(self, context: FixContext) -> bool:
                return True

            async def apply(self, context: FixContext) -> FixResult:
                # Apply the fix
                return FixResult(success=True, fix_type=self.name, message="Fixed!")
    """

    # Fix identity
    name: str = "base_fix"
    description: str = "Base fix"
    version: str = "1.0.0"

    # Which platforms this fix applies to
    platforms: list[Platform] = []  # Empty = all

    # Requirements
    requires_approval: bool = True
    reversible: bool = True

    # Risk assessment
    risk_level: str = "low"  # low, medium, high

    def applies_to_platform(self, platform: Platform) -> bool:
        """Check if this fix applies to a platform."""
        if not self.platforms:
            return True
        return platform in self.platforms

    @abstractmethod
    async def can_apply(self, context: FixContext) -> bool:
        """Check if this fix can be applied in the current context.

        Args:
            context: The fix context

        Returns:
            True if the fix can be applied
        """
        ...

    @abstractmethod
    async def apply(self, context: FixContext) -> FixResult:
        """Apply the fix.

        Args:
            context: The fix context

        Returns:
            Result of applying the fix
        """
        ...

    async def rollback(self, context: FixContext) -> RollbackResult:
        """Rollback the fix.

        Override this to implement custom rollback logic.

        Args:
            context: The fix context

        Returns:
            Result of the rollback
        """
        if not self.reversible:
            return RollbackResult(
                success=False,
                message="This fix is not reversible",
            )

        return RollbackResult(
            success=False,
            message="Rollback not implemented",
        )

    def get_instruction(self, context: Optional[FixContext] = None) -> str:
        """Get the instruction text for this fix.

        Override to provide context-specific instructions.
        """
        return self.description

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name})>"
