#!/usr/bin/env python3
"""
Generate architecture diagrams for MCP-NIMA documentation.

Requires: graphviz (pip install graphviz)
"""

from graphviz import Digraph


def abstract_architecture():
    """
    High-level abstract architecture showing single source of truth pattern.
    """
    dot = Digraph('Abstract_Architecture')
    dot.attr(rankdir='TB', fontsize='11', labelloc='t',
             label='MCP-NIMA: Single Source of Truth Pattern', dpi='300')

    # Multiple interfaces
    with dot.subgraph(name='cluster_interfaces') as c:
        c.attr(label='User Interfaces', style='rounded', color='blue')
        c.node('cli', 'CLI', shape='box', style='filled', fillcolor='lightblue', fontsize='10')
        c.node('gui', 'Streamlit GUI', shape='box', style='filled', fillcolor='lightblue', fontsize='10')
        c.node('api', 'Python API', shape='box', style='filled', fillcolor='lightblue', fontsize='10')
        c.node('mcp', 'MCP Server', shape='box', style='filled', fillcolor='lightblue', fontsize='10')

    # Single source of truth
    with dot.subgraph(name='cluster_tools') as t:
        t.attr(label='Single Source of Truth', style='rounded', color='green')
        t.node('tools', 'agent/tools/\n\n• particle_physics.py\n• gan_physics.py\n• rag_tool.py',
               shape='box', style='filled', fillcolor='lightgreen', fontsize='10')

    # Core implementations
    with dot.subgraph(name='cluster_core') as core:
        core.attr(label='Core Libraries', style='dashed', fontsize='10', color='gray')
        core.node('libs', 'NumPy, Matplotlib,\nSciPy, PyPDF2',
                  shape='box', fontsize='9', style='filled', fillcolor='lightgray')

    # Connections
    dot.edge('cli', 'tools', label='import', fontsize='8', color='blue')
    dot.edge('gui', 'tools', label='import', fontsize='8', color='blue')
    dot.edge('api', 'tools', label='import', fontsize='8', color='blue')
    dot.edge('mcp', 'tools', label='auto-discover', fontsize='8', color='purple')

    dot.edge('tools', 'libs', style='dashed', label='uses', fontsize='7', color='gray')

    return dot


def mcp_nima_overview():
    """
    Detailed architecture showing all components and data flow.
    """
    dot = Digraph('MCP_NIMA_Overview')
    dot.attr(rankdir='LR', fontsize='10', labelloc='t',
             label='MCP-NIMA Architecture: Multi-Interface Tool Server', dpi='300')

    # MCP Client Layer
    with dot.subgraph(name='cluster_client') as c:
        c.attr(label='MCP Client Layer', style='rounded', color='blue')
        c.node('client', 'Claude Desktop\nor Custom Agent', shape='box', style='filled', fillcolor='lightblue')

    # Interface Layer
    with dot.subgraph(name='cluster_interfaces') as i:
        i.attr(label='Other Interfaces', style='rounded', color='cyan')
        i.node('cli', 'CLI\n\ncli.py', shape='box', style='filled', fillcolor='lightcyan', fontsize='9')
        i.node('gui', 'Streamlit GUI\n\ngui/app.py', shape='box', style='filled', fillcolor='lightcyan', fontsize='9')
        i.node('api', 'Python API\n\nfrom smolnima import ...', shape='box', style='filled', fillcolor='lightcyan', fontsize='9')

    # MCP Server
    with dot.subgraph(name='cluster_mcp') as m:
        m.attr(label='MCP Server', style='rounded', color='green')
        m.node('server', 'mcp_server.py\n\n• Auto-discover @tool\n• Build MCP schemas\n• Execute tools\n• stdio communication',
               shape='box', style='filled', fillcolor='lightgreen')

    # Re-export Layer
    with dot.subgraph(name='cluster_export') as e:
        e.attr(label='Re-export Layer', style='rounded', color='orange', fontsize='9')
        e.node('root_tools', 'tools/__init__.py\n\nRe-exports from\nagent.tools',
               shape='box', fontsize='8', style='filled', fillcolor='lightyellow')
        e.node('mcp_tools', 'mcp/tools/__init__.py\n\nRe-exports from\nagent.tools',
               shape='box', fontsize='8', style='filled', fillcolor='lightyellow')

    # Agent Layer
    with dot.subgraph(name='cluster_agent') as a:
        a.attr(label='Agent System', style='rounded', color='purple', fontsize='9')
        a.node('agent', 'CodeAgent\n\nMulti-step reasoning\nCode generation\nTool orchestration',
               shape='box', fontsize='8', style='filled', fillcolor='plum')
        a.node('gemini', 'GeminiModel\n\nLLM backend\nAPI integration',
               shape='box', fontsize='8', style='filled', fillcolor='plum')

    # Tools (Single Source of Truth)
    with dot.subgraph(name='cluster_sot') as s:
        s.attr(label='Single Source of Truth - agent/tools/', style='rounded', fontsize='9', color='darkgreen')
        s.node('t1', 'particle_physics.py\n\n5 tools:\n• Energy, Lorentz\n• Properties, Decay\n• Binding energy',
               shape='box', fontsize='8', style='filled', fillcolor='palegreen')
        s.node('t2', 'gan_physics.py\n\n2 tools:\n• Event generation\n• Visualization',
               shape='box', fontsize='8', style='filled', fillcolor='palegreen')
        s.node('t3', 'rag_tool.py\n\n2 tools:\n• Load documents\n• Search KB',
               shape='box', fontsize='8', style='filled', fillcolor='palegreen')

    # External Services
    with dot.subgraph(name='cluster_external') as ext:
        ext.attr(label='External Services', style='dashed', fontsize='9', color='red')
        ext.node('gemini_api', 'Gemini API\n\n(for agent only)', shape='ellipse', fontsize='8', style='filled', fillcolor='mistyrose')
        ext.node('pdfs', 'PDF Documents\n\n./pdfs/', shape='ellipse', fontsize='8', style='filled', fillcolor='mistyrose')

    # Main connections
    dot.edge('client', 'server', label='MCP\nProtocol', fontsize='8', color='blue', penwidth='2')
    dot.edge('cli', 'agent', label='creates', fontsize='7', color='cyan')
    dot.edge('gui', 'agent', label='creates', fontsize='7', color='cyan')
    dot.edge('api', 'agent', label='creates', fontsize='7', color='cyan')

    # Re-export connections
    dot.edge('server', 'mcp_tools', label='imports', fontsize='7', color='green')
    dot.edge('cli', 'root_tools', label='imports', fontsize='7', color='cyan', style='dashed')
    dot.edge('gui', 'root_tools', label='imports', fontsize='7', color='cyan', style='dashed')

    # Tools connections
    dot.edge('mcp_tools', 't1', label='re-exports', fontsize='7', color='orange')
    dot.edge('mcp_tools', 't2', fontsize='7', color='orange')
    dot.edge('mcp_tools', 't3', fontsize='7', color='orange')

    dot.edge('root_tools', 't1', label='re-exports', fontsize='7', color='orange', style='dashed')
    dot.edge('root_tools', 't2', fontsize='7', color='orange', style='dashed')
    dot.edge('root_tools', 't3', fontsize='7', color='orange', style='dashed')

    # Agent uses tools
    dot.edge('agent', 't1', label='uses', fontsize='7', color='purple')
    dot.edge('agent', 't2', fontsize='7', color='purple')
    dot.edge('agent', 't3', fontsize='7', color='purple')

    # External dependencies
    dot.edge('agent', 'gemini', style='solid', fontsize='7', color='purple')
    dot.edge('gemini', 'gemini_api', style='dashed', label='requires', fontsize='7', color='red')
    dot.edge('t3', 'pdfs', style='dashed', label='reads', fontsize='7', color='red')

    return dot


