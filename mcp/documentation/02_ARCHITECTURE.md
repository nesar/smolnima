# MCP-NIMA Architecture

## High-Level Design

MCP-NIMA follows a **single source of truth** pattern where physics tools are defined once and exposed through multiple interfaces.

```
┌─────────────────────────────────────────────────────────────┐
│                    Multiple Interfaces                       │
│  CLI | Streamlit GUI | Python API | MCP Server              │
└────────────┬───────────────┬──────────────┬─────────────────┘
             │               │              │
             │               │              │ MCP Protocol
             └───────────────┴──────────────┼─────────────────┐
                                            │                 │
┌───────────────────────────────────────────▼─────────────────┤
│                     agent/tools/                             │
│               SINGLE SOURCE OF TRUTH                         │
│  • particle_physics.py - Calculations & particle properties │
│  • gan_physics.py - Event generation & visualization        │
│  • rag_tool.py - Document search & RAG                      │
└──────────────────────────────────────────────────────────────┘
```

### Complete System Architecture

![MCP-NIMA Overview](mcp_nima_overview.png)

The detailed architecture diagram shows all components, tools, and interfaces.

## Component Architecture

### 1. Tool Layer (`agent/tools/`) - Single Source of Truth

**Purpose**: Define all physics tools once, export everywhere

**Modules**:
- **`particle_physics.py`**: Core physics calculations
  - Relativistic energy, Lorentz factor
  - Particle properties database
  - Decay probabilities, binding energy

- **`gan_physics.py`**: Event generation and visualization
  - Quark distribution models (u, d quarks)
  - Cross-section calculations (σ1 = 4u + d, σ2 = 4d + u)
  - Event generation from PDFs
  - Matplotlib visualizations

- **`rag_tool.py`**: RAG document search
  - PDF loading and parsing
  - Keyword-based search
  - Document retrieval

**Tool Definition Pattern**:
```python
from smolagents import tool

@tool
def calculate_relativistic_energy(mass_MeV: float, momentum_MeV: float) -> float:
    """
    Calculate relativistic energy using E = sqrt((mc²)² + (pc)²).

    Args:
        mass_MeV: Particle rest mass in MeV/c²
        momentum_MeV: Particle momentum in MeV/c

    Returns:
        Energy in MeV
    """
    return float(np.sqrt(mass_MeV**2 + momentum_MeV**2))
```

**Key Feature**: `@tool` decorator makes function:
- Discoverable by MCP server
- Usable by agent
- Accessible via API

### 2. Agent Layer (`agent/agents/`)

**Purpose**: Orchestrate tools for complex multi-step tasks

**Components**:
- **`nima_agent.py`**: Creates `CodeAgent` with physics tools
- **`streamlit_agent.py`**: Wrapper for Streamlit GUI integration

**Agent Configuration**:
```python
agent = CodeAgent(
    tools=[...],  # All physics tools
    model=GeminiModel(...),
    max_steps=10,
    additional_authorized_imports=["numpy", "matplotlib", "scipy", "pandas"]
)
```

**Key Feature**: Agent executes Python code dynamically to solve physics problems

### 3. MCP Server (`mcp/mcp_server.py`)

**Purpose**: Bridge between MCP protocol and physics tools

**Key Mechanisms**:

**Tool Discovery**:
```python
def discover_tools() -> dict[str, callable]:
    """
    Walks through tools/ package (which re-exports agent.tools)
    Finds all @tool decorated functions
    Returns dict mapping tool names to callables
    """
```

Discovery process:
1. Uses `pkgutil.walk_packages()` to traverse `tools/` package
2. Uses `inspect.getmembers()` to find decorated functions
3. Checks for `__wrapped__` or `name` attributes (smolagents pattern)
4. Builds tool registry automatically

**MCP Tool Schema Builder**:
```python
def build_mcp_tool(name: str, func: callable) -> Tool:
    """
    Converts Python function to MCP Tool with JSON schema
    Extracts: docstring, parameters, type annotations
    Generates: MCP-compliant tool description
    """
```

**MCP Endpoints**:
- `@app.list_tools()`: Returns all discovered tools with schemas
- `@app.call_tool()`: Executes tool and returns result as TextContent

**Communication Modes**:
- **STDIO** (default): stdin/stdout pipes managed by MCP client
- **SSE**: HTTP server for web-based clients

### 4. Re-export Layers

**Purpose**: Avoid code duplication while maintaining clean imports

**Root-level `tools/__init__.py`**:
```python
# Re-exports from agent.tools for backward compatibility
import importlib

_particle_physics = importlib.import_module('agent.tools.particle_physics')
calculate_relativistic_energy = _particle_physics.calculate_relativistic_energy
# ... other tools
```

**MCP `tools/__init__.py`**:
```python
# Re-exports from agent.tools for MCP server
from agent.tools.particle_physics import (
    calculate_relativistic_energy,
    # ... other tools
)
```

**Key Feature**: Uses `importlib` to avoid triggering full package initialization

### 5. Conditional Imports (`agent/__init__.py`)

**Purpose**: Allow tool imports without full agent dependencies

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
    from .prompts import PHYSICS_SYSTEM_PROMPT
    _AGENT_AVAILABLE = True
