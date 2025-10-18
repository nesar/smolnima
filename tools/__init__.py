"""Physics tools for smolnima."""

# Support both package and direct imports
try:
    from .particle_physics import *
    from .gan_physics import *
    from .rag_tool import search_knowledge_base
except ImportError:
    from particle_physics import *
    from gan_physics import *
    from rag_tool import search_knowledge_base

__all__ = [
    "calculate_relativistic_energy",
    "calculate_lorentz_factor",
    "get_particle_properties",
    "calculate_decay_probability",
    "calculate_binding_energy",
    "generate_physics_events",
    "visualize_quark_distributions",
    "search_knowledge_base",
]
