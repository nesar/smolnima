"""Core agent system for smolnima - no streamlit dependencies."""

from .agents import create_nima_agent
from .models import GeminiModel
from .prompts import PHYSICS_SYSTEM_PROMPT
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

__all__ = [
    "create_nima_agent",
    "GeminiModel",
    "PHYSICS_SYSTEM_PROMPT",
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
