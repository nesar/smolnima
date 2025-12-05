# MCP-NIMA: Design Rationale

## Overview

**MCP-NIMA** is an MCP server that exposes particle and nuclear physics analysis tools through the Model Context Protocol. It implements a **single source of truth** pattern where tools defined once in `agent/tools/` are automatically available via CLI, GUI, Python API, and MCP.

![Abstract Architecture](abstract_architecture.png)

The abstract architecture diagram shows the high-level tool server pattern that MCP-NIMA implements.

## Motivation

### The Problem

Particle and nuclear physics research requires:
1. **Complex calculations** (relativistic kinematics, decay rates, binding energies)
2. **Event generation** (GAN-based particle physics simulation)
3. **Literature search** (RAG over physics papers)
4. **Multiple interfaces** (CLI, GUI, programmatic access)

Traditional approaches result in:
- Code duplication across interfaces
- Manual tool registration and maintenance
- Inconsistent functionality between interfaces
- Difficult integration with AI assistants

### The Solution

MCP-NIMA provides:
- **9 specialized physics tools** via MCP protocol
- **Single source of truth**: Tools defined once in `agent/tools/`
- **Automatic exposure** via CLI, Web GUI, Python API, and MCP server
- **Zero duplication**: No manual registration or code copying
- **AI-powered analysis**: Any MCP client can perform physics calculations

## Design Rationale

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

### Why Smolagents?

**smolagents** is Hugging Face's lightweight agent framework:
- Simple `@tool` decorator
- Built-in `CodeAgent` for multi-step reasoning
- Gemini API integration
- LLM-agnostic (works with any OpenAI-compatible API)

**Key benefit**: Tools defined with `@tool` are automatically:
- Discoverable by MCP server
- Executable by CLI/GUI agent
- Usable via Python API

### Why Single Source of Truth?

**Problem**: Previous implementations duplicated tool definitions:
- Agent tools in `agent/tools/`
- Duplicate MCP tools in `mcp/tools/`
- Manual synchronization required

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

### Why Conditional Imports?

**Problem**: MCP server needs tools, but not full agent framework (smolagents dependency)

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

## Core Design Principles

1. **Single Source of Truth**: Tools defined once in `agent/tools/`, never duplicated
2. **Auto-Discovery**: MCP server automatically discovers tools via `@tool` decorator
3. **Multi-Interface**: Same tools accessible via CLI, GUI, API, and MCP
4. **Separation of Concerns**: MCP server, agent, and GUI cleanly separated
5. **Minimal Code**: Professional, crisp implementation following smolagents best practices
6. **No Placeholders**: All tools are real, functional physics calculations

## Architecture Comparison

| Aspect | Original NIMA | smolnima |
|--------|---------------|----------|
| **Framework** | Custom Streamlit | smolagents |
| **Interfaces** | Web UI only | CLI + Web UI + API + MCP |
| **Code** | ~2000+ lines | ~800 lines |
| **Tool Duplication** | N/A | Zero (single source) |
| **MCP Support** | ❌ No | ✅ Yes |
| **Complexity** | High | Minimal |

## References

- **MCP Specification**: https://modelcontextprotocol.io/
- **Smolagents**: https://github.com/huggingface/smolagents
- **Gemini API**: https://ai.google.dev/
