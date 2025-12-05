# MCP-NIMA Tool Reference

## Overview

MCP-NIMA provides **9 specialized tools** for particle and nuclear physics analysis. All tools are defined in `agent/tools/` and automatically exposed via MCP, CLI, GUI, and Python API.

## Tool Categories

### 1. Particle Physics Calculations (5 tools)
### 2. Event Generation & Visualization (2 tools)
### 3. RAG Document Search (2 tools)

---

## Particle Physics Tools

Source: `agent/tools/particle_physics.py`

### calculate_relativistic_energy

Calculate relativistic energy using E = √((mc²)² + (pc)²).

**Parameters**:
- `mass_MeV` (float): Particle rest mass in MeV/c²
- `momentum_MeV` (float): Particle momentum in MeV/c

**Returns**: Energy in MeV (float)

**Example**:
```python
# Electron with 100 MeV/c momentum
energy = calculate_relativistic_energy(0.511, 100.0)
# Returns: 100.0013 MeV
```

**Physics**: Uses the relativistic energy-momentum relation. For ultrarelativistic particles (p >> m), E ≈ p.

---

### calculate_lorentz_factor

Calculate Lorentz factor γ = 1/√(1 - v²/c²).

**Parameters**:
- `velocity_fraction` (float): Velocity as fraction of speed of light (v/c), must be < 1

**Returns**: Lorentz factor gamma (float)

**Example**:
```python
gamma = calculate_lorentz_factor(0.9)
# Returns: 2.294 (time dilation factor at 90% light speed)
```

**Physics**: Fundamental to special relativity. γ determines time dilation, length contraction, and relativistic momentum.

---

### get_particle_properties

Get particle properties from the particle database.

**Parameters**:
- `particle_name` (str): Name of particle (e.g., 'electron', 'proton', 'muon', 'neutron', 'pion0', 'pion+')

**Returns**: Dictionary with mass (MeV), charge, lifetime (s), and spin

**Example**:
```python
props = get_particle_properties("muon")
# Returns: {
#     'mass_MeV': 105.66,
#     'charge': -1,
#     'lifetime_s': 2.197e-06,
#     'spin': 0.5
# }
```

**Physics**: Comprehensive particle database with experimentally measured properties.

---

### calculate_decay_probability

Calculate decay probability P(t) = 1 - exp(-t/τ) for a particle.

**Parameters**:
- `lifetime_s` (float): Mean lifetime τ in seconds
- `time_s` (float): Time elapsed in seconds

**Returns**: Probability of decay between 0 and 1 (float)

**Example**:
```python
# Probability muon decays in 2 microseconds (about 1 lifetime)
prob = calculate_decay_probability(2.197e-6, 2.0e-6)
# Returns: 0.632 (63.2%)
```

**Physics**: Exponential decay law. After one lifetime (t = τ), ~63.2% of particles have decayed.

---

### calculate_binding_energy

Calculate nuclear binding energy from isotope mass.

**Parameters**:
- `isotope_mass_u` (float): Measured isotope mass in atomic mass units (u)
- `num_protons` (int): Number of protons (Z)
- `num_neutrons` (int): Number of neutrons (N)

**Returns**: Binding energy in MeV (float)

**Example**:
```python
# Helium-4 nucleus (2 protons, 2 neutrons)
binding_energy = calculate_binding_energy(4.002603, 2, 2)
# Returns: 28.3 MeV (highly bound nucleus)
```

**Physics**: Mass defect Δm = (Z·m_p + N·m_n - M) converted to energy via E = Δm·c². Measures nuclear stability.

---

## Event Generation & Visualization Tools

Source: `agent/tools/gan_physics.py`

### generate_physics_events

Generate particle physics events based on quark distribution models.

**Parameters**:
- `num_events` (int, default=10000): Number of events to generate
- `truth_params` (list[float], optional): 6 parameters [u_a, u_b, u_p, d_a, d_b, d_q]
- `seed` (int, optional): Random seed for reproducibility

**Returns**: String with statistics (str)

**Example**:
```python
result = generate_physics_events(10000, seed=42)
# Returns statistics for σ1 (4u + d) and σ2 (4d + u) distributions
```

**Physics**:
- u-quark PDF: u(x) = p · x^a · (1-x)^b
- d-quark PDF: d(x) = q · x^a · (1-x)^b
- Cross-sections: σ1 = 4u + d, σ2 = 4d + u (deep inelastic scattering)
- Events sampled via inverse CDF method

**Default parameters**: `[-0.4, 2.4, 0.5, -0.06, 0.4, 0.48]`

---

### visualize_quark_distributions

Create visualization of u and d quark distributions and cross-sections.

**Parameters**:
- `truth_params` (list[float], optional): 6 parameters [u_a, u_b, u_p, d_a, d_b, d_q]
- `save_path` (str, optional): Path to save figure (GUI: leave empty for auto-display)

**Returns**: Description of visualization (str)

**Example**:
```python
# In GUI: plot displays automatically
result = visualize_quark_distributions()

# In MCP/CLI: save to file
result = visualize_quark_distributions(save_path="quark_pdfs.png")
```

**Output**: 4-panel figure showing:
1. u and d quark PDFs
2. u/d ratio vs momentum fraction
3. Cross-sections σ1 and σ2
4. σ1/σ2 ratio

**Physics**: Visualizes parton distribution functions used in deep inelastic scattering analysis.

