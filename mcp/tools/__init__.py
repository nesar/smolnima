"""
Physics tools package for MCP server.

This package imports tools from agent.tools to avoid duplication.
All tool definitions live in agent/tools/ and are automatically
exposed via MCP by importing them here.
"""

import sys
import os

# Add parent directory to path to import from agent
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, parent_dir)

# Import directly from agent.tools submodules to avoid triggering agent.__init__
# This prevents unnecessary dependencies from being loaded
from agent.tools.particle_physics import (
    calculate_relativistic_energy,
    calculate_lorentz_factor,
    get_particle_properties,
    calculate_decay_probability,
    calculate_binding_energy,
)
from agent.tools.gan_physics import (
    generate_physics_events,
    visualize_quark_distributions,
)
from agent.tools.rag_tool import (
    search_knowledge_base,
    load_documents_from_directory,
)

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
