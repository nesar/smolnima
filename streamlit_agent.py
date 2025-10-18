"""Agent wrapper for Streamlit with enhanced logging."""

from smolagents import CodeAgent
import streamlit as st
from agent import create_nima_agent, PHYSICS_SYSTEM_PROMPT
from models import GeminiModel
import matplotlib.pyplot as plt
import io
import sys
from io import StringIO
import re


class StreamlitCodeAgent(CodeAgent):
    """CodeAgent with Streamlit-specific logging and code capture."""

    def __init__(self, *args, **kwargs):
        """Initialize with logging support."""
        super().__init__(*args, **kwargs)
        self.step_count = 0
        self.executed_code_blocks = []
        self.verbose_output = []

    @staticmethod
    def clean_ansi_codes(text: str) -> str:
        """Remove ANSI color codes and escape sequences from text."""
        # Remove ANSI escape sequences
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        text = ansi_escape.sub('', text)

        # Remove other ANSI codes
        ansi_escape_extended = re.compile(r'\x1b\[[\d;]*[A-Za-z]')
        text = ansi_escape_extended.sub('', text)

        return text

    @staticmethod
    def extract_useful_output(text: str) -> dict:
        """Extract and structure useful information from verbose output."""
        lines = text.split('\n')
        sections = []
        current_section = None
        in_code_block = False
        code_lines = []

        for line in lines:
            # Skip box drawing characters and decorative lines
            if any(char in line for char in ['─', '╭', '╮', '╯', '╰', '┃', '━', '│']):
                continue

            # Skip "New run" headers and model info
            if 'New run' in line or 'GeminiModel' in line:
                continue

            # Skip "Step X" and "Output message" separator lines
            if re.match(r'^\s*Step \d+\s*$', line) or 'Output message of the LLM:' in line:
                continue

            # Detect section headers
            if line.strip().startswith('Thought:'):
                if current_section:
                    sections.append(current_section)
                current_section = {'type': 'thought', 'content': [line.replace('Thought:', '').strip()]}
                continue

            elif line.strip().startswith('Code:'):
                if current_section:
                    sections.append(current_section)
                current_section = {'type': 'code', 'content': []}
                in_code_block = False
                continue

            elif line.strip().startswith('Observation:'):
                if current_section:
                    sections.append(current_section)
                current_section = {'type': 'observation', 'content': [line.replace('Observation:', '').strip()]}
                continue

            elif 'Execution logs:' in line:
                if current_section:
                    sections.append(current_section)
                current_section = {'type': 'execution', 'content': []}
                continue

            elif line.strip().startswith('Out -') or line.strip().startswith('Final answer:'):
                if current_section:
                    sections.append(current_section)
                content = line.replace('Out -', '').replace('Final answer:', '').strip()
                current_section = {'type': 'final', 'content': [content]}
                continue

            # Handle code blocks
            if current_section and current_section['type'] == 'code':
                if '```py' in line:
                    in_code_block = True
                    continue
                elif '```' in line and in_code_block:
                    in_code_block = False
                    continue
                elif '<end_code>' in line:
                    continue
                elif in_code_block or line.strip():
                    current_section['content'].append(line)
                continue

            # Add content to current section
            if current_section and line.strip() and not line.strip().startswith('['):
                current_section['content'].append(line.strip())

        # Add last section
        if current_section:
            sections.append(current_section)

        return sections

    def run(self, task, **kwargs):
        """Run agent with step logging and output capture."""
        logger = st.session_state.get("logger")

        if logger:
            logger.info(f"Starting task: {task[:100]}", "agent")

        self.step_count = 0
        self.executed_code_blocks = []
        self.verbose_output = []

        # Store reference in session state for access
        if "executed_code" not in st.session_state:
            st.session_state.executed_code = []
        if "agent_output" not in st.session_state:
            st.session_state.agent_output = []

        # Clear previous execution's data
        st.session_state.executed_code = []
        st.session_state.agent_output = []

        # Capture stdout/stderr during execution
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        captured_output = StringIO()

        try:
            # Redirect output
            sys.stdout = captured_output
            sys.stderr = captured_output

            result = super().run(task, **kwargs)

            # Restore output
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            # Store captured output after cleaning
            output_text = captured_output.getvalue()
            if output_text:
                # Clean ANSI codes and extract useful information
                cleaned_text = self.clean_ansi_codes(output_text)
                sections = self.extract_useful_output(cleaned_text)

                if sections:
                    st.session_state.agent_output.append(sections)
                    self.verbose_output.append(sections)

            if logger:
                logger.success(f"Task completed in {self.step_count} steps", "agent")
            return result

        except Exception as e:
            # Restore output
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            # Store captured output even on error
            output_text = captured_output.getvalue()
            if output_text:
                # Clean ANSI codes and extract useful information
                cleaned_text = self.clean_ansi_codes(output_text)
                sections = self.extract_useful_output(cleaned_text)

                if sections:
                    st.session_state.agent_output.append(sections)
                    self.verbose_output.append(sections)

            if logger:
                logger.error(f"Task failed: {str(e)}", "agent")
            raise

    def execute_python_code(self, code: str, **kwargs):
        """Override to capture executed code."""
        logger = st.session_state.get("logger")

        # Log the code execution
        if logger:
            logger.info("Executing Python code", "agent")

        # Store the code block
        self.executed_code_blocks.append(code)
        st.session_state.executed_code.append(code)

        # Execute the code using parent method
        result = super().execute_python_code(code, **kwargs)

        return result

    def step(self, *args, **kwargs):
        """Override step to add logging."""
        self.step_count += 1
        logger = st.session_state.get("logger")

        if logger:
            logger.step(self.step_count, f"Executing step {self.step_count}")

        return super().step(*args, **kwargs)


def create_streamlit_agent(config):
    """
    Create agent with Streamlit logging support.

    Args:
        config: Configuration object

    Returns:
        StreamlitCodeAgent instance
    """
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
    import os

    # Initialize model with retry logic
    model = GeminiModel(
        model_id=config.model_name,
        api_key=config.api_key,
        temperature=config.temperature,
        max_retries=3,
        retry_delay=2.0
    )

    # Load documents
    if os.path.exists(config.pdfs_dir):
        doc_count = load_documents_from_directory(config.pdfs_dir)
        if config.verbose and doc_count > 0:
            logger = st.session_state.get("logger")
            if logger:
                logger.info(f"Loaded {doc_count} documents from {config.pdfs_dir}", "system")

    # Collect tools
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

    # Create agent
    agent = StreamlitCodeAgent(
        tools=tools,
        model=model,
        max_steps=config.max_steps,
        verbosity_level=2 if config.verbose else 0,
        additional_authorized_imports=["numpy", "matplotlib", "scipy", "pandas"],
    )

    agent.system_prompt = PHYSICS_SYSTEM_PROMPT

    return agent
