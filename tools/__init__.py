"""Physics tools for smolnima - backward compatibility wrapper."""

# Use importlib to import tools directly without triggering agent.__init__
# This allows MCP server to use tools without requiring full agent dependencies
import importlib
import sys

# Import particle physics tools
_particle_physics = importlib.import_module('agent.tools.particle_physics')
calculate_relativistic_energy = _particle_physics.calculate_relativistic_energy
calculate_lorentz_factor = _particle_physics.calculate_lorentz_factor
get_particle_properties = _particle_physics.get_particle_properties
calculate_decay_probability = _particle_physics.calculate_decay_probability
calculate_binding_energy = _particle_physics.calculate_binding_energy

# Import GAN physics tools
_gan_physics = importlib.import_module('agent.tools.gan_physics')
generate_physics_events = _gan_physics.generate_physics_events
visualize_quark_distributions = _gan_physics.visualize_quark_distributions

# Import RAG tools
_rag_tool = importlib.import_module('agent.tools.rag_tool')
search_knowledge_base = _rag_tool.search_knowledge_base
load_documents_from_directory = _rag_tool.load_documents_from_directory

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
