"""
smolnima - Nuclear Imaging with Multi-Agents (smolagents edition)

A minimal, crisp implementation of Dr. NIMA using smolagents framework.
Provides physics research capabilities with RAG, code execution, and specialized tools.
"""

__version__ = "0.1.0"
__author__ = "Dr. NIMA Team"

# Support both package and direct imports
try:
    from .agent import create_nima_agent
    from .config import Config
except ImportError:
    from agent import create_nima_agent
    from config import Config

__all__ = ["create_nima_agent", "Config"]
