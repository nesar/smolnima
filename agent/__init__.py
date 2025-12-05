"""Core agent system for smolnima - no streamlit dependencies."""

# Tools are always available (no heavy dependencies)
from .tools import (
    calculate_relativistic_energy,
    calculate_lorentz_factor,
    get_particle_properties,
    calculate_decay_probability,
    calculate_binding_energy,
    generate_physics_events,
    visualize_quark_distributions,
    search_knowledge_base,
    load_documents_from_directory,
)

# Agent components require smolagents - import only if available
try:
    from .agents import create_nima_agent
    from .models import GeminiModel
    from .prompts import PHYSICS_SYSTEM_PROMPT
    _AGENT_AVAILABLE = True
except ImportError:
    _AGENT_AVAILABLE = False
    create_nima_agent = None
    GeminiModel = None
    PHYSICS_SYSTEM_PROMPT = None

__all__ = [
    "calculate_relativistic_energy",
    "calculate_lorentz_factor",
    "get_particle_properties",
    "calculate_decay_probability",
    "calculate_binding_energy",
    "generate_physics_events",
    "visualize_quark_distributions",
    "search_knowledge_base",
    "load_documents_from_directory",
]

# Add agent components to exports if available
if _AGENT_AVAILABLE:
    __all__.extend([
        "create_nima_agent",
        "GeminiModel",
        "PHYSICS_SYSTEM_PROMPT",
    ])
