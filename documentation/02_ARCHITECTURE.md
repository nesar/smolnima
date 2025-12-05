# smolnima Architecture

## High-Level Design

smolnima follows a **single source of truth** pattern where physics tools are defined once and exposed through four independent interfaces.

```
┌─────────────────────────────────────────────────────────────┐
│                 Four Independent Interfaces                  │
│   CLI  |  Streamlit GUI  |  Python API  |  MCP Server      │
└────┬─────────┬──────────────┬──────────────┬────────────────┘
     │         │              │              │
     │         │              │              │ MCP Protocol
     └─────────┴──────────────┴──────────────┼────────────────┐
                                             │                │
┌────────────────────────────────────────────▼────────────────┤
│                     agent/tools/                             │
│               SINGLE SOURCE OF TRUTH                         │
│  • particle_physics.py - Calculations & particle properties │
│  • gan_physics.py - Event generation & visualization        │
│  • rag_tool.py - Document search & RAG                      │
└──────────────────────────────────────────────────────────────┘
```

### Complete System Architecture

![smolnima Overview](smolnima_overview.png)

The detailed architecture diagram shows all components, tools, and interfaces.

## Component Architecture

### 1. Tool Layer (agent/tools/) - Single Source of Truth

**Purpose**: Define all physics tools once, export everywhere

**Modules**:
- **particle_physics.py**: Core physics calculations
  - Relativistic energy, Lorentz factor
  - Particle properties database
  - Decay probabilities, binding energy

- **gan_physics.py**: Event generation and visualization
  - Quark distribution models (u, d quarks)
  - Cross-section calculations (σ1 = 4u + d, σ2 = 4d + u)
  - Event generation from PDFs
  - Matplotlib visualizations

- **rag_tool.py**: RAG document search
  - PDF loading and parsing
  - Keyword-based search
  - Document retrieval

**Tool Definition Pattern**:
\`\`\`python
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
\`\`\`

**Key Feature**: @tool decorator makes function:
- Discoverable by MCP server
- Usable by agent (CLI/GUI/API)
- Accessible programmatically

### 2. Agent Layer (agent/agents/)

**Purpose**: Orchestrate tools for complex multi-step tasks

**Components**:
- **nima_agent.py**: Creates CodeAgent with physics tools
- **streamlit_agent.py**: Wrapper for Streamlit GUI integration

**Agent Configuration**:
\`\`\`python
agent = CodeAgent(
    tools=[...],  # All physics tools
    model=GeminiModel(...),
    max_steps=10,
    additional_authorized_imports=["numpy", "matplotlib", "scipy", "pandas"]
)
\`\`\`

**Key Feature**: Agent executes Python code dynamically to solve physics problems

### 3. Interface Implementations

#### A. Command Line Interface (cli.py)

**Purpose**: Quick queries, automation, scripts

**Implementation**:
\`\`\`python
from agent import create_nima_agent, Config

config = Config.from_env()
agent = create_nima_agent(config)

# Interactive mode
while True:
    user_input = input("You: ")
    result = agent.run(user_input)
    print(result)
\`\`\`

**Features**:
- Interactive mode: python -m smolnima.cli
- Single query: python -m smolnima.cli -q "query"
- Environment variable configuration
- Built-in help and examples

#### B. Streamlit Web GUI (gui/app.py)

**Purpose**: Interactive exploration, visualization

**Implementation**:
\`\`\`python
from gui.streamlit_agent import create_streamlit_agent

agent = create_streamlit_agent(config)
result = agent.run(user_query)

# Streamlit captures matplotlib figures automatically
for fig_num in plt.get_fignums():
    st.pyplot(plt.figure(fig_num))
\`\`\`

**Features**:
- Real-time plot visualization
- Code execution display (see all Python code run by agent)
- Agent activity monitoring (step-by-step progress)
- Configuration sidebar
- Example queries
- Chat history

**Streamlit-Specific Enhancements** (gui/streamlit_agent.py):
- StreamlitCodeAgent: Extends CodeAgent with logging
- Captures executed code blocks
- Cleans ANSI codes from verbose output
- Automatically stores plots in session state

#### C. Python API

**Purpose**: Programmatic access, Jupyter notebooks, integration

**Implementation**:
\`\`\`python
from smolnima import create_nima_agent, Config

config = Config(
    api_key="...",
    model_name="gemini-2.5-flash",
    pdfs_dir="./pdfs"
)
agent = create_nima_agent(config)
result = agent.run("Calculate Lorentz factor for v=0.9c")
\`\`\`

**Features**:
- Direct tool access: from agent.tools import calculate_relativistic_energy
- Agent creation via factory function
- Configuration via Config dataclass
- Environment variable loading

#### D. MCP Server (mcp/mcp_server.py)

**Purpose**: AI assistant integration (Claude Desktop, custom agents)

**Implementation**:
\`\`\`python
def discover_tools() -> dict[str, callable]:
    """
    Walks through tools/ package (which re-exports agent.tools)
    Finds all @tool decorated functions
    Returns dict mapping tool names to callables
    """
\`\`\`

**Features**:
- Auto-discovery of tools
- JSON Schema generation
- STDIO and SSE transport modes
- MCP protocol compliance

See [04_CLIENT.md](04_CLIENT.md) for MCP client integration details.

See [03_TOOLS.md](03_TOOLS.md) for complete tool reference.
See [04_CLIENT.md](04_CLIENT.md) for MCP client integration.
