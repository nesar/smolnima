"""NIMA agent creation and configuration."""

from smolagents import CodeAgent, Tool
from typing import List, Optional
import os

from ..models import GeminiModel
from ..prompts import PHYSICS_SYSTEM_PROMPT
from ..tools import (
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


def create_nima_agent(
    config,
    additional_tools: Optional[List[Tool]] = None
) -> CodeAgent:
    """
    Create and configure the NIMA agent.

    Args:
        config: Configuration object with api_key, model_name, etc.
        additional_tools: Optional list of additional tools to include

    Returns:
        Configured CodeAgent ready to use
    """
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

    # Set system prompt using the new property format
    agent.prompt_templates["system_prompt"] = PHYSICS_SYSTEM_PROMPT

    return agent
