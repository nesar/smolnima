"""Model wrappers for smolagents - backward compatibility wrapper."""

# Re-export from new agent.models module for backward compatibility
from agent.models import GeminiModel

__all__ = ["GeminiModel"]
