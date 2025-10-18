"""Main agent setup for smolnima - backward compatibility wrapper."""

# Re-export from new agent module for backward compatibility
from agent import (
    create_nima_agent,
    GeminiModel,
    PHYSICS_SYSTEM_PROMPT,
)

__all__ = [
    "create_nima_agent",
    "GeminiModel",
    "PHYSICS_SYSTEM_PROMPT",
]
