#!/bin/bash

# MCP-NIMA Server Launcher
# Runs the MCP server for Dr. NIMA's particle physics tools

# Change to mcp directory
cd "$(dirname "$0")"

# Check if running in SSE mode (HTTP) or STDIO mode
MODE="${MCP_TRANSPORT:-stdio}"

if [ "$MODE" = "sse" ]; then
    echo "Starting MCP-NIMA server in SSE mode (HTTP)..."
    echo "Server will be available at http://${MCP_HOST:-0.0.0.0}:${MCP_PORT:-8000}"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    python3 mcp_server.py
else
    echo "Starting MCP-NIMA server in STDIO mode..."
    echo "This mode is for direct integration with MCP clients."
    echo ""
    python3 mcp_server.py
fi
