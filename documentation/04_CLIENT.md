# MCP-NIMA Client Integration

## Overview

MCP-NIMA tools can be accessed through multiple interfaces:
1. **MCP Clients** (Claude Desktop, custom agents)
2. **Command Line** (CLI)
3. **Web GUI** (Streamlit)
4. **Python API** (programmatic access)

This guide focuses on MCP client integration. For other interfaces, see the main [README.md](../../README.md).

---

## MCP Client Setup

### Claude Desktop Integration

**1. Install Claude Desktop**

Download from: https://claude.ai/download

**2. Configure MCP Server**

Edit Claude Desktop config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**3. Add MCP-NIMA Server**

```json
{
  "mcpServers": {
    "nima": {
      "command": "/Users/your-username/path/to/smolnima/mcp/run_mcp_server.sh",
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

**Important**: Use absolute path to `run_mcp_server.sh`

**4. Restart Claude Desktop**

Tools will appear in the MCP tools section.

---

### Custom MCP Client Integration

**STDIO Mode** (recommended):

```python
import subprocess
import json

# Start MCP server
process = subprocess.Popen(
    ["/path/to/smolnima/mcp/run_mcp_server.sh"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Send list_tools request
request = {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
}
process.stdin.write(json.dumps(request) + "\n")
process.stdin.flush()

# Read response
response = process.stdout.readline()
tools = json.loads(response)
```

**SSE Mode** (HTTP):

```python
import requests

# Start server with: MCP_TRANSPORT=sse ./run_mcp_server.sh

# List tools
response = requests.get("http://localhost:8000/tools")
tools = response.json()

# Call tool
response = requests.post(
    "http://localhost:8000/tools/call",
    json={
        "name": "calculate_lorentz_factor",
        "arguments": {"velocity_fraction": 0.9}
    }
)
result = response.json()
```

---

## Example MCP Requests

### List Available Tools

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 1
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    {
      "name": "calculate_relativistic_energy",
      "description": "Calculate relativistic energy using E = sqrt((mc²)² + (pc)²)...",
      "inputSchema": {
        "type": "object",
        "properties": {
          "mass_MeV": {"type": "number"},
          "momentum_MeV": {"type": "number"}
        },
        "required": ["mass_MeV", "momentum_MeV"]
      }
    },
    ...
  ]
}
```

### Call a Tool

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "calculate_lorentz_factor",
    "arguments": {
      "velocity_fraction": 0.9
    }
  },
  "id": 2
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": [
    {
      "type": "text",
      "text": "2.294157338705618"
    }
  ]
}
```

---

## Usage Examples

### Example 1: Particle Properties

**User Query** (in Claude Desktop):
```
What are the properties of a muon?
```

**Claude's Tool Use**:
```json
{
  "name": "get_particle_properties",
  "arguments": {
    "particle_name": "muon"
  }
}
```

**Response**:
```json
{
  "mass_MeV": 105.6583755,
  "charge": -1,
  "lifetime_s": 2.1969811e-06,
  "spin": 0.5
}
```

**Claude's Answer**:
> A muon has the following properties:
> - Mass: 105.66 MeV/c²
> - Electric charge: -1 (same as electron)
> - Mean lifetime: 2.197 microseconds
> - Spin: 1/2 (fermion)
>
> The muon is about 207 times heavier than an electron and is unstable, decaying primarily into an electron, electron antineutrino, and muon neutrino.

---

### Example 2: Multi-Tool Calculation

**User Query**:
```
A proton is moving at 80% the speed of light. Calculate its Lorentz factor and total energy.
```

**Claude's Tool Uses**:

1. Get proton mass:
```json
{
  "name": "get_particle_properties",
  "arguments": {"particle_name": "proton"}
}
```
Result: `{"mass_MeV": 938.272088, ...}`

2. Calculate Lorentz factor:
```json
{
  "name": "calculate_lorentz_factor",
  "arguments": {"velocity_fraction": 0.8}
}
```
Result: `1.6666666666666667`

3. Calculate relativistic energy:
```json
{
  "name": "calculate_relativistic_energy",
  "arguments": {
    "mass_MeV": 938.272088,
    "momentum_MeV": 1251.029451  // calculated from γmv
  }
}
```
Result: `1563.7868133...`

**Claude's Answer**:
> For a proton moving at 0.8c:
> - Lorentz factor (γ) = 1.667
> - Total energy = 1564 MeV
> - Rest mass energy = 938 MeV
> - Kinetic energy = 626 MeV

---

### Example 3: Event Generation

**User Query**:
```
Generate 10,000 particle physics events and show me the quark distribution statistics.
```

**Claude's Tool Use**:
```json
{
  "name": "generate_physics_events",
  "arguments": {
    "num_events": 10000,
    "seed": 42
  }
}
```

**Response**:
```
Generated 10000 physics events:

Sigma1 (4u + d) distribution:
  Mean: 0.342
  Std: 0.189

Sigma2 (4d + u) distribution:
  Mean: 0.298
  Std: 0.172

Truth parameters used: [-0.4, 2.4, 0.5, -0.06, 0.4, 0.48]
```

**Claude's Answer**:
> I've generated 10,000 events from quark distribution models:
>
> **Cross-section σ1 = 4u + d**:
> - Mean: 0.342
> - Standard deviation: 0.189
>
> **Cross-section σ2 = 4d + u**:
> - Mean: 0.298
> - Standard deviation: 0.172
>
> The u-quark contribution dominates, consistent with proton structure.

---

### Example 4: RAG Literature Search

**Setup**: Place physics PDFs in `./pdfs/` before starting agent

**User Query**:
```
What are Generalized Parton Distributions (GPDs)?
```

**Claude's Tool Use**:
```json
{
  "name": "search_knowledge_base",
  "arguments": {
    "query": "Generalized Parton Distributions GPDs",
    "max_chars": 5000
  }
}
```

**Response**:
```
Found 15 relevant sections:

[From gpd_review.pdf]
Generalized Parton Distributions (GPDs) are functions that describe the correlations between the longitudinal momentum and the transverse spatial distribution of partons in a hadron. They provide access to the orbital angular momentum of quarks and gluons...

[From dv
cs_physics.pdf]
In deeply virtual Compton scattering (DVCS), GPDs can be accessed through measurements of the cross section and asymmetries. The GPDs H, E, H̃, and Ẽ are related to quark helicity and flavor...
```

**Claude's Answer**:
> Based on the physics literature:
>
> **Generalized Parton Distributions (GPDs)** are quantum mechanical probability amplitudes that describe both the momentum and spatial distribution of quarks and gluons inside hadrons like protons and neutrons.
>
> Key features:
> - Combine information from form factors and parton distribution functions
> - Provide 3D imaging of hadron structure
> - Give access to orbital angular momentum of partons
> - Four GPDs: H, E, H̃, Ẽ (different quark helicity/orbital configurations)
> - Accessible experimentally through Deeply Virtual Compton Scattering (DVCS)

---

## Tool Chaining

MCP clients can chain multiple tools for complex analyses:

**User Query**:
```
Compare the decay rates of a muon and a pion+ at 1 microsecond.
```

**Tool Chain**:
1. `get_particle_properties("muon")` → lifetime = 2.197 μs
2. `calculate_decay_probability(2.197e-6, 1.0e-6)` → 0.371
3. `get_particle_properties("pion+")` → lifetime = 26.0 ns
4. `calculate_decay_probability(2.603e-8, 1.0e-6)` → 0.99996
5. Format comparison

**Result**:
- Muon: 37.1% decayed
- Pion+: 99.996% decayed (almost all gone)

---

## Error Handling

MCP-NIMA tools return clear error messages:

**Invalid Input**:
```json
{
  "name": "calculate_lorentz_factor",
  "arguments": {"velocity_fraction": 1.5}
}
```

**Response**:
```json
{
  "type": "text",
  "text": "Error: Velocity must be less than speed of light"
}
```

**Unknown Particle**:
```json
{
  "name": "get_particle_properties",
  "arguments": {"particle_name": "graviton"}
}
```

**Response**:
```json
{
  "type": "text",
  "text": "Error: Particle 'graviton' not found. Available: electron, proton, muon, neutron, pion0, pion+"
}
```

---

## Performance Considerations

### Latency

| Operation | Typical Latency |
|-----------|----------------|
| Tool list | < 10 ms |
| Simple calculation | < 50 ms |
| Event generation (10k) | ~200 ms |
| Visualization | ~300 ms |
| RAG search | ~100 ms |
| MCP protocol overhead | ~10 ms |

### Concurrency

MCP server runs in STDIO mode (single process):
- **Concurrent requests**: Queued and executed sequentially
- **Recommended**: One query at a time per client
- **Scalability**: Start multiple server instances for parallel clients

### Memory

| Component | Memory Usage |
|-----------|--------------|
| Base server | ~50 MB |
| PDF documents | ~10 MB per document |
| Event generation | ~100 MB for 100k events |
| Visualization | ~50 MB per plot |

---

## Troubleshooting

### Server Not Starting

**Symptom**: No response from MCP server

**Check**:
1. Path to `run_mcp_server.sh` is correct
2. Script is executable: `chmod +x run_mcp_server.sh`
3. Python dependencies installed: `pip install -e .`
4. Check stderr for errors

### Tools Not Found

**Symptom**: Empty tool list

**Solution**:
```bash
cd /path/to/smolnima/mcp
python3 -c "
import sys
sys.path.insert(0, '..')
from tools import *
print('Tools imported successfully')
"
```

### Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'smolagents'`

**Solution**:
```bash
pip install smolagents numpy matplotlib scipy pandas PyPDF2
```

### API Key Issues

**Note**: MCP server does NOT require API key (tools are computational, not LLM-based). The agent/GUI require API keys for conversational interface, but MCP tools work standalone.

---

## Advanced Configuration

### Custom Environment

```json
{
  "mcpServers": {
    "nima": {
      "command": "/path/to/smolnima/mcp/run_mcp_server.sh",
      "env": {
        "MCP_TRANSPORT": "stdio",
        "PYTHONPATH": "/custom/path",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### SSE Mode for Web Clients

```bash
export MCP_TRANSPORT=sse
export MCP_HOST=0.0.0.0
export MCP_PORT=8000
cd /path/to/smolnima/mcp
./run_mcp_server.sh
```

Access at: `http://localhost:8000/sse`

---

## Best Practices

1. **Tool Selection**: Use simplest tool for the task (avoid complex tools for simple calculations)
2. **Error Handling**: Check for error messages in responses
3. **Chaining**: Break complex queries into multiple tool calls
4. **Caching**: MCP clients should cache tool schemas (call `list_tools` once)
5. **Validation**: Validate inputs on client side before sending to server
6. **Documentation**: Use tool descriptions to guide LLM tool selection

---

## Security

MCP-NIMA follows MCP security best practices:

- **Subprocess Isolation**: Runs in separate process
- **No Network Access**: STDIO communication only (default)
- **Read-Only Operations**: Most tools are pure functions
- **File Access**: Limited to configured `input/` and `out/` directories
- **No Code Execution**: Tools are pre-defined, no dynamic code eval (except in agent mode)

---

## Support

For issues with MCP integration:
- MCP Specification: https://modelcontextprotocol.io/
- Claude Desktop: https://claude.ai/download
- MCP-NIMA Issues: Create GitHub issue with client logs
