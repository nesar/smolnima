#!/bin/bash
# Clean launcher - kills all streamlit and runs on port 8503

echo "🧹 Cleaning up all Streamlit processes..."

# Kill all streamlit processes
pkill -9 -f streamlit

# Wait a moment
sleep 2

# Check if ports are free
echo "🔍 Checking ports..."
for port in 8501 8502 8503 8504; do
    if lsof -ti:$port > /dev/null 2>&1; then
        echo "   Port $port is in use, killing..."
        lsof -ti:$port | xargs kill -9 2>/dev/null
    else
        echo "   Port $port is free ✓"
        FREE_PORT=$port
        break
    fi
done

# Wait another moment
sleep 1

# Use free port or default to 8503
PORT=${FREE_PORT:-8503}

echo ""
echo "🚀 Starting smolnima on port $PORT..."
echo "   Open: http://localhost:$PORT"
echo ""

# Check if enhanced version exists, use it, otherwise use standard
if [ -f "streamlit_app_enhanced.py" ]; then
    echo "   Using enhanced Streamlit app with agent activity panel"
    streamlit run streamlit_app_enhanced.py --server.port $PORT
else
    streamlit run streamlit_app.py --server.port $PORT
fi