def single_source_pattern():
    """
    Simplified diagram focusing on the single source of truth pattern.
    """
    dot = Digraph('Single_Source_Pattern')
    dot.attr(rankdir='TB', fontsize='10', labelloc='t',
             label='Single Source of Truth: Write Once, Use Everywhere', dpi='300')

    # Developer action
    dot.node('dev', 'Developer\n\n1. Writes tool in\nagent/tools/my_tool.py',
             shape='box', style='filled', fillcolor='wheat', fontsize='10')

    # Export step
    dot.node('export', '2. Adds to\nagent/tools/__init__.py',
             shape='box', style='filled', fillcolor='lightyellow', fontsize='10')

    # Automatic availability
    with dot.subgraph(name='cluster_auto') as a:
        a.attr(label='3. Automatically Available Everywhere', style='rounded', fontsize='9', color='green')
        a.node('a1', 'CLI', shape='box', fontsize='9', style='filled', fillcolor='lightgreen')
        a.node('a2', 'Web GUI', shape='box', fontsize='9', style='filled', fillcolor='lightgreen')
        a.node('a3', 'Python API', shape='box', fontsize='9', style='filled', fillcolor='lightgreen')
        a.node('a4', 'MCP Server', shape='box', fontsize='9', style='filled', fillcolor='lightgreen')

    # No duplication
    dot.node('result', '✓ Zero Duplication\n✓ Single Maintenance Point\n✓ Consistent Behavior',
             shape='box', style='filled,rounded', fillcolor='gold', fontsize='10')

    # Flow
    dot.edge('dev', 'export', label='Step 1', fontsize='9', penwidth='2', color='blue')
    dot.edge('export', 'a1', label='auto', fontsize='8', color='green')
    dot.edge('export', 'a2', label='auto', fontsize='8', color='green')
    dot.edge('export', 'a3', label='auto', fontsize='8', color='green')
    dot.edge('export', 'a4', label='auto', fontsize='8', color='green')

    dot.edge('a1', 'result', fontsize='8', color='orange', style='dashed')
    dot.edge('a2', 'result', fontsize='8', color='orange', style='dashed')
    dot.edge('a3', 'result', fontsize='8', color='orange', style='dashed')
    dot.edge('a4', 'result', fontsize='8', color='orange', style='dashed')

    return dot


if __name__ == '__main__':
    print("Generating MCP-NIMA architecture diagrams...")

    print("\n1. Abstract architecture...")
    d0 = abstract_architecture()
    d0.render('abstract_architecture', format='png', cleanup=True)
    print("   ✓ Generated abstract_architecture.png")

    print("\n2. Detailed MCP-NIMA overview...")
    d1 = mcp_nima_overview()
    d1.render('mcp_nima_overview', format='png', cleanup=True)
    print("   ✓ Generated mcp_nima_overview.png")

    print("\n3. Single source of truth pattern...")
    d2 = single_source_pattern()
    d2.render('single_source_pattern', format='png', cleanup=True)
    print("   ✓ Generated single_source_pattern.png")

    print("\n✓ All architecture diagrams generated successfully!")
    print("\nGenerated files:")
    print("  - abstract_architecture.png")
    print("  - mcp_nima_overview.png")
    print("  - single_source_pattern.png")
