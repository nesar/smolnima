# smolnima: Design Rationale

## Overview

**smolnima** (Nuclear Imaging with Multi-Agents) is a minimal, professional particle and nuclear physics assistant built with smolagents. It provides **four interfaces** to the same underlying physics tools: CLI, Web GUI, Python API, and MCP Server.

The system implements a **single source of truth** pattern where tools defined once in `agent/tools/` are automatically available across all interfaces.

![Abstract Architecture](abstract_architecture.png)

The abstract architecture diagram shows the multi-interface pattern that smolnima implements.

## Motivation

### The Problem

Particle and nuclear physics research requires:
1. **Complex calculations** (relativistic kinematics, decay rates, binding energies)
2. **Event generation** (GAN-based particle physics simulation)
3. **Literature search** (RAG over physics papers)
4. **Multiple interfaces** (CLI for scripts, GUI for interactive work, API for integration, MCP for AI assistants)

Traditional approaches result in:
- Code duplication across interfaces
- Manual tool registration and maintenance
- Inconsistent functionality between interfaces
- Difficult integration with AI assistants
- Heavy, complex codebases

### The Solution

smolnima provides:
- **9 specialized physics tools** exposed uniformly
- **4 interfaces**: CLI, Streamlit GUI, Python API, MCP Server
- **Single source of truth**: Tools defined once in `agent/tools/`
- **Automatic exposure**: Add tool once, available everywhere
- **Zero duplication**: No manual registration or code copying
- **AI-powered analysis**: CodeAgent with Gemini for multi-step reasoning
- **Minimal codebase**: ~800 lines vs ~2000+ in original NIMA

## Design Rationale

### Why Four Interfaces?

Each interface serves a specific use case:

**CLI (Command Line)**:
- Quick queries and automation
- Shell scripts and pipelines
- No GUI overhead
- Fast startup time

**Streamlit GUI**:
- Interactive exploration
- Real-time plot visualization
- Agent activity monitoring
- Code execution transparency

**Python API**:
- Programmatic integration
- Jupyter notebooks
- Batch processing
- Custom workflows

**MCP Server**:
- AI assistant integration (Claude Desktop)
- Standard protocol (JSON-RPC)
- Secure subprocess isolation
- Custom agent systems

### Why Smolagents?

**smolagents** is Hugging Face's lightweight agent framework:
- Simple `@tool` decorator
- Built-in `CodeAgent` for multi-step reasoning
- Gemini API integration
- LLM-agnostic (works with any OpenAI-compatible API)
- Dynamic code generation and execution

**Key benefit**: Tools defined with `@tool` are automatically:
- Discoverable by MCP server
- Executable by CLI/GUI agent
- Usable via Python API
- Consistent across all interfaces

### Why Single Source of Truth?

**Problem**: Previous implementations duplicated tool definitions:
- Agent tools in one location
- Duplicate tools for each interface
- Manual synchronization required
- Inconsistent behavior possible

**Solution**: Tools defined once, exposed everywhere:
```
agent/tools/           ← SINGLE SOURCE OF TRUTH
    ├── particle_physics.py
    ├── gan_physics.py
    └── rag_tool.py

Re-exported automatically to:
    • CLI (via agent imports)
    • GUI (via agent imports)
    • Python API (via agent imports)
    • MCP Server (via auto-discovery)
```

**Benefits**:
- Write once, use everywhere
- No code duplication
- Single point of maintenance
- Consistent behavior across all interfaces
- Add tool in one place → available in all 4 interfaces

### Why Conditional Imports?

**Problem**: Different interfaces have different dependencies:
- CLI/GUI need full agent framework (smolagents)
- MCP server only needs tool definitions (numpy, scipy, etc.)

**Solution**: `agent/__init__.py` uses try/except:
```python
# Tools always importable (lightweight dependencies)
from .tools import (
    calculate_relativistic_energy,
    # ... other tools
)

# Agent components require smolagents - import only if available
try:
    from .agents import create_nima_agent
    from .models import GeminiModel
except ImportError:
    # Gracefully degrade if smolagents not available
    pass
```

**Benefit**: MCP server can import and expose tools without requiring full agent framework

### Why Streamlit for GUI?

**Pros**:
- Rapid development
- Automatic plot capture
- Built-in widgets
- Python-native (no JavaScript)
- Session state management

**Cons**:
- Heavier than pure CLI
- Requires web browser
- Not suitable for batch processing

**Decision**: Use Streamlit for GUI, provide CLI and API for other use cases

### Why MCP?

**Pros**:
- Standard protocol for LLM-tool communication
- Supported by major AI platforms (Anthropic Claude Desktop, etc.)
- Language-agnostic (JSON-RPC over stdio)
- Secure subprocess isolation
- Simple deployment (no servers, ports, or networking)

**Cons**:
- Still evolving standard
- Limited to stdio communication (no streaming large data)
- Requires client support

**Decision**: Provide MCP server as fourth interface option

## Core Design Principles

1. **Single Source of Truth**: Tools defined once in `agent/tools/`, never duplicated
2. **Multi-Interface**: Same tools accessible via CLI, GUI, Python API, and MCP
3. **Auto-Discovery**: MCP server automatically discovers tools via `@tool` decorator
4. **Separation of Concerns**: CLI, GUI, API, and MCP cleanly separated
5. **Minimal Code**: Professional, crisp implementation following smolagents best practices
6. **No Placeholders**: All tools are real, functional physics calculations
7. **Graceful Degradation**: Interfaces work independently with appropriate dependencies

## Architecture Comparison

| Aspect | Original NIMA | smolnima |
|--------|---------------|----------|
| **Framework** | Custom Streamlit | smolagents + minimal wrappers |
| **Interfaces** | Web UI only | CLI + Web UI + Python API + MCP Server |
| **Agent** | Multi-agent (Manager, RAG, Code) | Single CodeAgent |
| **Code** | ~2000+ lines | ~800 lines |
| **Tool Duplication** | N/A | Zero (single source) |
| **MCP Support** | ❌ No | ✅ Yes |
| **Complexity** | High | Minimal |
| **Dependencies** | Streamlit + custom code | smolagents + standard libs |

## Interface Overview

### 1. Command Line (CLI)
- **Use case**: Scripts, automation, quick queries
- **Launch**: `python -m smolnima.cli` or `python -m smolnima.cli -q "query"`
- **Benefits**: Fast, scriptable, no GUI overhead
- **Example**: Batch processing of particle calculations

### 2. Streamlit Web GUI
- **Use case**: Interactive exploration, visualization
- **Launch**: `./run_clean.sh` (opens browser at http://localhost:8501)
- **Benefits**: Real-time plots, code transparency, agent activity monitoring
- **Example**: Exploring quark distributions with live visualization

### 3. Python API
- **Use case**: Integration into existing workflows
- **Import**: `from smolnima import create_nima_agent, Config`
- **Benefits**: Programmatic access, Jupyter notebooks, batch processing
- **Example**: Automated physics calculations in research pipeline

### 4. MCP Server
- **Use case**: AI assistant integration (Claude Desktop, custom agents)
- **Launch**: `cd mcp && ./run_mcp_server.sh`
- **Benefits**: Standard protocol, secure, AI-powered analysis
- **Example**: Ask Claude Desktop to perform particle physics calculations

## References

- **MCP Specification**: https://modelcontextprotocol.io/
- **Smolagents**: https://github.com/huggingface/smolagents
- **Gemini API**: https://ai.google.dev/
- **Streamlit**: https://streamlit.io/
- **Original NIMA**: Multi-agent Streamlit implementation (predecessor)
