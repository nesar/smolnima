# MCP-NIMA: Model Context Protocol Server

MCP server that exposes Dr. NIMA's particle and nuclear physics tools via the Model Context Protocol.

## Overview

This MCP server provides AI assistants with access to:

- **Particle Physics Tools**: Relativistic calculations, particle properties, decay probabilities, binding energy
- **Event Generation**: GAN-based particle physics event simulation
- **RAG Tools**: Search physics literature from PDF documents
- **Visualization**: Quark distributions and cross-sections

## Installation

```bash
cd mcp
pip install -e .
```

Or install dependencies directly:

```bash
pip install mcp smolagents numpy matplotlib scipy pandas PyPDF2 starlette uvicorn
```

## Quick Start

### STDIO Mode (Default)

For direct integration with MCP clients:

```bash
./run_mcp_server.sh
```

Or:

```bash
python mcp_server.py
```

### SSE Mode (HTTP)

For HTTP-based access:

```bash
export MCP_TRANSPORT=sse
export MCP_HOST=0.0.0.0
export MCP_PORT=8000
./run_mcp_server.sh
```

The server will be available at:
- SSE endpoint: `http://localhost:8000/sse`
- Messages endpoint: `http://localhost:8000/messages`

## Available Tools

The server auto-discovers all `@tool` decorated functions from:

1. **../agent/tools/** - Domain-specific physics tools (shared with agent/GUI/CLI)
2. **agent_tools/** - Agent helper tools (placeholder for future expansion)

Note: Tools are defined once in `agent/tools/` and automatically exposed via MCP. No duplication!

### Particle Physics Tools

- `calculate_relativistic_energy(mass_MeV, momentum_MeV)` - Calculate E = √((mc²)² + (pc)²)
- `calculate_lorentz_factor(velocity_fraction)` - Calculate γ = 1/√(1 - v²/c²)
- `get_particle_properties(particle_name)` - Get mass, charge, lifetime, spin
- `calculate_decay_probability(lifetime_s, time_s)` - Calculate P(t) = 1 - exp(-t/τ)
- `calculate_binding_energy(isotope_mass_u, num_protons, num_neutrons)` - Nuclear binding energy

### Event Generation Tools

- `generate_physics_events(num_events, truth_params, seed)` - Generate particle events
- `visualize_quark_distributions(truth_params, save_filename)` - Visualize quark PDFs

### RAG Tools

- `search_knowledge_base(query, max_chars)` - Search loaded PDF documents

## Directory Structure

```
mcp/
├── mcp_server.py           # Main MCP server with auto-discovery
├── pyproject.toml          # Package configuration
├── run_mcp_server.sh       # Server launcher script
├── README.md               # This file
├── agent_tools/            # Agent helper tools (placeholder)
│   └── __init__.py
├── mcp_utils/              # Shared utilities
│   ├── __init__.py
│   └── path_utils.py
├── input/                  # Input data directory
└── out/                    # Output directory

Note: Physics tools are imported from ../agent/tools/ to avoid duplication
```

## Configuration

### Environment Variables

- `MCP_TRANSPORT`: Transport mode (`stdio` or `sse`), default: `stdio`
- `MCP_HOST`: Host for SSE mode, default: `0.0.0.0`
- `MCP_PORT`: Port for SSE mode, default: `8000`

### Input/Output Directories

Create `input/` and `out/` directories in your working directory:

```bash
mkdir -p input out
```

- Place PDF documents in `input/` for RAG search
- Visualizations and generated data will be saved to `out/`

## Using with MCP Clients

### Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "nima": {
      "command": "/path/to/smolnima/mcp/run_mcp_server.sh",
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

### Other MCP Clients

Connect to the server using the MCP protocol:

- **STDIO**: Run `python mcp_server.py` and communicate via stdin/stdout
- **SSE**: Connect to `http://localhost:8000/sse` for server-sent events

## Adding Custom Tools

Tools should be added to `../agent/tools/` (not in the mcp directory):

1. Create your tool file in `agent/tools/`:

```python
# In agent/tools/my_new_tool.py
from smolagents import tool
import numpy as np

@tool
def my_physics_tool(param: float) -> float:
    """
    My custom physics calculation.

    Args:
        param: Input parameter

    Returns:
        Result of calculation
    """
    return param * 2.0
```

2. Add the import to `agent/tools/__init__.py`:

```python
from .my_new_tool import my_physics_tool

__all__ = [..., "my_physics_tool"]
```

3. The tool is now available in:
   - Agent (CLI/GUI)
   - Python API
   - MCP Server (automatically discovered!)

No need to duplicate code - write once, use everywhere!

## Architecture

The MCP server uses **auto-discovery** to find all tools:

1. Walks through `tools/` and `agent_tools/` packages
2. Finds all functions with `@tool` decorator from smolagents
3. Converts them to MCP Tool format with proper JSON Schema
4. Serves them via MCP protocol

This means **zero configuration** - just add `@tool` decorated functions and they're automatically available!

## Development

### Testing

```bash
cd mcp
pytest
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .
```

## License

Same as parent smolnima project.

## Documentation

Complete project documentation available in `../documentation/`:

- **[01_RATIONALE.md](../documentation/01_RATIONALE.md)** - Design rationale
- **[02_ARCHITECTURE.md](../documentation/02_ARCHITECTURE.md)** - System architecture
- **[03_TOOLS.md](../documentation/03_TOOLS.md)** - Tool reference
- **[04_CLIENT.md](../documentation/04_CLIENT.md)** - MCP client integration (this server)

Generate architecture diagrams:
```bash
cd ../documentation
python3 flowchart.py  # Requires: pip install graphviz
```

## Credits

- Based on the design pattern from hep-ke/mcp
- Part of the Dr. NIMA (smolnima) project
- Uses smolagents framework for tool definitions
- Implements Model Context Protocol (MCP) specification
