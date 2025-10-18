"""Main agent setup for smolnima."""

from smolagents import CodeAgent, Tool
from typing import List, Optional
import os

# Support both package and direct imports
try:
    from .config import Config
    from .models import GeminiModel
    from .tools import (
        calculate_relativistic_energy,
        calculate_lorentz_factor,
        get_particle_properties,
        calculate_decay_probability,
        calculate_binding_energy,
        generate_physics_events,
        visualize_quark_distributions,
        search_knowledge_base,
    )
    from .tools.rag_tool import load_documents_from_directory
except ImportError:
    # Direct imports for Streamlit deployment
    from config import Config
    from models import GeminiModel
    from tools import (
        calculate_relativistic_energy,
        calculate_lorentz_factor,
        get_particle_properties,
        calculate_decay_probability,
        calculate_binding_energy,
        generate_physics_events,
        visualize_quark_distributions,
        search_knowledge_base,
    )
    from tools.rag_tool import load_documents_from_directory


PHYSICS_SYSTEM_PROMPT = """You are Dr. NIMA, an expert AI assistant specializing in particle and nuclear physics research.

Your capabilities:
- Answer questions about particle physics, nuclear physics, and quantum field theory
- Perform calculations using relativistic kinematics and quantum mechanics
- Generate and analyze particle physics event data
- Search physics literature and reference materials
- Create visualizations of physics concepts and data

When solving problems:
1. Break down complex questions into clear steps
2. Use available tools for calculations and data generation
3. Search the knowledge base for theoretical background when needed
4. Show your work and explain the physics concepts involved
5. Generate visualizations when they help explain concepts

Available tools can:
- Calculate relativistic energies, Lorentz factors, decay probabilities
- Get particle properties (mass, charge, lifetime, spin)
- Generate physics events from quark distribution models
- Visualize quark distributions and cross-sections
- Search the knowledge base for physics research and theory

Be precise, educational, and thorough in your responses."""


def create_nima_agent(
    config: Optional[Config] = None,
    additional_tools: Optional[List[Tool]] = None
) -> CodeAgent:
    """
    Create and configure the NIMA agent.

    Args:
        config: Configuration object (uses default if not provided)
        additional_tools: Optional list of additional tools to include

    Returns:
        Configured CodeAgent ready to use
    """
    if config is None:
        config = Config.from_env()

    # Initialize model
    model = GeminiModel(
        model_id=config.model_name,
        api_key=config.api_key,
        temperature=config.temperature
    )

    # Load documents if pdfs directory exists
    if os.path.exists(config.pdfs_dir):
        doc_count = load_documents_from_directory(config.pdfs_dir)
        if config.verbose and doc_count > 0:
            print(f"Loaded {doc_count} documents from {config.pdfs_dir}")

    # Collect all tools
    tools = [
        calculate_relativistic_energy,
        calculate_lorentz_factor,
        get_particle_properties,
        calculate_decay_probability,
        calculate_binding_energy,
        generate_physics_events,
        visualize_quark_distributions,
        search_knowledge_base,
    ]

    if additional_tools:
        tools.extend(additional_tools)

    # Create agent
    agent = CodeAgent(
        tools=tools,
        model=model,
        max_steps=config.max_steps,
        verbosity_level=2 if config.verbose else 0,
        additional_authorized_imports=["numpy", "matplotlib", "scipy", "pandas"],
    )

    # Set system prompt
    agent.system_prompt = PHYSICS_SYSTEM_PROMPT

    return agent
