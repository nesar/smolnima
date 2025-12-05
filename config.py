"""Configuration management for smolnima."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration for smolnima agent system."""

    # API Configuration
    api_key: Optional[str] = None
    model_name: str = "gemini-2.5-flash"

    # Paths
    pdfs_dir: str = "./pdfs"
    tools_dir: str = "./tools"

    # Agent Configuration
    max_steps: int = 10
    temperature: float = 0.3
    verbose: bool = True

    def __post_init__(self):
        """Load API key from environment if not provided."""
        if self.api_key is None:
            self.api_key = os.getenv("GOOGLE_API_KEY")

    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        return cls(
            api_key=os.getenv("GOOGLE_API_KEY"),
            model_name=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            pdfs_dir=os.getenv("PDFS_DIR", "./pdfs"),
            tools_dir=os.getenv("TOOLS_DIR", "./tools"),
            max_steps=int(os.getenv("MAX_STEPS", "10")),
            temperature=float(os.getenv("TEMPERATURE", "0.3")),
            verbose=os.getenv("VERBOSE", "true").lower() == "true"
        )