---

## RAG Document Search Tools

Source: `agent/tools/rag_tool.py`

### load_documents_from_directory

Load PDF documents from directory into memory for search.

**Parameters**:
- `pdf_dir` (str, default="./pdfs"): Directory containing PDF files

**Returns**: Number of documents loaded (int)

**Example**:
```python
# Usually called automatically during agent initialization
count = load_documents_from_directory("./pdfs")
# Returns: 5 (if 5 PDFs found)
```

**Note**: Called automatically when agent is created with `pdfs_dir` config parameter.

---

### search_knowledge_base

Search the physics knowledge base for information relevant to query.

**Parameters**:
- `query` (str): Search query or topic to look up
- `max_chars` (int, default=8000): Maximum characters to return

**Returns**: Relevant content from knowledge base (str)

**Example**:
```python
result = search_knowledge_base("GPD generalized parton distributions")
# Returns relevant sections from loaded PDFs containing GPD information
```

**Algorithm**:
1. Tokenizes query into keywords
2. Searches all loaded PDFs for matching lines
3. Returns context (±2 lines) around matches
4. Ranks by keyword density
5. Returns top 10 sections up to max_chars

**Use Case**: Retrieve theoretical background, equations, and research findings from physics literature.

---

## Tool Usage Patterns

### Via MCP Client

```json
{
  "method": "tools/call",
  "params": {
    "name": "calculate_lorentz_factor",
    "arguments": {
      "velocity_fraction": 0.9
    }
  }
}
```

### Via CLI

```bash
python -m smolnima.cli -q "Calculate the Lorentz factor for v=0.9c"
```

### Via Python API

```python
from agent.tools import calculate_lorentz_factor

gamma = calculate_lorentz_factor(0.9)
print(f"Lorentz factor: {gamma}")
```

### Via Agent (Multi-step reasoning)

```python
from smolnima import create_nima_agent, Config

config = Config.from_env()
agent = create_nima_agent(config)

result = agent.run("""
Calculate the relativistic energy of a muon with momentum 500 MeV/c.
Then calculate the Lorentz factor and time dilation factor.
""")
```

The agent will:
1. Get muon mass from `get_particle_properties("muon")`
2. Calculate energy using `calculate_relativistic_energy(105.66, 500)`
3. Calculate gamma using derived velocity
4. Return comprehensive answer with calculations

---

## Tool Discovery Mechanism

All tools are automatically discovered by the MCP server:

1. **Tool Definition**: Function decorated with `@tool` in `agent/tools/*.py`
2. **Re-export**: Imported in `agent/tools/__init__.py`
3. **Auto-Discovery**: MCP server walks packages, finds `@tool` decorated functions
4. **Schema Generation**: Converts function signature to JSON Schema
5. **MCP Exposure**: Tool available to all MCP clients

**Add New Tool**:
```python
# 1. Create in agent/tools/my_tool.py
from smolagents import tool

@tool
def my_new_calculation(param: float) -> float:
    """Description of what it does."""
    return param * 2.0

# 2. Add to agent/tools/__init__.py
from .my_tool import my_new_calculation
__all__ = [..., "my_new_calculation"]

# 3. Done! Available everywhere automatically
```

---

## Physics Constants and Data

### Particle Database

Built-in properties for:
- **Leptons**: electron, muon
- **Baryons**: proton, neutron
- **Mesons**: pion0, pion+

Properties include PDG-standard values for mass, charge, lifetime, and spin.

### Quark Distribution Models

Default parameters tuned for proton structure functions in deep inelastic scattering:
- u-quark dominance at high x
- d-quark dominance at low x
- Consistent with HERA and fixed-target experiments

### RAG Knowledge Base

Supports:
- Research papers (arXiv PDFs)
- Textbooks and references
- Lecture notes

Automatically loaded from `pdfs/` directory when agent initializes.

---

## Error Handling

All tools include robust error handling:

```python
# Example: Velocity validation
def calculate_lorentz_factor(velocity_fraction: float) -> float:
    if velocity_fraction >= 1.0:
        raise ValueError("Velocity must be less than speed of light")
    return float(1.0 / np.sqrt(1.0 - velocity_fraction**2))
```

Errors are:
- Caught by MCP server
- Returned as TextContent with error message
- Logged for debugging

---

## Performance Characteristics

| Tool | Complexity | Typical Runtime |
|------|-----------|-----------------|
| `calculate_relativistic_energy` | O(1) | < 1 ms |
| `calculate_lorentz_factor` | O(1) | < 1 ms |
| `get_particle_properties` | O(1) | < 1 ms |
| `calculate_decay_probability` | O(1) | < 1 ms |
| `calculate_binding_energy` | O(1) | < 1 ms |
| `generate_physics_events` | O(n) | ~100 ms for 10k events |
| `visualize_quark_distributions` | O(1) | ~200 ms |
| `load_documents_from_directory` | O(n·m) | ~1 s/MB of PDFs |
| `search_knowledge_base` | O(n·m) | ~10-100 ms |

*n = number of events/documents, m = document size*

---

## Future Tool Extensions

Placeholder in `mcp/agent_tools/` for:
- Multi-agent orchestration tools
- Data persistence helpers (save_array, load_array)
- Advanced analysis workflows
- Integration with external physics codes

See `agent_tools/__init__.py` for structure.
