# MCP-NIMA Documentation

Professional, minimal documentation for the MCP-NIMA particle physics tool server.

## Documentation Files

1. **[01_RATIONALE.md](01_RATIONALE.md)** - Design rationale and motivation
   - Problem statement
   - Solution overview
   - Why MCP? Why smolagents?
   - Single source of truth pattern
   - Core design principles

2. **[02_ARCHITECTURE.md](02_ARCHITECTURE.md)** - System architecture
   - Component overview
   - Data flow diagrams
   - Directory structure
   - Tool discovery mechanism
   - Multi-interface design

3. **[03_TOOLS.md](03_TOOLS.md)** - Complete tool reference
   - 9 physics tools with examples
   - Tool categories and use cases
   - Performance characteristics
   - Tool chaining patterns

4. **[04_CLIENT.md](04_CLIENT.md)** - MCP client integration guide
   - Claude Desktop setup
   - Custom client integration
   - Example requests/responses
   - Troubleshooting guide

## Architecture Diagrams

Generate diagrams with:

```bash
# Install dependencies first
brew install graphviz  # macOS
# OR: apt-get install graphviz  # Linux
# OR: choco install graphviz  # Windows

pip install graphviz

# Generate diagrams
cd documentation
python3 flowchart.py
```

This creates:
- **abstract_architecture.png** - High-level single source of truth pattern
- **mcp_nima_overview.png** - Detailed component architecture
- **single_source_pattern.png** - Write once, use everywhere workflow

## Quick Links

### For Developers
- Start with [01_RATIONALE.md](01_RATIONALE.md) to understand the design
- Read [02_ARCHITECTURE.md](02_ARCHITECTURE.md) for implementation details
- Reference [03_TOOLS.md](03_TOOLS.md) when adding or using tools

### For Users
- MCP setup: [04_CLIENT.md](04_CLIENT.md)
- Tool reference: [03_TOOLS.md](03_TOOLS.md)
- Main README: [../../README.md](../../README.md)

### For Integrators
- Architecture: [02_ARCHITECTURE.md](02_ARCHITECTURE.md)
- Client guide: [04_CLIENT.md](04_CLIENT.md)
- MCP server README: [../README.md](../README.md)

## Documentation Style

This documentation follows professional technical writing principles:

- **Minimal**: Concise, no fluff
- **Informative**: Complete information, clear examples
- **Professional**: Proper terminology, accurate physics
- **Structured**: Logical organization, easy navigation
- **Visual**: Diagrams for complex concepts

Inspired by the documentation style of [hep-ke/mcp](https://github.com/anthropics/hep-ke).

## Contributing

When modifying the codebase:

1. **Update tool docs** if adding/changing tools in [03_TOOLS.md](03_TOOLS.md)
2. **Update architecture** if changing component structure in [02_ARCHITECTURE.md](02_ARCHITECTURE.md)
3. **Regenerate diagrams** after architectural changes: `python3 flowchart.py`
4. **Keep it minimal** - remove outdated content, don't accumulate

## License

Same as parent smolnima project.
