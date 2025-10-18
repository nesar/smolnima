"""Experiment tracking and artifact saving."""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import json


class ExperimentTracker:
    """Track and save experiment artifacts to timestamped directories."""

    def __init__(self, base_dir: str = "./experiments"):
        """
        Initialize experiment tracker.

        Args:
            base_dir: Base directory for saving experiments
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.current_experiment_dir: Optional[Path] = None

    def start_experiment(self, description: str = "") -> Path:
        """
        Start a new experiment and create timestamped directory.

        Args:
            description: Optional description of experiment

        Returns:
            Path to experiment directory
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Create directory name
        if description:
            # Sanitize description for filename
            safe_desc = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in description)
            safe_desc = safe_desc[:50]  # Limit length
            dir_name = f"{timestamp}_{safe_desc}"
        else:
            dir_name = timestamp

        self.current_experiment_dir = self.base_dir / dir_name
        self.current_experiment_dir.mkdir(parents=True, exist_ok=True)

        # Create metadata file
        metadata = {
            "timestamp": timestamp,
            "description": description,
            "start_time": datetime.now().isoformat(),
        }

        with open(self.current_experiment_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        return self.current_experiment_dir

    def save_code(self, code: str, filename: str = "generated_code.py"):
        """
        Save generated code to experiment directory.

        Args:
            code: Python code to save
            filename: Name for the code file
        """
        if not self.current_experiment_dir:
            return

        filepath = self.current_experiment_dir / filename
        with open(filepath, "w") as f:
            f.write(code)

    def save_codes(self, codes: List[str]):
        """
        Save multiple code blocks to experiment directory.

        Args:
            codes: List of code blocks
        """
        if not self.current_experiment_dir:
            return

        for i, code in enumerate(codes, 1):
            filename = f"code_block_{i:02d}.py"
            self.save_code(code, filename)

    def save_output(self, output: str, filename: str = "output.txt"):
        """
        Save text output to experiment directory.

        Args:
            output: Text output to save
            filename: Name for the output file
        """
        if not self.current_experiment_dir:
            return

        filepath = self.current_experiment_dir / filename
        with open(filepath, "w") as f:
            f.write(output)

    def save_plot(self, plot_data: bytes, filename: str = None):
        """
        Save plot image to experiment directory.

        Args:
            plot_data: Binary image data
            filename: Optional filename (auto-generated if not provided)
        """
        if not self.current_experiment_dir:
            return

        if filename is None:
            # Auto-generate filename
            existing_plots = list(self.current_experiment_dir.glob("plot_*.png"))
            plot_num = len(existing_plots) + 1
            filename = f"plot_{plot_num:02d}.png"

        filepath = self.current_experiment_dir / filename
        with open(filepath, "wb") as f:
            f.write(plot_data)

    def save_plots(self, plots: List[bytes]):
        """
        Save multiple plots to experiment directory.

        Args:
            plots: List of binary image data
        """
        for plot_data in plots:
            self.save_plot(plot_data)

    def save_metadata(self, key: str, value):
        """
        Add metadata to the experiment.

        Args:
            key: Metadata key
            value: Metadata value
        """
        if not self.current_experiment_dir:
            return

        metadata_path = self.current_experiment_dir / "metadata.json"

        # Read existing metadata
        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
        else:
            metadata = {}

        # Update metadata
        metadata[key] = value

        # Write back
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

    def finish_experiment(self):
        """Mark experiment as finished and update metadata."""
        if not self.current_experiment_dir:
            return

        self.save_metadata("end_time", datetime.now().isoformat())
        self.current_experiment_dir = None

    def get_experiment_path(self) -> Optional[Path]:
        """Get current experiment directory path."""
        return self.current_experiment_dir

    def list_experiments(self) -> List[str]:
        """List all experiment directories."""
        if not self.base_dir.exists():
            return []

        experiments = [d.name for d in self.base_dir.iterdir() if d.is_dir() and d.name != '.gitkeep']
        return sorted(experiments, reverse=True)  # Most recent first
