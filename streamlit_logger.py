"""Agent activity logger for Streamlit."""

import streamlit as st
from datetime import datetime
from typing import Optional, Callable
import io
import sys


class StreamlitAgentLogger:
    """Logger that captures agent activity for Streamlit display."""

    def __init__(self):
        """Initialize logger."""
        if "agent_logs" not in st.session_state:
            st.session_state.agent_logs = []

    def log(self, message: str, level: str = "info", agent: str = "system"):
        """
        Add a log entry.

        Args:
            message: Log message
            level: Log level (info, warning, error, success)
            agent: Agent name (system, agent, tool)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        log_entry = {
            "timestamp": timestamp,
            "message": message,
            "level": level,
            "agent": agent
        }

        st.session_state.agent_logs.append(log_entry)

    def info(self, message: str, agent: str = "agent"):
        """Log info message."""
        self.log(message, "info", agent)

    def success(self, message: str, agent: str = "agent"):
        """Log success message."""
        self.log(message, "success", agent)

    def warning(self, message: str, agent: str = "agent"):
        """Log warning message."""
        self.log(message, "warning", agent)

    def error(self, message: str, agent: str = "agent"):
        """Log error message."""
        self.log(message, "error", agent)

    def tool_call(self, tool_name: str, args: str = ""):
        """Log tool call."""
        msg = f"🔧 Calling tool: {tool_name}"
        if args:
            msg += f" with args: {args}"
        self.log(msg, "info", "tool")

    def tool_result(self, tool_name: str, success: bool = True):
        """Log tool result."""
        if success:
            self.log(f"✓ Tool {tool_name} completed", "success", "tool")
        else:
            self.log(f"✗ Tool {tool_name} failed", "error", "tool")

    def step(self, step_num: int, description: str):
        """Log agent step."""
        self.log(f"Step {step_num}: {description}", "info", "agent")

    def clear(self):
        """Clear all logs."""
        st.session_state.agent_logs = []

    def get_logs(self, limit: Optional[int] = None):
        """Get recent logs."""
        logs = st.session_state.agent_logs
        if limit:
            return logs[-limit:]
        return logs


class StreamCapture:
    """Capture stdout/stderr for agent activity."""

    def __init__(self, logger: StreamlitAgentLogger):
        """Initialize stream capture."""
        self.logger = logger
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.capture_buffer = io.StringIO()

    def __enter__(self):
        """Start capturing."""
        sys.stdout = self.capture_buffer
        sys.stderr = self.capture_buffer
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop capturing and log output."""
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

        output = self.capture_buffer.getvalue()
        if output.strip():
            # Parse output for tool calls and steps
            for line in output.strip().split('\n'):
                if line.strip():
                    # Try to detect tool calls
                    if "tool:" in line.lower() or "calling" in line.lower():
                        self.logger.tool_call(line.strip())
                    elif "step" in line.lower():
                        self.logger.step(0, line.strip())
                    else:
                        self.logger.info(line.strip())


def display_agent_logs(logger: StreamlitAgentLogger, limit: int = 50):
    """
    Display agent activity logs in Streamlit.

    Args:
        logger: StreamlitAgentLogger instance
        limit: Maximum number of recent logs to show
    """
    logs = logger.get_logs(limit)

    if not logs:
        st.info("No agent activity yet")
        return

    # Display logs with color coding
    for log in logs:
        timestamp = log["timestamp"]
        message = log["message"]
        level = log["level"]
        agent = log["agent"]

        # Color and icon based on level
        if level == "success":
            icon = "✅"
            color = "green"
        elif level == "warning":
            icon = "⚠️"
            color = "orange"
        elif level == "error":
            icon = "❌"
            color = "red"
        elif agent == "tool":
            icon = "🔧"
            color = "blue"
        else:
            icon = "ℹ️"
            color = "gray"

        # Format message
        formatted = f"`{timestamp}` {icon} {message}"

        # Display with appropriate styling
        if level == "error":
            st.error(formatted, icon=icon)
        elif level == "warning":
            st.warning(formatted, icon=icon)
        elif level == "success":
            st.success(formatted, icon=icon)
        else:
            st.markdown(formatted)
