#!/bin/bash
# DESC: Stops the tmux session, kills processes on ports 3000/8000/8001, and clears dev environment

SESSION="parco-dev"
PORTS=("3000" "8000" "8001")

echo "🛑 Stopping tmux session: $SESSION..."
tmux kill-session -t $SESSION 2>/dev/null

echo "🧹 Cleaning up processes on ports: ${PORTS[*]}..."
for PORT in "${PORTS[@]}"; do
    PID=$(lsof -ti tcp:$PORT)
    if [ ! -z "$PID" ]; then
        echo "⚠️  Port $PORT is in use by PID $PID. Killing..."
        kill -9 $PID || echo "Failed to kill PID $PID"
    else
        echo "✅ Port $PORT is already free."
    fi
done

echo "🧼 Killing leftover node/npm processes..."
pkill -f "react-scripts/scripts/start.js"
pkill -f "node .*start.js"

echo "✅ Development environment shut down cleanly."
