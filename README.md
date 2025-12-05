# smolnima

**Nuclear Imaging with Multi-Agents** - A minimal, crisp implementation using smolagents.

## Overview

smolnima is a prototype agentic system written for nuclear and particle physics applications. It is written with smolagent backend and a GUI with streamlit. It provides an AI-powered assistant for particle and nuclear physics research with:

- **Physics Tools**: Relativistic calculations, particle properties, decay rates, binding energy
- **Event Generation**: GAN-based particle physics event simulation
- **RAG System**: Search physics literature from PDF documents
- **Code Execution**: Dynamic Python code generation and execution for calculations
- **Visualizations**: Quark distributions, cross-sections, and physics plots

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install from the package
pip install -e .
```

## Quick Start

### Set up API Key

```bash
export GOOGLE_API_KEY="your-gemini-api-key"
```

### Streamlit Web Interface (Recommended)

```bash
cd smolnima
./run_clean.sh
# Opens at http://localhost:8501 (or next available port)
```

The Streamlit interface includes:
- 📝 **Code Execution Display**: See all Python code executed by the agent
- 📊 **Interactive Plots**: Visualizations appear directly in the GUI
- 🔍 **Agent Activity Panel**: Real-time step-by-step progress monitoring
- 📚 **Example Queries**: One-click example questions

### Interactive CLI Mode

```bash
python -m smolnima.cli
```

### Single Query

```bash
python -m smolnima.cli -q "What is the mass of a proton?"
```

### MCP Server (Model Context Protocol)

Run as an MCP server to expose tools to AI assistants:

```bash
cd mcp
./run_mcp_server.sh
```

For HTTP mode (SSE):

```bash
cd mcp
export MCP_TRANSPORT=sse
export MCP_PORT=8000
./run_mcp_server.sh
```

See [mcp/README.md](mcp/README.md) for detailed MCP server documentation.

### Python API

```python
from smolnima import create_nima_agent, Config

# Create config
config = Config.from_env()

# Create agent
agent = create_nima_agent(config)

# Run query
result = agent.run("Calculate the Lorentz factor for v=0.9c")
print(result)
```

## Example Queries

1. **Particle Properties**
   ```
   What are the properties of a muon?
   ```

2. **Relativistic Calculations**
   ```
   Calculate the relativistic energy of an electron with momentum 100 MeV/c
   ```

3. **Event Generation**
   ```
   Generate 10000 physics events and show me the statistics
   ```

4. **Visualizations**
   ```
   Visualize quark distributions for the default parameters
   ```

5. **Literature Search**
   ```
   Search the knowledge base for information about GPDs
   ```

6. **Complex Queries**
   ```
   How are GPDs, QCFs and CFFs related? Show equations and generate visualization.
   ```

## Architecture

```
smolnima/
├── __init__.py       # Package exports
├── config.py         # Configuration management
├── models.py         # Gemini model wrapper
├── agent.py          # Main agent setup
├── cli.py            # Command-line interface
├── gui/              # Streamlit web interface
│   ├── app.py
│   └── streamlit_agent.py
├── agent/            # Agent components
│   ├── agents/       # Agent implementations
│   ├── models/       # Model wrappers
│   ├── prompts/      # System prompts
│   └── tools/        # Physics tools
│       ├── particle_physics.py
│       ├── gan_physics.py
│       └── rag_tool.py
└── mcp/              # MCP server
    ├── mcp_server.py     # MCP server with auto-discovery
    ├── tools/            # MCP-exposed physics tools
    ├── agent_tools/      # Agent helper tools (placeholder)
    └── mcp_utils/        # Utilities
```

## Key Differences from Original NIMA

| Feature | Original NIMA | smolnima |
|---------|---------------|----------|
| **Framework** | Custom Streamlit | smolagents |
| **Interface** | Web UI | CLI / Web UI / Python API / MCP Server |
| **Agents** | Multi-agent (Manager, RAG, Code) | Single CodeAgent |
| **Code** | ~2000+ lines | ~800 lines |
| **Dependencies** | Streamlit + custom code | smolagents + minimal |
| **Complexity** | High | Minimal |
| **MCP Support** | ❌ No | ✅ Yes |

## Features Comparison

Both implementations support:
- ✅ Physics calculations and particle properties
- ✅ Event generation and visualization
- ✅ RAG with PDF documents
- ✅ Code execution
- ✅ Gemini API integration

smolnima advantages:
- ✨ Much simpler codebase (~60% less code)
- ✨ Proper use of smolagents framework
- ✨ CLI, Web UI, Python API, and MCP Server
- ✨ **Code execution transparency**: See all executed Python code
- ✨ **Inline plot display**: Visualizations appear directly in GUI
- ✨ **Real-time monitoring**: Agent activity tracking
- ✨ **MCP integration**: Expose tools to any MCP-compatible AI assistant
- ✨ Better separation of concerns
- ✨ Easier to extend and maintain

## Configuration

Configure via environment variables or Config object:

```bash
export GOOGLE_API_KEY="your-key"
export GEMINI_MODEL="gemini-2.5-flash"
export PDFS_DIR="./pdfs"
export MAX_STEPS="10"
export TEMPERATURE="0.3"
```

Or in Python:

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

## Adding Custom Tools

```python
from smolagents import tool
from smolnima import create_nima_agent

@tool
def my_custom_tool(param: str) -> str:
    """My custom physics tool."""
    # Your implementation
    return f"Processed: {param}"

# Add to agent
agent = create_nima_agent(additional_tools=[my_custom_tool])
```

## PDF Documents

Place PDF documents in `./pdfs/` directory. They will be automatically loaded and available for RAG search.

## Development

```bash
# Run tests (when available)
pytest

# Format code
black smolnima/

# Type checking
mypy smolnima/
```

## License

Same as original Dr. NIMA project.

## Credits

- Original NIMA: Multi-agent Streamlit implementation
- smolnima: Minimal smolagents rewrite
- Framework: [smolagents by Hugging Face](https://github.com/huggingface/smolagents)
# Refactored for clean separation of agent and GUI components