except ImportError:
    _AGENT_AVAILABLE = False
    # Gracefully degrade
```

**Benefit**: MCP server can import tools without requiring smolagents

### 6. Interface Layers

#### CLI (`cli.py`)
```python
from agent import create_nima_agent, Config

config = Config.from_env()
agent = create_nima_agent(config)
result = agent.run(user_input)
```

#### GUI (`gui/app.py`)
```python
from gui.streamlit_agent import create_streamlit_agent

agent = create_streamlit_agent(config)
result = agent.run(user_query)
# Streamlit captures matplotlib figures automatically
```

#### Python API
```python
from smolnima import create_nima_agent, Config

config = Config(api_key="...", model_name="gemini-2.5-flash")
agent = create_nima_agent(config)
result = agent.run("Calculate Lorentz factor for v=0.9c")
```

#### MCP Server
```bash
cd mcp
./run_mcp_server.sh
# Tools automatically discovered and exposed via MCP
```

## Data Flow

### Single Tool Call (MCP Client → Physics Tool)

```
1. MCP Client sends tool call request
2. mcp_server.py receives via stdio
3. Tool discovered in tools/ (re-export from agent.tools)
4. Tool executed with arguments
5. Result returned as TextContent
6. Response sent back to client via stdio
```

### Agent Execution (GUI/CLI → Multi-step Task)

```
1. User submits query via GUI/CLI
2. Agent analyzes task, plans steps
3. Agent generates Python code using tools
4. Code executed in sandbox
5. Tools called dynamically
6. Results formatted and returned
7. (GUI only) Matplotlib figures captured automatically
```

## Directory Structure

```
smolnima/
├── agent/                    # Agent components
│   ├── __init__.py          # Conditional imports
│   ├── agents/              # Agent implementations
│   │   ├── nima_agent.py
│   │   └── streamlit_agent.py
│   ├── models/              # Model wrappers
│   │   └── gemini.py
│   ├── prompts/             # System prompts
│   │   └── nima_prompts.py
│   └── tools/               # ← SINGLE SOURCE OF TRUTH
│       ├── __init__.py
│       ├── particle_physics.py
│       ├── gan_physics.py
│       └── rag_tool.py
│
├── tools/__init__.py         # Re-exports for backward compat
│
├── gui/                      # Streamlit interface
│   ├── app.py
│   └── streamlit_agent.py
│
├── cli.py                    # Command-line interface
├── config.py                 # Configuration management
│
└── mcp/                      # MCP Server
    ├── mcp_server.py        # Auto-discovery & execution
    ├── tools/__init__.py    # Re-exports from agent.tools
    ├── agent_tools/         # Placeholder for future
    │   └── __init__.py
    ├── mcp_utils/           # Path utilities
    │   ├── __init__.py
    │   └── path_utils.py
    ├── pyproject.toml       # Package configuration
    ├── run_mcp_server.sh    # Launcher script
    ├── README.md            # MCP server docs
    └── documentation/       # Architecture docs
        ├── 01_RATIONALE.md
        ├── 02_ARCHITECTURE.md
        └── flowchart.py
```

## Testing Strategy

### Unit Tests

**Tools**: Test individual physics tools
```python
def test_calculate_relativistic_energy():
    # Test with known values (electron at 100 MeV/c momentum)
    mass = 0.511  # MeV
    momentum = 100.0  # MeV
    energy = calculate_relativistic_energy(mass, momentum)
    assert abs(energy - 100.0013) < 0.001
```

### Integration Tests

**Agent**: Test full agent workflow
```python
@pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="API key required")
def test_agent_physics_query():
    config = Config.from_env()
    agent = create_nima_agent(config)
    result = agent.run("What is the mass of a muon?")
    assert "105" in result.lower()  # muon mass ~105 MeV
```

### Running Tests

```bash
# Unit tests (fast, no API key)
pytest tests/test_tools.py

# Integration tests (requires GOOGLE_API_KEY)
export GOOGLE_API_KEY="your-key"
pytest tests/ -v
```

## Configuration

### Environment Variables

```bash
export GOOGLE_API_KEY="your-gemini-api-key"
export GEMINI_MODEL="gemini-2.5-flash"
export PDFS_DIR="./pdfs"
export MAX_STEPS="10"
export TEMPERATURE="0.3"
```

### Python Configuration

```python
from smolnima import Config

config = Config(
    api_key="your-key",
    model_name="gemini-2.5-flash",
    pdfs_dir="./pdfs",
    max_steps=10,
    temperature=0.3,
    verbose=True
)
```

## Key Design Features

1. **Zero Duplication**: Tools defined once in `agent/tools/`
2. **Auto-Discovery**: MCP server finds tools automatically via `@tool` decorator
3. **Multi-Interface**: Same tools via CLI, GUI, API, and MCP
4. **Conditional Imports**: Graceful degradation when dependencies missing
5. **Professional Code**: Minimal, crisp, no placeholders
6. **Clean Separation**: Agent, GUI, and MCP server cleanly separated

See **[03_TOOLS.md](03_TOOLS.md)** for complete tool reference.
